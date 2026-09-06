import uuid
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from app.models.user import User
from app.models.conversation import Conversation, ConversationMessage
from app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    ConversationMessageResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.schemas.rag import RAGQueryRequest, Citation
from app.services.rag_service import RAGService, rag_service

class ConversationService:
    def __init__(self, rag: Optional[RAGService] = None):
        self.rag_service = rag or rag_service

    def create_conversation(
        self,
        db: Session,
        user: User,
        title: Optional[str] = None
    ) -> ConversationResponse:
        conv_title = title.strip() if title and title.strip() else "New Conversation"
        conv = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title=conv_title
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=0
        )

    def list_conversations(
        self,
        db: Session,
        user: User
    ) -> List[ConversationResponse]:
        stmt = (
            select(
                Conversation,
                func.count(ConversationMessage.id).label("message_count")
            )
            .outerjoin(ConversationMessage, Conversation.id == ConversationMessage.conversation_id)
            .where(Conversation.user_id == user.id)
            .group_by(Conversation.id)
            .order_by(desc(Conversation.updated_at))
        )

        results = db.execute(stmt).all()
        conversations = []
        for conv, count in results:
            conversations.append(
                ConversationResponse(
                    id=conv.id,
                    user_id=conv.user_id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=count
                )
            )
        return conversations

    def get_conversation_by_id(
        self,
        db: Session,
        user: User,
        conversation_id: uuid.UUID
    ) -> ConversationDetailResponse:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
        conv = db.execute(stmt).scalar_one_or_none()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        messages_stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
        )
        db_messages = list(db.execute(messages_stmt).scalars().all())

        parsed_messages = []
        for m in db_messages:
            cits = None
            if m.citations:
                cits = [Citation.model_validate(c) for c in m.citations]
            parsed_messages.append(
                ConversationMessageResponse(
                    id=m.id,
                    conversation_id=m.conversation_id,
                    role=m.role,
                    content=m.content,
                    citations=cits,
                    grounding_metadata=m.grounding_metadata,
                    is_sufficient_context=m.is_sufficient_context,
                    created_at=m.created_at
                )
            )

        return ConversationDetailResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=parsed_messages
        )

    def delete_conversation(
        self,
        db: Session,
        user: User,
        conversation_id: uuid.UUID
    ) -> None:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
        conv = db.execute(stmt).scalar_one_or_none()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        db.delete(conv)
        db.commit()

    def send_message(
        self,
        db: Session,
        user: User,
        conversation_id: uuid.UUID,
        request: SendMessageRequest
    ) -> SendMessageResponse:
        cleaned_content = request.content.strip()
        if not cleaned_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content cannot be empty"
            )

        conv_stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
        conv = db.execute(conv_stmt).scalar_one_or_none()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        past_msgs_stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(6)
        )
        past_db_msgs = list(db.execute(past_msgs_stmt).scalars().all())
        past_db_msgs.reverse()

        history_context = [
            {"role": m.role, "content": m.content}
            for m in past_db_msgs
        ]

        rag_req = RAGQueryRequest(
            query=cleaned_content,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            document_ids=request.document_ids,
            document_type=request.document_type
        )

        rag_res = self.rag_service.answer_query(
            db=db,
            user=user,
            request=rag_req,
            history=history_context
        )

        user_msg = ConversationMessage(
            id=uuid.uuid4(),
            conversation_id=conv.id,
            role="user",
            content=cleaned_content,
            is_sufficient_context=True
        )
        db.add(user_msg)

        citations_data = [
            c.model_dump(mode="json")
            for c in rag_res.citations
        ] if rag_res.citations else None

        grounding_metadata = {
            "retrieved_sources": len(rag_res.citations),
            "highest_similarity": max((c.similarity_score for c in rag_res.citations), default=0.0),
            "average_similarity": round(sum(c.similarity_score for c in rag_res.citations) / len(rag_res.citations), 4) if rag_res.citations else 0.0,
            "has_sufficient_context": rag_res.has_sufficient_context,
            "model_info": rag_res.model_info,
        }

        assistant_msg = ConversationMessage(
            id=uuid.uuid4(),
            conversation_id=conv.id,
            role="assistant",
            content=rag_res.answer,
            citations=citations_data,
            grounding_metadata=grounding_metadata,
            is_sufficient_context=rag_res.has_sufficient_context
        )
        db.add(assistant_msg)

        if conv.title in ("New Conversation", "", None):
            conv.title = cleaned_content[:50]

        conv.updated_at = func.now()
        db.commit()
        db.refresh(user_msg)
        db.refresh(assistant_msg)

        return SendMessageResponse(
            user_message=ConversationMessageResponse(
                id=user_msg.id,
                conversation_id=user_msg.conversation_id,
                role=user_msg.role,
                content=user_msg.content,
                citations=None,
                grounding_metadata=None,
                is_sufficient_context=True,
                created_at=user_msg.created_at
            ),
            assistant_message=ConversationMessageResponse(
                id=assistant_msg.id,
                conversation_id=assistant_msg.conversation_id,
                role=assistant_msg.role,
                content=assistant_msg.content,
                citations=rag_res.citations,
                grounding_metadata=grounding_metadata,
                is_sufficient_context=rag_res.has_sufficient_context,
                created_at=assistant_msg.created_at
            )
        )

conversation_service = ConversationService()
