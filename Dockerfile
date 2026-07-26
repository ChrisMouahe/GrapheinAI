# Multi-Stage Production Dockerfile for GrapheinAI
# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies into wheels directory
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime Production Image
FROM python:3.12-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

WORKDIR /app

# Install runtime system libraries required by OpenCV and ReportLab
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root production user & required directories
RUN useradd -m -u 1000 graphein && \
    mkdir -p /app/data/raw /app/data/reports /app/logs /app/backups && \
    chown -R graphein:graphein /app

# Copy application source code
COPY --chown=graphein:graphein . /app

USER graphein

EXPOSE 8088 8501

# Production Container Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8088/api/health || exit 1

ENTRYPOINT ["uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", "8088"]
