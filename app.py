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

# Serve static files from frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root - THIS MUST COME AFTER API ROUTES
# Get all existing routes first
existing_routes = [route.path for route in app.routes]

# Add root route only if not already present
if "/" not in existing_routes:
    @app.get("/", include_in_schema=False)
    async def read_index():
        return FileResponse('frontend/index.html')

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)