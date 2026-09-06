import re
from typing import Dict, Any, List, Optional
from evaluation.metrics.normalizers import normalize_text

class GroundednessEvaluator:
    def evaluate_groundedness(
        self,
        query: str,
        retrieved_context: str,
        generated_answer: str,
        expected_claims: List[str],
        should_have_context: bool = True
    ) -> Dict[str, Any]:
        norm_answer = normalize_text(generated_answer)
        norm_context = normalize_text(retrieved_context)

        is_insufficient_declared = (
            "not contain sufficient information" in norm_answer or
            "insufficient information" in norm_answer or
            "not provide enough information" in norm_answer
        )

        if not should_have_context:
            if is_insufficient_declared or not norm_context:
                return {
                    "is_grounded": True,
                    "groundedness_score": 1.0,
                    "unsupported_claims": [],
                    "insufficient_context_handled": True,
                    "note": "Correctly handled out-of-context question"
                }
            else:
                return {
                    "is_grounded": False,
                    "groundedness_score": 0.0,
                    "unsupported_claims": ["Answer hallucinated without context"],
                    "insufficient_context_handled": False,
                    "note": "Hallucinated on out-of-domain query"
                }

        if not expected_claims:
            score = 1.0 if not is_insufficient_declared else 0.5
            return {
                "is_grounded": score >= 0.7,
                "groundedness_score": score,
                "unsupported_claims": [],
                "insufficient_context_handled": False,
                "note": "No ground-truth claims specified"
            }

        supported_count = 0
        unsupported = []

        for claim in expected_claims:
            claim_tokens = [w for w in re.findall(r'\w+', claim.lower()) if len(w) > 2]
            if not claim_tokens:
                supported_count += 1
                continue
                
            in_context = sum(1 for t in claim_tokens if t in norm_context) / float(len(claim_tokens))
            in_answer = sum(1 for t in claim_tokens if t in norm_answer) / float(len(claim_tokens))

            if in_context >= 0.4 and (in_answer >= 0.3 or len(norm_answer) > 20):
                supported_count += 1
            else:
                unsupported.append(claim)

        score = float(supported_count) / float(len(expected_claims))

        return {
            "is_grounded": score >= 0.6,
            "groundedness_score": round(score, 4),
            "expected_claims_count": len(expected_claims),
            "supported_claims_count": supported_count,
            "unsupported_claims": unsupported,
            "insufficient_context_handled": is_insufficient_declared
        }

    def evaluate_all(self, qa_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not qa_results:
            return {
                "average_groundedness": 0.0,
                "cases_evaluated": 0,
                "grounded_ratio": 0.0,
                "details": []
            }

        scores = []
        grounded_count = 0
        details = []

        for item in qa_results:
            res = self.evaluate_groundedness(
                query=item["query"],
                retrieved_context=item.get("retrieved_context", ""),
                generated_answer=item.get("generated_answer", ""),
                expected_claims=item.get("expected_claims", []),
                should_have_context=item.get("should_have_context", True)
            )
            scores.append(res["groundedness_score"])
            if res["is_grounded"]:
                grounded_count += 1
            details.append({
                "id": item.get("id"),
                "query": item["query"],
                **res
            })

        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "average_groundedness": round(avg_score, 4),
            "cases_evaluated": len(qa_results),
            "grounded_ratio": round(float(grounded_count) / float(len(qa_results)), 4),
            "details": details
        }
