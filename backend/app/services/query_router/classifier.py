import re
from typing import Dict, Any, Optional
from app.schemas.query_router import RouteType, QueryIntent, QueryClassification

class QueryIntentClassifier:
    SQL_INJECTION_PATTERNS = [
        re.compile(r'\b(drop\s+table|delete\s+from|insert\s+into|update\s+\w+\s+set|truncate\s+table|alter\s+table|grant\s+|revoke\s+)\b', re.IGNORECASE),
        re.compile(r'(--|;\s*select|;\s*drop|;\s*delete|;\s*insert|union\s+select)', re.IGNORECASE),
        re.compile(r'\b(exec\s*\(|execute\s*\()', re.IGNORECASE),
    ]

    EXPIRATION_PATTERNS = [
        re.compile(r'\b(when\s+does|when\s+do|when\s+is)\b.*\b(expire|expiring|expiry|due|renew|renewal)\b', re.IGNORECASE),
        re.compile(r'\b(expire|expires|expiring|expiry)\b.*\b(this\s+month|next\s+month|this\s+week|soon|upcoming|overdue)\b', re.IGNORECASE),
        re.compile(r'\b(which|what)\b.*\b(subscriptions?|policies|insurance|warrant(y|ies)|contracts?)\b.*\b(expire|expires|expiring|expiry|due)\b', re.IGNORECASE),
        re.compile(r'\b(upcoming|overdue|pending)\b.*\b(expir(y|ies)|renewals?|deadlines?|due\s+dates?)\b', re.IGNORECASE),
        re.compile(r'\b(warranty|guarantee)\b.*\b(valid|expire|expiry|until|end)\b', re.IGNORECASE),
    ]

    REMINDER_PATTERNS = [
        re.compile(r'\b(what|list|show|get|view|check)\b.*\b(my\s+)?(reminders|alerts|tasks|scheduled\s+items)\b', re.IGNORECASE),
        re.compile(r'\b(overdue|due|pending|completed)\b\s+(reminders|alerts)\b', re.IGNORECASE),
        re.compile(r'^reminders?$', re.IGNORECASE),
    ]

    METADATA_PATTERNS = [
        re.compile(r'\b(how\s+many|count\s+of|total\s+number\s+of)\b.*\b(documents?|files?|pdfs?|images?|uploads?|vault)\b', re.IGNORECASE),
        re.compile(r'\b(list|show|what)\b.*\b(my\s+)?(documents?|files?|uploaded\s+files?|vault\s+documents?)\b', re.IGNORECASE),
        re.compile(r'\b(status|size|storage)\s+(of|for)\s+(my\s+)?(documents?|files?|vault)\b', re.IGNORECASE),
        re.compile(r'\b(what|which)\s+documents?\s+(are|were)\s+(processed|ready|failed|uploaded)\b', re.IGNORECASE),
    ]

    CRICKET_PATTERNS = [
        re.compile(r'\b(cricket|scorecard|innings|batting|bowling|overs?|wickets?|strike\s+rate|economy\s+rate)\b', re.IGNORECASE),
        re.compile(r'\b(who\s+scored|top\s+scorer|highest\s+score|most\s+runs|most\s+wickets|best\s+bowler)\b', re.IGNORECASE),
        re.compile(r'\b(how\s+many\s+runs|how\s+many\s+wickets|player\s+stats|career\s+stats)\b', re.IGNORECASE),
        re.compile(r'\b(match\s+summary|match\s+result|who\s+won\s+the\s+match)\b', re.IGNORECASE),
    ]

    COMPARISON_PATTERNS = [
        re.compile(r'\b(compare|comparison|difference\s+between|versus|\bvs\b|contrasting)\b', re.IGNORECASE),
        re.compile(r'\b(how\s+do\s+.*\s+compare|which\s+is\s+better|pros\s+and\s+cons)\b', re.IGNORECASE),
    ]

    HYBRID_ANALYSIS_PATTERNS = [
        re.compile(r'\b(analyze|breakdown|evaluate)\b.*\b(and\s+explain|along\s+with|together\s+with)\b', re.IGNORECASE),
        re.compile(r'\b(summarize\s+the\s+(costs?|numbers?|metrics?|figures?))\b.*\b(and\s+(explain|describe|clarify))\b', re.IGNORECASE),
    ]

    def classify(self, query: str) -> QueryClassification:
        cleaned = query.strip()
        if not cleaned:
            return QueryClassification(
                route=RouteType.RAG,
                intent=QueryIntent.UNSUPPORTED,
                confidence=1.0,
                parameters={},
                reasoning="Empty query"
            )

        for pat in self.SQL_INJECTION_PATTERNS:
            if pat.search(cleaned):
                return QueryClassification(
                    route=RouteType.RAG,
                    intent=QueryIntent.RAG_DOCUMENT_QUESTION,
                    confidence=1.0,
                    parameters={"is_sanitized": True},
                    reasoning="Sanitized SQL injection pattern redirected to safe document question"
                )

        for pat in self.COMPARISON_PATTERNS:
            if pat.search(cleaned):
                params = self._extract_comparison_params(cleaned)
                return QueryClassification(
                    route=RouteType.HYBRID,
                    intent=QueryIntent.DOCUMENT_COMPARISON,
                    confidence=0.92,
                    parameters=params,
                    reasoning="Query requests comparative analysis across documents or items"
                )

        for pat in self.HYBRID_ANALYSIS_PATTERNS:
            if pat.search(cleaned):
                return QueryClassification(
                    route=RouteType.HYBRID,
                    intent=QueryIntent.HYBRID_DOCUMENT_ANALYSIS,
                    confidence=0.88,
                    parameters={},
                    reasoning="Query combines structured metric evaluation with semantic explanation"
                )

        for pat in self.EXPIRATION_PATTERNS:
            if pat.search(cleaned):
                params = self._extract_expiration_params(cleaned)
                return QueryClassification(
                    route=RouteType.SQL,
                    intent=QueryIntent.DOCUMENT_DATES_EXPIRATION,
                    confidence=0.95,
                    parameters=params,
                    reasoning="Query targets structured expiration/date facts"
                )

        for pat in self.REMINDER_PATTERNS:
            if pat.search(cleaned):
                params = self._extract_reminder_params(cleaned)
                return QueryClassification(
                    route=RouteType.SQL,
                    intent=QueryIntent.REMINDER_LOOKUP,
                    confidence=0.95,
                    parameters=params,
                    reasoning="Query targets user reminder records and task statuses"
                )

        for pat in self.CRICKET_PATTERNS:
            if pat.search(cleaned):
                params = self._extract_cricket_params(cleaned)
                return QueryClassification(
                    route=RouteType.SQL,
                    intent=QueryIntent.CRICKET_STATISTICS,
                    confidence=0.93,
                    parameters=params,
                    reasoning="Query targets structured cricket scorecard and player statistics"
                )

        for pat in self.METADATA_PATTERNS:
            if pat.search(cleaned):
                params = self._extract_metadata_params(cleaned)
                return QueryClassification(
                    route=RouteType.SQL,
                    intent=QueryIntent.DOCUMENT_METADATA,
                    confidence=0.94,
                    parameters=params,
                    reasoning="Query targets document repository metadata, counts, or statuses"
                )

        return QueryClassification(
            route=RouteType.RAG,
            intent=QueryIntent.RAG_DOCUMENT_QUESTION,
            confidence=0.85,
            parameters={},
            reasoning="Query requires semantic document comprehension and grounded retrieval"
        )

    def _extract_expiration_params(self, query: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        q_lower = query.lower()
        if "this month" in q_lower:
            params["timeframe"] = "THIS_MONTH"
        elif "next month" in q_lower:
            params["timeframe"] = "NEXT_MONTH"
        elif "this week" in q_lower:
            params["timeframe"] = "THIS_WEEK"
        elif "overdue" in q_lower:
            params["timeframe"] = "OVERDUE"
        else:
            params["timeframe"] = "ALL_UPCOMING"

        if "insurance" in q_lower or "policy" in q_lower or "policies" in q_lower:
            params["category"] = "insurance"
        elif "subscription" in q_lower or "subscriptions" in q_lower:
            params["category"] = "subscription"
        elif "warranty" in q_lower or "warranties" in q_lower:
            params["category"] = "warranty"
        elif "contract" in q_lower or "lease" in q_lower:
            params["category"] = "contract"
        return params

    def _extract_reminder_params(self, query: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        q_lower = query.lower()
        if "overdue" in q_lower:
            params["status"] = "OVERDUE"
        elif "due" in q_lower:
            params["status"] = "DUE"
        elif "completed" in q_lower:
            params["status"] = "COMPLETED"
        elif "pending" in q_lower:
            params["status"] = "PENDING"
        return params

    def _extract_metadata_params(self, query: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        q_lower = query.lower()
        if "pdf" in q_lower:
            params["document_type"] = "PDF"
        elif "csv" in q_lower:
            params["document_type"] = "CSV"
        elif "image" in q_lower or "png" in q_lower or "jpg" in q_lower:
            params["document_type"] = "IMAGE"
        elif "docx" in q_lower or "word" in q_lower:
            params["document_type"] = "DOCX"

        if "how many" in q_lower or "count" in q_lower or "total" in q_lower:
            params["aggregation"] = "COUNT"
        else:
            params["aggregation"] = "LIST"
        return params

    def _extract_cricket_params(self, query: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        q_lower = query.lower()
        if "top scorer" in q_lower or "most runs" in q_lower or "highest score" in q_lower:
            params["stat_type"] = "TOP_RUNS"
        elif "most wickets" in q_lower or "best bowler" in q_lower or "top wicket" in q_lower:
            params["stat_type"] = "TOP_WICKETS"
        elif "strike rate" in q_lower:
            params["stat_type"] = "TOP_STRIKE_RATE"
        elif "economy" in q_lower:
            params["stat_type"] = "BEST_ECONOMY"
        elif "summary" in q_lower or "result" in q_lower or "who won" in q_lower:
            params["stat_type"] = "MATCH_SUMMARY"

        player_match = re.search(r'\b(?:for|by|of|is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', query)
        if player_match:
            params["player_name"] = player_match.group(1).strip()
        return params

    def _extract_comparison_params(self, query: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        q_lower = query.lower()
        if "insurance" in q_lower or "policy" in q_lower or "policies" in q_lower:
            params["subject"] = "insurance_policies"
        elif "cricket" in q_lower or "scorecard" in q_lower or "match" in q_lower:
            params["subject"] = "cricket_matches"
        elif "warranty" in q_lower or "warranties" in q_lower:
            params["subject"] = "warranties"
        return params

query_intent_classifier = QueryIntentClassifier()
