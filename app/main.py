from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import sensors, watering, predictions

app = FastAPI(
    title="Smart Garden API",
    description="IoT API for smart garden monitoring and control with ML predictions",
    version="0.1.0",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(watering.router, prefix="/api/watering", tags=["Watering"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["ML Predictions"])


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Smart Garden API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }