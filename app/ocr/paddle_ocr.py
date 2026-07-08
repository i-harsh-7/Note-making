import numpy as np
from app.ocr.base_ocr import OCRProvider


class PaddleOCRProvider(OCRProvider):
    """PaddleOCR backend for Windows and Linux.

    Lazy-initializes the model on first call to avoid slow import at startup.
    """

    name = "paddleocr"

    def __init__(self):
        self._ocr = None

    def _get_ocr(self):
        if self._ocr is None:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                use_gpu=False,
                show_log=False,
            )
        return self._ocr

    def extract_text(self, image_path: str) -> str:
        result = self._get_ocr().ocr(image_path, cls=True)
        if not result or not result[0]:
            return ""
        return "\n".join(
            line[1][0] for line in result[0] if line and line[1]
        )

    def extract_text_from_array(self, image: np.ndarray) -> str:
        result = self._get_ocr().ocr(image, cls=True)
        if not result or not result[0]:
            return ""
        return "\n".join(
            line[1][0] for line in result[0] if line and line[1]
        )
