import asyncio
import json
import re
import paho.mqtt.client as mqtt
from datetime import datetime
from app.database.database import SessionLocal, SensorReading

BROKER = "viridion_mqtt"
PORT = 1883
TOPIC = "smartgarden/#"

mqtt_client = mqtt.Client()

# -----------------------------
# Per-plant buffers
# -----------------------------
sensor_buffers = {}  

def get_or_create_buffer(plant_id: str):
    if plant_id not in sensor_buffers:
        sensor_buffers[plant_id] = {
            "temperature": None,
            "humidity": None,
            "soil_moisture": None,
            "light_level": None,
            "last_update": None
        }
    return sensor_buffers[plant_id]


# -----------------------------
# MQTT CALLBACKS
# -----------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"📡 Subscribed to '{TOPIC}' (includes all plants)")
    else:
        print(f"❌ MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    topic = msg.topic
    print(f"📥 Received from {topic}: {payload}")

    match = re.match(r"smartgarden/(plant\d+)/", topic)
    if not match:
        print(f"⚠️ Ignoring message with no plant ID: {topic}")
        return

    plant_id = match.group(1)

    try:
        data = json.loads(payload)
        update_sensor_buffer(plant_id, data)
    except Exception as e:
        print(f"⚠️ Error parsing message for {plant_id}: {e}")


# -----------------------------
# BUFFER UPDATE + SAVE
# -----------------------------
def update_sensor_buffer(plant_id: str, data: dict):
    """Merge readings for the same plant and save combined record."""
    buffer = get_or_create_buffer(plant_id)
    updated = False

    for key, value in data.items():
        if key in buffer:
            buffer[key] = float(value)
            updated = True

    if updated:
        buffer["last_update"] = datetime.utcnow()
        print(f"🧩 Updated buffer for {plant_id}: {buffer}")

    # Save when all sensors reported
    if all(buffer[k] is not None for k in ["temperature", "humidity", "soil_moisture"]):
        save_combined_reading(plant_id, buffer)
        buffer["last_update"] = datetime.utcnow()  # keep last timestamp


# -----------------------------
# DATABASE LOGIC
# -----------------------------
def save_combined_reading(plant_id: str, buffer: dict):
    """Insert one row per plant per reading."""
    db = SessionLocal()
    try:
        reading = SensorReading(
            plant_id=plant_id,
            timestamp=buffer["last_update"] or datetime.utcnow(),
            temperature=buffer.get("temperature"),
            humidity=buffer.get("humidity"),
            soil_moisture=buffer.get("soil_moisture"),
            light_level=buffer.get("light_level"),
        )
        db.add(reading)
        db.commit()
        print(f"💾 Saved reading for {plant_id}: "
              f"T={reading.temperature}°C, H={reading.humidity}%, S={reading.soil_moisture}%")
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to save reading for {plant_id}: {e}")
    finally:
        db.close()


# -----------------------------
# STARTUP
# -----------------------------
def start_mqtt(loop: asyncio.AbstractEventLoop):
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()
    print("🚀 MQTT listener started")
