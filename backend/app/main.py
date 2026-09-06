from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import health
from app.api.router import api_router
from app.config import settings
from app.core.scheduler import app_scheduler

@asynccontextmanager
async def lifespan(application: FastAPI):
    if settings.SCHEDULER_ENABLED:
        app_scheduler.start()
    yield
    if app_scheduler.is_running:
        app_scheduler.shutdown(wait=False)

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="IntelliRAG - Autonomous Multimodal Document AI, Enterprise Hybrid RAG, Cricket Scorecard Intelligence, and Actionable Reminder Engine.",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router, tags=["Health"])
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
