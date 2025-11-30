from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import Agent
from app.schemas.schemas import Agent as AgentSchema, AgentCreate, AgentUpdate
from app.crud.crud import create_agent, get_agents, get_agent, update_agent, delete_agent

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