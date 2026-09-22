from PyQt5.QtWidgets import (
    QDialog,
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

from models.exam_model import ExamModel


class AddExamDialog(QDialog):

    def __init__(self, exam=None):
        super().__init__()

        self.exam = exam

        if self.exam:
            self.setWindowTitle("Edit Examination Session")
        else:
            self.setWindowTitle("Schedule New Examination")

        self.setFixedSize(500, 700)

        self.setup_ui()

        if self.exam:
            self.load_exam()

    ######################################################

    def setup_ui(self):

        self.setObjectName("pageWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        # Card Container
        card = QFrame()
        card.setObjectName("card")
        cardLayout = QVBoxLayout(card)
        cardLayout.setContentsMargins(22, 22, 22, 22)
        cardLayout.setSpacing(10)

        if self.exam:
            title = QLabel("✏ Edit Examination Session")
        else:
            title = QLabel("➕ Schedule New Examination")

        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cardLayout.addWidget(title)

        subtitle = QLabel("Configure academic session attributes and scheduling timetable.")
        subtitle.setObjectName("pageSubtitle")
        cardLayout.addWidget(subtitle)

        self.exam_name = QLineEdit()
        self.exam_name.setPlaceholderText("Exam Name (e.g. Midterm Assessment)")

        self.subject_code = QLineEdit()
        self.subject_code.setPlaceholderText("Subject Code (e.g. CS601)")

        self.subject_name = QLineEdit()
        self.subject_name.setPlaceholderText("Subject Name (e.g. Computer Networks)")

        self.department = QLineEdit()
        self.department.setPlaceholderText("Department (e.g. Computer Science)")

        self.semester = QLineEdit()
        self.semester.setPlaceholderText("Semester (e.g. 6)")

        self.hall = QLineEdit()
        self.hall.setPlaceholderText("Exam Hall / Laboratory (e.g. Lab 3)")

        self.exam_date = QLineEdit()
        self.exam_date.setPlaceholderText("Exam Date (YYYY-MM-DD)")

        self.start_time = QLineEdit()
        self.start_time.setPlaceholderText("Start Time (HH:MM e.g. 10:00)")

        self.end_time = QLineEdit()
        self.end_time.setPlaceholderText("End Time (HH:MM e.g. 12:00)")

        self.duration = QLineEdit()
        self.duration.setPlaceholderText("Duration in Minutes (e.g. 120)")

        for field in [
            self.exam_name,
            self.subject_code,
            self.subject_name,
            self.department,
            self.semester,
            self.hall,
            self.exam_date,
            self.start_time,
            self.end_time,
            self.duration,
        ]:
            field.setMinimumHeight(38)
            cardLayout.addWidget(field)

        layout.addWidget(card)

        # Save Button
        if self.exam:
            self.saveBtn = QPushButton("Update Examination Session")
        else:
            self.saveBtn = QPushButton("Save & Publish Examination")

        self.saveBtn.setCursor(Qt.PointingHandCursor)
        self.saveBtn.setMinimumHeight(44)
        self.saveBtn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.saveBtn.clicked.connect(self.save_exam)

        layout.addWidget(self.saveBtn)
        self.setLayout(layout)

    ######################################################

    def load_exam(self):

        self.exam_name.setText(self.exam["exam_name"])
        self.subject_code.setText(self.exam["subject_code"])
        self.subject_name.setText(self.exam["subject_name"])
        self.department.setText(self.exam["department"])
        self.semester.setText(self.exam["semester"])
        self.hall.setText(self.exam["hall"])
        self.exam_date.setText(self.exam["exam_date"])
        self.start_time.setText(self.exam["start_time"])
        self.end_time.setText(self.exam["end_time"])
        self.duration.setText(self.exam["duration"])

    ######################################################

    def save_exam(self):

        if (
            self.exam_name.text().strip() == "" or
            self.subject_code.text().strip() == "" or
            self.subject_name.text().strip() == "" or
            self.department.text().strip() == "" or
            self.semester.text().strip() == "" or
            self.hall.text().strip() == "" or
            self.exam_date.text().strip() == "" or
            self.start_time.text().strip() == "" or
            self.end_time.text().strip() == "" or
            self.duration.text().strip() == ""
        ):
            QMessageBox.warning(
                self,
                "Validation Error",
                "All examination attributes are mandatory."
            )
            return

        data = {
            "exam_name": self.exam_name.text().strip(),
            "subject_code": self.subject_code.text().strip(),
            "subject_name": self.subject_name.text().strip(),
            "department": self.department.text().strip(),
            "semester": self.semester.text().strip(),
            "hall": self.hall.text().strip(),
            "exam_date": self.exam_date.text().strip(),
            "start_time": self.start_time.text().strip(),
            "end_time": self.end_time.text().strip(),
            "duration": self.duration.text().strip(),
        }

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        if self.exam:

            success = ExamModel.update_exam(
                self.exam["id"],
                data["exam_name"],
                data["subject_code"],
                data["subject_name"],
                data["department"],
                data["semester"],
                data["hall"],
                data["exam_date"],
                data["start_time"],
                data["end_time"],
                data["duration"]
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Examination session updated successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to update examination record."
                )

        # ----------------------------------------------------
        # ADD
        # ----------------------------------------------------

        else:

            success = ExamModel.add_exam(
                data["exam_name"],
                data["subject_code"],
                data["subject_name"],
                data["department"],
                data["semester"],
                data["hall"],
                data["exam_date"],
                data["start_time"],
                data["end_time"],
                data["duration"]
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Examination session scheduled successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to schedule examination."
                )