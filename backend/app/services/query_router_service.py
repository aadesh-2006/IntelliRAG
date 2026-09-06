import time
from typing import Optional, List, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.query_router import (
    RouteType,
    QueryIntent,
    QueryClassification,
    QueryRouterRequest,
    QueryRouterResponse,
)
from app.schemas.rag import RAGQueryRequest
from app.services.query_router.classifier import QueryIntentClassifier, query_intent_classifier
from app.services.query_router.structured_service import StructuredDataService, structured_data_service
from app.services.query_router.hybrid_service import HybridQueryService, hybrid_query_service
from app.services.rag_service import RAGService, rag_service

class QueryRouterService:
    def __init__(
        self,
        classifier: Optional[QueryIntentClassifier] = None,
        structured_svc: Optional[StructuredDataService] = None,
        rag_svc: Optional[RAGService] = None,
        hybrid_svc: Optional[HybridQueryService] = None
    ):
        self.classifier = classifier or query_intent_classifier
        self.structured_service = structured_svc or structured_data_service
        self.rag_service = rag_svc or rag_service
        self.hybrid_service = hybrid_svc or hybrid_query_service

    def classify_query(self, query: str) -> QueryClassification:
        return self.classifier.classify(query)

    def route_and_execute(
        self,
        db: Session,
        user: User,
        request: QueryRouterRequest,
        history: Optional[List[Dict[str, str]]] = None
    ) -> QueryRouterResponse:
        start_time = time.perf_counter()
        cleaned_query = request.query.strip()
        if not cleaned_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query text cannot be empty or whitespace only"
            )

        classification = self.classify_query(cleaned_query)
        selected_route = request.force_route or classification.route

        if selected_route == RouteType.SQL:
            sql_res = self.structured_service.execute(
                db=db,
                user=user,
                classification=classification,
                request=request
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return QueryRouterResponse(
                query=cleaned_query,
                route=RouteType.SQL,
                intent=classification.intent,
                confidence=classification.confidence,
                answer=sql_res.get("answer", ""),
                structured_data=sql_res.get("structured_data"),
                citations=[],
                retrieved_chunks_count=0,
                has_sufficient_context=sql_res.get("has_sufficient_context", True),
                model_info={"provider": "database", "model": "sql_engine"},
                execution_time_ms=elapsed_ms
            )

        elif selected_route == RouteType.HYBRID:
            hybrid_res = self.hybrid_service.execute(
                db=db,
                user=user,
                classification=classification,
                request=request,
                history=history
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            hybrid_res.execution_time_ms = elapsed_ms
            return hybrid_res

        else:
            rag_req = RAGQueryRequest(
                query=cleaned_query,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold or 0.0,
                document_ids=request.document_ids,
                document_type=request.document_type
            )
            rag_res = self.rag_service.answer_query(
                db=db,
                user=user,
                request=rag_req,
                history=history
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return QueryRouterResponse(
                query=cleaned_query,
                route=RouteType.RAG,
                intent=classification.intent if classification.route == RouteType.RAG else QueryIntent.RAG_DOCUMENT_QUESTION,
                confidence=classification.confidence,
                answer=rag_res.answer,
                structured_data=None,
                citations=rag_res.citations,
                retrieved_chunks_count=rag_res.retrieved_chunks_count,
                has_sufficient_context=rag_res.has_sufficient_context,
                model_info=rag_res.model_info,
                execution_time_ms=elapsed_ms
            )

query_router_service = QueryRouterService()
