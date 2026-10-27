# Multi-stage build for AI Safety Monitoring System

FROM python:3.12.0-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

WORKDIR /app

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.getenv('PORT', '5000') + '/health')"

# Expose the Cloud Run default port (local Docker Compose can override PORT).
EXPOSE 8080

# Run one worker to avoid starting multiple copies of the camera/monitoring services.
CMD ["sh", "-c", "gunicorn -w 1 -b 0.0.0.0:${PORT:-5000} --timeout 120 'backend.main:create_app(\"production\")'"]

# Development stage
FROM base as development

WORKDIR /app

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    ipython

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run in development mode
CMD ["python", "main.py"]
