"""
Monitoring and metrics collection utilities.
"""
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    
    def to_prometheus_format(self) -> str:
        """Convert to Prometheus format."""
        tags_str = ','.join([f'{k}="{v}"' for k, v in self.tags.items()])
        return f'{self.name}{{{tags_str}}} {self.value} {int(self.timestamp.timestamp() * 1000)}'


class MetricsCollector:
    """Centralized metrics collection."""
    
    def __init__(self):
        self.metrics: List[MetricPoint] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
    
    def counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a counter metric."""
        tags = tags or {}
        key = f"{name}:{','.join(sorted(tags.items()))}"
        self.counters[key] = self.counters.get(key, 0) + value
        
        self.metrics.append(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags
        ))
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric."""
        tags = tags or {}
        key = f"{name}:{','.join(sorted(tags.items()))}"
        self.gauges[key] = value
        
        self.metrics.append(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags
        ))
    
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric."""
        tags = tags or {}
        key = f"{name}:{','.join(sorted(tags.items()))}"
        
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        
        self.metrics.append(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags
        ))
    
    @contextmanager
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.histogram(f"{name}_duration_seconds", duration, tags)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {k: {"count": len(v), "sum": sum(v), "avg": sum(v)/len(v) if v else 0} 
                          for k, v in self.histograms.items()},
            "total_points": len(self.metrics)
        }


class PerformanceMonitor:
    """Monitor system and application performance."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_request_metrics(self, method: str, path: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        tags = {
            "method": method,
            "path": path,
            "status_code": str(status_code)
        }
        
        self.metrics.counter("http_requests_total", 1.0, tags)
        self.metrics.histogram("http_request_duration_seconds", duration, tags)
    
    def record_database_metrics(self, operation: str, table: str, duration: float, success: bool):
        """Record database operation metrics."""
        tags = {
            "operation": operation,
            "table": table,
            "status": "success" if success else "error"
        }
        
        self.metrics.counter("database_operations_total", 1.0, tags)
        self.metrics.histogram("database_operation_duration_seconds", duration, tags)
    
    def record_job_metrics(self, job_type: str, status: str, duration: Optional[float] = None):
        """Record job processing metrics."""
        tags = {
            "job_type": job_type,
            "status": status
        }
        
        self.metrics.counter("jobs_total", 1.0, tags)
        if duration is not None:
            self.metrics.histogram("job_duration_seconds", duration, tags)
    
    def record_file_upload_metrics(self, file_type: str, file_size: int, duration: float, success: bool):
        """Record file upload metrics."""
        tags = {
            "file_type": file_type,
            "status": "success" if success else "error"
        }
        
        self.metrics.counter("file_uploads_total", 1.0, tags)
        self.metrics.histogram("file_upload_duration_seconds", duration, tags)
        self.metrics.histogram("file_upload_size_bytes", file_size, tags)
    
    def record_external_service_metrics(self, service: str, operation: str, duration: float, success: bool):
        """Record external service call metrics."""
        tags = {
            "service": service,
            "operation": operation,
            "status": "success" if success else "error"
        }
        
        self.metrics.counter("external_service_calls_total", 1.0, tags)
        self.metrics.histogram("external_service_duration_seconds", duration, tags)


class BusinessMetrics:
    """Track business-specific metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_user_activity(self, tenant_id: str, user_id: str, action: str):
        """Record user activity."""
        tags = {
            "tenant_id": tenant_id,
            "action": action
        }
        
        self.metrics.counter("user_actions_total", 1.0, tags)
    
    def record_content_processing(self, tenant_id: str, content_type: str, duration_minutes: float):
        """Record content processing metrics."""
        tags = {
            "tenant_id": tenant_id,
            "content_type": content_type
        }
        
        self.metrics.counter("content_processed_total", 1.0, tags)
        self.metrics.histogram("content_processing_duration_minutes", duration_minutes, tags)
    
    def record_storage_usage(self, tenant_id: str, storage_type: str, size_bytes: int):
        """Record storage usage."""
        tags = {
            "tenant_id": tenant_id,
            "storage_type": storage_type
        }
        
        self.metrics.gauge("storage_usage_bytes", size_bytes, tags)
    
    def record_api_quota_usage(self, tenant_id: str, quota_type: str, used: int, limit: int):
        """Record API quota usage."""
        tags = {
            "tenant_id": tenant_id,
            "quota_type": quota_type
        }
        
        self.metrics.gauge("quota_used", used, tags)
        self.metrics.gauge("quota_limit", limit, tags)
        
        if limit > 0:
            usage_percentage = (used / limit) * 100
            self.metrics.gauge("quota_usage_percentage", usage_percentage, tags)


class HealthMetrics:
    """Track system health metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_system_health(self, component: str, status: str, response_time: Optional[float] = None):
        """Record system component health."""
        tags = {
            "component": component,
            "status": status
        }
        
        # Convert status to numeric for easier alerting
        status_value = 1.0 if status == "healthy" else 0.0
        self.metrics.gauge("component_health", status_value, tags)
        
        if response_time is not None:
            self.metrics.histogram("component_response_time_seconds", response_time, tags)
    
    def record_resource_usage(self, resource: str, usage_percentage: float):
        """Record resource usage."""
        tags = {"resource": resource}
        self.metrics.gauge("resource_usage_percentage", usage_percentage, tags)
    
    def record_error_rate(self, component: str, error_count: int, total_count: int):
        """Record error rates."""
        tags = {"component": component}
        
        if total_count > 0:
            error_rate = (error_count / total_count) * 100
            self.metrics.gauge("error_rate_percentage", error_rate, tags)


class AlertManager:
    """Manage alerts based on metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alert_rules = []
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule."""
        self.alert_rules.append(rule)
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alert rules and return triggered alerts."""
        alerts = []
        
        for rule in self.alert_rules:
            if self._evaluate_rule(rule):
                alerts.append({
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return alerts
    
    def _evaluate_rule(self, rule: Dict[str, Any]) -> bool:
        """Evaluate a single alert rule."""
        # This is a simplified implementation
        # In production, you'd integrate with a proper alerting system
        metric_name = rule.get("metric")
        threshold = rule.get("threshold")
        comparison = rule.get("comparison", "gt")
        
        if metric_name in self.metrics.gauges:
            current_value = self.metrics.gauges[metric_name]
            
            if comparison == "gt" and current_value > threshold:
                return True
            elif comparison == "lt" and current_value < threshold:
                return True
            elif comparison == "eq" and current_value == threshold:
                return True
        
        return False


class MetricsExporter:
    """Export metrics to external systems."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def export_to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for metric in self.metrics.metrics:
            lines.append(metric.to_prometheus_format())
        
        return '\n'.join(lines)
    
    def export_to_json(self) -> Dict[str, Any]:
        """Export metrics as JSON."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "tags": m.tags
                }
                for m in self.metrics.metrics
            ],
            "summary": self.metrics.get_metrics_summary()
        }
    
    async def send_to_external_system(self, endpoint: str, format_type: str = "json"):
        """Send metrics to external monitoring system."""
        try:
            if format_type == "json":
                data = self.export_to_json()
            elif format_type == "prometheus":
                data = self.export_to_prometheus()
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # In production, implement actual HTTP client to send data
            logger.info(f"Would send {len(self.metrics.metrics)} metrics to {endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")


# Global metrics collector instance
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor(metrics_collector)
business_metrics = BusinessMetrics(metrics_collector)
health_metrics = HealthMetrics(metrics_collector)
alert_manager = AlertManager(metrics_collector)
metrics_exporter = MetricsExporter(metrics_collector)