import re
from datetime import datetime
from typing import Any, Optional

def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    s = str(text).strip().lower()
    s = re.sub(r'[\s_]+', ' ', s)
    s = re.sub(r'[^\w\s\.\,\-\:\/\$]', '', s)
    return s.strip()

def normalize_date(date_val: Any) -> Optional[str]:
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        return date_val.strftime("%Y-%m-%d")
    
    s = str(date_val).strip()
    iso_match = re.search(r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b', s)
    if iso_match:
        y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        try:
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            pass

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def normalize_number(num_val: Any) -> Optional[float]:
    if num_val is None:
        return None
    if isinstance(num_val, (int, float)):
        return float(num_val)
    
    s = str(num_val).strip()
    s = re.sub(r'[\$,€£¥\s]', '', s)
    s = s.replace(',', '')
    match = re.search(r'[-+]?\d*\.?\d+', s)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None
