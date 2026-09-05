from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.retrieval import SearchQueryRequest, SearchQueryResponse
from app.services.retrieval_service import retrieval_service

router = APIRouter()

@router.post(
    "/search",
    response_model=SearchQueryResponse,
    status_code=status.HTTP_200_OK
)
def search_chunks(
    request: SearchQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SearchQueryResponse:
    return retrieval_service.search_similar_chunks(
        db=db,
        user=current_user,
        request=request
    )
