"""API endpoints for agent management."""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, Query, Depends
from datetime import datetime, timedelta

from ...models.agent_operations import (
    AgentCapability,
    AgentOperation,
    AgentStatus,
    AgentMetrics,
    AgentWorkload,
    AgentEvent,
    AgentMaintenanceWindow
)
from ...models.operations import (
    Operation,
    OperationStatus,
    OperationType,
    OperationPriority
)
from ...services.agent_service import agent_service
from ...services.operation_queue import queue_manager
from ...services.metrics_collector import collector
from ...websockets.operations import operations_ws_manager

router = APIRouter()

@router.post("/agents/register")
async def register_agent(
    agent_id: str,
    capabilities: List[AgentCapability],
    metadata: Optional[Dict[str, Any]] = None
):
    """Register a new agent with capabilities."""
    try:
        await agent_service.register_agent(
            agent_id,
            [cap.name for cap in capabilities],
            metadata
        )
        return {"status": "success", "message": "Agent registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/deregister")
async def deregister_agent(agent_id: str):
    """Deregister an agent."""
    try:
        await agent_service.deregister_agent(agent_id)
        return {"status": "success", "message": "Agent deregistered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/heartbeat")
async def update_heartbeat(agent_id: str):
    """Update agent heartbeat."""
    try:
        await agent_service.update_agent_heartbeat(agent_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str) -> AgentStatus:
    """Get current status of an agent."""
    try:
        if agent_id not in agent_service.active_agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found"
            )

        agent_data = agent_service.active_agents[agent_id]
        active_ops = [
            op.id for op in queue_manager.active_operations.values()
            if op.agent_id == agent_id
        ]

        return AgentStatus(
            agent_id=agent_id,
            status=agent_data["status"],
            last_heartbeat=agent_data["last_heartbeat"],
            current_operations=active_ops,
            capabilities=agent_service.agent_capabilities[agent_id],
            metadata=agent_data["metadata"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str) -> AgentMetrics:
    """Get performance metrics for an agent."""
    try:
        metrics = await agent_service.get_agent_metrics(agent_id)
        return AgentMetrics(
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            **metrics
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/agents/{agent_id}/workload")
async def get_agent_workload(agent_id: str) -> AgentWorkload:
    """Get current workload for an agent."""
    try:
        active_ops = [
            op for op in queue_manager.active_operations.values()
            if op.agent_id == agent_id
        ]
        queued_ops = sum(
            1 for queue in queue_manager.queues.values()
            for op in queue.queue
            if op[2].agent_id == agent_id
        )

        metrics = agent_service.agent_metrics[agent_id]
        return AgentWorkload(
            agent_id=agent_id,
            active_operations=len(active_ops),
            queued_operations=queued_ops,
            completed_operations=metrics["operations_completed"],
            failed_operations=metrics["operations_failed"],
            average_processing_time=metrics["total_execution_time"] / max(metrics["operations_completed"], 1)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/operations")
async def create_agent_operation(
    agent_id: str,
    project_id: str,
    capability: str,
    params: Dict[str, Any],
    priority: OperationPriority = OperationPriority.NORMAL,
    operation_type: Optional[OperationType] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Operation:
    """Create a new operation for an agent."""
    try:
        operation = await agent_service.execute_operation(
            project_id,
            capability,
            params,
            priority,
            operation_type,
            metadata
        )
        return operation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/operations/{operation_id}/cancel")
async def cancel_agent_operation(
    agent_id: str,
    operation_id: str
):
    """Cancel an agent operation."""
    try:
        await agent_service.cancel_operation(operation_id)
        return {"status": "success", "message": "Operation cancelled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/agents/{agent_id}/operations")
async def list_agent_operations(
    agent_id: str,
    status: Optional[OperationStatus] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, gt=0, le=1000)
) -> List[Operation]:
    """List operations for an agent."""
    try:
        operations = [
            op for op in queue_manager.active_operations.values()
            if op.agent_id == agent_id
            and (not status or op.status == status)
            and (not start_time or op.created_at >= start_time)
            and (not end_time or op.created_at <= end_time)
        ]
        return operations[:limit]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/maintenance")
async def schedule_maintenance(
    agent_id: str,
    window: AgentMaintenanceWindow
):
    """Schedule maintenance for an agent."""
    try:
        # Record maintenance window
        collector.record_metric(
            "agent",
            f"maintenance.{agent_id}",
            window.dict()
        )
        return {"status": "success", "message": "Maintenance scheduled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/events")
async def record_agent_event(
    agent_id: str,
    event: AgentEvent
):
    """Record an agent event."""
    try:
        # Record event metrics
        collector.record_metric(
            "agent",
            f"event.{agent_id}",
            event.dict()
        )
        return {"status": "success", "message": "Event recorded"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/agents/{agent_id}/ws")
async def agent_websocket(
    websocket: WebSocket,
    agent_id: str,
    client_id: str = Query(...),
    subscriptions: Optional[List[str]] = Query(None)
):
    """WebSocket endpoint for real-time agent updates."""
    subs = set(subscriptions or [])
    subs.add(f"agent:{agent_id}")
    await operations_ws_manager.handle_websocket(
        websocket,
        client_id,
        subs
    )
