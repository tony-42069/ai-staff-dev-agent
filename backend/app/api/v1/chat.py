from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict
import json
import asyncio
from datetime import datetime
from app.core.intelligence import CoreIntelligence
from app.models.chat import ChatMessage, ChatRequest

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.ping_interval = 30  # seconds

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        asyncio.create_task(self._keep_alive(websocket, client_id))

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: ChatMessage, websocket: WebSocket):
        await websocket.send_text(message.model_dump_json())

    async def _keep_alive(self, websocket: WebSocket, client_id: str):
        try:
            while client_id in self.active_connections:
                await asyncio.sleep(self.ping_interval)
                await websocket.send_json({"type": "ping"})
                pong = await websocket.receive_json()
                if pong.get("type") != "pong":
                    break
        except Exception:
            self.disconnect(client_id)

manager = ConnectionManager()

@router.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    intelligence = CoreIntelligence()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                request = ChatRequest.model_validate_json(data)
                
                # Send acknowledgment
                ack_message = ChatMessage(
                    type="status",
                    content="Processing your request...",
                    sender="agent"
                )
                await manager.send_message(ack_message, websocket)

                # Process the request
                if request.type == "message":
                    response = await intelligence.process_message(request.content)
                else:  # command
                    response = await intelligence.process_command(request.content)

                # Send response
                response_message = ChatMessage(
                    type="message",
                    content=response,
                    sender="agent"
                )
                await manager.send_message(response_message, websocket)

            except json.JSONDecodeError:
                error_message = ChatMessage(
                    type="status",
                    content="Error: Invalid JSON format",
                    sender="agent"
                )
                await manager.send_message(error_message, websocket)
            except ValueError as e:
                error_message = ChatMessage(
                    type="status",
                    content=f"Error: {str(e)}",
                    sender="agent"
                )
                await manager.send_message(error_message, websocket)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        try:
            error_message = ChatMessage(
                type="status",
                content=f"Error: {str(e)}",
                sender="agent"
            )
            await manager.send_message(error_message, websocket)
        finally:
            manager.disconnect(client_id)
