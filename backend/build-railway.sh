#!/bin/bash

# Railway deployment script for Chatbot API Server

echo "Starting Railway deployment..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not set"
    exit 1
fi

# Check if ZAI_API_KEY is set
if [ -z "$ZAI_API_KEY" ]; then
    echo "ERROR: ZAI_API_KEY environment variable not set"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run database migrations
echo "Setting up database..."
python -c "
import os
import sys
sys.path.append('.')
from app.db.database import engine
from app.models import models

# Test database connection
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)

# Create tables
models.Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

echo "Starting server..."

# Use PORT from Railway (defaults to 8000)
PORT=${PORT:-8000}

# Start the server
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT