from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResponse
from app.services.analytics_service import analytics_service

router = APIRouter()

@router.post("/query", response_model=AnalyticsQueryResponse, status_code=status.HTTP_200_OK)
def query_analytics(
    request: AnalyticsQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnalyticsQueryResponse:
    return analytics_service.query_analytics(
        db=db,
        user=current_user,
        request=request
    )
