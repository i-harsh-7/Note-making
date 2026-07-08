import time
from pathlib import Path

from app.event_bus import EventBus
from app.transcription.timestamp_utils import seconds_to_hms, video_session_id

OUTPUT_DIR = Path("output") / "captures"


class ScreenCapture:
    """Captures screen regions via mss and optionally runs OCR on the result."""

    def __init__(self, event_bus: EventBus, output_dir: Path = OUTPUT_DIR):
        self._bus = event_bus
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._frame_counter = 0
        self._session_id = video_session_id()

        self._bus.region_selected.connect(self.capture_region)

    def capture_region(self, x: int, y: int, w: int, h: int) -> str:
        """Capture a screen region and save it as PNG. Returns the saved path."""
        import mss
        import mss.tools

        self._frame_counter += 1
        timestamp = time.monotonic()
        filename = (
            f"{self._session_id}_frame_{self._frame_counter:04d}"
            f"_{seconds_to_hms(timestamp).replace(':', '-')}.png"
        )
        output_path = self._output_dir / filename

        with mss.mss() as sct:
            monitor = {"top": y, "left": x, "width": w, "height": h}
            shot = sct.grab(monitor)
            mss.tools.to_png(shot.rgb, shot.size, output=str(output_path))

        self._bus.capture_taken.emit(str(output_path), timestamp)
        self._bus.status_changed.emit(f"Captured: {output_path.name}")
        return str(output_path)

    def capture_and_ocr(self, x: int, y: int, w: int, h: int, ocr_provider) -> str:
        """Capture region, run OCR, emit results. Returns OCR text."""
        image_path = self.capture_region(x, y, w, h)
        try:
            text = ocr_provider.extract_text(image_path)
            self._bus.ocr_result_ready.emit(text, image_path)
            return text
        except Exception as exc:
            self._bus.error_occurred.emit("ocr", f"OCR failed: {exc}")
            return ""

    def capture_frame_with_tag(
        self, x: int, y: int, w: int, h: int, user_timestamp: float | None = None
    ) -> str:
        """Capture and tag with a user-provided or system timestamp."""
        ts = user_timestamp if user_timestamp is not None else time.monotonic()
        image_path = self.capture_region(x, y, w, h)
        self._bus.status_changed.emit(
            f"Frame captured at {seconds_to_hms(ts)} → {Path(image_path).name}"
        )
        return image_path
