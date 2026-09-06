import enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class AnalyticsIntent(str, enum.Enum):
    DOCUMENT_COUNT = "DOCUMENT_COUNT"
    DOCUMENT_BREAKDOWN = "DOCUMENT_BREAKDOWN"
    DOCUMENT_DATE_RANGE = "DOCUMENT_DATE_RANGE"
    DOCUMENT_STATUS_ANALYSIS = "DOCUMENT_STATUS_ANALYSIS"
    STORAGE_ANALYSIS = "STORAGE_ANALYSIS"
    EXPIRATION_ANALYSIS = "EXPIRATION_ANALYSIS"
    REMINDER_ANALYSIS = "REMINDER_ANALYSIS"
    CRICKET_BATTING_ANALYSIS = "CRICKET_BATTING_ANALYSIS"
    CRICKET_BOWLING_ANALYSIS = "CRICKET_BOWLING_ANALYSIS"
    CRICKET_MATCH_ANALYSIS = "CRICKET_MATCH_ANALYSIS"
    UNSUPPORTED = "UNSUPPORTED"

class DateRangeFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    timeframe_label: Optional[str] = None

class AnalyticsQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language analytical question")
    intent: Optional[AnalyticsIntent] = None
    date_range: Optional[DateRangeFilter] = None
    filters: Optional[Dict[str, Any]] = None

class AnalyticsResult(BaseModel):
    query: str
    intent: AnalyticsIntent
    metric: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    group_by: Optional[str] = None
    date_range: Optional[Dict[str, Any]] = None
    data: List[Dict[str, Any]] = Field(default_factory=list)
    total: Optional[Union[int, float]] = None
    unit: Optional[str] = None
    generated_at: str
    execution_time_ms: float

class AnalyticsQueryResponse(BaseModel):
    query: str
    intent: AnalyticsIntent
    metric: str
    structured_result: AnalyticsResult
    answer: str
    model_info: Optional[Dict[str, Any]] = None
    execution_time_ms: float
