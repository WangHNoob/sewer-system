from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.chat_engine import ChatEngine
import json, uuid, base64

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.engines: dict[str, ChatEngine] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.connections[session_id] = websocket
        self.engines[session_id] = ChatEngine(session_id=session_id)

    def disconnect(self, session_id: str):
        self.connections.pop(session_id, None)
        self.engines.pop(session_id, None)


manager = ConnectionManager()


@router.websocket("/chat/ws")
async def chat_websocket(websocket: WebSocket):
    session_id = str(uuid.uuid4())[:8]
    await manager.connect(websocket, session_id)

    await websocket.send_json({"type": "session", "session_id": session_id})

    try:
        while True:
            data = await websocket.receive_json()
            engine = manager.engines[session_id]

            if data["type"] == "text":
                async for event in engine.handle_text_message(data["content"]):
                    await websocket.send_json(event)

            elif data["type"] == "image":
                image_bytes = base64.b64decode(data["image_base64"])
                text = data.get("content", "请评估图像中的缺陷")
                async for event in engine.handle_image_message(image_bytes, text):
                    await websocket.send_json(event)

            elif data["type"] == "detect_only":
                image_bytes = base64.b64decode(data["image_base64"])
                result = engine.run_detection_only(image_bytes)
                await websocket.send_json({"type": "detection_result", "data": result})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
