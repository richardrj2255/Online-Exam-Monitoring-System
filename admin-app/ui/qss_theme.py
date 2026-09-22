"""
QSS Theme and Design System for Online Exam Monitoring System (admin-app).
Based on the AI Online Exam Management Dashboard modern dark-mode aesthetic:
- Main Background Canvas: Deep Slate (#0F172A)
- Card & Panel Containers: #1E293B with 1px border (#334155) and rounded corners (10-12px)
- Primary Accent: Indigo/Violet (#6366F1), hover (#4F46E5), pressed (#4338CA)
- Success / Emerald: Background #064E3B, Text #34D399, Border #059669
- Warning / Rose: Background #881337, Text #FDA4AF, Border #E11D48
- Neutral / Slate: Background #1E293B / #334155, Text #94A3B8
- Info / Accent: Background #1E1B4B, Text #818CF8
- Text: Primary #F8FAFC, Secondary #94A3B8, Muted #64748B
- Font: Segoe UI, Inter, Roboto, sans-serif
"""

from PyQt5.QtWidgets import QLabel, QFrame, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


# =====================================================================
# COLOR PALETTE CONSTANTS
# =====================================================================

BG_CANVAS = "#0F172A"       # Deep slate main window canvas
BG_CARD = "#1E293B"         # Panel & card container background
BG_CARD_ALT = "#162032"     # Alternating card / table row
BG_INPUT = "#0F172A"        # Input background
BG_SIDEBAR = "#0B1120"      # Darker navigation sidebar
BORDER_SUBTLE = "#334155"   # 1px crisp border
BORDER_FOCUS = "#6366F1"    # Focus state border ring

COLOR_PRIMARY = "#6366F1"   # Indigo accent
COLOR_PRIMARY_HOVER = "#4F46E5"
COLOR_PRIMARY_PRESSED = "#4338CA"

TEXT_PRIMARY = "#F8FAFC"    # Crisp heading & label white
TEXT_SECONDARY = "#94A3B8"  # Subtitle muted gray
TEXT_MUTED = "#64748B"      # Disabled / placeholder slate

# Status badge colors
BADGE_SUCCESS_BG = "#064E3B"
BADGE_SUCCESS_TEXT = "#34D399"
BADGE_SUCCESS_BORDER = "#059669"

BADGE_DANGER_BG = "#881337"
BADGE_DANGER_TEXT = "#FDA4AF"
BADGE_DANGER_BORDER = "#E11D48"

BADGE_WARNING_BG = "#78350F"
BADGE_WARNING_TEXT = "#FDE68A"
BADGE_WARNING_BORDER = "#D97706"

BADGE_INFO_BG = "#1E1B4B"
BADGE_INFO_TEXT = "#A5B4FC"
BADGE_INFO_BORDER = "#4F46E5"

BADGE_NEUTRAL_BG = "#1E293B"
BADGE_NEUTRAL_TEXT = "#94A3B8"
BADGE_NEUTRAL_BORDER = "#334155"


# =====================================================================
# GLOBAL QSS STYLESHEET
# =====================================================================

