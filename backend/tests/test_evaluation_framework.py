import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (root_dir, backend_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
import math
from datetime import datetime
from evaluation.metrics.normalizers import normalize_text, normalize_date, normalize_number
from evaluation.metrics.ranking_metrics import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mrr_at_k,
    calculate_ndcg_at_k
)
from evaluation.metrics.score_calculators import compare_field_values, calculate_field_accuracy
from evaluation.evaluators.groundedness_evaluator import GroundednessEvaluator
from evaluation.evaluators.citation_evaluator import CitationEvaluator
from evaluation.evaluators.extraction_evaluator import ExtractionEvaluator
from evaluation.evaluators.retrieval_evaluator import RetrievalEvaluator
from evaluation.runner import EvaluationRunner

def test_normalized_text_comparison():
    assert normalize_text("  Apex Shield Insurance  ") == "apex shield insurance"
    assert normalize_text("Price: $1,450.00!") == "price: $1,450.00"
    assert normalize_text(None) == ""
    assert normalize_text(123) == "123"

def test_normalized_date_comparison():
    assert normalize_date("2025-01-15") == "2025-01-15"
    assert normalize_date("15/01/2025") == "2025-01-15"
    assert normalize_date("January 15, 2025") == "2025-01-15"
    assert normalize_date("2025-01-15T10:30:00Z") == "2025-01-15"
    assert normalize_date(datetime(2025, 1, 15, 12, 0)) == "2025-01-15"
    assert normalize_date("invalid-date-string") is None
    assert normalize_date(None) is None

def test_numeric_comparison():
    assert normalize_number("$1,450.00") == 1450.0
    assert normalize_number("1,800.50 USD") == 1800.5
    assert normalize_number("25") == 25.0
    assert normalize_number(500) == 500.0
    assert normalize_number("not a number") is None
    assert normalize_number(None) is None

def test_compare_field_values_exact_and_normalized():
    exact, norm = compare_field_values("2025-01-15", "2025-01-15")
    assert exact is True and norm is True

    exact, norm = compare_field_values("2025-01-15", "January 15, 2025")
    assert exact is False and norm is True

    exact, norm = compare_field_values("$1,450.00", "1450")
    assert exact is False and norm is True

    exact, norm = compare_field_values("Titan Ultra", "titan ultra")
    assert exact is False and norm is True

    exact, norm = compare_field_values("value A", "value B")
    assert exact is False and norm is False

    exact, norm = compare_field_values(None, None)
    assert exact is True and norm is True

def test_calculate_field_accuracy():
    exp = {
        "policy": "POL-1",
        "date": "2025-01-15",
        "amount": 1000.0
    }
    act = {
        "policy": "POL-1",
        "date": "January 15, 2025",
        "amount": "$1,000.00"
    }
    exact_acc, norm_acc, details = calculate_field_accuracy(exp, act)
    assert exact_acc == pytest.approx(1.0 / 3.0)
    assert norm_acc == pytest.approx(1.0)
    assert details["policy"]["exact_match"] is True
    assert details["date"]["exact_match"] is False
    assert details["date"]["normalized_match"] is True

def test_ranking_metrics_recall_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = {"doc2", "doc4"}

    assert calculate_recall_at_k(retrieved, relevant, 1) == 0.0
    assert calculate_recall_at_k(retrieved, relevant, 2) == 0.5
    assert calculate_recall_at_k(retrieved, relevant, 4) == 1.0
    assert calculate_recall_at_k([], relevant, 3) == 0.0
    assert calculate_recall_at_k(retrieved, set(), 3) == 0.0
    assert calculate_recall_at_k(retrieved, relevant, 0) == 0.0

def test_ranking_metrics_precision_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = {"doc2", "doc4"}

    assert calculate_precision_at_k(retrieved, relevant, 1) == 0.0
    assert calculate_precision_at_k(retrieved, relevant, 2) == 0.5
    assert calculate_precision_at_k(retrieved, relevant, 4) == 0.5
    assert calculate_precision_at_k([], relevant, 3) == 0.0
    assert calculate_precision_at_k(retrieved, set(), 3) == 0.0

def test_ranking_metrics_mrr_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    assert calculate_mrr_at_k(retrieved, {"doc1"}, 4) == 1.0
    assert calculate_mrr_at_k(retrieved, {"doc2"}, 4) == 0.5
    assert calculate_mrr_at_k(retrieved, {"doc3"}, 4) == pytest.approx(1.0 / 3.0)
    assert calculate_mrr_at_k(retrieved, {"doc5"}, 4) == 0.0
    assert calculate_mrr_at_k([], {"doc1"}, 4) == 0.0

