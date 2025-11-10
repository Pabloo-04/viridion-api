import time
import asyncio
from sqlalchemy.exc import OperationalError
from app.database.database import Base, engine
from app.mqtt.mqtt_handler import start_mqtt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import sensors, watering, predictions

app = FastAPI(
    title="Smart Garden API",
    description="IoT API for smart garden monitoring and control with ML predictions",
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(watering.router, prefix="/api/watering", tags=["Watering"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["ML Predictions"])

@app.on_event("startup")
async def on_startup():
    print("🚀 Starting Smart Garden API...")

    # Ensure database is ready
    for i in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("🗄️ Database ready.")
            break
        except OperationalError:
            print(f"⏳ Waiting for database... ({i+1}/10)")
            time.sleep(3)
    else:
        print("❌ Database connection failed after retries.")
        raise

    # Start MQTT background listener
    loop = asyncio.get_running_loop()
    start_mqtt(loop)
    print("📡 MQTT bridge initialized.")

@app.on_event("shutdown")
def on_shutdown():
    print("🛑 Shutting down Smart Garden API...")

@app.get("/")
def root():
    return {
        "message": "Smart Garden API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "operational"
    }
