from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

app_path = os.path.join(backend_path, 'app')
sys.path.insert(0, app_path)

# Import the FastAPI app from backend
from main import app

# Configure CORS for API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend build directory
dist_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

# Mount assets
assets_path = os.path.join(dist_dir, 'assets')
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# Serve index.html for root and any other path (SPA support)
@app.get("/{full_path:path}", include_in_schema=False)
async def read_index(full_path: str):
    # If the path is an API path, let it fall through (but FastAPI matches strictly first usually)
    # Actually, since API routes are already included in 'app', they take precedence if they match.
    # However, this catch-all might shadow 404s for API.
    # Better to only serve index.html if it's NOT an API call.
    
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not Found")

    if os.path.exists(os.path.join(dist_dir, "index.html")):
        return FileResponse(os.path.join(dist_dir, "index.html"))
    
    return {"message": "Frontend not built. Please run 'npm run build' in frontend directory."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
