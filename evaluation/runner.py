import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.services.retrieval_service import RetrievalService
from app.services.prompt_service import prompt_service
from app.services.rag_service import RAGService
from app.services.llm_service import llm_service
from app.schemas.rag import RAGQueryRequest

from evaluation.evaluators.extraction_evaluator import ExtractionEvaluator
from evaluation.evaluators.retrieval_evaluator import RetrievalEvaluator
from evaluation.evaluators.groundedness_evaluator import GroundednessEvaluator
from evaluation.evaluators.citation_evaluator import CitationEvaluator

class EvaluationRunner:
    def __init__(
        self,
        documents_dir: str = "evaluation/datasets/documents",
        ground_truth_dir: str = "evaluation/datasets/extraction_ground_truth",
        questions_path: str = "evaluation/datasets/rag_questions/questions.json",
        results_dir: str = "evaluation/results"
    ):
        self.documents_dir = Path(documents_dir)
        self.ground_truth_dir = Path(ground_truth_dir)
        self.questions_path = Path(questions_path)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.extraction_evaluator = ExtractionEvaluator(
            documents_dir=documents_dir,
            ground_truth_dir=ground_truth_dir
        )
        self.retrieval_evaluator = RetrievalEvaluator(
            questions_path=questions_path,
            documents_dir=documents_dir
        )
        self.groundedness_evaluator = GroundednessEvaluator()
        self.citation_evaluator = CitationEvaluator()

    def run(
        self,
        run_extraction: bool = True,
        run_retrieval: bool = True,
        run_groundedness: bool = True,
        run_citations: bool = True
    ) -> Dict[str, Any]:
        started_at = datetime.now(timezone.utc).isoformat()
        results: Dict[str, Any] = {
            "evaluation_run_id": str(uuid.uuid4()),
            "timestamp": started_at,
            "dataset_version": "1.0",
            "model_info": {
                "llm_provider": llm_service.provider_name,
                "llm_model": llm_service.model_name,
                "embedding_model": getattr(embedding_service, "model_name", settings.EMBEDDING_MODEL_NAME),
                "vector_dimension": embedding_service.dimension
            }
        }

        if run_extraction:
            results["extraction"] = self.extraction_evaluator.evaluate_all()

        if run_retrieval:
            results["retrieval"] = self.retrieval_evaluator.evaluate_all()

        if run_groundedness or run_citations:
            rag_eval_data = self._run_rag_pipeline_for_qa()
            if run_groundedness:
                results["groundedness"] = self.groundedness_evaluator.evaluate_all(rag_eval_data)
            if run_citations:
                results["citations"] = self.citation_evaluator.evaluate_all(rag_eval_data)

        self._save_results(results)
        return results

    def _run_rag_pipeline_for_qa(self) -> list:
        with open(self.questions_path, "r", encoding="utf-8") as f:
            qa_json = json.load(f)

        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

        try:
            user = User(
                id=uuid.uuid4(),
                email="rag_eval@intellirag.ai",
                password_hash="notapassword"
            )
            db.add(user)
            db.commit()

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

            rag_serv = RAGService(
                retriever=RetrievalService(embed_service=embedding_service),
                prompter=prompt_service,
                llm=llm_service
            )

            qa_eval_records = []
            for q_obj in qa_json.get("queries", []):
                req = RAGQueryRequest(
                    query=q_obj["query"],
                    top_k=5,
                    similarity_threshold=0.25 if not q_obj.get("should_have_context", True) else 0.0
                )
                res = rag_serv.answer_query(db=db, user=user, request=req)

                retrieval_res = rag_serv.retrieval_service.search_similar_chunks(
                    db=db,
                    user=user,
                    request=req
                )
                context_str = " ".join([c.content for c in retrieval_res.results])

                qa_eval_records.append({
                    "id": q_obj["id"],
                    "query": q_obj["query"],
                    "expected_document": q_obj.get("expected_document"),
                    "expected_claims": q_obj.get("expected_claims", []),
                    "should_have_context": q_obj.get("should_have_context", True),
                    "generated_answer": res.answer,
                    "retrieved_context": context_str,
                    "citations": res.citations,
                    "retrieved_chunks": retrieval_res.results
                })
            return qa_eval_records
        finally:
            db.close()

    def _save_results(self, results: Dict[str, Any]):
        json_path = self.results_dir / "latest_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        md_path = self.results_dir / "latest_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.generate_markdown_report(results))

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        ts = results.get("timestamp", "")
        model_info = results.get("model_info", {})
        ext = results.get("extraction", {})
        ret = results.get("retrieval", {})
        gnd = results.get("groundedness", {})
        cit = results.get("citations", {})

        md = []
        md.append("# IntelliRAG AI Evaluation Report\n")
        md.append(f"**Timestamp:** {ts} | **Dataset Version:** {results.get('dataset_version')} | **Run ID:** `{results.get('evaluation_run_id')}`\n")
        md.append("## Configuration & Model Details")
        md.append(f"- **LLM Provider:** `{model_info.get('llm_provider')}` ({model_info.get('llm_model')})")
        md.append(f"- **Embedding Model:** `{model_info.get('embedding_model')}` (Dimension: {model_info.get('vector_dimension')})")
        md.append("- **Evaluation Mode:** Local Deterministic Evaluation\n")

        if ext:
            md.append("## 1. Document Extraction Evaluation")
            md.append(f"- **Documents Evaluated:** {ext.get('documents_evaluated', 0)}")
            md.append(f"- **Overall Normalized Field Accuracy:** **{ext.get('overall_accuracy', 0.0) * 100:.1f}%**")
            md.append(f"- **Overall Exact Field Accuracy:** **{ext.get('overall_exact_accuracy', 0.0) * 100:.1f}%**\n")
            md.append("| Document | Type | Exact Acc | Normalized Acc | Date Recall | Status |")
            md.append("|---|---|---|---|---|---|")
            for d in ext.get("document_results", []):
                d_rec = d.get("date_evaluation", {}).get("date_recall", 1.0)
                md.append(f"| `{d.get('document_filename')}` | {d.get('document_type')} | {d.get('exact_accuracy')*100:.1f}% | {d.get('normalized_accuracy')*100:.1f}% | {d_rec*100:.1f}% | {d.get('status')} |")
            md.append("")

        if ret:
            m = ret.get("metrics", {})
            md.append("## 2. RAG Retrieval Evaluation")
            md.append(f"- **Total Queries Evaluated:** {ret.get('total_queries', 0)} ({ret.get('relevant_queries_evaluated', 0)} relevant + out-of-domain)")
            md.append(f"- **Recall@1:** {m.get('recall@1', 0.0):.4f} | **Recall@3:** {m.get('recall@3', 0.0):.4f} | **Recall@5:** {m.get('recall@5', 0.0):.4f}")
            md.append(f"- **Precision@1:** {m.get('precision@1', 0.0):.4f} | **Precision@3:** {m.get('precision@3', 0.0):.4f} | **Precision@5:** {m.get('precision@5', 0.0):.4f}")
            md.append(f"- **MRR@5:** **{m.get('mrr@5', 0.0):.4f}**")
            md.append(f"- **NDCG@5:** **{m.get('ndcg@5', 0.0):.4f}**\n")

        if gnd:
            md.append("## 3. RAG Groundedness & Faithfulness")
            md.append(f"- **Average Groundedness Score:** **{gnd.get('average_groundedness', 0.0):.4f}**")
            md.append(f"- **Grounded Cases Ratio:** **{gnd.get('grounded_ratio', 0.0) * 100:.1f}%**")
            md.append(f"- **Cases Evaluated:** {gnd.get('cases_evaluated', 0)}\n")

        if cit:
            md.append("## 4. Citation Correctness")
            md.append(f"- **Citation Validity Rate:** **{cit.get('overall_validity_rate', 0.0) * 100:.1f}%**")
            md.append(f"- **Citation Source-Match Rate:** **{cit.get('overall_source_match_rate', 0.0) * 100:.1f}%**")
            md.append(f"- **Queries Evaluated:** {cit.get('queries_evaluated', 0)}\n")

        md.append("---")
        md.append("*Generated by IntelliRAG AI Evaluation Suite (Module 15)*")
        return "\n".join(md)
