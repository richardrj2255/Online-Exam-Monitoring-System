"""
QSS Theme and Design System for Online Exam Monitoring System (admin-app).
Supports both:
- ☀️ Light Theme (Default / Professional Modern)
- 🌙 Dark Theme (Executive Mode)
Provides backward compatibility for existing imports and reactive badges.
"""

from PyQt5.QtWidgets import QLabel, QFrame, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ui.theme_manager import (
    LIGHT_THEME_QSS,
    DARK_THEME_QSS,
    LIGHT_PALETTE,
    DARK_PALETTE,
    get_current_theme,
    get_theme_palette,
    get_theme_stylesheet,
    apply_theme,
    toggle_theme,
    register_theme_listener,
    unregister_theme_listener,
)


# =====================================================================
# DYNAMIC COLOR GETTERS FOR BACKWARD COMPATIBILITY
# =====================================================================

def _get_current_palette():
    return get_theme_palette()

# Expose constants that default to current active theme palette
BG_CANVAS = LIGHT_PALETTE["bg_canvas"]
BG_CARD = LIGHT_PALETTE["bg_card"]
BG_CARD_ALT = LIGHT_PALETTE["bg_card_alt"]
BG_INPUT = LIGHT_PALETTE["bg_input"]
BG_SIDEBAR = LIGHT_PALETTE["bg_sidebar"]
BORDER_SUBTLE = LIGHT_PALETTE["border_subtle"]
BORDER_FOCUS = LIGHT_PALETTE["border_focus"]

COLOR_PRIMARY = LIGHT_PALETTE["color_primary"]
COLOR_PRIMARY_HOVER = LIGHT_PALETTE["color_primary_hover"]
COLOR_PRIMARY_PRESSED = LIGHT_PALETTE["color_primary_pressed"]

TEXT_PRIMARY = LIGHT_PALETTE["text_primary"]
TEXT_SECONDARY = LIGHT_PALETTE["text_secondary"]
TEXT_MUTED = LIGHT_PALETTE["text_muted"]

BADGE_SUCCESS_BG = LIGHT_PALETTE["badge_success_bg"]
BADGE_SUCCESS_TEXT = LIGHT_PALETTE["badge_success_text"]
BADGE_SUCCESS_BORDER = LIGHT_PALETTE["badge_success_border"]

BADGE_DANGER_BG = LIGHT_PALETTE["badge_danger_bg"]
BADGE_DANGER_TEXT = LIGHT_PALETTE["badge_danger_text"]
BADGE_DANGER_BORDER = LIGHT_PALETTE["badge_danger_border"]

BADGE_WARNING_BG = LIGHT_PALETTE["badge_warning_bg"]
BADGE_WARNING_TEXT = LIGHT_PALETTE["badge_warning_text"]
BADGE_WARNING_BORDER = LIGHT_PALETTE["badge_warning_border"]

BADGE_INFO_BG = LIGHT_PALETTE["badge_info_bg"]
BADGE_INFO_TEXT = LIGHT_PALETTE["badge_info_text"]
BADGE_INFO_BORDER = LIGHT_PALETTE["badge_info_border"]

BADGE_NEUTRAL_BG = LIGHT_PALETTE["badge_neutral_bg"]
BADGE_NEUTRAL_TEXT = LIGHT_PALETTE["badge_neutral_text"]
BADGE_NEUTRAL_BORDER = LIGHT_PALETTE["badge_neutral_border"]


# =====================================================================
# GLOBAL QSS STYLESHEET
# =====================================================================

def get_main_stylesheet():
    """Returns the current active theme stylesheet."""
    return get_theme_stylesheet()


# =====================================================================
# UI HELPER: STATUS BADGE WIDGET (THEME-REACTIVE)
# =====================================================================

class StatusBadge(QFrame):
    """
    Sleek pill status badge for tables and cards (e.g. 'Live - Normal', 'Flagged', 'Submitted').
    Dynamically updates its color scheme when theme toggles.
    """
    def __init__(self, text, variant="neutral", parent=None):
        super().__init__(parent)
        self.text = text
        self.variant = variant

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(8, 3, 10, 3)
        self.layout.setSpacing(6)

        self.dot = QLabel("●")
        self.lbl = QLabel(text)

        self.layout.addWidget(self.dot)
        self.layout.addWidget(self.lbl)
        self.setLayout(self.layout)

        self.update_style()
        register_theme_listener(self._on_theme_changed)

    def _on_theme_changed(self, theme_name):
        try:
            self.update_style()
        except RuntimeError:
            # Widget might have been deleted by Qt
            pass

    def update_style(self):
        palette = get_theme_palette()
        v = self.variant.lower()

        if v in ("success", "normal", "active", "nominal"):
            bg = palette["badge_success_bg"]
            fg = palette["badge_success_text"]
            border = palette["badge_success_border"]
            dot_color = palette["badge_success_text"]
        elif v in ("danger", "warning", "rose", "alert", "flagged"):
            bg = palette["badge_danger_bg"]
            fg = palette["badge_danger_text"]
            border = palette["badge_danger_border"]
            dot_color = palette["badge_danger_text"]
        elif v in ("amber", "caution"):
            bg = palette["badge_warning_bg"]
            fg = palette["badge_warning_text"]
            border = palette["badge_warning_border"]
            dot_color = palette["badge_warning_text"]
        elif v in ("info", "indigo", "scheduled"):
            bg = palette["badge_info_bg"]
            fg = palette["badge_info_text"]
            border = palette["badge_info_border"]
            dot_color = palette["badge_info_text"]
        else:
            bg = palette["badge_neutral_bg"]
            fg = palette["badge_neutral_text"]
            border = palette["badge_neutral_border"]
            dot_color = palette["badge_neutral_text"]

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)
        self.dot.setStyleSheet(f"color: {dot_color}; font-size: 8px; background: transparent; border: none;")
        self.lbl.setStyleSheet(f"color: {fg}; font-size: 11px; font-weight: 700; background: transparent; border: none;")


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
