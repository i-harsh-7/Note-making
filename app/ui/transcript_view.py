from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt

from app.event_bus import EventBus


class TranscriptView(QWidget):
    """Scrolling display of live transcript chunks with timestamps."""

    def __init__(self, event_bus: EventBus, parent=None):
        super().__init__(parent)
        self._bus = event_bus
        self._build_ui()
        self._bus.transcript_chunk.connect(self._append_chunk)
        self._bus.recording_started.connect(lambda: self._clear())

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel("Transcript")
        label.setObjectName("section_label")
        layout.addWidget(label)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setPlaceholderText("Live transcript will appear here...")
        layout.addWidget(self._text)

    def _append_chunk(self, text: str, _timestamp: float) -> None:
        cursor = self._text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._text.setTextCursor(cursor)
        self._text.insertPlainText(text + "\n")
        self._text.ensureCursorVisible()

    def _clear(self) -> None:
        self._text.clear()
