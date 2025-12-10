#!/usr/bin/env python3
"""
Seed script to create the Solar Expert v2 agent and link it to the billing-v2 MCP server.

Usage:
  python create_solar_expert_v2_agent.py
Requirements:
  - DATABASE_URL must point to your PostgreSQL instance
  - bill.json present in mcp_servers/billing_server_v2 or resource/
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.models import Base, Agent, MCPServer, AgentMCPServer


AGENT_NAME = "Solar Expert v2"


SYSTEM_PROMPT = """
You are Solar Expert v2, a Malaysian solar consultant.
Primary goals: explain TNB electricity bills clearly, convert RM <-> kWh using provided billing tools, and design rooftop solar PV systems with concise savings summaries.
When tools are needed, call the MCP billing tools: tnb_bill_rm_to_kwh, tnb_bill_kwh_to_rm, and calculate_solar_impact.
Always state assumptions, show key numbers (bill RM, kWh, system size, savings, net payable), and mention when a request is outside the bill.json range.
Keep answers short, plain-language, and actionable. Do not hallucinate prices or tariffs beyond the data provided.
"""


def get_engine() -> sessionmaker:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    engine = create_engine(db_url, future=True)
    return engine


def ensure_tables(engine):
    Base.metadata.create_all(bind=engine)


def upsert_mcp_server(session, workdir: Path) -> MCPServer:
    server_id = "billing-v2"
    server = session.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        server = MCPServer(
            id=server_id,
            name="Billing Server V2",
            description="Billing tools (RM, kWh, solar impact) using resource/bill.json",
            command="python",
            arguments=["main.py"],
            environment={},
            working_directory=str(workdir),
            enabled=True,
            auto_start=False,
            health_check_interval=30,
            status="stopped",
        )
        session.add(server)
    else:
        server.description = "Billing tools (RM, kWh, solar impact) using resource/bill.json"
        server.command = "python"
        server.arguments = ["main.py"]
        server.environment = server.environment or {}
        server.working_directory = str(workdir)
        server.enabled = True
        server.auto_start = False
        server.health_check_interval = 30
        server.status = server.status or "stopped"
    session.flush()
    return server


def upsert_agent(session) -> Agent:
    agent = session.query(Agent).filter(Agent.name == AGENT_NAME).first()
    if not agent:
        agent = Agent(
            name=AGENT_NAME,
            description="Explains TNB bills and designs solar PV systems with savings using billing MCP tools",
            system_prompt=SYSTEM_PROMPT.strip(),
            model="glm-4.6",
            temperature=0.3,
            mcp_servers=["billing-v2"],
            is_active=True,
        )
        session.add(agent)
        session.flush()
    else:
        agent.description = "Explains TNB bills and designs solar PV systems with savings using billing MCP tools"
        agent.system_prompt = SYSTEM_PROMPT.strip()
        agent.model = "glm-4.6"
        agent.temperature = 0.3
        agent.mcp_servers = ["billing-v2"]
        agent.is_active = True
        session.flush()
    return agent


def upsert_agent_mapping(session, agent: Agent, server: MCPServer):
    mapping = (
        session.query(AgentMCPServer)
        .filter(AgentMCPServer.agent_id == agent.id, AgentMCPServer.server_id == server.id)
        .first()
    )
    if not mapping:
        mapping = AgentMCPServer(agent_id=agent.id, server_id=server.id, is_enabled=True)
        session.add(mapping)
    else:
        mapping.is_enabled = True
    session.flush()


def main():
    engine = get_engine()
    ensure_tables(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    workdir = Path(__file__).resolve().parent / "mcp_servers" / "billing_server_v2"

    with SessionLocal() as session:
        server = upsert_mcp_server(session, workdir)
        agent = upsert_agent(session)
        upsert_agent_mapping(session, agent, server)
        session.commit()
        print(f"Created/updated agent '{agent.name}' (id={agent.id}) linked to MCP server '{server.id}'.")


if __name__ == "__main__":
    main()
