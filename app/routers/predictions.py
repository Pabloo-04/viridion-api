from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.schemas import WateringRequest, WateringPredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()

@router.post("/watering", response_model=WateringPredictionResponse)
async def watering_prediction(
    data: WateringRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Make a watering prediction based on the latest sensor data for the given plant.
    """
    _, result = await PredictionService.predict_and_save(db, data.plant_id)
    return result
