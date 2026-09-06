import re
from typing import Dict, Any, Optional, Tuple
from app.schemas.analytics import AnalyticsIntent, DateRangeFilter
from app.services.analytics.date_parser import date_parser

class AnalyticsIntentClassifier:
    MALICIOUS_SQL_PATTERNS = [
        re.compile(r'\b(drop\s+table|delete\s+from|insert\s+into|update\s+\w+\s+set|truncate\s+table|alter\s+table|grant\s+|revoke\s+)\b', re.IGNORECASE),
        re.compile(r'(--|;\s*select|;\s*drop|;\s*delete|;\s*insert|union\s+select)', re.IGNORECASE),
        re.compile(r'\b(exec\s*\(|execute\s*\(|select\s+.*\s+from\s+users)\b', re.IGNORECASE),
        re.compile(r'\b(password|hash|admin\s+token)\b', re.IGNORECASE),
    ]

    STORAGE_PATTERNS = [
        re.compile(r'\b(storage|disk\s+space|disk\s+usage|file\s+size|storage\s+usage|storage\s+footprint|total\s+size|how\s+much\s+space|bytes|megabytes|gigabytes)\b', re.IGNORECASE),
    ]

    STATUS_PATTERNS = [
        re.compile(r'\b(processing\s+status|status\s+breakdown|which\s+documents\s+are\s+(still\s+)?(processing|failed|ready|uploaded)|failed\s+documents|processing\s+documents)\b', re.IGNORECASE),
    ]

    DATE_RANGE_PATTERNS = [
        re.compile(r'\b(uploaded\s+(today|yesterday|this\s+week|last\s+week|this\s+month|last\s+month|this\s+year|last\s+year|in\s+the\s+last|past))\b', re.IGNORECASE),
        re.compile(r'\b(documents?|files?|uploads?)\b.*\b(this\s+month|last\s+month|this\s+year|last\s+year|this\s+week|today)\b', re.IGNORECASE),
    ]

    BREAKDOWN_PATTERNS = [
        re.compile(r'\b(by\s+type|by\s+document\s+type|distribution\s+of\s+documents|breakdown\s+of\s+(documents|files)|how\s+many\s+(pdfs?|images?|csvs?|docx?|spreadsheets?|text\s+files?))\b', re.IGNORECASE),
    ]

    COUNT_PATTERNS = [
        re.compile(r'\b(how\s+many|count\s+of|total\s+number\s+of|total)\s+(documents?|files?|uploads?|items?)\b', re.IGNORECASE),
    ]

    EXPIRATION_PATTERNS = [
        re.compile(r'\b(warrant(y|ies)|insurance|policies|policy|subscriptions?|contracts?|leases?)\b.*\b(expire|expires|expiring|expiry|due|renew|renewal)\b', re.IGNORECASE),
        re.compile(r'\b(which|what)\b.*\b(expire|expires|expiring|expiry|due|renew)\b', re.IGNORECASE),
        re.compile(r'\b(expir(y|ies)|warrant(y|ies)|renewals?|due\s+dates?)\b.*\b(in\s+the\s+next|next\s+\d+\s+days|upcoming|overdue)\b', re.IGNORECASE),
    ]

    REMINDER_PATTERNS = [
        re.compile(r'\b(how\s+many|total|count|list|show)\b.*\b(reminders|scheduled\s+tasks|alerts)\b', re.IGNORECASE),
        re.compile(r'\b(pending|overdue|completed|due)\s+reminders\b', re.IGNORECASE),
        re.compile(r'^reminders?$', re.IGNORECASE),
    ]

    CRICKET_BATTING_PATTERNS = [
        re.compile(r'\b(batting\s+average|highest\s+runs|highest\s+score|most\s+runs|strike\s+rate|who\s+scored|top\s+run\s+scorer|batting\s+stats|batsman\s+stats|runs\s+scored)\b', re.IGNORECASE),
        re.compile(r'\b(fours|sixes|boundaries|half\s+centuries|centuries|runs)\b.*\b(scored|cricket|player)\b', re.IGNORECASE),
    ]

    CRICKET_BOWLING_PATTERNS = [
        re.compile(r'\b(bowling\s+average|most\s+wickets|highest\s+wickets|best\s+economy|best\s+bowler|wickets\s+taken|bowling\s+stats|bowler\s+stats|runs\s+conceded|maidens)\b', re.IGNORECASE),
    ]

    CRICKET_MATCH_PATTERNS = [
        re.compile(r'\b(cricket\s+match|cricket\s+scorecard|match\s+summary|match\s+result|who\s+won\s+the\s+match|cricket\s+tournament)\b', re.IGNORECASE),
    ]

    def classify_and_extract(
        self,
        query: str,
        explicit_intent: Optional[AnalyticsIntent] = None,
        explicit_date_range: Optional[DateRangeFilter] = None,
        explicit_filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[AnalyticsIntent, Dict[str, Any]]:
        cleaned = query.strip()
        params: Dict[str, Any] = {
            "metric": "COUNT",
            "filters": explicit_filters.copy() if explicit_filters else {},
            "group_by": None,
            "date_range": None,
            "limit": 10,
            "is_sanitized": False
        }

        if explicit_date_range:
            params["date_range"] = {
                "start_date": explicit_date_range.start_date,
                "end_date": explicit_date_range.end_date,
                "label": explicit_date_range.timeframe_label or "custom"
            }
        else:
            start_dt, end_dt, label = date_parser.parse_expression(cleaned)
            if start_dt or end_dt:
                params["date_range"] = {
                    "start_date": start_dt.isoformat() if start_dt else None,
                    "end_date": end_dt.isoformat() if end_dt else None,
                    "label": label
                }

        for pat in self.MALICIOUS_SQL_PATTERNS:
            if pat.search(cleaned):
                params["is_sanitized"] = True
                params["metric"] = "REJECTED"
                return AnalyticsIntent.UNSUPPORTED, params

        if explicit_intent:
            self._enrich_parameters(cleaned, explicit_intent, params)
            return explicit_intent, params

        for pat in self.STORAGE_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "SUM_SIZE"
                self._enrich_parameters(cleaned, AnalyticsIntent.STORAGE_ANALYSIS, params)
                return AnalyticsIntent.STORAGE_ANALYSIS, params

        for pat in self.STATUS_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "COUNT_BY_STATUS"
                params["group_by"] = "status"
                self._enrich_parameters(cleaned, AnalyticsIntent.DOCUMENT_STATUS_ANALYSIS, params)
                return AnalyticsIntent.DOCUMENT_STATUS_ANALYSIS, params

        for pat in self.EXPIRATION_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "EXPIRING_ITEMS"
                self._enrich_parameters(cleaned, AnalyticsIntent.EXPIRATION_ANALYSIS, params)
                return AnalyticsIntent.EXPIRATION_ANALYSIS, params

        for pat in self.REMINDER_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "REMINDER_COUNT"
                self._enrich_parameters(cleaned, AnalyticsIntent.REMINDER_ANALYSIS, params)
                return AnalyticsIntent.REMINDER_ANALYSIS, params

        for pat in self.CRICKET_BATTING_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "BATTING_METRICS"
                self._enrich_parameters(cleaned, AnalyticsIntent.CRICKET_BATTING_ANALYSIS, params)
                return AnalyticsIntent.CRICKET_BATTING_ANALYSIS, params

        for pat in self.CRICKET_BOWLING_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "BOWLING_METRICS"
                self._enrich_parameters(cleaned, AnalyticsIntent.CRICKET_BOWLING_ANALYSIS, params)
                return AnalyticsIntent.CRICKET_BOWLING_ANALYSIS, params

        for pat in self.CRICKET_MATCH_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "MATCH_METRICS"
                self._enrich_parameters(cleaned, AnalyticsIntent.CRICKET_MATCH_ANALYSIS, params)
                return AnalyticsIntent.CRICKET_MATCH_ANALYSIS, params

        for pat in self.DATE_RANGE_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "COUNT_IN_RANGE"
                self._enrich_parameters(cleaned, AnalyticsIntent.DOCUMENT_DATE_RANGE, params)
                return AnalyticsIntent.DOCUMENT_DATE_RANGE, params

        for pat in self.BREAKDOWN_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "COUNT_BY_TYPE"
                params["group_by"] = "document_type"
                self._enrich_parameters(cleaned, AnalyticsIntent.DOCUMENT_BREAKDOWN, params)
                return AnalyticsIntent.DOCUMENT_BREAKDOWN, params

        for pat in self.COUNT_PATTERNS:
            if pat.search(cleaned):
                params["metric"] = "COUNT"
                self._enrich_parameters(cleaned, AnalyticsIntent.DOCUMENT_COUNT, params)
                return AnalyticsIntent.DOCUMENT_COUNT, params

        if "cricket" in cleaned.lower() or "scorecard" in cleaned.lower():
            params["metric"] = "MATCH_METRICS"
            return AnalyticsIntent.CRICKET_MATCH_ANALYSIS, params

        if "document" in cleaned.lower() or "file" in cleaned.lower() or "upload" in cleaned.lower():
            params["metric"] = "COUNT"
            return AnalyticsIntent.DOCUMENT_COUNT, params

        return AnalyticsIntent.UNSUPPORTED, params

    def _enrich_parameters(self, query: str, intent: AnalyticsIntent, params: Dict[str, Any]) -> None:
        q_lower = query.lower()

        if "pdf" in q_lower:
            params["filters"]["document_type"] = "PDF"
        elif "image" in q_lower or "png" in q_lower or "jpg" in q_lower or "jpeg" in q_lower:
            params["filters"]["document_type"] = "IMAGE"
        elif "docx" in q_lower or "word" in q_lower:
            params["filters"]["document_type"] = "DOCX"
        elif "csv" in q_lower:
            params["filters"]["document_type"] = "CSV"
        elif "json" in q_lower:
            params["filters"]["document_type"] = "JSON"

        if "processing" in q_lower:
            params["filters"]["status"] = "PROCESSING"
        elif "failed" in q_lower:
            params["filters"]["status"] = "FAILED"
        elif "ready" in q_lower or "processed" in q_lower:
            params["filters"]["status"] = "PROCESSED"
        elif "uploaded" in q_lower:
            params["filters"]["status"] = "UPLOADED"

        if "overdue" in q_lower:
            params["filters"]["reminder_status"] = "OVERDUE"
        elif "pending" in q_lower:
            params["filters"]["reminder_status"] = "PENDING"
        elif "completed" in q_lower:
            params["filters"]["reminder_status"] = "COMPLETED"

        if "insurance" in q_lower or "policy" in q_lower or "policies" in q_lower:
            params["filters"]["category"] = "insurance"
        elif "subscription" in q_lower or "subscriptions" in q_lower:
            params["filters"]["category"] = "subscription"
        elif "warranty" in q_lower or "warranties" in q_lower:
            params["filters"]["category"] = "warranty"
        elif "contract" in q_lower or "contracts" in q_lower or "lease" in q_lower:
            params["filters"]["category"] = "contract"

        player_match = re.search(r'\b(?:for|by|of|is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', query)
        if player_match:
            params["filters"]["player_name"] = player_match.group(1).strip()

        limit_match = re.search(r'\b(?:top|limit|first)\s+(\d+)\b', q_lower)
        if limit_match:
            val = int(limit_match.group(1))
            params["limit"] = max(1, min(val, 100))

analytics_intent_classifier = AnalyticsIntentClassifier()
