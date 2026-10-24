"""
Guitar Mastery AI — FastAPI Application Entry Point

Multi-agent AI application for guitar education, covering:
- Guitar history, construction, and lutherie
- Jazz theory, technique, and improvisation
- Interactive quizzes and lessons
- Practice tracking and plateau-busting
"""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import structlog

from config.settings import settings
from src.db.connection import init_db, async_session

logger = structlog.get_logger("main")


def _create_agents(db_factory, api_key: str):
    """Instantiate all specialized agents with their DB session factory."""
    from anthropic import AsyncAnthropic
    from src.agents.luthier import LuthierHistorianAgent
    from src.agents.jazz_teacher import JazzTeacherAgent
    from src.agents.sql_expert import SQLExpertAgent
    from src.agents.dev_pm import DevPMAgent

    client = AsyncAnthropic(api_key=api_key)

    return {
        "luthier_historian": LuthierHistorianAgent(db_session_factory=db_factory, client=client),
        "jazz_teacher": JazzTeacherAgent(db_session_factory=db_factory, client=client),
        "sql_expert": SQLExpertAgent(db_session_factory=db_factory, client=client),
        "dev_pm": DevPMAgent(db_session_factory=db_factory, client=client),
    }


def build_coordinator(api_key: str):
    """Build an orchestrator bound to one Anthropic API key.

    The public demo is bring-your-own-key: each request can carry the
    visitor's key, so a coordinator is built per key and never stored.
    """
    from src.orchestrator.coordinator import AgentCoordinator

    return AgentCoordinator(agents=_create_agents(db_factory=async_session, api_key=api_key))


_ready = False
_ready_lock = asyncio.Lock()


async def ensure_ready():
    """Create tables and load seed data once per process.

    Runs from the lifespan hook and again lazily on the first request, because
    serverless platforms do not always deliver ASGI lifespan events.
    """
    global _ready
    if _ready:
        return
    async with _ready_lock:
        if _ready:
            return
        await init_db()
        from src.db.seed import seed_all

        await seed_all()
        _ready = True
        logger.info("database_ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("starting_application", version=settings.app_version)
    await ensure_ready()

    # Optional server-side key (local development). The hosted demo leaves it unset.
    app.state.coordinator = build_coordinator(settings.anthropic_api_key) if settings.anthropic_api_key else None
    if app.state.coordinator is None:
        logger.info("byok_mode", msg="No server ANTHROPIC_API_KEY; visitors supply their own key")

    yield

    logger.info("shutting_down_application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent AI application for guitar mastery — history, theory, technique, and practice",
    lifespan=lifespan,
    # The stock Swagger UI fails WCAG 2.2 AA (contrast, nested controls, no lang);
    # /docs serves an accessible reference generated from the same OpenAPI schema.
    docs_url=None,
    redoc_url=None,
)

class ReadinessMiddleware(BaseHTTPMiddleware):
    """Guarantee the database is initialised before any API request."""

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api"):
            await ensure_ready()
        return await call_next(request)


app.add_middleware(ReadinessMiddleware)

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
@app.get("/", include_in_schema=False)
async def root(request: Request):
    """Serve the Guitar Mastery AI web interface."""
    if templates:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"app_name": settings.app_name, "version": settings.app_version},
        )
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "ui": "Frontend templates not found. Ensure src/frontend/templates/ exists.",
    }


def _schema_fields(schema: dict, components: dict) -> list[dict]:
    """Flatten a request-body schema into rows for the docs table."""
    ref = schema.get("$ref", "")
    if ref:
        schema = components.get(ref.split("/")[-1], {})
    required = set(schema.get("required", []))
    rows = []
    for name, prop in schema.get("properties", {}).items():
        kind = prop.get("type") or "/".join(
            p.get("type", "object") for p in prop.get("anyOf", []) if p.get("type") != "null"
        ) or "object"
        rows.append({
            "name": name,
            "type": kind,
            "required": name in required,
            "description": prop.get("description", ""),
        })
    return rows


@app.get("/docs", include_in_schema=False)
async def api_docs(request: Request):
    """Accessible API reference built from the OpenAPI schema."""
    spec = app.openapi()
    components = spec.get("components", {}).get("schemas", {})
    endpoints = []
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            body = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            endpoints.append({
                "method": method.upper(),
                "path": path,
                "summary": op.get("summary", ""),
                "description": (op.get("description") or "").strip(),
                "tag": (op.get("tags") or ["general"])[0],
                "fields": _schema_fields(body, components) if body else [],
                "id": f"{method}-{path}".replace("/", "-").strip("-"),
            })
    return templates.TemplateResponse(
        request,
        "docs.html",
        {"spec": spec, "endpoints": endpoints, "app_name": settings.app_name, "version": settings.app_version},
    )


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
