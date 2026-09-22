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


class StudentAssignmentPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setupUI()
        self.load_assignments()

    ####################################################
    # UI
    ####################################################

    def setupUI(self):

        self.setStyleSheet(f"background-color: {BG_CANVAS};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # Header Card
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

        title = QLabel("📋 Student Examination Assignment")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Allocate examinees to scheduled examination sessions and verify seating allocations.")
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

        self.totalLabel = QLabel("Total Assignments: 0")
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
        self.search.setPlaceholderText("🔍 Search assignments by student name or register number...")
        self.search.setMinimumHeight(38)
        self.search.textChanged.connect(self.search_assignments)

        assignBtn = QPushButton("+ Assign Student to Exam")
        assignBtn.setMinimumHeight(38)
        assignBtn.setStyleSheet(f"""
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
        assignBtn.clicked.connect(self.open_assign_dialog)

        top_layout.addWidget(self.search)
        top_layout.addWidget(assignBtn)

        main_layout.addLayout(top_layout)

        # Table Card
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
    # Load Assignments
    ####################################################

    def load_assignments(self):

        assignments = AssignmentModel.get_all_assignments()

        self.table.setRowCount(len(assignments))
        self.totalLabel.setText(f"Total Assignments: {len(assignments)}")

        for row, assignment in enumerate(assignments):

            regItem = QTableWidgetItem(assignment["register_no"])
            regItem.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 0, regItem)

            self.table.setItem(row, 1, QTableWidgetItem(assignment["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(assignment["exam_name"]))

            codeItem = QTableWidgetItem(assignment["subject_code"])
            codeItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, codeItem)

            self.table.setItem(row, 4, QTableWidgetItem(assignment["subject_name"]))

            dateItem = QTableWidgetItem(assignment["exam_date"])
            dateItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, dateItem)

            startItem = QTableWidgetItem(assignment["start_time"])
            startItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, startItem)

            endItem = QTableWidgetItem(assignment["end_time"])
            endItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 7, endItem)

            # Delete Button
            deleteBtn = QPushButton("🗑 Remove")
            deleteBtn.setStyleSheet(f"""
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