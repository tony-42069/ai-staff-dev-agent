import asyncio
import json
import logging
import uuid
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.security import OAuth2PasswordBearer
from ..models.operations import Operation, OperationMessage, OperationStatus, OperationUpdate

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.operation_subscribers: Dict[str, Set[str]] = {}
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.heartbeat_tasks[client_id] = asyncio.create_task(
            self._heartbeat(client_id, websocket)
        )
        logger.info(f"Client {client_id} connected")

    async def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.close()
            except Exception:
                pass
            del self.active_connections[client_id]
            
        # Cancel heartbeat task
        if client_id in self.heartbeat_tasks:
            self.heartbeat_tasks[client_id].cancel()
            del self.heartbeat_tasks[client_id]

        # Remove client from all operation subscriptions
        for subscribers in self.operation_subscribers.values():
            subscribers.discard(client_id)

        logger.info(f"Client {client_id} disconnected")

    async def subscribe_to_operation(self, client_id: str, operation_id: str):
        """Subscribe client to operation updates"""
        if operation_id not in self.operation_subscribers:
            self.operation_subscribers[operation_id] = set()
        self.operation_subscribers[operation_id].add(client_id)
        logger.info(f"Client {client_id} subscribed to operation {operation_id}")

    async def unsubscribe_from_operation(self, client_id: str, operation_id: str):
        """Unsubscribe client from operation updates"""
        if operation_id in self.operation_subscribers:
            self.operation_subscribers[operation_id].discard(client_id)
            if not self.operation_subscribers[operation_id]:
                del self.operation_subscribers[operation_id]
        logger.info(f"Client {client_id} unsubscribed from operation {operation_id}")

    async def broadcast_status(self, operation_id: str, update: OperationUpdate):
        """Broadcast operation status to all subscribed clients"""
        if operation_id not in self.operation_subscribers:
            return

        message = OperationMessage(
            type="status" if update.status != OperationStatus.COMPLETED else "complete",
            operation_id=operation_id,
            data={
                "status": update.status,
                "progress": update.progress,
                "result": update.result,
                "error": update.error,
                "metadata": update.metadata
            }
        )

        dead_clients = set()
        for client_id in self.operation_subscribers[operation_id]:
            websocket = self.active_connections.get(client_id)
            if websocket:
                try:
                    await websocket.send_json(message.dict())
                except WebSocketDisconnect:
                    dead_clients.add(client_id)
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {e}")
                    dead_clients.add(client_id)

        # Clean up dead connections
        for client_id in dead_clients:
            await self.disconnect(client_id)

    async def _heartbeat(self, client_id: str, websocket: WebSocket):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    await self.disconnect(client_id)
                    break
        except asyncio.CancelledError:
            pass

    async def handle_client_message(self, client_id: str, message: dict):
        """Handle incoming messages from clients"""
        try:
            msg_type = message.get("type")
            if msg_type == "subscribe":
                operation_id = message.get("operation_id")
                if operation_id:
                    await self.subscribe_to_operation(client_id, operation_id)
            elif msg_type == "unsubscribe":
                operation_id = message.get("operation_id")
                if operation_id:
                    await self.unsubscribe_from_operation(client_id, operation_id)
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            websocket = self.active_connections.get(client_id)
            if websocket:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid message format"}
                })


# Global connection manager instance
manager = ConnectionManager()

async def get_token(websocket: WebSocket):
    """Extract and validate token from WebSocket query parameters"""
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return None
        # TODO: Add token validation logic here
        return token
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return None

async def handle_websocket(websocket: WebSocket):
    """Main WebSocket connection handler"""
    client_id = str(uuid.uuid4())
    token = await get_token(websocket)
    if not token:
        return

    try:
        await manager.connect(websocket, client_id)
        
        while True:
            try:
                message = await websocket.receive_json()
                await manager.handle_client_message(client_id, message)
            except WebSocketDisconnect:
                await manager.disconnect(client_id)
                break
            except json.JSONDecodeError:
                logger.error("Received invalid JSON")
                continue
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                continue
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(client_id)
