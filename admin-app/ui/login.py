import sys

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ui.theme_manager import (
    apply_theme,
    toggle_theme,
    get_current_theme,
    get_theme_palette,
    register_theme_listener,
)


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Online Exam Monitoring System - Admin Portal"
        )

        self.setFixedSize(
            540,
            650
        )

        self.dashboard = None

        self.init_ui()
        register_theme_listener(self._on_theme_changed)

    # =========================================================
    # CREATE LOGIN UI
    # =========================================================

    def init_ui(self):
        self.setObjectName("pageWidget")

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(40, 30, 40, 30)
        root_layout.setAlignment(Qt.AlignCenter)

        # Top bar with Theme Switcher
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        self.themeToggleBtn = QPushButton()
        self.themeToggleBtn.setObjectName("themeToggleBtn")
        self.themeToggleBtn.setCursor(Qt.PointingHandCursor)
        self.themeToggleBtn.setMinimumHeight(34)
        self.update_theme_toggle_text()
        self.themeToggleBtn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.themeToggleBtn)

        root_layout.addLayout(top_bar)

        # Central floating card
        card = QFrame()
        card.setObjectName("card")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(14)

        # -----------------------------------------------------
        # Brand Logo & Badges
        # -----------------------------------------------------
        badge_layout = QHBoxLayout()
        badge_layout.setAlignment(Qt.AlignCenter)

        self.brand_badge = QLabel("🛡️ PROCTOR AI")
        self.brand_badge.setAlignment(Qt.AlignCenter)
        self.brand_badge.setFont(QFont("Segoe UI", 11, QFont.Bold))
        badge_layout.addWidget(self.brand_badge)
        card_layout.addLayout(badge_layout)

        # -----------------------------------------------------
        # Title & Subtitle
        # -----------------------------------------------------
        title = QLabel("Administrator Login")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        subtitle = QLabel("Online Examination & AI Proctoring System")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(6)

        # -----------------------------------------------------
        # Username
        # -----------------------------------------------------
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter administrator username")
        self.username.setMinimumHeight(44)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username)

        # -----------------------------------------------------
        # Password
        # -----------------------------------------------------
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter administrator password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(44)

        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password)

        card_layout.addSpacing(10)

        # -----------------------------------------------------
        # Login Button
        # -----------------------------------------------------
        login_btn = QPushButton("Authenticate & Open Dashboard →")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setMinimumHeight(46)
        login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))

        login_btn.clicked.connect(self.login)
        self.password.returnPressed.connect(self.login)

        card_layout.addWidget(login_btn)

        # -----------------------------------------------------
        # Security Footer Note
        # -----------------------------------------------------
        footer_note = QLabel("Authorized Personnel Only • Secure Proctoring Gateway")
        footer_note.setObjectName("pageSubtitle")
        footer_note.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(footer_note)

        card.setLayout(card_layout)
        root_layout.addWidget(card)

        self.setLayout(root_layout)
        self._apply_badge_style()

    def update_theme_toggle_text(self):
        current = get_current_theme()
        if current == "dark":
            self.themeToggleBtn.setText("🌙 Dark Mode")
        else:
            self.themeToggleBtn.setText("☀️ Light Mode")

    def toggle_theme(self):
        toggle_theme(QApplication.instance())
        self.update_theme_toggle_text()
        self._apply_badge_style()

    def _on_theme_changed(self, theme_name):
        self.update_theme_toggle_text()
        self._apply_badge_style()

    def _apply_badge_style(self):
        p = get_theme_palette()
        self.brand_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {p['badge_info_bg']};
                color: {p['badge_info_text']};
                border: 1px solid {p['badge_info_border']};
                border-radius: 12px;
                padding: 5px 14px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
        """)

    # =========================================================
    # LOGIN
    # =========================================================

    def login(self):

        username = self.username.text().strip()
        password = self.password.text()

        # -----------------------------------------------------
        # Check credentials
        # -----------------------------------------------------

        if (
            username == "admin"
            and password == "admin123"
        ):

            self.open_dashboard()

        else:

            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid Username or Password"
            )

            self.password.clear()
            self.password.setFocus()

    # =========================================================
    # OPEN DASHBOARD
    # =========================================================

    def open_dashboard(self):

        try:

            from ui.dashboard import Dashboard

            self.dashboard = Dashboard()
            self.dashboard.show()
            self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Dashboard Error",
                f"Unable to open dashboard.\n\n{e}"
            )


# =============================================================
# STANDALONE TEST
# =============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )
    apply_theme(app, "light")

    window = LoginWindow()
    window.show()

    sys.exit(
        app.exec_()
    )