import json
from typing import Dict, List
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time sensor updates"""

    def __init__(self):
        # Store active connections per plant_id
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, plant_id: str):
        """Accept a new WebSocket connection for a specific plant"""
        await websocket.accept()
        if plant_id not in self.active_connections:
            self.active_connections[plant_id] = []
        self.active_connections[plant_id].append(websocket)
        print(f"✅ WebSocket connected for {plant_id}. Total connections: {len(self.active_connections[plant_id])}")

    def disconnect(self, websocket: WebSocket, plant_id: str):
        """Remove a WebSocket connection"""
        if plant_id in self.active_connections:
            self.active_connections[plant_id].remove(websocket)
            print(f"❌ WebSocket disconnected for {plant_id}. Remaining: {len(self.active_connections[plant_id])}")
            # Clean up empty lists
            if not self.active_connections[plant_id]:
                del self.active_connections[plant_id]

    async def send_sensor_update(self, plant_id: str, data: dict):
        """Send sensor data to all clients subscribed to a specific plant"""
        if plant_id not in self.active_connections:
            return

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()

        message = json.dumps({
            "type": "sensor_update",
            "plant_id": plant_id,
            "data": data
        })

        # Send to all connected clients for this plant
        disconnected = []
        for connection in self.active_connections[plant_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"⚠️ Error sending to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, plant_id)

    async def send_watering_update(self, plant_id: str, status: dict):
        """Send watering status update to all clients subscribed to a plant"""
        if plant_id not in self.active_connections:
            return

        message = json.dumps({
            "type": "watering_update",
            "plant_id": plant_id,
            "data": status
        })

        disconnected = []
        for connection in self.active_connections[plant_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"⚠️ Error sending watering update: {e}")
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection, plant_id)

    async def send_tank_update(self, plant_id: str, status: dict):
        """Send water tank status update to all clients subscribed to a plant"""
        if plant_id not in self.active_connections:
            return

        message = json.dumps({
            "type": "tank_update",
            "plant_id": plant_id,
            "data": status
        })

        disconnected = []
        for connection in self.active_connections[plant_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"⚠️ Error sending tank update: {e}")
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection, plant_id)

    async def broadcast_all(self, message: dict):
        """Broadcast a message to all connected clients (all plants)"""
        message_str = json.dumps(message)
        for plant_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    print(f"⚠️ Error broadcasting to {plant_id}: {e}")


# Global WebSocket manager instance
ws_manager = ConnectionManager()
