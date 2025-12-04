# Multi-stage build for Frontend + Backend

# Stage 1: Build Frontend
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Explicitly unset VITE_API_BASE_URL during build to force relative paths
RUN VITE_API_BASE_URL="" npm run build

# Stage 2: Build Backend
FROM python:3.11-slim as backend-builder
WORKDIR /app
# Install system dependencies for psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY app.py .
COPY railway_schema_fix.py .

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Run schema fix if needed (only once)
RUN python railway_schema_fix.py || echo "Schema fix completed or not needed"

# FAST STARTUP - No slow health checks in Dockerfile
CMD sh -c "cd backend && echo 'Starting app...' && \
    cd .. && python app.py"
