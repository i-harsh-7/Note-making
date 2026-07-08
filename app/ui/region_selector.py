from PyQt6.QtWidgets import QWidget, QRubberBand, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QMouseEvent, QPen

from app.event_bus import EventBus


class RegionSelector(QWidget):
    """Full-screen rubber-band overlay for selecting a screen capture region.

    Shown modally over the entire screen. On mouse release, emits
    EventBus.region_selected(x, y, w, h) and closes itself.
    """

    def __init__(self, event_bus: EventBus, mode: str = "capture", parent=None):
        """
        mode: "capture" — take screenshot of selection
              "ocr"     — capture + immediately run OCR
        """
        super().__init__(parent)
        self._bus = event_bus
        self._mode = mode
        self._origin = QPoint()
        self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)

        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Cover all screens
        virtual_geom = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(virtual_geom)
        self.showFullScreen()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.pos()
            self._rubber_band.setGeometry(QRect(self._origin, QSize()))
            self._rubber_band.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._origin.isNull():
            self._rubber_band.setGeometry(
                QRect(self._origin, event.pos()).normalized()
            )

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            rect = QRect(self._origin, event.pos()).normalized()
            self._rubber_band.hide()
            self.close()

            if rect.width() > 4 and rect.height() > 4:
                self._bus.region_selected.emit(
                    rect.x(), rect.y(), rect.width(), rect.height()
                )

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._rubber_band.hide()
            self.close()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))  # dim overlay
        painter.end()
