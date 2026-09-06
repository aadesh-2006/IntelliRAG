import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, asc, and_, or_
from app.models.user import User
from app.models.document import Document
from app.models.reminder import Reminder
from app.models.cricket import CricketMatch, CricketInnings, CricketBattingPerformance, CricketBowlingPerformance
from app.schemas.analytics import AnalyticsIntent, AnalyticsResult

class SafeAnalyticsExecutor:
    def execute(
        self,
        db: Session,
        user: User,
        intent: AnalyticsIntent,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        if params.get("is_sanitized"):
            return self._build_result(
                query=query,
                intent=AnalyticsIntent.UNSUPPORTED,
                metric="REJECTED",
                filters=params.get("filters", {}),
                group_by=None,
                date_range=None,
                data=[],
                total=0,
                unit=None,
                start_time=start_time
            )

        if intent == AnalyticsIntent.DOCUMENT_COUNT:
            return self._execute_document_count(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.DOCUMENT_BREAKDOWN:
            return self._execute_document_breakdown(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.DOCUMENT_STATUS_ANALYSIS:
            return self._execute_document_status(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.DOCUMENT_DATE_RANGE:
            return self._execute_document_date_range(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.STORAGE_ANALYSIS:
            return self._execute_storage_analysis(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.EXPIRATION_ANALYSIS:
            return self._execute_expiration_analysis(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.REMINDER_ANALYSIS:
            return self._execute_reminder_analysis(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.CRICKET_BATTING_ANALYSIS:
            return self._execute_cricket_batting(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.CRICKET_BOWLING_ANALYSIS:
            return self._execute_cricket_bowling(db, user, params, query, start_time)
        elif intent == AnalyticsIntent.CRICKET_MATCH_ANALYSIS:
            return self._execute_cricket_match(db, user, params, query, start_time)
        else:
            return self._build_result(
                query=query,
                intent=AnalyticsIntent.UNSUPPORTED,
                metric="UNSUPPORTED",
                filters=params.get("filters", {}),
                group_by=None,
                date_range=params.get("date_range"),
                data=[],
                total=0,
                unit=None,
                start_time=start_time
            )

    def _execute_document_count(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        stmt = select(func.count(Document.id)).where(Document.user_id == user.id)
        filters = params.get("filters", {})
        if "document_type" in filters:
            stmt = stmt.where(Document.document_type == filters["document_type"])
        if "status" in filters:
            stmt = stmt.where(Document.status == filters["status"])

        dr = params.get("date_range")
        if dr:
            if dr.get("start_date"):
                st = datetime.datetime.fromisoformat(dr["start_date"])
                stmt = stmt.where(Document.created_at >= st)
            if dr.get("end_date"):
                et = datetime.datetime.fromisoformat(dr["end_date"])
                stmt = stmt.where(Document.created_at <= et)

        count = db.execute(stmt).scalar() or 0
        data = [{
            "metric": "document_count",
            "value": count,
            "document_type": filters.get("document_type", "ALL"),
            "status": filters.get("status", "ALL"),
            "timeframe": dr.get("label") if dr else "all-time"
        }]

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.DOCUMENT_COUNT,
            metric="COUNT",
            filters=filters,
            group_by=params.get("group_by"),
            date_range=dr,
            data=data,
            total=count,
            unit="documents",
            start_time=start_time
        )

    def _execute_document_breakdown(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        stmt = (
            select(
                Document.document_type,
                func.count(Document.id).label("count"),
                func.sum(Document.file_size).label("total_size")
            )
            .where(Document.user_id == user.id)
            .group_by(Document.document_type)
            .order_by(desc("count"))
        )
        rows = db.execute(stmt).all()
        data = [
            {
                "document_type": r[0],
                "count": r[1],
                "total_size_bytes": r[2] or 0
            }
            for r in rows
        ]
        total_count = sum(d["count"] for d in data)
        return self._build_result(
            query=query,
            intent=AnalyticsIntent.DOCUMENT_BREAKDOWN,
            metric="BREAKDOWN_BY_TYPE",
            filters=params.get("filters", {}),
            group_by="document_type",
            date_range=params.get("date_range"),
            data=data,
            total=total_count,
            unit="documents",
            start_time=start_time
        )

    def _execute_document_status(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        stmt = (
            select(
                Document.status,
                func.count(Document.id).label("count")
            )
            .where(Document.user_id == user.id)
            .group_by(Document.status)
            .order_by(desc("count"))
        )
        rows = db.execute(stmt).all()
        data = [
            {
                "status": r[0],
                "count": r[1]
            }
            for r in rows
        ]
        total_count = sum(d["count"] for d in data)
        return self._build_result(
            query=query,
            intent=AnalyticsIntent.DOCUMENT_STATUS_ANALYSIS,
            metric="BREAKDOWN_BY_STATUS",
            filters=params.get("filters", {}),
            group_by="status",
            date_range=params.get("date_range"),
            data=data,
            total=total_count,
            unit="documents",
            start_time=start_time
        )

    def _execute_document_date_range(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        dr = params.get("date_range")
        stmt = select(Document).where(Document.user_id == user.id)
        if dr:
            if dr.get("start_date"):
                st = datetime.datetime.fromisoformat(dr["start_date"])
                stmt = stmt.where(Document.created_at >= st)
            if dr.get("end_date"):
                et = datetime.datetime.fromisoformat(dr["end_date"])
                stmt = stmt.where(Document.created_at <= et)

        limit = params.get("limit", 10)
        docs = list(db.execute(stmt.order_by(desc(Document.created_at)).limit(limit)).scalars().all())

        count_stmt = select(func.count(Document.id)).where(Document.user_id == user.id)
        if dr:
            if dr.get("start_date"):
                st = datetime.datetime.fromisoformat(dr["start_date"])
                count_stmt = count_stmt.where(Document.created_at >= st)
            if dr.get("end_date"):
                et = datetime.datetime.fromisoformat(dr["end_date"])
                count_stmt = count_stmt.where(Document.created_at <= et)
        total_count = db.execute(count_stmt).scalar() or 0

        data = [
            {
                "id": str(d.id),
                "filename": d.original_filename,
                "document_type": d.document_type,
                "size_bytes": d.file_size,
                "status": d.status,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in docs
        ]

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.DOCUMENT_DATE_RANGE,
            metric="DATE_RANGE_LIST",
            filters=params.get("filters", {}),
            group_by=None,
            date_range=dr,
            data=data,
            total=total_count,
            unit="documents",
            start_time=start_time
        )

    def _execute_storage_analysis(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        agg_stmt = (
            select(
                func.count(Document.id).label("doc_count"),
                func.sum(Document.file_size).label("total_size"),
                func.avg(Document.file_size).label("avg_size"),
                func.min(Document.file_size).label("min_size"),
                func.max(Document.file_size).label("max_size")
            )
            .where(Document.user_id == user.id)
        )
        agg_row = db.execute(agg_stmt).first()
        doc_count = agg_row[0] or 0
        total_size = agg_row[1] or 0
        avg_size = float(agg_row[2]) if agg_row[2] is not None else 0.0
        min_size = agg_row[3] or 0
        max_size = agg_row[4] or 0

        breakdown_stmt = (
            select(
                Document.document_type,
                func.count(Document.id).label("count"),
                func.sum(Document.file_size).label("type_size")
            )
            .where(Document.user_id == user.id)
            .group_by(Document.document_type)
            .order_by(desc("type_size"))
        )
        breakdown_rows = db.execute(breakdown_stmt).all()

        data = [
            {
                "summary": {
                    "total_documents": doc_count,
                    "total_size_bytes": total_size,
                    "avg_size_bytes": round(avg_size, 2),
                    "min_size_bytes": min_size,
                    "max_size_bytes": max_size
                },
                "by_type": [
                    {
                        "document_type": r[0],
                        "count": r[1],
                        "size_bytes": r[2] or 0
                    }
                    for r in breakdown_rows
                ]
            }
        ]

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.STORAGE_ANALYSIS,
            metric="STORAGE_USAGE",
            filters=params.get("filters", {}),
            group_by="document_type",
            date_range=params.get("date_range"),
            data=data,
            total=total_size,
            unit="bytes",
            start_time=start_time
        )

    def _execute_expiration_analysis(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        stmt = select(Reminder).where(
            Reminder.user_id == user.id,
            Reminder.reminder_type.in_(["EXPIRY", "WARRANTY", "RENEWAL", "DUE_DATE", "DEADLINE"])
        )
        filters = params.get("filters", {})
        category = filters.get("category")
        if category:
            cat_pattern = f"%{category}%"
            stmt = stmt.where(
                or_(
                    Reminder.title.ilike(cat_pattern),
                    Reminder.description.ilike(cat_pattern)
                )
            )

        dr = params.get("date_range")
        if dr:
            if dr.get("start_date"):
                st = datetime.datetime.fromisoformat(dr["start_date"])
                stmt = stmt.where(Reminder.due_at >= st)
            if dr.get("end_date"):
                et = datetime.datetime.fromisoformat(dr["end_date"])
                stmt = stmt.where(Reminder.due_at <= et)

        reminders = list(db.execute(stmt.order_by(Reminder.due_at.asc())).scalars().all())
        now = datetime.datetime.now(datetime.timezone.utc)

        data = []
        for r in reminders:
            due_dt = r.due_at
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=datetime.timezone.utc)
            delta_days = (due_dt - now).days
            data.append({
                "id": str(r.id),
                "title": r.title,
                "reminder_type": r.reminder_type,
                "due_at": due_dt.isoformat(),
                "days_until_due": delta_days,
                "status": r.status,
                "document_id": str(r.document_id) if r.document_id else None
            })

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.EXPIRATION_ANALYSIS,
            metric="EXPIRING_ITEMS",
            filters=filters,
            group_by="reminder_type",
            date_range=dr,
            data=data,
            total=len(data),
            unit="items",
            start_time=start_time
        )

    def _execute_reminder_analysis(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        status_stmt = (
            select(
                Reminder.status,
                func.count(Reminder.id).label("count")
            )
            .where(Reminder.user_id == user.id)
            .group_by(Reminder.status)
        )
        status_rows = db.execute(status_stmt).all()
        status_counts = {r[0]: r[1] for r in status_rows}

        total_stmt = select(func.count(Reminder.id)).where(Reminder.user_id == user.id)
        filters = params.get("filters", {})
        if "reminder_status" in filters:
            total_stmt = total_stmt.where(Reminder.status == filters["reminder_status"])

        total_count = db.execute(total_stmt).scalar() or 0

        recent_stmt = select(Reminder).where(Reminder.user_id == user.id)
        if "reminder_status" in filters:
            recent_stmt = recent_stmt.where(Reminder.status == filters["reminder_status"])
        reminders = list(db.execute(recent_stmt.order_by(Reminder.due_at.asc()).limit(10)).scalars().all())

        data = [
            {
                "status_breakdown": status_counts,
                "total_reminders": total_count,
                "reminders": [
                    {
                        "id": str(r.id),
                        "title": r.title,
                        "status": r.status,
                        "type": r.reminder_type,
                        "due_at": r.due_at.isoformat() if r.due_at else None
                    }
                    for r in reminders
                ]
            }
        ]

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.REMINDER_ANALYSIS,
            metric="REMINDER_BREAKDOWN",
            filters=filters,
            group_by="status",
            date_range=params.get("date_range"),
            data=data,
            total=total_count,
            unit="reminders",
            start_time=start_time
        )

    def _execute_cricket_batting(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        filters = params.get("filters", {})
        player_name = filters.get("player_name")

        if player_name:
            stmt = (
                select(
                    func.count(CricketBattingPerformance.id).label("innings"),
                    func.sum(CricketBattingPerformance.runs).label("total_runs"),
                    func.sum(CricketBattingPerformance.balls).label("total_balls"),
                    func.sum(CricketBattingPerformance.fours).label("total_fours"),
                    func.sum(CricketBattingPerformance.sixes).label("total_sixes"),
                    func.max(CricketBattingPerformance.runs).label("highest_score"),
                    func.avg(CricketBattingPerformance.strike_rate).label("avg_sr")
                )
                .join(CricketInnings, CricketBattingPerformance.innings_id == CricketInnings.id)
                .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
                .where(
                    CricketMatch.user_id == user.id,
                    CricketBattingPerformance.player_name.ilike(f"%{player_name}%")
                )
            )
            row = db.execute(stmt).first()
            innings_count = row[0] or 0
            total_runs = row[1] or 0
            total_balls = row[2] or 0
            fours = row[3] or 0
            sixes = row[4] or 0
            highest_score = row[5] or 0
            avg_sr = float(row[6]) if row[6] is not None else 0.0

            sr = (total_runs / total_balls * 100.0) if total_balls > 0 else 0.0

            data = [{
                "player_name": player_name,
                "innings_count": innings_count,
                "total_runs": total_runs,
                "total_balls": total_balls,
                "fours": fours,
                "sixes": sixes,
                "highest_score": highest_score,
                "strike_rate": round(sr, 2)
            }]

            return self._build_result(
                query=query,
                intent=AnalyticsIntent.CRICKET_BATTING_ANALYSIS,
                metric="PLAYER_BATTING_CAREER",
                filters=filters,
                group_by="player_name",
                date_range=None,
                data=data,
                total=total_runs,
                unit="runs",
                start_time=start_time
            )

        limit = params.get("limit", 10)
        stmt = (
            select(
                CricketBattingPerformance.player_name,
                func.count(CricketBattingPerformance.id).label("innings"),
                func.sum(CricketBattingPerformance.runs).label("total_runs"),
                func.sum(CricketBattingPerformance.balls).label("total_balls"),
                func.sum(CricketBattingPerformance.fours).label("total_fours"),
                func.sum(CricketBattingPerformance.sixes).label("total_sixes"),
                func.max(CricketBattingPerformance.runs).label("highest_score")
            )
            .join(CricketInnings, CricketBattingPerformance.innings_id == CricketInnings.id)
            .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
            .where(CricketMatch.user_id == user.id)
            .group_by(CricketBattingPerformance.player_name)
            .order_by(desc("total_runs"))
            .limit(limit)
        )
        rows = db.execute(stmt).all()
        data = [
            {
                "player_name": r[0],
                "innings": r[1],
                "total_runs": r[2] or 0,
                "total_balls": r[3] or 0,
                "fours": r[4] or 0,
                "sixes": r[5] or 0,
                "highest_score": r[6] or 0,
                "strike_rate": round((r[2] / r[3] * 100.0), 2) if r[3] and r[3] > 0 else 0.0
            }
            for r in rows
        ]
        top_runs = data[0]["total_runs"] if data else 0

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.CRICKET_BATTING_ANALYSIS,
            metric="TOP_RUN_SCORERS",
            filters=filters,
            group_by="player_name",
            date_range=None,
            data=data,
            total=top_runs,
            unit="runs",
            start_time=start_time
        )

    def _execute_cricket_bowling(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        filters = params.get("filters", {})
        player_name = filters.get("player_name")

        if player_name:
            stmt = (
                select(
                    func.count(CricketBowlingPerformance.id).label("spells"),
                    func.sum(CricketBowlingPerformance.overs).label("total_overs"),
                    func.sum(CricketBowlingPerformance.maidens).label("total_maidens"),
                    func.sum(CricketBowlingPerformance.runs_conceded).label("total_runs"),
                    func.sum(CricketBowlingPerformance.wickets).label("total_wickets"),
                    func.avg(CricketBowlingPerformance.economy).label("avg_economy")
                )
                .join(CricketInnings, CricketBowlingPerformance.innings_id == CricketInnings.id)
                .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
                .where(
                    CricketMatch.user_id == user.id,
                    CricketBowlingPerformance.player_name.ilike(f"%{player_name}%")
                )
            )
            row = db.execute(stmt).first()
            spells = row[0] or 0
            overs = float(row[1]) if row[1] is not None else 0.0
            maidens = row[2] or 0
            runs_conceded = row[3] or 0
            wickets = row[4] or 0
            avg_econ = float(row[5]) if row[5] is not None else (runs_conceded / overs if overs > 0 else 0.0)

            data = [{
                "player_name": player_name,
                "innings_count": spells,
                "total_overs": round(overs, 1),
                "maidens": maidens,
                "runs_conceded": runs_conceded,
                "total_wickets": wickets,
                "economy": round(avg_econ, 2)
            }]

            return self._build_result(
                query=query,
                intent=AnalyticsIntent.CRICKET_BOWLING_ANALYSIS,
                metric="PLAYER_BOWLING_CAREER",
                filters=filters,
                group_by="player_name",
                date_range=None,
                data=data,
                total=wickets,
                unit="wickets",
                start_time=start_time
            )

        limit = params.get("limit", 10)
        stmt = (
            select(
                CricketBowlingPerformance.player_name,
                func.sum(CricketBowlingPerformance.wickets).label("total_wickets"),
                func.sum(CricketBowlingPerformance.runs_conceded).label("total_runs"),
                func.sum(CricketBowlingPerformance.overs).label("total_overs"),
                func.sum(CricketBowlingPerformance.maidens).label("total_maidens")
            )
            .join(CricketInnings, CricketBowlingPerformance.innings_id == CricketInnings.id)
            .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
            .where(CricketMatch.user_id == user.id)
            .group_by(CricketBowlingPerformance.player_name)
            .order_by(desc("total_wickets"))
            .limit(limit)
        )
        rows = db.execute(stmt).all()
        data = [
            {
                "player_name": r[0],
                "total_wickets": r[1] or 0,
                "runs_conceded": r[2] or 0,
                "total_overs": round(float(r[3]), 1) if r[3] is not None else 0.0,
                "maidens": r[4] or 0,
                "economy": round((r[2] / float(r[3])), 2) if r[3] and float(r[3]) > 0 else 0.0
            }
            for r in rows
        ]
        top_wickets = data[0]["total_wickets"] if data else 0

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.CRICKET_BOWLING_ANALYSIS,
            metric="TOP_WICKET_TAKERS",
            filters=filters,
            group_by="player_name",
            date_range=None,
            data=data,
            total=top_wickets,
            unit="wickets",
            start_time=start_time
        )

    def _execute_cricket_match(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        query: str,
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        count_stmt = select(func.count(CricketMatch.id)).where(CricketMatch.user_id == user.id)
        total_matches = db.execute(count_stmt).scalar() or 0

        winners_stmt = (
            select(
                CricketMatch.winner,
                func.count(CricketMatch.id).label("wins")
            )
            .where(CricketMatch.user_id == user.id, CricketMatch.winner.isnot(None))
            .group_by(CricketMatch.winner)
            .order_by(desc("wins"))
        )
        winner_rows = db.execute(winners_stmt).all()

        limit = params.get("limit", 10)
        matches = list(
            db.execute(
                select(CricketMatch)
                .where(CricketMatch.user_id == user.id)
                .order_by(desc(CricketMatch.created_at))
                .limit(limit)
            ).scalars().all()
        )

        data = [
            {
                "summary": {
                    "total_matches": total_matches,
                    "winners": [{"team": r[0], "wins": r[1]} for r in winner_rows]
                },
                "matches": [
                    {
                        "id": str(m.id),
                        "team_1": m.team_1,
                        "team_2": m.team_2,
                        "winner": m.winner,
                        "result_text": m.result_text,
                        "tournament": m.tournament,
                        "venue": m.venue,
                        "match_date": m.match_date
                    }
                    for m in matches
                ]
            }
        ]

        return self._build_result(
            query=query,
            intent=AnalyticsIntent.CRICKET_MATCH_ANALYSIS,
            metric="MATCH_SUMMARY",
            filters=params.get("filters", {}),
            group_by="winner",
            date_range=None,
            data=data,
            total=total_matches,
            unit="matches",
            start_time=start_time
        )

    def _build_result(
        self,
        query: str,
        intent: AnalyticsIntent,
        metric: str,
        filters: Dict[str, Any],
        group_by: Optional[str],
        date_range: Optional[Dict[str, Any]],
        data: List[Dict[str, Any]],
        total: Optional[float],
        unit: Optional[str],
        start_time: datetime.datetime
    ) -> AnalyticsResult:
        exec_ms = round((datetime.datetime.now(datetime.timezone.utc) - start_time).total_seconds() * 1000.0, 2)
        return AnalyticsResult(
            query=query,
            intent=intent,
            metric=metric,
            filters=filters,
            group_by=group_by,
            date_range=date_range,
            data=data,
            total=total,
            unit=unit,
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            execution_time_ms=exec_ms
        )

safe_analytics_executor = SafeAnalyticsExecutor()
