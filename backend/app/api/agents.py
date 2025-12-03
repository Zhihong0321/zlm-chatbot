from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
from app.db.database import get_db
from app.models.models import Agent
from app.schemas.schemas import (
    Agent as AgentSchema, AgentCreate, AgentUpdate, AgentWithFiles,
    AgentKnowledgeFileResponse, AgentKnowledgeFileCreate, FileUploadResponse
)
from app.crud.crud import (
    create_agent, get_agents, get_agent, update_agent, delete_agent,
    get_agent_knowledge_files, create_agent_knowledge_file, delete_agent_knowledge_file,
    get_agent_with_files, upload_file_to_zai
)

router = APIRouter()

@router.get("/test")
def test_agents_endpoint():
    return {"message": "Agents router is working"}

@router.post("/", response_model=AgentSchema)
def create_agent_endpoint(agent: AgentCreate, db: Session = Depends(get_db)):
    return create_agent(db=db, agent=agent)


@router.get("/", response_model=List[AgentSchema])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        agents = get_agents(db, skip=skip, limit=limit)
        return agents
    except Exception as e:
        # Log the specific error causing the 500
        import logging
        logging.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")


@router.get("/{agent_id}", response_model=AgentSchema)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent


@router.put("/{agent_id}", response_model=AgentSchema)
def update_agent_endpoint(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    db_agent = update_agent(db, agent_id=agent_id, agent=agent)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent


@router.delete("/{agent_id}")
def delete_agent_endpoint(agent_id: int, db: Session = Depends(get_db)):
    if not delete_agent(db, agent_id=agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}


# File Management Endpoints
@router.get("/{agent_id}/files", response_model=List[AgentKnowledgeFileResponse])
def get_agent_files(agent_id: int, db: Session = Depends(get_db)):
    # Check if agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    files = get_agent_knowledge_files(db, agent_id)
    return files


@router.post("/{agent_id}/upload", response_model=FileUploadResponse)
async def upload_agent_file(
    agent_id: int,
    file: UploadFile = File(...),
    purpose: str = Form("agent"),
    db: Session = Depends(get_db)
):
    """Upload a knowledge file to an agent"""
    
    # Check if agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Validate file type
    allowed_types = ["txt", "pdf", "doc", "docx", "xlsx", "ppt", "pptx", "jpg", "jpeg", "png"]
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ""
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type .{file_extension} not allowed. Supported: {', '.join(allowed_types)}"
        )
    
    # Validate file size (100MB max)
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB")
    
    # Get API key from environment
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Z.ai API key not configured")
    
    # Upload to Z.ai
    upload_result = upload_file_to_zai(content, file.filename, api_key)
    
    if not upload_result["success"]:
        raise HTTPException(status_code=500, detail=f"File upload failed: {upload_result['message']}")
    
    # Save file record to database
    from datetime import datetime, timedelta
    
    file_data = AgentKnowledgeFileCreate(
        agent_id=agent_id,
        zai_file_id=upload_result["file_id"],
        filename=upload_result["filename"],
        original_filename=file.filename,
        file_size=upload_result["size"],
        file_type=file_extension,
        purpose=purpose,
        status="active",
        metadata={"uploaded_by": "system", "source": "agent_upload"},
        expires_at=datetime.fromisoformat(upload_result["expires_at"].replace('Z', '+00:00'))
    )
    
    db_file = create_agent_knowledge_file(db, file_data)
    
    return FileUploadResponse(
        success=True,
        file_id=upload_result["file_id"],
        filename=upload_result["filename"],
        message="File uploaded successfully",
        size=upload_result["size"]
    )


@router.get("/{agent_id}/with-files", response_model=AgentWithFiles)
def get_agent_with_files_endpoint(agent_id: int, db: Session = Depends(get_db)):
    """Get agent details including all associated files"""
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    files = get_agent_knowledge_files(db, agent_id)
    
    # Convert to response format
    return AgentWithFiles(
        **agent.__dict__,
        knowledge_files=files
    )


@router.delete("/{agent_id}/files/{file_id}")
def delete_agent_file_endpoint(agent_id: int, file_id: int, db: Session = Depends(get_db)):
    """Delete an agent's knowledge file"""
    
    # Check if agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Delete the file
    if not delete_agent_knowledge_file(db, file_id, agent_id):
        raise HTTPException(status_code=404, detail="File not found or already deleted")
    
    return {"message": "File deleted successfully"}