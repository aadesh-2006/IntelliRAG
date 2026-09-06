import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import status
from app.models.user import User
from app.models.document import Document
from app.models.reminder import Reminder
from app.services.date_extractor import date_extractor
from tests.test_documents import create_test_user

def test_date_extractor_actionable_patterns():
    text = (
        "This product comes with a 1-year limited warranty valid until 2026-12-31.\n"
        "Passport expiration date: 15/08/2028.\n"
        "Subscription renewal deadline is November 10, 2026.\n"
        "Invoice payment due date: 2026-05-20.\n"
        "Random printed document created on 2023-01-01."
    )
    candidates = date_extractor.extract_from_document_content(extracted_text=text)
    assert len(candidates) >= 4

    types = [c.type for c in candidates]
    assert "WARRANTY" in types
    assert "EXPIRY" in types
    assert "RENEWAL" in types
    assert "PAYMENT" in types

def test_date_extractor_with_metadata_pages_and_tables():
    metadata = {
        "pages": [
            {
                "page_number": 1,
                "text": "The contract expires on 2027-01-15.",
                "tables": [
                    {
                        "headers": ["Item", "Payment Due Date", "Amount"],
                        "rows": [
                            ["Cloud Hosting", "2026-11-30", "$120.00"]
                        ]
                    }
                ]
            }
        ]
    }
    candidates = date_extractor.extract_from_document_content(
        extracted_text="The contract expires on 2027-01-15.",
        extracted_metadata=metadata
    )
    assert len(candidates) >= 2
    types = [c.type for c in candidates]
    assert "RENEWAL" in types or "EXPIRY" in types
    assert "PAYMENT" in types

def test_create_reminder_endpoint(client):
    user, token = create_test_user("rem_user1@intellirag.ai")
    due = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    payload = {
        "title": "Cloud Subscription Renewal",
        "description": "Renew annual AWS commitment",
        "reminder_type": "RENEWAL",
        "due_at": due,
        "lead_time_days": 2
    }
    response = client.post(
        "/api/reminders",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Cloud Subscription Renewal"
    assert data["reminder_type"] == "RENEWAL"
    assert data["status"] == "PENDING"
    assert "remind_at" in data

def test_create_reminder_with_linked_document(client, db_session):
    user, token = create_test_user("rem_user2@intellirag.ai")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="server_lease.pdf",
        original_filename="Server_Lease_Agreement.pdf",
        file_type="application/pdf",
        file_path="/storage/server_lease.pdf",
        file_size=1024,
        status="PROCESSED",
        document_type="GENERAL_DOCUMENT",
        extracted_text="Warranty valid until 2027-06-30."
    )
    db_session.add(doc)
    db_session.commit()

    due = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    payload = {
        "document_id": str(doc.id),
        "title": "Hardware Warranty",
        "reminder_type": "WARRANTY",
        "due_at": due,
        "source_text": "Warranty valid until 2027-06-30.",
        "source_page": 1
    }
    response = client.post(
        "/api/reminders",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["document_id"] == str(doc.id)
    assert data["document_filename"] == "Server_Lease_Agreement.pdf"

def test_create_reminder_invalid_document_returns_404(client):
    user, token = create_test_user("rem_user3@intellirag.ai")
    payload = {
        "document_id": str(uuid.uuid4()),
        "title": "Fake Doc Reminder",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    }
    response = client.post(
        "/api/reminders",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_and_filter_reminders(client, db_session):
    user, token = create_test_user("rem_user4@intellirag.ai")
    now = datetime.now(timezone.utc)
    r1 = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Upcoming Expiry",
        reminder_type="EXPIRY",
        due_at=now + timedelta(days=5),
        remind_at=now + timedelta(days=3),
        status="PENDING"
    )
    r2 = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Overdue Bill",
        reminder_type="PAYMENT",
        due_at=now - timedelta(days=2),
        remind_at=now - timedelta(days=4),
        status="PENDING"
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    res_all = client.get("/api/reminders", headers=headers)
    assert res_all.status_code == status.HTTP_200_OK
    assert len(res_all.json()) >= 2

    res_type = client.get("/api/reminders?reminder_type=EXPIRY", headers=headers)
    assert res_type.status_code == status.HTTP_200_OK
    assert all(r["reminder_type"] == "EXPIRY" for r in res_type.json())

    res_upcoming = client.get("/api/reminders?upcoming=true", headers=headers)
    assert res_upcoming.status_code == status.HTTP_200_OK
    assert any(r["title"] == "Upcoming Expiry" for r in res_upcoming.json())

    res_overdue = client.get("/api/reminders?overdue=true", headers=headers)
    assert res_overdue.status_code == status.HTTP_200_OK
    assert any(r["title"] == "Overdue Bill" for r in res_overdue.json())

def test_get_update_complete_and_delete_reminder(client, db_session):
    user, token = create_test_user("rem_user5@intellirag.ai")
    rem = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Initial Title",
        reminder_type="CUSTOM",
        due_at=datetime.now(timezone.utc) + timedelta(days=10),
        remind_at=datetime.now(timezone.utc) + timedelta(days=8),
        status="PENDING"
    )
    db_session.add(rem)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    get_res = client.get(f"/api/reminders/{rem.id}", headers=headers)
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["title"] == "Initial Title"

    patch_res = client.patch(
        f"/api/reminders/{rem.id}",
        json={"title": "Updated Title", "status": "DUE"},
        headers=headers
    )
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.json()["title"] == "Updated Title"
    assert patch_res.json()["status"] == "DUE"

    complete_res = client.post(f"/api/reminders/{rem.id}/complete", headers=headers)
    assert complete_res.status_code == status.HTTP_200_OK
    assert complete_res.json()["status"] == "COMPLETED"
    assert complete_res.json()["completed_at"] is not None

    del_res = client.delete(f"/api/reminders/{rem.id}", headers=headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    get_again = client.get(f"/api/reminders/{rem.id}", headers=headers)
    assert get_again.status_code == status.HTTP_404_NOT_FOUND

def test_reminders_summary_endpoint(client, db_session):
    user, token = create_test_user("rem_user6@intellirag.ai")
    now = datetime.now(timezone.utc)
    r1 = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Active Warranty",
        reminder_type="WARRANTY",
        due_at=now + timedelta(days=15),
        remind_at=now + timedelta(days=10),
        status="PENDING"
    )
    r2 = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Completed Task",
        reminder_type="CUSTOM",
        due_at=now - timedelta(days=1),
        remind_at=now - timedelta(days=2),
        status="COMPLETED"
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/reminders/summary", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total_pending"] >= 1
    assert data["warranty_count"] >= 1
    assert data["completed_count"] >= 1
    assert data["next_reminder"] is not None

