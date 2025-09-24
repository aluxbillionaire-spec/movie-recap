"""
Simple test API for verifying multi-tenant and i18n functionality
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json

app = FastAPI(title="Movie Recap Service - Test API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
TENANTS = {
    "default": {
        "id": "default",
        "name": "default",
        "display_name": "Default Tenant",
        "billing_plan": "free",
        "settings": {
            "region": "us-east-1",
            "security": {
                "allowed_countries": ["US", "CA"],
                "rate_limits": {}
            }
        },
        "is_active": True
    },
    "customer1": {
        "id": "customer1", 
        "name": "customer1",
        "display_name": "Customer One Inc.",
        "billing_plan": "professional",
        "settings": {
            "region": "eu-west-1",
            "security": {
                "allowed_countries": ["US", "CA", "GB", "DE", "FR"],
                "blocked_countries": ["CN", "RU"],
                "rate_limits": {}
            }
        },
        "is_active": True
    }
}

USERS = {
    "user1": {
        "id": "user1",
        "email": "admin@customer1.com",
        "full_name": "Admin User",
        "tenant_id": "customer1",
        "roles": ["admin"],
        "is_active": True
    },
    "user2": {
        "id": "user2", 
        "email": "user@default.com",
        "full_name": "Default User",
        "tenant_id": "default",
        "roles": ["user"],
        "is_active": True
    }
}

METRICS = {
    "customer1": {
        "total_users": 15,
        "active_users_24h": 12,
        "storage_used_gb": 45.2,
        "processing_hours_used": 8.5,
        "api_calls_24h": 1250,
        "error_rate_percent": 0.3,
        "avg_response_time_ms": 180
    },
    "default": {
        "total_users": 5,
        "active_users_24h": 3,
        "storage_used_gb": 12.1,
        "processing_hours_used": 2.1,
        "api_calls_24h": 450,
        "error_rate_percent": 0.8,
        "avg_response_time_ms": 220
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

class TenantResponse(BaseModel):
    id: str
    name: str
    display_name: str
    billing_plan: str
    settings: Dict
    is_active: bool

def get_tenant_from_request(request: Request) -> str:
    """Extract tenant from request"""
    # Check subdomain
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        if subdomain != "localhost" and subdomain in TENANTS:
            return subdomain
    
    # Check header
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header and tenant_header in TENANTS:
        return tenant_header
    
    # Default tenant
    return "default"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "movie-recap-api",
        "version": "1.0.0",
        "features": {
            "multi_tenant": True,
            "i18n": True,
            "security": True,
            "analytics": True
        }
    }

@app.post("/api/v1/auth/login")
async def login(request: Request, login_data: LoginRequest):
    """Mock login endpoint"""
    tenant_id = get_tenant_from_request(request)
    
    # Mock authentication
    for user in USERS.values():
        if user["email"] == login_data.email and user["tenant_id"] == tenant_id:
            return {
                "access_token": f"mock_token_{user['id']}",
                "token_type": "bearer",
                "user": user,
                "tenant": TENANTS[tenant_id]
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/tenants")
async def list_tenants():
    """List all tenants"""
    return list(TENANTS.values())

@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get tenant by ID"""
    if tenant_id not in TENANTS:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TENANTS[tenant_id]

@app.get("/api/v1/tenants/{tenant_id}/metrics")
async def get_tenant_metrics(tenant_id: str):
    """Get tenant metrics"""
    if tenant_id not in TENANTS:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant = TENANTS[tenant_id]
    metrics = METRICS.get(tenant_id, {})
    
    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant["display_name"],
        "region": tenant["settings"]["region"],
        **metrics
    }

@app.get("/api/v1/analytics/global/metrics")
async def get_global_metrics():
    """Get global metrics"""
    total_users = sum(m.get("total_users", 0) for m in METRICS.values())
    total_storage = sum(m.get("storage_used_gb", 0) for m in METRICS.values())
    
    return {
        "total_tenants": len(TENANTS),
        "total_users": total_users,
        "total_storage_gb": total_storage,
        "regional_metrics": {
            "us-east-1": {"tenants": 1, "users": 5},
            "eu-west-1": {"tenants": 1, "users": 15}
        },
        "global_uptime_percent": 99.95,
        "avg_response_time_ms": 195.0
    }

@app.get("/api/v1/tenant-info")
async def get_current_tenant_info(request: Request):
    """Get current tenant information based on request"""
    tenant_id = get_tenant_from_request(request)
    tenant = TENANTS[tenant_id]
    
    return {
        "detected_tenant": tenant_id,
        "tenant_info": tenant,
        "request_headers": dict(request.headers),
        "host": request.headers.get("host"),
        "detection_method": "header" if request.headers.get("X-Tenant-ID") else "subdomain"
    }

@app.get("/api/v1/security/check")
async def security_check(request: Request):
    """Test security middleware functionality"""
    tenant_id = get_tenant_from_request(request)
    tenant = TENANTS[tenant_id]
    security_config = tenant["settings"]["security"]
    
    client_ip = request.client.host if request.client else "unknown"
    
    return {
        "tenant_id": tenant_id,
        "client_ip": client_ip,
        "security_config": security_config,
        "rate_limit_status": "within_limits",
        "geo_check": "allowed",
        "ip_check": "allowed"
    }

@app.get("/api/v1/i18n/test")
async def i18n_test():
    """Test endpoint for i18n functionality"""
    return {
        "supported_languages": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "es", "name": "Spanish", "native": "Español"}, 
            {"code": "fr", "name": "French", "native": "Français"},
            {"code": "de", "name": "German", "native": "Deutsch"},
            {"code": "zh", "name": "Chinese", "native": "中文"},
            {"code": "ar", "name": "Arabic", "native": "العربية", "rtl": True}
        ],
        "test_translations": {
            "en": {"welcome": "Welcome back!", "dashboard": "Dashboard"},
            "es": {"welcome": "¡Bienvenido de vuelta!", "dashboard": "Panel Principal"},
            "fr": {"welcome": "Bon retour !", "dashboard": "Tableau de bord"},
            "zh": {"welcome": "欢迎回来！", "dashboard": "仪表板"},
            "ar": {"welcome": "مرحباً بعودتك!", "dashboard": "لوحة التحكم"}
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)