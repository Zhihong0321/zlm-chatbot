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

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Start command - Enhanced with robust migration handling
CMD sh -c "cd backend && echo 'Starting MCP database setup...' && \
    echo 'DATABASE_URL: $DATABASE_URL' && \
    echo 'Running Alembic migrations...' && \
    alembic upgrade head && \
    echo 'Migration completed, checking MCP schema...' && \
    cd .. && echo 'Starting application...' && \
    python app.py"
