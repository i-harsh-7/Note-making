import sys
import platform
import subprocess
import importlib.util
from dataclasses import dataclass, field


@dataclass
class PlatformInfo:
    os: str                    # "darwin" | "win32" | "linux"
    is_apple_silicon: bool
    has_metal: bool
    audio_backend: str         # "wasapi" | "coreaudio" | "pipewire" | "alsa"
    ocr_backend: str           # "apple_vision" | "paddleocr" | "tesseract"
    whisper_device: str        # "cuda" | "cpu"
    whisper_compute: str       # "int8" | "float16"
    extra_flags: dict = field(default_factory=dict)


class PlatformRegistry:
    @staticmethod
    def detect() -> PlatformInfo:
        os_name = sys.platform  # "darwin", "win32", "linux"

        # --- Apple Silicon ---
        is_apple_silicon = (os_name == "darwin" and platform.machine() == "arm64")
        has_metal = is_apple_silicon

        # --- Whisper device/compute ---
        whisper_device, whisper_compute = PlatformRegistry._detect_whisper_backend(
            is_apple_silicon
        )

        # --- Audio backend ---
        audio_backend = PlatformRegistry._detect_audio_backend(os_name)

        # --- OCR backend ---
        ocr_backend = PlatformRegistry._detect_ocr_backend(os_name)

        return PlatformInfo(
            os=os_name,
            is_apple_silicon=is_apple_silicon,
            has_metal=has_metal,
            audio_backend=audio_backend,
            ocr_backend=ocr_backend,
            whisper_device=whisper_device,
            whisper_compute=whisper_compute,
        )

    @staticmethod
    def _detect_whisper_backend(is_apple_silicon: bool):
        if is_apple_silicon:
            # CTranslate2 uses Apple AMX/Accelerate on arm64 CPU
            return "cpu", "int8"

        # Check CUDA availability
        try:
            import ctranslate2
            types = ctranslate2.get_supported_compute_types("cuda")
            if types:
                return "cuda", "float16"
        except Exception:
            pass

        return "cpu", "int8"

    @staticmethod
    def _detect_audio_backend(os_name: str) -> str:
        if os_name == "darwin":
            return "coreaudio"
        if os_name == "win32":
            return "wasapi"
        # Linux: probe for PipeWire
        try:
            result = subprocess.run(
                ["pactl", "info"],
                capture_output=True, text=True, timeout=3
            )
            if "PipeWire" in result.stdout:
                return "pipewire"
        except Exception:
            pass
        return "alsa"

    @staticmethod
    def _detect_ocr_backend(os_name: str) -> str:
        if os_name == "darwin":
            if importlib.util.find_spec("Vision") is not None:
                return "apple_vision"

        if importlib.util.find_spec("paddleocr") is not None:
            return "paddleocr"

        if importlib.util.find_spec("pytesseract") is not None:
            return "tesseract"

        return "tesseract"  # will raise at runtime if not installed
