# Safe Railway Setup for Existing PostgreSQL Database

## ⚠️  IMPORTANT: EXISTING DATABASE PROTECTION

This setup **preserves all existing data** in your PostgreSQL database.

## 🚀 Railway Setup Steps

### 1. Create Railway Project
1. Go to https://railway.app → New Project → Connect your GitHub repo
2. Click "Add Service" → Select your repository
3. Click "Add Service" → Select PostgreSQL (if not already added)

### 2. Connect to EXISTING PostgreSQL
If you already have a PostgreSQL service with data:
1. Go to your PostgreSQL service in Railway
2. Click "Connect" tab  
3. Copy the DATABASE_URL
4. In your backend service settings → Variables → Add:
   ```
   DATABASE_URL=paste_the_connection_string_here
   ENVIRONMENT=production
   ```

### 3. Set ZAI_API_KEY
In backend service Settings → Variables:
```
ZAI_API_KEY=your_zai_api_key_here
```

### 4. Deploy & Verify
1. Deploy your backend service
2. The safe setup will:
   - ✅ Connect to existing database
   - ✅ Check existing tables and data
   - ✅ Only create missing tables
   - ✅ Only add default agents if agents table is empty
   - ✅ Only add default session if sessions table is empty
   - ✅ **NEVER delete or modify existing data**

3. Check deployment logs - should show:
   ```
   Connected to PostgreSQL: 14.x
   Existing tables: [agents, chat_sessions, ...]
     agents: X records (preserved)
     chat_sessions: Y records (preserved)
     ...
   ✅ Database setup completed - existing data preserved
   ```

## 🔍 Health Check

Visit `https://your-app.railway.app/api/v1/ui/health`

It will show:
- ✅ Database connection OK (with PostgreSQL status)
- ✅ ZAI_API_KEY configured
- Overall: "healthy"

## 📊 What the Safe Setup Does

**It WILL:**
- Connect to existing PostgreSQL
- Check table existence and data counts
- Create tables that don't exist
- Add default agents only if agents table is empty
- Add default session only if sessions table is empty

**It WILL NOT:**
- Delete any existing data
- Modify existing tables
- Drop or reset database
- Run destructive migrations

## 🚨 Emergency Commands

If anything goes wrong, the setup logs will show exactly what happened. You can always:
1. Check Railway logs for detailed operation logs
2. Manually inspect database counts via Railway PostgreSQL interface
3. Redeploy if needed (setup is idempotent - safe to run multiple times)

The `safe_db_setup.py` script is designed to be **completely non-destructive** to your existing production data.