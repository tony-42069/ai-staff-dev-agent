from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from datetime import datetime
from app.core.intelligence import CoreIntelligence

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: Dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    intelligence = CoreIntelligence()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process the message based on its type
            if message["type"] == "message":
                # Send acknowledgment to user
                await manager.send_message({
                    "type": "message",
                    "content": "Processing your message...",
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

                # Process message with intelligence engine
                response = await intelligence.process_message(message["content"])

                # Send response back to user
                await manager.send_message({
                    "type": "message",
                    "content": response,
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

            elif message["type"] == "command":
                # Send acknowledgment to user
                await manager.send_message({
                    "type": "status",
                    "content": "Processing command...",
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

                # Process command with intelligence engine
                result = await intelligence.process_command(message["content"])

                # Send result back to user
                await manager.send_message({
                    "type": "message",
                    "content": result,
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        # Send error message to user
        await manager.send_message({
            "type": "status",
            "content": f"Error: {str(e)}",
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        manager.disconnect(websocket) 