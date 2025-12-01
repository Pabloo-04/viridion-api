from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db, SensorReading
from app.database.schemas import SensorReadingCreate, SensorReadingResponse, WaterTankStatus
from app.services import sensor_service
from app.services.websocket_manager import ws_manager

router = APIRouter()


# ------------------------------
# 🌱 Create a new reading
# ------------------------------
@router.post("/", response_model=SensorReadingResponse)
async def add_sensor_reading(data: SensorReadingCreate, db: AsyncSession = Depends(get_db)):
    reading = SensorReading(**data.dict())
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading


# ------------------------------
# 📊 Get full reading list
# ------------------------------
@router.get("/", response_model=list[SensorReadingResponse])
async def list_readings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorReading))
    return result.scalars().all()


# ------------------------------
# 🌾 Soil Moisture History
# ------------------------------
@router.get("/soil")
async def get_soil_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_soil_history(db, plant_id, limit)


# ------------------------------
#  Air Temperature History
# ------------------------------
@router.get("/temperature")
async def get_temperature_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_temperature_history(db, plant_id, limit)


# ------------------------------
#  Air Humidity History
# ------------------------------
@router.get("/humidity")
async def get_humidity_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_humidity_history(db, plant_id, limit)

# ------------------------------
#  Air Humidity History
# ------------------------------
@router.get("/pressure")
async def pressure_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_pressure_history(db, plant_id, limit)

# ------------------------------
#  Light Level History
# ------------------------------

@router.get("/light")
async def pressure_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_light_history(db, plant_id, limit)

# ------------------------------
# 💧 Water Tank Status
# ------------------------------
@router.get("/tank/status", response_model=WaterTankStatus)
async def get_tank_status(
    plant_id: str = Query("plant1", description="Plant ID to check water tank status")
):
    """Get current water tank status (has water or not)"""
    status_data = await sensor_service.get_water_tank_status(plant_id)
    return WaterTankStatus(**status_data)


# ------------------------------
# 🔌 WebSocket - Real-time Sensor Updates
# ------------------------------
@router.websocket("/ws/{plant_id}")
async def websocket_endpoint(websocket: WebSocket, plant_id: str):
    """
    WebSocket endpoint for real-time sensor updates.
    Connect to: ws://localhost:8000/api/sensors/ws/plant1

    Message types received:
    - sensor_update: Real-time sensor data
    - watering_update: Watering status changes
    - tank_update: Water tank status changes
    """
    await ws_manager.connect(websocket, plant_id)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back for ping/pong if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, plant_id)
        print(f"🔌 Client disconnected from {plant_id}")