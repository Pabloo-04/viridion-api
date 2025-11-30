import asyncio
import json
import re
import paho.mqtt.client as mqtt
from datetime import datetime
from zoneinfo import ZoneInfo  
from app.database.database import SessionLocal, SensorReading

BROKER = "viridion_mqtt"
PORT = 1883
TOPIC = "smartgarden/#"

mqtt_client = mqtt.Client()

# -----------------------------
# Per-plant buffers
# -----------------------------
sensor_buffers = {}

# 👇 ADD THIS: Watering state tracker
watering_states = {}

# 👇 Water tank state tracker
water_tank_states = {}

def get_or_create_buffer(plant_id: str):
    if plant_id not in sensor_buffers:
        sensor_buffers[plant_id] = {
            "temperature": None,
            "humidity": None,
            "soil_moisture": None,
            "light_level": None,
            "pressure": None,
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

    # Handle watering status updates
    if "/watering/status" in topic:
        handle_watering_status(topic, payload)
        return
    
    if "/tank/status" in topic:
        handle_water_tank_status(topic, payload)
        return

    # Handle sensor data
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
# WATERING STATUS HANDLER (UPDATED)
# -----------------------------
def handle_watering_status(topic: str, payload: str):
    """Update watering status when ESP32 reports back"""
    try:
        data = json.loads(payload)
        plant_id = data.get("plant_id", "unknown")
        status = data.get("status", "unknown")
        is_watering = data.get("is_watering", False)

        # 👇 UPDATE: Store the watering state globally
        watering_states[plant_id] = {
            "active": is_watering,
            "status": status,
            "last_update": datetime.now(ZoneInfo("America/El_Salvador")).isoformat()
        }

        print(f"💧 [{plant_id}] Watering status updated: {status} (active: {is_watering})")
        print(f"   Stored state: {watering_states[plant_id]}")

    except Exception as e:
        print(f"⚠️ Error handling watering status: {e}")


# -----------------------------
# WATER TANK STATUS HANDLER
# -----------------------------
def handle_water_tank_status(topic: str, payload: str):
    """Update water tank status when ESP32 reports back"""
    try:
        data = json.loads(payload)
        plant_id = data.get("plant_id", "unknown")
        has_water = data.get("has_water", False)  # Boolean value

        # Store the water tank state globally
        water_tank_states[plant_id] = {
            "has_water": has_water,
            "status": "available" if has_water else "empty",
            "last_update": datetime.now(ZoneInfo("America/El_Salvador")).isoformat()
        }

        print(f"💧 [{plant_id}] Water tank status updated: {'HAS WATER' if has_water else 'EMPTY'}")
        print(f"   Stored state: {water_tank_states[plant_id]}")

    except Exception as e:
        print(f"⚠️ Error handling water tank status: {e}")



def get_watering_state(plant_id: str = "plant1"):
    """Get current watering state for a plant"""
    state = watering_states.get(plant_id, {
        "active": False, 
        "status": "unknown",
        "last_update": None
    })
    print(f"🔍 Getting watering state for {plant_id}: {state}")
    return state

def get_water_tank_state(plant_id: str = "plant1"):
    """Get current water tank state for a plant"""
    state = water_tank_states.get(plant_id, {
        "has_water": False,
        "status": "unknown",
        "last_update": None
    })
    print(f"🔍 Getting water tank state for {plant_id}: {state}")
    return state


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

    required = ["temperature", "humidity", "soil_moisture"]

    if all(buffer[k] is not None for k in required):
        save_combined_reading(plant_id, buffer)


# -----------------------------
# DATABASE LOGIC
# -----------------------------
import traceback

def save_combined_reading(plant_id: str, buffer: dict):
    db = SessionLocal()
    try:
        reading = SensorReading(
            plant_id=plant_id,
            timestamp=datetime.now(ZoneInfo("America/El_Salvador")),
            temperature=buffer.get("temperature"),
            humidity=buffer.get("humidity"),
            soil_moisture=buffer.get("soil_moisture"),
            light_level=buffer.get("light_level"),
            pressure=buffer.get("pressure"),
        )

        db.add(reading)
        db.commit()
        print("💾 SUCCESS — Row saved to DB:", reading.id)

    except Exception as e:
        db.rollback()
        print("\n🚨 DATABASE INSERT FAILED 🚨")
        print("Error:", e)
        print("-------- FULL TRACEBACK --------")
        print(traceback.format_exc())
        print("--------------------------------\n")

    finally:
        db.close()


# -----------------------------
# PUBLISH COMMAND (for API)
# -----------------------------
def publish_watering_command(plant_id: str, status: bool, duration: int = 10):
    """Send watering command to ESP32"""
    topic = f"smartgarden/{plant_id}/watering/command"
    payload = json.dumps({
        "status": status,
        "duration": duration
    })
    
    result = mqtt_client.publish(topic, payload, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"📤 Published to {topic}: {payload}")
        return True
    else:
        print(f"❌ Failed to publish command, rc: {result.rc}")
        return False


# -----------------------------
# STARTUP
# -----------------------------
def start_mqtt(loop: asyncio.AbstractEventLoop):
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()
    print("🚀 MQTT listener started")


# -----------------------------
# EXPORT CLIENT (for router use)
# -----------------------------
def get_mqtt_client():
    """Get MQTT client instance for publishing from API"""
    return mqtt_client