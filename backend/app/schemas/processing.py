from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class BoundingBox(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    x0: float
    y0: float
    x1: float
    y1: float
    page_number: int

class TableCell(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    row_index: int
    col_index: int
    content: str
    bbox: Optional[BoundingBox] = None

class TableRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    row_index: int
    cells: List[TableCell] = []

class TableBlock(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    table_index: int
    page_number: int
    headers: List[str] = []
    rows: List[TableRow] = []
    caption: Optional[str] = None
    bbox: Optional[BoundingBox] = None

class TextBlock(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    block_id: str
    block_type: str
    text: str
    page_number: int
    bbox: Optional[BoundingBox] = None
    confidence: Optional[float] = None

class DocumentPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page_number: int
    width: Optional[float] = None
    height: Optional[float] = None
    text_blocks: List[TextBlock] = []
    tables: List[TableBlock] = []
    has_ocr: bool = False

class ExtractedDocument(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    document_id: str
    processor: str
    page_count: int
    total_text_blocks: int
    total_tables: int
    full_text: str
    pages: List[DocumentPage] = []
    metadata: Dict[str, Any] = {}
    processed_at: datetime

class ProcessingTriggerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    document_id: str
    status: str
    message: str

class DocumentContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    document_id: str
    filename: str
    original_filename: str
    status: str
    document_type: str
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    extracted_text: Optional[str] = None
    extracted_metadata: Optional[Dict[str, Any]] = None
