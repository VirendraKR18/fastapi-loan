FROM python:3.11-slim

# Install tesseract OCR (system dependency for pytesseract)
RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

# Copy application code
COPY . .

# Render injects PORT env var
ENV DEPLOYMENT_MODE=render

EXPOSE 8001

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}
