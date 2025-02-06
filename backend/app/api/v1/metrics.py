"""API endpoints for system metrics."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from ...services.metrics_collector import collector

router = APIRouter()

class MetricValue(BaseModel):
    """Model for metric value response."""
    value: Any
    timestamp: str
    metadata: Dict[str, Any]

class MetricHistory(BaseModel):
    """Model for metric history response."""
    category: str
    name: str
    values: list[MetricValue]
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class MetricsSummary(BaseModel):
    """Model for metrics summary response."""
    categories: list[str]
    metrics: Dict[str, Dict[str, MetricValue]]
    timestamp: str

class MetricStatistics(BaseModel):
    """Model for metric statistics response."""
    count: int
    min: float
    max: float
    avg: float
    start_time: str
    end_time: str

@router.get("/metrics/current/{category}/{name}", response_model=MetricValue)
async def get_current_metric(category: str, name: str):
    """Get current value of a specific metric."""
    metric = collector.get_metric(category, name)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric

@router.get("/metrics/history/{category}/{name}", response_model=MetricHistory)
async def get_metric_history(
    category: str,
    name: str,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, gt=0, le=1000)
):
    """Get historical values for a specific metric."""
    history = collector.get_metric_history(category, name, start_time, end_time)
    if not history:
        raise HTTPException(status_code=404, detail="No history found")
        
    # Apply limit
    history = history[-limit:]
    
    return {
        "category": category,
        "name": name,
        "values": history,
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": end_time.isoformat() if end_time else None
    }

@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(category: Optional[str] = None):
    """Get summary of all current metrics."""
    return collector.get_metrics_summary(category)

@router.get("/metrics/statistics/{category}/{name}", response_model=MetricStatistics)
async def get_metric_statistics(
    category: str,
    name: str,
    window: timedelta = Query(default=timedelta(hours=1))
):
    """Get statistics for a metric over a time window."""
    stats = collector.calculate_statistics(category, name, window)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="No data available for the specified metric and time window"
        )
    return stats

@router.post("/metrics/{category}/{name}")
async def record_metric(
    category: str,
    name: str,
    value: Any,
    metadata: Optional[Dict[str, Any]] = None
):
    """Record a new metric value."""
    try:
        collector.record_metric(category, name, value, metadata)
        return {"status": "success", "message": "Metric recorded"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record metric: {str(e)}"
        )

@router.get("/metrics/system")
async def get_system_metrics():
    """Get current system metrics (CPU, memory, disk)."""
    return {
        "memory": collector.get_metric("system", "memory_usage"),
        "cpu": collector.get_metric("system", "cpu_usage"),
        "disk": collector.get_metric("system", "disk_usage")
    }

@router.get("/metrics/agent/{agent_id}")
async def get_agent_metrics(agent_id: str):
    """Get metrics for a specific agent."""
    metrics = {
        name: value
        for category, values in collector.metrics.items()
        for name, value in values.items()
        if category == f"agent.{agent_id}"
    }
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for agent {agent_id}"
        )
        
    return metrics

@router.get("/metrics/project/{project_id}")
async def get_project_metrics(project_id: str):
    """Get metrics for a specific project."""
    metrics = {
        name: value
        for category, values in collector.metrics.items()
        for name, value in values.items()
        if category == f"project.{project_id}"
    }
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for project {project_id}"
        )
        
    return metrics
