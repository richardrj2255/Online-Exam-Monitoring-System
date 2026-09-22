from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QHeaderView,
    QAbstractItemView,
    QFrame,
    QMessageBox
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from functools import partial

from ui.dialogs.add_student_dialog import AddStudentDialog
from models.student_model import StudentModel
from ui.theme_manager import get_theme_palette, register_theme_listener


class StudentsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setupUI()
        self.load_students()
        register_theme_listener(self._on_theme_changed)

    ####################################################
    # UI
    # ##################################################

    def setupUI(self):

        self.setObjectName("pageWidget")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # Header card
        headerCard = QFrame()
        headerCard.setObjectName("headerCard")
        headerLayout = QHBoxLayout(headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("👨‍🎓 Examinee Roster & Profile Management")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Register, modify, and audit student credentials for monitored exams.")
        subtitle.setObjectName("pageSubtitle")

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        self.totalLabel = QLabel("Total Students: 0")
        self.totalLabel.setFont(QFont("Segoe UI", 11, QFont.Bold))
        headerLayout.addWidget(self.totalLabel)

        main_layout.addWidget(headerCard)

        # Action Bar
        topCard = QFrame()
        topCard.setObjectName("card")
        top_layout = QHBoxLayout(topCard)
        top_layout.setContentsMargins(14, 10, 14, 10)
        top_layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search examinees by Register Number or Name...")
        self.search.textChanged.connect(self.search_students)
        self.search.setMinimumHeight(40)

        add_btn = QPushButton("+ Register Student")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.open_add_student)

        top_layout.addWidget(self.search)
        top_layout.addWidget(add_btn)

        main_layout.addWidget(topCard)

        # Table
        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
        tableLayout = QVBoxLayout(tableCard)
        tableLayout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "REGISTER NO",
            "NAME",
            "DEPARTMENT",
            "SEMESTER",
            "HALL",
            "SEAT",
            "PHOTO",
            "EDIT",
            "DELETE"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 95)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 105)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setShowGrid(False)

        tableLayout.addWidget(self.table)
        main_layout.addWidget(tableCard)

        self.setLayout(main_layout)
        self._apply_badge_style()

    def _on_theme_changed(self, theme_name):
        self._apply_badge_style()

    def _apply_badge_style(self):
        p = get_theme_palette()
        self.totalLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {p['badge_info_bg']};
                color: {p['badge_info_text']};
                border: 1px solid {p['badge_info_border']};
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }}
        """)

    ####################################################
    # Add Student
    ####################################################

    def open_add_student(self):

        dialog = AddStudentDialog()

        if dialog.exec_():
            self.load_students()

    ####################################################
    # Load Students
    ####################################################

    def load_students(self):

        students = StudentModel.get_all_students()

        self.table.setRowCount(len(students))
        self.totalLabel.setText(f"Total Students: {len(students)}")

        for row, student in enumerate(students):

            regItem = QTableWidgetItem(student["register_no"])
            regItem.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.table.setItem(row, 0, regItem)

            nameItem = QTableWidgetItem(student["name"])
            nameItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 1, nameItem)

            deptItem = QTableWidgetItem(student["department"])
            deptItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 2, deptItem)

            semItem = QTableWidgetItem(str(student["semester"]))
            semItem.setTextAlignment(Qt.AlignCenter)
            semItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 3, semItem)

            hallItem = QTableWidgetItem(str(student["hall"]))
            hallItem.setTextAlignment(Qt.AlignCenter)
            hallItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 4, hallItem)

            seatItem = QTableWidgetItem(str(student["seat"]))
            seatItem.setTextAlignment(Qt.AlignCenter)
            seatItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 5, seatItem)

            photo = "📷 Enrolled" if student["photo"] else "-"
            photoItem = QTableWidgetItem(photo)
            photoItem.setTextAlignment(Qt.AlignCenter)
            photoItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 6, photoItem)

            # Edit Button
            edit_btn = QPushButton("✏ Edit")
            edit_btn.setObjectName("secondaryBtn")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setMinimumHeight(32)
            edit_btn.clicked.connect(
                partial(self.edit_student, student["register_no"])
            )
            self.table.setCellWidget(row, 7, edit_btn)

            # Delete Button
            delete_btn = QPushButton("🗑 Delete")
            delete_btn.setObjectName("dangerBtn")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setMinimumHeight(32)
            delete_btn.clicked.connect(
                partial(self.delete_student, student["register_no"])
            )
            self.table.setCellWidget(row, 8, delete_btn)

    ####################################################
    # Edit Student
    ####################################################

    def edit_student(self, register_no):

        student = StudentModel.get_student(register_no)

        if not student:
            QMessageBox.warning(self, "Error", "Student not found.")
            return

        dialog = AddStudentDialog(student)

        if dialog.exec_():
            self.load_students()

    ####################################################
    # Delete Student
    ####################################################

    def delete_student(self, register_no):

        reply = QMessageBox.question(
            self,
            "Delete Student",
            f"Are you sure you want to delete\n\n{register_no} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = StudentModel.delete_student(register_no)

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Student deleted successfully."
                )
                self.load_students()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Unable to delete student."
                )

    ####################################################
    # Search Student
    ####################################################

    def search_students(self):

        text = self.search.text().lower()

        for row in range(self.table.rowCount()):
            show = False
            for col in range(2):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    show = True
                    break

            self.table.setRowHidden(row, not show)