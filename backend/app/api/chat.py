from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import ChatMessage, AgentMCPServer, MCPServer
from app.schemas.schemas import ChatMessageCreate, ChatMessage as ChatMessageSchema, ChatResponse, ChatRequest, MessageRequest
from app.crud.crud import create_chat_message, get_chat_session, get_session_knowledge
from app.core.zai_client import get_zai_client
from typing import Dict, Any, List, Optional
import json
import logging
import time
from pathlib import Path

from fastapi import HTTPException

BILLING_SERVER_IDS = {"billing-auto", "billing-1", "6a98396f-83de-441c-9a39-5c785e1d0230"}
_BILL_CACHE = None

router = APIRouter()


@router.post("/{session_id}/messages", response_model=ChatMessageSchema)
def send_message(
    session_id: int, 
    request: MessageRequest,
    db: Session = Depends(get_db)
):
    try:
        # Explicitly query session and agent separately to avoid lazy loading issues
        from app.models.models import ChatSession, Agent
        
        db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if db_session is None:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Get agent explicitly
        agent = db.query(Agent).filter(Agent.id == db_session.agent_id).first()
        if not agent:
             raise HTTPException(status_code=404, detail="Agent for session not found")
        
        message = request.message
        
        # Create user message
        user_message = ChatMessageCreate(
            session_id=session_id,
            role="user",
            content=message
        )
        db_message = create_chat_message(db=db, message=user_message)
        
        # Get knowledge context  
        knowledge_files = get_session_knowledge(db, session_id=session_id)
        
        # Build context
        context = f"Agent: {agent.name}\nSystem Prompt: {agent.system_prompt}"
        
        if knowledge_files:
            context += "\n\nKnowledge Context:\n"
            for kf in knowledge_files:
                context += f"\n--- {kf.filename} ---\n{kf.content}\n"
        
        # Get AI response
        try:
            ai_response = chat_with_zai(
                message=message,
                system_prompt=context,
                model=agent.model,
                temperature=agent.temperature
            )
            
            # Create assistant message
            assistant_message = ChatMessageCreate(
                session_id=session_id,
                role="assistant",
                content=ai_response["content"],
                reasoning_content=ai_response.get("reasoning_content"),
                model=ai_response["model"],
                token_usage=ai_response["token_usage"]
            )
            db_assistant_message = create_chat_message(db=db, message=assistant_message)
            
            return db_assistant_message
        except Exception as e:
            # Rollback is handled by global exception handler or dependency if not done here
            # But explicit is better for transaction errors
            db.rollback()
            import logging
            logging.getLogger(__name__).error(f"Chat error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")
    except HTTPException:
        # HTTP exceptions are fine, just re-raise
        raise
    except Exception as e:
        # Fallback for any other error in the route
        db.rollback()
        import logging
        logging.getLogger(__name__).error(f"Internal chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{session_id}/upload")
