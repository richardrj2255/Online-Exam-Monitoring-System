"""
Theme Manager for Online Exam Monitoring System (admin-app).
Provides a dynamic dual-theme engine supporting:
- ☀️ Light Theme (Default / Professional Modern)
- 🌙 Dark Theme (Executive Mode)
Live switching without restarting the application or dropping backend state.
"""

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

# =====================================================================
# THEME COLOR CONSTANTS & PALETTES
# =====================================================================

LIGHT_PALETTE = {
    "name": "light",
    "bg_canvas": "#F8FAFC",
    "bg_card": "#FFFFFF",
    "bg_card_alt": "#F1F5F9",
    "bg_sidebar": "#FFFFFF",
    "bg_header": "#FFFFFF",
    "bg_input": "#FFFFFF",
    "bg_input_focus": "#F8FAFC",
    "border_subtle": "#E2E8F0",
    "border_card": "#E2E8F0",
    "border_focus": "#4F46E5",
    "border_hover": "#818CF8",
    "color_primary": "#4F46E5",
    "color_primary_hover": "#4338CA",
    "color_primary_pressed": "#3730A3",
    "text_primary": "#0F172A",
    "text_secondary": "#64748B",
    "text_muted": "#94A3B8",
    # Status badges
    "badge_success_bg": "#DCFCE7",
    "badge_success_text": "#15803D",
    "badge_success_border": "#86EFAC",
    "badge_danger_bg": "#FFE4E6",
    "badge_danger_text": "#BE123C",
    "badge_danger_border": "#FDA4AF",
    "badge_warning_bg": "#FEF3C7",
    "badge_warning_text": "#B45309",
    "badge_warning_border": "#FCD34D",
    "badge_info_bg": "#EEF2FF",
    "badge_info_text": "#4338CA",
    "badge_info_border": "#C7D2FE",
    "badge_neutral_bg": "#F1F5F9",
    "badge_neutral_text": "#475569",
    "badge_neutral_border": "#CBD5E1",
    # Table specific
    "table_bg": "#FFFFFF",
    "table_alt_bg": "#F8FAFC",
    "table_header_bg": "#F1F5F9",
    "table_grid": "#E2E8F0",
    "table_hover": "#EEF2F6",
    "table_select_bg": "#E0E7FF",
    "table_select_text": "#1E1B4B",
    # Camera container
    "camera_screen_bg": "#F1F5F9",
    "camera_screen_border": "#CBD5E1",
    "camera_screen_text": "#475569",
}

DARK_PALETTE = {
    "name": "dark",
    "bg_canvas": "#0F172A",
    "bg_card": "#1E293B",
    "bg_card_alt": "#162032",
    "bg_sidebar": "#0B1120",
    "bg_header": "#1E293B",
    "bg_input": "#0F172A",
    "bg_input_focus": "#111C2E",
    "border_subtle": "#334155",
    "border_card": "#334155",
    "border_focus": "#6366F1",
    "border_hover": "#818CF8",
    "color_primary": "#6366F1",
    "color_primary_hover": "#4F46E5",
    "color_primary_pressed": "#4338CA",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    # Status badges
    "badge_success_bg": "#064E3B",
    "badge_success_text": "#34D399",
    "badge_success_border": "#059669",
    "badge_danger_bg": "#881337",
    "badge_danger_text": "#FDA4AF",
    "badge_danger_border": "#E11D48",
    "badge_warning_bg": "#78350F",
    "badge_warning_text": "#FDE68A",
    "badge_warning_border": "#D97706",
    "badge_info_bg": "#1E1B4B",
    "badge_info_text": "#A5B4FC",
    "badge_info_border": "#4F46E5",
    "badge_neutral_bg": "#1E293B",
    "badge_neutral_text": "#94A3B8",
    "badge_neutral_border": "#334155",
    # Table specific
    "table_bg": "#1E293B",
    "table_alt_bg": "#162032",
    "table_header_bg": "#0F172A",
    "table_grid": "#273549",
    "table_hover": "#243248",
    "table_select_bg": "#312E81",
    "table_select_text": "#FFFFFF",
    # Camera container
    "camera_screen_bg": "#090D16",
    "camera_screen_border": "#334155",
    "camera_screen_text": "#64748B",
}


# =====================================================================
# QSS GENERATOR
# =====================================================================

