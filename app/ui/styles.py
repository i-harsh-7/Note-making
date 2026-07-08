OPACITY_DEFAULT = 0.93
OPACITY_MIN = 0.4
OPACITY_MAX = 1.0

WIDGET_W = 420
WIDGET_H = 620

ACCENT = "#4C9FE8"
ACCENT_HOVER = "#2E86D9"
DANGER = "#E05C5C"
DANGER_HOVER = "#C94040"
SUCCESS = "#4CAF80"
BG_DARK = "#1A1D23"
BG_PANEL = "#22262E"
BG_INPUT = "#2B2F38"
TEXT_PRIMARY = "#E8EAF0"
TEXT_SECONDARY = "#8B95A8"
BORDER = "#363C4A"

MAIN_STYLE = f"""
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Text', 'Inter', sans-serif;
    font-size: 13px;
    border-radius: 12px;
}}
QTextEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px;
    color: {TEXT_PRIMARY};
    font-size: 12px;
    selection-background-color: {ACCENT};
}}
QScrollBar:vertical {{
    background: {BG_PANEL};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QLabel {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
}}
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    color: {TEXT_PRIMARY};
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}
"""

BTN_PRIMARY = f"""
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton:pressed {{
    background-color: #1A6DB8;
}}
QPushButton:disabled {{
    background-color: {BORDER};
    color: {TEXT_SECONDARY};
}}
"""

BTN_DANGER = f"""
QPushButton {{
    background-color: {DANGER};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {DANGER_HOVER};
}}
QPushButton:pressed {{
    background-color: #A83030;
}}
"""

BTN_SECONDARY = f"""
QPushButton {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {BG_INPUT};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {BORDER};
}}
"""

TITLE_BAR_STYLE = f"""
QWidget {{
    background-color: {BG_PANEL};
    border-radius: 10px 10px 0px 0px;
}}
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    font-weight: 600;
}}
"""

STATUS_BAR_STYLE = f"""
QLabel {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
    padding: 2px 8px;
    background-color: {BG_PANEL};
    border-radius: 0px 0px 10px 10px;
}}
"""
