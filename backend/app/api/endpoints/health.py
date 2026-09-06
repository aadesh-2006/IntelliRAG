from fastapi import APIRouter
from sqlalchemy import text
from app.config import settings
from app.db.session import engine
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    db_status = "disconnected"
    app_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "unavailable"
        app_status = "degraded"

    return HealthResponse(
        status=app_status,
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
    )

@router.get("/health/ready", response_model=ReadinessResponse)
def get_readiness() -> ReadinessResponse:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return ReadinessResponse(status="ready", database="connected")
    except Exception:
        return ReadinessResponse(status="not_ready", database="unavailable")