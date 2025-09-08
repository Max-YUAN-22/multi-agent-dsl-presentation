# backend/websocket_manager.py
import asyncio
import time
from typing import List, Dict, Tuple
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections with heartbeat."""

    def __init__(self, heartbeat_interval: int = 30, timeout: int = 60) -> None:
        self.active: Dict[WebSocket, float] = {}
        self.heartbeat_interval = heartbeat_interval
        self.timeout = timeout
        self._heartbeat_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        """Accepts and stores a new WebSocket connection."""
        await websocket.accept()
        self.active[websocket] = time.time()
        print(f"WebSocket {websocket.client} connected. Total clients: {len(self.active)}")
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            print("Heartbeat loop started.")

    def disconnect(self, websocket: WebSocket):
        """Removes a WebSocket connection."""
        if websocket in self.active:
            del self.active[websocket]
            print(f"WebSocket {websocket.client} disconnected. Total clients: {len(self.active)}")

    def update_last_pong(self, websocket: WebSocket):
        if websocket in self.active:
            self.active[websocket] = time.time()
            print(f"Received pong from {websocket.client}")

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            now = time.time()
            print(f"Running heartbeat check. Active connections: {len(self.active)}")
            dead: List[WebSocket] = []
            for ws, last_pong in self.active.items():
                if now - last_pong > self.timeout:
                    print(f"Client {ws.client} timed out. Disconnecting.")
                    dead.append(ws)
                else:
                    try:
                        print(f"Sending ping to {ws.client}")
                        await ws.send_json({"type": "ping"})
                    except Exception as e:
                        print(f"Failed to send ping to {ws.client}: {e}. Disconnecting.")
                        dead.append(ws)
            
            for ws in dead:
                self.disconnect(ws)

    async def broadcast(self, message: dict):
        """Sends a JSON message to all active connections."""
        print(f"Broadcasting message to {len(self.active)} clients: {message}")
        dead: List[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"Failed to broadcast to {ws.client}: {e}. Disconnecting.")
                dead.append(ws)
        
        for ws in dead:
            self.disconnect(ws)


# Singleton instance for the connection manager
manager = ConnectionManager(heartbeat_interval=5, timeout=10)