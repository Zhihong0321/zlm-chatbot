#!/bin/bash
# Switch to Local Development Mode

echo "🏠 Switching to LOCAL DEVELOPMENT mode..."

# Copy local environment config
cp .env.local .env

# Start PostgreSQL if not running
if ! docker ps | grep -q "oneapi-postgres"; then
    echo "🚀 Starting PostgreSQL container..."
    docker-compose up -d postgres
    echo "⏳ Waiting for database to be ready..."
    sleep 5
fi

# Test database connection
echo "🔍 Testing database connection..."
python test_local_db.py

if [ $? -eq 0 ]; then
    echo "✅ Local development setup complete!"
    echo ""
    echo "🚀 Start the application with:"
    echo "   cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
else
    echo "❌ Database setup failed. Check the logs above."
fi
