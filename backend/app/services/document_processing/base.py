from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from app.schemas.processing import ExtractedDocument

class BaseDocumentProcessor(ABC):
    @abstractmethod
    def process(
        self,
        file_path: Path,
        document_id: str,
        document_type: str = "GENERAL"
    ) -> ExtractedDocument:
        pass
