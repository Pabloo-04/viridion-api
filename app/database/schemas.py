from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SensorData(BaseModel):
    """Sensor reading data"""
    temperature: float = Field(..., ge=-50, le=100, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage")
    light_level: Optional[float] = Field(None, ge=0, description="Light level")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CurrentSensorResponse(BaseModel):
    """Current sensor data response"""
    temperature: float
    humidity: float
    soilMoisture: float
    wateringStatus: bool = False
    lastUpdate: str


class HistoricalDataPoint(BaseModel):
    """Historical data point"""
    time: str
    temp: float
    humidity: float
    soil: float


class WateringSchedule(BaseModel):
    """Watering schedule configuration"""
    enabled: bool
    duration: int = Field(..., ge=1, le=60, description="Duration in minutes")
    threshold: int = Field(..., ge=0, le=100, description="Soil moisture threshold")


class WateringToggle(BaseModel):
    """Toggle watering status"""
    status: bool


class PredictionRequest(BaseModel):
    """ML prediction request"""
    temperature: float
    humidity: float
    soil_moisture: float
    hour_of_day: int = Field(..., ge=0, le=23)


class PredictionResponse(BaseModel):
    """ML prediction response"""
    should_water: bool
    confidence: float = Field(..., ge=0, le=1)
    next_watering_time: str
    reasoning: Optional[str] = None