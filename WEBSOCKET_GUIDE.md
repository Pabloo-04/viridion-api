# WebSocket Real-Time Updates Guide

This guide explains how to use the WebSocket endpoints for real-time sensor data updates in the Smart Garden API.

## Overview

The API now supports **WebSocket connections** for real-time updates alongside the existing HTTP REST endpoints. When your ESP32 publishes sensor data via MQTT, it's automatically broadcast to all connected WebSocket clients.

## WebSocket Endpoint

**URL Pattern:**
```
ws://localhost:8000/api/sensors/ws/{plant_id}
```

**Examples:**
- `ws://localhost:8000/api/sensors/ws/plant1`
- `ws://localhost:8000/api/sensors/ws/plant2`

## Message Types

The WebSocket sends three types of messages:

### 1. Sensor Update
Sent when new sensor readings arrive via MQTT.

```json
{
  "type": "sensor_update",
  "plant_id": "plant1",
  "data": {
    "temperature": 25.5,
    "humidity": 60.2,
    "soil_moisture": 45.8,
    "light_level": 1234,
    "pressure": 101.3,
    "last_update": "2025-11-30T10:30:45.123456"
  }
}
```

### 2. Watering Update
Sent when watering status changes.

```json
{
  "type": "watering_update",
  "plant_id": "plant1",
  "data": {
    "active": true,
    "status": "watering",
    "last_update": "2025-11-30T10:30:45.123456-06:00"
  }
}
```

### 3. Tank Update
Sent when water tank status changes.

```json
{
  "type": "tank_update",
  "plant_id": "plant1",
  "data": {
    "has_water": true,
    "status": "available",
    "last_update": "2025-11-30T10:30:45.123456-06:00"
  }
}
```

## Usage Examples

### JavaScript (Browser)

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/sensors/ws/plant1');

// Connection opened
ws.onopen = () => {
  console.log('Connected to Smart Garden');
};

// Receive messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch(message.type) {
    case 'sensor_update':
      console.log('Temperature:', message.data.temperature);
      console.log('Humidity:', message.data.humidity);
      console.log('Soil Moisture:', message.data.soil_moisture);
      break;

    case 'watering_update':
      console.log('Watering active:', message.data.active);
      break;

    case 'tank_update':
      console.log('Tank has water:', message.data.has_water);
      break;
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Connection closed
ws.onclose = () => {
  console.log('Disconnected from Smart Garden');
};

// Send ping (keep-alive)
ws.send('ping');
```

### React Hook Example

```javascript
import { useEffect, useState } from 'react';

function useSensorWebSocket(plantId) {
  const [sensorData, setSensorData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/sensors/ws/${plantId}`);

    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sensor_update') {
        setSensorData(message.data);
      }
    };

    ws.onclose = () => setIsConnected(false);

    // Cleanup on unmount
    return () => ws.close();
  }, [plantId]);

  return { sensorData, isConnected };
}

// Usage in component
function PlantDashboard() {
  const { sensorData, isConnected } = useSensorWebSocket('plant1');

  return (
    <div>
      <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      {sensorData && (
        <>
          <p>Temperature: {sensorData.temperature}°C</p>
          <p>Humidity: {sensorData.humidity}%</p>
          <p>Soil Moisture: {sensorData.soil_moisture}%</p>
        </>
      )}
    </div>
  );
}
```

### Python Example

```python
import asyncio
import websockets
import json

async def connect_to_garden():
    uri = "ws://localhost:8000/api/sensors/ws/plant1"

    async with websockets.connect(uri) as websocket:
        print("Connected to Smart Garden")

        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'sensor_update':
                sensor_data = data['data']
                print(f"Temperature: {sensor_data['temperature']}°C")
                print(f"Humidity: {sensor_data['humidity']}%")
                print(f"Soil: {sensor_data['soil_moisture']}%")

# Run
asyncio.run(connect_to_garden())
```

### Node.js Example

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/api/sensors/ws/plant1');

ws.on('open', () => {
  console.log('Connected to Smart Garden');
});

ws.on('message', (data) => {
  const message = JSON.parse(data);
  console.log('Received:', message);
});

ws.on('close', () => {
  console.log('Disconnected');
});
```

## Testing

### 1. Using the Test Page

Open the provided `websocket_test.html` file in your browser:

```bash
open websocket_test.html
```

Or serve it with Python:
```bash
python -m http.server 8080
# Then open http://localhost:8080/websocket_test.html
```

### 2. Using Browser Console

```javascript
const ws = new WebSocket('ws://localhost:8000/api/sensors/ws/plant1');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

### 3. Using wscat (CLI tool)

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c ws://localhost:8000/api/sensors/ws/plant1
```

## HTTP Endpoints (Still Available)

All original HTTP endpoints remain functional:

- `GET /api/sensors/soil?plant_id=plant1` - Soil moisture history
- `GET /api/sensors/temperature?plant_id=plant1` - Temperature history
- `GET /api/sensors/humidity?plant_id=plant1` - Humidity history
- `GET /api/sensors/pressure?plant_id=plant1` - Pressure history
- `GET /api/sensors/light?plant_id=plant1` - Light level history
- `GET /api/sensors/tank/status?plant_id=plant1` - Water tank status

Use HTTP for:
- Historical data queries
- One-time data fetches
- Initial page loads

Use WebSocket for:
- Real-time monitoring
- Live dashboards
- Instant notifications

## Architecture

```
ESP32 → MQTT → FastAPI → WebSocket → Frontend
                    ↓
                Database (PostgreSQL)
```

1. ESP32 publishes sensor data to MQTT broker
2. FastAPI MQTT handler receives the data
3. Data is saved to PostgreSQL database
4. Data is broadcast to all WebSocket clients subscribed to that plant
5. Frontend receives instant updates

## Best Practices

1. **Reconnection Logic**: Implement automatic reconnection in case of network issues
   ```javascript
   function connectWithRetry() {
     const ws = new WebSocket(url);
     ws.onclose = () => {
       setTimeout(connectWithRetry, 3000); // Retry after 3 seconds
     };
   }
   ```

2. **Ping/Pong**: Keep connection alive
   ```javascript
   setInterval(() => {
     if (ws.readyState === WebSocket.OPEN) {
       ws.send('ping');
     }
   }, 30000); // Every 30 seconds
   ```

3. **Multiple Plants**: Open separate connections for different plants
   ```javascript
   const wsPlant1 = new WebSocket('ws://localhost:8000/api/sensors/ws/plant1');
   const wsPlant2 = new WebSocket('ws://localhost:8000/api/sensors/ws/plant2');
   ```

4. **Clean Disconnection**: Always close connections when done
   ```javascript
   window.addEventListener('beforeunload', () => {
     ws.close();
   });
   ```

## Troubleshooting

**Connection refused:**
- Ensure the API is running: `uvicorn app.main:app --reload`
- Check the correct port (default: 8000)

**No messages received:**
- Verify MQTT is connected and publishing data
- Check plant_id matches your ESP32 configuration
- Look at API console logs for MQTT messages

**Connection drops:**
- Implement reconnection logic
- Check network stability
- Use ping/pong keep-alive

## Production Considerations

For production deployments:

1. **Use WSS (Secure WebSocket)**:
   ```javascript
   const ws = new WebSocket('wss://yourdomain.com/api/sensors/ws/plant1');
   ```

2. **Reverse Proxy (Nginx)**:
   ```nginx
   location /api/sensors/ws/ {
       proxy_pass http://localhost:8000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;
   }
   ```

3. **Load Balancing**: Use sticky sessions for WebSocket connections

4. **Monitoring**: Track active connections and message throughput
