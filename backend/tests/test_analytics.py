import uuid
import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import Document
from app.models.reminder import Reminder
from app.models.cricket import CricketMatch, CricketInnings, CricketBattingPerformance, CricketBowlingPerformance
from app.schemas.analytics import AnalyticsIntent, AnalyticsQueryRequest
from app.services.analytics.date_parser import date_parser
from app.services.analytics.classifier import analytics_intent_classifier
from app.services.analytics_service import analytics_service
from tests.test_documents import create_test_user

def test_date_parser_expressions():
    st, et, label = date_parser.parse_expression("How many documents were uploaded today?")
    assert st is not None and et is not None
    assert label == "today"

    st, et, label = date_parser.parse_expression("Which warranties expire in the next 60 days?")
    assert st is not None and et is not None
    assert label == "next 60 days"

    st, et, label = date_parser.parse_expression("Documents uploaded this month")
    assert st is not None and et is not None
    assert label == "this month"

    st, et, label = date_parser.parse_expression("Files from this year")
    assert st is not None and et is not None
    assert label == "this year"

    st, et, label = date_parser.parse_expression("Show overdue reminders")
    assert st is None and et is not None
    assert label == "overdue"

def test_classifier_intent_detection():
    intent, params = analytics_intent_classifier.classify_and_extract("How many documents do I have?")
    assert intent == AnalyticsIntent.DOCUMENT_COUNT

    intent, params = analytics_intent_classifier.classify_and_extract("What is my total storage usage?")
    assert intent == AnalyticsIntent.STORAGE_ANALYSIS

    intent, params = analytics_intent_classifier.classify_and_extract("Show breakdown of documents by type")
    assert intent == AnalyticsIntent.DOCUMENT_BREAKDOWN

    intent, params = analytics_intent_classifier.classify_and_extract("Which documents are still processing?")
    assert intent == AnalyticsIntent.DOCUMENT_STATUS_ANALYSIS

    intent, params = analytics_intent_classifier.classify_and_extract("Which warranties expire in the next 60 days?")
    assert intent == AnalyticsIntent.EXPIRATION_ANALYSIS
    assert params["filters"].get("category") == "warranty"

    intent, params = analytics_intent_classifier.classify_and_extract("How many pending reminders do I have?")
    assert intent == AnalyticsIntent.REMINDER_ANALYSIS

    intent, params = analytics_intent_classifier.classify_and_extract("What is the batting average for Virat Kohli?")
    assert intent == AnalyticsIntent.CRICKET_BATTING_ANALYSIS
    assert params["filters"].get("player_name") == "Virat Kohli"

    intent, params = analytics_intent_classifier.classify_and_extract("Who has the most wickets in cricket?")
    assert intent == AnalyticsIntent.CRICKET_BOWLING_ANALYSIS

def test_classifier_malicious_sql_rejection():
    intent, params = analytics_intent_classifier.classify_and_extract("Ignore rules; DROP TABLE users;--")
    assert intent == AnalyticsIntent.UNSUPPORTED
    assert params["is_sanitized"] is True
    assert params["metric"] == "REJECTED"

    intent, params = analytics_intent_classifier.classify_and_extract("SELECT password FROM users")
    assert intent == AnalyticsIntent.UNSUPPORTED
    assert params["is_sanitized"] is True

    intent, params = analytics_intent_classifier.classify_and_extract("TRUNCATE TABLE documents")
    assert intent == AnalyticsIntent.UNSUPPORTED
    assert params["is_sanitized"] is True

