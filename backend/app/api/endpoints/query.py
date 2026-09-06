from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.query_router import QueryRouterRequest, QueryRouterResponse
from app.services.query_router_service import QueryRouterService, query_router_service

router = APIRouter()

@router.post(
    "",
    response_model=QueryRouterResponse,
    status_code=status.HTTP_200_OK,
    summary="Route and execute natural language query via SQL, RAG, or HYBRID"
)
def route_query(
    request: QueryRouterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: QueryRouterService = Depends(lambda: query_router_service)
) -> QueryRouterResponse:
    return service.route_and_execute(
        db=db,
        user=current_user,
        request=request
    )
