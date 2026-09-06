import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

ACTIONABLE_PATTERNS = [
    (
        r"(?i)\b(warranty\s+(?:expires?|end(?:s)?|valid\s+(?:until|through|thru)|period\s+until))\b[:\s]*",
        "WARRANTY",
        "Warranty Expiry",
        0.95
    ),
    (
        r"(?i)\b(policy\s+renewal|insurance\s+renewal|subscription\s+renewal|service\s+renewal|renewal(?:\s+deadline|\s+due|\s+date)?|renew(?:al)?\s+(?:due|by|on|before|deadline)|auto-renewal(?:\s+date)?)\b[:\s]*",
        "RENEWAL",
        "Renewal Due",
        0.92
    ),
    (
        r"(?i)\b(subscription\s+end(?:s)?|contract\s+(?:termination|expiration|expires?|end(?:s)?))\b[:\s]*",
        "RENEWAL",
        "Subscription/Contract End",
        0.90
    ),
    (
        r"(?i)\b(payment\s+due|amount\s+due\s+by|bill\s+due|invoice\s+due|pay\s+(?:by|before|on))\b[:\s]*",
        "PAYMENT",
        "Payment Due",
        0.92
    ),
    (
        r"(?i)\b(expir(?:es?|y|ation)\s*(?:date)?|valid\s+(?:until|through|thru))\b[:\s]*",
        "EXPIRY",
        "Document Expiry",
        0.88
    ),
    (
        r"(?i)\b(due\s+date|deadline|submit\s+(?:by|before)|complete\s+(?:by|before)|action\s+required\s+by)\b[:\s]*",
        "DEADLINE",
        "Action Deadline",
        0.85
    )
]

IRRELEVANT_PATTERNS = [
    r"(?i)\b(born\s+on|date\s+of\s+birth|dob)\b",
    r"(?i)\b(published\s+on|publication\s+date)\b",
    r"(?i)\b(created\s+on|creation\s+date|issued\s+on|issue\s+date|invoice\s+date|order\s+date|printed\s+on)\b",
]

class ActionableDateCandidate(BaseModel):
    date: datetime
    type: str
    title: str
    source_text: str
    page: Optional[int] = None
    section: Optional[str] = None
    confidence: float

