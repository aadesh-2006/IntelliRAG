import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.models.user import User
from app.models.document import Document
from app.models.cricket import (
    CricketMatch,
    CricketInnings,
    CricketBattingPerformance,
    CricketBowlingPerformance,
)
from app.schemas.cricket import (
    CricketDetectionResponse,
    CricketMatchResponse,
    CricketInningsResponse,
    CricketBattingPerformanceResponse,
    CricketBowlingPerformanceResponse,
    CricketExtrasResponse,
    CricketValidationResponse,
    CricketMatchSummaryResponse,
    CricketMatchStatsResponse,
    CricketPlayerStatsResponse,
)
from app.services.cricket.detector import cricket_detector
from app.services.cricket.extractor import cricket_extractor
from app.services.cricket.validator import cricket_validator
from app.services.cricket.stats_service import cricket_stats_service
from app.services.cricket.summary_service import cricket_summary_service

class CricketService:
    def _get_user_document(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID
    ) -> Document:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.user_id == user.id
        )
        doc = db.execute(stmt).scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        return doc

    def detect_scorecard(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID
    ) -> CricketDetectionResponse:
        doc = self._get_user_document(db, user, document_id)
        return cricket_detector.detect(
            document_id=doc.id,
            extracted_text=doc.extracted_text,
            extracted_metadata=doc.extracted_metadata
        )

    def extract_and_store_scorecard(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID
    ) -> CricketMatchResponse:
        doc = self._get_user_document(db, user, document_id)

        if doc.status not in ("PROCESSED", "READY"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document must be processed before extracting cricket scorecard"
            )

        match_data = cricket_extractor.extract(
            document_id=doc.id,
            user_id=user.id,
            extracted_text=doc.extracted_text,
            extracted_metadata=doc.extracted_metadata
        )

        validation_result = cricket_validator.validate(match_data)

        existing_stmt = select(CricketMatch).where(CricketMatch.document_id == doc.id)
        existing_match = db.execute(existing_stmt).scalar_one_or_none()
        if existing_match:
            db.delete(existing_match)
            db.commit()

        meta = match_data.get("metadata", {})
        match = CricketMatch(
            id=uuid.uuid4(),
            document_id=doc.id,
            user_id=user.id,
            team_1=meta.get("team_1") or "Team 1",
            team_2=meta.get("team_2") or "Team 2",
            venue=meta.get("venue"),
            city=meta.get("city"),
            match_date=meta.get("match_date"),
            tournament=meta.get("tournament"),
            match_number=meta.get("match_number"),
            format=meta.get("format"),
            toss_winner=meta.get("toss_winner"),
            toss_decision=meta.get("toss_decision"),
            winner=meta.get("winner"),
            result_text=meta.get("result_text"),
            player_of_match=meta.get("player_of_match"),
            raw_metadata={"metadata": meta, "innings_count": len(match_data.get("innings", []))},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(match)
        db.flush()

        for inn_dict in match_data.get("innings", []):
            innings = CricketInnings(
                id=uuid.uuid4(),
                match_id=match.id,
                innings_number=inn_dict.get("innings_number", 1),
                team=inn_dict.get("team", "Unknown"),
                total_runs=inn_dict.get("total_runs", 0),
                wickets=inn_dict.get("wickets", 0),
                overs=inn_dict.get("overs", 20.0),
                run_rate=inn_dict.get("run_rate"),
                extras_wides=inn_dict.get("extras_wides", 0),
                extras_no_balls=inn_dict.get("extras_no_balls", 0),
                extras_byes=inn_dict.get("extras_byes", 0),
                extras_leg_byes=inn_dict.get("extras_leg_byes", 0),
                extras_penalty=inn_dict.get("extras_penalty", 0),
                extras_total=inn_dict.get("extras_total", 0),
                raw_metadata={"innings_number": inn_dict.get("innings_number"), "team": inn_dict.get("team")}
            )
            db.add(innings)
            db.flush()

            for b_dict in inn_dict.get("batting_performances", []):
                bat = CricketBattingPerformance(
                    id=uuid.uuid4(),
                    innings_id=innings.id,
                    player_name=b_dict.get("player_name", "Batsman"),
                    runs=b_dict.get("runs", 0),
                    balls=b_dict.get("balls", 0),
                    fours=b_dict.get("fours", 0),
                    sixes=b_dict.get("sixes", 0),
                    strike_rate=b_dict.get("strike_rate"),
                    dismissal=b_dict.get("dismissal"),
                    batting_position=b_dict.get("batting_position"),
                    source_page=b_dict.get("source_page"),
                    source_text=b_dict.get("source_text")
                )
                db.add(bat)

            for bowl_dict in inn_dict.get("bowling_performances", []):
                bowl = CricketBowlingPerformance(
                    id=uuid.uuid4(),
                    innings_id=innings.id,
                    player_name=bowl_dict.get("player_name", "Bowler"),
                    overs=bowl_dict.get("overs", 0.0),
                    maidens=bowl_dict.get("maidens", 0),
                    runs_conceded=bowl_dict.get("runs_conceded", 0),
                    wickets=bowl_dict.get("wickets", 0),
                    economy=bowl_dict.get("economy"),
                    wides=bowl_dict.get("wides"),
                    no_balls=bowl_dict.get("no_balls"),
                    source_page=bowl_dict.get("source_page"),
                    source_text=bowl_dict.get("source_text")
                )
                db.add(bowl)

        db.commit()
        db.refresh(match)

        return self.get_scorecard(db, user, document_id, validation_result=validation_result)

    def get_scorecard(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID,
        validation_result: Optional[CricketValidationResponse] = None
    ) -> CricketMatchResponse:
        self._get_user_document(db, user, document_id)

        stmt = (
            select(CricketMatch)
            .where(
                CricketMatch.document_id == document_id,
                CricketMatch.user_id == user.id
            )
            .options(
                joinedload(CricketMatch.innings)
                .joinedload(CricketInnings.batting_performances),
                joinedload(CricketMatch.innings)
                .joinedload(CricketInnings.bowling_performances)
            )
        )
        match = db.execute(stmt).unique().scalar_one_or_none()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cricket scorecard has not been extracted for this document"
            )

        if not validation_result:
            validation_result = cricket_validator.validate({
                "innings": [
                    {
                        "innings_number": inn.innings_number,
                        "team": inn.team,
                        "total_runs": inn.total_runs,
                        "wickets": inn.wickets,
                        "overs": inn.overs,
                        "extras_total": inn.extras_total,
                        "batting_performances": [
                            {"player_name": b.player_name, "runs": b.runs, "balls": b.balls, "fours": b.fours, "sixes": b.sixes}
                            for b in inn.batting_performances
                        ],
                        "bowling_performances": [
                            {"player_name": bw.player_name, "overs": bw.overs, "maidens": bw.maidens, "runs_conceded": bw.runs_conceded, "wickets": bw.wickets}
                            for bw in inn.bowling_performances
                        ]
                    }
                    for inn in match.innings
                ]
            })

        innings_responses: List[CricketInningsResponse] = []
        for inn in match.innings:
            bat_responses = [
                CricketBattingPerformanceResponse(
                    id=b.id,
                    player_name=b.player_name,
                    runs=b.runs,
                    balls=b.balls,
                    fours=b.fours,
                    sixes=b.sixes,
                    strike_rate=b.strike_rate,
                    dismissal=b.dismissal,
                    batting_position=b.batting_position,
                    source_page=b.source_page,
                    source_text=b.source_text
                )
                for b in inn.batting_performances
            ]

            bowl_responses = [
                CricketBowlingPerformanceResponse(
                    id=bw.id,
                    player_name=bw.player_name,
                    overs=bw.overs,
                    maidens=bw.maidens,
                    runs_conceded=bw.runs_conceded,
                    wickets=bw.wickets,
                    economy=bw.economy,
                    wides=bw.wides,
                    no_balls=bw.no_balls,
                    source_page=bw.source_page,
                    source_text=bw.source_text
                )
                for bw in inn.bowling_performances
            ]

            innings_responses.append(
                CricketInningsResponse(
                    id=inn.id,
                    innings_number=inn.innings_number,
                    team=inn.team,
                    total_runs=inn.total_runs,
                    wickets=inn.wickets,
                    overs=inn.overs,
                    run_rate=inn.run_rate,
                    extras=CricketExtrasResponse(
                        wides=inn.extras_wides,
                        no_balls=inn.extras_no_balls,
                        byes=inn.extras_byes,
                        leg_byes=inn.extras_leg_byes,
                        penalty=inn.extras_penalty,
                        total=inn.extras_total
                    ),
                    batting_performances=bat_responses,
                    bowling_performances=bowl_responses
                )
            )

        return CricketMatchResponse(
            id=match.id,
            document_id=match.document_id,
            team_1=match.team_1,
            team_2=match.team_2,
            venue=match.venue,
            city=match.city,
            match_date=match.match_date,
            tournament=match.tournament,
            match_number=match.match_number,
            format=match.format,
            toss_winner=match.toss_winner,
            toss_decision=match.toss_decision,
            winner=match.winner,
            result_text=match.result_text,
            player_of_match=match.player_of_match,
            innings=innings_responses,
            validation=validation_result,
            created_at=match.created_at,
            updated_at=match.updated_at
        )

    def get_match_statistics(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID
    ) -> CricketMatchStatsResponse:
        self._get_user_document(db, user, document_id)

        stmt = (
            select(CricketMatch)
            .where(
                CricketMatch.document_id == document_id,
                CricketMatch.user_id == user.id
            )
            .options(
                joinedload(CricketMatch.innings)
                .joinedload(CricketInnings.batting_performances),
                joinedload(CricketMatch.innings)
                .joinedload(CricketInnings.bowling_performances)
            )
        )
        match = db.execute(stmt).unique().scalar_one_or_none()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scorecard not found for this document"
            )

        return cricket_stats_service.get_match_statistics(match)

    def get_match_summary(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID
    ) -> CricketMatchSummaryResponse:
        self._get_user_document(db, user, document_id)

        stmt = (
            select(CricketMatch)
            .where(
                CricketMatch.document_id == document_id,
                CricketMatch.user_id == user.id
            )
            .options(
                joinedload(CricketMatch.innings)
                .joinedload(CricketInnings.batting_performances),
                joinedload(CricketMatch.innings)
                .joinedload(CricketInnings.bowling_performances)
            )
        )
        match = db.execute(stmt).unique().scalar_one_or_none()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scorecard not found for this document"
            )

        return cricket_summary_service.generate_summary(match)

    def get_player_statistics(
        self,
        db: Session,
        user: User,
        player_name: str
    ) -> CricketPlayerStatsResponse:
        return cricket_stats_service.get_player_statistics(db, user.id, player_name)

cricket_service = CricketService()
