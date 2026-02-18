FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}

# Run PDF ingestion
RUN python -m scripts.ingest_pdf || echo "PDF ingestion skipped - will use sample data"

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
