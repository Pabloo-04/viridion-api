from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db, SensorReading
from app.database.schemas import SensorReadingCreate, SensorReadingResponse
from app.services import sensor_service  # 👈 import the new service layer

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
# 🌡️ Air Temperature History
# ------------------------------
@router.get("/temperature")
async def get_temperature_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_temperature_history(db, plant_id, limit)


# ------------------------------
# 💧 Air Humidity History
# ------------------------------
@router.get("/humidity")
async def get_humidity_history(
    plant_id: str | None = Query(None, description="Filter by plant ID"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await sensor_service.get_humidity_history(db, plant_id, limit)
