import numpy as np
from app.ocr.base_ocr import OCRProvider


class TesseractOCR(OCRProvider):
    """Universal Tesseract fallback. Requires: pip install pytesseract + Tesseract binary."""

    name = "tesseract"

    def extract_text(self, image_path: str) -> str:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(
            Image.open(image_path), config="--psm 6"
        ).strip()

    def extract_text_from_array(self, image: np.ndarray) -> str:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(
            Image.fromarray(image), config="--psm 6"
        ).strip()
