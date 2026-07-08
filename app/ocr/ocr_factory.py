import sys
import importlib.util

from app.platform_registry import PlatformInfo
from app.ocr.base_ocr import OCRProvider


class OCRFactory:
    @staticmethod
    def create(platform_info: PlatformInfo) -> OCRProvider:
        # macOS: try Apple Vision (Neural Engine) first
        if platform_info.os == "darwin":
            try:
                from app.ocr.apple_vision_ocr import AppleVisionOCR  # type: ignore
                return AppleVisionOCR()
            except (ImportError, NameError):
                pass

        # Windows / Linux primary: PaddleOCR
        if importlib.util.find_spec("paddleocr") is not None:
            from app.ocr.paddle_ocr import PaddleOCRProvider
            return PaddleOCRProvider()

        # Universal fallback: Tesseract
        if importlib.util.find_spec("pytesseract") is not None:
            from app.ocr.tesseract_ocr import TesseractOCR
            return TesseractOCR()

        raise RuntimeError(
            "No OCR backend available.\n"
            "Install one of:\n"
            "  pip install paddleocr paddlepaddle   (Windows/Linux)\n"
            "  pip install pytesseract              (+ Tesseract binary)\n"
            "  pip install pyobjc-framework-Vision  (macOS)"
        )
