from fastapi import APIRouter
from app.api.endpoints import health, auth, documents

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])