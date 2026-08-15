FROM python:3.13-slim

WORKDIR /app

# Install system dependencies with retry logic
RUN apt-get update || apt-get update || apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    ffmpeg \
    libsm6 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/* || true

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application
COPY . .

# Create data and logs directories
RUN mkdir -p data logs

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
