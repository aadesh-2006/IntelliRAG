from datetime import datetime, timezone
from typing import Dict, Any, List
from app.models.cricket import CricketMatch
from app.schemas.cricket import CricketMatchSummaryResponse
from app.services.cricket.normalizer import CricketNormalizer

class CricketSummaryService:
    def generate_summary(
        self,
        match: CricketMatch
    ) -> CricketMatchSummaryResponse:
        lines: List[str] = []
        highlights: List[str] = []

        header = f"{match.team_1} vs {match.team_2}"
        if match.tournament:
            header += f" ({match.tournament})"
        if match.format:
            header += f" - {match.format}"

        lines.append(header)

        info_parts = []
        if match.venue:
            info_parts.append(f"at {match.venue}")
        if match.match_date:
            info_parts.append(f"on {match.match_date}")
        if info_parts:
            lines.append("Played " + " ".join(info_parts) + ".")

        if match.toss_winner and match.toss_decision:
            lines.append(f"{match.toss_winner} won the toss and opted to {match.toss_decision}.")

        for inn in match.innings:
            inn_text = f"{inn.team} scored {inn.total_runs}/{inn.wickets} in {inn.overs} overs (RR: {inn.run_rate or 'N/A'})."

            top_bat = max(inn.batting_performances, key=lambda b: b.runs, default=None) if inn.batting_performances else None
            top_bowl = max(inn.bowling_performances, key=lambda bw: (bw.wickets, -bw.runs_conceded), default=None) if inn.bowling_performances else None

            details = []
            if top_bat and top_bat.runs > 0:
                details.append(f"{top_bat.player_name} top-scored with {top_bat.runs} ({top_bat.balls}b, {top_bat.fours}x4, {top_bat.sixes}x6)")
                highlights.append(f"{top_bat.player_name} ({inn.team}): {top_bat.runs} off {top_bat.balls} balls")

            if top_bowl and top_bowl.wickets > 0:
                details.append(f"{top_bowl.player_name} took {top_bowl.wickets}/{top_bowl.runs_conceded} in {top_bowl.overs} overs")
                highlights.append(f"{top_bowl.player_name}: {top_bowl.wickets}/{top_bowl.runs_conceded} ({top_bowl.overs} ov)")

            if details:
                inn_text += " " + ", while ".join(details) + "."

            lines.append(inn_text)

        if match.result_text:
            lines.append(f"Result: {match.result_text}")
        elif match.winner:
            lines.append(f"{match.winner} won the match.")

        if match.player_of_match:
            lines.append(f"Player of the Match: {match.player_of_match}.")
            highlights.append(f"Player of the Match: {match.player_of_match}")

        summary_text = " ".join(lines)

        return CricketMatchSummaryResponse(
            document_id=match.document_id,
            match_id=match.id,
            title=header,
            summary_text=summary_text,
            highlights=highlights,
            winner=match.winner,
            player_of_match=match.player_of_match,
            generated_at=datetime.now(timezone.utc)
        )

cricket_summary_service = CricketSummaryService()