def _build_stylesheet(p: dict) -> str:
    """Builds the comprehensive QSS stylesheet for the given palette dictionary."""
    return f"""
    /* =====================================================================
       Online Exam Monitoring System - Modern Responsive QSS Theme: {p['name'].upper()}
       ===================================================================== */

    /* Global Base & Canvas */
    QMainWindow, QDialog, QWidget#centralWidget, QWidget#pageWidget, QWidget#rootWidget {{
        background-color: {p['bg_canvas']};
        color: {p['text_primary']};
        font-family: "Segoe UI", "Inter", "Roboto", -apple-system, sans-serif;
        font-size: 13px;
    }}

    /* Card Panels & Containers */
    QFrame#card, QFrame.card, QGroupBox {{
        background-color: {p['bg_card']};
        border: 1px solid {p['border_card']};
        border-radius: 12px;
        padding: 16px;
    }}

    QFrame#card:hover, QGroupBox:hover {{
        border: 1px solid {p['border_hover']};
    }}

    /* Structured Metric Cards */
    QFrame#card_metric {{
        background-color: {p['bg_card']};
        border: 1px solid {p['border_card']};
        border-radius: 10px;
        padding: 10px 16px;
    }}

    QFrame#card_metric:hover {{
        border: 1px solid {p['border_hover']};
    }}

    QFrame#headerCard, QFrame#tableCard {{
        background-color: {p['bg_card']};
        border: 1px solid {p['border_card']};
        border-radius: 14px;
    }}

    QFrame#headerCard:hover, QFrame#tableCard:hover {{
        border: 1px solid {p['border_hover']};
    }}

    /* Top Header Bar */
    QFrame#topHeader {{
        background-color: {p['bg_header']};
        border-bottom: 1px solid {p['border_subtle']};
    }}

    /* Navigation Sidebar */
    QFrame#sidebar {{
        background-color: {p['bg_sidebar']};
        border-right: 1px solid {p['border_subtle']};
    }}

    /* GroupBox Title */
    QGroupBox {{
        font-weight: 700;
        font-size: 15px;
        color: {p['text_primary']};
        margin-top: 14px;
        padding-top: 10px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        color: {p['color_primary']};
    }}

    /* Global Labels & Text Hierarchy */
    QLabel {{
        color: {p['text_primary']};
        background: transparent;
        font-size: 13px;
    }}

    QLabel#heading, QLabel#pageTitle {{
        font-size: 22px;
        font-weight: 800;
        color: {p['text_primary']};
        letter-spacing: -0.3px;
    }}

    QLabel#sectionHeader {{
        font-size: 16px;
        font-weight: 700;
        color: {p['text_primary']};
    }}

    QLabel#subtitle, QLabel#pageSubtitle {{
        font-size: 13px;
        color: {p['text_secondary']};
        font-weight: 400;
    }}

    QLabel#kpiValue {{
        font-size: 28px;
        font-weight: 800;
        color: {p['text_primary']};
    }}

    QLabel#kpiTitle {{
        font-size: 13px;
        font-weight: 600;
        color: {p['text_secondary']};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {p['color_primary']};
        color: #FFFFFF;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {p['color_primary_hover']};
    }}

    QPushButton:pressed {{
        background-color: {p['color_primary_pressed']};
    }}

    QPushButton:disabled {{
        background-color: {p['bg_card_alt']};
        color: {p['text_muted']};
        border: 1px solid {p['border_subtle']};
    }}

    /* Secondary / Outline Button */
    QPushButton#secondaryBtn, QPushButton.secondary {{
        background-color: {p['bg_card']};
        color: {p['text_primary']};
        border: 1px solid {p['border_subtle']};
    }}

    QPushButton#secondaryBtn:hover, QPushButton.secondary:hover {{
        background-color: {p['bg_card_alt']};
        border-color: {p['border_hover']};
        color: {p['color_primary']};
    }}

    /* Danger Button */
    QPushButton#dangerBtn, QPushButton.danger {{
        background-color: {p['badge_danger_bg']};
        color: {p['badge_danger_text']};
        border: 1px solid {p['badge_danger_border']};
        font-weight: 600;
    }}

    QPushButton#dangerBtn:hover, QPushButton.danger:hover {{
        background-color: #E11D48;
        color: #FFFFFF;
        border-color: #BE123C;
    }}

    /* Success Button */
    QPushButton#successBtn, QPushButton.success {{
        background-color: {p['badge_success_bg']};
        color: {p['badge_success_text']};
        border: 1px solid {p['badge_success_border']};
        font-weight: 600;
    }}

    QPushButton#successBtn:hover, QPushButton.success:hover {{
        background-color: #059669;
        color: #FFFFFF;
        border-color: #047857;
    }}

    /* Navigation Sidebar Buttons */
    QPushButton#navBtn {{
        color: {p['text_secondary']};
        background-color: transparent;
        border: none;
        border-radius: 8px;
        text-align: left;
        padding: 11px 16px;
        font-size: 13px;
        font-weight: 500;
    }}

    QPushButton#navBtn:hover {{
        color: {p['text_primary']};
        background-color: {p['bg_card_alt']};
    }}

    QPushButton#navBtn[active="true"] {{
        color: #FFFFFF;
        background-color: {p['color_primary']};
        border-left: 4px solid {p['color_primary_pressed']};
        font-weight: 700;
    }}

    /* Theme Toggle Switch Button */
    QPushButton#themeToggleBtn {{
        background-color: {p['bg_card_alt']};
        color: {p['text_primary']};
        border: 1px solid {p['border_subtle']};
        border-radius: 18px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
    }}

    QPushButton#themeToggleBtn:hover {{
        background-color: {p['bg_card']};
        border-color: {p['color_primary']};
        color: {p['color_primary']};
    }}

    /* Input Controls */
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {p['bg_input']};
        color: {p['text_primary']};
        border: 1px solid {p['border_subtle']};
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: {p['color_primary']};
        selection-color: #FFFFFF;
        font-size: 13px;
    }}

    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {p['border_focus']};
        background-color: {p['bg_input_focus']};
    }}

    QLineEdit::placeholder, QTextEdit::placeholder {{
        color: {p['text_muted']};
    }}

    /* Dropdown / Combobox */
    QComboBox {{
        padding-right: 28px;
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid {p['border_subtle']};
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
        background: {p['bg_card_alt']};
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {p['text_secondary']};
        width: 0;
        height: 0;
        margin: 0 auto;
    }}

    QComboBox QAbstractItemView,
    QComboBox QListView {{
        background-color: {p['bg_card']};
        color: {p['text_primary']};
        border: 1px solid {p['border_subtle']};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {p['color_primary']};
        selection-color: #FFFFFF;
        outline: none;
    }}

    QComboBox QAbstractItemView::item,
    QComboBox QListView::item {{
        padding: 6px 10px;
        color: {p['text_primary']};
        background-color: {p['bg_card']};
        border-radius: 4px;
        min-height: 24px;
    }}

    QComboBox QAbstractItemView::item:hover,
    QComboBox QListView::item:hover,
    QComboBox QAbstractItemView::item:selected,
    QComboBox QListView::item:selected {{
        background-color: {p['table_hover']};
        color: {p['color_primary']};
    }}

    /* Table Widget */
    QTableWidget, QTableView {{
        background-color: {p['table_bg']};
        alternate-background-color: {p['table_alt_bg']};
        color: {p['text_primary']};
        border: 1px solid {p['border_subtle']};
        border-radius: 10px;
        gridline-color: {p['table_grid']};
        selection-background-color: {p['table_select_bg']};
        selection-color: {p['table_select_text']};
        font-size: 13px;
        outline: none;
    }}

    QTableWidget::item {{
        padding: 9px 12px;
        border-bottom: 1px solid {p['table_grid']};
    }}

    QTableWidget::item:selected {{
        background-color: {p['table_select_bg']};
        color: {p['table_select_text']};
    }}

    QTableWidget::item:hover {{
        background-color: {p['table_hover']};
    }}

    QHeaderView::section {{
        background-color: {p['table_header_bg']};
        color: {p['text_secondary']};
        padding: 10px 14px;
        border: none;
        border-bottom: 1px solid {p['border_subtle']};
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Table Action Buttons */
    QTableWidget QPushButton,
    QTableView QPushButton,
    QTableWidget QWidget QPushButton,
    QTableView QWidget QPushButton {{
        padding: 4px 8px;
        font-size: 12px;
        min-height: 26px;
        border-radius: 6px;
    }}

    /* Video Feed Containers */
    QLabel#cameraFeed {{
        background-color: {p['camera_screen_bg']};
        color: {p['camera_screen_text']};
        border: 1px solid {p['camera_screen_border']};
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
    }}

    QLabel#cameraFeed:hover {{
        border-color: {p['border_hover']};
    }}

    QFrame#cameraCard {{
        background-color: {p['bg_card']};
        border: 1px solid {p['border_card']};
        border-radius: 14px;
    }}

    QFrame#cameraCard:hover {{
        border: 1px solid {p['border_hover']};
    }}

    QFrame#cameraCard[flagged="true"] {{
        border: 2px solid {p['badge_danger_border']};
    }}

    /* Modern Slim Scrollbar */
    QScrollBar:vertical {{
        background: {p['bg_canvas']};
        width: 8px;
        margin: 0;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical {{
        background: {p['border_subtle']};
        min-height: 24px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {p['color_primary']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
        background: transparent;
    }}

    QScrollBar:horizontal {{
        background: {p['bg_canvas']};
        height: 8px;
        margin: 0;
        border-radius: 4px;
    }}

    QScrollBar::handle:horizontal {{
        background: {p['border_subtle']};
        min-width: 24px;
        border-radius: 4px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {p['color_primary']};
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
        border: 1px solid {p['border_subtle']};
        border-radius: 10px;
        background: {p['bg_card']};
    }}

    QTabBar::tab {{
        background: {p['bg_canvas']};
        color: {p['text_secondary']};
        padding: 9px 18px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 4px;
        font-weight: 600;
        font-size: 13px;
    }}

    QTabBar::tab:selected {{
        background: {p['color_primary']};
        color: #FFFFFF;
    }}

    /* Message Box */
    QMessageBox {{
        background-color: {p['bg_card']};
        border: 1px solid {p['border_subtle']};
    }}

    QMessageBox QLabel {{
        color: {p['text_primary']};
        font-size: 13px;
    }}
    """


