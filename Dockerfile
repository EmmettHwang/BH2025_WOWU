# Multi-stage build for FastAPI backend + Static frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .env .env

# Create thumbnails directory
RUN mkdir -p /app/backend/thumbnails

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Start backend (serves both API and static files)
CMD cd /app/backend && uvicorn main:app --host 0.0.0.0 --port $PORT
