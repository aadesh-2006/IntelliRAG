import io
import uuid
import pytest
from tests.test_documents import create_test_user

def test_dashboard_stats_empty_workspace(client):
    user, token = create_test_user("dash_empty@intellirag.ai")

    res = client.get(
        "/api/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] == 0
    assert data["processed_documents"] == 0
    assert data["processing_documents"] == 0
    assert data["failed_documents"] == 0
    assert data["ready_documents"] == 0
    assert data["uploaded_documents"] == 0
    assert data["embedding_documents"] == 0
    assert data["total_chunks"] == 0
    assert data["total_storage_bytes"] == 0
    assert data["documents_by_status"]["UPLOADED"] == 0
    assert data["recent_documents"] == []

def test_dashboard_stats_aggregation_across_statuses_and_types(client):
    user, token = create_test_user("dash_agg@intellirag.ai")

    f1 = {"file": ("invoice1.txt", io.BytesIO(b"# Invoice\n\nTotal due: $1500.00."), "text/plain")}
    up1 = client.post("/api/documents/upload", files=f1, data={"document_type": "INVOICE"}, headers={"Authorization": f"Bearer {token}"})
    d1_id = up1.json()["id"]
    client.post(f"/api/documents/{d1_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{d1_id}/embed", headers={"Authorization": f"Bearer {token}"})

    f2 = {"file": ("balance.csv", io.BytesIO(b"Asset,Value\nCash,5000\n"), "text/csv")}
    up2 = client.post("/api/documents/upload", files=f2, data={"document_type": "BALANCE_SHEET"}, headers={"Authorization": f"Bearer {token}"})
    d2_id = up2.json()["id"]
    client.post(f"/api/documents/{d2_id}/process", headers={"Authorization": f"Bearer {token}"})

    f3 = {"file": ("raw.txt", io.BytesIO(b"# Raw document\n\nOnly uploaded content."), "text/plain")}
    up3 = client.post("/api/documents/upload", files=f3, data={"document_type": "GENERAL"}, headers={"Authorization": f"Bearer {token}"})

    res = client.get(
        "/api/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] == 3
    assert data["ready_documents"] == 1
    assert data["processed_documents"] == 1
    assert data["uploaded_documents"] == 1
    assert data["total_chunks"] > 0
    assert data["total_storage_bytes"] > 0

    assert data["documents_by_status"]["READY"] == 1
    assert data["documents_by_status"]["PROCESSED"] == 1
    assert data["documents_by_status"]["UPLOADED"] == 1

    assert data["documents_by_type"]["INVOICE"] == 1
    assert data["documents_by_type"]["BALANCE_SHEET"] == 1
    assert data["documents_by_type"]["GENERAL"] == 1

    assert "text/plain" in data["documents_by_file_type"]
    assert "text/csv" in data["documents_by_file_type"]

    assert len(data["recent_documents"]) == 3
    filenames = [d["original_filename"] for d in data["recent_documents"]]
    assert "raw.txt" in filenames
    assert "invoice1.txt" in filenames
    assert "balance.csv" in filenames

def test_dashboard_stats_cross_user_isolation(client):
    user1, token1 = create_test_user("dash_user1@intellirag.ai")
    user2, token2 = create_test_user("dash_user2@intellirag.ai")

    f1 = {"file": ("user1_doc.txt", io.BytesIO(b"# Private\n\nUser 1 content."), "text/plain")}
    client.post("/api/documents/upload", files=f1, headers={"Authorization": f"Bearer {token1}"})

    res1 = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    assert res1.json()["total_documents"] == 1

    res2 = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 200
    assert res2.json()["total_documents"] == 0
    assert res2.json()["total_storage_bytes"] == 0
    assert res2.json()["recent_documents"] == []

def test_dashboard_stats_unauthenticated_rejected(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 401
