from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QApplication, QFileDialog,
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSlot
from PyQt6.QtGui import QMouseEvent, QIcon

from app.event_bus import EventBus
from app.platform_registry import PlatformInfo
from app.ui.control_panel import ControlPanel
from app.ui.transcript_view import TranscriptView
from app.ui.notes_view import NotesView
from app.ui.region_selector import RegionSelector
from app.ui.styles import (
    MAIN_STYLE, TITLE_BAR_STYLE, STATUS_BAR_STYLE,
    WIDGET_W, WIDGET_H, OPACITY_DEFAULT, BG_PANEL, TEXT_PRIMARY, BORDER,
)


class FloatingWidget(QWidget):
    """Frameless, always-on-top, semi-transparent main window.

    Draggable by its title bar. Owns all worker references and
    wires ControlPanel button clicks to the appropriate workers.
    """

    def __init__(
        self,
        event_bus: EventBus,
        platform_info: PlatformInfo,
        audio_capture,
        transcriber,
        ollama_client,
        ocr_provider,
        screen_capture,
        doc_writer,
        parent=None,
    ):
        super().__init__(parent)
        self._bus = event_bus
        self._platform = platform_info
        self._audio = audio_capture
        self._transcriber = transcriber
        self._ollama = ollama_client
        self._ocr = ocr_provider
        self._screen = screen_capture
        self._doc = doc_writer
        self._drag_pos: QPoint | None = None
        self._region_selector: RegionSelector | None = None

        self._init_window()
        self._build_ui()
        self._connect_control_panel()
        self._connect_event_bus()
        self._start_autosave()

    # -----------------------------------------------------------------
    # Window setup
    # -----------------------------------------------------------------

    def _init_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(OPACITY_DEFAULT)
        self.resize(WIDGET_W, WIDGET_H)
        self.setStyleSheet(MAIN_STYLE)

        # Position top-right of primary screen
        screen_rect = QApplication.primaryScreen().availableGeometry()
        self.move(screen_rect.right() - WIDGET_W - 20, screen_rect.top() + 40)

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Title bar
        title_bar = self._make_title_bar()
        root.addWidget(title_bar)

        # Content area
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setContentsMargins(8, 6, 8, 0)

        self._transcript_view = TranscriptView(self._bus)
        self._notes_view = NotesView(self._bus)
        splitter.addWidget(self._transcript_view)
        splitter.addWidget(self._notes_view)
        splitter.setSizes([240, 180])
        root.addWidget(splitter, stretch=1)

        # Control panel
        self._control_panel = ControlPanel(self._bus)
        root.addWidget(self._control_panel)

        # Status bar
        self._status_bar = QLabel("Ready.")
        self._status_bar.setStyleSheet(STATUS_BAR_STYLE)
        self._status_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self._status_bar)

    def _make_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet(TITLE_BAR_STYLE)
        bar.setFixedHeight(38)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 8, 0)

        icon_label = QLabel("◉")
        icon_label.setStyleSheet(f"color: #4C9FE8; font-size: 14px;")
        title = QLabel("NoteAI")
        title.setObjectName("title_label")

        btn_min = QPushButton("─")
        btn_min.setFixedSize(24, 24)
        btn_min.setStyleSheet(
            f"QPushButton {{ background: {BG_PANEL}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; font-size: 10px; }}"
            f"QPushButton:hover {{ background: #3A4050; }}"
        )
        btn_min.clicked.connect(self.showMinimized)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet(
            "QPushButton { background: #E05C5C; color: white; border: none; "
            "border-radius: 4px; font-size: 11px; font-weight: bold; }"
            "QPushButton:hover { background: #C94040; }"
        )
        btn_close.clicked.connect(self._on_close)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(btn_min)
        layout.addWidget(btn_close)
        return bar

    # -----------------------------------------------------------------
    # Button → worker wiring
    # -----------------------------------------------------------------

    def _connect_control_panel(self) -> None:
        cp = self._control_panel

        # Recording
        cp.btn_record.toggled.connect(self._on_record_toggled)

        # Timestamp extraction
        cp.btn_extract.clicked.connect(self._on_extract_timestamps)

        # Screen capture
        cp.btn_capture.clicked.connect(lambda: self._open_region_selector("capture"))
        cp.btn_ocr_capture.clicked.connect(lambda: self._open_region_selector("ocr"))
        cp.btn_frame.clicked.connect(self._on_capture_frame)

        # Document
        cp.btn_save.clicked.connect(self._on_save)
        cp.btn_reformat.clicked.connect(self._doc.reformat)
        cp.btn_ai_summary.clicked.connect(self._on_ai_summary)
        cp.btn_clean_notes.clicked.connect(self._on_clean_notes)
        cp.btn_insert_line.clicked.connect(self._on_insert_at_line)

        # Opacity
        cp.slider_opacity.valueChanged.connect(
            lambda v: self.setWindowOpacity(v / 100.0)
        )

    # -----------------------------------------------------------------
    # EventBus → UI wiring
    # -----------------------------------------------------------------

    def _connect_event_bus(self) -> None:
        self._bus.status_changed.connect(self._on_status_changed)
        self._bus.error_occurred.connect(
            lambda mod, msg: self._status_bar.setText(f"[{mod}] {msg}")
        )
        self._bus.doc_saved.connect(
            lambda path: self._status_bar.setText(f"Saved → {path}")
        )
        self._bus.region_selected.connect(self._on_region_selected)

    # -----------------------------------------------------------------
    # Slots
    # -----------------------------------------------------------------

    @pyqtSlot(bool)
    def _on_record_toggled(self, checked: bool) -> None:
        if checked:
            if not self._transcriber.isRunning():
                self._transcriber.start()
            self._audio.start()
            self._bus.audio_chunk_ready.connect(self._transcriber.enqueue_chunk)
        else:
            self._audio.stop()
            self._bus.audio_chunk_ready.disconnect(self._transcriber.enqueue_chunk)
            self._transcriber.flush()

    @pyqtSlot()
    def _on_extract_timestamps(self) -> None:
        from app.transcription.timestamp_utils import hms_to_seconds
        cp = self._control_panel
        start_str = cp.edit_ts_start.text().strip()
        end_str = cp.edit_ts_end.text().strip()
        if not start_str or not end_str:
            self._bus.status_changed.emit("Enter both start and end timestamps.")
            return
        try:
            start_sec = hms_to_seconds(start_str)
            end_sec = hms_to_seconds(end_str)
            self._bus.status_changed.emit(
                f"Extracting {start_str} → {end_str} ({end_sec - start_sec:.1f}s)"
            )
            # Emit as a synthetic audio chunk request (user can extend this
            # to actually slice an audio file and enqueue it)
            self._bus.doc_action_requested.emit(
                "timestamp_extract", {"start": start_sec, "end": end_sec}
            )
        except ValueError as exc:
            self._bus.status_changed.emit(f"Invalid timestamp: {exc}")

    def _open_region_selector(self, mode: str) -> None:
        self._pending_region_mode = mode
        self._region_selector = RegionSelector(self._bus, mode=mode)

    @pyqtSlot(int, int, int, int)
    def _on_region_selected(self, x: int, y: int, w: int, h: int) -> None:
        mode = getattr(self, "_pending_region_mode", "capture")
        if mode == "ocr":
            self._screen.capture_and_ocr(x, y, w, h, self._ocr)
        else:
            self._screen.capture_region(x, y, w, h)

    @pyqtSlot()
    def _on_capture_frame(self) -> None:
        screen_geom = QApplication.primaryScreen().geometry()
        self._screen.capture_region(
            screen_geom.x(), screen_geom.y(),
            screen_geom.width(), screen_geom.height(),
        )

    @pyqtSlot()
    def _on_save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Notes", str(self._doc.get_path()), "Word Document (*.docx)"
        )
        if path:
            self._doc.save(Path(path))
        else:
            self._doc.save()

    @pyqtSlot()
    def _on_ai_summary(self) -> None:
        transcript = self._transcript_view._text.toPlainText()
        if transcript.strip():
            self._ollama.request_summary(transcript)
            self._bus.status_changed.emit("Generating AI summary...")
        else:
            self._bus.status_changed.emit("No transcript to summarize.")

    @pyqtSlot()
    def _on_clean_notes(self) -> None:
        transcript = self._transcript_view._text.toPlainText()
        if transcript.strip():
            self._ollama.request_clean_notes(transcript)
            self._bus.status_changed.emit("Cleaning notes with LLM...")
        else:
            self._bus.status_changed.emit("No transcript to clean.")

    @pyqtSlot()
    def _on_insert_at_line(self) -> None:
        cp = self._control_panel
        try:
            line_num = int(cp.edit_line_num.text())
        except ValueError:
            self._bus.status_changed.emit("Enter a valid line number.")
            return
        text = self._notes_view.get_text()
        if text.strip():
            self._doc.insert_at_line(line_num, text)
            self._bus.status_changed.emit(f"Inserted at line {line_num}.")
        else:
            self._bus.status_changed.emit("Notes view is empty.")

    @pyqtSlot(str)
    def _on_status_changed(self, message: str) -> None:
        # Special internal "opacity:N" message from old slider path — ignore
        if message.startswith("opacity:"):
            return
        self._status_bar.setText(message)

    @pyqtSlot()
    def _on_close(self) -> None:
        self._doc.save()
        if self._audio.is_running:
            self._audio.stop()
        if self._transcriber.isRunning():
            self._transcriber.flush()
            self._transcriber.quit()
            self._transcriber.wait(3000)
        if self._ollama.isRunning():
            self._ollama._queue.put(None)
            self._ollama.quit()
            self._ollama.wait(3000)
        QApplication.quit()

    # -----------------------------------------------------------------
    # Auto-save
    # -----------------------------------------------------------------

    def _start_autosave(self) -> None:
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(60_000)  # every 60 seconds
        self._autosave_timer.timeout.connect(lambda: self._doc.save())
        self._autosave_timer.start()

    # -----------------------------------------------------------------
    # Drag to move
    # -----------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            # Clamp to screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            new_pos.setX(max(screen.left(), min(new_pos.x(), screen.right() - self.width())))
            new_pos.setY(max(screen.top(), min(new_pos.y(), screen.bottom() - self.height())))
            self.move(new_pos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
