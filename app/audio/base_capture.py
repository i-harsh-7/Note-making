from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject
import numpy as np

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SECONDS = 5      # Whisper performs best on 5-30s chunks
DTYPE = np.float32


class AudioCapture(QObject, ABC):
    """ABC for all platform audio loopback backends.

    Note: QObject must come before ABC in MRO to resolve metaclass conflict.
    Subclasses must call super().__init__(event_bus) in their __init__.
    """

    def __init__(self, event_bus):
        super().__init__()
        self._event_bus = event_bus
        self._running = False

    @abstractmethod
    def start(self) -> None:
        """Begin audio capture."""

    @abstractmethod
    def stop(self) -> None:
        """Stop audio capture and clean up."""

    def _emit_chunk(self, pcm_bytes: bytes, timestamp: float) -> None:
        self._event_bus.audio_chunk_ready.emit(pcm_bytes, timestamp)

    @property
    def is_running(self) -> bool:
        return self._running
