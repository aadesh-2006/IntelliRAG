from typing import Dict, Any, List, Optional, Tuple
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.cricket import (
    CricketMatch,
    CricketInnings,
    CricketBattingPerformance,
    CricketBowlingPerformance,
)
from app.schemas.cricket import (
    CricketTopPerformer,
    CricketMatchStatsResponse,
    CricketPlayerStatsResponse,
)
from app.services.cricket.normalizer import CricketNormalizer

class CricketStatsService:
    def get_match_statistics(
        self,
        match: CricketMatch
    ) -> CricketMatchStatsResponse:
        top_scorers: List[CricketTopPerformer] = []
        top_wicket_takers: List[CricketTopPerformer] = []
        highest_strike_rates: List[CricketTopPerformer] = []
        best_economies: List[CricketTopPerformer] = []

        total_runs = 0
        total_wickets = 0
        total_fours = 0
        total_sixes = 0

        all_batsmen: List[Tuple[str, str, int, int, float, int, int]] = []
        all_bowlers: List[Tuple[str, str, float, int, int, float]] = []

        for inn in match.innings:
            total_runs += inn.total_runs
            total_wickets += inn.wickets

            for b in inn.batting_performances:
                total_fours += b.fours
                total_sixes += b.sixes
                sr = b.strike_rate or CricketNormalizer.calculate_strike_rate(b.runs, b.balls) or 0.0
                all_batsmen.append((b.player_name, inn.team, b.runs, b.balls, sr, b.fours, b.sixes))

            for bowl in inn.bowling_performances:
                econ = bowl.economy or CricketNormalizer.calculate_economy(bowl.runs_conceded, bowl.overs) or 0.0
                all_bowlers.append((bowl.player_name, inn.team, bowl.overs, bowl.runs_conceded, bowl.wickets, econ))

        all_batsmen.sort(key=lambda x: (x[2], -x[3]), reverse=True)
        for p in all_batsmen[:3]:
            top_scorers.append(CricketTopPerformer(
                player_name=p[0],
                team=p[1],
                metric_label="Runs",
                metric_value=f"{p[2]} ({p[3]}b)",
                subtext=f"SR: {p[4]} | 4s: {p[5]}, 6s: {p[6]}"
            ))

        all_bowlers.sort(key=lambda x: (x[4], -x[3]), reverse=True)
        for b in all_bowlers[:3]:
            top_wicket_takers.append(CricketTopPerformer(
                player_name=b[0],
                team=b[1],
                metric_label="Wickets",
                metric_value=f"{b[4]}/{b[3]}",
                subtext=f"{b[2]} ov, Econ: {b[5]}"
            ))

        qualified_sr = [b for b in all_batsmen if b[3] >= 5]
        qualified_sr.sort(key=lambda x: x[4], reverse=True)
        for p in qualified_sr[:3]:
            highest_strike_rates.append(CricketTopPerformer(
                player_name=p[0],
                team=p[1],
                metric_label="Strike Rate",
                metric_value=f"{p[4]}",
                subtext=f"{p[2]} runs off {p[3]} balls"
            ))

        qualified_econ = [b for b in all_bowlers if CricketNormalizer.parse_overs_to_balls(b[2]) >= 6]
        qualified_econ.sort(key=lambda x: x[5])
        for b in qualified_econ[:3]:
            best_economies.append(CricketTopPerformer(
                player_name=b[0],
                team=b[1],
                metric_label="Economy",
                metric_value=f"{b[5]}",
                subtext=f"{b[2]} ov, {b[4]} wkts for {b[3]} runs"
            ))

        return CricketMatchStatsResponse(
            document_id=match.document_id,
            match_id=match.id,
            top_scorers=top_scorers,
            top_wicket_takers=top_wicket_takers,
            highest_strike_rates=highest_strike_rates,
            best_economies=best_economies,
            total_match_runs=total_runs,
            total_match_wickets=total_wickets,
            total_boundaries_fours=total_fours,
            total_boundaries_sixes=total_sixes
        )

    def get_player_statistics(
        self,
        db: Session,
        user_id: uuid.UUID,
        player_name: str
    ) -> CricketPlayerStatsResponse:
        clean_name = player_name.strip().lower()

        bat_stmt = (
            select(CricketBattingPerformance, CricketMatch.id)
            .join(CricketInnings, CricketBattingPerformance.innings_id == CricketInnings.id)
            .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
            .where(CricketMatch.user_id == user_id)
        )
        all_bats = db.execute(bat_stmt).all()

        bowl_stmt = (
            select(CricketBowlingPerformance, CricketMatch.id)
            .join(CricketInnings, CricketBowlingPerformance.innings_id == CricketInnings.id)
            .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
            .where(CricketMatch.user_id == user_id)
        )
        all_bowls = db.execute(bowl_stmt).all()

        player_bats = [b[0] for b in all_bats if clean_name in b[0].player_name.lower()]
        player_bowls = [bw[0] for bw in all_bowls if clean_name in bw[0].player_name.lower()]

        match_ids = set()
        for b in all_bats:
            if clean_name in b[0].player_name.lower():
                match_ids.add(b[1])
        for bw in all_bowls:
            if clean_name in bw[0].player_name.lower():
                match_ids.add(bw[1])

        total_runs = sum(b.runs for b in player_bats)
        total_balls = sum(b.balls for b in player_bats)
        total_fours = sum(b.fours for b in player_bats)
        total_sixes = sum(b.sixes for b in player_bats)
        highest_score = max((b.runs for b in player_bats), default=0)
        fifties = sum(1 for b in player_bats if 50 <= b.runs < 100)
        hundreds = sum(1 for b in player_bats if b.runs >= 100)

        dismissals_count = sum(1 for b in player_bats if not CricketNormalizer.is_not_out(b.dismissal))
        batting_avg = round(total_runs / dismissals_count, 2) if dismissals_count > 0 else (float(total_runs) if total_runs > 0 else None)
        batting_sr = CricketNormalizer.calculate_strike_rate(total_runs, total_balls) if total_balls > 0 else None

        total_balls_bowled = sum(CricketNormalizer.parse_overs_to_balls(bw.overs) for bw in player_bowls)
        total_overs = CricketNormalizer.balls_to_overs_float(total_balls_bowled)
        total_wickets = sum(bw.wickets for bw in player_bowls)
        runs_conceded = sum(bw.runs_conceded for bw in player_bowls)

        bowling_avg = round(runs_conceded / total_wickets, 2) if total_wickets > 0 else None
        bowling_econ = CricketNormalizer.calculate_economy(runs_conceded, total_overs) if total_balls_bowled > 0 else None

        best_bw = None
        if player_bowls:
            sorted_bowls = sorted(player_bowls, key=lambda x: (x.wickets, -x.runs_conceded), reverse=True)
            best = sorted_bowls[0]
            best_bw = f"{best.wickets}/{best.runs_conceded} ({best.overs} ov)"

        return CricketPlayerStatsResponse(
            player_name=player_name,
            matches_count=len(match_ids),
            innings_batted=len(player_bats),
            total_runs=total_runs,
            highest_score=highest_score,
            batting_average=batting_avg,
            batting_strike_rate=batting_sr,
            fifties=fifties,
            hundreds=hundreds,
            total_fours=total_fours,
            total_sixes=total_sixes,
            innings_bowled=len(player_bowls),
            total_overs=total_overs,
            total_wickets=total_wickets,
            runs_conceded=runs_conceded,
            bowling_average=bowling_avg,
            bowling_economy=bowling_econ,
            best_bowling_figures=best_bw
        )

cricket_stats_service = CricketStatsService()
