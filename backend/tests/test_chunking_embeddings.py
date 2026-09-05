import io
import uuid
import pytest
from app.config import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import embedding_service
from tests.test_documents import create_test_user
from tests.conftest import TestingSessionLocal

def test_chunking_service_headings_and_paragraphs():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)
    fake_doc = Document(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        filename="test.txt",
        original_filename="test.txt",
        file_type="text/plain",
        file_path="mock/path.txt",
        file_size=500,
        status="PROCESSED",
        document_type="GENERAL",
        extracted_metadata={
            "pages": [
                {
                    "page_number": 1,
                    "text_blocks": [
                        {"block_type": "heading", "text": "Executive Summary", "page_number": 1},
                        {"block_type": "paragraph", "text": "IntelliRAG is a next-generation document platform.", "page_number": 1},
                        {"block_type": "paragraph", "text": "It indexes structured tables, PDFs, and OCR images.", "page_number": 1},
                        {"block_type": "heading", "text": "Financial Highlights", "page_number": 1},
                        {"block_type": "paragraph", "text": "Revenue surged by 45 percent reaching all-time records.", "page_number": 1},
                    ],
                    "tables": []
                }
            ]
        }
    )

    chunks = chunker.chunk_document(fake_doc)
    assert len(chunks) >= 2
    assert any("Executive Summary" in c.metadata.get("section", "") for c in chunks)
    assert any("Financial Highlights" in c.metadata.get("section", "") for c in chunks)
    for idx, c in enumerate(chunks):
        assert c.chunk_index == idx
        assert c.metadata["page_number"] == 1
        assert "token_count" in c.metadata
        assert "character_length" in c.metadata

def test_chunking_service_tables():
    chunker = ChunkingService(chunk_size=300)
    fake_doc = Document(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        filename="stats.csv",
        original_filename="stats.csv",
        file_type="text/csv",
        file_path="mock/stats.csv",
        file_size=200,
        status="PROCESSED",
        document_type="CRICKET_BROCHURE",
        extracted_metadata={
            "pages": [
                {
                    "page_number": 1,
                    "text_blocks": [],
                    "tables": [
                        {
                            "table_index": 1,
                            "page_number": 1,
                            "headers": ["Batter", "Runs", "SR"],
                            "rows": [
                                {"row_index": 0, "cells": [{"content": "Batter"}, {"content": "Runs"}, {"content": "SR"}]},
                                {"row_index": 1, "cells": [{"content": "Rohit"}, {"content": "92"}, {"content": "224.3"}]},
                                {"row_index": 2, "cells": [{"content": "Kohli"}, {"content": "76"}, {"content": "128.8"}]},
                            ]
                        }
                    ]
                }
            ]
        }
    )

    chunks = chunker.chunk_document(fake_doc)
    assert len(chunks) == 1
    table_chunk = chunks[0]
    assert table_chunk.metadata["is_table"] is True
    assert table_chunk.metadata["table_headers"] == ["Batter", "Runs", "SR"]
    assert "Rohit" in table_chunk.content
    assert "Kohli" in table_chunk.content

def test_chunking_service_empty_document():
    chunker = ChunkingService()
    empty_doc = Document(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        filename="empty.txt",
        original_filename="empty.txt",
        file_type="text/plain",
        file_path="mock/empty.txt",
        file_size=0,
        status="PROCESSED",
        document_type="GENERAL",
        extracted_text="",
        extracted_metadata={"pages": []}
    )
    chunks = chunker.chunk_document(empty_doc)
    assert chunks == []

def test_embedding_service_dimension_and_normalization():
    text = "Artificial intelligence document parsing with pgvector."
    vector = embedding_service.embed_text(text)
    assert len(vector) == settings.VECTOR_DIMENSION
    assert len(vector) == 768

    norm_sq = sum(x * x for x in vector)
    assert abs(norm_sq - 1.0) < 1e-3

