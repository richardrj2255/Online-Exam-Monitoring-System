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

from ui.qss_theme import (
    get_main_stylesheet,
    BG_CANVAS,
    BG_CARD,
    BORDER_SUBTLE,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
    BADGE_INFO_BORDER
)


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Online Exam Monitoring System - Admin Portal"
        )

        self.setFixedSize(
            520,
            620
        )

        self.dashboard = None

        self.init_ui()

    # =========================================================
    # CREATE LOGIN UI
    # =========================================================

    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CANVAS};
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }}
        """)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(40, 40, 40, 40)
        root_layout.setAlignment(Qt.AlignCenter)

        # Central floating card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 16px;
            }}
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(14)

        # -----------------------------------------------------
        # Brand Logo & Badges
        # -----------------------------------------------------
        badge_layout = QHBoxLayout()
        badge_layout.setAlignment(Qt.AlignCenter)

        brand_badge = QLabel("🛡️ PROCTOR AI")
        brand_badge.setAlignment(Qt.AlignCenter)
        brand_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
        """)
        badge_layout.addWidget(brand_badge)
        card_layout.addLayout(badge_layout)

        # -----------------------------------------------------
        # Title & Subtitle
        # -----------------------------------------------------
        title = QLabel(
            "Administrator Login"
        )
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 22px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)

        subtitle = QLabel(
            "Online Examination & AI Proctoring System"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)

        # -----------------------------------------------------
        # Username
        # -----------------------------------------------------
        username_label = QLabel(
            "Username"
        )
        username_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        self.username = QLineEdit()
        self.username.setPlaceholderText(
            "Enter administrator username"
        )
        self.username.setMinimumHeight(42)
        self.username.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CANVAS};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_PRIMARY};
                background-color: #111C2E;
            }}
        """)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username)

        # -----------------------------------------------------
        # Password
        # -----------------------------------------------------
        password_label = QLabel(
            "Password"
        )
        password_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        self.password = QLineEdit()
        self.password.setPlaceholderText(
            "Enter administrator password"
        )
        self.password.setEchoMode(
            QLineEdit.Password
        )
        self.password.setMinimumHeight(42)
        self.password.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CANVAS};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_PRIMARY};
                background-color: #111C2E;
            }}
        """)

        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password)

        card_layout.addSpacing(10)

        # -----------------------------------------------------
        # Login Button
        # -----------------------------------------------------
        login_btn = QPushButton(
            "Authenticate & Open Dashboard →"
        )
        login_btn.setMinimumHeight(44)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #4338CA;
            }}
        """)

        login_btn.clicked.connect(
            self.login
        )

        # Allow pressing Enter to login
        self.password.returnPressed.connect(
            self.login
        )

        card_layout.addWidget(login_btn)

        # -----------------------------------------------------
        # Security Footer Note
        # -----------------------------------------------------
        footer_note = QLabel(
            "Authorized Personnel Only • Secure Proctoring Gateway"
        )
        footer_note.setAlignment(Qt.AlignCenter)
        footer_note.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                font-size: 11px;
                background: transparent;
                border: none;
            }}
        """)
        card_layout.addWidget(footer_note)

        card.setLayout(card_layout)
        root_layout.addWidget(card)

        self.setLayout(root_layout)

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
    app.setStyleSheet(get_main_stylesheet())

    window = LoginWindow()
    window.show()

    sys.exit(
        app.exec_()
    )