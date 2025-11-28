from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.database import get_db, WateringEvent, SystemStatus
from app.database.schemas import WateringToggle
from app.mqtt.mqtt_handler import publish_watering_command  , get_watering_state
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory runtime state
watering_state = {
    "active": False,
    "schedule": {
        "enabled": True,
        "duration": 10,
        "threshold": 30
    }
}


@router.post("/toggle")
async def toggle_watering(data: WateringToggle, db: AsyncSession = Depends(get_db)):
    """Toggle watering on/off and send command to ESP32 via MQTT"""
    
    # Update in-memory state
    watering_state["active"] = data.status
    
    # Send MQTT command to ESP32
    plant_id = data.plant_id or "plant1"
    duration =  data.duration
    
    mqtt_sent = publish_watering_command(
        plant_id=plant_id,
        status=data.status,
        duration=duration
    )
    
    if not mqtt_sent:
        logger.warning("⚠️ Failed to send MQTT command")
    
    # Log watering event to database
    if data.status:
        event = WateringEvent(
            duration=duration ,  
            triggered_by="manual",
            timestamp=datetime.utcnow()
        )
        db.add(event)
        await db.commit()
    
    return {
        "success": True,
        "status": data.status,
        "mqtt_sent": mqtt_sent,
        "plant_id": plant_id,
        "duration": duration,
        "message": f"💧 Watering {'started' if data.status else 'stopped'}"
    }


@router.get("/status")
async def get_watering_status(plant_id: str = "plant1"):
    """Get current watering status from ESP32 via MQTT"""
    # Get real-time status from MQTT handler
    mqtt_state = get_watering_state(plant_id)
    
    # Update in-memory state with MQTT state if available
    if mqtt_state.get("status") != "unknown":
        watering_state["active"] = mqtt_state.get("active", False)
    
    return {
        "wateringStatus": watering_state["active"],
        "schedule": watering_state["schedule"],
        "mqtt_status": mqtt_state.get("status"),
        "last_update": mqtt_state.get("last_update")
    }


@router.get("/history")
async def get_watering_history(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Get watering event history"""
    result = await db.execute(
        select(WateringEvent).order_by(desc(WateringEvent.timestamp)).limit(limit)
    )
    events = result.scalars().all()

    return [
        {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "duration": event.duration,
            "triggered_by": event.triggered_by
        }
        for event in events
    ]