#!/bin/bash

# Create Railway deployment guide

echo "Creating Railway deployment documentation..."

# Create deployment documentation
cat > RAILWAY_DEPLOYMENT.md << 'EOF'
# Railway Deployment Guide

## 1. Preparation

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository with the backend code
- Z.ai API key

### Repository Structure
Ensure your repository has this structure:
```
your-repo/
├── backend/
│   ├── Dockerfile
│   ├── railway.json
│   ├── build-railway.sh
│   ├── requirements.txt
│   ├── run.py
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── db/
│       └── schemas/
└── .gitignore
```

## 2. Railway Setup

### Step 1: Connect Repository
1. Log into Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Set root directory to `backend`

### Step 2: Add PostgreSQL Database
1. In your project dashboard, click "Add Service"
2. Select "PostgreSQL"
3. Railway will automatically provision a database
4. Click on the database service to see connection details

### Step 3: Configure Environment Variables
In your Railway project settings, add these environment variables:

```env
ZAI_API_KEY=your_zai_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend-domain.railway.app"]
```

**Important:**
- `DATABASE_URL` will be automatically set when you add PostgreSQL service
- `ZAI_API_KEY` must be your actual Z.ai API key
- `CORS_ORIGINS` should include your frontend domain

### Step 4: Deploy
1. Railway will automatically detect changes and deploy
2. Monitor the build logs for any errors
3. Once deployed, Railway will provide a public URL

## 3. Verification

### Health Check
Test the health endpoint:
```bash
curl https://your-app-url.railway.app/api/v1/ui/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "version": "1.0.0"
}
```

### API Documentation
Access Swagger UI at:
`https://your-app-url.railway.app/docs`

### Test API Endpoints
```bash
# Create an agent
curl -X POST "https://your-app-url.railway.app/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "description": "Test description",
    "system_prompt": "You are a helpful assistant.",
    "model": "glm-4.5",
    "temperature": 0.7
  }'

# Create a session
curl -X POST "https://your-app-url.railway.app/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Session",
    "agent_id": 1
  }'
```

## 4. Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check that `DATABASE_URL` is correctly set
   - Verify PostgreSQL service is running
   - Check Railway logs for connection errors

2. **Build Failures**
   - Review build logs for dependency errors
   - Ensure `requirements.txt` is valid
   - Check Dockerfile syntax

3. **API Key Errors**
   - Verify `ZAI_API_KEY` is set correctly
   - Check Z.ai API key is valid and has sufficient balance

4. **CORS Issues**
   - Ensure frontend domain is in `CORS_ORIGINS`
   - Check that CORS headers are properly configured

### Checking Logs
1. Go to Railway dashboard
2. Select your service
3. Click on the "Logs" tab
4. Look for error messages and stack traces

### Restarting Service
1. In Railway dashboard
2. Click on your service
3. Click "Restart" or push new commits to trigger redeploy

## 5. Monitoring

### Health Monitoring
Railway automatically monitors the `/api/v1/ui/health` endpoint
- Service restarts automatically on failures
- Health checks every 30 seconds

### Performance Monitoring
Monitor response times and resource usage in Railway dashboard
- Memory usage
- CPU usage
- Network traffic
- Response times

## 6. Scaling

Railway supports automatic scaling:
- Free tier: Basic scaling
- Pro tier: Advanced scaling with custom rules

## 7. Custom Domain (Optional)

1. In Railway project settings
2. Click "Settings" tab
3. Under "Domains", click "Add Domain"
4. Enter your custom domain
5. Configure DNS records as instructed by Railway

## 8. Production Best Practices

### Security
- Use HTTPS (Railway provides automatically)
- Keep API keys secret (use environment variables)
- Monitor logs for suspicious activity

### Performance
- Enable Railway's built-in caching if needed
- Monitor resource usage
- Optimize database queries

### Backup
- Railway automatically backs up PostgreSQL
- Export data regularly for extra safety
- Document your API responses

## Success Criteria

Your deployment is successful when:
- [ ] All health checks pass
- [ ] API endpoints respond correctly
- [ ] Database operations work
- [ ] Z.ai API integration functions
- [ ] Logs show no critical errors
- [ ] Frontend can connect to backend (if applicable)

Congratulations! Your Chatbot API is now running on Railway! 🎉
EOF

echo "Railway deployment guide created successfully!"
echo "File: RAILWAY_DEPLOYMENT.md"