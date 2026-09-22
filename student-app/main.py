import torch
import sys

from PyQt5.QtWidgets import QApplication

from ui.login import StudentLogin


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = StudentLogin()

    window.show()

    sys.exit(app.exec_())