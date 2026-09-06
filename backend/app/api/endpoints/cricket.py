import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.cricket import (
    CricketDetectionResponse,
    CricketMatchResponse,
    CricketMatchStatsResponse,
    CricketMatchSummaryResponse,
    CricketPlayerStatsResponse,
)
from app.services.cricket_service import cricket_service

router = APIRouter(prefix="/cricket", tags=["Cricket Scorecard AI"])

@router.post(
    "/documents/{document_id}/detect",
    response_model=CricketDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect if document is a cricket scorecard"
)
def detect_cricket_scorecard(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CricketDetectionResponse:
    return cricket_service.detect_scorecard(
        db=db,
        user=current_user,
        document_id=document_id
    )

@router.post(
    "/documents/{document_id}/extract",
    response_model=CricketMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract and store structured cricket scorecard"
)
def extract_cricket_scorecard(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CricketMatchResponse:
    return cricket_service.extract_and_store_scorecard(
        db=db,
        user=current_user,
        document_id=document_id
    )

@router.get(
    "/documents/{document_id}",
    response_model=CricketMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get extracted cricket scorecard"
)
def get_cricket_scorecard(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CricketMatchResponse:
    return cricket_service.get_scorecard(
        db=db,
        user=current_user,
        document_id=document_id
    )

@router.get(
    "/documents/{document_id}/statistics",
    response_model=CricketMatchStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get match-level cricket statistics"
)
def get_match_statistics(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CricketMatchStatsResponse:
    return cricket_service.get_match_statistics(
        db=db,
        user=current_user,
        document_id=document_id
    )

@router.get(
    "/documents/{document_id}/summary",
    response_model=CricketMatchSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get generated deterministic cricket match summary"
)
def get_match_summary(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CricketMatchSummaryResponse:
    return cricket_service.get_match_summary(
        db=db,
        user=current_user,
        document_id=document_id
    )

@router.get(
    "/players/{player_name}/statistics",
    response_model=CricketPlayerStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get cumulative player statistics across user's scorecards"
)
def get_player_statistics(
    player_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CricketPlayerStatsResponse:
    return cricket_service.get_player_statistics(
        db=db,
        user=current_user,
        player_name=player_name
    )
