# Viridion  API

IoT API for smart garden monitoring and control.

## Features

- 📊 Real-time sensor data collection (temperature, humidity, soil moisture)
- 💧 Automated watering control
- 🤖 ML-powered watering predictions
- 📈 Historical data analysis


## Setup

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Setup Database
```bash
# Start PostgreSQL with TimescaleDB (Docker)
docker run -d --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=yourpassword \
  timescale/timescaledb:latest-pg16
```

### 4. Run the API
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Sensors
- `POST /api/sensors/readings` - Store sensor reading
- `GET /api/sensors/current` - Get current readings
- `GET /api/sensors/history` - Get historical data
- `GET /api/sensors/analytics` - Get analytics

### Watering
- `POST /api/watering/toggle` - Toggle watering on/off
- `GET /api/watering/status` - Get watering status
- `POST /api/watering/schedule` - Update schedule
- `GET /api/watering/history` - Get watering history

### ML Predictions
- `POST /api/predictions/watering` - Get watering prediction
- `GET /api/predictions/history` - Get prediction history

## Development
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black app/

# Lint
ruff check app/
```

## License

MIT