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

from ui.dialogs.add_exam_dialog import AddExamDialog
from models.exam_model import ExamModel
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
    BADGE_SUCCESS_BG,
    BADGE_SUCCESS_TEXT,
    BADGE_SUCCESS_BORDER,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
    BADGE_INFO_BORDER,
    BADGE_DANGER_BG,
    BADGE_DANGER_TEXT,
    BADGE_DANGER_BORDER,
    create_badge_widget,
)


class ExamsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setupUI()
        self.load_exams()

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

        title = QLabel("📝 Examination Sessions & Scheduling")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Create exam schedules, configure timing, and trigger live monitoring proctoring.")
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

        self.totalLabel = QLabel("Total Exams: 0")
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
        self.search.setPlaceholderText("🔍 Search by Exam Name, Subject Code, or Department...")
        self.search.setMinimumHeight(38)
        self.search.textChanged.connect(self.search_exam)

        add_btn = QPushButton("+ Create Examination")
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
        add_btn.clicked.connect(self.open_add_exam)

        top_layout.addWidget(self.search)
        top_layout.addWidget(add_btn)

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
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "EXAM",
            "SUBJECT CODE",
            "SUBJECT",
            "DEPARTMENT",
            "SEM",
            "HALL",
            "DATE",
            "TIME",
            "STATUS",
            "START",
            "EDIT",
            "DELETE"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(10, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(11, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(12, QHeaderView.ResizeToContents)

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
    # Open Add Dialog
    ####################################################

    def open_add_exam(self):

        dialog = AddExamDialog()

        if dialog.exec_():
            self.load_exams()

    ####################################################
    # Load Exams
    ####################################################

    def load_exams(self):

        exams = ExamModel.get_all_exams()

        self.table.setRowCount(len(exams))
        self.totalLabel.setText(f"Total Exams: {len(exams)}")

        for row, exam in enumerate(exams):

            idItem = QTableWidgetItem(str(exam["id"]))
            idItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, idItem)

            examItem = QTableWidgetItem(exam["exam_name"])
            examItem.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 1, examItem)

            codeItem = QTableWidgetItem(exam["subject_code"])
            codeItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, codeItem)

            self.table.setItem(row, 3, QTableWidgetItem(exam["subject_name"]))
            self.table.setItem(row, 4, QTableWidgetItem(exam["department"]))

            semItem = QTableWidgetItem(str(exam["semester"]))
            semItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, semItem)

            hallItem = QTableWidgetItem(exam["hall"])
            hallItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, hallItem)

            dateItem = QTableWidgetItem(exam["exam_date"])
            dateItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 7, dateItem)

            time = exam["start_time"] + " - " + exam["end_time"]
            timeItem = QTableWidgetItem(time)
            timeItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 8, timeItem)

            # Status Badge Pill (Column 9)
            status = str(exam["exam_status"] or "Scheduled")
            if status == "Started":
                status_widget = create_badge_widget("STARTED", "success")
            elif status == "Completed":
                status_widget = create_badge_widget("COMPLETED", "neutral")
            else:
                status_widget = create_badge_widget("SCHEDULED", "info")

            self.table.setCellWidget(row, 9, status_widget)

            # Start Button (Column 10)
            start_btn = QPushButton("▶ Start Exam")
            start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BADGE_SUCCESS_BG};
                    color: {BADGE_SUCCESS_TEXT};
                    border: 1px solid {BADGE_SUCCESS_BORDER};
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #065F46;
                    color: #FFFFFF;
                }}
            """)

            start_btn.clicked.connect(
                lambda checked, eid=exam["id"]: self.start_exam(eid)
            )

            if status == "Started":
                start_btn.setText("🟢 Started")
                start_btn.setEnabled(False)
            elif status == "Completed":
                start_btn.setText("✓ Completed")
                start_btn.setEnabled(False)

            self.table.setCellWidget(row, 10, start_btn)

            # Edit Button (Column 11)
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
                lambda checked, eid=exam["id"]: self.edit_exam(eid)
            )
            self.table.setCellWidget(row, 11, edit_btn)

            # Delete Button (Column 12)
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
                lambda checked, eid=exam["id"]: self.delete_exam(eid)
            )
            self.table.setCellWidget(row, 12, delete_btn)

    ####################################################
    # Start Exam
    ####################################################

    def start_exam(self, exam_id):

        exam = ExamModel.get_exam(exam_id)

        if not exam:
            QMessageBox.warning(self, "Error", "Exam not found.")
            return

        if exam["exam_status"] == "Started":
            QMessageBox.information(
                self,
                "Exam Already Started",
                "This examination has already started."
            )
            return

        if exam["exam_status"] == "Completed":
            QMessageBox.warning(
                self,
                "Exam Completed",
                "This examination has already been completed."
            )
            return

        reply = QMessageBox.question(
            self,
            "Start Examination",
            f"Are you sure you want to start\n\n"
            f"{exam['exam_name']}?\n\n"
            f"All assigned students will be allowed to start the examination.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = ExamModel.start_exam(exam_id)

            if success:
                QMessageBox.information(
                    self,
                    "Exam Started",
                    "The examination has started successfully.\n\n"
                    "All assigned students can now enter the exam."
                )
                self.load_exams()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Unable to start the examination."
                )

    ####################################################
    # Edit Exam
    ####################################################

    def edit_exam(self, exam_id):

        exam = ExamModel.get_exam(exam_id)

        if not exam:
            QMessageBox.warning(self, "Error", "Exam not found.")
            return

        dialog = AddExamDialog(exam)

        if dialog.exec_():
            self.load_exams()

    ####################################################
    # Delete Exam
    ####################################################

    def delete_exam(self, exam_id):

        reply = QMessageBox.question(
            self,
            "Delete Exam",
            "Are you sure you want to delete this examination?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = ExamModel.delete_exam(exam_id)

            if success:
                QMessageBox.information(
                    self,
                    "Deleted",
                    "Examination deleted successfully."
                )
                self.load_exams()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Unable to delete examination."
                )

    ####################################################
    # Search Exam
    ####################################################

    def search_exam(self):

        text = self.search.text().lower()

        for row in range(self.table.rowCount()):
            visible = False
            for col in [1, 2, 3]:
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(row, not visible)