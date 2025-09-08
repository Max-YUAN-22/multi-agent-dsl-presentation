# backend/websocket.py
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import json
from backend.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "pong":
                manager.update_last_pong(websocket)
            else:
                print(f"Received unexpected data: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