async def upload_knowledge_file(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify session exists
    db_session = get_chat_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check file size (50KB limit)
    max_size = 50 * 1024  # 50KB
    content = await file.read()
    
    if len(content) > max_size:
        raise HTTPException(
            status_code=413, 
            detail="File size exceeds 50KB limit"
        )
    
    # Decode content
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be text-based (UTF-8 encoded)"
        )
    
    # Create knowledge record
    from app.schemas.schemas import SessionKnowledgeCreate
    from app.crud.crud import create_session_knowledge
    
    knowledge = SessionKnowledgeCreate(
        session_id=session_id,
        filename=file.filename,
        content=text_content,
        file_size=len(content)
    )
    
    db_knowledge = create_session_knowledge(db=db, knowledge=knowledge)
    
    return {
        "message": "File uploaded successfully",
        "knowledge": db_knowledge
    }


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Verify session exists
        from app.models.models import ChatSession, Agent
        db_session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        
        if db_session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get agent info
        agent = None
        if request.agent_id:
             agent = db.query(Agent).filter(Agent.id == request.agent_id).first()
             if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
        else:
             # Explicitly load agent from session relation ID
             agent = db.query(Agent).filter(Agent.id == db_session.agent_id).first()
             if not agent:
                # Fallback if data is corrupted
                 raise HTTPException(status_code=404, detail="Agent for session not found")
        
        # Get knowledge context
        knowledge_files = get_session_knowledge(db, session_id=request.session_id)
        
        # Build context
        context = f"Agent: {agent.name}\nSystem Prompt: {agent.system_prompt}"
        
        if knowledge_files:
            context += "\n\nKnowledge Context:\n"
            for kf in knowledge_files:
                context += f"\n--- {kf.filename} ---\n{kf.content}\n"
        
        # Get AI response with MCP tool support
        try:
            logger = logging.getLogger(__name__)
            client = get_zai_client()

            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": request.message})

            tools, server_map = _build_tools_for_agent(db, agent)
            tool_choice = "auto" if tools else None

            start_time = time.time()

            response = client.chat.completions.create(
                model=agent.model,
                messages=messages,
                temperature=agent.temperature,
                tools=tools or None,
                tool_choice=tool_choice
            )

            message = response.choices[0].message
            tools_used: List[Dict[str, Any]] = []
            mcp_responses: Dict[str, Any] = {}

            # If tool calls were requested, execute them and get final answer
            if getattr(message, "tool_calls", None):
                messages.append(message.model_dump(exclude_none=True))
                tool_outputs = []

                for call in message.tool_calls:
                    tool_name = call.function.name
                    args = json.loads(call.function.arguments or "{}")
                    result_text, server_id = _dispatch_tool(tool_name, args, server_map)
                    tools_used.append({"tool": tool_name, "arguments": args, "server_id": server_id})
                    mcp_responses.setdefault(server_id, []).append({"tool": tool_name, "result": result_text})
                    tool_outputs.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result_text
                    })

                messages.extend(tool_outputs)

                response = client.chat.completions.create(
                    model=agent.model,
                    messages=messages,
                    temperature=agent.temperature
                )
                message = response.choices[0].message

            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Z.ai API Latency: {duration:.2f}s. Model: {agent.model}")

            # Store user message
            user_message = ChatMessageCreate(
                session_id=request.session_id,
                role="user",
                content=request.message
            )
            create_chat_message(db=db, message=user_message)

            token_usage = response.usage.model_dump() if response.usage else None

            # Store assistant message
            assistant_message = ChatMessageCreate(
                session_id=request.session_id,
                role="assistant",
                content=message.content or message.reasoning_content or "",
                reasoning_content=message.reasoning_content,
                model=agent.model,
                token_usage=token_usage,
                tools_used=tools_used or None,
                mcp_server_responses=mcp_responses or None
            )
            create_chat_message(db=db, message=assistant_message)

            return ChatResponse(
                message=assistant_message.content,
                reasoning_content=assistant_message.reasoning_content,
                model=assistant_message.model,
                token_usage=assistant_message.token_usage or {}
            )

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).error(f"Internal chat error (playground): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Helpers
def _build_tools_for_agent(db: Session, agent) -> (List[Dict[str, Any]], Dict[str, MCPServer]):
    """Return tool definitions and server map for the agent."""
    servers = _get_agent_mcp_servers(db, agent.id)
    server_map = {s.id: s for s in servers}
    tools: List[Dict[str, Any]] = []

    for server in servers:
        if server.id in BILLING_SERVER_IDS or (server.name and "billing" in server.name.lower()):
            tools.extend(_billing_tools())

    return tools, server_map


def _get_agent_mcp_servers(db: Session, agent_id: int) -> List[MCPServer]:
    """Fetch mapped MCP servers for agent (AgentMCPServer), fallback to enabled Billing server."""
    assignments = db.query(AgentMCPServer).filter(
        AgentMCPServer.agent_id == agent_id,
        AgentMCPServer.is_enabled == True
    ).all()

    server_ids = [a.server_id for a in assignments]
    servers: List[MCPServer] = []
    if server_ids:
        servers = db.query(MCPServer).filter(MCPServer.id.in_(server_ids), MCPServer.enabled == True).all()

    if servers:
        return servers

    # Fallback: pick enabled billing server if present
    fallback = db.query(MCPServer).filter(MCPServer.enabled == True, MCPServer.name.ilike("%billing%"))
    servers = fallback.all()
    return servers


def _billing_tools() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "tnb_bill_rm_to_kwh",
                "description": "Convert RM amount to the nearest kWh usage using bill.json",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rm": {"type": "number", "description": "Bill amount in RM"}
                    },
                    "required": ["rm"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tnb_bill_kwh_to_rm",
                "description": "Convert kWh usage to RM using bill.json",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "kwh": {"type": "number", "description": "Usage in kWh"}
                    },
                    "required": ["kwh"]
                }
            }
        }
    ]


def _dispatch_tool(name: str, arguments: Dict[str, Any], server_map: Dict[str, MCPServer]):
    """Dispatch tool to the appropriate MCP server. For now, billing tools are handled inline using bill.json."""
    # Choose billing server id if available
    server_id = None
    if server_map:
        for sid, srv in server_map.items():
            if sid in BILLING_SERVER_IDS or (srv.name and "billing" in srv.name.lower()):
                server_id = sid
                break

    if name in {"tnb_bill_rm_to_kwh", "tnb_bill_kwh_to_rm"}:
        result = _execute_billing_tool(name, arguments)
        return result, server_id or "billing"

    return f"Unsupported tool {name}", server_id or "unknown"


def _load_bill_table():
    global _BILL_CACHE
    if _BILL_CACHE is not None:
        return _BILL_CACHE

    candidates = [
        Path("/app/mcp_servers/billing_server/bill.json"),
        Path("/app/resource/bill.json"),
        Path(__file__).resolve().parents[3] / "mcp_servers" / "billing_server" / "bill.json",
        Path(__file__).resolve().parents[3] / "resource" / "bill.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                _BILL_CACHE = data
                return data
            except Exception:
                continue
    raise RuntimeError("bill.json not found for billing MCP")


def _execute_billing_tool(name: str, arguments: Dict[str, Any]) -> str:
    data = _load_bill_table()
    if not data:
        return "out_of_scope: billing data unavailable"

    try:
        if name == "tnb_bill_rm_to_kwh":
            rm = float(arguments.get("rm"))
            rec = min(data, key=lambda r: abs(float(r.get("bill", 0)) - rm))
            bill_val = float(rec.get("bill", 0))
            if abs(bill_val - rm) > bill_val * 10:  # crude guard for wild values
                return "out_of_scope: value outside bill.json range"
            return f"{rec.get('kwh')} kWh (nearest to RM {rm:.2f}, bill entry RM {bill_val:.2f})"

        if name == "tnb_bill_kwh_to_rm":
            kwh = float(arguments.get("kwh"))
            rec = min(data, key=lambda r: abs(float(r.get("kwh", 0)) - kwh))
            kwh_val = float(rec.get("kwh", 0))
            if abs(kwh_val - kwh) > kwh_val * 10:
                return "out_of_scope: value outside bill.json range"
            return f"RM {rec.get('bill'):.2f} (nearest to {kwh} kWh, bill entry {kwh_val} kWh)"
    except Exception as e:
        return f"error executing billing tool: {e}"

    return "Unsupported billing tool"