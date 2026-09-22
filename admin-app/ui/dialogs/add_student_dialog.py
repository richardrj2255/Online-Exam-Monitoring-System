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


class AddStudentDialog(QDialog):

    def __init__(self, student=None):
        super().__init__()

        self.student = student
        self.photo_path = ""

        if self.student:
            self.setWindowTitle("Edit Examinee Record")
        else:
            self.setWindowTitle("Register New Examinee")

        self.setFixedSize(500, 640)

        self.setup_ui()

        if self.student:
            self.load_student()

    ##########################################################

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
        cardLayout.setSpacing(12)

        if self.student:
            title = QLabel("✏ Edit Examinee Profile")
        else:
            title = QLabel("👨‍🎓 Register New Examinee")

        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cardLayout.addWidget(title)

        subtitle = QLabel("Examinee demographic information and photo biometric identification.")
        subtitle.setObjectName("pageSubtitle")
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
            field.setMinimumHeight(40)
            cardLayout.addWidget(field)

        # Photo row
        photoFrame = QFrame()
        photoFrame.setObjectName("card")
        photoLayout = QHBoxLayout(photoFrame)
        photoLayout.setContentsMargins(12, 10, 12, 10)
        photoLayout.setSpacing(10)

        self.photoLabel = QLabel("No Biometric Photo Enrolled")
        self.photoLabel.setObjectName("pageSubtitle")

        browse = QPushButton("📷 Choose Photo")
        browse.setObjectName("secondaryBtn")
        browse.setCursor(Qt.PointingHandCursor)
        browse.setMinimumHeight(34)
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

        self.saveBtn.setCursor(Qt.PointingHandCursor)
        self.saveBtn.setMinimumHeight(44)
        self.saveBtn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.saveBtn.clicked.connect(self.save_student)

        layout.addWidget(self.saveBtn)
        self.setLayout(layout)

    ##########################################################

    def load_student(self):

        self.reg.setText(self.student["register_no"])
        self.reg.setReadOnly(True)

        self.name.setText(self.student["name"])
        self.dept.setText(self.student["department"])
        self.sem.setText(str(self.student["semester"]))
        self.hall.setText(str(self.student["hall"]))
        self.seat.setText(str(self.student["seat"]))

        self.photo_path = self.student["photo"]

        if self.photo_path:
            self.photoLabel.setText(os.path.basename(self.photo_path))

    ##########################################################

    def choose_photo(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Student Photo",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file_name:
            self.photo_path = file_name
            self.photoLabel.setText(os.path.basename(file_name))

    ##########################################################

    def save_student(self):

        register_no = self.reg.text().strip()
        name = self.name.text().strip()
        department = self.dept.text().strip()
        semester = self.sem.text().strip()
        hall = self.hall.text().strip()
        seat = self.seat.text().strip()

        if not register_no or not name:

            QMessageBox.warning(
                self,
                "Validation Error",
                "Register Number and Student Name are mandatory fields."
            )
            return

        # -----------------------------------------------------
        # EDIT MODE
        # -----------------------------------------------------

        if self.student:

            success = StudentModel.update_student(
                register_no,
                name,
                department,
                semester,
                hall,
                seat,
                self.photo_path
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Examinee profile updated successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to update examinee profile."
                )

        # -----------------------------------------------------
        # INSERT MODE
        # -----------------------------------------------------

        else:

            success = StudentModel.add_student(
                register_no,
                name,
                department,
                semester,
                hall,
                seat,
                self.photo_path
            )

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "New examinee registered successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Examinee with this Register Number already exists."
                )