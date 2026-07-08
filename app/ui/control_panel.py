from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QLineEdit, QGroupBox, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSlot

from app.event_bus import EventBus
from app.ui.styles import BTN_PRIMARY, BTN_DANGER, BTN_SECONDARY


class ControlPanel(QWidget):
    """All user action buttons and controls.

    Emits intents via EventBus — does not hold references to workers directly.
    The FloatingWidget owns those and routes actions.
    """

    def __init__(self, event_bus: EventBus, parent=None):
        super().__init__(parent)
        self._bus = event_bus
        self._recording = False
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(6)

        # ── Recording group ──────────────────────────────────────────
        rec_group = QGroupBox("Audio Capture")
        rec_layout = QVBoxLayout(rec_group)
        rec_layout.setSpacing(4)

        self.btn_record = QPushButton("Start Recording")
        self.btn_record.setStyleSheet(BTN_PRIMARY)
        self.btn_record.setCheckable(True)
        rec_layout.addWidget(self.btn_record)

        # Manual timestamp extraction
        ts_row = QHBoxLayout()
        self.lbl_start = QLabel("From:")
        self.edit_ts_start = QLineEdit()
        self.edit_ts_start.setPlaceholderText("HH:MM:SS")
        self.edit_ts_start.setMaximumWidth(90)
        self.lbl_end = QLabel("To:")
        self.edit_ts_end = QLineEdit()
        self.edit_ts_end.setPlaceholderText("HH:MM:SS")
        self.edit_ts_end.setMaximumWidth(90)
        self.btn_extract = QPushButton("Extract")
        self.btn_extract.setStyleSheet(BTN_SECONDARY)
        self.btn_extract.setMaximumWidth(70)
        for w in (self.lbl_start, self.edit_ts_start, self.lbl_end,
                  self.edit_ts_end, self.btn_extract):
            ts_row.addWidget(w)
        rec_layout.addLayout(ts_row)
        root.addWidget(rec_group)

        # ── Screen capture group ─────────────────────────────────────
        cap_group = QGroupBox("Screen Capture")
        cap_layout = QHBoxLayout(cap_group)
        cap_layout.setSpacing(4)

        self.btn_capture = QPushButton("Select Region")
        self.btn_capture.setStyleSheet(BTN_SECONDARY)

        self.btn_ocr_capture = QPushButton("OCR Region")
        self.btn_ocr_capture.setStyleSheet(BTN_SECONDARY)

        self.btn_frame = QPushButton("Capture Frame")
        self.btn_frame.setStyleSheet(BTN_SECONDARY)

        for b in (self.btn_capture, self.btn_ocr_capture, self.btn_frame):
            cap_layout.addWidget(b)
        root.addWidget(cap_group)

        # ── Document group ───────────────────────────────────────────
        doc_group = QGroupBox("Document")
        doc_grid = QGridLayout(doc_group)
        doc_grid.setSpacing(4)

        self.btn_save = QPushButton("Save Doc")
        self.btn_save.setStyleSheet(BTN_PRIMARY)

        self.btn_reformat = QPushButton("Reformat")
        self.btn_reformat.setStyleSheet(BTN_SECONDARY)

        self.btn_ai_summary = QPushButton("AI Summary")
        self.btn_ai_summary.setStyleSheet(BTN_SECONDARY)

        self.btn_clean_notes = QPushButton("Clean Notes")
        self.btn_clean_notes.setStyleSheet(BTN_SECONDARY)

        # Insert-at controls
        self.lbl_insert = QLabel("Insert at line:")
        self.edit_line_num = QLineEdit()
        self.edit_line_num.setPlaceholderText("line #")
        self.edit_line_num.setMaximumWidth(60)
        self.btn_insert_line = QPushButton("Insert")
        self.btn_insert_line.setStyleSheet(BTN_SECONDARY)
        self.btn_insert_line.setMaximumWidth(60)

        doc_grid.addWidget(self.btn_save, 0, 0)
        doc_grid.addWidget(self.btn_reformat, 0, 1)
        doc_grid.addWidget(self.btn_ai_summary, 1, 0)
        doc_grid.addWidget(self.btn_clean_notes, 1, 1)
        doc_grid.addWidget(self.lbl_insert, 2, 0)
        insert_row = QHBoxLayout()
        insert_row.addWidget(self.edit_line_num)
        insert_row.addWidget(self.btn_insert_line)
        doc_grid.addLayout(insert_row, 2, 1)
        root.addWidget(doc_group)

        # ── Opacity slider ───────────────────────────────────────────
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("Opacity:"))
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(40, 100)
        self.slider_opacity.setValue(93)
        self.slider_opacity.setMaximumWidth(120)
        opacity_row.addWidget(self.slider_opacity)
        opacity_row.addStretch()
        root.addLayout(opacity_row)

    def _connect_signals(self) -> None:
        self.btn_record.toggled.connect(self._on_record_toggled)
        self.slider_opacity.valueChanged.connect(
            lambda v: self._bus.status_changed.emit(f"opacity:{v}")
        )

    @pyqtSlot(bool)
    def _on_record_toggled(self, checked: bool) -> None:
        if checked:
            self.btn_record.setText("Stop Recording")
            self.btn_record.setStyleSheet(BTN_DANGER)
        else:
            self.btn_record.setText("Start Recording")
            self.btn_record.setStyleSheet(BTN_PRIMARY)
