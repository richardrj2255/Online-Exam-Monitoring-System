from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QFrame,
    QMessageBox
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from models.assignment_model import AssignmentModel


class AssignStudentDialog(QDialog):

    def __init__(self):

        super().__init__()

        self.setupUI()
        self.load_students()
        self.load_exams()

    ####################################################
    # UI
    ####################################################

    def setupUI(self):

        self.setWindowTitle("Assign Examinee to Examination")
        self.setFixedSize(500, 380)
        self.setObjectName("pageWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        card = QFrame()
        card.setObjectName("card")
        cardLayout = QVBoxLayout(card)
        cardLayout.setContentsMargins(22, 22, 22, 22)
        cardLayout.setSpacing(12)

        title = QLabel("📋 Assign Examinee to Exam")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cardLayout.addWidget(title)

        subtitle = QLabel("Select student candidate and scheduled examination session.")
        subtitle.setObjectName("pageSubtitle")
        cardLayout.addWidget(subtitle)

        student_label = QLabel("Candidate Student:")
        student_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.studentCombo = QComboBox()
        self.studentCombo.setMinimumHeight(40)

        exam_label = QLabel("Scheduled Examination:")
        exam_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.examCombo = QComboBox()
        self.examCombo.setMinimumHeight(40)

        cardLayout.addWidget(student_label)
        cardLayout.addWidget(self.studentCombo)
        cardLayout.addWidget(exam_label)
        cardLayout.addWidget(self.examCombo)

        layout.addWidget(card)

        self.assignBtn = QPushButton("Confirm & Assign Examinee")
        self.assignBtn.setCursor(Qt.PointingHandCursor)
        self.assignBtn.setMinimumHeight(44)
        self.assignBtn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.assignBtn.clicked.connect(self.assign_student)

        layout.addWidget(self.assignBtn)
        self.setLayout(layout)

    ####################################################
    # Load Students
    ####################################################

    def load_students(self):

        self.studentCombo.clear()
        students = AssignmentModel.get_all_students()

        for student in students:
            self.studentCombo.addItem(
                f"{student['register_no']} - {student['name']}",
                student["id"]
            )

    ####################################################
    # Load Exams
    ####################################################

    def load_exams(self):

        self.examCombo.clear()
        exams = AssignmentModel.get_all_exams()

        for exam in exams:
            self.examCombo.addItem(
                f"{exam['exam_name']} ({exam['subject_code']})",
                exam["id"]
            )

    ####################################################
    # Assign Student
    ####################################################

    def assign_student(self):

        student_id = self.studentCombo.currentData()
        exam_id = self.examCombo.currentData()

        AssignmentModel.assign_student(
            student_id,
            exam_id
        )

        QMessageBox.information(
            self,
            "Assignment Confirmed",
            "Examinee assigned to examination successfully."
        )

        self.accept()