import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class CricketDetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    is_scorecard: bool
    confidence: float
    signals: List[str]
    detected_teams: List[str]
    summary: str

class CricketBattingPerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_name: str
    runs: int
    balls: int
    fours: int
    sixes: int
    strike_rate: Optional[float] = None
    dismissal: Optional[str] = None
    batting_position: Optional[int] = None
    source_page: Optional[int] = None
    source_text: Optional[str] = None

class CricketBowlingPerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_name: str
    overs: float
    maidens: int
    runs_conceded: int
    wickets: int
    economy: Optional[float] = None
    wides: Optional[int] = None
    no_balls: Optional[int] = None
    source_page: Optional[int] = None
    source_text: Optional[str] = None

class CricketExtrasResponse(BaseModel):
    wides: int = 0
    no_balls: int = 0
    byes: int = 0
    leg_byes: int = 0
    penalty: int = 0
    total: int = 0

class CricketInningsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    innings_number: int
    team: str
    total_runs: int
    wickets: int
    overs: float
    run_rate: Optional[float] = None
    extras: CricketExtrasResponse
    batting_performances: List[CricketBattingPerformanceResponse]
    bowling_performances: List[CricketBowlingPerformanceResponse]

class CricketValidationResponse(BaseModel):
    is_valid: bool
    warnings: List[str]
    errors: List[str]

class CricketMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    team_1: str
    team_2: str
    venue: Optional[str] = None
    city: Optional[str] = None
    match_date: Optional[str] = None
    tournament: Optional[str] = None
    match_number: Optional[str] = None
    format: Optional[str] = None
    toss_winner: Optional[str] = None
    toss_decision: Optional[str] = None
    winner: Optional[str] = None
    result_text: Optional[str] = None
    player_of_match: Optional[str] = None
    innings: List[CricketInningsResponse]
    validation: Optional[CricketValidationResponse] = None
    created_at: datetime
    updated_at: datetime

class CricketMatchSummaryResponse(BaseModel):
    document_id: uuid.UUID
    match_id: uuid.UUID
    title: str
    summary_text: str
    highlights: List[str]
    winner: Optional[str] = None
    player_of_match: Optional[str] = None
    generated_at: datetime

class CricketTopPerformer(BaseModel):
    player_name: str
    team: str
    metric_label: str
    metric_value: str
    subtext: Optional[str] = None

class CricketMatchStatsResponse(BaseModel):
    document_id: uuid.UUID
    match_id: uuid.UUID
    top_scorers: List[CricketTopPerformer]
    top_wicket_takers: List[CricketTopPerformer]
    highest_strike_rates: List[CricketTopPerformer]
    best_economies: List[CricketTopPerformer]
    total_match_runs: int
    total_match_wickets: int
    total_boundaries_fours: int
    total_boundaries_sixes: int

class CricketPlayerStatsResponse(BaseModel):
    player_name: str
    matches_count: int
    innings_batted: int
    total_runs: int
    highest_score: int
    batting_average: Optional[float] = None
    batting_strike_rate: Optional[float] = None
    fifties: int
    hundreds: int
    total_fours: int
    total_sixes: int
    innings_bowled: int
    total_overs: float
    total_wickets: int
    runs_conceded: int
    bowling_average: Optional[float] = None
    bowling_economy: Optional[float] = None
    best_bowling_figures: Optional[str] = None
