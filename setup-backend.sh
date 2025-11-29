#!/bin/bash

echo "Setting up Chatbot API Server development environment..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your actual configuration before running the server."
    echo "   - Set ZAI_API_KEY to your Z.ai API key"
    echo "   - Set DATABASE_URL to your PostgreSQL connection string"
else
    echo ".env file already exists"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create backend directory structure if it doesn't exist
echo "Setting up backend structure..."
mkdir -p backend/app/models backend/app/api backend/app/core backend/app/crud backend/app/schemas backend/app/db

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your actual ZAI_API_KEY and DATABASE_URL"
echo "2. Set up PostgreSQL database"
echo "3. Run the server: cd backend && python main.py"
echo "4. Open http://localhost:8000/docs to see API documentation"
echo ""
echo "For Railway deployment:"
echo "1. Connect your GitHub repository to Railway"
echo "2. Set environment variables in Railway dashboard"
echo "3. Deploy automatically"