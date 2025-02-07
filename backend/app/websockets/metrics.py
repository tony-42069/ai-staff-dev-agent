"""WebSocket handler for real-time metrics updates."""
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime
import logging
from fastapi import WebSocket, WebSocketDisconnect

from ..services.metrics_collector import collector

logger = logging.getLogger(__name__)

class MetricsWebsocketManager:
    """Manages WebSocket connections for metrics updates."""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "all": set(),  # Connections receiving all metrics
            "system": set(),  # System-level metrics only
        }
        self.agent_connections: Dict[str, Set[WebSocket]] = {}
        self.client_subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        subscriptions: Optional[Set[str]] = None
    ) -> None:
        """Handle new WebSocket connection."""
        try:
            await websocket.accept()
            
            # Store client subscriptions
            self.client_subscriptions[websocket] = subscriptions or {"all"}
            
            # Add to relevant connection sets
            for subscription in self.client_subscriptions[websocket]:
                if subscription.startswith("agent:"):
                    agent_id = subscription.split(":")[1]
                    if agent_id not in self.agent_connections:
                        self.agent_connections[agent_id] = set()
                    self.agent_connections[agent_id].add(websocket)
                else:
                    if subscription not in self.active_connections:
                        self.active_connections[subscription] = set()
                    self.active_connections[subscription].add(websocket)

            logger.info(
                "Client %s connected with metrics subscriptions: %s",
                client_id,
                subscriptions
            )

            # Send initial state
            await self._send_initial_state(websocket, subscriptions)

        except Exception as e:
            logger.error("Error in metrics WebSocket connection: %s", e)
            await self.disconnect(websocket)
            raise

    async def disconnect(self, websocket: WebSocket) -> None:
        """Handle WebSocket disconnection."""
        try:
            # Remove from all connection sets
            subscriptions = self.client_subscriptions.pop(websocket, set())
            
            for subscription in subscriptions:
                if subscription.startswith("agent:"):
                    agent_id = subscription.split(":")[1]
                    if agent_id in self.agent_connections:
                        self.agent_connections[agent_id].discard(websocket)
                else:
                    if subscription in self.active_connections:
                        self.active_connections[subscription].discard(websocket)

            logger.info("Metrics client disconnected")

        except Exception as e:
            logger.error("Error in metrics WebSocket disconnection: %s", e)

    async def broadcast_metric_update(
        self,
        category: str,
        name: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Broadcast metric update to relevant clients."""
        message = {
            "type": "metric_update",
            "timestamp": datetime.utcnow().isoformat(),
            "metric": {
                "category": category,
                "name": name,
                "value": value,
                "metadata": metadata or {}
            }
        }

        # Determine target connections
        targets = set()
        
        # Add connections subscribed to all updates
        targets.update(self.active_connections.get("all", set()))
        
        # Add system metric subscribers if applicable
        if category == "system":
            targets.update(self.active_connections.get("system", set()))
        
        # Add agent-specific connections if applicable
        if category.startswith("agent."):
            agent_id = category.split(".")[1]
            targets.update(self.agent_connections.get(agent_id, set()))

        # Broadcast to all targets
        for websocket in targets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(
                    "Error sending metric update to client: %s",
                    e
                )
                await self.disconnect(websocket)

    async def broadcast_system_metrics(self) -> None:
        """Broadcast system metrics updates periodically."""
        while True:
            try:
                # Get current system metrics
                metrics = {
                    "memory": collector.get_metric("system", "memory_usage"),
                    "cpu": collector.get_metric("system", "cpu_usage"),
                    "disk": collector.get_metric("system", "disk_usage")
                }

                message = {
                    "type": "system_metrics",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": metrics
                }

                # Send to system subscribers
                targets = self.active_connections.get("system", set())
                targets.update(self.active_connections.get("all", set()))

                for websocket in targets:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(
                            "Error sending system metrics to client: %s",
                            e
                        )
                        await self.disconnect(websocket)

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error("Error in system metrics broadcast: %s", e)
                await asyncio.sleep(1)

    async def _send_initial_state(
        self,
        websocket: WebSocket,
        subscriptions: Set[str]
    ) -> None:
        """Send initial metrics state to new connection."""
        try:
            metrics_data = {}

            # Include system metrics if subscribed
            if "system" in subscriptions or "all" in subscriptions:
                metrics_data["system"] = {
                    "memory": collector.get_metric("system", "memory_usage"),
                    "cpu": collector.get_metric("system", "cpu_usage"),
                    "disk": collector.get_metric("system", "disk_usage")
                }

            # Include agent metrics if subscribed
            for subscription in subscriptions:
                if subscription.startswith("agent:"):
                    agent_id = subscription.split(":")[1]
                    agent_metrics = {
                        name: value
                        for category, values in collector.metrics.items()
                        for name, value in values.items()
                        if category == f"agent.{agent_id}"
                    }
                    if agent_metrics:
                        metrics_data[f"agent.{agent_id}"] = agent_metrics

            if metrics_data:
                await websocket.send_json({
                    "type": "initial_state",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": metrics_data
                })

        except Exception as e:
            logger.error("Error sending initial metrics state: %s", e)
            await self.disconnect(websocket)

# Global WebSocket manager instance
metrics_ws_manager = MetricsWebsocketManager()

async def handle_metrics_websocket(
    websocket: WebSocket,
    client_id: str,
    subscriptions: Optional[Set[str]] = None
) -> None:
    """Handle metrics WebSocket connection lifecycle."""
    try:
        await metrics_ws_manager.connect(
            websocket,
            client_id,
            subscriptions
        )
        
        while True:
            try:
                # Wait for messages (client commands, etc.)
                message = await websocket.receive_json()
                
                # Handle client messages
                if message.get("type") == "subscribe":
                    new_subs = set(message.get("subscriptions", []))
                    metrics_ws_manager.client_subscriptions[websocket] = new_subs
                
                elif message.get("type") == "unsubscribe":
                    metrics_ws_manager.client_subscriptions[websocket].clear()
                
            except WebSocketDisconnect:
                await metrics_ws_manager.disconnect(websocket)
                break
                
            except Exception as e:
                logger.error("Error handling metrics WebSocket message: %s", e)
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except Exception as e:
        logger.error("Metrics WebSocket handler error: %s", e)
        try:
            await metrics_ws_manager.disconnect(websocket)
        except:
            pass
