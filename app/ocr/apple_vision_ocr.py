import sys
import numpy as np
from app.ocr.base_ocr import OCRProvider

# Guard: only define the class on macOS with PyObjC available
if sys.platform == "darwin":
    try:
        import Vision
        import Quartz
        from Foundation import NSURL
        import tempfile, os
        from PIL import Image as PILImage

        class AppleVisionOCR(OCRProvider):
            """Uses Apple Vision VNRecognizeTextRequest — Neural Engine accelerated on Apple Silicon."""

            name = "apple_vision"

            def extract_text(self, image_path: str) -> str:
                url = NSURL.fileURLWithPath_(image_path)
                handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(
                    url, {}
                )
                request = Vision.VNRecognizeTextRequest.alloc().init()
                request.setRecognitionLevel_(
                    Vision.VNRequestTextRecognitionLevelAccurate
                )
                request.setUsesLanguageCorrection_(True)

                err = handler.performRequests_error_([request], None)
                results = request.results()
                if not results:
                    return ""

                lines = []
                for obs in results:
                    candidates = obs.topCandidates_(1)
                    if candidates:
                        lines.append(str(candidates[0].string()))
                return "\n".join(lines)

            def extract_text_from_array(self, image: np.ndarray) -> str:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    tmp_path = f.name
                try:
                    PILImage.fromarray(image).save(tmp_path)
                    return self.extract_text(tmp_path)
                finally:
                    os.unlink(tmp_path)

    except ImportError:
        # PyObjC not available; AppleVisionOCR won't exist on this install
        pass
