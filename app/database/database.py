from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Float, DateTime, Boolean, String, create_engine
from app.config import settings

# ============================================================
# 🕐  TIMEZONE HELPER
# ============================================================
def get_local_time():
    """Get current time in El Salvador timezone (CST - UTC-6)"""
    return datetime.now(ZoneInfo(settings.timezone))


# ============================================================
# ⚙️  ASYNC ENGINE (for FastAPI routes)
# ============================================================
engine = create_async_engine(
    settings.database_url,  # e.g. postgresql+asyncpg://postgres:password@db:5432/smart_garden
    echo=False,
    future=True,
    pool_pre_ping=True,
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ============================================================
# ⚙️  SYNC ENGINE (for MQTT threads / background tasks)
# ============================================================
# Convert async URL -> sync URL (remove "+asyncpg")
sync_database_url = settings.database_url.replace("+asyncpg", "")

sync_engine = create_engine(
    sync_database_url,
    echo=False,
    pool_pre_ping=True,
)

# ✅ SessionLocal: normal (synchronous) DB session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# ============================================================
# 🧱  Base Model
# ============================================================
Base = declarative_base()

# ============================================================
# 📊  Tables / ORM Models
# ============================================================
class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(String, index=True, nullable=False)  # e.g. "plant1" or "plant2"
    timestamp = Column(DateTime(timezone=True), default=get_local_time, index=True, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    light_level = Column(Float, nullable=True)
    pressure = Column(Float,nullable = True)
  

class WateringEvent(Base):
    __tablename__ = "watering_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=get_local_time, index=True, nullable=False)
    duration = Column(Integer, nullable=False)
    water_amount = Column(Float, nullable=True)
    triggered_by = Column(String, nullable=False)  # manual/scheduled/ml_prediction


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=get_local_time, index=True, nullable=False)
    should_water = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    soil_moisture = Column(Float, nullable=False)


class SystemStatus(Base):
    __tablename__ = "system_status"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=get_local_time, nullable=False)
    watering_active = Column(Boolean, default=False)
    auto_watering_enabled = Column(Boolean, default=True)
    duration_setting = Column(Integer, default=10)
    threshold_setting = Column(Integer, default=30)

# ============================================================
# 🧩  Dependencies
# ============================================================
async def get_db():
    """Async session for FastAPI routes."""
    async with async_session() as session:
        yield session


def get_sync_db():
    """Sync session generator for background tasks (like MQTT)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()