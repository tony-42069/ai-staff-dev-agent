"""Service for managing agent operations and capabilities."""
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging
import uuid

from ..models.operations import (
    Operation,
    OperationStatus,
    OperationType,
    OperationPriority
)
from ..models.errors import (
    OperationError,
    AgentError,
    RetryStrategy,
    ErrorCode
)
from .operation_queue import queue_manager
from .retry_handler import retry_handler
from .metrics_collector import collector

logger = logging.getLogger(__name__)

class AgentService:
    """Service for managing agent operations."""
    def __init__(self):
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, Set[str]] = {}
        self.agent_metrics: Dict[str, Dict[str, Any]] = {}

    async def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new agent with capabilities."""
        try:
            if agent_id in self.active_agents:
                raise AgentError(
                    f"Agent {agent_id} already registered",
                    agent_id=agent_id
                )

            self.active_agents[agent_id] = {
                "registered_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow(),
                "status": "active",
                "metadata": metadata or {}
            }

            self.agent_capabilities[agent_id] = set(capabilities)
            self.agent_metrics[agent_id] = {
                "operations_completed": 0,
                "operations_failed": 0,
                "total_execution_time": 0.0,
                "capability_usage": {}
            }

            logger.info(
                "Agent %s registered with capabilities: %s",
                agent_id,
                capabilities
            )

            # Record metrics
            collector.record_metric(
                "agent",
                f"registration.{agent_id}",
                {
                    "capabilities": capabilities,
                    "metadata": metadata
                }
            )

        except Exception as e:
            logger.error("Failed to register agent: %s", e)
            raise

    async def deregister_agent(self, agent_id: str) -> None:
        """Deregister an agent."""
        try:
            if agent_id not in self.active_agents:
                raise AgentError(
                    f"Agent {agent_id} not registered",
                    agent_id=agent_id
                )

            # Cancel any active operations
            active_ops = [
                op for op in queue_manager.active_operations.values()
                if op.agent_id == agent_id
            ]
            for op in active_ops:
                await self.cancel_operation(op.id)

            # Clean up agent data
            self.active_agents.pop(agent_id)
            self.agent_capabilities.pop(agent_id)
            self.agent_metrics.pop(agent_id)

            logger.info("Agent %s deregistered", agent_id)

            # Record metrics
            collector.record_metric(
                "agent",
                f"deregistration.{agent_id}",
                {}
            )

        except Exception as e:
            logger.error("Failed to deregister agent: %s", e)
            raise

    async def update_agent_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat timestamp."""
        if agent_id in self.active_agents:
            self.active_agents[agent_id]["last_heartbeat"] = datetime.utcnow()

    async def check_agent_health(self) -> None:
        """Check health of all registered agents."""
        while True:
            try:
                current_time = datetime.utcnow()
                for agent_id, data in list(self.active_agents.items()):
                    last_heartbeat = data["last_heartbeat"]
                    if (current_time - last_heartbeat).total_seconds() > 60:
                        # Agent hasn't sent heartbeat in over a minute
                        data["status"] = "unavailable"
                        logger.warning("Agent %s appears unavailable", agent_id)

                        # Record metrics
                        collector.record_metric(
                            "agent",
                            f"health.{agent_id}",
                            {"status": "unavailable"}
                        )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error("Error checking agent health: %s", e)
                await asyncio.sleep(5)

    async def execute_operation(
        self,
        project_id: str,
        capability: str,
        params: Dict[str, Any],
        priority: OperationPriority = OperationPriority.NORMAL,
        operation_type: Optional[OperationType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Operation:
        """Execute an operation using an appropriate agent."""
        try:
            # Find suitable agent
            agent_id = await self._find_agent_for_capability(capability)
            if not agent_id:
                raise OperationError(
                    f"No agent available for capability: {capability}",
                    code=ErrorCode.CAPABILITY_NOT_FOUND
                )

            # Create operation
            operation = Operation(
                id=str(uuid.uuid4()),
                project_id=project_id,
                agent_id=agent_id,
                type=operation_type,
                capability=capability,
                status=OperationStatus.QUEUED,
                priority=priority,
                metadata=metadata or {}
            )

            # Add to queue
            await queue_manager.enqueue_operation(operation)

            logger.info(
                "Operation %s queued for agent %s",
                operation.id,
                agent_id
            )

            # Record metrics
            collector.record_metric(
                "operation",
                f"queued.{operation.id}",
                {
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "capability": capability,
                    "priority": priority.value
                }
            )

            return operation

        except Exception as e:
            logger.error("Failed to execute operation: %s", e)
            raise

    async def cancel_operation(self, operation_id: str) -> None:
        """Cancel an operation."""
        try:
            operation = queue_manager.active_operations.get(operation_id)
            if not operation:
                raise OperationError(
                    f"Operation {operation_id} not found",
                    code=ErrorCode.NOT_FOUND
                )

            operation.status = OperationStatus.CANCELLED
            logger.info("Operation %s cancelled", operation_id)

            # Record metrics
            collector.record_metric(
                "operation",
                f"cancelled.{operation_id}",
                {"reason": "user_requested"}
            )

        except Exception as e:
            logger.error("Failed to cancel operation: %s", e)
            raise

    async def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get metrics for an agent."""
        if agent_id not in self.agent_metrics:
            raise AgentError(
                f"Agent {agent_id} not found",
                agent_id=agent_id
            )

        metrics = self.agent_metrics[agent_id].copy()
        
        # Add current status
        if agent_id in self.active_agents:
            metrics["status"] = self.active_agents[agent_id]["status"]
            metrics["uptime"] = (
                datetime.utcnow() - 
                self.active_agents[agent_id]["registered_at"]
            ).total_seconds()

        # Add active operations
        active_ops = [
            op for op in queue_manager.active_operations.values()
            if op.agent_id == agent_id
        ]
        metrics["active_operations"] = len(active_ops)

        return metrics

    async def _find_agent_for_capability(
        self,
        capability: str
    ) -> Optional[str]:
        """Find an appropriate agent for a capability."""
        available_agents = [
            agent_id
            for agent_id, data in self.active_agents.items()
            if (
                data["status"] == "active"
                and capability in self.agent_capabilities[agent_id]
            )
        ]

        if not available_agents:
            return None

        # Simple round-robin selection for now
        # Could be enhanced with load balancing, performance metrics, etc.
        return available_agents[0]

    async def _update_agent_metrics(
        self,
        agent_id: str,
        operation: Operation,
        execution_time: float
    ) -> None:
        """Update metrics for an agent."""
        if agent_id not in self.agent_metrics:
            return

        metrics = self.agent_metrics[agent_id]
        
        if operation.status == OperationStatus.COMPLETED:
            metrics["operations_completed"] += 1
        elif operation.status == OperationStatus.FAILED:
            metrics["operations_failed"] += 1

        metrics["total_execution_time"] += execution_time

        # Update capability usage
        if operation.capability:
            if operation.capability not in metrics["capability_usage"]:
                metrics["capability_usage"][operation.capability] = 0
            metrics["capability_usage"][operation.capability] += 1

        # Record metrics
        collector.record_metric(
            "agent",
            f"metrics.{agent_id}",
            metrics
        )

# Global agent service instance
agent_service = AgentService()
