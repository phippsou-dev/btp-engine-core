FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    poppler-utils \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt requirements-service.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-service.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENAI_ENABLED=false
ENV GPT_ENABLED=false
ENV GEMINI_ENABLED=false
ENV VISION_API_ENABLED=false
ENV LOVABLE_GATEWAY_ENABLED=false
ENV DB_WRITES_ENABLED=false
ENV DST_PUSH_ENABLED=false
ENV PROD_ACCESS_ENABLED=false
ENV MAX_COST_USD=0.0

# Run service
CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8080"]