def get_main_stylesheet():
    return f"""
    /* Global Base */
    QMainWindow, QDialog, QWidget {{
        background-color: {BG_CANVAS};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", "Inter", "Roboto", -apple-system, sans-serif;
        font-size: 13px;
    }}

    /* Card Panels & Containers */
    QFrame#card, QFrame.card, QGroupBox {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
    }}

    QGroupBox {{
        font-weight: bold;
        font-size: 14px;
        color: {TEXT_PRIMARY};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        color: {COLOR_PRIMARY};
    }}

    /* Labels */
    QLabel {{
        color: {TEXT_PRIMARY};
        background: transparent;
    }}

    QLabel#heading {{
        font-size: 22px;
        font-weight: bold;
        color: {TEXT_PRIMARY};
    }}

    QLabel#subtitle {{
        font-size: 13px;
        color: {TEXT_SECONDARY};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLOR_PRIMARY};
        color: #FFFFFF;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {COLOR_PRIMARY_HOVER};
    }}

    QPushButton:pressed {{
        background-color: {COLOR_PRIMARY_PRESSED};
    }}

    QPushButton:disabled {{
        background-color: {BG_CARD};
        color: {TEXT_MUTED};
        border: 1px solid {BORDER_SUBTLE};
    }}

    /* Secondary / Outline Button */
    QPushButton#secondaryBtn, QPushButton.secondary {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
    }}

    QPushButton#secondaryBtn:hover, QPushButton.secondary:hover {{
        background-color: #243248;
        border-color: #475569;
    }}

    /* Danger Button */
    QPushButton#dangerBtn, QPushButton.danger {{
        background-color: {BADGE_DANGER_BG};
        color: {BADGE_DANGER_TEXT};
        border: 1px solid {BADGE_DANGER_BORDER};
    }}

    QPushButton#dangerBtn:hover, QPushButton.danger:hover {{
        background-color: #9F1239;
        color: #FFFFFF;
    }}

    /* Success Button */
    QPushButton#successBtn, QPushButton.success {{
        background-color: {BADGE_SUCCESS_BG};
        color: {BADGE_SUCCESS_TEXT};
        border: 1px solid {BADGE_SUCCESS_BORDER};
    }}

    QPushButton#successBtn:hover, QPushButton.success:hover {{
        background-color: #065F46;
        color: #FFFFFF;
    }}

    /* Input Controls */
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: {COLOR_PRIMARY};
        selection-color: #FFFFFF;
        font-size: 13px;
    }}

    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {BORDER_FOCUS};
        background-color: #111C2E;
    }}

    QLineEdit::placeholder, QTextEdit::placeholder {{
        color: {TEXT_MUTED};
    }}

    /* Dropdown / Combobox */
    QComboBox {{
        padding-right: 24px;
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid {BORDER_SUBTLE};
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
        background: {BG_CARD};
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY};
        width: 0;
        height: 0;
        margin: 0 auto;
    }}

    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {COLOR_PRIMARY};
        selection-color: #FFFFFF;
        outline: none;
    }}

    /* Table Widget */
    QTableWidget, QTableView {{
        background-color: {BG_CARD};
        alternate-background-color: {BG_CARD_ALT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 10px;
        gridline-color: #273549;
        selection-background-color: #312E81;
        selection-color: #FFFFFF;
        outline: none;
    }}

    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid #243248;
    }}

    QTableWidget::item:selected {{
        background-color: #312E81;
        color: #FFFFFF;
    }}

    QTableWidget::item:hover {{
        background-color: #243248;
    }}

    QHeaderView::section {{
        background-color: {BG_CANVAS};
        color: {TEXT_SECONDARY};
        padding: 10px 12px;
        border: none;
        border-bottom: 1px solid {BORDER_SUBTLE};
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Modern Slim Scrollbar */
    QScrollBar:vertical {{
        background: {BG_CANVAS};
        width: 8px;
        margin: 0;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical {{
        background: {BORDER_SUBTLE};
        min-height: 24px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {COLOR_PRIMARY};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
        background: transparent;
    }}

    QScrollBar:horizontal {{
        background: {BG_CANVAS};
        height: 8px;
        margin: 0;
        border-radius: 4px;
    }}

    QScrollBar::handle:horizontal {{
        background: {BORDER_SUBTLE};
        min-width: 24px;
        border-radius: 4px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {COLOR_PRIMARY};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
        background: transparent;
    }}

    /* Scroll Area */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}

    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 10px;
        background: {BG_CARD};
    }}

    QTabBar::tab {{
        background: {BG_CANVAS};
        color: {TEXT_SECONDARY};
        padding: 8px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 4px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        background: {COLOR_PRIMARY};
        color: #FFFFFF;
    }}

    /* Message Box */
    QMessageBox {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER_SUBTLE};
    }}

    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
    }}
    """


# =====================================================================
# UI HELPER: STATUS BADGE WIDGET
# =====================================================================

class StatusBadge(QFrame):
    """
    Sleek pill status badge for tables and cards (e.g. 'Live - Normal', 'Flagged', 'Submitted').
    """
    def __init__(self, text, variant="neutral", parent=None):
        super().__init__(parent)

        if variant == "success":
            bg = BADGE_SUCCESS_BG
            fg = BADGE_SUCCESS_TEXT
            border = BADGE_SUCCESS_BORDER
            dot_color = BADGE_SUCCESS_TEXT
        elif variant in ("danger", "warning", "rose"):
            bg = BADGE_DANGER_BG
            fg = BADGE_DANGER_TEXT
            border = BADGE_DANGER_BORDER
            dot_color = BADGE_DANGER_TEXT
        elif variant == "amber":
            bg = BADGE_WARNING_BG
            fg = BADGE_WARNING_TEXT
            border = BADGE_WARNING_BORDER
            dot_color = BADGE_WARNING_TEXT
        elif variant in ("info", "indigo"):
            bg = BADGE_INFO_BG
            fg = BADGE_INFO_TEXT
            border = BADGE_INFO_BORDER
            dot_color = BADGE_INFO_TEXT
        else:
            bg = BADGE_NEUTRAL_BG
            fg = BADGE_NEUTRAL_TEXT
            border = BADGE_NEUTRAL_BORDER
            dot_color = BADGE_NEUTRAL_TEXT

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
                padding: 3px 8px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 2, 8, 2)
        layout.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 8px; background: transparent; border: none;")

        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {fg}; font-size: 11px; font-weight: 700; background: transparent; border: none;")

        layout.addWidget(dot)
        layout.addWidget(lbl)
        self.setLayout(layout)


def create_badge_widget(text, variant="neutral"):
    """
    Creates a container QWidget with centered StatusBadge to place directly in QTableWidget.
    """
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setAlignment(Qt.AlignCenter)
    badge = StatusBadge(text, variant)
    layout.addWidget(badge)
    return container
