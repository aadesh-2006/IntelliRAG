from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.schemas.retrieval import SearchQueryRequest
from app.services.retrieval_service import RetrievalService, retrieval_service
from app.services.prompt_service import PromptService, prompt_service
from app.services.llm_service import BaseLLMService, llm_service

class RAGService:
    def __init__(
        self,
        retriever: Optional[RetrievalService] = None,
        prompter: Optional[PromptService] = None,
        llm: Optional[BaseLLMService] = None
    ):
        self.retrieval_service = retriever or retrieval_service
        self.prompt_service = prompter or prompt_service
        self.llm_service = llm or llm_service

    def answer_query(
        self,
        db: Session,
        user: User,
        request: RAGQueryRequest
    ) -> RAGQueryResponse:
        cleaned_query = request.query.strip()
        if not cleaned_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query text cannot be empty or whitespace only"
            )

        retrieval_req = SearchQueryRequest(
            query=cleaned_query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            document_ids=request.document_ids,
            document_type=request.document_type
        )

        retrieval_res = self.retrieval_service.search_similar_chunks(
            db=db,
            user=user,
            request=retrieval_req
        )

        model_info = {
            "provider": self.llm_service.provider_name,
            "model": self.llm_service.model_name
        }

        if not retrieval_res.results:
            return RAGQueryResponse(
                query=cleaned_query,
                answer="The provided documents do not contain sufficient information to answer this question.",
                citations=[],
                retrieved_chunks_count=0,
                has_sufficient_context=False,
                model_info=model_info
            )

        context_text, citations = self.prompt_service.build_context_and_citations(retrieval_res.results)

        if not citations:
            return RAGQueryResponse(
                query=cleaned_query,
                answer="The provided documents do not contain sufficient information to answer this question.",
                citations=[],
                retrieved_chunks_count=0,
                has_sufficient_context=False,
                model_info=model_info
            )

        user_prompt = self.prompt_service.build_user_prompt(cleaned_query, context_text)

        generated_answer = self.llm_service.generate(
            system_prompt=self.prompt_service.SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        is_insufficient = (
            "do not contain sufficient information" in generated_answer.lower() or
            "does not contain sufficient information" in generated_answer.lower() or
            "do not provide enough information" in generated_answer.lower()
        )

        return RAGQueryResponse(
            query=cleaned_query,
            answer=generated_answer,
            citations=citations,
            retrieved_chunks_count=len(citations),
            has_sufficient_context=not is_insufficient,
            model_info=model_info
        )

rag_service = RAGService()
