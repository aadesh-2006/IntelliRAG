import uuid
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from app.schemas.processing import ExtractedDocument, DocumentPage
from app.services.document_processing.base import BaseDocumentProcessor
from app.services.document_processing.ocr_utils import run_image_ocr

class ImageProcessor(BaseDocumentProcessor):
    def process(
        self,
        file_path: Path,
        document_id: str,
        document_type: str = "GENERAL"
    ) -> ExtractedDocument:
        with Image.open(file_path) as img:
            img_format = img.format or "IMAGE"
            width, height = img.size
            img_converted = img.convert("RGB")
            text_blocks, full_text = run_image_ocr(img_converted, page_number=1)

        page = DocumentPage(
            page_number=1,
            width=float(width),
            height=float(height),
            text_blocks=text_blocks,
            tables=[],
            has_ocr=True
        )

        return ExtractedDocument(
            document_id=document_id,
            processor="pytesseract_ocr_vision",
            page_count=1,
            total_text_blocks=len(text_blocks),
            total_tables=0,
            full_text=full_text,
            pages=[page],
            metadata={
                "image_format": img_format,
                "width": width,
                "height": height,
                "document_type": document_type,
            },
            processed_at=datetime.now(timezone.utc)
        )
