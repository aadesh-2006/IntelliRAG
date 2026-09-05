import io
import uuid
import pytest
from tests.test_documents import create_test_user

def test_retrieval_query_returns_top_matching_chunks(client):
    user, token = create_test_user("retrieval_user1@intellirag.ai")
    sample_text = (
        "# Q3 Statement\n\n"
        "Net income reached $12.5M for the fiscal quarter ending September.\n\n"
        "Operating margins expanded to 28 percent.\n\n"
        "Cash reserves remain solid at $45M."
    )
    files = {"file": ("q3_statement.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")}
    upload_res = client.post(
        "/api/documents/upload",
        files=files,
        data={"document_type": "BALANCE_SHEET"},
        headers={"Authorization": f"Bearer {token}"}
    )
    doc_id = upload_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})

    search_res = client.post(
        "/api/retrieval/search",
        json={"query": "net income and cash reserves", "top_k": 3},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["query"] == "net income and cash reserves"
    assert data["total_results"] > 0
    assert data["top_k"] == 3
    first_match = data["results"][0]
    assert first_match["document_id"] == doc_id
    assert first_match["document_filename"] == "q3_statement.txt"
    assert first_match["document_type"] == "BALANCE_SHEET"
    assert first_match["similarity_score"] > 0.0
    assert 0.0 <= first_match["distance"] <= 2.0
    assert "Net income" in first_match["content"] or "Cash reserves" in first_match["content"] or "Statement" in first_match["content"]

def test_retrieval_vector_similarity_ordering(client):
    user, token = create_test_user("ordering_user@intellirag.ai")
    
    doc1_text = "# Cricket Stats\n\nRohit scored 92 runs with 8 sixes in the opening match."
    files1 = {"file": ("cricket.txt", io.BytesIO(doc1_text.encode("utf-8")), "text/plain")}
    up1 = client.post("/api/documents/upload", files=files1, headers={"Authorization": f"Bearer {token}"})
    doc1_id = up1.json()["id"]
    client.post(f"/api/documents/{doc1_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc1_id}/embed", headers={"Authorization": f"Bearer {token}"})

    doc2_text = "# Corporate Tax\n\nFederal tax depreciation schedules under Section 179 rules."
    files2 = {"file": ("tax.txt", io.BytesIO(doc2_text.encode("utf-8")), "text/plain")}
    up2 = client.post("/api/documents/upload", files=files2, headers={"Authorization": f"Bearer {token}"})
    doc2_id = up2.json()["id"]
    client.post(f"/api/documents/{doc2_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc2_id}/embed", headers={"Authorization": f"Bearer {token}"})

    search_res = client.post(
        "/api/retrieval/search",
        json={"query": "cricket runs and sixes", "top_k": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_res.status_code == 200
    results = search_res.json()["results"]
    assert len(results) >= 2
    assert results[0]["document_id"] == doc1_id
    assert results[0]["similarity_score"] >= results[1]["similarity_score"]

def test_retrieval_top_k_parameter(client):
    user, token = create_test_user("topk_user@intellirag.ai")
    paragraphs = "\n\n".join([f"# Section {i}\n\nDetailed breakdown of paragraph content number {i}." for i in range(10)])
    files = {"file": ("large_doc.txt", io.BytesIO(paragraphs.encode("utf-8")), "text/plain")}
    upload_res = client.post("/api/documents/upload", files=files, headers={"Authorization": f"Bearer {token}"})
    doc_id = upload_res.json()["id"]
    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})

    search_res = client.post(
        "/api/retrieval/search",
        json={"query": "breakdown of paragraph content", "top_k": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_res.status_code == 200
    data = search_res.json()
    assert len(data["results"]) == 2
    assert data["total_results"] == 2
    assert data["top_k"] == 2

def test_retrieval_similarity_threshold_filtering(client):
    user, token = create_test_user("thresh_user@intellirag.ai")
    text = "# Quantum Algorithms\n\nSuperconducting qubits and fault tolerant error correction."
    files = {"file": ("quantum.txt", io.BytesIO(text.encode("utf-8")), "text/plain")}
    upload_res = client.post("/api/documents/upload", files=files, headers={"Authorization": f"Bearer {token}"})
    doc_id = upload_res.json()["id"]
    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})

    search_all = client.post(
        "/api/retrieval/search",
        json={"query": "quantum error correction", "similarity_threshold": 0.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_all.status_code == 200
    assert len(search_all.json()["results"]) > 0

    search_impossible = client.post(
        "/api/retrieval/search",
        json={"query": "unrelated gardening tools and tomato planting", "similarity_threshold": 0.999},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_impossible.status_code == 200
    assert len(search_impossible.json()["results"]) == 0

def test_retrieval_filter_by_document_id(client):
    user, token = create_test_user("docfilter_user@intellirag.ai")

    f1 = {"file": ("docA.txt", io.BytesIO(b"# Topic A\n\nThis is content data inside document A."), "text/plain")}
    up1 = client.post("/api/documents/upload", files=f1, headers={"Authorization": f"Bearer {token}"})
    docA_id = up1.json()["id"]
    client.post(f"/api/documents/{docA_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{docA_id}/embed", headers={"Authorization": f"Bearer {token}"})

    f2 = {"file": ("docB.txt", io.BytesIO(b"# Topic B\n\nThis is content data inside document B."), "text/plain")}
    up2 = client.post("/api/documents/upload", files=f2, headers={"Authorization": f"Bearer {token}"})
    docB_id = up2.json()["id"]
    client.post(f"/api/documents/{docB_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{docB_id}/embed", headers={"Authorization": f"Bearer {token}"})

    search_res = client.post(
        "/api/retrieval/search",
        json={"query": "content data inside document", "document_ids": [docA_id]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_res.status_code == 200
    results = search_res.json()["results"]
    assert len(results) > 0
    assert all(r["document_id"] == docA_id for r in results)

def test_retrieval_filter_by_document_type(client):
    user, token = create_test_user("typefilter_user@intellirag.ai")

    f1 = {"file": ("invoice.txt", io.BytesIO(b"# Invoice\n\nTotal billing balance due is $500."), "text/plain")}
    up1 = client.post("/api/documents/upload", files=f1, data={"document_type": "INVOICE"}, headers={"Authorization": f"Bearer {token}"})
    doc1_id = up1.json()["id"]
    client.post(f"/api/documents/{doc1_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc1_id}/embed", headers={"Authorization": f"Bearer {token}"})

    f2 = {"file": ("balance.txt", io.BytesIO(b"# Balance\n\nTotal assets and shareholder equity is $500."), "text/plain")}
    up2 = client.post("/api/documents/upload", files=f2, data={"document_type": "BALANCE_SHEET"}, headers={"Authorization": f"Bearer {token}"})
    doc2_id = up2.json()["id"]
    client.post(f"/api/documents/{doc2_id}/process", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/documents/{doc2_id}/embed", headers={"Authorization": f"Bearer {token}"})

    search_res = client.post(
        "/api/retrieval/search",
        json={"query": "Total", "document_type": "INVOICE"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_res.status_code == 200
    results = search_res.json()["results"]
    assert len(results) > 0
    assert all(r["document_type"] == "INVOICE" for r in results)

def test_retrieval_empty_query_rejected(client):
    user, token = create_test_user("emptyquery_user@intellirag.ai")

    res1 = client.post(
        "/api/retrieval/search",
        json={"query": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res1.status_code == 422

    res2 = client.post(
        "/api/retrieval/search",
        json={"query": "     "},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res2.status_code == 400

def test_retrieval_cross_user_isolation(client):
    user1, token1 = create_test_user("isolated_user1@intellirag.ai")
    user2, token2 = create_test_user("isolated_user2@intellirag.ai")

    files = {"file": ("classified.txt", io.BytesIO(b"# Top Secret\n\nQuantum hyperdrive telemetry coordinates 42."), "text/plain")}
    up = client.post("/api/documents/upload", files=files, headers={"Authorization": f"Bearer {token1}"})
    doc_id = up.json()["id"]
    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token1}"})
    client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token1}"})

    search_user1 = client.post(
        "/api/retrieval/search",
        json={"query": "telemetry coordinates 42"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert search_user1.status_code == 200
    assert len(search_user1.json()["results"]) > 0

    search_user2 = client.post(
        "/api/retrieval/search",
        json={"query": "telemetry coordinates 42"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert search_user2.status_code == 200
    assert len(search_user2.json()["results"]) == 0

def test_retrieval_unauthenticated_request_rejected(client):
    res = client.post(
        "/api/retrieval/search",
        json={"query": "test query"}
    )
    assert res.status_code == 401

def test_retrieval_non_ready_document_excluded(client):
    user, token = create_test_user("nonready_user@intellirag.ai")

    files = {"file": ("unprocessed.txt", io.BytesIO(b"# Unprocessed\n\nOnly uploaded raw text content."), "text/plain")}
    up = client.post("/api/documents/upload", files=files, headers={"Authorization": f"Bearer {token}"})
    doc_id = up.json()["id"]

    search_res = client.post(
        "/api/retrieval/search",
        json={"query": "raw text content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert search_res.status_code == 200
    assert len(search_res.json()["results"]) == 0
