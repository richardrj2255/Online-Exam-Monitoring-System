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
from ui.theme_manager import get_theme_palette, register_theme_listener
from ui.qss_theme import create_badge_widget


class ExamsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setupUI()
        self.load_exams()
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

        title = QLabel("📝 Examination Sessions & Scheduling")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Create exam schedules, configure timing, and trigger live monitoring proctoring.")
        subtitle.setObjectName("pageSubtitle")

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        self.totalLabel = QLabel("Total Exams: 0")
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
        self.search.setPlaceholderText("🔍 Search by Exam Name, Subject Code, or Department...")
        self.search.setMinimumHeight(40)
        self.search.textChanged.connect(self.search_exam)

        add_btn = QPushButton("+ Create Examination")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.open_add_exam)

        top_layout.addWidget(self.search)
        top_layout.addWidget(add_btn)

        main_layout.addWidget(topCard)

        # Table Card
        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
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
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(9, 115)
        self.table.horizontalHeader().setSectionResizeMode(10, QHeaderView.Fixed)
        self.table.setColumnWidth(10, 130)
        self.table.horizontalHeader().setSectionResizeMode(11, QHeaderView.Fixed)
        self.table.setColumnWidth(11, 95)
        self.table.horizontalHeader().setSectionResizeMode(12, QHeaderView.Fixed)
        self.table.setColumnWidth(12, 105)

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
            idItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 0, idItem)

            examItem = QTableWidgetItem(exam["exam_name"])
            examItem.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.table.setItem(row, 1, examItem)

            codeItem = QTableWidgetItem(exam["subject_code"])
            codeItem.setTextAlignment(Qt.AlignCenter)
            codeItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 2, codeItem)

            subItem = QTableWidgetItem(exam["subject_name"])
            subItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 3, subItem)

            deptItem = QTableWidgetItem(exam["department"])
            deptItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 4, deptItem)

            semItem = QTableWidgetItem(str(exam["semester"]))
            semItem.setTextAlignment(Qt.AlignCenter)
            semItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 5, semItem)

            hallItem = QTableWidgetItem(exam["hall"])
            hallItem.setTextAlignment(Qt.AlignCenter)
            hallItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 6, hallItem)

            dateItem = QTableWidgetItem(exam["exam_date"])
            dateItem.setTextAlignment(Qt.AlignCenter)
            dateItem.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 7, dateItem)

            time = exam["start_time"] + " - " + exam["end_time"]
            timeItem = QTableWidgetItem(time)
            timeItem.setTextAlignment(Qt.AlignCenter)
            timeItem.setFont(QFont("Segoe UI", 11))
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
            start_btn.setObjectName("successBtn")
            start_btn.setCursor(Qt.PointingHandCursor)
            start_btn.setMinimumHeight(32)

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
            edit_btn.setObjectName("secondaryBtn")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setMinimumHeight(32)
            edit_btn.clicked.connect(
                lambda checked, eid=exam["id"]: self.edit_exam(eid)
            )
            self.table.setCellWidget(row, 11, edit_btn)

            # Delete Button (Column 12)
            delete_btn = QPushButton("🗑 Delete")
            delete_btn.setObjectName("dangerBtn")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setMinimumHeight(32)
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