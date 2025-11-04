from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.database import get_db, SensorReading
from app.database.schemas import SensorData, CurrentSensorResponse, HistoricalDataPoint
from datetime import datetime, timedelta
from typing import List

router = APIRouter()


@router.post("/readings", status_code=201)
async def create_reading(data: SensorData, db: Session = Depends(get_db)):
    """Store new sensor reading"""
    reading = SensorReading(
        temperature=data.temperature,
        humidity=data.humidity,
        soil_moisture=data.soil_moisture,
        light_level=data.light_level,
        timestamp=data.timestamp
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    
    return {
        "id": reading.id,
        "timestamp": reading.timestamp,
        "message": "Reading stored successfully"
    }


@router.get("/current", response_model=CurrentSensorResponse)
async def get_current(db: Session = Depends(get_db)):
    """Get latest sensor reading"""
    reading = db.query(SensorReading).order_by(desc(SensorReading.timestamp)).first()
    
    if not reading:
        raise HTTPException(status_code=404, detail="No sensor data available")
    
    return CurrentSensorResponse(
        temperature=reading.temperature,
        humidity=reading.humidity,
        soilMoisture=reading.soil_moisture,
        wateringStatus=False,  # TODO: Get from system status
        lastUpdate=reading.timestamp.isoformat()
    )


@router.get("/history", response_model=List[HistoricalDataPoint])
async def get_history(hours: int = 24, db: Session = Depends(get_db)):
    """Get historical sensor data"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Query with time bucketing for efficient aggregation
    readings = db.query(SensorReading).filter(
        SensorReading.timestamp >= cutoff
    ).order_by(SensorReading.timestamp).all()
    
    # Group by hour
    hourly_data = {}
    for reading in readings:
        hour_key = reading.timestamp.strftime("%H:%M")
        if hour_key not in hourly_data:
            hourly_data[hour_key] = {
                "temps": [],
                "humidities": [],
                "soils": []
            }
        hourly_data[hour_key]["temps"].append(reading.temperature)
        hourly_data[hour_key]["humidities"].append(reading.humidity)
        hourly_data[hour_key]["soils"].append(reading.soil_moisture)
    
    # Calculate averages
    result = []
    for time_key, values in sorted(hourly_data.items()):
        result.append(HistoricalDataPoint(
            time=time_key,
            temp=round(sum(values["temps"]) / len(values["temps"]), 1),
            humidity=round(sum(values["humidities"]) / len(values["humidities"]), 0),
            soil=round(sum(values["soils"]) / len(values["soils"]), 0)
        ))
    
    return result


@router.get("/analytics")
async def get_analytics(days: int = 7, db: Session = Depends(get_db)):
    """Get analytics data for dashboard"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    readings = db.query(SensorReading).filter(
        SensorReading.timestamp >= cutoff
    ).all()
    
    if not readings:
        return {"message": "No data available for analytics"}
    
    return {
        "total_readings": len(readings),
        "avg_temperature": round(sum(r.temperature for r in readings) / len(readings), 1),
        "avg_humidity": round(sum(r.humidity for r in readings) / len(readings), 1),
        "avg_soil_moisture": round(sum(r.soil_moisture for r in readings) / len(readings), 1),
        "min_soil_moisture": min(r.soil_moisture for r in readings),
        "max_temperature": max(r.temperature for r in readings),
        "period_days": days
    }