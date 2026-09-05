import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from app.schemas.processing import (
    ExtractedDocument,
    DocumentPage,
    TextBlock,
    TableBlock,
    TableRow,
    TableCell,
)
from app.services.document_processing.base import BaseDocumentProcessor

class TextProcessor(BaseDocumentProcessor):
    def process(
        self,
        file_path: Path,
        document_id: str,
        document_type: str = "GENERAL"
    ) -> ExtractedDocument:
        ext = file_path.suffix.lower()
        raw_content = file_path.read_text(encoding="utf-8", errors="replace")
        
        text_blocks: List[TextBlock] = []
        table_blocks: List[TableBlock] = []
        full_text = ""

        if ext == ".csv":
            lines = raw_content.splitlines()
            reader = csv.reader(lines)
            raw_rows = [row for row in reader if row]
            
            if raw_rows:
                headers = raw_rows[0]
                rows: List[TableRow] = []
                for r_idx, row in enumerate(raw_rows):
                    cells = [
                        TableCell(row_index=r_idx, col_index=c_idx, content=str(val).strip())
                        for c_idx, val in enumerate(row)
                    ]
                    rows.append(TableRow(row_index=r_idx, cells=cells))

                table_blocks.append(
                    TableBlock(
                        table_index=1,
                        page_number=1,
                        headers=headers,
                        rows=rows
                    )
                )
                csv_summary = f"CSV Table with {len(rows)} rows and {len(headers)} columns."
                text_blocks.append(
                    TextBlock(
                        block_id=str(uuid.uuid4()),
                        block_type="table_summary",
                        text=csv_summary,
                        page_number=1,
                        confidence=100.0
                    )
                )
                full_text = f"{csv_summary}\n\n" + "\n".join([", ".join(r) for r in raw_rows])
            else:
                full_text = ""

        elif ext == ".json":
            try:
                parsed_json = json.loads(raw_content)
                pretty_json = json.dumps(parsed_json, indent=2)
                full_text = pretty_json
                
                if isinstance(parsed_json, list) and parsed_json and isinstance(parsed_json[0], dict):
                    headers = list(parsed_json[0].keys())
                    rows: List[TableRow] = []
                    for r_idx, item in enumerate(parsed_json):
                        cells = [
                            TableCell(row_index=r_idx, col_index=c_idx, content=str(item.get(h, "")))
                            for c_idx, h in enumerate(headers)
                        ]
                        rows.append(TableRow(row_index=r_idx, cells=cells))
                    
                    table_blocks.append(
                        TableBlock(
                            table_index=1,
                            page_number=1,
                            headers=headers,
                            rows=rows
                        )
                    )
                
                text_blocks.append(
                    TextBlock(
                        block_id=str(uuid.uuid4()),
                        block_type="json_document",
                        text=pretty_json,
                        page_number=1,
                        confidence=100.0
                    )
                )
            except Exception:
                full_text = raw_content
                text_blocks.append(
                    TextBlock(
                        block_id=str(uuid.uuid4()),
                        block_type="raw_text",
                        text=raw_content,
                        page_number=1,
                        confidence=100.0
                    )
                )

        else:
            full_text = raw_content
            paragraphs = [p.strip() for p in raw_content.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [p.strip() for p in raw_content.split("\n") if p.strip()]

            for p in paragraphs:
                is_heading = p.startswith("#") or (len(p) < 80 and (p.isupper() or not p.endswith(".")))
                b_type = "heading" if is_heading else "paragraph"
                text_blocks.append(
                    TextBlock(
                        block_id=str(uuid.uuid4()),
                        block_type=b_type,
                        text=p,
                        page_number=1,
                        confidence=100.0
                    )
                )

        page = DocumentPage(
            page_number=1,
            width=612.0,
            height=792.0,
            text_blocks=text_blocks,
            tables=table_blocks,
            has_ocr=False
        )

        return ExtractedDocument(
            document_id=document_id,
            processor="structured_text_parser",
            page_count=1,
            total_text_blocks=len(text_blocks),
            total_tables=len(table_blocks),
            full_text=full_text,
            pages=[page],
            metadata={
                "extension": ext,
                "document_type": document_type,
                "character_count": len(full_text),
            },
            processed_at=datetime.now(timezone.utc)
        )
