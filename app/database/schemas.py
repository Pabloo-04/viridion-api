# app/database/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ----------------------------
# Sensor Reading
# ----------------------------
class SensorReadingBase(BaseModel):
    temperature: float = Field(..., ge=-50, le=100, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage")
    light_level: Optional[float] = Field(None, ge=0, description="Light intensity")


class SensorReadingCreate(SensorReadingBase):
    """Schema for creating a sensor reading"""
    pass


class SensorReadingResponse(SensorReadingBase):
    """Schema for returning a sensor reading"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # allows ORM to Pydantic conversion


# ----------------------------
# Watering Event
# ----------------------------
class WateringEventBase(BaseModel):
    duration: int = Field(..., ge=1, le=600, description="Watering duration (seconds)")
    water_amount: Optional[float] = Field(None, ge=0, description="Water amount (liters)")
    triggered_by: str = Field(..., description="Trigger source: manual/scheduled/ml_prediction")


class WateringEventCreate(WateringEventBase):
    pass


class WateringEventResponse(WateringEventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Prediction
# ----------------------------
class PredictionBase(BaseModel):
    should_water: bool
    confidence: float = Field(..., ge=0, le=1)
    temperature: float
    humidity: float
    soil_moisture: float


class PredictionCreate(PredictionBase):
    pass


class PredictionResponse(PredictionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# ----------------------------
# Watering Toggle (simple endpoint)
# ----------------------------
class WateringToggle(BaseModel):
    """Toggle watering system on/off"""
    status: bool

# ----------------------------
# System Status
# ----------------------------
class SystemStatusBase(BaseModel):
    watering_active: bool = False
    auto_watering_enabled: bool = True
    duration_setting: int = Field(10, ge=1, le=600)
    threshold_setting: int = Field(30, ge=0, le=100)


class SystemStatusResponse(SystemStatusBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
