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
from ui.qss_theme import (
    BG_CANVAS,
    BG_CARD,
    BG_CARD_ALT,
    BORDER_SUBTLE,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
    BADGE_INFO_BORDER,
    BADGE_DANGER_BG,
    BADGE_DANGER_TEXT,
    BADGE_DANGER_BORDER,
)


class StudentsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setupUI()
        self.load_students()

    ####################################################
    # UI
    # ##################################################

    def setupUI(self):

        self.setStyleSheet(f"background-color: {BG_CANVAS};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # Header card
        headerCard = QFrame()
        headerCard.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)
        headerLayout = QHBoxLayout(headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("👨‍🎓 Examinee Roster & Profile Management")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Register, modify, and audit student credentials for monitored exams.")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        self.totalLabel = QLabel("Total Students: 0")
        self.totalLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_INFO_BG};
                color: {BADGE_INFO_TEXT};
                border: 1px solid {BADGE_INFO_BORDER};
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }}
        """)
        headerLayout.addWidget(self.totalLabel)

        main_layout.addWidget(headerCard)

        # Action Bar
        topCard = QFrame()
        topCard.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        top_layout = QHBoxLayout(topCard)
        top_layout.setContentsMargins(14, 10, 14, 10)
        top_layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search examinees by Register Number or Name...")
        self.search.textChanged.connect(self.search_students)
        self.search.setMinimumHeight(38)

        add_btn = QPushButton("+ Register Student")
        add_btn.setMinimumHeight(38)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        add_btn.clicked.connect(self.open_add_student)

        top_layout.addWidget(self.search)
        top_layout.addWidget(add_btn)

        main_layout.addWidget(topCard)

        # Table
        tableCard = QFrame()
        tableCard.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)
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
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                alternate-background-color: {BG_CARD_ALT};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                gridline-color: #243248;
                font-size: 13px;
                outline: none;
            }}

            QHeaderView::section {{
                background-color: {BG_CANVAS};
                color: {TEXT_SECONDARY};
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {BORDER_SUBTLE};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}

            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid #1E293B;
            }}

            QTableWidget::item:selected {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)

        tableLayout.addWidget(self.table)
        main_layout.addWidget(tableCard)

        self.setLayout(main_layout)

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
            regItem.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 0, regItem)

            self.table.setItem(row, 1, QTableWidgetItem(student["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(student["department"]))

            semItem = QTableWidgetItem(student["semester"])
            semItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, semItem)

            hallItem = QTableWidgetItem(student["hall"])
            hallItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, hallItem)

            seatItem = QTableWidgetItem(student["seat"])
            seatItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, seatItem)

            photo = "📷 Enrolled" if student["photo"] else "-"
            photoItem = QTableWidgetItem(photo)
            photoItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, photoItem)

            # Edit Button
            edit_btn = QPushButton("✏ Edit")
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BADGE_INFO_BG};
                    color: {BADGE_INFO_TEXT};
                    border: 1px solid {BADGE_INFO_BORDER};
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #312E81;
                    color: #FFFFFF;
                }}
            """)
            edit_btn.clicked.connect(
                partial(self.edit_student, student["register_no"])
            )
            self.table.setCellWidget(row, 7, edit_btn)

            # Delete Button
            delete_btn = QPushButton("🗑 Delete")
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BADGE_DANGER_BG};
                    color: {BADGE_DANGER_TEXT};
                    border: 1px solid {BADGE_DANGER_BORDER};
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #9F1239;
                    color: #FFFFFF;
                }}
            """)
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