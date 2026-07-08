"""
NoteAI — Local AI video note-taking companion
Entry point: platform detection → dependency wiring → launch
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


def main() -> int:
    # HiDPI policy must be set before QApplication creation
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("NoteAI")
    app.setOrganizationName("LocalAI")
    app.setQuitOnLastWindowClosed(False)  # keep alive even when minimized to tray

    # ── 1. Platform detection ────────────────────────────────────────
    from app.platform_registry import PlatformRegistry
    platform_info = PlatformRegistry.detect()
    print(
        f"[NoteAI] Platform: {platform_info.os} | "
        f"Apple Silicon: {platform_info.is_apple_silicon} | "
        f"Audio: {platform_info.audio_backend} | "
        f"OCR: {platform_info.ocr_backend} | "
        f"Whisper: {platform_info.whisper_device}/{platform_info.whisper_compute}"
    )

    # ── 2. Event bus ─────────────────────────────────────────────────
    from app.event_bus import EventBus
    bus = EventBus()

    # ── 3. Audio capture ─────────────────────────────────────────────
    from app.audio.audio_factory import AudioFactory
    audio_capture = AudioFactory.create(platform_info, bus)

    # ── 4. Transcriber ───────────────────────────────────────────────
    from app.transcription.transcriber import Transcriber
    transcriber = Transcriber(platform_info, bus)

    # ── 5. LLM client ────────────────────────────────────────────────
    from app.llm.ollama_client import OllamaClient
    ollama_client = OllamaClient(bus, model="llama3")
    ollama_client.start()

    # ── 6. OCR provider ──────────────────────────────────────────────
    from app.ocr.ocr_factory import OCRFactory
    try:
        ocr_provider = OCRFactory.create(platform_info)
        print(f"[NoteAI] OCR backend: {ocr_provider.name}")
    except RuntimeError as exc:
        print(f"[NoteAI] WARNING: {exc}")
        ocr_provider = None

    # ── 7. Screen capture ────────────────────────────────────────────
    from app.capture.screen_capture import ScreenCapture
    screen_capture = ScreenCapture(bus)

    # ── 8. Document writer ───────────────────────────────────────────
    from app.doc.doc_writer import DocWriter
    doc_writer = DocWriter(bus)

    # ── 9. Main widget ───────────────────────────────────────────────
    from app.ui.floating_widget import FloatingWidget
    widget = FloatingWidget(
        event_bus=bus,
        platform_info=platform_info,
        audio_capture=audio_capture,
        transcriber=transcriber,
        ollama_client=ollama_client,
        ocr_provider=ocr_provider,
        screen_capture=screen_capture,
        doc_writer=doc_writer,
    )
    widget.show()

    bus.status_changed.emit(
        f"Ready — {platform_info.audio_backend} audio | {platform_info.ocr_backend} OCR"
    )

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