def test_ranking_metrics_ndcg_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    assert calculate_ndcg_at_k(retrieved, {"doc1"}, 1) == 1.0
    assert calculate_ndcg_at_k(retrieved, {"doc2"}, 1) == 0.0
    assert calculate_ndcg_at_k(retrieved, {"doc2"}, 2) == pytest.approx(1.0 / math.log2(3))
    assert calculate_ndcg_at_k([], {"doc1"}, 4) == 0.0
    assert calculate_ndcg_at_k(retrieved, set(), 4) == 0.0

def test_groundedness_evaluation_supported_claims():
    evaluator = GroundednessEvaluator()
    res = evaluator.evaluate_groundedness(
        query="When does policy expire?",
        retrieved_context="The Apex Shield policy expires on 2026-01-15 with a coverage limit of 500,000.",
        generated_answer="The policy expires on 2026-01-15 [Source 1].",
        expected_claims=["The policy expires on 2026-01-15."],
        should_have_context=True
    )
    assert res["is_grounded"] is True
    assert res["groundedness_score"] >= 0.8
    assert len(res["unsupported_claims"]) == 0

def test_groundedness_evaluation_out_of_domain_refusal():
    evaluator = GroundednessEvaluator()
    res = evaluator.evaluate_groundedness(
        query="What is quantum gravity formula?",
        retrieved_context="",
        generated_answer="The provided documents do not contain sufficient information to answer this question.",
        expected_claims=[],
        should_have_context=False
    )
    assert res["is_grounded"] is True
    assert res["groundedness_score"] == 1.0
    assert res["insufficient_context_handled"] is True

def test_groundedness_evaluation_hallucination_penalty():
    evaluator = GroundednessEvaluator()
    res = evaluator.evaluate_groundedness(
        query="What is secret code?",
        retrieved_context="Unrelated document content.",
        generated_answer="The secret code is 998244353.",
        expected_claims=["The secret code is XYZ."],
        should_have_context=False
    )
    assert res["is_grounded"] is False
    assert res["groundedness_score"] == 0.0

def test_citation_evaluation_valid_citations():
    class DummyCit:
        def __init__(self, cit_id, fname):
            self.citation_id = cit_id
            self.document_filename = fname

    evaluator = CitationEvaluator()
    cits = [DummyCit(1, "policy_doc.txt"), DummyCit(2, "warranty_doc.txt")]
    res = evaluator.evaluate_citations(
        generated_answer="The policy expires in 2026 [Source 1]. The warranty covers parts [Source 2].",
        citations=cits,
        retrieved_chunks=[],
        expected_document="policy_doc.txt"
    )
    assert res["citations_present"] is True
    assert res["validity_rate"] == 1.0
    assert res["cited_sources_count"] == 2

def test_citation_evaluation_invalid_citation_index():
    class DummyCit:
        def __init__(self, cit_id, fname):
            self.citation_id = cit_id
            self.document_filename = fname

    evaluator = CitationEvaluator()
    cits = [DummyCit(1, "policy_doc.txt")]
    res = evaluator.evaluate_citations(
        generated_answer="The secret answer is found here [Source 99].",
        citations=cits,
        retrieved_chunks=[],
        expected_document="policy_doc.txt"
    )
    assert res["validity_rate"] == 0.0

def test_empty_dataset_handling():
    evaluator = GroundednessEvaluator()
    res = evaluator.evaluate_all([])
    assert res["average_groundedness"] == 0.0
    assert res["cases_evaluated"] == 0

    cit_evaluator = CitationEvaluator()
    c_res = cit_evaluator.evaluate_all([])
    assert c_res["overall_validity_rate"] == 1.0
    assert c_res["queries_evaluated"] == 0

def test_full_evaluation_runner_pipeline():
    runner = EvaluationRunner()
    res = runner.run(
        run_extraction=True,
        run_retrieval=True,
        run_groundedness=True,
        run_citations=True
    )
    assert "evaluation_run_id" in res
    assert "timestamp" in res
    assert "extraction" in res
    assert "retrieval" in res
    assert "groundedness" in res
    assert "citations" in res
    assert res["extraction"]["documents_evaluated"] >= 4
    assert res["retrieval"]["total_queries"] >= 5
    assert res["retrieval"]["metrics"]["recall@5"] == 1.0
