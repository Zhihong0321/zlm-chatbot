from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1 import api_router
from app.db.database import engine
from app.models import models

# Create database tables
# models.Base.metadata.create_all(bind=engine)

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

# Global Exception Handler
from fastapi import Request
from fastapi.responses import JSONResponse
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_details = traceback.format_exc()
    print(f"GLOBAL ERROR: {error_details}")  # Log to stdout for Railway logs
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc), "trace": error_details}
    )

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