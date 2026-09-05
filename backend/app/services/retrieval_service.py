import json
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import BaseEmbeddingService, embedding_service
from app.schemas.retrieval import SearchQueryRequest, RetrievedChunk, SearchQueryResponse

class RetrievalService:
    def __init__(self, embed_service: Optional[BaseEmbeddingService] = None):
        self.embedding_service = embed_service or embedding_service

    def search_similar_chunks(
        self,
        db: Session,
        user: User,
        request: SearchQueryRequest
    ) -> SearchQueryResponse:
        cleaned_query = request.query.strip()
        if not cleaned_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query text cannot be empty or whitespace only"
            )

        query_vector = self.embedding_service.embed_text(cleaned_query)

        is_sqlite = db.get_bind().dialect.name == "sqlite"

        if is_sqlite:
            query = (
                select(DocumentChunk, Document.original_filename, Document.document_type)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(
                    Document.user_id == user.id,
                    Document.status == "READY",
                    DocumentChunk.embedding.isnot(None)
                )
            )
            if request.document_ids:
                doc_uuids = [d if isinstance(d, uuid.UUID) else uuid.UUID(str(d)) for d in request.document_ids]
                query = query.where(Document.id.in_(doc_uuids))
            if request.document_type:
                query = query.where(Document.document_type == request.document_type)

            rows = db.execute(query).all()
            scored_candidates = []

            for chunk, doc_filename, doc_type in rows:
                emb = chunk.embedding
                if emb is None:
                    continue
                if isinstance(emb, str):
                    emb = json.loads(emb)
                elif hasattr(emb, "tolist"):
                    emb = emb.tolist()

                dot_product = sum(a * b for a, b in zip(query_vector, emb))
                similarity = max(-1.0, min(1.0, dot_product))
                distance = max(0.0, 1.0 - similarity)

                if request.similarity_threshold is not None and similarity < request.similarity_threshold:
                    continue

                scored_candidates.append((chunk, doc_filename, doc_type, similarity, distance))

            scored_candidates.sort(key=lambda x: x[3], reverse=True)
            top_candidates = scored_candidates[:request.top_k]

            results = [
                RetrievedChunk(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    document_filename=doc_filename,
                    document_type=doc_type,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    similarity_score=round(float(sim), 4),
                    distance=round(float(dist), 4),
                    metadata=chunk.chunk_metadata
                )
                for chunk, doc_filename, doc_type, sim, dist in top_candidates
            ]
        else:
            distance_expr = DocumentChunk.embedding.cosine_distance(query_vector)
            query = (
                select(
                    DocumentChunk,
                    Document.original_filename,
                    Document.document_type,
                    distance_expr.label("distance")
                )
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(
                    Document.user_id == user.id,
                    Document.status == "READY",
                    DocumentChunk.embedding.isnot(None)
                )
            )
            if request.document_ids:
                doc_uuids = [d if isinstance(d, uuid.UUID) else uuid.UUID(str(d)) for d in request.document_ids]
                query = query.where(Document.id.in_(doc_uuids))
            if request.document_type:
                query = query.where(Document.document_type == request.document_type)
            if request.similarity_threshold is not None:
                max_distance = 1.0 - request.similarity_threshold
                query = query.where(distance_expr <= max_distance)

            query = query.order_by(distance_expr.asc()).limit(request.top_k)

            rows = db.execute(query).all()
            results = []
            for chunk, doc_filename, doc_type, dist in rows:
                dist_val = float(dist)
                sim_score = max(0.0, min(1.0, 1.0 - dist_val))
                results.append(
                    RetrievedChunk(
                        id=chunk.id,
                        document_id=chunk.document_id,
                        document_filename=doc_filename,
                        document_type=doc_type,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        similarity_score=round(sim_score, 4),
                        distance=round(dist_val, 4),
                        metadata=chunk.chunk_metadata
                    )
                )

        return SearchQueryResponse(
            query=cleaned_query,
            total_results=len(results),
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            results=results
        )

retrieval_service = RetrievalService()
