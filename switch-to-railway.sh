#!/bin/bash
# Switch to Railway Deployment Mode

echo "🚂 Switching to RAILWAY DEPLOYMENT mode..."

# Copy Railway environment template
cp .env.example .env

echo "📝 Railway environment configured!"
echo ""
echo "🚂 DEPLOYMENT INSTRUCTIONS:"
echo "   1. Push changes to GitHub:"
echo "      git add ."
echo "      git commit -m 'Configure for Railway deployment'"
echo "      git push origin master"
echo ""
echo "   2. Railway will auto-deploy from latest commit"
echo "   3. Set environment variables in Railway dashboard if needed:"
echo "      - ZAI_API_KEY"
echo "      - DATABASE_URL (auto-provided by Railway)"
echo "      - ENVIRONMENT=production"
echo ""
echo "   4. Check Railway deployment logs for errors"
