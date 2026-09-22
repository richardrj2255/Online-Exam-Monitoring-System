import sys

from PyQt5.QtWidgets import QApplication

from ui.login import LoginWindow
from ui.theme_manager import apply_theme

# =============================================================
# APPLICATION
# =============================================================

app = QApplication(
    sys.argv
)
apply_theme(app, "light")


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