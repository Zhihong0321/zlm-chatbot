# Deployment Mode Switching

This codebase supports easy switching between local development and Railway deployment modes.

## Environment Files

### Local Development Mode
- `.env.local` - Local development configuration
- Uses PostgreSQL on `localhost:5432` 
- Docker Compose: `docker-compose up postgres`

### Railway Deployment Mode  
- `.env` - Railway production configuration
- Uses Railway PostgreSQL automatically
- Environment variables set by Railway

## Quick Switch Instructions

### 1. For Local Development:
```bash
# Step 1: Start local PostgreSQL
docker-compose up -d postgres

# Step 2: Copy local config
cp .env.local .env

# Step 3: Run backend
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Step 4: Run frontend  
cd frontend && npm run dev
```

### 2. For Railway Deployment:
```bash
# Step 1: Copy Railway config  
cp .env.example .env

# Step 2: Push to GitHub (Railway will auto-deploy)
git push origin master

# Step 3: Configure Railway environment variables manually if needed
```

## Environment Configuration

### Key Differences:

**Local Development (.env.local):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/railway
ENVIRONMENT=development
PORT=8000
```

**Railway Production (.env):**
```env
DATABASE_URL=${RAILWAY_POSTGRES_URL}
ENVIRONMENT=production  
PORT=${PORT}
```

## Database Setup Commands

### Local:
```bash
# Test connection and run migrations
python test_local_db.py
```

### Railway:
```bash
# Migrations run automatically in Dockerfile
# Manual: cd backend && alembic upgrade head
```

## Detection in Code

The application detects the deployment mode automatically:

```python
# Backend: app/core/config.py
ENVIRONMENT: str = "production"  # Railway default
# Will be "development" if set in local .env

# Database validation runs in production only
if os.getenv("ENVIRONMENT") == "production":
    validate_production_database()
```

## Files Affecting Deployment Mode

1. **`.env`** - Main environment file (switch this to change modes)
2. **Dockerfile** - Same for both modes (uses environment variables)  
3. **docker-compose.yml** - Local development only
4. **app/core/config.py** - Configuration that adapts to ENVIRONMENT
5. **backend/app/db/database.py** - Database connection logic

## Verification

To verify current mode:

```bash
# Check environment variable
echo $ENVIRONMENT

# Check database connection
python test_local_db.py  # Should work for local mode
```
