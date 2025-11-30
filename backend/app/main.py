from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1 import api_router
from app.db.database import engine
from app.models import models

# CRITICAL: DO NOT create tables here - Railway startup handles it
# models.Base.metadata.create_all(bind=engine)  # REMOVED - handled by start_production.py

app = FastAPI(
    title="Chatbot API Server",
    description="Z.ai GLM Chatbot API with Knowledge Management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


# Mount static files properly
from fastapi.staticfiles import StaticFiles
import os

# Determine paths
# Docker: /app/frontend/dist
# Local: ../frontend/dist (if built) or ../frontend (source)
docker_dist_path = "/app/frontend/dist"
local_dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'dist')

frontend_dist = None
if os.path.exists(docker_dist_path):
    frontend_dist = docker_dist_path
elif os.path.exists(local_dist_path):
    frontend_dist = local_dist_path

if frontend_dist:
    # Mount assets folder if it exists
    assets_path = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# SPA Catch-All Route
# This handles serving index.html for all non-API routes to support React Router
from fastapi.responses import FileResponse
from fastapi import HTTPException

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # 1. Skip API routes (redundant as they match first, but good for safety)
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    # 2. Try to serve specific static file if it exists (e.g. favicon.ico, robot.txt)
    if frontend_dist:
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # 3. Fallback to index.html for SPA routing (React Router)
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    return {"message": "Frontend not found", "path": full_path}

@app.get("/api-status")
def status_check():
    return {"status": "online"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)