#!/usr/bin/env python3
"""
Initialize the database with default data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.models import models
from app.crud import crud
from app.schemas import schemas

def create_default_agents():
    """Create default AI agents"""
    db = SessionLocal()
    try:
        # Check if agents already exist
        existing_agents = crud.get_agents(db, limit=1)
        if existing_agents:
            print("Agents already exist, skipping creation")
            return
        
        # Create Code Assistant
        code_assistant = schemas.AgentCreate(
            name="Code Assistant",
            description="Expert in programming, debugging, and code optimization",
            system_prompt="You are a helpful coding assistant. Provide clear, concise programming advice and help users optimize their code.",
            model="glm-4.6",
            temperature=0.3,
            is_active=True
        )
        crud.create_agent(db, code_assistant)
        print("Created Code Assistant")
        
        # Create General Helper
        general_helper = schemas.AgentCreate(
            name="General Helper",
            description="Helps with various tasks and general questions",
            system_prompt="You are a helpful AI assistant. Be friendly, informative, and assist with a wide range of topics.",
            model="glm-4.5",
            temperature=0.7,
            is_active=True
        )
        crud.create_agent(db, general_helper)
        print("Created General Helper")
        
        # Create Data Analyst
        data_analyst = schemas.AgentCreate(
            name="Data Analyst",
            description="Specializes in data analysis, visualization, and insights",
            system_prompt="You are a data analysis expert. Help users analyze data, create insights, and provide recommendations based on data patterns.",
            model="glm-4.5-air",
            temperature=0.5,
            is_active=True
        )
        crud.create_agent(db, data_analyst)
        print("Created Data Analyst")
        
    finally:
        db.close()

def create_default_session():
    """Create a default chat session"""
    db = SessionLocal()
    try:
        # Check if sessions already exist
        existing_sessions = crud.get_chat_sessions(db, limit=1)
        if existing_sessions:
            print("Sessions already exist, skipping creation")
            return
        
        # Get first agent (Code Assistant)
        agents = crud.get_agents(db, limit=1)
        if not agents:
            print("No agents found, please create agents first")
            return
        
        # Create default session
        default_session = schemas.ChatSessionCreate(
            title="React Performance Discussion",
            agent_id=agents[0].id,
            message_count=0
        )
        crud.create_chat_session(db, default_session)
        print("Created default chat session")
        
    finally:
        db.close()

def main():
    """Initialize database with default data"""
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    
    print("Creating default agents...")
    create_default_agents()
    
    print("Creating default session...")
    create_default_session()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    main()