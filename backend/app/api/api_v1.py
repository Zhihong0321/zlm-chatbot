from fastapi import APIRouter
from app.api import agents, sessions, chat, ui

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(ui.router, prefix="/ui", tags=["ui"])