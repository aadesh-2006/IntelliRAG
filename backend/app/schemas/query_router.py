from enum import Enum
from typing import Optional, List, Dict, Any
import uuid
from pydantic import BaseModel, Field
from app.schemas.rag import Citation

class RouteType(str, Enum):
    SQL = "SQL"
    RAG = "RAG"
    HYBRID = "HYBRID"

class QueryIntent(str, Enum):
    DOCUMENT_METADATA = "DOCUMENT_METADATA"
    DOCUMENT_DATES_EXPIRATION = "DOCUMENT_DATES_EXPIRATION"
    REMINDER_LOOKUP = "REMINDER_LOOKUP"
    CRICKET_STATISTICS = "CRICKET_STATISTICS"
    RAG_DOCUMENT_QUESTION = "RAG_DOCUMENT_QUESTION"
    DOCUMENT_COMPARISON = "DOCUMENT_COMPARISON"
    HYBRID_DOCUMENT_ANALYSIS = "HYBRID_DOCUMENT_ANALYSIS"
    UNSUPPORTED = "UNSUPPORTED"

class QueryClassification(BaseModel):
    route: RouteType
    intent: QueryIntent
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = None

class QueryRouterRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    document_ids: Optional[List[uuid.UUID]] = None
    document_type: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    force_route: Optional[RouteType] = None

class QueryRouterResponse(BaseModel):
    query: str
    route: RouteType
    intent: QueryIntent
    confidence: float
    answer: str
    structured_data: Optional[Dict[str, Any]] = None
    citations: Optional[List[Citation]] = None
    retrieved_chunks_count: int = 0
    has_sufficient_context: bool = True
    model_info: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
