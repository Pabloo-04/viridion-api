# -------------------------------------------------------
# BASE
# -------------------------------------------------------
  FROM python:3.11-slim

  WORKDIR /app
  ENV POETRY_VIRTUALENVS_CREATE=false \
      PYTHONUNBUFFERED=1
  
  # System deps for Postgres + compiling libs
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev gcc \
      && pip install --no-cache-dir poetry \
      && rm -rf /var/lib/apt/lists/*
  
  # -------------------------------------------------------
  # Install dependencies FIRST so cache works properly
  # -------------------------------------------------------
  COPY pyproject.toml poetry.lock* ./
  RUN poetry install --no-interaction --no-ansi --no-root
  
  # -------------------------------------------------------
  # Copy actual source AFTER deps installed
  # -------------------------------------------------------
  COPY . .
  
  EXPOSE 8000
  CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  