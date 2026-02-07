"""
Admin API Routes — Health checks, system status, and debugging.
"""

from fastapi import APIRouter
from src.db.connection import check_connection
from config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Comprehensive system health check."""
    db_health = await check_connection()

    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "components": {
            "database": db_health,
            "agents": {
                "luthier_historian": {"status": "configured"},
                "jazz_teacher": {"status": "configured"},
                "sql_expert": {"status": "configured"},
                "dev_pm": {"status": "configured"},
            },
            "api": {"status": "healthy"},
        },
    }


@router.get("/config")
async def get_config():
    """Return non-sensitive configuration info."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "default_model": settings.default_model,
        "rate_limit": settings.rate_limit_per_minute,
        "log_level": settings.log_level,
    }
