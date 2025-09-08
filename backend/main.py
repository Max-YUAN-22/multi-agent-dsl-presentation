# backend/main.py
import os
import sys
import uvicorn
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add project root to the Python path to allow absolute imports from root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from backend.api_routes import router
from backend.websocket_manager import manager

# Create FastAPI app
app = FastAPI(title="Multi-Agent DSL Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("connection open")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "pong":
                    manager.update_last_pong(websocket)
            except json.JSONDecodeError:
                print(f"Received non-JSON message: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("connection closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)