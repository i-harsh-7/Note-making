import queue
import numpy as np
from PyQt6.QtCore import QThread

from app.platform_registry import PlatformInfo
from app.transcription.timestamp_utils import seconds_to_hms

# Whisper model to use. "base.en" is fast; swap to "small.en" for better accuracy.
DEFAULT_MODEL = "base.en"


class Transcriber(QThread):
    """Background worker that consumes PCM audio chunks and produces transcripts.

    Model loading is deferred to run() so the UI is responsive at startup.
    """

    def __init__(self, platform_info: PlatformInfo, event_bus):
        super().__init__()
        self._platform = platform_info
        self._bus = event_bus
        self._queue: queue.Queue = queue.Queue()
        self._model = None
        self._session_transcript: list[str] = []

    # -----------------------------------------------------------------
    # Public API (called from main thread)
    # -----------------------------------------------------------------

    def enqueue_chunk(self, pcm_bytes: bytes, timestamp: float) -> None:
        self._queue.put((pcm_bytes, timestamp))

    def flush(self) -> None:
        """Signal end of session; emits the full transcript."""
        self._queue.put(None)  # sentinel

    # -----------------------------------------------------------------
    # QThread worker
    # -----------------------------------------------------------------

    def run(self) -> None:
        self._bus.status_changed.emit("Loading Whisper model...")
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                DEFAULT_MODEL,
                device=self._platform.whisper_device,
                compute_type=self._platform.whisper_compute,
            )
        except Exception as exc:
            self._bus.error_occurred.emit("transcriber", f"Model load failed: {exc}")
            return

        self._bus.status_changed.emit("Whisper ready.")

        while True:
            item = self._queue.get()
            if item is None:
                # Session ended — emit full transcript
                full = "\n".join(self._session_transcript)
                self._bus.transcript_final.emit(full)
                self._session_transcript.clear()
                break

            pcm_bytes, timestamp = item
            self._transcribe(pcm_bytes, timestamp)

    def _transcribe(self, pcm_bytes: bytes, timestamp: float) -> None:
        try:
            audio = np.frombuffer(pcm_bytes, dtype=np.float32)
            segments, _ = self._model.transcribe(
                audio,
                language="en",
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )
            for seg in segments:
                tag = seconds_to_hms(timestamp + seg.start)
                text = f"[{tag}] {seg.text.strip()}"
                self._session_transcript.append(text)
                self._bus.transcript_chunk.emit(text, timestamp + seg.start)
        except Exception as exc:
            self._bus.error_occurred.emit("transcriber", f"Transcription error: {exc}")