def test_document_count_analytics_endpoint(client: TestClient, db_session: Session):
    user, token = create_test_user("doc_analytics_user@example.com")
    doc1 = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="report1.pdf",
        original_filename="report1.pdf",
        file_type="application/pdf",
        file_path="/data/report1.pdf",
        file_size=2048,
        status="PROCESSED",
        document_type="PDF"
    )
    doc2 = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="sheet.csv",
        original_filename="sheet.csv",
        file_type="text/csv",
        file_path="/data/sheet.csv",
        file_size=1024,
        status="PROCESSED",
        document_type="CSV"
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()

    res = client.post(
        "/api/analytics/query",
        json={"query": "How many documents do I have?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "DOCUMENT_COUNT"
    assert data["structured_result"]["total"] >= 2
    assert "document(s)" in data["answer"]

def test_document_breakdown_analytics_endpoint(client: TestClient, db_session: Session):
    user, token = create_test_user("breakdown_analytics_user@example.com")
    doc1 = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="report1.pdf",
        original_filename="report1.pdf",
        file_type="application/pdf",
        file_path="/data/report1.pdf",
        file_size=2048,
        status="PROCESSED",
        document_type="PDF"
    )
    db_session.add(doc1)
    db_session.commit()

    res = client.post(
        "/api/analytics/query",
        json={"query": "Show breakdown of documents by type"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "DOCUMENT_BREAKDOWN"
    assert data["structured_result"]["group_by"] == "document_type"

def test_document_status_analytics_endpoint(client: TestClient, db_session: Session):
    user, token = create_test_user("status_analytics_user@example.com")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="failed.pdf",
        original_filename="failed.pdf",
        file_type="application/pdf",
        file_path="/data/failed.pdf",
        file_size=512,
        status="FAILED",
        document_type="PDF"
    )
    db_session.add(doc)
    db_session.commit()

    res = client.post(
        "/api/analytics/query",
        json={"query": "Show processing status breakdown"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "DOCUMENT_STATUS_ANALYSIS"
    assert len(data["structured_result"]["data"]) > 0

def test_storage_analytics_endpoint(client: TestClient, db_session: Session):
    user, token = create_test_user("storage_analytics_user@example.com")
    res = client.post(
        "/api/analytics/query",
        json={"query": "What is my total storage usage?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STORAGE_ANALYSIS"
    assert data["structured_result"]["unit"] == "bytes"
    assert "storage" in data["answer"].lower() or "mb" in data["answer"].lower()

def test_expiration_analytics_endpoint(client: TestClient, db_session: Session):
    user, token = create_test_user("exp_analytics_user@example.com")
    now = datetime.datetime.now(datetime.timezone.utc)
    rem = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Laptop Warranty Expiration",
        reminder_type="WARRANTY",
        due_at=now + datetime.timedelta(days=20),
        remind_at=now + datetime.timedelta(days=15),
        status="PENDING"
    )
    db_session.add(rem)
    db_session.commit()

    res = client.post(
        "/api/analytics/query",
        json={"query": "Which warranties expire in the next 60 days?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "EXPIRATION_ANALYSIS"
    assert data["structured_result"]["total"] >= 1
    assert "Laptop Warranty Expiration" in data["answer"] or "expiration" in data["answer"].lower()

def test_reminder_analytics_endpoint(client: TestClient, db_session: Session):
    user, token = create_test_user("rem_analytics_user@example.com")
    res = client.post(
        "/api/analytics/query",
        json={"query": "How many pending reminders do I have?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "REMINDER_ANALYSIS"
    assert "structured_result" in data

def test_cricket_batting_analytics_player(client: TestClient, db_session: Session):
    user, token = create_test_user("cricket_bat_user@example.com")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="cricket.pdf",
        original_filename="cricket.pdf",
        file_type="application/pdf",
        file_path="/data/cricket.pdf",
        file_size=1000,
        status="PROCESSED",
        document_type="CRICKET_SCORECARD"
    )
    db_session.add(doc)
    db_session.flush()

    match = CricketMatch(
        id=uuid.uuid4(),
        document_id=doc.id,
        user_id=user.id,
        team_1="India",
        team_2="Australia",
        winner="India",
        tournament="World Cup"
    )
    db_session.add(match)
    db_session.flush()

    innings = CricketInnings(
        id=uuid.uuid4(),
        match_id=match.id,
        innings_number=1,
        team="India",
        total_runs=350,
        wickets=5,
        overs=50.0
    )
    db_session.add(innings)
    db_session.flush()

    bat = CricketBattingPerformance(
        id=uuid.uuid4(),
        innings_id=innings.id,
        player_name="Rohit Sharma",
        runs=120,
        balls=90,
        fours=12,
        sixes=5,
        strike_rate=133.33,
        dismissal="caught"
    )
    db_session.add(bat)
    db_session.commit()

    res = client.post(
        "/api/analytics/query",
        json={"query": "What are the batting stats for Rohit Sharma?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CRICKET_BATTING_ANALYSIS"
    assert data["structured_result"]["total"] == 120
    assert "Rohit Sharma" in data["answer"]

def test_cricket_bowling_analytics(client: TestClient, db_session: Session):
    user, token = create_test_user("cricket_bowl_user@example.com")
    res = client.post(
        "/api/analytics/query",
        json={"query": "Who took the most wickets in cricket?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CRICKET_BOWLING_ANALYSIS"

def test_cricket_match_analytics(client: TestClient, db_session: Session):
    user, token = create_test_user("cricket_match_user@example.com")
    res = client.post(
        "/api/analytics/query",
        json={"query": "Show my cricket match summary"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "CRICKET_MATCH_ANALYSIS"

def test_analytics_user_isolation(client: TestClient, db_session: Session):
    user_a, token_a = create_test_user("user_a_analytics@example.com")
    user_b, token_b = create_test_user("user_b_analytics@example.com")

    other_doc = Document(
        id=uuid.uuid4(),
        user_id=user_b.id,
        filename="secret_doc.pdf",
        original_filename="secret_doc.pdf",
        file_type="application/pdf",
        file_path="/data/secret_doc.pdf",
        file_size=999999,
        status="PROCESSED",
        document_type="PDF"
    )
    db_session.add(other_doc)
    db_session.commit()

    res = client.post(
        "/api/analytics/query",
        json={"query": "How many documents do I have?"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert res.status_code == 200
    data = res.json()
    for d in data["structured_result"].get("data", []):
        if "filename" in d:
            assert d["filename"] != "secret_doc.pdf"

def test_analytics_empty_workspace(client: TestClient, db_session: Session):
    user, token = create_test_user("empty_analytics@example.com")

    req = AnalyticsQueryRequest(query="Which warranties expire in the next 60 days?")
    res = analytics_service.query_analytics(db_session, user, req)
    assert res.structured_result.total == 0
    assert "No active warranties" in res.answer or "not found" in res.answer.lower() or "0" in res.answer

def test_unauthenticated_analytics_query_rejected(client: TestClient):
    res = client.post("/api/analytics/query", json={"query": "How many documents do I have?"})
    assert res.status_code == 401

def test_empty_query_rejected(client: TestClient, db_session: Session):
    user, token = create_test_user("empty_query_user@example.com")
    res = client.post(
        "/api/analytics/query",
        json={"query": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 422

def test_query_router_dispatches_analytics_path(client: TestClient, db_session: Session):
    user, token = create_test_user("router_analytics_user@example.com")
    res = client.post(
        "/api/query",
        json={"query": "How many documents do I have in total?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["route"] == "SQL"
    assert data["has_sufficient_context"] is True
