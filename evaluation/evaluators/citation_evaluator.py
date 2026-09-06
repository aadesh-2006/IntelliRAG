import re
from typing import Dict, Any, List

class CitationEvaluator:
    def evaluate_citations(
        self,
        generated_answer: str,
        citations: List[Any],
        retrieved_chunks: List[Any],
        expected_document: str = None
    ) -> Dict[str, Any]:
        citation_tags = re.findall(r'\[Source\s+(\d+)\]', generated_answer, re.I)
        cited_indices = [int(tag) for tag in citation_tags]

        if not cited_indices and not citations:
            return {
                "citations_present": False,
                "validity_rate": 1.0,
                "source_match_rate": 1.0,
                "cited_sources_count": 0,
                "valid_sources_count": 0,
                "details": []
            }

        valid_citations = 0
        source_matched_citations = 0
        details = []

        indices_to_check = cited_indices if cited_indices else [getattr(c, "citation_id", i+1) for i, c in enumerate(citations)]

        for idx in indices_to_check:
            match_found = False
            for cit in citations:
                cit_id = getattr(cit, "citation_id", getattr(cit, "source_id", None))
                if cit_id == idx:
                    valid_citations += 1
                    doc_fname = getattr(cit, "document_filename", "")
                    if expected_document is None or doc_fname == expected_document:
                        source_matched_citations += 1
                        match_found = True
                    details.append({
                        "citation_id": idx,
                        "document_filename": doc_fname,
                        "valid": True,
                        "matches_expected_document": match_found
                    })
                    break
            if not match_found and idx not in [d.get("citation_id") for d in details]:
                details.append({
                    "citation_id": idx,
                    "valid": False,
                    "matches_expected_document": False
                })

        total_cited = len(indices_to_check)
        val_rate = float(valid_citations) / float(total_cited) if total_cited > 0 else 1.0
        match_rate = float(source_matched_citations) / float(total_cited) if total_cited > 0 else 1.0

        return {
            "citations_present": len(indices_to_check) > 0,
            "validity_rate": round(val_rate, 4),
            "source_match_rate": round(match_rate, 4),
            "cited_sources_count": total_cited,
            "valid_sources_count": valid_citations,
            "details": details
        }

    def evaluate_all(self, qa_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not qa_results:
            return {
                "overall_validity_rate": 1.0,
                "overall_source_match_rate": 1.0,
                "queries_evaluated": 0,
                "details": []
            }

        validity_sum = 0.0
        match_sum = 0.0
        count = 0
        details = []

        for q in qa_results:
            if not q.get("should_have_context", True):
                continue
            res = self.evaluate_citations(
                generated_answer=q.get("generated_answer", ""),
                citations=q.get("citations", []),
                retrieved_chunks=q.get("retrieved_chunks", []),
                expected_document=q.get("expected_document")
            )
            validity_sum += res["validity_rate"]
            match_sum += res["source_match_rate"]
            count += 1
            details.append({
                "id": q.get("id"),
                "query": q.get("query"),
                **res
            })

        n = float(count) if count > 0 else 1.0
        return {
            "overall_validity_rate": round(validity_sum / n, 4),
            "overall_source_match_rate": round(match_sum / n, 4),
            "queries_evaluated": count,
            "details": details
        }
