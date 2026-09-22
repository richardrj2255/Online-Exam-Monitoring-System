import sys

from PyQt5.QtWidgets import QApplication

from ui.login import LoginWindow
from ui.qss_theme import get_main_stylesheet


# =============================================================
# APPLICATION
# =============================================================

app = QApplication(
    sys.argv
)
app.setStyleSheet(
    get_main_stylesheet()
)


# =============================================================
# LOGIN WINDOW
# =============================================================

window = LoginWindow()

window.show()


# =============================================================
# START APPLICATION
# =============================================================

sys.exit(
    app.exec_()
)