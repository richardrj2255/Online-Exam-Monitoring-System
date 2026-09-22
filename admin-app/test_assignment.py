import sys

from PyQt5.QtWidgets import QApplication
from ui.dialogs.assign_student_dialog import AssignStudentDialog

app = QApplication(sys.argv)

dialog = AssignStudentDialog()

dialog.exec_()