"""
Guitar Mastery AI — FastAPI Application Entry Point

Multi-agent AI application for guitar education, covering:
- Guitar history, construction, and lutherie
- Jazz theory, technique, and improvisation
- Interactive quizzes and lessons
- Practice tracking and plateau-busting
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import structlog

from config.settings import settings
from src.db.connection import init_db, async_session

logger = structlog.get_logger("main")


def _create_agents(db_factory):
    """Instantiate all specialized agents with their DB session factory."""
    from anthropic import AsyncAnthropic
    from src.agents.luthier import LuthierHistorianAgent
    from src.agents.jazz_teacher import JazzTeacherAgent
    from src.agents.sql_expert import SQLExpertAgent
    from src.agents.dev_pm import DevPMAgent

    # Create a shared Anthropic client with the API key from settings
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    return {
        "luthier_historian": LuthierHistorianAgent(db_session_factory=db_factory, client=client),
        "jazz_teacher": JazzTeacherAgent(db_session_factory=db_factory, client=client),
        "sql_expert": SQLExpertAgent(db_session_factory=db_factory, client=client),
        "dev_pm": DevPMAgent(db_session_factory=db_factory, client=client),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("starting_application", version=settings.app_version)
    await init_db()
    logger.info("database_initialized")

    # Initialize agents and orchestrator
    if settings.anthropic_api_key:
        from src.orchestrator.coordinator import AgentCoordinator

        agents = _create_agents(db_factory=async_session)
        coordinator = AgentCoordinator(agents=agents)
        app.state.coordinator = coordinator
        logger.info("agents_initialized", agents=list(agents.keys()))
    else:
        app.state.coordinator = None
        logger.warning("no_api_key", msg="ANTHROPIC_API_KEY not set — agents in routing-only mode")

    yield

    # Shutdown
    logger.info("shutting_down_application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent AI application for guitar mastery — history, theory, technique, and practice",
    lifespan=lifespan,
)

# Static files and templates
static_path = Path(__file__).parent / "frontend" / "static"
template_path = Path(__file__).parent / "frontend" / "templates"

templates = Jinja2Templates(directory=str(template_path)) if template_path.exists() else None


# ============================================================
# Import and register API routes
# ============================================================
from src.api.routes.chat import router as chat_router
from src.api.routes.admin import router as admin_router

app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

# Mount static files AFTER API routes so /static doesn't shadow anything
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ============================================================
# Root endpoint — serves the UI
# ============================================================
@app.get("/")
async def root(request: Request):
    """Serve the Guitar Mastery AI web interface."""
    if templates:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.app_version,
        })
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "ui": "Frontend templates not found. Ensure src/frontend/templates/ exists.",
    }


@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/v1/chat",
            "agents": "/api/v1/chat/agents",
            "health": "/api/v1/admin/health",
        },
    }


@app.get("/health")
async def health():
    """Quick health check."""
    return {"status": "healthy", "version": settings.app_version}
