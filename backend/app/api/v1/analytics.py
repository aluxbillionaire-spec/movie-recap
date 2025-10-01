"""
Analytics and Monitoring Service

Comprehensive analytics, monitoring, and reporting for global multi-tenant deployment.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
from dataclasses import dataclass

from app.core.database import get_async_session
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usage_tracking import UsageTracking
from app.models.audit_log import AuditLog
from app.middleware.tenant import get_current_tenant_id, get_current_tenant
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class TenantMetrics(BaseModel):
    tenant_id: str
    tenant_name: str
    region: str
    
    # User metrics
    total_users: int
    active_users_24h: int
    active_users_7d: int
    active_users_30d: int
    new_users_7d: int
    
    # Usage metrics
    storage_used_gb: float
    processing_hours_used: float
    api_calls_24h: int
    bandwidth_used_gb: float
    
    # Performance metrics
    avg_response_time_ms: float
    error_rate_percent: float
    uptime_percent: float
    
    # Business metrics
    projects_created: int
    jobs_completed: int
    revenue_monthly: float
    churn_rate_percent: float


class GlobalMetrics(BaseModel):
    timestamp: datetime
    
    # Global totals
    total_tenants: int
    total_users: int
    total_storage_gb: float
    total_processing_hours: float
    
    # Regional breakdown
    regional_metrics: Dict[str, Dict[str, Any]]
    
    # Performance overview
    global_uptime_percent: float
    avg_response_time_ms: float
    total_requests_24h: int
    error_rate_percent: float
    
    # Growth metrics
    new_tenants_7d: int
    new_users_7d: int
    revenue_growth_percent: float


class RegionalMetrics(BaseModel):
    region: str
    timestamp: datetime
    
    # Regional stats
    tenants_count: int
    users_count: int
    storage_used_gb: float
    processing_hours: float
    
    # Performance metrics
    avg_latency_ms: float
    error_rate: float
    uptime_percent: float
    requests_per_second: float
    
    # Resource utilization
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_mbps: float


@dataclass
class AlertRule:
    name: str
    condition: str
    threshold: float
    severity: str  # critical, warning, info
    tenant_id: Optional[str] = None
    region: Optional[str] = None


class AnalyticsService:
    """Service for collecting and analyzing application metrics."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_rules = self._get_default_alert_rules()
    
    def _get_default_alert_rules(self) -> List[AlertRule]:
        """Define default alert rules for monitoring."""
        return [
            AlertRule("high_error_rate", "error_rate > threshold", 5.0, "critical"),
            AlertRule("high_response_time", "avg_response_time > threshold", 2000.0, "warning"),
            AlertRule("low_uptime", "uptime < threshold", 99.0, "critical"),
            AlertRule("high_storage_usage", "storage_usage > threshold", 90.0, "warning"),
            AlertRule("quota_exceeded", "usage > quota", 100.0, "critical"),
        ]
    
    async def get_tenant_metrics(self, tenant_id: str, period_days: int = 30) -> TenantMetrics:
        """Get comprehensive metrics for a specific tenant."""
        
        period_start = datetime.now() - timedelta(days=period_days)
        
        # Get tenant info
        tenant_query = select(Tenant).where(Tenant.id == tenant_id)
        tenant_result = await self.db.execute(tenant_query)
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # User metrics
        user_metrics = await self._get_user_metrics(tenant_id, period_start)
        
        # Usage metrics
        usage_metrics = await self._get_usage_metrics(tenant_id, period_start)
        
        # Performance metrics
        perf_metrics = await self._get_performance_metrics(tenant_id, period_start)
        
        # Business metrics
        business_metrics = await self._get_business_metrics(tenant_id, period_start)
        
        return TenantMetrics(
            tenant_id=tenant_id,
            tenant_name=tenant.display_name,
            region=tenant.settings.get("region", "unknown"),
            **user_metrics,
            **usage_metrics,
            **perf_metrics,
            **business_metrics
        )
    
    async def _get_user_metrics(self, tenant_id: str, period_start: datetime) -> Dict[str, int]:
        """Get user-related metrics for a tenant."""
        
        # Total users
        total_users_query = select(func.count(User.id)).where(
            User.tenant_id == tenant_id
        )
        total_users_result = await self.db.execute(total_users_query)
        total_users = total_users_result.scalar() or 0
        
        # Active users (based on last_login)
        now = datetime.now()
        
        active_24h_query = select(func.count(User.id)).where(
            (User.tenant_id == tenant_id) &
            (User.last_login >= now - timedelta(hours=24))
        )
        active_24h_result = await self.db.execute(active_24h_query)
        active_users_24h = active_24h_result.scalar() or 0
        
        active_7d_query = select(func.count(User.id)).where(
            (User.tenant_id == tenant_id) &
            (User.last_login >= now - timedelta(days=7))
        )
        active_7d_result = await self.db.execute(active_7d_query)
        active_users_7d = active_7d_result.scalar() or 0
        
        active_30d_query = select(func.count(User.id)).where(
            (User.tenant_id == tenant_id) &
            (User.last_login >= now - timedelta(days=30))
        )
        active_30d_result = await self.db.execute(active_30d_query)
        active_users_30d = active_30d_result.scalar() or 0
        
        # New users in last 7 days
        new_users_7d_query = select(func.count(User.id)).where(
            (User.tenant_id == tenant_id) &
            (User.created_at >= now - timedelta(days=7))
        )
        new_users_7d_result = await self.db.execute(new_users_7d_query)
        new_users_7d = new_users_7d_result.scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users_24h": active_users_24h,
            "active_users_7d": active_users_7d,
            "active_users_30d": active_users_30d,
            "new_users_7d": new_users_7d
        }
    
    async def _get_usage_metrics(self, tenant_id: str, period_start: datetime) -> Dict[str, float]:
        """Get usage metrics for a tenant."""
        
        # Aggregate usage from usage_tracking table
        usage_query = select(
            func.sum(UsageTracking.amount).filter(
                UsageTracking.resource_type == "storage"
            ).label("storage_used"),
            func.sum(UsageTracking.amount).filter(
                UsageTracking.resource_type == "processing_time"
            ).label("processing_hours"),
            func.sum(UsageTracking.amount).filter(
                UsageTracking.resource_type == "api_calls"
            ).label("api_calls"),
            func.sum(UsageTracking.amount).filter(
                UsageTracking.resource_type == "bandwidth"
            ).label("bandwidth_used")
        ).where(
            (UsageTracking.tenant_id == tenant_id) &
            (UsageTracking.created_at >= period_start)
        )
        
        usage_result = await self.db.execute(usage_query)
        usage_row = usage_result.first()
        
        return {
            "storage_used_gb": float(usage_row.storage_used or 0) / (1024**3),
            "processing_hours_used": float(usage_row.processing_hours or 0),
            "api_calls_24h": int(usage_row.api_calls or 0),
            "bandwidth_used_gb": float(usage_row.bandwidth_used or 0) / (1024**3)
        }
    
    async def _get_performance_metrics(self, tenant_id: str, period_start: datetime) -> Dict[str, float]:
        """Get performance metrics for a tenant."""
        
        # This would typically come from APM tools like New Relic, Datadog, etc.
        # For now, return mock data
        return {
            "avg_response_time_ms": 250.0,
            "error_rate_percent": 0.5,
            "uptime_percent": 99.9
        }
    
    async def _get_business_metrics(self, tenant_id: str, period_start: datetime) -> Dict[str, Any]:
        """Get business-related metrics for a tenant."""
        
        # Projects and jobs metrics would come from respective tables
        # For now, return mock data
        return {
            "projects_created": 25,
            "jobs_completed": 156,
            "revenue_monthly": 299.99,
            "churn_rate_percent": 2.1
        }
    
    async def get_global_metrics(self) -> GlobalMetrics:
        """Get global platform metrics across all tenants and regions."""
        
        # Get total counts
        total_tenants_query = select(func.count(Tenant.id)).where(Tenant.is_active == True)
        total_tenants_result = await self.db.execute(total_tenants_query)
        total_tenants = total_tenants_result.scalar() or 0
        
        total_users_query = select(func.count(User.id)).where(User.is_active == True)
        total_users_result = await self.db.execute(total_users_query)
        total_users = total_users_result.scalar() or 0
        
        # Get regional breakdown
        regional_query = select(
            func.coalesce(Tenant.settings['region'].astext, 'unknown').label('region'),
            func.count(Tenant.id).label('tenant_count'),
            func.count(User.id).label('user_count')
        ).select_from(
            Tenant.__table__.join(User.__table__, Tenant.id == User.tenant_id)
        ).where(
            Tenant.is_active == True
        ).group_by(
            Tenant.settings['region'].astext
        )
        
        regional_result = await self.db.execute(regional_query)
        regional_data = {row.region: {"tenants": row.tenant_count, "users": row.user_count} 
                        for row in regional_result}
        
        # Calculate growth metrics
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        new_tenants_query = select(func.count(Tenant.id)).where(
            (Tenant.created_at >= week_ago) & (Tenant.is_active == True)
        )
        new_tenants_result = await self.db.execute(new_tenants_query)
        new_tenants_7d = new_tenants_result.scalar() or 0
        
        new_users_query = select(func.count(User.id)).where(
            (User.created_at >= week_ago) & (User.is_active == True)
        )
        new_users_result = await self.db.execute(new_users_query)
        new_users_7d = new_users_result.scalar() or 0
        
        return GlobalMetrics(
            timestamp=now,
            total_tenants=total_tenants,
            total_users=total_users,
            total_storage_gb=1024.5,  # Mock data
            total_processing_hours=5678.9,  # Mock data
            regional_metrics=regional_data,
            global_uptime_percent=99.95,
            avg_response_time_ms=180.0,
            total_requests_24h=1250000,
            error_rate_percent=0.12,
            new_tenants_7d=new_tenants_7d,
            new_users_7d=new_users_7d,
            revenue_growth_percent=15.7
        )
    
    async def check_alerts(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check for alerts based on defined rules."""
        
        alerts = []
        
        # Get metrics for alert checking
        if tenant_id:
            metrics = await self.get_tenant_metrics(tenant_id)
            
            # Check tenant-specific alerts
            for rule in self.alert_rules:
                if rule.tenant_id and rule.tenant_id != tenant_id:
                    continue
                
                alert = await self._evaluate_alert_rule(rule, metrics)
                if alert:
                    alerts.append(alert)
        else:
            # Check global alerts
            global_metrics = await self.get_global_metrics()
            
            for rule in self.alert_rules:
                if rule.tenant_id:  # Skip tenant-specific rules
                    continue
                
                alert = await self._evaluate_global_alert_rule(rule, global_metrics)
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    async def _evaluate_alert_rule(self, rule: AlertRule, metrics: TenantMetrics) -> Optional[Dict[str, Any]]:
        """Evaluate an alert rule against tenant metrics."""
        
        # Simple rule evaluation (in practice, use a proper rule engine)
        if rule.name == "high_error_rate" and metrics.error_rate_percent > rule.threshold:
            return {
                "rule": rule.name,
                "severity": rule.severity,
                "message": f"Error rate {metrics.error_rate_percent:.2f}% exceeds threshold {rule.threshold}%",
                "tenant_id": metrics.tenant_id,
                "timestamp": datetime.now(),
                "value": metrics.error_rate_percent
            }
        
        if rule.name == "high_response_time" and metrics.avg_response_time_ms > rule.threshold:
            return {
                "rule": rule.name,
                "severity": rule.severity,
                "message": f"Response time {metrics.avg_response_time_ms:.0f}ms exceeds threshold {rule.threshold}ms",
                "tenant_id": metrics.tenant_id,
                "timestamp": datetime.now(),
                "value": metrics.avg_response_time_ms
            }
        
        return None
    
    async def _evaluate_global_alert_rule(self, rule: AlertRule, metrics: GlobalMetrics) -> Optional[Dict[str, Any]]:
        """Evaluate an alert rule against global metrics."""
        
        if rule.name == "global_high_error_rate" and metrics.error_rate_percent > rule.threshold:
            return {
                "rule": rule.name,
                "severity": rule.severity,
                "message": f"Global error rate {metrics.error_rate_percent:.2f}% exceeds threshold {rule.threshold}%",
                "timestamp": datetime.now(),
                "value": metrics.error_rate_percent
            }
        
        return None


# API Endpoints

@router.get("/tenants/{tenant_id}/metrics", response_model=TenantMetrics)
async def get_tenant_analytics(
    tenant_id: str,
    period_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_session)
):
    """Get analytics metrics for a specific tenant."""
    
    analytics = AnalyticsService(db)
    return await analytics.get_tenant_metrics(tenant_id, period_days)


@router.get("/global/metrics", response_model=GlobalMetrics)
async def get_global_analytics(
    db: AsyncSession = Depends(get_async_session)
):
    """Get global platform analytics."""
    
    analytics = AnalyticsService(db)
    return await analytics.get_global_metrics()


@router.get("/alerts")
async def get_alerts(
    tenant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """Get current alerts for tenant or globally."""
    
    analytics = AnalyticsService(db)
    return await analytics.check_alerts(tenant_id)


@router.get("/health/dashboard")
async def get_health_dashboard(
    db: AsyncSession = Depends(get_async_session)
):
    """Get health dashboard data for operations team."""
    
    analytics = AnalyticsService(db)
    
    # Get key health indicators
    global_metrics = await analytics.get_global_metrics()
    alerts = await analytics.check_alerts()
    
    # Get top tenants by usage
    top_tenants_query = select(
        Tenant.id,
        Tenant.display_name,
        func.count(User.id).label('user_count')
    ).select_from(
        Tenant.__table__.join(User.__table__, Tenant.id == User.tenant_id)
    ).where(
        Tenant.is_active == True
    ).group_by(
        Tenant.id, Tenant.display_name
    ).order_by(
        func.count(User.id).desc()
    ).limit(10)
    
    top_tenants_result = await db.execute(top_tenants_query)
    top_tenants = [
        {"tenant_id": row.id, "name": row.display_name, "users": row.user_count}
        for row in top_tenants_result
    ]
    
    return {
        "global_metrics": global_metrics,
        "active_alerts": len([a for a in alerts if a.get("severity") in ["critical", "warning"]]),
        "top_tenants": top_tenants,
        "system_health": "healthy" if global_metrics.global_uptime_percent > 99.0 else "degraded"
    }