import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Add backend/app directory to Python path  
app_path = os.path.join(backend_path, 'app')
sys.path.insert(0, app_path)

from fastapi import FastAPI
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)