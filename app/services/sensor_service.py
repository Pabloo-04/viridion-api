from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database.database import SensorReading


# --------------------------------------------
# 🔍 Generic async query functions
# --------------------------------------------

async def get_soil_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch soil moisture readings."""
    stmt = select(SensorReading.soil_moisture, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.asc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    return [{"timestamp": r[1], "soil_moisture": r[0]} for r in rows if r[0] is not None]


async def get_temperature_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch temperature readings."""
    stmt = select(SensorReading.temperature, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.asc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    return [{"timestamp": r[1], "temperature": r[0]} for r in rows if r[0] is not None]


async def get_humidity_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch air humidity readings."""
    stmt = select(SensorReading.humidity, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.asc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    return [{"timestamp": r[1], "humidity": r[0]} for r in rows if r[0] is not None]
