import uuid
import pytest
from datetime import datetime, timezone
from fastapi import status

from app.models.document import Document
from app.models.cricket import CricketMatch, CricketInnings, CricketBattingPerformance, CricketBowlingPerformance
from app.services.cricket.normalizer import CricketNormalizer
from app.services.cricket.detector import cricket_detector
from app.services.cricket.extractor import cricket_extractor
from app.services.cricket.validator import cricket_validator
from app.services.cricket.stats_service import cricket_stats_service
from app.services.cricket.summary_service import cricket_summary_service
from tests.test_documents import create_test_user

def test_cricket_normalizer_overs_and_rates():
    assert CricketNormalizer.parse_overs_to_balls(10.3) == 63
    assert CricketNormalizer.parse_overs_to_balls("10.3") == 63
    assert CricketNormalizer.parse_overs_to_balls(20.0) == 120
    assert CricketNormalizer.parse_overs_to_balls(4) == 24
    assert CricketNormalizer.parse_overs_to_balls(0.5) == 5

    assert CricketNormalizer.balls_to_overs_float(63) == 10.3
    assert CricketNormalizer.balls_to_overs_float(120) == 20.0

    assert CricketNormalizer.calculate_economy(24, 4.0) == 6.0
    assert CricketNormalizer.calculate_economy(35, 3.3) == 10.0

    assert CricketNormalizer.calculate_strike_rate(82, 53) == 154.72
    assert CricketNormalizer.calculate_strike_rate(0, 0) == 0.0

    assert CricketNormalizer.is_not_out("not out") is True
    assert CricketNormalizer.is_not_out("dnb") is True
    assert CricketNormalizer.is_not_out("c Warner b Starc") is False
    assert CricketNormalizer.is_not_out("lbw b Bumrah") is False

def test_cricket_detector_scorecard_vs_general_document():
    doc_id = uuid.uuid4()
    scorecard_text = (
        "India vs Australia T20 Match Scorecard at MCG\n"
        "India won the toss and opted to bat\n"
        "Batting: Rohit Sharma c Smith b Starc 64 (42b, 7x4, 3x6) SR: 152.38\n"
        "Virat Kohli not out 82 (53b, 6x4, 4x6)\n"
        "Total: 185/4 (20.0 ov)\n"
        "Bowling: Pat Cummins 4.0 0 32 1\n"
        "Mitchell Starc 4.0 0 38 2\n"
        "India won by 15 runs. Player of the Match: Virat Kohli"
    )
    scorecard_meta = {
        "pages": [
            {
                "page_number": 1,
                "tables": [
                    {
                        "headers": ["Batsman", "Dismissal", "R", "B", "4s", "6s", "SR"],
                        "rows": [
                            ["Rohit Sharma", "c Smith b Starc", 64, 42, 7, 3, 152.38],
                            ["Virat Kohli", "not out", 82, 53, 6, 4, 154.72]
                        ]
                    },
                    {
                        "headers": ["Bowler", "O", "M", "R", "W", "Econ"],
                        "rows": [
                            ["Mitchell Starc", 4.0, 0, 38, 2, 9.5],
                            ["Pat Cummins", 4.0, 0, 32, 1, 8.0]
                        ]
                    }
                ]
            }
        ]
    }

    res_card = cricket_detector.detect(doc_id, scorecard_text, scorecard_meta)
    assert res_card.is_scorecard is True
    assert res_card.confidence >= 0.70
    assert len(res_card.signals) >= 3
    assert "India" in res_card.detected_teams or "Australia" in res_card.detected_teams

    general_text = "Quarterly financial invoice for enterprise cloud infrastructure services rendered in October."
    res_gen = cricket_detector.detect(doc_id, general_text, None)
    assert res_gen.is_scorecard is False
    assert res_gen.confidence < 0.30

