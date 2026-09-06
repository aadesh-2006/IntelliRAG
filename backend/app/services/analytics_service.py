import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResponse, AnalyticsIntent, AnalyticsResult
from app.services.analytics.classifier import analytics_intent_classifier
from app.services.analytics.executor import safe_analytics_executor
from app.services.analytics.explanation_service import analytics_explanation_service
from app.services.llm_service import llm_service

class AnalyticsService:
    def query_analytics(
        self,
        db: Session,
        user: User,
        request: AnalyticsQueryRequest
    ) -> AnalyticsQueryResponse:
        start_time = datetime.datetime.now(datetime.timezone.utc)

        intent, params = analytics_intent_classifier.classify_and_extract(
            query=request.query,
            explicit_intent=request.intent,
            explicit_date_range=request.date_range,
            explicit_filters=request.filters
        )

        structured_result = safe_analytics_executor.execute(
            db=db,
            user=user,
            intent=intent,
            params=params,
            query=request.query,
            start_time=start_time
        )

        answer = analytics_explanation_service.explain(structured_result)

        exec_ms = round((datetime.datetime.now(datetime.timezone.utc) - start_time).total_seconds() * 1000.0, 2)

        return AnalyticsQueryResponse(
            query=request.query,
            intent=intent,
            metric=structured_result.metric,
            structured_result=structured_result,
            answer=answer,
            model_info={
                "provider": llm_service.provider_name,
                "model": llm_service.model_name
            },
            execution_time_ms=exec_ms
        )

analytics_service = AnalyticsService()
