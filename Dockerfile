# ------------------------------
# Base image
# ------------------------------
    FROM python:3.11-slim AS base

    # Set working directory
    WORKDIR /app
    
    # Disable Python’s output buffering
    ENV PYTHONUNBUFFERED=1
    
    # ------------------------------
    # Install system deps & Poetry
    # ------------------------------
    RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
      && pip install --no-cache-dir poetry \
      && rm -rf /var/lib/apt/lists/*
    
    # ------------------------------
    # Copy dependency files first
    # ------------------------------
    COPY pyproject.toml poetry.lock* /app/
    
    # Install only project dependencies (no dev deps)
    RUN poetry install --no-root --no-interaction --no-ansi
    
    # ------------------------------
    # Copy application source
    # ------------------------------
    COPY . /app
    
    # Expose API port
    EXPOSE 8000
    
    # ------------------------------
    # Run API (no reload for Docker)
    # ------------------------------
    CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    