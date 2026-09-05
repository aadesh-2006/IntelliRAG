import io
import uuid
import pytest
from app.core.security import hash_password, create_access_token
from app.models.user import User
from tests.conftest import TestingSessionLocal

def create_test_user(email: str) -> tuple[User, str]:
    db = TestingSessionLocal()
    user = User(
        email=email,
        password_hash=hash_password("Password123!")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.id)
    db.close()
    return user, token

def test_document_upload_success(client):
    user, token = create_test_user("docuser@intellirag.ai")
    file_content = b"%PDF-1.4 Mock PDF Document Content for testing"
    files = {"file": ("test_report.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"document_type": "INVOICE"}

    response = client.post(
        "/api/documents/upload",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["original_filename"] == "test_report.pdf"
    assert res_data["file_type"] == "application/pdf"
    assert res_data["document_type"] == "INVOICE"
    assert res_data["status"] == "UPLOADED"
    assert res_data["file_size"] == len(file_content)
    assert "id" in res_data
    assert res_data["user_id"] == str(user.id)

def test_document_upload_unsupported_extension(client):
    user, token = create_test_user("badext@intellirag.ai")
    file_content = b"Binary executable content"
    files = {"file": ("danger.exe", io.BytesIO(file_content), "application/octet-stream")}

    response = client.post(
        "/api/documents/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]

def test_list_documents_scoped_to_user(client):
    user1, token1 = create_test_user("user1@intellirag.ai")
    user2, token2 = create_test_user("user2@intellirag.ai")

    client.post(
        "/api/documents/upload",
        files={"file": ("doc1.txt", io.BytesIO(b"Hello user 1"), "text/plain")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    client.post(
        "/api/documents/upload",
        files={"file": ("doc2.txt", io.BytesIO(b"Hello user 2"), "text/plain")},
        headers={"Authorization": f"Bearer {token2}"}
    )

    res1 = client.get("/api/documents", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] == 1
    assert data1["items"][0]["original_filename"] == "doc1.txt"

    res2 = client.get("/api/documents", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total"] == 1
    assert data2["items"][0]["original_filename"] == "doc2.txt"

def test_get_document_by_id_and_isolation(client):
    user1, token1 = create_test_user("iso1@intellirag.ai")
    user2, token2 = create_test_user("iso2@intellirag.ai")

    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("confidential.pdf", io.BytesIO(b"%PDF content"), "application/pdf")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    doc_id = upload_res.json()["id"]

    res_owner = client.get(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token1}"})
    assert res_owner.status_code == 200
    assert res_owner.json()["id"] == doc_id

    res_other = client.get(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res_other.status_code == 404

def test_download_document_and_isolation(client):
    user1, token1 = create_test_user("down1@intellirag.ai")
    user2, token2 = create_test_user("down2@intellirag.ai")

    file_payload = b"Sample text content inside file for download"
    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("sample.txt", io.BytesIO(file_payload), "text/plain")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    doc_id = upload_res.json()["id"]

    dl_owner = client.get(f"/api/documents/{doc_id}/download", headers={"Authorization": f"Bearer {token1}"})
    assert dl_owner.status_code == 200
    assert dl_owner.content == file_payload

    dl_other = client.get(f"/api/documents/{doc_id}/download", headers={"Authorization": f"Bearer {token2}"})
    assert dl_other.status_code == 404

def test_delete_document_and_isolation(client):
    user1, token1 = create_test_user("del1@intellirag.ai")
    user2, token2 = create_test_user("del2@intellirag.ai")

    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("todelete.txt", io.BytesIO(b"Delete me"), "text/plain")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    doc_id = upload_res.json()["id"]

    del_other = client.delete(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token2}"})
    assert del_other.status_code == 404

    del_owner = client.delete(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token1}"})
    assert del_owner.status_code == 204

    get_again = client.get(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token1}"})
    assert get_again.status_code == 404

def test_unauthenticated_document_endpoints_rejected(client):
    fake_id = uuid.uuid4()
    assert client.get("/api/documents").status_code == 401
    assert client.post("/api/documents/upload").status_code == 401
    assert client.get(f"/api/documents/{fake_id}").status_code == 401
    assert client.get(f"/api/documents/{fake_id}/download").status_code == 401
    assert client.delete(f"/api/documents/{fake_id}").status_code == 401