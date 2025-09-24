"""
Enhanced Security Middleware

Advanced security features for global multi-tenant deployment.
"""

import time
import hashlib
import json
from typing import Dict, Set, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import logging
from ipaddress import ip_address, ip_network
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    requests: int
    window: int  # seconds
    burst: int = 0  # burst allowance
    tenant_specific: bool = False


@dataclass
class SecurityConfig:
    """Security configuration for tenants."""
    allowed_countries: Set[str] = field(default_factory=set)
    blocked_countries: Set[str] = field(default_factory=set)
    allowed_ips: Set[str] = field(default_factory=set)
    blocked_ips: Set[str] = field(default_factory=set)
    rate_limits: Dict[str, RateLimitRule] = field(default_factory=dict)
    require_2fa: bool = False
    max_login_attempts: int = 5
    lockout_duration: int = 3600  # seconds


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Advanced security middleware with:
    - Geographic access control
    - Advanced rate limiting
    - IP allowlisting/blocklisting
    - Tenant-specific security policies
    - DDoS protection
    - Suspicious activity detection
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.geo_db = None  # Would integrate with MaxMind GeoIP
        
        # Default rate limits
        self.default_rate_limits = {
            "auth": RateLimitRule(requests=5, window=300, burst=2),  # 5 auth attempts per 5 min
            "api": RateLimitRule(requests=100, window=60, burst=20),  # 100 API calls per minute
            "upload": RateLimitRule(requests=10, window=3600, burst=2),  # 10 uploads per hour
            "global": RateLimitRule(requests=1000, window=3600, burst=100),  # Global limit
        }
        
        # Known malicious IP patterns (example)
        self.suspicious_patterns = [
            "tor_exit_nodes",
            "known_botnets", 
            "cloud_providers_abuse"
        ]
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Initialize Redis connection if needed
            if not self.redis_client:
                await self._init_redis()
            
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Skip security checks for health endpoints
            if self._should_skip_security_check(request.url.path):
                return await call_next(request)
            
            # Get tenant security config
            tenant_config = await self._get_tenant_security_config(request)
            
            # Security checks
            await self._check_ip_restrictions(client_ip, tenant_config)
            await self._check_geo_restrictions(client_ip, tenant_config)
            await self._check_rate_limits(request, client_ip, tenant_config)
            await self._check_suspicious_activity(request, client_ip)
            
            # Add security headers to request state
            request.state.client_ip = client_ip
            request.state.security_config = tenant_config
            
            response = await call_next(request)
            
            # Add security headers to response
            self._add_security_headers(response, request)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Security check failed"}
            )
    
    async def _init_redis(self):
        """Initialize Redis connection for rate limiting and caching."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for security middleware")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies."""
        # Check various headers for real IP
        for header in ["X-Forwarded-For", "X-Real-IP", "CF-Connecting-IP"]:
            if header in request.headers:
                ip = request.headers[header].split(",")[0].strip()
                if self._is_valid_ip(ip):
                    return ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _is_valid_ip(self, ip_str: str) -> bool:
        """Validate IP address format."""
        try:
            ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    def _should_skip_security_check(self, path: str) -> bool:
        """Check if security checks should be skipped."""
        skip_paths = ["/health", "/metrics", "/docs", "/openapi.json"]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _get_tenant_security_config(self, request: Request) -> SecurityConfig:
        """Get security configuration for current tenant."""
        # Use default config if no tenant context
        if not hasattr(request.state, 'tenant') or not request.state.tenant:
            return SecurityConfig(rate_limits=self.default_rate_limits)
        
        tenant = request.state.tenant
        config = SecurityConfig(rate_limits=self.default_rate_limits.copy())
        
        # Load tenant-specific settings from database/cache
        if tenant.settings:
            security_settings = tenant.settings.get("security", {})\n            \n            # Parse allowed/blocked countries
            config.allowed_countries = set(security_settings.get("allowed_countries", []))
            config.blocked_countries = set(security_settings.get("blocked_countries", []))
            \n            # Parse IP restrictions
            config.allowed_ips = set(security_settings.get("allowed_ips", []))
            config.blocked_ips = set(security_settings.get("blocked_ips", []))
            \n            # Parse custom rate limits
            custom_limits = security_settings.get("rate_limits", {})
            for endpoint, limit_config in custom_limits.items():
                config.rate_limits[endpoint] = RateLimitRule(**limit_config)
        
        return config
    
    async def _check_ip_restrictions(self, client_ip: str, config: SecurityConfig):
        """Check IP allowlist/blocklist."""
        if client_ip == "unknown":
            return
            
        # Check blocklist first
        for blocked_ip in config.blocked_ips:
            if self._ip_matches_pattern(client_ip, blocked_ip):
                logger.warning(f"Blocked IP access attempt: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied from this IP address"
                )
        
        # Check allowlist (if configured)
        if config.allowed_ips:
            allowed = any(
                self._ip_matches_pattern(client_ip, allowed_ip) 
                for allowed_ip in config.allowed_ips
            )
            if not allowed:
                logger.warning(f"Non-allowlisted IP access attempt: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: IP not in allowlist"
                )
    
    def _ip_matches_pattern(self, client_ip: str, pattern: str) -> bool:
        """Check if client IP matches a pattern (supports CIDR)."""
        try:
            if "/" in pattern:
                # CIDR notation
                return ip_address(client_ip) in ip_network(pattern, strict=False)
            else:
                # Exact match
                return client_ip == pattern
        except ValueError:
            return False
    
    async def _check_geo_restrictions(self, client_ip: str, config: SecurityConfig):
        """Check geographic access restrictions."""
        if client_ip == "unknown" or not (config.allowed_countries or config.blocked_countries):
            return
        
        # Get country code (would integrate with GeoIP service)
        country_code = await self._get_country_code(client_ip)
        
        if country_code:
            # Check blocked countries
            if country_code in config.blocked_countries:
                logger.warning(f"Blocked country access: {country_code} from {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied from this geographic location"
                )
            
            # Check allowed countries
            if config.allowed_countries and country_code not in config.allowed_countries:
                logger.warning(f"Non-allowed country access: {country_code} from {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access not permitted from this geographic location"
                )
    
    async def _get_country_code(self, ip: str) -> Optional[str]:
        """Get country code for IP address."""
        # This would integrate with a GeoIP service like MaxMind
        # For now, return None (no geo-blocking)
        # In production, you would use:
        # import geoip2.database
        # reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
        # response = reader.country(ip)
        # return response.country.iso_code
        return None
    
    async def _check_rate_limits(self, request: Request, client_ip: str, config: SecurityConfig):
        """Advanced rate limiting with multiple windows and burst allowance."""
        if not self.redis_client:
            return
        
        # Determine rate limit category
        path = request.url.path
        category = self._get_rate_limit_category(path)
        
        if category not in config.rate_limits:
            return
        
        rule = config.rate_limits[category]
        
        # Create rate limit keys
        tenant_id = getattr(request.state, 'tenant_id', 'default')
        base_key = f"rate_limit:{category}:{client_ip}"
        
        if rule.tenant_specific and tenant_id:
            base_key = f"rate_limit:{category}:{tenant_id}:{client_ip}"
        
        # Check current window
        current_time = int(time.time())
        window_start = current_time - (current_time % rule.window)
        window_key = f"{base_key}:{window_start}"
        
        try:
            # Get current count
            current_count = await self.redis_client.get(window_key) or 0
            current_count = int(current_count)
            
            # Check burst allowance
            burst_key = f"{base_key}:burst"
            burst_used = await self.redis_client.get(burst_key) or 0
            burst_used = int(burst_used)
            
            total_allowed = rule.requests + rule.burst
            total_used = current_count + burst_used
            
            if total_used >= total_allowed:
                # Rate limit exceeded
                logger.warning(f"Rate limit exceeded: {client_ip} for {category}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for {category}",
                    headers={"Retry-After": str(rule.window)}
                )
            
            # Increment counters
            if current_count < rule.requests:
                await self.redis_client.incr(window_key)
                await self.redis_client.expire(window_key, rule.window)
            else:
                await self.redis_client.incr(burst_key)
                await self.redis_client.expire(burst_key, rule.window)
                
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Fail open - allow request if Redis is down
    
    def _get_rate_limit_category(self, path: str) -> str:
        """Determine rate limit category from request path."""
        if "/auth/" in path:
            return "auth"
        elif "/upload" in path:
            return "upload"
        elif "/api/" in path:
            return "api"
        else:
            return "global"
    
    async def _check_suspicious_activity(self, request: Request, client_ip: str):
        """Detect and block suspicious activity patterns."""
        if not self.redis_client or client_ip == "unknown":
            return
        
        # Track request patterns
        pattern_key = f"activity:{client_ip}:patterns"
        
        # Simple suspicious activity detection
        user_agent = request.headers.get("user-agent", "")
        
        # Check for common bot patterns
        suspicious_agents = ["bot", "crawler", "scanner", "exploit"]
        if any(pattern in user_agent.lower() for pattern in suspicious_agents):
            logger.warning(f"Suspicious user agent from {client_ip}: {user_agent}")
            
        # Track rapid requests from same IP
        request_key = f"activity:{client_ip}:requests"
        try:
            recent_requests = await self.redis_client.incr(request_key)
            if recent_requests == 1:
                await self.redis_client.expire(request_key, 60)  # 1 minute window
            
            if recent_requests > 1000:  # More than 1000 requests per minute
                logger.warning(f"Potential DDoS from {client_ip}: {recent_requests} requests/min")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Suspicious activity detected"
                )
                
        except redis.RedisError:
            pass  # Fail open
    
    def _add_security_headers(self, response, request: Request):
        """Add security headers to response."""
        # Standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Rate limit info
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
            response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)