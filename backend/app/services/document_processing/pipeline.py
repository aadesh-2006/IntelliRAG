from pathlib import Path
from typing import Dict
from app.schemas.processing import ExtractedDocument
from app.services.document_processing.base import BaseDocumentProcessor
from app.services.document_processing.pdf_processor import PDFProcessor
from app.services.document_processing.image_processor import ImageProcessor
from app.services.document_processing.text_processor import TextProcessor
from app.services.document_processing.docx_processor import DocxProcessor

class DocumentProcessingPipeline:
    def __init__(self):
        self._pdf_processor = PDFProcessor()
        self._image_processor = ImageProcessor()
        self._text_processor = TextProcessor()
        self._docx_processor = DocxProcessor()

        self._processors: Dict[str, BaseDocumentProcessor] = {
            ".pdf": self._pdf_processor,
            ".png": self._image_processor,
            ".jpg": self._image_processor,
            ".jpeg": self._image_processor,
            ".tiff": self._image_processor,
            ".bmp": self._image_processor,
            ".webp": self._image_processor,
            ".txt": self._text_processor,
            ".md": self._text_processor,
            ".csv": self._text_processor,
            ".json": self._text_processor,
            ".docx": self._docx_processor,
        }

    def get_processor_for_file(self, file_path: Path) -> BaseDocumentProcessor:
        ext = file_path.suffix.lower()
        if ext not in self._processors:
            raise ValueError(f"No document processor registered for file extension '{ext}'")
        return self._processors[ext]

    def process_document(
        self,
        file_path: Path,
        document_id: str,
        document_type: str = "GENERAL"
    ) -> ExtractedDocument:
        if not file_path.exists():
            raise FileNotFoundError(f"Document file not found at path: {file_path}")

        processor = self.get_processor_for_file(file_path)
        return processor.process(
            file_path=file_path,
            document_id=document_id,
            document_type=document_type
        )

document_pipeline = DocumentProcessingPipeline()