def test_cricket_extractor_and_validator():
    doc_id = uuid.uuid4()
    user_id = uuid.uuid4()
    text = (
        "India vs Australia\n"
        "Venue: Melbourne Cricket Ground\n"
        "Date: 2026-11-15\n"
        "Tournament: ICC T20 World Cup\n"
        "India won the toss and elected to bat\n"
        "India won by 15 runs\n"
        "Player of the match: Virat Kohli"
    )
    meta = {
        "pages": [
            {
                "page_number": 1,
                "tables": [
                    {
                        "headers": ["Batsman", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"],
                        "rows": [
                            ["Rohit Sharma", "c Warner b Starc", "45", "30", "5", "2", "150.0"],
                            ["Virat Kohli", "not out", "82", "53", "6", "4", "154.7"],
                            ["Suryakumar Yadav", "c Maxwell b Cummins", "35", "18", "4", "2", "194.4"]
                        ]
                    },
                    {
                        "headers": ["Bowler", "Overs", "Maidens", "Runs", "Wickets", "Econ"],
                        "rows": [
                            ["Mitchell Starc", "4.0", "0", "36", "1", "9.0"],
                            ["Pat Cummins", "4.0", "0", "42", "1", "10.5"]
                        ]
                    }
                ]
            }
        ]
    }

    match_data = cricket_extractor.extract(doc_id, user_id, text, meta)
    assert match_data["metadata"]["team_1"] == "India"
    assert match_data["metadata"]["team_2"] == "Australia"
    assert match_data["metadata"]["toss_decision"] == "bat"
    assert match_data["metadata"]["winner"] == "India"
    assert match_data["metadata"]["player_of_match"] == "Virat Kohli"
    assert len(match_data["innings"]) >= 1

    first_inn = match_data["innings"][0]
    assert len(first_inn["batting_performances"]) == 3
    assert len(first_inn["bowling_performances"]) == 2
    assert first_inn["total_runs"] == 45 + 82 + 35

    val_res = cricket_validator.validate(match_data)
    assert val_res.is_valid is True
    assert len(val_res.errors) == 0

def test_cricket_validator_catches_inconsistencies():
    bad_data = {
        "innings": [
            {
                "innings_number": 1,
                "team": "Team A",
                "total_runs": -50,
                "wickets": 14,
                "overs": 20.9,
                "extras_total": 5,
                "batting_performances": [
                    {"player_name": "Player 1", "runs": -10, "balls": -5, "fours": 10, "sixes": 5}
                ],
                "bowling_performances": [
                    {"player_name": "Bowler 1", "overs": 4.0, "maidens": 0, "runs_conceded": -20, "wickets": 12}
                ]
            }
        ]
    }
    val = cricket_validator.validate(bad_data)
    assert val.is_valid is False
    assert len(val.errors) >= 3

def test_cricket_summary_service():
    user_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    match = CricketMatch(
        id=uuid.uuid4(),
        document_id=doc_id,
        user_id=user_id,
        team_1="India",
        team_2="Australia",
        tournament="ICC T20 World Cup",
        format="T20",
        venue="MCG",
        match_date="2026-11-15",
        toss_winner="India",
        toss_decision="bat",
        winner="India",
        result_text="India won by 15 runs",
        player_of_match="Virat Kohli"
    )
    inn = CricketInnings(
        id=uuid.uuid4(),
        match_id=match.id,
        innings_number=1,
        team="India",
        total_runs=185,
        wickets=4,
        overs=20.0,
        run_rate=9.25
    )
    bat = CricketBattingPerformance(
        id=uuid.uuid4(),
        innings_id=inn.id,
        player_name="Virat Kohli",
        runs=82,
        balls=53,
        fours=6,
        sixes=4,
        strike_rate=154.72
    )
    bowl = CricketBowlingPerformance(
        id=uuid.uuid4(),
        innings_id=inn.id,
        player_name="Mitchell Starc",
        overs=4.0,
        maidens=0,
        runs_conceded=36,
        wickets=2,
        economy=9.0
    )
    inn.batting_performances = [bat]
    inn.bowling_performances = [bowl]
    match.innings = [inn]

    summary_res = cricket_summary_service.generate_summary(match)
    assert summary_res.winner == "India"
    assert summary_res.player_of_match == "Virat Kohli"
    assert "India vs Australia" in summary_res.title
    assert "Virat Kohli" in summary_res.summary_text
    assert "185/4 in 20.0 overs" in summary_res.summary_text

def test_cricket_detect_endpoint(client, db_session):
    user, token = create_test_user("cricket_detect_user@intellirag.ai")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="match_scorecard.pdf",
        original_filename="Match_Scorecard.pdf",
        file_type="application/pdf",
        file_path="/storage/match_scorecard.pdf",
        file_size=2048,
        status="PROCESSED",
        document_type="GENERAL_DOCUMENT",
        extracted_text="India vs Australia T20 Match. India 185/4 (20.0 ov). Australia 170/8 (20.0 ov). India won by 15 runs. Player of the Match: Virat Kohli."
    )
    db_session.add(doc)
    db_session.commit()

    res = client.post(
        f"/api/cricket/documents/{doc.id}/detect",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["is_scorecard"] is True
    assert data["confidence"] > 0.40
    assert len(data["signals"]) > 0

def test_cricket_extract_and_get_endpoints(client, db_session):
    user, token = create_test_user("cricket_extract_user@intellirag.ai")
    scorecard_meta = {
        "pages": [
            {
                "page_number": 1,
                "tables": [
                    {
                        "headers": ["Batsman", "Dismissal", "R", "B", "4s", "6s", "SR"],
                        "rows": [
                            ["Rohit Sharma", "c Smith b Starc", 64, 42, 7, 3, 152.38],
                            ["Virat Kohli", "not out", 82, 53, 6, 4, 154.72]
                        ]
                    },
                    {
                        "headers": ["Bowler", "O", "M", "R", "W", "Econ"],
                        "rows": [
                            ["Mitchell Starc", 4.0, 0, 38, 2, 9.5],
                            ["Pat Cummins", 4.0, 0, 32, 1, 8.0]
                        ]
                    }
                ]
            }
        ]
    }
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="ipl_final.pdf",
        original_filename="IPL_Final.pdf",
        file_type="application/pdf",
        file_path="/storage/ipl_final.pdf",
        file_size=2048,
        status="PROCESSED",
        document_type="GENERAL_DOCUMENT",
        extracted_text="CSK vs MI Final at Wankhede. CSK won the toss and opted to bat. CSK won by 20 runs. Player of the Match: MS Dhoni.",
        extracted_metadata=scorecard_meta
    )
    db_session.add(doc)
    db_session.commit()

    extract_res = client.post(
        f"/api/cricket/documents/{doc.id}/extract",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert extract_res.status_code == status.HTTP_200_OK
    data = extract_res.json()
    assert data["document_id"] == str(doc.id)
    assert len(data["innings"]) >= 1
    assert data["validation"]["is_valid"] is True

    get_res = client.get(
        f"/api/cricket/documents/{doc.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["id"] == data["id"]

    stats_res = client.get(
        f"/api/cricket/documents/{doc.id}/statistics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert stats_res.status_code == status.HTTP_200_OK
    stats_data = stats_res.json()
    assert len(stats_data["top_scorers"]) >= 1
    assert len(stats_data["top_wicket_takers"]) >= 1

    sum_res = client.get(
        f"/api/cricket/documents/{doc.id}/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert sum_res.status_code == status.HTTP_200_OK
    assert "summary_text" in sum_res.json()

    player_res = client.get(
        "/api/cricket/players/Virat Kohli/statistics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert player_res.status_code == status.HTTP_200_OK
    p_data = player_res.json()
    assert p_data["player_name"] == "Virat Kohli"
    assert p_data["total_runs"] == 82
    assert p_data["fifties"] == 1

def test_cricket_unprocessed_document_extract_fails(client, db_session):
    user, token = create_test_user("cricket_unproc@intellirag.ai")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="raw.pdf",
        original_filename="Raw.pdf",
        file_type="application/pdf",
        file_path="/storage/raw.pdf",
        file_size=1024,
        status="UPLOADED"
    )
    db_session.add(doc)
    db_session.commit()

    res = client.post(
        f"/api/cricket/documents/{doc.id}/extract",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST

def test_cricket_user_isolation(client, db_session):
    user1, token1 = create_test_user("cricket_iso1@intellirag.ai")
    user2, token2 = create_test_user("cricket_iso2@intellirag.ai")

    doc1 = Document(
        id=uuid.uuid4(),
        user_id=user1.id,
        filename="private_scorecard.pdf",
        original_filename="Private_Scorecard.pdf",
        file_type="application/pdf",
        file_path="/storage/private_scorecard.pdf",
        file_size=1024,
        status="PROCESSED",
        extracted_text="India vs Pakistan. India won by 5 runs."
    )
    db_session.add(doc1)
    db_session.commit()

    res_user2 = client.post(
        f"/api/cricket/documents/{doc1.id}/detect",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert res_user2.status_code == status.HTTP_404_NOT_FOUND

    res_user2_extract = client.post(
        f"/api/cricket/documents/{doc1.id}/extract",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert res_user2_extract.status_code == status.HTTP_404_NOT_FOUND

def test_cricket_unauthenticated_access_rejected(client):
    doc_id = uuid.uuid4()
    res = client.get(f"/api/cricket/documents/{doc_id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
