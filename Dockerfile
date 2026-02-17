# NovaOS V2 Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional dependencies for platform integrations
RUN pip install --no-cache-dir \
    stripe \
    sendgrid \
    tweepy \
    beautifulsoup4 \
    requests \
    psutil

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NOVAOS_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from workers.manager import get_worker_manager; print('healthy')" || exit 1

# Default command
CMD ["python", "-m", "cli", "workers", "start"]
