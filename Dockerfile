# Anti-Gravity Backend Dockerfile
FROM python:3.11-slim

LABEL maintainer="Anti-Gravity Development Team"
LABEL description="Backend API server for Anti-Gravity astrology system"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Swiss Ephemeris requirements
    build-essential \
    # PDF generation fonts
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-liberation \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY anti_gravity_master_content.json ./
COPY swe_data/ ./swe_data/

# Create output directory for PDFs
RUN mkdir -p /app/output && chmod 777 /app/output

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
