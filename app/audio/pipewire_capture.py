import time
import threading
import numpy as np

from app.audio.base_capture import AudioCapture, SAMPLE_RATE, CHANNELS, CHUNK_SECONDS

_MONITOR_NAMES = ("monitor", "pipewire", "pulse", "alsa_output")


class PipeWireCapture(AudioCapture):
    """Linux PipeWire/ALSA loopback capture.

    PipeWire automatically exposes monitor sources for each sink.
    Filter for names containing 'monitor' to get desktop audio.
    """

    def __init__(self, event_bus):
        super().__init__(event_bus)
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        self._event_bus.recording_started.emit()
        self._event_bus.status_changed.emit("Recording (PipeWire monitor)...")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=CHUNK_SECONDS + 2)
        self._event_bus.recording_stopped.emit()
        self._event_bus.status_changed.emit("Recording stopped.")

    def _find_monitor_device(self, soundcard):
        all_mics = soundcard.all_microphones(include_loopback=True)
        for mic in all_mics:
            if any(name in mic.name.lower() for name in _MONITOR_NAMES):
                return mic
        self._event_bus.status_changed.emit(
            "Warning: No monitor source found. Using default mic."
        )
        return soundcard.default_microphone()

    def _capture_loop(self) -> None:
        try:
            import soundcard
        except ImportError:
            self._event_bus.error_occurred.emit(
                "audio", "soundcard not installed. Run: pip install soundcard"
            )
            self._running = False
            return

        try:
            device = self._find_monitor_device(soundcard)
            with device.recorder(samplerate=SAMPLE_RATE, channels=CHANNELS) as rec:
                while self._running:
                    data = rec.record(numframes=SAMPLE_RATE * CHUNK_SECONDS)
                    if data.ndim > 1:
                        data = data[:, 0]
                    pcm = data.astype(np.float32)
                    self._emit_chunk(pcm.tobytes(), time.monotonic())
        except Exception as exc:
            self._event_bus.error_occurred.emit("audio", f"PipeWire error: {exc}")
            self._running = False
