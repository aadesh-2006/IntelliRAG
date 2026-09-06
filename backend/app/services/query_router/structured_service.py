import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, and_, or_
from app.models.user import User
from app.models.document import Document
from app.models.reminder import Reminder
from app.models.cricket import CricketMatch, CricketInnings, CricketBattingPerformance, CricketBowlingPerformance
from app.schemas.query_router import QueryClassification, QueryIntent, QueryRouterRequest

class StructuredDataService:
    def execute(
        self,
        db: Session,
        user: User,
        classification: QueryClassification,
        request: QueryRouterRequest
    ) -> Dict[str, Any]:
        intent = classification.intent
        params = classification.parameters

        if intent == QueryIntent.DOCUMENT_METADATA:
            return self._handle_document_metadata(db, user, params, request)
        elif intent == QueryIntent.DOCUMENT_DATES_EXPIRATION:
            return self._handle_document_expirations(db, user, params, request)
        elif intent == QueryIntent.REMINDER_LOOKUP:
            return self._handle_reminder_lookup(db, user, params, request)
        elif intent == QueryIntent.CRICKET_STATISTICS:
            return self._handle_cricket_statistics(db, user, params, request)
        else:
            return self._handle_generic_metadata(db, user, params, request)

    def _handle_document_metadata(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        request: QueryRouterRequest
    ) -> Dict[str, Any]:
        stmt = select(Document).where(Document.user_id == user.id)
        if request.document_ids:
            stmt = stmt.where(Document.id.in_(request.document_ids))
        if request.document_type:
            stmt = stmt.where(Document.document_type == request.document_type.upper())
        elif params.get("document_type"):
            stmt = stmt.where(Document.document_type == params["document_type"].upper())

        docs = list(db.execute(stmt.order_by(desc(Document.created_at))).scalars().all())

        if not docs:
            return {
                "answer": "You currently have no documents matching this criteria in your workspace vault.",
                "structured_data": {"total_documents": 0, "documents": []},
                "has_sufficient_context": True
            }

        total_count = len(docs)
        total_size = sum(d.file_size for d in docs)
        type_counts: Dict[str, int] = {}
        status_counts: Dict[str, int] = {}

        for d in docs:
            type_counts[d.document_type] = type_counts.get(d.document_type, 0) + 1
            status_counts[d.status] = status_counts.get(d.status, 0) + 1

        type_summary = ", ".join(f"{cnt} {t}" for t, cnt in sorted(type_counts.items()))
        status_summary = ", ".join(f"{cnt} {s}" for s, cnt in sorted(status_counts.items()))

        def format_bytes(b: int) -> str:
            if b < 1024:
                return f"{b} B"
            elif b < 1024 * 1024:
                return f"{b / 1024:.1f} KB"
            return f"{b / (1024 * 1024):.1f} MB"

        if params.get("aggregation") == "COUNT":
            answer = (
                f"You have {total_count} document(s) in your vault ({type_summary}) "
                f"with a total size of {format_bytes(total_size)}. "
                f"Current processing statuses: {status_summary}."
            )
        else:
            doc_lines = [
                f"- **{d.original_filename}** ({d.document_type}, {format_bytes(d.file_size)}, Status: {d.status})"
                for d in docs[:10]
            ]
            header = f"You have {total_count} document(s) in your vault ({type_summary}, total size: {format_bytes(total_size)}):"
            answer = header + "\n\n" + "\n".join(doc_lines)

        structured_data = {
            "total_documents": total_count,
            "total_size_bytes": total_size,
            "type_breakdown": type_counts,
            "status_breakdown": status_counts,
            "documents": [
                {
                    "id": str(d.id),
                    "filename": d.original_filename,
                    "type": d.document_type,
                    "size_bytes": d.file_size,
                    "status": d.status,
                    "created_at": d.created_at.isoformat() if d.created_at else ""
                }
                for d in docs[:20]
            ]
        }

        return {
            "answer": answer,
            "structured_data": structured_data,
            "has_sufficient_context": True
        }

    def _handle_document_expirations(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        request: QueryRouterRequest
    ) -> Dict[str, Any]:
        stmt = select(Reminder).where(
            Reminder.user_id == user.id,
            Reminder.reminder_type.in_(["EXPIRY", "WARRANTY", "RENEWAL", "DUE_DATE", "DEADLINE"])
        )

        category = params.get("category")
        if category:
            cat_filter = f"%{category}%"
            stmt = stmt.where(
                or_(
                    Reminder.title.ilike(cat_filter),
                    Reminder.description.ilike(cat_filter)
                )
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        timeframe = params.get("timeframe", "ALL_UPCOMING")

        if timeframe == "THIS_MONTH":
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_of_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                end_of_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            stmt = stmt.where(Reminder.due_at >= start_of_month, Reminder.due_at < end_of_month)
        elif timeframe == "THIS_WEEK":
            end_of_week = now + datetime.timedelta(days=7)
            stmt = stmt.where(Reminder.due_at >= now, Reminder.due_at <= end_of_week)
        elif timeframe == "OVERDUE":
            stmt = stmt.where(Reminder.due_at < now, Reminder.status != "COMPLETED")

        reminders = list(db.execute(stmt.order_by(Reminder.due_at.asc())).scalars().all())

        if not reminders:
            category_str = f" for '{category}'" if category else ""
            time_str = f" ({timeframe.lower().replace('_', ' ')})" if timeframe != "ALL_UPCOMING" else ""
            return {
                "answer": f"No active policy, warranty, or subscription expirations found{category_str}{time_str} in your documents.",
                "structured_data": {"expirations": []},
                "has_sufficient_context": True
            }

        lines = []
        for r in reminders:
            due_dt = r.due_at
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=datetime.timezone.utc)
            due_str = due_dt.strftime("%Y-%m-%d")
            delta_days = (due_dt - now).days
            if delta_days < 0:
                timing_str = f"**OVERDUE** by {abs(delta_days)} days"
            elif delta_days == 0:
                timing_str = "**TODAY**"
            else:
                timing_str = f"in {delta_days} days"
            lines.append(f"- **{r.title}**: expires/due on **{due_str}** ({timing_str}) [{r.reminder_type}]")

        answer = f"Found {len(reminders)} upcoming/actionable expiration(s):\n\n" + "\n".join(lines)

        structured_data = {
            "total_expirations": len(reminders),
            "expirations": [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "type": r.reminder_type,
                    "due_date": r.due_at.isoformat() if r.due_at else "",
                    "status": r.status,
                    "document_id": str(r.document_id) if r.document_id else None
                }
                for r in reminders
            ]
        }

        return {
            "answer": answer,
            "structured_data": structured_data,
            "has_sufficient_context": True
        }

    def _handle_reminder_lookup(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        request: QueryRouterRequest
    ) -> Dict[str, Any]:
        stmt = select(Reminder).where(Reminder.user_id == user.id)
        status_filter = params.get("status")
        if status_filter:
            stmt = stmt.where(Reminder.status == status_filter.upper())

        reminders = list(db.execute(stmt.order_by(Reminder.due_at.asc())).scalars().all())

        if not reminders:
            filter_str = f" with status '{status_filter}'" if status_filter else ""
            return {
                "answer": f"You have no scheduled reminders{filter_str}.",
                "structured_data": {"reminders": []},
                "has_sufficient_context": True
            }

        lines = []
        for r in reminders:
            due_dt = r.due_at
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=datetime.timezone.utc)
            due_str = due_dt.strftime("%Y-%m-%d %H:%M UTC")
            lines.append(f"- **{r.title}** ({r.reminder_type}): due on {due_str} | Status: `{r.status}`")

        answer = f"You have {len(reminders)} reminder(s):\n\n" + "\n".join(lines)
        structured_data = {
            "total_reminders": len(reminders),
            "reminders": [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "type": r.reminder_type,
                    "due_date": r.due_at.isoformat() if r.due_at else "",
                    "status": r.status
                }
                for r in reminders
            ]
        }

        return {
            "answer": answer,
            "structured_data": structured_data,
            "has_sufficient_context": True
        }

    def _handle_cricket_statistics(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        request: QueryRouterRequest
    ) -> Dict[str, Any]:
        player_name = params.get("player_name")
        stat_type = params.get("stat_type")

        if player_name:
            stmt = (
                select(CricketBattingPerformance)
                .join(CricketInnings, CricketBattingPerformance.innings_id == CricketInnings.id)
                .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
                .where(
                    CricketMatch.user_id == user.id,
                    CricketBattingPerformance.player_name.ilike(f"%{player_name}%")
                )
            )
            bat_entries = list(db.execute(stmt).scalars().all())

            bowl_stmt = (
                select(CricketBowlingPerformance)
                .join(CricketInnings, CricketBowlingPerformance.innings_id == CricketInnings.id)
                .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
                .where(
                    CricketMatch.user_id == user.id,
                    CricketBowlingPerformance.player_name.ilike(f"%{player_name}%")
                )
            )
            bowl_entries = list(db.execute(bowl_stmt).scalars().all())

            if not bat_entries and not bowl_entries:
                return {
                    "answer": f"No cricket performances found for player '{player_name}' in your processed scorecards.",
                    "structured_data": {"player_name": player_name, "found": False},
                    "has_sufficient_context": True
                }

            total_runs = sum(b.runs for b in bat_entries)
            total_balls = sum(b.balls for b in bat_entries)
            dismissals = sum(1 for b in bat_entries if b.dismissal_type and b.dismissal_type.upper() != "NOT OUT")
            avg = f"{total_runs / dismissals:.2f}" if dismissals > 0 else "N/A (undefeated)"
            sr = f"{(total_runs / total_balls) * 100.0:.2f}" if total_balls > 0 else "0.00"

            total_wickets = sum(bw.wickets for bw in bowl_entries)
            runs_conceded = sum(bw.runs_conceded for bw in bowl_entries)

            answer = (
                f"**Career Statistics for {player_name}**:\n"
                f"- **Innings Played**: {len(bat_entries)}\n"
                f"- **Total Runs**: {total_runs} (Balls: {total_balls})\n"
                f"- **Batting Average**: {avg}\n"
                f"- **Strike Rate**: {sr}\n"
                f"- **Wickets Taken**: {total_wickets} (Runs Conceded: {runs_conceded})"
            )

            structured_data = {
                "player_name": player_name,
                "innings_count": len(bat_entries),
                "total_runs": total_runs,
                "total_balls": total_balls,
                "batting_average": avg,
                "strike_rate": sr,
                "total_wickets": total_wickets,
                "runs_conceded": runs_conceded
            }

            return {
                "answer": answer,
                "structured_data": structured_data,
                "has_sufficient_context": True
            }

        if stat_type == "TOP_RUNS" or not stat_type:
            stmt = (
                select(CricketBattingPerformance, CricketMatch)
                .join(CricketInnings, CricketBattingPerformance.innings_id == CricketInnings.id)
                .join(CricketMatch, CricketInnings.match_id == CricketMatch.id)
                .where(CricketMatch.user_id == user.id)
                .order_by(desc(CricketBattingPerformance.runs))
                .limit(5)
            )
            top_batsmen = db.execute(stmt).all()
            if not top_batsmen:
                return {
                    "answer": "No cricket batting records found in your uploaded scorecards.",
                    "structured_data": {"top_batsmen": []},
                    "has_sufficient_context": True
                }

            lines = []
            batsmen_data = []
            for bp, match in top_batsmen:
                sr_str = f"{bp.strike_rate:.1f}" if bp.strike_rate is not None else "N/A"
                lines.append(f"- **{bp.player_name}**: **{bp.runs}** runs ({bp.balls} balls, SR: {sr_str}) in *{match.match_title or 'Match'}*")
                batsmen_data.append({
                    "player_name": bp.player_name,
                    "runs": bp.runs,
                    "balls": bp.balls,
                    "strike_rate": bp.strike_rate,
                    "match": match.match_title
                })

            answer = "Top cricket run scorers across your documents:\n\n" + "\n".join(lines)
            return {
                "answer": answer,
                "structured_data": {"top_scorers": batsmen_data},
                "has_sufficient_context": True
            }

        matches_stmt = select(CricketMatch).where(CricketMatch.user_id == user.id).order_by(desc(CricketMatch.created_at)).limit(5)
        matches = list(db.execute(matches_stmt).scalars().all())
        if not matches:
            return {
                "answer": "No cricket scorecards found in your workspace.",
                "structured_data": {"matches": []},
                "has_sufficient_context": True
            }

        lines = [f"- **{m.match_title or 'Cricket Match'}**: {m.result_description or 'Completed'} (Winner: {m.winner or 'N/A'})" for m in matches]
        answer = f"Found {len(matches)} cricket match scorecard(s):\n\n" + "\n".join(lines)
        return {
            "answer": answer,
            "structured_data": {"matches": [{"id": str(m.id), "title": m.match_title, "result": m.result_description} for m in matches]},
            "has_sufficient_context": True
        }

    def _handle_generic_metadata(
        self,
        db: Session,
        user: User,
        params: Dict[str, Any],
        request: QueryRouterRequest
    ) -> Dict[str, Any]:
        return self._handle_document_metadata(db, user, params, request)

structured_data_service = StructuredDataService()
