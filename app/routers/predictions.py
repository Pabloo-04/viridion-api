from fastapi import APIRouter
from app.models.predictor import predictor
from app.database.schemas import WateringRequest, WateringPredictionResponse

router = APIRouter()

@router.post("/watering", response_model=WateringPredictionResponse)
def watering_prediction(data: WateringRequest):
    
    result = predictor.predict(
        soil_moisture=data.soil_moisture,
        soil_humidity=data.soil_humidity,
        temperature=data.temperature
    )
    return result