def test_process_due_reminders_endpoint(client, db_session):
    user, token = create_test_user("rem_user7@intellirag.ai")
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    rem = Reminder(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Due Reminder",
        reminder_type="EXPIRY",
        due_at=past + timedelta(days=1),
        remind_at=past,
        status="PENDING"
    )
    db_session.add(rem)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/reminders/process-due", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["processed_count"] >= 1

    db_session.refresh(rem)
    assert rem.status == "DUE"

def test_scan_document_actionable_dates_endpoint(client, db_session):
    user, token = create_test_user("rem_user8@intellirag.ai")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="contract.pdf",
        original_filename="Client_Contract.pdf",
        file_type="application/pdf",
        file_path="/storage/contract.pdf",
        file_size=2048,
        status="PROCESSED",
        document_type="GENERAL_DOCUMENT",
        extracted_text="Service renewal deadline is 2027-03-31.\nWarranty valid until 2026-10-15."
    )
    db_session.add(doc)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(f"/api/documents/{doc.id}/actionable-dates", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["document_id"] == str(doc.id)
    assert data["candidates_count"] >= 2
    types = [c["type"] for c in data["candidates"]]
    assert "RENEWAL" in types
    assert "WARRANTY" in types

def test_scan_unprocessed_document_fails(client, db_session):
    user, token = create_test_user("rem_user9@intellirag.ai")
    doc = Document(
        id=uuid.uuid4(),
        user_id=user.id,
        filename="pending.pdf",
        original_filename="Pending.pdf",
        file_type="application/pdf",
        file_path="/storage/pending.pdf",
        file_size=1024,
        status="UPLOADED",
        document_type="GENERAL_DOCUMENT"
    )
    db_session.add(doc)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(f"/api/documents/{doc.id}/actionable-dates", headers=headers)
    assert res.status_code == status.HTTP_400_BAD_REQUEST

def test_user_isolation_for_reminders(client, db_session):
    user1, token1 = create_test_user("user1_iso@intellirag.ai")
    user2, token2 = create_test_user("user2_iso@intellirag.ai")

    rem = Reminder(
        id=uuid.uuid4(),
        user_id=user2.id,
        title="Other User Secret Reminder",
        reminder_type="CUSTOM",
        due_at=datetime.now(timezone.utc) + timedelta(days=5),
        remind_at=datetime.now(timezone.utc) + timedelta(days=3),
        status="PENDING"
    )
    db_session.add(rem)
    db_session.commit()

    headers1 = {"Authorization": f"Bearer {token1}"}
    get_res = client.get(f"/api/reminders/{rem.id}", headers=headers1)
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

    patch_res = client.patch(f"/api/reminders/{rem.id}", json={"title": "Hacked"}, headers=headers1)
    assert patch_res.status_code == status.HTTP_404_NOT_FOUND

    del_res = client.delete(f"/api/reminders/{rem.id}", headers=headers1)
    assert del_res.status_code == status.HTTP_404_NOT_FOUND

    list_res = client.get("/api/reminders", headers=headers1)
    assert list_res.status_code == status.HTTP_200_OK
    assert not any(r["id"] == str(rem.id) for r in list_res.json())

def test_unauthenticated_reminders_access(client):
    assert client.get("/api/reminders").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/reminders/summary").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.post("/api/reminders", json={}).status_code == status.HTTP_401_UNAUTHORIZED