class ActionableDateExtractor:
    def parse_date_string(self, text: str) -> Optional[datetime]:
        text = text.strip()

        m_iso = re.search(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b", text)
        if m_iso:
            y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
            if 1 <= m <= 12 and 1 <= d <= 31 and 1900 <= y <= 2100:
                try:
                    return datetime(y, m, d, 0, 0, 0, tzinfo=timezone.utc)
                except ValueError:
                    pass

        m_text_dmy = re.search(
            r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+),?\s+(\d{4})\b",
            text
        )
        if m_text_dmy:
            d_str, mon_str, y_str = m_text_dmy.group(1), m_text_dmy.group(2).lower(), m_text_dmy.group(3)
            if mon_str in MONTH_MAP:
                m_val = MONTH_MAP[mon_str]
                d_val, y_val = int(d_str), int(y_str)
                if 1 <= d_val <= 31 and 1900 <= y_val <= 2100:
                    try:
                        return datetime(y_val, m_val, d_val, 0, 0, 0, tzinfo=timezone.utc)
                    except ValueError:
                        pass

        m_text_mdy = re.search(
            r"\b([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b",
            text
        )
        if m_text_mdy:
            mon_str, d_str, y_str = m_text_mdy.group(1).lower(), m_text_mdy.group(2), m_text_mdy.group(3)
            if mon_str in MONTH_MAP:
                m_val = MONTH_MAP[mon_str]
                d_val, y_val = int(d_str), int(y_str)
                if 1 <= d_val <= 31 and 1900 <= y_val <= 2100:
                    try:
                        return datetime(y_val, m_val, d_val, 0, 0, 0, tzinfo=timezone.utc)
                    except ValueError:
                        pass

        m_dmy = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\b", text)
        if m_dmy:
            v1, v2, y = int(m_dmy.group(1)), int(m_dmy.group(2)), int(m_dmy.group(3))
            if 1900 <= y <= 2100:
                if 1 <= v2 <= 12 and 1 <= v1 <= 31:
                    try:
                        return datetime(y, v2, v1, 0, 0, 0, tzinfo=timezone.utc)
                    except ValueError:
                        pass
                elif 1 <= v1 <= 12 and 1 <= v2 <= 31:
                    try:
                        return datetime(y, v1, v2, 0, 0, 0, tzinfo=timezone.utc)
                    except ValueError:
                        pass

        return None

    def is_irrelevant_context(self, context: str) -> bool:
        for irr_pat in IRRELEVANT_PATTERNS:
            if re.search(irr_pat, context):
                has_actionable = False
                for act_pat, _, _, _ in ACTIONABLE_PATTERNS:
                    if re.search(act_pat, context):
                        has_actionable = True
                        break
                if not has_actionable:
                    return True
        return False

    def extract_from_text(
        self,
        text: str,
        page_num: Optional[int] = None,
        section_name: Optional[str] = None
    ) -> List[ActionableDateCandidate]:
        if not text or not text.strip():
            return []

        candidates: List[ActionableDateCandidate] = []
        lines = text.split("\n")

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if self.is_irrelevant_context(line_str):
                continue

            for act_pat, rem_type, title_prefix, conf in ACTIONABLE_PATTERNS:
                m_act = re.search(act_pat, line_str)
                if not m_act:
                    continue

                snippet_start = max(0, m_act.start() - 20)
                snippet_end = min(len(line_str), m_act.end() + 60)
                sub_snippet = line_str[snippet_start:snippet_end]

                date_val = self.parse_date_string(sub_snippet)
                if not date_val:
                    date_val = self.parse_date_string(line_str)

                if date_val:
                    clean_source = line_str if len(line_str) <= 200 else line_str[:200] + "..."
                    cand = ActionableDateCandidate(
                        date=date_val,
                        type=rem_type,
                        title=f"{title_prefix}: {date_val.strftime('%d %b %Y')}",
                        source_text=clean_source,
                        page=page_num,
                        section=section_name,
                        confidence=conf
                    )
                    candidates.append(cand)
                    break

        return candidates

    def extract_from_document_content(
        self,
        extracted_text: Optional[str] = None,
        extracted_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ActionableDateCandidate]:
        all_candidates: List[ActionableDateCandidate] = []
        seen_keys = set()

        if extracted_metadata and isinstance(extracted_metadata, dict):
            pages = extracted_metadata.get("pages", [])
            for p in pages:
                if not isinstance(p, dict):
                    continue
                p_num = p.get("page_number")
                
                raw_page_text = p.get("text", "")
                if raw_page_text:
                    cands = self.extract_from_text(raw_page_text, page_num=p_num)
                    for c in cands:
                        key = (c.date.isoformat(), c.type, c.page, c.section)
                        if key not in seen_keys:
                            seen_keys.add(key)
                            all_candidates.append(c)

                blocks = p.get("blocks") or p.get("text_blocks") or []
                for b in blocks:
                    if not isinstance(b, dict):
                        continue
                    b_type = b.get("type") or b.get("block_type")
                    b_sec = b.get("section")
                    b_text = b.get("text", "")
                    if b_text:
                        cands = self.extract_from_text(b_text, page_num=p_num, section_name=b_sec)
                        for c in cands:
                            key = (c.date.isoformat(), c.type, c.page, c.section)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                all_candidates.append(c)

                tables = p.get("tables", [])
                for t in tables:
                    if not isinstance(t, dict):
                        continue
                    headers = t.get("headers", [])
                    header_str = " | ".join(str(h) for h in headers)
                    rows = t.get("rows", [])
                    for r in rows:
                        row_cells = []
                        if isinstance(r, dict):
                            cells = r.get("cells", [])
                            for cell in cells:
                                if isinstance(cell, dict):
                                    row_cells.append(str(cell.get("content", "")))
                                else:
                                    row_cells.append(str(cell))
                        elif isinstance(r, list):
                            row_cells = [str(c) for c in r]

                        for col_idx, cell_val in enumerate(row_cells):
                            col_header = headers[col_idx] if col_idx < len(headers) else ""
                            cell_context = f"{col_header}: {cell_val}" if col_header else cell_val
                            cands = self.extract_from_text(cell_context, page_num=p_num, section_name="Table")
                            for c in cands:
                                key = (c.date.isoformat(), c.type, c.page, c.section)
                                if key not in seen_keys:
                                    seen_keys.add(key)
                                    all_candidates.append(c)

                        row_line = " | ".join(row_cells)
                        full_table_context = f"{header_str} - {row_line}"
                        cands = self.extract_from_text(full_table_context, page_num=p_num, section_name="Table")
                        for c in cands:
                            key = (c.date.isoformat(), c.type, c.page, c.section)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                all_candidates.append(c)

        if extracted_text:
            cands = self.extract_from_text(extracted_text)
            for c in cands:
                key = (c.date.isoformat(), c.type, c.page, c.section)
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_candidates.append(c)

        return all_candidates

date_extractor = ActionableDateExtractor()
