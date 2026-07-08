from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt

from app.event_bus import EventBus


class NotesView(QWidget):
    """Displays LLM-cleaned notes and AI summaries."""

    def __init__(self, event_bus: EventBus, parent=None):
        super().__init__(parent)
        self._bus = event_bus
        self._build_ui()
        self._bus.notes_updated.connect(self._set_notes)
        self._bus.summary_ready.connect(self._prepend_summary)
        self._bus.ocr_result_ready.connect(self._append_ocr)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel("Notes")
        label.setObjectName("section_label")
        layout.addWidget(label)

        self._text = QTextEdit()
        self._text.setPlaceholderText("LLM-structured notes and OCR results appear here...")
        layout.addWidget(self._text)

    def _set_notes(self, text: str) -> None:
        self._text.setPlainText(text)

    def _prepend_summary(self, summary: str) -> None:
        existing = self._text.toPlainText()
        header = "─── AI Summary ───\n" + summary + "\n─────────────────\n\n"
        self._text.setPlainText(header + existing)

    def _append_ocr(self, text: str, _image_path: str) -> None:
        self._text.append("\n[OCR Result]\n" + text + "\n")

    def get_text(self) -> str:
        return self._text.toPlainText()
