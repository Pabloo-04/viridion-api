from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.database import get_db, WateringEvent, SystemStatus
from app.database.schemas import WateringToggle, WateringSchedule
from datetime import datetime

router = APIRouter()


watering_state = {
    "active": False,
    "schedule": {
        "enabled": True,
        "duration": 10,
        "threshold": 30
    }
}


@router.post("/toggle")
async def toggle_watering(data: WateringToggle, db: Session = Depends(get_db)):
    """Toggle watering on/off"""
    watering_state["active"] = data.status
    
    if data.status:
        # Log watering event
        event = WateringEvent(
            duration=watering_state["schedule"]["duration"] * 60,  # convert to seconds
            triggered_by="manual",
            timestamp=datetime.utcnow()
        )
        db.add(event)
        db.commit()
    
    return {
        "success": True,
        "status": data.status,
        "message": f"Watering {'started' if data.status else 'stopped'}"
    }


@router.get("/status")
async def get_watering_status():
    """Get current watering status"""
    return {
        "wateringStatus": watering_state["active"],
        "schedule": watering_state["schedule"]
    }


@router.post("/schedule")
async def update_schedule(schedule: WateringSchedule):
    """Update watering schedule"""
    watering_state["schedule"] = schedule.model_dump()
    
    return {
        "success": True,
        "schedule": watering_state["schedule"],
        "message": "Schedule updated successfully"
    }


@router.get("/history")
async def get_watering_history(limit: int = 50, db: Session = Depends(get_db)):
    """Get watering event history"""
    events = db.query(WateringEvent).order_by(
        desc(WateringEvent.timestamp)
    ).limit(limit).all()
    
    return [
        {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "duration": event.duration,
            "triggered_by": event.triggered_by
        }
        for event in events
    ]