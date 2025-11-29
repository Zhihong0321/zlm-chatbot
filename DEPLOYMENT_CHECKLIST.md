# Milestone 6 Deployment Checklist

## Pre-Deployment Checklist

### Prerequisites
- [ ] Railway CLI installed: `npm install -g @railway/cli`
- [ ] Logged into Railway: `railway login`
- [ ] Z.ai API key obtained from https://z.ai/manage-apikey/apikey-list
- [ ] Repository pushed to Git (optional but recommended)

### Environment Variables
- [ ] `ZAI_API_KEY` set in environment
- [ ] `DATABASE_URL` configured (or let Railway create it)

### Project Structure Verification
- [ ] Backend has `railway.json` configuration
- [ ] Frontend has `railway.json` configuration
- [ ] Backend has `requirements.txt`
- [ ] Frontend has `package.json` with build scripts
- [ ] Both have valid Dockerfiles

## Deployment Process

### Backend Deployment
- [ ] Navigate to backend directory
- [ ] Initialize Railway project: `railway init`
- [ ] Set environment variables: `railway variables set ZAI_API_KEY=$ZAI_API_KEY`
- [ ] Deploy: `railway up`
- [ ] Note the backend URL
- [ ] Verify health endpoint: `curl https://backend-url/api/v1/ui/health`

### Frontend Deployment
- [ ] Navigate to frontend directory
- [ ] Initialize Railway project: `railway init`
- [ ] Configure backend URL in environment
- [ ] Deploy: `railway up`
- [ ] Note the frontend URL
- [ ] Verify frontend loads in browser

## Post-Deployment Testing

### Basic Functionality Tests
- [ ] Frontend loads without errors
- [ ] Can create new chat session
- [ ] Can send message and receive response
- [ ] Can view message history
- [ ] Can switch between agents
- [ ] Can create custom agent

### Integration Tests
- [ ] API endpoints accessible from frontend
- [ ] File upload works correctly
- [ ] Session management functions
- [ ] Search functionality works
- [ ] Export functionality works

### Error Handling Tests
- [ ] Network errors handled gracefully
- [ ] Invalid API responses handled
- [ ] Large file uploads rejected appropriately
- [ ] Concurrent sessions managed correctly

### Performance Tests
- [ ] Initial load time < 3 seconds
- [ ] Message response time < 10 seconds
- [ ] Dashboard loads efficiently
- [ ] Search results appear quickly

## Production Verification

### Security
- [ ] API keys not exposed in frontend
- [ ] CORS properly configured
- [ ] Input validation active
- [ ] Rate limiting working (if implemented)

### Monitoring
- [ ] Application monitoring configured
- [ ] Error tracking implemented
- [ ] Log access working
- [ ] Health checks passing

### Documentation
- [ ] API documentation updated with live URLs
- [ ] User guide created
- [ ] Deployment instructions documented
- [ ] Troubleshooting guide available

## Success Criteria

### Milestone 6 is Complete When:
- [ ] Both services deployed successfully
- [ ] All core features working in production
- [ ] Integration tests passing
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Security validation passed

## Troubleshooting

### Common Issues
1. **Build Failures**: Check requirements.txt and package.json for valid dependencies
2. **Connection Errors**: Verify CORS and API endpoint configuration
3. **Database Issues**: Check DATABASE_URL format and PostgreSQL service
4. **API Key Issues**: Verify ZAI_API_KEY is valid and active

### Resources
- [Railway Documentation](https://docs.railway.app)
- [Project Status](MILESTONE_6_STATUS.md)
- [Deployment Guide](MILESTONE_6_README.md)

## Next Steps

After successful deployment:
1. Collect user feedback
2. Monitor performance metrics
3. Identify optimization opportunities
4. Prepare for Milestone 7: Polish & Optimization

Remember to update the status in MILESTONE_6_STATUS.md as you complete each step!