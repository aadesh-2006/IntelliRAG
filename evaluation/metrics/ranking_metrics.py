import math
from typing import List, Set, Any

def calculate_recall_at_k(retrieved_ids: List[Any], relevant_ids: Set[Any], k: int) -> float:
    if not relevant_ids or k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    matched = len(set(top_k) & relevant_ids)
    return float(matched) / float(len(relevant_ids))

def calculate_precision_at_k(retrieved_ids: List[Any], relevant_ids: Set[Any], k: int) -> float:
    if not retrieved_ids or k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    matched = len(set(top_k) & relevant_ids)
    return float(matched) / float(len(top_k))

def calculate_mrr_at_k(retrieved_ids: List[Any], relevant_ids: Set[Any], k: int) -> float:
    if not relevant_ids or not retrieved_ids or k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    for rank_idx, item in enumerate(top_k, 1):
        if item in relevant_ids:
            return 1.0 / float(rank_idx)
    return 0.0

def calculate_ndcg_at_k(retrieved_ids: List[Any], relevant_ids: Set[Any], k: int) -> float:
    if not relevant_ids or not retrieved_ids or k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    
    dcg = 0.0
    for i, item in enumerate(top_k):
        rel = 1.0 if item in relevant_ids else 0.0
        if rel > 0.0:
            dcg += rel / math.log2(i + 2)
            
    idcg = 0.0
    num_ideal = min(k, len(relevant_ids))
    for i in range(num_ideal):
        idcg += 1.0 / math.log2(i + 2)
        
    if idcg <= 0.0:
        return 0.0
    return min(1.0, dcg / idcg)
