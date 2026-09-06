from typing import Dict, Any, Tuple
from evaluation.metrics.normalizers import normalize_text, normalize_date, normalize_number

def compare_field_values(expected_val: Any, actual_val: Any) -> Tuple[bool, bool]:
    if expected_val is None and actual_val is None:
        return True, True
    if expected_val is None or actual_val is None:
        return False, False
        
    exact = (str(expected_val).strip() == str(actual_val).strip())
    
    expected_d = normalize_date(expected_val)
    actual_d = normalize_date(actual_val)
    if expected_d is not None and actual_d is not None:
        normalized = (expected_d == actual_d)
        return exact, normalized
        
    expected_n = normalize_number(expected_val)
    actual_n = normalize_number(actual_val)
    if expected_n is not None and actual_n is not None:
        normalized = (abs(expected_n - actual_n) < 1e-4)
        return exact, normalized
        
    expected_t = normalize_text(expected_val)
    actual_t = normalize_text(actual_val)
    normalized = (expected_t == actual_t)
    return exact, normalized

def calculate_field_accuracy(expected_fields: Dict[str, Any], actual_fields: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
    if not expected_fields:
        return 1.0, 1.0, {}
        
    exact_matches = 0
    norm_matches = 0
    details = {}
    
    for k, exp_v in expected_fields.items():
        act_v = actual_fields.get(k)
        exact, norm = compare_field_values(exp_v, act_v)
        if exact:
            exact_matches += 1
        if norm:
            norm_matches += 1
        details[k] = {
            "expected": exp_v,
            "actual": act_v,
            "exact_match": exact,
            "normalized_match": norm
        }
        
    total = len(expected_fields)
    exact_acc = float(exact_matches) / float(total)
    norm_acc = float(norm_matches) / float(total)
    return exact_acc, norm_acc, details
