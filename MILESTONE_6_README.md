# Milestone 6: Full Deployment & Integration Testing Guide

## Overview

This guide covers the complete deployment of the Chatbot API Server to Railway and integration testing to ensure all components work together seamlessly in production.

## Prerequisites

### 1. Install Required Tools
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Verify login
railway whoami
```

### 2. Prepare Environment Variables
You'll need the following environment variables:
- `ZAI_API_KEY` - Your Z.ai API key (get from https://z.ai/manage-apikey/apikey-list)
- `DATABASE_URL` - PostgreSQL connection string (Railway will provide this)

### 3. Project Structure Check
Ensure your project has the following structure:
```
oneapi/
├── backend/
│   ├── railway.json
│   ├── Dockerfile
│   └── build-railway.sh
├── frontend/
│   ├── railway.json
│   └── Dockerfile
├── deploy-milestone-6.sh
└── MILESTONE_6_STATUS.md
```

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

1. **Set Environment Variables**
   ```bash
   export ZAI_API_KEY="your_zai_api_key_here"
   export DATABASE_URL="postgresql://user:password@host:port/database"
   ```

2. **Run Deployment Script**
   ```bash
   chmod +x deploy-milestone-6.sh
   ./deploy-milestone-6.sh
   ```

The script will:
- Deploy backend to Railway
- Deploy frontend to Railway
- Run integration tests
- Clean up test data
- Provide deployment URLs

### Option 2: Manual Deployment

#### Deploy Backend

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Initialize Railway Project**
   ```bash
   railway init
   ```

3. **Set Environment Variables**
   ```bash
   railway variables set ZAI_API_KEY=$ZAI_API_KEY
   railway variables set DATABASE_URL=$DATABASE_URL
   ```

4. **Deploy Backend**
   ```bash
   railway up
   ```

5. **Get Backend URL**
   ```bash
   railway domain
   ```

#### Deploy Frontend

1. **Navigate to Frontend Directory**
   ```bash
   cd ../frontend
   ```

2. **Initialize Railway Project**
   ```bash
   railway init
   ```

3. **Configure Frontend Environment**
   Create `.env.production`:
   ```
   VITE_API_BASE_URL=https://your-backend-url.railway.app
   ```

4. **Deploy Frontend**
   ```bash
   railway up
   ```

5. **Get Frontend URL**
   ```bash
   railway domain
   ```

## Integration Testing

### Automated Testing (via deploy script)
The deployment script includes automated tests that verify:
- Backend health endpoint
- Frontend accessibility
- Session creation and management
- Message sending and history retrieval
- Agent creation and management

### Manual Testing Checklist

#### 1. Basic Connectivity
- [ ] Backend health check: `https://backend-url/api/v1/ui/health`
- [ ] Frontend loads: `https://frontend-url`
- [ ] API docs accessible: `https://backend-url/docs`

#### 2. Core Functionality
- [ ] Create new chat session
- [ ] Send message and receive response
- [ ] View message history
- [ ] Switch agents during conversation
- [ ] Upload knowledge file
- [ ] Create custom agent

#### 3. Session Management
- [ ] View all sessions in dashboard
- [ ] Search through conversations
- [ ] Filter sessions by date/agent
- [ ] Delete single session
- [ ] Export session data

#### 4. Error Handling
- [ ] Invalid API key handling
- [ ] Network error recovery
- [ ] Invalid file upload rejection
- [ ] Large message handling
- [ ] Concurrent session management

#### 5. Performance
- [ ] Initial load time under 3 seconds
- [ ] Message responses under 10 seconds
- [ ] Dashboard loads efficiently
- [ ] Search results appear quickly
- [ ] File uploads complete promptly

## Monitoring & Debugging

### Railway Dashboard
1. Visit [Railway Dashboard](https://railway.app)
2. Select your project
3. Monitor:
   - Build logs
   - Runtime logs
   - Environment variables
   - Metrics

### Health Endpoints
- Backend: `/api/v1/ui/health`
- Returns application status and connectivity

### Log Locations
- Backend logs: Railway dashboard → Backend service → Logs
- Frontend logs: Railway dashboard → Frontend service → Logs
- Build logs: Railway dashboard → Deployments → View logs

## Troubleshooting

### Common Issues

#### 1. Backend Deployment Fails
**Symptoms:** Build errors, deployment failures
**Solutions:**
- Check `requirements.txt` for valid dependencies
- Verify `Dockerfile` syntax
- Review build logs in Railway dashboard
- Ensure `railway.json` configuration is valid

#### 2. Frontend Cannot Connect to Backend
**Symptoms:** API errors, connection refused
**Solutions:**
- Verify `VITE_API_BASE_URL` in frontend environment
- Check CORS configuration in backend
- Ensure backend is running and accessible
- Verify API endpoints are correct

#### 3. Database Connection Issues
**Symptoms:** Database errors, connection timeouts
**Solutions:**
- Verify `DATABASE_URL` format and credentials
- Check PostgreSQL service status in Railway
- Ensure database migrations have run
- Test connection manually

#### 4. Z.ai API Integration Fails
**Symptoms:** Model errors, API key issues
**Solutions:**
- Verify `ZAI_API_KEY` is valid and active
- Check Z.ai account balance
- Test API key with `test_connection.py`
- Verify model availability

### Debug Commands

#### Backend
```bash
# Check backend health
curl https://your-backend.railway.app/api/v1/ui/health

# Test API directly
curl -X POST https://your-backend.railway.app/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Session"}'
```

#### Frontend
```bash
# Check frontend build
npm run build

# Test frontend locally with production backend
npm run dev -- --host
```

## Production Considerations

### Security
- [ ] API keys stored in Railway environment variables
- [ ] CORS properly configured for production domain
- [ ] Input validation active
- [ ] Rate limiting configured

### Performance
- [ ] Database connection pooling enabled
- [ ] Caching implemented where appropriate
- [ ] Frontend assets optimized
- [ ] CDN usage for static assets

### Backup
- [ ] Database backup strategy in place
- [ ] Configuration documented
- [ ] Recovery procedures tested

## Next Steps

After successful deployment and testing:

1. **Update Documentation**
   - API documentation with live examples
   - User guide for the deployed application
   - Deployment troubleshooting guide

2. **Monitor Performance**
   - Set up alerts for errors
   - Monitor response times
   - Track resource usage

3. **Prepare for Milestone 7**
   - Collect performance metrics
   - Document user feedback
   - Identify optimization opportunities

## Support Resources

- **Railway Documentation**: https://docs.railway.app
- **Z.ai API Documentation**: Available in your Z.ai dashboard
- **Project Status**: Check `MILESTONE_6_STATUS.md` for current progress
- **Troubleshooting**: Review logs in Railway dashboard

## Success Criteria

Milestone 6 is complete when:
- [ ] Both backend and frontend are successfully deployed
- [ ] All integration tests pass
- [ ] Core functionality works in production
- [ ] Monitoring is configured
- [ ] Documentation is updated
- [ ] Security validation passes

Once these criteria are met, you're ready to proceed to **Milestone 7: Polish & Optimization**.