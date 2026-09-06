import re
from typing import Dict, Any, List, Optional
from app.schemas.cricket import CricketDetectionResponse

class CricketScorecardDetector:
    KEYWORDS = [
        "batting", "bowling", "scorecard", "innings", "overs", "wickets",
        "maidens", "economy", "strike rate", "runs", "extras", "toss",
        "fall of wickets", "c & b", "lbw", "not out", "bowled", "caught",
        "leg byes", "no balls", "wides", "player of the match", "man of the match"
    ]

    TEAM_PATTERNS = [
        r"\b(India|Australia|England|South Africa|New Zealand|Pakistan|Sri Lanka|West Indies|Bangladesh|Afghanistan|Zimbabwe|Ireland|Scotland|Netherlands)\b",
        r"\b(CSK|MI|RCB|KKR|DC|RR|PBKS|SRH|LSG|GT|Chennai Super Kings|Mumbai Indians|Royal Challengers Bangalore|Kolkata Knight Riders|Delhi Capitals|Rajasthan Royals|Punjab Kings|Sunrisers Hyderabad|Lucknow Super Giants|Gujarat Titans)\b",
    ]

    def detect(
        self,
        document_id: Any,
        extracted_text: Optional[str] = None,
        extracted_metadata: Optional[Dict[str, Any]] = None
    ) -> CricketDetectionResponse:
        full_text = (extracted_text or "").lower()
        signals = []
        confidence_points = 0.0

        for kw in self.KEYWORDS:
            if kw in full_text:
                signals.append(f"Found keyword: '{kw}'")
                confidence_points += 0.05

        table_count = 0
        cricket_table_signals = 0
        if extracted_metadata and "pages" in extracted_metadata:
            for p in extracted_metadata["pages"]:
                for t in p.get("tables", []):
                    table_count += 1
                    headers = [str(h).lower() for h in t.get("headers", [])]
                    header_str = " ".join(headers)
                    if any(col in header_str for col in ["r", "b", "4s", "6s", "sr", "runs", "balls"]):
                        cricket_table_signals += 1
                        signals.append("Detected batting table layout")
                    if any(col in header_str for col in ["o", "m", "w", "econ", "overs", "maidens", "wickets"]):
                        cricket_table_signals += 1
                        signals.append("Detected bowling table layout")

        if cricket_table_signals > 0:
            confidence_points += min(0.4, cricket_table_signals * 0.15)

        batting_col_pattern = re.search(r"\b(player|batsman|batter)\s+(runs|r)\s+(balls|b)\b", full_text)
        if batting_col_pattern:
            confidence_points += 0.2
            signals.append("Matched standard batting columns regex")

        bowling_col_pattern = re.search(r"\b(bowler|bowling)\s+(overs|o)\s+(maidens|m)\s+(runs|r)\s+(wickets|w)\b", full_text)
        if bowling_col_pattern:
            confidence_points += 0.2
            signals.append("Matched standard bowling columns regex")

        score_pattern = re.search(r"\b\d+/\d+\s*\(?[0-9\.]+\s*ov", full_text)
        if score_pattern:
            confidence_points += 0.25
            signals.append("Matched cricket innings score pattern (e.g. 185/4 in 20.0 ov)")

        result_pattern = re.search(r"\bwon by\s+\d+\s+(?:runs|wickets)\b|\bwon the match\b", full_text)
        if result_pattern:
            confidence_points += 0.2
            signals.append("Matched cricket match result text")

        toss_pattern = re.search(r"\bwon the toss\b", full_text)
        if toss_pattern:
            confidence_points += 0.15
            signals.append("Matched toss decision statement")

        detected_teams = []
        for pat in self.TEAM_PATTERNS:
            matches = re.findall(pat, extracted_text or "", flags=re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0]
                m_str = m.strip()
                if m_str and m_str not in detected_teams:
                    detected_teams.append(m_str)

        if len(detected_teams) >= 2:
            confidence_points += 0.2
            signals.append(f"Detected potential match teams: {', '.join(detected_teams[:4])}")
        elif len(detected_teams) == 1:
            confidence_points += 0.08
            signals.append(f"Detected team: {detected_teams[0]}")

        final_confidence = min(0.99, round(confidence_points, 2))
        is_scorecard = final_confidence >= 0.40 or (cricket_table_signals >= 1 and len(signals) >= 3)

        if is_scorecard:
            summary = f"Identified as a cricket scorecard with {int(final_confidence * 100)}% confidence across {len(signals)} structural signals."
        else:
            summary = "Document does not exhibit sufficient cricket scorecard structure or statistics."

        return CricketDetectionResponse(
            document_id=document_id,
            is_scorecard=is_scorecard,
            confidence=final_confidence,
            signals=signals,
            detected_teams=detected_teams[:2],
            summary=summary
        )

cricket_detector = CricketScorecardDetector()
