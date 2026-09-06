from fastapi import APIRouter
from app.api.endpoints import (
    health,
    auth,
    documents,
    retrieval,
    rag,
    dashboard,
    conversations,
    reminders,
    notifications,
    notification_preferences,
    cricket,
    query,
    analytics,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(notification_preferences.router, prefix="/notification-preferences", tags=["Notification Preferences"])
api_router.include_router(cricket.router, tags=["Cricket Scorecard AI"])
api_router.include_router(query.router, prefix="/query", tags=["Query Router"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["AI Analytics Engine"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["Retrieval"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
