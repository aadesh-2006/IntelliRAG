import uuid
from typing import List, Tuple, Optional
from PIL import Image
import pytesseract
from app.schemas.processing import TextBlock, BoundingBox

def run_image_ocr(
    image: Image.Image,
    page_number: int = 1
) -> Tuple[List[TextBlock], str]:
    text_blocks: List[TextBlock] = []
    full_text = ""

    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        n_boxes = len(data.get("text", []))
        
        current_paragraph: List[str] = []
        min_x, min_y, max_x, max_y = 1e9, 1e9, -1, -1
        confidences: List[float] = []

        for i in range(n_boxes):
            word = str(data["text"][i]).strip()
            conf = float(data["conf"][i]) if "conf" in data and str(data["conf"][i]).replace(".", "", 1).isdigit() else -1.0
            
            if word:
                current_paragraph.append(word)
                x = float(data["left"][i])
                y = float(data["top"][i])
                w = float(data["width"][i])
                h = float(data["height"][i])
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + w)
                max_y = max(max_y, y + h)
                if conf >= 0:
                    confidences.append(conf)

            block_num = data["block_num"][i] if "block_num" in data else 0
            next_block_num = data["block_num"][i + 1] if i + 1 < n_boxes and "block_num" in data else -1

            if current_paragraph and (next_block_num != block_num or i == n_boxes - 1):
                p_text = " ".join(current_paragraph)
                avg_conf = sum(confidences) / len(confidences) if confidences else 90.0
                bbox = BoundingBox(
                    x0=min_x if min_x < 1e9 else 0.0,
                    y0=min_y if min_y < 1e9 else 0.0,
                    x1=max_x if max_x > -1 else float(image.width),
                    y1=max_y if max_y > -1 else float(image.height),
                    page_number=page_number
                )
                text_blocks.append(
                    TextBlock(
                        block_id=str(uuid.uuid4()),
                        block_type="ocr_text",
                        text=p_text,
                        page_number=page_number,
                        bbox=bbox,
                        confidence=round(avg_conf, 2)
                    )
                )
                current_paragraph = []
                min_x, min_y, max_x, max_y = 1e9, 1e9, -1, -1
                confidences = []

        if not text_blocks:
            simple_text = pytesseract.image_to_string(image).strip()
            if simple_text:
                full_text = simple_text
                text_blocks.append(
                    TextBlock(
                        block_id=str(uuid.uuid4()),
                        block_type="ocr_text",
                        text=simple_text,
                        page_number=page_number,
                        bbox=BoundingBox(
                            x0=0.0,
                            y0=0.0,
                            x1=float(image.width),
                            y1=float(image.height),
                            page_number=page_number
                        ),
                        confidence=85.0
                    )
                )
            else:
                full_text = ""
        else:
            full_text = "\n\n".join([b.text for b in text_blocks])

    except Exception:
        full_text = ""
        text_blocks = []

    return text_blocks, full_text
