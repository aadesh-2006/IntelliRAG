import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.document import Document

class CricketMatch(Base):
    __tablename__ = "cricket_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    team_1: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    team_2: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    venue: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    match_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    tournament: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    match_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    format: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    toss_winner: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    toss_decision: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    winner: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    result_text: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    player_of_match: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    raw_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="cricket_matches"
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="cricket_match"
    )
    innings: Mapped[List["CricketInnings"]] = relationship(
        "CricketInnings",
        back_populates="match",
        cascade="all, delete-orphan",
        order_by="CricketInnings.innings_number"
    )

class CricketInnings(Base):
    __tablename__ = "cricket_innings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cricket_matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    innings_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    team: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    total_runs: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    wickets: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    overs: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    run_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    extras_wides: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    extras_no_balls: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    extras_byes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    extras_leg_byes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    extras_penalty: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    extras_total: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    raw_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )

    match: Mapped["CricketMatch"] = relationship(
        "CricketMatch",
        back_populates="innings"
    )
    batting_performances: Mapped[List["CricketBattingPerformance"]] = relationship(
        "CricketBattingPerformance",
        back_populates="innings",
        cascade="all, delete-orphan",
        order_by="CricketBattingPerformance.batting_position"
    )
    bowling_performances: Mapped[List["CricketBowlingPerformance"]] = relationship(
        "CricketBowlingPerformance",
        back_populates="innings",
        cascade="all, delete-orphan"
    )

class CricketBattingPerformance(Base):
    __tablename__ = "cricket_batting_performances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    innings_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cricket_innings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    player_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )
    runs: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    balls: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    fours: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    sixes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    strike_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    dismissal: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    batting_position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    source_page: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    source_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    innings: Mapped["CricketInnings"] = relationship(
        "CricketInnings",
        back_populates="batting_performances"
    )

class CricketBowlingPerformance(Base):
    __tablename__ = "cricket_bowling_performances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    innings_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cricket_innings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    player_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )
    overs: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    maidens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    runs_conceded: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    wickets: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    economy: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    wides: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    no_balls: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    source_page: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    source_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    innings: Mapped["CricketInnings"] = relationship(
        "CricketInnings",
        back_populates="bowling_performances"
    )