def test_embedding_service_batch():
    texts = [
        "First chunk of financial balance sheet.",
        "Second chunk of cricket tournament brochure.",
        "Third chunk with table structures.",
    ]
    batch_vectors = embedding_service.embed_batch(texts)
    assert len(batch_vectors) == 3
    for v in batch_vectors:
        assert len(v) == settings.VECTOR_DIMENSION

def test_embed_endpoint_full_pipeline_flow(client):
    user, token = create_test_user("embeduser@intellirag.ai")
    sample_text = (
        "# Q3 Statement\n\n"
        "Net income reached $12.5M for the fiscal quarter ending September.\n\n"
        "Operating margins expanded to 28 percent.\n\n"
        "Cash reserves remain solid at $45M."
    )
    files = {"file": ("q3_statement.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")}
    data = {"document_type": "BALANCE_SHEET"}

    upload_res = client.post(
        "/api/documents/upload",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    process_res = client.post(
        f"/api/documents/{doc_id}/process",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "PROCESSED"

    embed_res = client.post(
        f"/api/documents/{doc_id}/embed",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert embed_res.status_code == 200
    embed_data = embed_res.json()
    assert embed_data["status"] == "READY"
    assert embed_data["total"] > 0
    assert embed_data["embedding_dimension"] == 768
    assert len(embed_data["items"]) == embed_data["total"]

    first_chunk = embed_data["items"][0]
    assert first_chunk["chunk_index"] == 0
    assert "Net income" in first_chunk["content"] or "Q3 Statement" in first_chunk["content"]

    chunks_res = client.get(
        f"/api/documents/{doc_id}/chunks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert chunks_res.status_code == 200
    chunks_data = chunks_res.json()
    assert chunks_data["total"] == embed_data["total"]
    assert chunks_data["status"] == "READY"

def test_embed_endpoint_retry_idempotency(client):
    user, token = create_test_user("retryuser@intellirag.ai")
    files = {"file": ("report.txt", io.BytesIO(b"# Heading\n\nParagraph text for embedding."), "text/plain")}
    upload_res = client.post("/api/documents/upload", files=files, headers={"Authorization": f"Bearer {token}"})
    doc_id = upload_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token}"})
    
    res1 = client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 200
    total_1 = res1.json()["total"]

    res2 = client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    total_2 = res2.json()["total"]

    assert total_1 == total_2

    db = TestingSessionLocal()
    db_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == uuid.UUID(doc_id)).all()
    assert len(db_chunks) == total_1
    db.close()

def test_embed_unprocessed_document_rejected(client):
    user, token = create_test_user("unproc@intellirag.ai")
    files = {"file": ("raw.txt", io.BytesIO(b"Raw text content"), "text/plain")}
    upload_res = client.post("/api/documents/upload", files=files, headers={"Authorization": f"Bearer {token}"})
    doc_id = upload_res.json()["id"]

    embed_res = client.post(f"/api/documents/{doc_id}/embed", headers={"Authorization": f"Bearer {token}"})
    assert embed_res.status_code == 400
    assert "PROCESSED" in embed_res.json()["detail"]

def test_cross_user_embed_and_chunks_isolation(client):
    user1, token1 = create_test_user("owner1@intellirag.ai")
    user2, token2 = create_test_user("owner2@intellirag.ai")

    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("private.txt", io.BytesIO(b"# Secret\n\nPrivate data"), "text/plain")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    doc_id = upload_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {token1}"})

    assert client.post(
        f"/api/documents/{doc_id}/embed",
        headers={"Authorization": f"Bearer {token2}"}
    ).status_code == 404

    assert client.get(
        f"/api/documents/{doc_id}/chunks",
        headers={"Authorization": f"Bearer {token2}"}
    ).status_code == 404

def test_unauthenticated_embed_and_chunks_rejected(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert client.post(f"/api/documents/{fake_id}/embed").status_code == 401
    assert client.get(f"/api/documents/{fake_id}/chunks").status_code == 401
