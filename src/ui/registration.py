from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QMessageBox
)
import sys


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Offline Examination Monitoring System")
        self.setGeometry(300, 150, 500, 350)

        layout = QGridLayout()

        self.name = QLineEdit()
        self.regno = QLineEdit()
        self.department = QLineEdit()
        self.course = QLineEdit()
        self.exam = QLineEdit()
        self.hall = QLineEdit()
        self.seat = QLineEdit()

        layout.addWidget(QLabel("Student Name"), 0, 0)
        layout.addWidget(self.name, 0, 1)

        layout.addWidget(QLabel("Register Number"), 1, 0)
        layout.addWidget(self.regno, 1, 1)

        layout.addWidget(QLabel("Department"), 2, 0)
        layout.addWidget(self.department, 2, 1)

        layout.addWidget(QLabel("Course"), 3, 0)
        layout.addWidget(self.course, 3, 1)

        layout.addWidget(QLabel("Exam"), 4, 0)
        layout.addWidget(self.exam, 4, 1)

        layout.addWidget(QLabel("Hall Number"), 5, 0)
        layout.addWidget(self.hall, 5, 1)

        layout.addWidget(QLabel("Seat Number"), 6, 0)
        layout.addWidget(self.seat, 6, 1)

        start_btn = QPushButton("Start Monitoring")
        start_btn.clicked.connect(self.start_exam)

        layout.addWidget(start_btn, 7, 0, 1, 2)

        self.setLayout(layout)

    def start_exam(self):
        QMessageBox.information(
            self,
            "Success",
            "Student Registered Successfully!"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RegistrationWindow()
    window.show()

    sys.exit(app.exec_())