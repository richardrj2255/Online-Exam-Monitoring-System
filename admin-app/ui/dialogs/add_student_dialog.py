import os

from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from models.student_model import StudentModel
from ui.qss_theme import (
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
    BADGE_INFO_BORDER,
)


class AddStudentDialog(QDialog):

    def __init__(self, student=None):
        super().__init__()

        self.student = student
        self.photo_path = ""

        if self.student:
            self.setWindowTitle("Edit Examinee Record")
        else:
            self.setWindowTitle("Register New Examinee")

        self.setFixedSize(480, 620)

        self.setup_ui()

        if self.student:
            self.load_student()

    ##########################################################

    def setup_ui(self):

        self.setStyleSheet(f"background-color: {BG_CANVAS}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        # Card Container
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
        cardLayout.setSpacing(10)

        if self.student:
            title = QLabel("✏ Edit Examinee Profile")
        else:
            title = QLabel("👨‍🎓 Register New Examinee")

        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: 700; background: transparent; border: none;")
        cardLayout.addWidget(title)

        subtitle = QLabel("Examinee demographic information and photo biometric identification.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none; margin-bottom: 6px;")
        cardLayout.addWidget(subtitle)

        self.reg = QLineEdit()
        self.reg.setPlaceholderText("Register Number (e.g. REG2026001)")

        self.name = QLineEdit()
        self.name.setPlaceholderText("Student Full Name")

        self.dept = QLineEdit()
        self.dept.setPlaceholderText("Department (e.g. Computer Science)")

        self.sem = QLineEdit()
        self.sem.setPlaceholderText("Semester (e.g. 6)")

        self.hall = QLineEdit()
        self.hall.setPlaceholderText("Exam Hall / Laboratory")

        self.seat = QLineEdit()
        self.seat.setPlaceholderText("Seat Number")

        for field in [self.reg, self.name, self.dept, self.sem, self.hall, self.seat]:
            field.setMinimumHeight(36)
            cardLayout.addWidget(field)

        # Photo row
        photoFrame = QFrame()
        photoFrame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CANVAS};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
            }}
        """)
        photoLayout = QHBoxLayout(photoFrame)
        photoLayout.setContentsMargins(10, 8, 10, 8)
        photoLayout.setSpacing(10)

        self.photoLabel = QLabel("No Biometric Photo Enrolled")
        self.photoLabel.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")

        browse = QPushButton("📷 Choose Photo")
        browse.setMinimumHeight(30)
        browse.setStyleSheet(f"""
            QPushButton {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)
        browse.clicked.connect(self.choose_photo)

        photoLayout.addWidget(self.photoLabel, 1)
        photoLayout.addWidget(browse)
        cardLayout.addWidget(photoFrame)

        layout.addWidget(card)

        # Save Button
        if self.student:
            self.saveBtn = QPushButton("Update Examinee Profile")
        else:
            self.saveBtn = QPushButton("Save & Enroll Examinee")

        self.saveBtn.setMinimumHeight(42)
        self.saveBtn.setStyleSheet(f"""
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
        self.saveBtn.clicked.connect(self.save_student)

        layout.addWidget(self.saveBtn)
        self.setLayout(layout)

    ##########################################################

    def load_student(self):

        self.reg.setText(self.student["register_no"])
        self.reg.setEnabled(False)

        self.name.setText(self.student["name"])
        self.dept.setText(self.student["department"])
        self.sem.setText(self.student["semester"])
        self.hall.setText(self.student["hall"])
        self.seat.setText(self.student["seat"])

        self.photo_path = self.student["photo"] if self.student["photo"] else ""

        if self.photo_path:
            self.photoLabel.setText(os.path.basename(self.photo_path))

    ##########################################################

    def choose_photo(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Photo",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if filename:
            self.photo_path = filename
            self.photoLabel.setText(os.path.basename(filename))

    ##########################################################

    def save_student(self):

        if (
            self.reg.text().strip() == "" or
            self.name.text().strip() == "" or
            self.dept.text().strip() == "" or
            self.sem.text().strip() == "" or
            self.hall.text().strip() == "" or
            self.seat.text().strip() == ""
        ):

            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fill all examinee details."
            )
            return

        ##################################################
        # EDIT MODE
        ##################################################

        if self.student:

            success = StudentModel.update_student(
                self.reg.text().strip(),
                self.name.text().strip(),
                self.dept.text().strip(),
                self.sem.text().strip(),
                self.hall.text().strip(),
                self.seat.text().strip(),
                self.photo_path
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Student updated successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Unable to update student."
                )

            return

        ##################################################
        # ADD MODE
        ##################################################

        success = StudentModel.add_student(
            self.reg.text().strip(),
            self.name.text().strip(),
            self.dept.text().strip(),
            self.sem.text().strip(),
            self.hall.text().strip(),
            self.seat.text().strip(),
            self.photo_path
        )

        if success:
            QMessageBox.information(
                self,
                "Success",
                "Student added successfully."
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Registration Error",
                "Register Number already exists in database."
            )