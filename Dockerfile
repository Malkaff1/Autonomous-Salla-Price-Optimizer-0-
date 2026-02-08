# Multi-stage build for Salla Price Optimizer SaaS
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements_saas.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_saas.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/store-data /app/logs /app/ai-agent-output

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 8000 8501 5555

# Default command (will be overridden by docker-compose)
CMD ["uvicorn", "api.oauth_handler:app", "--host", "0.0.0.0", "--port", "8000"]
