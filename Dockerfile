# Multi-stage build for Salla Price Optimizer SaaS
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    redis-tools \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements_saas.txt .

# Upgrade pip tools in separate layer for better caching
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies with legacy resolver for complex AI dependencies
# The legacy resolver is more successful at resolving complex AI library chains
RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements_saas.txt || \
    (echo "First attempt failed, trying with backtracking resolver..." && \
     pip install --no-cache-dir -r requirements_saas.txt) && \
    pip list

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/store-data /app/logs /app/ai-agent-output && \
    chmod -R 755 /app/store-data /app/logs /app/ai-agent-output

# Convert entrypoint.sh to Unix line endings and make executable
RUN if [ -f /app/scripts/entrypoint.sh ]; then \
        sed -i 's/\r$//' /app/scripts/entrypoint.sh && \
        chmod +x /app/scripts/entrypoint.sh; \
    fi

# Expose ports
EXPOSE 8000 8501 5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (will be overridden by docker-compose)
CMD ["uvicorn", "api.oauth_handler:app", "--host", "0.0.0.0", "--port", "8000"]
