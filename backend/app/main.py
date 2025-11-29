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


@app.get("/")
def root():
    from fastapi.responses import FileResponse
    import os
    # Serve frontend/index.html from parent directory (correct path)
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend', 'index.html')
    return FileResponse(frontend_path)


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)