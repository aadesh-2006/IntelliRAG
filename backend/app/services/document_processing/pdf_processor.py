import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import pdfplumber
from app.schemas.processing import (
    ExtractedDocument,
    DocumentPage,
    TextBlock,
    TableBlock,
    TableRow,
    TableCell,
    BoundingBox,
)
from app.services.document_processing.base import BaseDocumentProcessor
from app.services.document_processing.ocr_utils import run_image_ocr

class PDFProcessor(BaseDocumentProcessor):
    def process(
        self,
        file_path: Path,
        document_id: str,
        document_type: str = "GENERAL"
    ) -> ExtractedDocument:
        pages: List[DocumentPage] = []
        all_text_parts: List[str] = []
        total_tables = 0
        total_blocks = 0

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page_idx, page in enumerate(pdf.pages, start=1):
                page_width = float(page.width) if page.width else 612.0
                page_height = float(page.height) if page.height else 792.0
                
                table_blocks: List[TableBlock] = []
                extracted_tables = page.extract_tables() or []
                
                for t_idx, raw_table in enumerate(extracted_tables, start=1):
                    if not raw_table:
                        continue
                    
                    rows: List[TableRow] = []
                    headers: List[str] = []
                    for r_idx, row in enumerate(raw_table):
                        cleaned_row = [str(c).strip() if c is not None else "" for c in row]
                        if r_idx == 0:
                            headers = cleaned_row
                        cells = [
                            TableCell(
                                row_index=r_idx,
                                col_index=c_idx,
                                content=c_val
                            )
                            for c_idx, c_val in enumerate(cleaned_row)
                        ]
                        rows.append(TableRow(row_index=r_idx, cells=cells))

                    if rows:
                        t_block = TableBlock(
                            table_index=t_idx,
                            page_number=page_idx,
                            headers=headers,
                            rows=rows
                        )
                        table_blocks.append(t_block)
                        total_tables += 1

                native_text = page.extract_text() or ""
                text_blocks: List[TextBlock] = []
                has_ocr = False

                if len(native_text.strip()) >= 20:
                    paragraphs = [p.strip() for p in native_text.split("\n\n") if p.strip()]
                    if not paragraphs:
                        paragraphs = [p.strip() for p in native_text.split("\n") if p.strip()]
                    
                    for p in paragraphs:
                        is_heading = len(p) < 80 and (p.isupper() or p.istitle() or not p.endswith("."))
                        b_type = "heading" if is_heading else "paragraph"
                        b = TextBlock(
                            block_id=str(uuid.uuid4()),
                            block_type=b_type,
                            text=p,
                            page_number=page_idx,
                            confidence=99.0
                        )
                        text_blocks.append(b)
                        total_blocks += 1
                        all_text_parts.append(p)
                else:
                    try:
                        page_img = page.to_image(resolution=150).original
                        ocr_blocks, ocr_text = run_image_ocr(page_img, page_number=page_idx)
                        if ocr_blocks:
                            has_ocr = True
                            text_blocks.extend(ocr_blocks)
                            total_blocks += len(ocr_blocks)
                            all_text_parts.append(ocr_text)
                    except Exception:
                        pass

                pages.append(
                    DocumentPage(
                        page_number=page_idx,
                        width=page_width,
                        height=page_height,
                        text_blocks=text_blocks,
                        tables=table_blocks,
                        has_ocr=has_ocr
                    )
                )

        full_text = "\n\n".join([t for t in all_text_parts if t.strip()])

        return ExtractedDocument(
            document_id=document_id,
            processor="pdfplumber_layout_parser",
            page_count=page_count,
            total_text_blocks=total_blocks,
            total_tables=total_tables,
            full_text=full_text,
            pages=pages,
            metadata={
                "document_type": document_type,
                "extraction_engine": "pdfplumber+tesseract",
                "extracted_page_count": len(pages),
            },
            processed_at=datetime.now(timezone.utc)
        )
