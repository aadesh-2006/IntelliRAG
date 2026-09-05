import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.config import settings
from app.models.document import Document

@dataclass
class GeneratedChunk:
    chunk_id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any]

class ChunkingService:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        min_chunk_size: int = settings.MIN_CHUNK_SIZE,
        max_chunk_size: int = settings.MAX_CHUNK_SIZE,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def _format_table(self, table: Dict[str, Any], page_number: int) -> str:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        t_idx = table.get("table_index", 1)

        lines = [f"[TABLE: #{t_idx} | Page {page_number}]"]
        if headers:
            lines.append(" | ".join(headers))
            lines.append(" | ".join(["---"] * len(headers)))

        for r in rows:
            cells = r.get("cells", [])
            cell_texts = [str(c.get("content", "")).strip() for c in cells]
            lines.append(" | ".join(cell_texts))

        return "\n".join(lines)

    def _split_text_with_overlap(
        self,
        text: str,
        base_metadata: Dict[str, Any],
        start_index: int
    ) -> List[GeneratedChunk]:
        chunks: List[GeneratedChunk] = []
        clean_text = text.strip()
        if not clean_text:
            return chunks

        if len(clean_text) <= self.chunk_size:
            meta = dict(base_metadata)
            meta.update({
                "character_length": len(clean_text),
                "token_count": len(clean_text.split()),
            })
            chunks.append(
                GeneratedChunk(
                    chunk_id=str(uuid.uuid4()),
                    chunk_index=start_index,
                    content=clean_text,
                    metadata=meta
                )
            )
            return chunks

        paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1:
            paragraphs = [p.strip() for p in clean_text.split("\n") if p.strip()]

        current_buffer: List[str] = []
        current_len = 0
        idx = start_index

        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len > self.chunk_size and current_buffer:
                chunk_str = "\n\n".join(current_buffer).strip()
                if len(chunk_str) >= self.min_chunk_size:
                    meta = dict(base_metadata)
                    meta.update({
                        "character_length": len(chunk_str),
                        "token_count": len(chunk_str.split()),
                    })
                    chunks.append(
                        GeneratedChunk(
                            chunk_id=str(uuid.uuid4()),
                            chunk_index=idx,
                            content=chunk_str,
                            metadata=meta
                        )
                    )
                    idx += 1

                overlap_len = 0
                overlap_buffer: List[str] = []
                for p in reversed(current_buffer):
                    if overlap_len + len(p) <= self.chunk_overlap:
                        overlap_buffer.insert(0, p)
                        overlap_len += len(p)
                    else:
                        break

                current_buffer = overlap_buffer + [para]
                current_len = sum(len(p) for p in current_buffer)
            else:
                current_buffer.append(para)
                current_len += para_len

        if current_buffer:
            chunk_str = "\n\n".join(current_buffer).strip()
            if len(chunk_str) >= self.min_chunk_size or not chunks:
                meta = dict(base_metadata)
                meta.update({
                    "character_length": len(chunk_str),
                    "token_count": len(chunk_str.split()),
                })
                chunks.append(
                    GeneratedChunk(
                        chunk_id=str(uuid.uuid4()),
                        chunk_index=idx,
                        content=chunk_str,
                        metadata=meta
                    )
                )

        return chunks

    def chunk_document(self, document: Document) -> List[GeneratedChunk]:
        raw_meta = document.extracted_metadata or {}
        pages = raw_meta.get("pages", [])
        document_type = document.document_type

        all_chunks: List[GeneratedChunk] = []
        current_chunk_idx = 0

        if pages:
            current_heading: Optional[str] = None
            for page in pages:
                page_num = page.get("page_number", 1)

                tables = page.get("tables", [])
                for table in tables:
                    table_str = self._format_table(table, page_num)
                    t_meta = {
                        "page_number": page_num,
                        "section": current_heading or f"Table {table.get('table_index', 1)}",
                        "is_table": True,
                        "table_index": table.get("table_index", 1),
                        "table_headers": table.get("headers", []),
                        "document_type": document_type,
                        "character_length": len(table_str),
                        "token_count": len(table_str.split()),
                    }
                    all_chunks.append(
                        GeneratedChunk(
                            chunk_id=str(uuid.uuid4()),
                            chunk_index=current_chunk_idx,
                            content=table_str,
                            metadata=t_meta
                        )
                    )
                    current_chunk_idx += 1

                text_blocks = page.get("text_blocks", [])
                page_text_segments: List[str] = []
                last_bbox: Optional[Dict[str, Any]] = None

                for block in text_blocks:
                    b_type = block.get("block_type", "paragraph")
                    b_text = block.get("text", "").strip()
                    if not b_text:
                        continue

                    if b_type == "heading":
                        if page_text_segments:
                            text_body = "\n\n".join(page_text_segments)
                            b_meta = {
                                "page_number": page_num,
                                "section": current_heading or "Introduction",
                                "block_type": "section_body",
                                "bbox": last_bbox,
                                "document_type": document_type,
                                "is_table": False,
                            }
                            generated = self._split_text_with_overlap(text_body, b_meta, current_chunk_idx)
                            all_chunks.extend(generated)
                            current_chunk_idx += len(generated)
                            page_text_segments = []

                        current_heading = b_text
                    else:
                        page_text_segments.append(b_text)
                        if block.get("bbox"):
                            last_bbox = block.get("bbox")

                if page_text_segments:
                    text_body = "\n\n".join(page_text_segments)
                    b_meta = {
                        "page_number": page_num,
                        "section": current_heading or "Content",
                        "block_type": "page_content",
                        "bbox": last_bbox,
                        "document_type": document_type,
                        "is_table": False,
                    }
                    generated = self._split_text_with_overlap(text_body, b_meta, current_chunk_idx)
                    all_chunks.extend(generated)
                    current_chunk_idx += len(generated)

        elif document.extracted_text and document.extracted_text.strip():
            b_meta = {
                "page_number": 1,
                "section": "Main",
                "block_type": "unstructured_text",
                "document_type": document_type,
                "is_table": False,
            }
            all_chunks = self._split_text_with_overlap(document.extracted_text, b_meta, 0)

        for i, c in enumerate(all_chunks):
            c.chunk_index = i

        return all_chunks

chunking_service = ChunkingService()
