# Railway Environment Variables

# The Railway deployment will automatically set these environment variables:
# - DATABASE_URL (from Railway PostgreSQL service)
# - PORT (Railway-provided port)

# Manual configuration needed in Railway dashboard:
ZAI_API_KEY=your_zai_api_key_here

# Database URL will be automatically provided by Railway:
DATABASE_URL=${RAILWAY_POSTGRES_URL}

# Application will run on Railway-provided port
