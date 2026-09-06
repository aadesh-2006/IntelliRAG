import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationDetailResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services.conversation_service import conversation_service

router = APIRouter()

@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_conversation(
    payload: ConversationCreateRequest = ConversationCreateRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ConversationResponse:
    return conversation_service.create_conversation(
        db=db,
        user=current_user,
        title=payload.title
    )

@router.get(
    "",
    response_model=List[ConversationResponse],
    status_code=status.HTTP_200_OK
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ConversationResponse]:
    return conversation_service.list_conversations(
        db=db,
        user=current_user
    )

@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_200_OK
)
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ConversationDetailResponse:
    return conversation_service.get_conversation_by_id(
        db=db,
        user=current_user,
        conversation_id=conversation_id
    )

@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    conversation_service.delete_conversation(
        db=db,
        user=current_user,
        conversation_id=conversation_id
    )

@router.post(
    "/{conversation_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_200_OK
)
def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SendMessageResponse:
    return conversation_service.send_message(
        db=db,
        user=current_user,
        conversation_id=conversation_id,
        request=payload
    )
