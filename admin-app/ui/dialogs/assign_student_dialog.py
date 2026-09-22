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
from ui.qss_theme import (
    BG_CANVAS,
    BG_CARD,
    BORDER_SUBTLE,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


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
        self.setFixedSize(480, 360)
        self.setStyleSheet(f"background-color: {BG_CANVAS}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
            }}
        """)
        cardLayout = QVBoxLayout(card)
        cardLayout.setContentsMargins(20, 20, 20, 20)
        cardLayout.setSpacing(12)

        title = QLabel("📋 Assign Examinee to Exam")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: 700; background: transparent; border: none;")
        cardLayout.addWidget(title)

        subtitle = QLabel("Select student candidate and scheduled examination session.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")
        cardLayout.addWidget(subtitle)

        student_label = QLabel("Candidate Student:")
        student_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 12px; background: transparent;")
        self.studentCombo = QComboBox()
        self.studentCombo.setMinimumHeight(38)

        exam_label = QLabel("Scheduled Examination:")
        exam_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 12px; background: transparent;")
        self.examCombo = QComboBox()
        self.examCombo.setMinimumHeight(38)

        cardLayout.addWidget(student_label)
        cardLayout.addWidget(self.studentCombo)
        cardLayout.addWidget(exam_label)
        cardLayout.addWidget(self.examCombo)

        layout.addWidget(card)

        self.assignBtn = QPushButton("Confirm & Assign Examinee")
        self.assignBtn.setMinimumHeight(42)
        self.assignBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
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