import io
import uuid
import pytest
from tests.test_documents import create_test_user

def test_create_and_list_conversations(client):
    user, token = create_test_user("conv_user1@intellirag.ai")

    create_res1 = client.post(
        "/api/conversations",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_res1.status_code == 201
    c1 = create_res1.json()
    assert c1["title"] == "New Conversation"
    assert c1["message_count"] == 0

    create_res2 = client.post(
        "/api/conversations",
        json={"title": "Custom Analysis"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_res2.status_code == 201
    c2 = create_res2.json()
    assert c2["title"] == "Custom Analysis"

    list_res = client.get(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_res.status_code == 200
    conversations = list_res.json()
    assert len(conversations) == 2
    titles = [c["title"] for c in conversations]
    assert "New Conversation" in titles
    assert "Custom Analysis" in titles

def test_get_conversation_details_and_messages(client):
    user, token = create_test_user("conv_user2@intellirag.ai")

    create_res = client.post(
        "/api/conversations",
        json={"title": "Detail Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = create_res.json()["id"]

    get_res = client.get(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == conv_id
    assert data["title"] == "Detail Test"
    assert data["messages"] == []

def test_delete_conversation(client):
    user, token = create_test_user("conv_user3@intellirag.ai")

    create_res = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = create_res.json()["id"]

    del_res = client.delete(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert del_res.status_code == 204

    get_res = client.get(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_res.status_code == 404

def test_conversations_cross_user_isolation(client):
    user1, token1 = create_test_user("conv_iso1@intellirag.ai")
    user2, token2 = create_test_user("conv_iso2@intellirag.ai")

    create_res = client.post(
        "/api/conversations",
        json={"title": "User1 Private Chat"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    conv_id = create_res.json()["id"]

    get_res = client.get(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert get_res.status_code == 404

    del_res = client.delete(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert del_res.status_code == 404

    send_res = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "Unauthorized message"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert send_res.status_code == 404

def test_conversations_unauthenticated_rejected(client):
    conv_id = uuid.uuid4()
    assert client.get("/api/conversations").status_code == 401
    assert client.post("/api/conversations").status_code == 401
    assert client.get(f"/api/conversations/{conv_id}").status_code == 401
    assert client.delete(f"/api/conversations/{conv_id}").status_code == 401
    assert client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Hi"}).status_code == 401

def test_send_message_full_rag_flow_and_grounding_persistence(client):
    user, token = create_test_user("conv_rag1@intellirag.ai")

    doc_text = (
        "# Security Policy\n\n"
        "All employee accounts require multi-factor authentication (MFA) enabled.\n\n"
        "Session timeout is configured for 15 minutes of inactivity.\n\n"
        "Password rotation occurs every 90 days."
    )
    files = {"file": ("security_policy.txt", io.BytesIO(doc_text.encode("utf-8")), "text/plain")}
    up_res = client.post(
        "/api/documents/upload",
        files=files,
        data={"document_type": "POLICY"},
        headers={"Authorization": f"Bearer {token}"}
    )
    doc_id = up_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})

    conv_res = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = conv_res.json()["id"]

    msg_res = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "What are the requirements for MFA and session timeout?", "top_k": 3},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert msg_res.status_code == 200
    msg_data = msg_res.json()

    user_msg = msg_data["user_message"]
    assert user_msg["role"] == "user"
    assert user_msg["content"] == "What are the requirements for MFA and session timeout?"

    asst_msg = msg_data["assistant_message"]
    assert asst_msg["role"] == "assistant"
    assert asst_msg["is_sufficient_context"] is True
    assert asst_msg["citations"] is not None
    assert len(asst_msg["citations"]) > 0
    assert asst_msg["citations"][0]["document_filename"] == "security_policy.txt"

    grounding = asst_msg["grounding_metadata"]
    assert grounding is not None
    assert grounding["retrieved_sources"] > 0
    assert grounding["highest_similarity"] > 0.0
    assert grounding["has_sufficient_context"] is True

    get_conv_res = client.get(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_detail = get_conv_res.json()
    assert len(conv_detail["messages"]) == 2
    assert conv_detail["messages"][0]["role"] == "user"
    assert conv_detail["messages"][1]["role"] == "assistant"
    assert conv_detail["title"] != "New Conversation"

def test_send_message_followup_and_history(client):
    user, token = create_test_user("conv_followup@intellirag.ai")

    doc_text = (
        "# Refund Policy\n\n"
        "Domestic orders have a 30-day refund window.\n\n"
        "International orders have a 45-day refund window and require customs receipts."
    )
    files = {"file": ("refunds.txt", io.BytesIO(doc_text.encode("utf-8")), "text/plain")}
    up_res = client.post(
        "/api/documents/upload",
        files=files,
        data={"document_type": "POLICY"},
        headers={"Authorization": f"Bearer {token}"}
    )
    doc_id = up_res.json()["id"]
    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})

    conv_res = client.post(
        "/api/conversations",
        json={"title": "Refunds FAQ"},
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = conv_res.json()["id"]

    m1 = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "What is the domestic refund window?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert m1.status_code == 200

    m2 = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "What is the international refund policy?", "similarity_threshold": 0.1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert m2.status_code == 200
    assert m2.json()["assistant_message"]["is_sufficient_context"] is True

    get_res = client.get(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(get_res.json()["messages"]) == 4

def test_send_message_insufficient_context(client):
    user, token = create_test_user("conv_insuf@intellirag.ai")

    conv_res = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = conv_res.json()["id"]

    msg_res = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "What is the orbital speed of Jupiter?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    asst_msg = data["assistant_message"]
    assert asst_msg["is_sufficient_context"] is False
    assert "do not contain sufficient information" in asst_msg["content"].lower()
    assert asst_msg["grounding_metadata"]["retrieved_sources"] == 0

def test_send_message_empty_content_rejected(client):
    user, token = create_test_user("conv_empty@intellirag.ai")
    conv_res = client.post("/api/conversations", headers={"Authorization": f"Bearer {token}"})
    conv_id = conv_res.json()["id"]

    res = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"content": "   "},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400
