from fastapi import APIRouter
from app.api import agents, sessions, chat, ui, diagnostic, railway_diagnostic, mcp

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(ui.router, prefix="/ui", tags=["ui"])
api_router.include_router(diagnostic.router, prefix="/system", tags=["system"])
api_router.include_router(railway_diagnostic.router, prefix="/diagnostic", tags=["diagnostic"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])