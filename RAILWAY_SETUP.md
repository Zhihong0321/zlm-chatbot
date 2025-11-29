# Railway Setup Instructions for ZLM Chatbot

## 🚀 Railway Setup Steps

### 1. Create Railway Project
1. Go to https://railway.app and login/create account
2. Click "New Project" 
3. Choose "Deploy from GitHub repo" and connect your repository

### 2. Configure PostgreSQL Database
1. In your Railway project, click "+" to add a service
2. Select "PostgreSQL" 
3. Name it something like "chatbot-db"
4. Railway will create the database with connection variables

### 3. Configure Backend API Service
1. Click "+" to add another service
2. Select your GitHub repository (should auto-detect Python FastAPI)
3. Set service name like "chatbot-api"

### 4. Set Environment Variables
In your backend service, go to "Settings" → "Variables" and add:

**Required:**
```
ZAI_API_KEY=your_zai_api_key_here
DATABASE_URL=postgresql://railway:railway@chatbot-db.railway.app:5432/railway
ENVIRONMENT=production
```

**How to get DATABASE_URL:**
- Go to your PostgreSQL service
- Click "Connect" tab
- Copy the "DATABASE_URL" connection string

**How to get ZAI_API_KEY:**
- Go to https://z.ai/manage-apikey/apikey-list
- Copy your API key (format: xxxxxxxx.xxxxxxxx)

### 5. Configure Health Check
In backend service settings:
- Healthcheck Path: `/api/v1/ui/health`
- Healthcheck Timeout: 300 seconds
- Restart Policy: ON_FAILURE
- Max Retries: 10

### 6. Deploy & Test
1. Click "Deploy" for the backend service
2. Railway will build and deploy
3. Monitor deployment logs - should show "✅ Production database ready"
4. Once deployed, test health endpoint: `https://your-app-name.railway.app/api/v1/ui/health`

### 7. Update Frontend API URL
In your frontend service/app, update the API URL to:
```javascript
const API_BASE_URL = 'https://your-backend-app-name.railway.app';
```

## 🔍 Verification Steps

1. **Database Health**: Visit `/api/v1/ui/health` - should show "healthy"
2. **API Test**: Try `GET /api/v1/agents/` - should return 3 default agents
3. **Chat Test**: Try `POST /api/v1/chat/chat` - should work with real Z.ai API

## 📊 Production Features Enabled

- ✅ PostgreSQL database with automatic migrations
- ✅ Health check with PostgreSQL status
- ✅ Automatic retries on failure
- ✅ Production database initialization
- ✅ Environment-specific configuration
- ✅ Comprehensive error handling

## 🚨 Common Issues & Fixes

**Database Connection Failed:**
- Verify DATABASE_URL matches Railway PostgreSQL service
- Check PostgreSQL service is running
- Ensure correct credentials

**ZAI_API_KEY Error:**
- Verify key format: `hash.keyhash`
- Test key locally first using test_connection.py

**Build Failures:**
- Check Railway build logs
- Ensure all requirements.txt dependencies are production-ready

**Health Check Failures:**
- Check service logs at `/logs`
- Verify all environment variables are set
- Test each endpoint manually

## 📈 Monitoring

Your Railway dashboard shows:
- Real-time logs
- Metrics usage
- Error rates
- Database connections
- Response times

The health check endpoint `/api/v1/ui/health` provides detailed status for monitoring.