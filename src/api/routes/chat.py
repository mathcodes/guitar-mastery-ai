"""
Chat API Routes — Main conversational endpoint for the Guitar Mastery AI.

Handles:
- Single-turn chat messages
- Streaming responses via SSE
- Session management
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional

import structlog

from src.orchestrator.router import classify_intent
from src.orchestrator.context import ConversationContext

router = APIRouter()
logger = structlog.get_logger("api.chat")


# ============================================================
# Request/Response Schemas
# ============================================================

class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User identifier")
    preferred_agent: Optional[str] = Field(None, description="Force routing to a specific agent")
    skill_level: str = Field("intermediate", description="User skill level")

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "message": "What scales can I play over a Cmaj7 chord?",
                "skill_level": "intermediate",
            }
        ]
    }}


class ChatResponse(BaseModel):
    """Response from the agent system."""
    message: str
    agent_used: str
    session_id: str
    suggestions: list[str] = []
    data: dict = {}
    routing_info: dict = {}
    metadata: dict = {}


# ============================================================
# Endpoints
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Main chat endpoint — send a message and get a response from the
    appropriate specialized agent.

    The orchestrator automatically routes your message to the best agent:
    - Guitar Luthier & Historian: construction, history, tonewoods
    - Jazz Guitar Teacher: theory, technique, practice, improvisation
    - SQL Expert: database queries about the knowledge base
    - Dev/PM: system status, benchmarks, documentation
    """
    # Bring-your-own-key: a visitor's key arrives per request and is used only
    # for this call. It is never logged, stored, or returned.
    visitor_key = (http_request.headers.get("x-anthropic-api-key") or "").strip()
    if visitor_key:
        if not visitor_key.startswith("sk-ant-") or len(visitor_key) > 300:
            raise HTTPException(status_code=400, detail="That doesn't look like an Anthropic API key (it should start with sk-ant-).")
        from src.main import build_coordinator

        coordinator = build_coordinator(visitor_key)
    else:
        coordinator = getattr(http_request.app.state, "coordinator", None)

    # Create or restore context
    ctx_kwargs = {
        "user_id": request.user_id,
        "user_skill_level": request.skill_level,
    }
    if request.session_id:
        ctx_kwargs["session_id"] = request.session_id
    context = ConversationContext(**ctx_kwargs)

    # Override agent if user specified one
    if request.preferred_agent:
        context.metadata["preferred_agent"] = request.preferred_agent

    # Add user message to context
    context.add_message("user", request.message)

    # Use the live orchestrator if available
    if coordinator:
        try:
            result = await coordinator.process_message(request.message, context)
            return ChatResponse(
                message=result.content,
                agent_used=result.primary_agent,
                session_id=result.session_id,
                suggestions=result.suggestions,
                data=result.data,
                routing_info=result.routing_decision,
                metadata={
                    "tokens_input": result.total_tokens_input,
                    "tokens_output": result.total_tokens_output,
                    "latency_ms": result.total_latency_ms,
                    "all_agents_used": result.all_agents_used,
                },
            )
        except Exception as e:
            from anthropic import AuthenticationError, PermissionDeniedError, RateLimitError

            if isinstance(e, AuthenticationError):
                raise HTTPException(status_code=401, detail="Anthropic rejected that API key. Check it and try again.")
            if isinstance(e, PermissionDeniedError):
                raise HTTPException(status_code=403, detail="That API key doesn't have access to the model this app uses.")
            if isinstance(e, RateLimitError):
                raise HTTPException(status_code=429, detail="Your Anthropic account is rate-limited right now. Wait a moment and retry.")
            logger.error("chat_error", error_type=type(e).__name__)
            raise HTTPException(status_code=502, detail="The agent couldn't complete that request. Please try again.")

    # Fallback: routing-only mode (no API key configured)
    routing = classify_intent(request.message)
    return ChatResponse(
        message=f"**Routing preview:** this question would go to the "
                f"**{routing.agent_name.replace('_', ' ')}** agent "
                f"({round(routing.confidence * 100)}% confidence).\n\n"
                f"To get a full answer, add your Anthropic API key with the "
                f"**API key** button at the top of the page. The key stays in your browser "
                f"and is only used to call Claude for your own questions.",
        agent_used=routing.agent_name,
        session_id=context.session_id,
        suggestions=[
            "Try: What scales work over a dominant 7th chord?",
            "Try: Tell me about the history of the Les Paul",
            "Try: Show me all jazz chords with difficulty 3+",
        ],
        routing_info={
            "agent": routing.agent_name,
            "confidence": routing.confidence,
            "category": routing.intent_category,
            "is_multi_agent": routing.is_multi_agent,
            "reasoning": routing.reasoning,
        },
    )


@router.get("/chat/agents")
async def list_agents():
    """List all available agents and their capabilities."""
    return {
        "agents": [
            {
                "name": "luthier_historian",
                "display_name": "Guitar Luthier & Historian",
                "description": "Expert in guitar construction, tonewood science, instrument history, and famous luthiers",
                "example_queries": [
                    "Who built the first archtop guitar?",
                    "What wood is best for an acoustic guitar top?",
                    "Tell me about the history of the Fender Stratocaster",
                ],
            },
            {
                "name": "jazz_teacher",
                "display_name": "Jazz Guitar Teacher (Mastery Level)",
                "description": "Master jazz educator covering theory, technique, improvisation, and practice methodology",
                "example_queries": [
                    "What scales work over a Dm7 chord?",
                    "How do I break out of a playing rut?",
                    "Explain the ii-V-I progression",
                    "Quiz me on jazz chord types",
                ],
            },
            {
                "name": "sql_expert",
                "display_name": "SQL & Data Expert",
                "description": "Translates natural language to SQL queries against the guitar knowledge database",
                "example_queries": [
                    "Show me all chords with difficulty 4 or higher",
                    "How many jazz standards are in the database?",
                    "Find all scales compatible with dominant 7th chords",
                ],
            },
            {
                "name": "dev_pm",
                "display_name": "Full Stack Developer & PM",
                "description": "Manages development workflow, benchmarks, documentation, and system health",
                "example_queries": [
                    "What's the current development status?",
                    "Show me recent error logs",
                    "Generate a progress report",
                ],
            },
        ]
    }
