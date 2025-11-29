#!/bin/bash

# Milestone 6: Full Deployment & Integration Testing
# This script deploys both backend and frontend to Railway and runs integration tests

echo "🚀 Starting Milestone 6 Deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run 'railway login' first."
    exit 1
fi

echo "✅ Railway CLI authenticated"

# Deploy backend first
echo "📦 Deploying backend to Railway..."
cd backend

# Set up environment variables for Railway
echo "🔧 Setting up environment variables..."
railway variables set ZAI_API_KEY=$ZAI_API_KEY
railway variables set DATABASE_URL=$DATABASE_URL

# Deploy backend
echo "🚢 Deploying backend service..."
railway up

# Get backend URL
BACKEND_URL=$(railway domain)
echo "✅ Backend deployed to: $BACKEND_URL"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 30

# Test backend health
echo "🏥 Testing backend health..."
curl -f "$BACKEND_URL/api/v1/ui/health" || {
    echo "❌ Backend health check failed"
    exit 1
}

cd ../frontend

# Update frontend environment to use Railway backend
echo "🔧 Updating frontend configuration..."
cat > .env.production << EOF
VITE_API_BASE_URL=$BACKEND_URL
EOF

# Deploy frontend
echo "🚢 Deploying frontend service..."
railway up

# Get frontend URL
FRONTEND_URL=$(railway domain)
echo "✅ Frontend deployed to: $FRONTEND_URL"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
sleep 30

# Test frontend health
echo "🏥 Testing frontend health..."
curl -f "$FRONTEND_URL" || {
    echo "❌ Frontend health check failed"
    exit 1
}

echo "🧪 Running integration tests..."

# Test API endpoints
echo "📋 Testing API endpoints..."

# Create a test session
SESSION_ID=$(curl -s -X POST "$BACKEND_URL/api/v1/sessions" \
    -H "Content-Type: application/json" \
    -d '{"title": "Milestone 6 Test Session"}' | \
    grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SESSION_ID" ]; then
    echo "❌ Failed to create test session"
    exit 1
fi

echo "✅ Test session created: $SESSION_ID"

# Send a test message
curl -s -X POST "$BACKEND_URL/api/v1/sessions/$SESSION_ID/messages" \
    -H "Content-Type: application/json" \
    -d '{"content": "Hello, this is a test message for Milestone 6"}' > /dev/null

echo "✅ Test message sent"

# Verify session history
HISTORY_CHECK=$(curl -s "$BACKEND_URL/api/v1/sessions/$SESSION_ID/history" | grep -o "Hello, this is a test message")
if [ -z "$HISTORY_CHECK" ]; then
    echo "❌ Failed to retrieve session history"
    exit 1
fi

echo "✅ Session history verified"

# Test agent creation
AGENT_ID=$(curl -s -X POST "$BACKEND_URL/api/v1/agents" \
    -H "Content-Type: application/json" \
    -d '{"name": "Milestone 6 Test Agent", "model": "glm-4.5", "system_prompt": "You are a helpful assistant for testing."}' | \
    grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$AGENT_ID" ]; then
    echo "❌ Failed to create test agent"
    exit 1
fi

echo "✅ Test agent created: $AGENT_ID"

# Clean up test data
echo "🧹 Cleaning up test data..."
curl -s -X DELETE "$BACKEND_URL/api/v1/sessions/$SESSION_ID" > /dev/null
curl -s -X DELETE "$BACKEND_URL/api/v1/agents/$AGENT_ID" > /dev/null

echo "✅ Integration tests completed successfully!"

# Display deployment summary
echo ""
echo "🎉 Milestone 6 Deployment Complete!"
echo "==================================="
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "API Documentation: $BACKEND_URL/docs"
echo "Health Check: $BACKEND_URL/api/v1/ui/health"
echo ""
echo "✅ All integration tests passed!"
echo "✅ Ready to proceed to Milestone 7: Polish & Optimization"