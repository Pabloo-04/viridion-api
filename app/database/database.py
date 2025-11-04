from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Boolean, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SensorReading(Base):
    """Sensor readings table (time-series)"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    soil_moisture = Column(Float, nullable=False)
    light_level = Column(Float, nullable=True)


class WateringEvent(Base):
    """Watering events table"""
    __tablename__ = "watering_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    duration = Column(Integer, nullable=False)  # seconds
    water_amount = Column(Float, nullable=True)  # liters
    triggered_by = Column(String, nullable=False)  # 'manual', 'scheduled', 'ml_prediction'


class Prediction(Base):
    """ML predictions table"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    should_water = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    soil_moisture = Column(Float, nullable=False)


class SystemStatus(Base):
    """System status table"""
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    watering_active = Column(Boolean, default=False)
    auto_watering_enabled = Column(Boolean, default=True)
    duration_setting = Column(Integer, default=10)
    threshold_setting = Column(Integer, default=30)


# Create all tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()