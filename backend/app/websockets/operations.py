"""WebSocket handler for real-time operation updates."""
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

# Configure logging
logging.basicConfig(level=logging.INFO)

from ..models.operations import Operation, OperationStatus
from ..services.operation_queue import queue_manager

logger = logging.getLogger(__name__)

class OperationsWebsocketManager:
    """Manages WebSocket connections for operation updates."""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "all": set(),  # Connections receiving all updates
            "system": set(),  # System-level updates
        }
        self.project_connections: Dict[str, Set[WebSocket]] = {}
        self.agent_connections: Dict[str, Set[WebSocket]] = {}
        self.client_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.client_heartbeats: Dict[WebSocket, datetime] = {}
        self.HEARTBEAT_TIMEOUT = 35  # Seconds (slightly higher than client's interval)

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        subscriptions: Optional[Set[str]] = None
    ) -> None:
        """Handle new WebSocket connection with improved error handling and heartbeat."""
        """Handle new WebSocket connection."""
        try:
            await websocket.accept()
            
            # Store client subscriptions and initialize heartbeat
            self.client_subscriptions[websocket] = subscriptions or {"all"}
            self.client_heartbeats[websocket] = datetime.utcnow()
            
            # Add to relevant connection sets
            for subscription in self.client_subscriptions[websocket]:
                if subscription.startswith("project:"):
                    project_id = subscription.split(":")[1]
                    if project_id not in self.project_connections:
                        self.project_connections[project_id] = set()
                    self.project_connections[project_id].add(websocket)
                elif subscription.startswith("agent:"):
                    agent_id = subscription.split(":")[1]
                    if agent_id not in self.agent_connections:
                        self.agent_connections[agent_id] = set()
                    self.agent_connections[agent_id].add(websocket)
                else:
                    if subscription not in self.active_connections:
                        self.active_connections[subscription] = set()
                    self.active_connections[subscription].add(websocket)

            logger.info(
                "Client %s connected with subscriptions: %s",
                client_id,
                subscriptions
            )

            # Start heartbeat monitoring for this connection
            asyncio.create_task(self._monitor_client_connection(websocket))

            # Send initial state
            await self._send_initial_state(websocket, subscriptions)

        except Exception as e:
            logger.error("Error in WebSocket connection: %s", e)
            await self.disconnect(websocket)
            raise

    async def disconnect(self, websocket: WebSocket) -> None:
        """Handle WebSocket disconnection with cleanup."""
        """Handle WebSocket disconnection."""
        try:
            # Remove from all tracking dictionaries
            subscriptions = self.client_subscriptions.pop(websocket, set())
            self.client_heartbeats.pop(websocket, None)
            
            for subscription in subscriptions:
                if subscription.startswith("project:"):
                    project_id = subscription.split(":")[1]
                    if project_id in self.project_connections:
                        self.project_connections[project_id].discard(websocket)
                elif subscription.startswith("agent:"):
                    agent_id = subscription.split(":")[1]
                    if agent_id in self.agent_connections:
                        self.agent_connections[agent_id].discard(websocket)
                else:
                    if subscription in self.active_connections:
                        self.active_connections[subscription].discard(websocket)

            logger.info("Client disconnected")

        except Exception as e:
            logger.error("Error in WebSocket disconnection: %s", e)

    async def broadcast_operation_update(
        self,
        operation: Operation,
        update_type: str = "update"
    ) -> None:
        """Broadcast operation update to relevant clients."""
        message = {
            "type": update_type,
            "timestamp": datetime.utcnow().isoformat(),
            "operation": {
                "id": operation.id,
                "project_id": operation.project_id,
                "agent_id": operation.agent_id,
                "type": operation.type,
                "capability": operation.capability,
                "status": operation.status,
                "progress": operation.progress,
                "error": operation.error,
                "result": operation.result,
                "metadata": operation.metadata
            }
        }

        # Determine target connections
        targets = set()
        
        # Add connections subscribed to all updates
        targets.update(self.active_connections.get("all", set()))
        
        # Add project-specific connections
        if operation.project_id:
            targets.update(
                self.project_connections.get(operation.project_id, set())
            )
        
        # Add agent-specific connections
        if operation.agent_id:
            targets.update(
                self.agent_connections.get(operation.agent_id, set())
            )

        # Broadcast to all targets
        for websocket in targets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(
                    "Error sending operation update to client: %s",
                    e
                )
                await self.disconnect(websocket)

    async def broadcast_queue_status(self) -> None:
        """Broadcast queue status updates."""
        while True:
            try:
                status = {
                    "type": "queue_status",
                    "timestamp": datetime.utcnow().isoformat(),
                    "queues": {
                        name: queue_manager.get_queue_status(name).dict()
                        for name in queue_manager.queues.keys()
                    }
                }

                # Send to system subscribers
                for websocket in self.active_connections.get("system", set()):
                    try:
                        await websocket.send_json(status)
                    except Exception as e:
                        logger.error(
                            "Error sending queue status to client: %s",
                            e
                        )
                        await self.disconnect(websocket)

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error("Error in queue status broadcast: %s", e)
                await asyncio.sleep(1)

    async def _send_initial_state(
        self,
        websocket: WebSocket,
        subscriptions: Set[str]
    ) -> None:
        """Send initial state to new connection."""
        try:
            # Send active operations
            active_ops = []
            for op in queue_manager.active_operations.values():
                # Check if operation matches subscriptions
                if (
                    "all" in subscriptions
                    or f"project:{op.project_id}" in subscriptions
                    or f"agent:{op.agent_id}" in subscriptions
                ):
                    active_ops.append({
                        "id": op.id,
                        "project_id": op.project_id,
                        "agent_id": op.agent_id,
                        "type": op.type,
                        "capability": op.capability,
                        "status": op.status,
                        "progress": op.progress,
                        "metadata": op.metadata
                    })

            if active_ops:
                await websocket.send_json({
                    "type": "initial_state",
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_operations": active_ops
                })

            # Send queue status if subscribed
            if "system" in subscriptions:
                status = {
                    "type": "queue_status",
                    "timestamp": datetime.utcnow().isoformat(),
                    "queues": {
                        name: queue_manager.get_queue_status(name).dict()
                        for name in queue_manager.queues.keys()
                    }
                }
                await websocket.send_json(status)

        except Exception as e:
            logger.error("Error sending initial state: %s", e)
            await self.disconnect(websocket)

    async def _monitor_client_connection(self, websocket: WebSocket) -> None:
        """Monitor client connection health."""
        while True:
            try:
                if websocket not in self.client_heartbeats:
                    break
                
                last_heartbeat = self.client_heartbeats[websocket]
                if (datetime.utcnow() - last_heartbeat).seconds > self.HEARTBEAT_TIMEOUT:
                    logger.warning("Client heartbeat timeout, closing connection")
                    await self.disconnect(websocket)
                    break
                
                await asyncio.sleep(self.HEARTBEAT_TIMEOUT // 2)
            except Exception as e:
                logger.error("Error in connection monitor: %s", e)
                await self.disconnect(websocket)
                break

    async def handle_ping(self, websocket: WebSocket) -> None:
        """Handle ping message from client."""
        try:
            self.client_heartbeats[websocket] = datetime.utcnow()
            await websocket.send_json({"type": "pong"})
        except Exception as e:
            logger.error("Error handling ping: %s", e)
            await self.disconnect(websocket)

# Global WebSocket manager instance
operations_ws_manager = OperationsWebsocketManager()

async def handle_websocket(
    websocket: WebSocket,
    client_id: str,
    subscriptions: Optional[Set[str]] = None
) -> None:
    """Handle WebSocket connection lifecycle with improved error handling."""
    try:
        await operations_ws_manager.connect(
            websocket,
            client_id,
            subscriptions
        )
        
        while True:
            try:
                # Wait for messages (client commands, etc.)
                message = await websocket.receive_json()
                
                # Handle client messages
                message_type = message.get("type")
                if message_type == "subscribe":
                    new_subs = set(message.get("subscriptions", []))
                    operations_ws_manager.client_subscriptions[websocket] = new_subs
                
                elif message_type == "unsubscribe":
                    operations_ws_manager.client_subscriptions[websocket].clear()
                
                elif message_type == "ping":
                    await operations_ws_manager.handle_ping(websocket)
                
            except WebSocketDisconnect:
                logger.info("Client %s disconnected", client_id)
                await operations_ws_manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error("Error handling WebSocket message: %s", e)
                if isinstance(websocket.client_state, WebSocketState):
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                
    except Exception as e:
        logger.error("WebSocket handler error: %s", e)
        try:
            await operations_ws_manager.disconnect(websocket)
        except:
            pass
