from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.database import get_db, WateringEvent, SystemStatus
from app.database.schemas import WateringToggle
from datetime import datetime

router = APIRouter()

# In-memory runtime state (for quick testing; real IoT would use DB)
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
    """Toggle watering on/off"""
    watering_state["active"] = data.status

    if data.status:
        # Create and store a watering event
        event = WateringEvent(
            duration=watering_state["schedule"]["duration"] * 60,  # convert minutes → seconds
            triggered_by="manual",
            timestamp=datetime.utcnow()
        )
        db.add(event)
        await db.commit()

    return {
        "success": True,
        "status": data.status,
        "message": f"💧 Watering {'started' if data.status else 'stopped'}"
    }


@router.get("/status")
async def get_watering_status():
    """Get current watering status"""
    return {
        "wateringStatus": watering_state["active"],
        "schedule": watering_state["schedule"]
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
