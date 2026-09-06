from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.query_router import QueryClassification, QueryRouterRequest, QueryRouterResponse, RouteType
from app.schemas.retrieval import SearchQueryRequest
from app.services.query_router.structured_service import StructuredDataService, structured_data_service
from app.services.retrieval_service import RetrievalService, retrieval_service
from app.services.prompt_service import PromptService, prompt_service
from app.services.llm_service import BaseLLMService, llm_service

class HybridQueryService:
    def __init__(
        self,
        structured_svc: Optional[StructuredDataService] = None,
        retriever: Optional[RetrievalService] = None,
        prompter: Optional[PromptService] = None,
        llm: Optional[BaseLLMService] = None
    ):
        self.structured_service = structured_svc or structured_data_service
        self.retrieval_service = retriever or retrieval_service
        self.prompt_service = prompter or prompt_service
        self.llm_service = llm or llm_service

    def execute(
        self,
        db: Session,
        user: User,
        classification: QueryClassification,
        request: QueryRouterRequest,
        history: Optional[List[Dict[str, str]]] = None
    ) -> QueryRouterResponse:
        cleaned_query = request.query.strip()

        structured_res = self.structured_service.execute(
            db=db,
            user=user,
            classification=classification,
            request=request
        )

        retrieval_req = SearchQueryRequest(
            query=cleaned_query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold or 0.0,
            document_ids=request.document_ids,
            document_type=request.document_type
        )

        retrieval_res = self.retrieval_service.search_similar_chunks(
            db=db,
            user=user,
            request=retrieval_req
        )

        context_text, citations = self.prompt_service.build_context_and_citations(retrieval_res.results)

        has_structured = bool(structured_res.get("structured_data"))
        has_text_context = bool(citations)

        model_info = {
            "provider": self.llm_service.provider_name,
            "model": self.llm_service.model_name
        }

        if not has_structured and not has_text_context:
            return QueryRouterResponse(
                query=cleaned_query,
                route=RouteType.HYBRID,
                intent=classification.intent,
                confidence=classification.confidence,
                answer="The provided documents and structured records do not contain sufficient information to perform this comparison.",
                structured_data=structured_res.get("structured_data"),
                citations=[],
                retrieved_chunks_count=0,
                has_sufficient_context=False,
                model_info=model_info
            )

        structured_fact_block = (
            f"=== STRUCTURED REPOSITORY FACTS ===\n"
            f"{structured_res.get('answer', '')}\n"
            f"=== END STRUCTURED FACTS ===\n\n"
        )

        combined_context = f"{structured_fact_block}=== RETRIEVED DOCUMENT CONTEXT ===\n{context_text}\n=== END DOCUMENT CONTEXT ==="

        user_prompt = self.prompt_service.build_user_prompt(
            query=cleaned_query,
            context_text=combined_context,
            history=history
        )

        generated_answer = self.llm_service.generate(
            system_prompt=self.prompt_service.SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        is_insufficient = (
            "do not contain sufficient information" in generated_answer.lower() or
            "does not contain sufficient information" in generated_answer.lower() or
            "do not provide enough information" in generated_answer.lower()
        )

        return QueryRouterResponse(
            query=cleaned_query,
            route=RouteType.HYBRID,
            intent=classification.intent,
            confidence=classification.confidence,
            answer=generated_answer,
            structured_data=structured_res.get("structured_data"),
            citations=citations,
            retrieved_chunks_count=len(citations),
            has_sufficient_context=not is_insufficient,
            model_info=model_info
        )

hybrid_query_service = HybridQueryService()
