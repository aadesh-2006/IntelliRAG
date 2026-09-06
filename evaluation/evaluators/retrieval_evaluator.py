import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Set
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.services.retrieval_service import RetrievalService
from app.schemas.retrieval import SearchQueryRequest
from evaluation.metrics.ranking_metrics import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mrr_at_k,
    calculate_ndcg_at_k
)

class RetrievalEvaluator:
    def __init__(
        self,
        questions_path: str = "evaluation/datasets/rag_questions/questions.json",
        documents_dir: str = "evaluation/datasets/documents"
    ):
        self.questions_path = Path(questions_path)
        self.documents_dir = Path(documents_dir)
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.retrieval_service = RetrievalService(embed_service=embedding_service)

    def evaluate_all(self, k_values: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        with open(self.questions_path, "r", encoding="utf-8") as f:
            qa_data = json.load(f)

        db = self.SessionLocal()
        try:
            eval_user = User(
                id=uuid.uuid4(),
                email="evaluator@intellirag.ai",
                password_hash="notapassword"
            )
            db.add(eval_user)
            db.commit()

            doc_map = self._index_evaluation_documents(db, eval_user)

            queries = qa_data.get("queries", [])
            query_results = []
            
            recall_at_k = {k: 0.0 for k in k_values}
            precision_at_k = {k: 0.0 for k in k_values}
            mrr_at_k = {k: 0.0 for k in k_values}
            ndcg_at_k = {k: 0.0 for k in k_values}
            valid_queries_count = 0

            for q_obj in queries:
                q_id = q_obj["id"]
                query_text = q_obj["query"]
                exp_doc = q_obj.get("expected_document")
                exp_keywords = q_obj.get("expected_keywords", [])
                should_have = q_obj.get("should_have_context", True)

                req = SearchQueryRequest(
                    query=query_text,
                    top_k=max(k_values),
                    similarity_threshold=0.0
                )
                res = self.retrieval_service.search_similar_chunks(
                    db=db,
                    user=eval_user,
                    request=req
                )

                retrieved_filenames = [r.document_filename for r in res.results]
                
                if not should_have or not exp_doc:
                    query_results.append({
                        "id": q_id,
                        "query": query_text,
                        "expected_document": None,
                        "retrieved_top_filenames": retrieved_filenames[:3],
                        "top_similarity": res.results[0].similarity_score if res.results else 0.0,
                        "note": "Negative / Out-of-domain sample"
                    })
                    continue

                valid_queries_count += 1
                relevant_set: Set[str] = {exp_doc}

                per_q_rec = {}
                per_q_prec = {}
                per_q_mrr = {}
                per_q_ndcg = {}

                for k in k_values:
                    rec = calculate_recall_at_k(retrieved_filenames, relevant_set, k)
                    prec = calculate_precision_at_k(retrieved_filenames, relevant_set, k)
                    mrr = calculate_mrr_at_k(retrieved_filenames, relevant_set, k)
                    ndcg = calculate_ndcg_at_k(retrieved_filenames, relevant_set, k)

                    recall_at_k[k] += rec
                    precision_at_k[k] += prec
                    mrr_at_k[k] += mrr
                    ndcg_at_k[k] += ndcg

                    per_q_rec[f"recall@{k}"] = round(rec, 4)
                    per_q_prec[f"precision@{k}"] = round(prec, 4)
                    per_q_mrr[f"mrr@{k}"] = round(mrr, 4)
                    per_q_ndcg[f"ndcg@{k}"] = round(ndcg, 4)

                query_results.append({
                    "id": q_id,
                    "query": query_text,
                    "expected_document": exp_doc,
                    "retrieved_top_filenames": retrieved_filenames[:3],
                    "top_similarity": res.results[0].similarity_score if res.results else 0.0,
                    "metrics": {
                        **per_q_rec,
                        **per_q_prec,
                        **per_q_mrr,
                        **per_q_ndcg
                    }
                })

            n = float(valid_queries_count) if valid_queries_count > 0 else 1.0
            aggregated = {
                f"recall@{k}": round(recall_at_k[k] / n, 4) for k in k_values
            }
            aggregated.update({
                f"precision@{k}": round(precision_at_k[k] / n, 4) for k in k_values
            })
            aggregated.update({
                f"mrr@{k}": round(mrr_at_k[k] / n, 4) for k in k_values
            })
            aggregated.update({
                f"ndcg@{k}": round(ndcg_at_k[k] / n, 4) for k in k_values
            })

            return {
                "total_queries": len(queries),
                "relevant_queries_evaluated": valid_queries_count,
                "metrics": aggregated,
                "query_details": query_results
            }
        finally:
            db.close()

    def _index_evaluation_documents(self, db: Any, user: User) -> Dict[str, Document]:
        doc_map = {}
        for doc_file in self.documents_dir.glob("*.*"):
            if doc_file.suffix in (".py", ".pyc"):
                continue
            with open(doc_file, "r", encoding="utf-8") as f:
                content = f.read()

            doc = Document(
                id=uuid.uuid4(),
                user_id=user.id,
                filename=f"{doc_file.stem}_{uuid.uuid4().hex[:6]}{doc_file.suffix}",
                original_filename=doc_file.name,
                file_type=doc_file.suffix.replace('.', '').lower() or "txt",
                file_size=len(content.encode("utf-8")),
                file_path=str(doc_file),
                document_type="GENERAL",
                status="READY",
                extracted_text=content
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            chunks = chunking_service.chunk_document(doc)
            for ch in chunks:
                vec = embedding_service.embed_text(ch.content)
                db_chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=doc.id,
                    chunk_index=ch.chunk_index,
                    content=ch.content,
                    embedding=vec,
                    chunk_metadata=ch.metadata
                )
                db.add(db_chunk)
            db.commit()
            doc_map[doc_file.name] = doc
        return doc_map
