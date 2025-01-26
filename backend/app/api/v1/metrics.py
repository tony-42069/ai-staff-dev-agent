from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional

from ...services.metrics_collector import collector

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/current")
async def get_current_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    try:
        return collector.get_current_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve current metrics: {str(e)}"
        )

@router.get("/historical/{timeframe}")
async def get_historical_metrics(
    timeframe: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get historical metrics for specified timeframe"""
    try:
        metrics = collector.get_historical_metrics(timeframe)
        if limit:
            metrics = metrics[-limit:]
        return metrics
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timeframe: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve historical metrics: {str(e)}"
        )

@router.get("/operations/summary")
async def get_operations_summary() -> Dict[str, Any]:
    """Get summary of operation metrics"""
    metrics = collector.get_current_metrics()
    return {
        "operations": metrics["operations"],
        "queues": metrics["queues"]
    }

@router.get("/system/health")
async def get_system_health() -> Dict[str, Any]:
    """Get system health metrics"""
    metrics = collector.get_current_metrics()
    return {
        "system": metrics["system"],
        "queue_sizes": {
            priority: data["size"]
            for priority, data in metrics["queues"].items()
        }
    }
