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

from ui.dialogs.assign_student_dialog import AssignStudentDialog
from models.assignment_model import AssignmentModel
from ui.theme_manager import get_theme_palette, register_theme_listener


class StudentAssignmentPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setupUI()
        self.load_assignments()
        register_theme_listener(self._on_theme_changed)

    ####################################################
    # UI
    ####################################################

    def setupUI(self):

        self.setObjectName("pageWidget")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # Header Card
        headerCard = QFrame()
        headerCard.setObjectName("headerCard")
        headerLayout = QHBoxLayout(headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("📋 Student Examination Assignment")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Allocate examinees to scheduled examination sessions and verify seating allocations.")
        subtitle.setObjectName("pageSubtitle")

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        self.totalLabel = QLabel("Total Assignments: 0")
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
        self.search.setPlaceholderText("🔍 Search assignments by student name or register number...")
        self.search.setMinimumHeight(40)
        self.search.textChanged.connect(self.search_assignments)

        assignBtn = QPushButton("+ Assign Student to Exam")
        assignBtn.setCursor(Qt.PointingHandCursor)
        assignBtn.setMinimumHeight(40)
        assignBtn.clicked.connect(self.open_assign_dialog)

        top_layout.addWidget(self.search)
        top_layout.addWidget(assignBtn)

        main_layout.addWidget(topCard)

        # Table Card
        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
        tableLayout = QVBoxLayout(tableCard)
        tableLayout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "REGISTER NO",
            "STUDENT NAME",
            "EXAM NAME",
            "SUBJECT CODE",
            "SUBJECT NAME",
            "EXAM DATE",
            "START TIME",
            "END TIME",
            "ACTION"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 120)

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
    # Load Assignments
    ####################################################

    def load_assignments(self):

        assignments = AssignmentModel.get_all_assignments()

        self.table.setRowCount(len(assignments))
        self.totalLabel.setText(f"Total Assignments: {len(assignments)}")

        for row, assignment in enumerate(assignments):

            regItem = QTableWidgetItem(assignment["register_no"])
            regItem.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.table.setItem(row, 0, regItem)

            nameItem = QTableWidgetItem(assignment["name"])
            nameItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 1, nameItem)

            examItem = QTableWidgetItem(assignment["exam_name"])
            examItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 2, examItem)

            codeItem = QTableWidgetItem(assignment["subject_code"])
            codeItem.setTextAlignment(Qt.AlignCenter)
            codeItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 3, codeItem)

            subItem = QTableWidgetItem(assignment["subject_name"])
            subItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 4, subItem)

            dateItem = QTableWidgetItem(assignment["exam_date"])
            dateItem.setTextAlignment(Qt.AlignCenter)
            dateItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 5, dateItem)

            startItem = QTableWidgetItem(assignment["start_time"])
            startItem.setTextAlignment(Qt.AlignCenter)
            startItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 6, startItem)

            endItem = QTableWidgetItem(assignment["end_time"])
            endItem.setTextAlignment(Qt.AlignCenter)
            endItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 7, endItem)

            # Delete Button
            deleteBtn = QPushButton("🗑 Remove")
            deleteBtn.setObjectName("dangerBtn")
            deleteBtn.setCursor(Qt.PointingHandCursor)
            deleteBtn.setMinimumHeight(32)
            deleteBtn.clicked.connect(
                partial(self.delete_assignment, assignment["assignment_id"])
            )

            btnContainer = QWidget()
            btnContainer.setStyleSheet("background: transparent;")
            btnLayout = QHBoxLayout(btnContainer)
            btnLayout.setContentsMargins(4, 2, 4, 2)
            btnLayout.setAlignment(Qt.AlignCenter)
            btnLayout.addWidget(deleteBtn)

            self.table.setCellWidget(row, 8, btnContainer)

    ####################################################
    # Open Assign Dialog
    ####################################################

    def open_assign_dialog(self):

        dialog = AssignStudentDialog()

        if dialog.exec_():
            self.load_assignments()

    ####################################################
    # Delete Assignment
    ####################################################

    def delete_assignment(self, assignment_id):

        reply = QMessageBox.question(
            self,
            "Delete Assignment",
            "Are you sure you want to remove this student exam assignment?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            AssignmentModel.delete_assignment(assignment_id)

            QMessageBox.information(
                self,
                "Success",
                "Assignment deleted successfully."
            )
            self.load_assignments()

    ####################################################
    # Search Assignments
    ####################################################

    def search_assignments(self):

        text = self.search.text().lower()

        for row in range(self.table.rowCount()):
            show = False
            for col in range(2):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    show = True
                    break

            self.table.setRowHidden(row, not show)