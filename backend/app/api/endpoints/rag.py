from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.rag_service import rag_service

router = APIRouter()

@router.post(
    "/query",
    response_model=RAGQueryResponse,
    status_code=status.HTTP_200_OK
)
def rag_query(
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RAGQueryResponse:
    return rag_service.answer_query(
        db=db,
        user=current_user,
        request=request
    )
