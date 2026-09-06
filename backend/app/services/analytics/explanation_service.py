import json
from typing import Dict, Any, Optional
from app.schemas.analytics import AnalyticsIntent, AnalyticsResult
from app.services.llm_service import llm_service

class AnalyticsExplanationService:
    def explain(self, result: AnalyticsResult) -> str:
        if result.intent == AnalyticsIntent.UNSUPPORTED:
            if result.metric == "REJECTED":
                return "The query was rejected because it contains unsupported or potentially unsafe database commands. IntelliRAG only allows safe, read-only analytics operations."
            return "This query could not be resolved into a supported structured analytics operation on your workspace data."

        if not result.data and (result.total is None or result.total == 0):
            return self._build_empty_explanation(result)

        system_prompt = (
            "You are an AI Analytics Assistant for IntelliRAG. Your job is to explain the provided authoritative "
            "database result to answer the user's analytical question in clear, concise natural language.\n"
            "Rules:\n"
            "1. Base your answer strictly on the provided structured database result.\n"
            "2. Do not invent, assume, or calculate new numbers.\n"
            "3. The database facts are authoritative.\n"
            "4. Format the answer cleanly using markdown."
        )

        user_prompt = (
            f"User Question: {result.query}\n\n"
            f"=== STRUCTURED ANALYTICS DATA ===\n"
            f"Intent: {result.intent.value}\n"
            f"Metric: {result.metric}\n"
            f"Total: {result.total}\n"
            f"Unit: {result.unit}\n"
            f"Filters: {json.dumps(result.filters)}\n"
            f"Date Range: {json.dumps(result.date_range)}\n"
            f"Data:\n{json.dumps(result.data, indent=2)}\n"
            f"=== END STRUCTURED ANALYTICS DATA ===\n\n"
            "Please explain this structured result clearly to answer the user's question."
        )

        try:
            explanation = llm_service.generate(system_prompt=system_prompt, user_prompt=user_prompt)
            if explanation and len(explanation.strip()) > 0:
                return explanation.strip()
        except Exception:
            pass

        return self._build_deterministic_explanation(result)

    def _build_empty_explanation(self, result: AnalyticsResult) -> str:
        q_lower = result.query.lower()
        if "cricket" in q_lower or result.intent in [AnalyticsIntent.CRICKET_BATTING_ANALYSIS, AnalyticsIntent.CRICKET_BOWLING_ANALYSIS, AnalyticsIntent.CRICKET_MATCH_ANALYSIS]:
            return "No cricket statistics or scorecard records were found matching your query."
        elif result.intent == AnalyticsIntent.EXPIRATION_ANALYSIS:
            return "No active warranties, policies, or subscriptions matching your criteria are expiring in that timeframe."
        elif result.intent == AnalyticsIntent.REMINDER_ANALYSIS:
            return "You have no scheduled reminders matching the specified status or timeframe."
        return "No documents or structured records matching your criteria were found in your workspace."

    def _build_deterministic_explanation(self, result: AnalyticsResult) -> str:
        intent = result.intent
        data = result.data

        if intent == AnalyticsIntent.DOCUMENT_COUNT:
            val = result.total if result.total is not None else (data[0].get("value", 0) if data else 0)
            tf = result.date_range.get("label", "all-time") if result.date_range else "all-time"
            return f"You have **{int(val)}** document(s) in your workspace ({tf})."

        elif intent == AnalyticsIntent.DOCUMENT_BREAKDOWN:
            lines = [f"- **{d['document_type']}**: {d['count']} document(s)" for d in data]
            return f"You have **{int(result.total or 0)}** total document(s) broken down by type:\n\n" + "\n".join(lines)

        elif intent == AnalyticsIntent.DOCUMENT_STATUS_ANALYSIS:
            lines = [f"- **{d['status']}**: {d['count']} document(s)" for d in data]
            return f"Document status breakdown (**{int(result.total or 0)}** total):\n\n" + "\n".join(lines)

        elif intent == AnalyticsIntent.STORAGE_ANALYSIS:
            summary = data[0].get("summary", {}) if data else {}
            total_bytes = summary.get("total_size_bytes", 0)
            mb = total_bytes / (1024 * 1024)
            return f"Total storage used across **{summary.get('total_documents', 0)}** document(s) is **{mb:.2f} MB** ({total_bytes} bytes)."

        elif intent == AnalyticsIntent.EXPIRATION_ANALYSIS:
            lines = [
                f"- **{d['title']}**: due on {d['due_at'][:10]} ({d['days_until_due']} days, {d['reminder_type']})"
                for d in data[:10]
            ]
            return f"Found **{len(data)}** upcoming/actionable expiration(s):\n\n" + "\n".join(lines)

        elif intent == AnalyticsIntent.REMINDER_ANALYSIS:
            breakdown = data[0].get("status_breakdown", {}) if data else {}
            summary_str = ", ".join(f"{k}: {v}" for k, v in breakdown.items())
            return f"You have **{int(result.total or 0)}** reminder(s) ({summary_str})."

        elif intent == AnalyticsIntent.CRICKET_BATTING_ANALYSIS:
            if result.metric == "PLAYER_BATTING_CAREER" and data:
                p = data[0]
                return f"**{p['player_name']}**: {p['total_runs']} runs in {p['innings_count']} innings (SR: {p['strike_rate']}, Highest: {p['highest_score']})."
            lines = [f"- **{d['player_name']}**: {d['total_runs']} runs (SR: {d['strike_rate']}, HS: {d['highest_score']})" for d in data[:5]]
            return "Top cricket run scorers:\n\n" + "\n".join(lines)

        elif intent == AnalyticsIntent.CRICKET_BOWLING_ANALYSIS:
            if result.metric == "PLAYER_BOWLING_CAREER" and data:
                p = data[0]
                return f"**{p['player_name']}**: {p['total_wickets']} wickets in {p['total_overs']} overs (Econ: {p['economy']}, Runs: {p['runs_conceded']})."
            lines = [f"- **{d['player_name']}**: {d['total_wickets']} wickets ({d['total_overs']} overs, Econ: {d['economy']})" for d in data[:5]]
            return "Top cricket wicket takers:\n\n" + "\n".join(lines)

        elif intent == AnalyticsIntent.CRICKET_MATCH_ANALYSIS:
            summary = data[0].get("summary", {}) if data else {}
            return f"Found **{summary.get('total_matches', 0)}** cricket match scorecard(s) in your workspace."

        return f"Analytics query completed with {len(data)} record(s)."

analytics_explanation_service = AnalyticsExplanationService()