LIGHT_THEME_QSS = _build_stylesheet(LIGHT_PALETTE)
DARK_THEME_QSS = _build_stylesheet(DARK_PALETTE)


# =====================================================================
# THEME ENGINE STATE & MANAGER
# =====================================================================

class ThemeEngine(QObject):
    """
    Singleton Theme Engine managing live stylesheet switching and theme listeners.
    """
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current_theme = "light"  # Default light theme
        self._listeners = []

    @property
    def current_theme(self) -> str:
        return self._current_theme

    def get_palette(self, theme_name: str = None) -> dict:
        theme = theme_name or self._current_theme
        return DARK_PALETTE if theme == "dark" else LIGHT_PALETTE

    def get_stylesheet(self, theme_name: str = None) -> str:
        theme = theme_name or self._current_theme
        return DARK_THEME_QSS if theme == "dark" else LIGHT_THEME_QSS

    def apply_theme(self, app_or_widget, theme_name: str):
        """
        Applies the selected theme live without restarting the application.
        Can receive QApplication instance, QMainWindow, or QWidget.
        """
        theme_name = theme_name.lower().strip()
        if theme_name not in ("light", "dark"):
            theme_name = "light"

        self._current_theme = theme_name
        qss = self.get_stylesheet(theme_name)

        if app_or_widget is not None:
            if hasattr(app_or_widget, "setStyleSheet"):
                app_or_widget.setStyleSheet(qss)
            elif isinstance(app_or_widget, type) and issubclass(app_or_widget, QApplication):
                instance = QApplication.instance()
                if instance:
                    instance.setStyleSheet(qss)

        # Notify registered listeners
        self.theme_changed.emit(theme_name)
        for listener in list(self._listeners):
            try:
                listener(theme_name)
            except Exception as e:
                print("Theme listener error:", e)

    def toggle_theme(self, app_or_widget = None) -> str:
        """Toggles between light and dark themes."""
        new_theme = "dark" if self._current_theme == "light" else "light"
        target = app_or_widget or QApplication.instance()
        self.apply_theme(target, new_theme)
        return new_theme

    def register_theme_listener(self, callback):
        """Registers a callback function to be called with (theme_name) when theme changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_theme_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)


# Singleton Instance
_THEME_ENGINE = ThemeEngine()


# =====================================================================
# PUBLIC API FUNCTIONS
# =====================================================================

def get_current_theme() -> str:
    return _THEME_ENGINE.current_theme

def get_theme_palette(theme_name: str = None) -> dict:
    return _THEME_ENGINE.get_palette(theme_name)

def get_theme_stylesheet(theme_name: str = None) -> str:
    return _THEME_ENGINE.get_stylesheet(theme_name)

def apply_theme(app_or_widget, theme_name: str):
    _THEME_ENGINE.apply_theme(app_or_widget, theme_name)

def toggle_theme(app_or_widget = None) -> str:
    return _THEME_ENGINE.toggle_theme(app_or_widget)

def register_theme_listener(callback):
    _THEME_ENGINE.register_theme_listener(callback)

def unregister_theme_listener(callback):
    _THEME_ENGINE.unregister_theme_listener(callback)
