from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from app.database.database import SensorReading
from app.mqtt.mqtt_handler import get_water_tank_state


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
    stmt = stmt.order_by(SensorReading.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()[::-1]
    return [{"timestamp": r[1], "soil_moisture": r[0]} for r in rows if r[0] is not None]


async def get_temperature_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch temperature readings."""
    stmt = select(SensorReading.temperature, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()[::-1]
    return [{"timestamp": r[1], "temperature": r[0]} for r in rows if r[0] is not None]


async def get_humidity_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch air humidity readings."""
    stmt = select(SensorReading.humidity, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()[::-1]
    return [{"timestamp": r[1], "humidity": r[0]} for r in rows if r[0] is not None]


async def get_pressure_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch air pressure readings."""
    stmt = select(SensorReading.pressure, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()[::-1]
    return [{"timestamp": r[1], "pressure": r[0]} for r in rows if r[0] is not None]

async def get_light_history(
    db: AsyncSession, plant_id: Optional[str] = None, limit: int = 50
) -> List[SensorReading]:
    """Fetch air pressure readings."""
    stmt = select(SensorReading.light_level, SensorReading.timestamp)
    if plant_id:
        stmt = stmt.where(SensorReading.plant_id == plant_id)
    stmt = stmt.order_by(SensorReading.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()[::-1]
    return [{"timestamp": r[1], "light_level": r[0]} for r in rows if r[0] is not None]


async def get_water_tank_status(plant_id: str = "plant1") -> Dict:
    """Get current water tank status for a plant."""
    state = get_water_tank_state(plant_id)
    return {
        "has_water": state.get("has_water", False),
        "status": state.get("status", "unknown"),
        "plant_id": plant_id,
        "last_update": state.get("last_update")
    }