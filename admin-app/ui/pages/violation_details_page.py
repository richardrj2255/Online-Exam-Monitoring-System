import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QFrame,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from database.database import get_connection
from ui.theme_manager import get_theme_palette
from ui.qss_theme import create_badge_widget


class ViolationDetailsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.load_violations()

    # =========================================================
    # SETUP UI
    # =========================================================

    def setup_ui(self):

        self.setObjectName("pageWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        # =====================================================
        # HEADER
        # =====================================================

        headerCard = QFrame()
        headerCard.setObjectName("headerCard")
        headerLayout = QHBoxLayout(headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)
        headerLayout.setSpacing(14)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("⚠ Real-Time Proctoring Infraction Logs")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel(
            "Review automated AI detection flags, suspicious examinee behaviors, and screenshot evidence."
        )
        subtitle.setObjectName("pageSubtitle")

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        # Refresh button
        self.refreshBtn = QPushButton("🔄 Refresh Logs")
        self.refreshBtn.setObjectName("secondaryBtn")
        self.refreshBtn.setCursor(Qt.PointingHandCursor)
        self.refreshBtn.setMinimumHeight(38)
        self.refreshBtn.clicked.connect(self.load_violations)
        headerLayout.addWidget(self.refreshBtn)

        layout.addWidget(headerCard)

        # =====================================================
        # TABLE
        # =====================================================

        tableCard = QFrame()
        tableCard.setObjectName("tableCard")
        tableLayout = QVBoxLayout(tableCard)
        tableLayout.setContentsMargins(16, 16, 16, 16)
        tableLayout.setSpacing(12)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "STUDENT NAME",
            "REGISTER NO",
            "EXAMINATION",
            "VIOLATION TYPE",
            "TIMESTAMP",
            "EVIDENCE SNAPSHOT",
            "PROCTOR STATUS",
        ])

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 185)
        self.table.setColumnWidth(5, 140)
        self.table.setColumnWidth(6, 140)

        tableLayout.addWidget(self.table)

        # =====================================================
        # FOOTER INFO BAR
        # =====================================================

        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(4, 0, 4, 0)

        self.countLabel = QLabel("Total Violations: 0")
        self.countLabel.setObjectName("pageSubtitle")
        self.countLabel.setFont(QFont("Segoe UI", 12, QFont.Bold))

        securityHint = QLabel("🛡️ Infractions are flagged automatically by OpenCV pose & device classifiers.")
        securityHint.setObjectName("pageSubtitle")

        footerLayout.addWidget(self.countLabel)
        footerLayout.addStretch()
        footerLayout.addWidget(securityHint)

        tableLayout.addLayout(footerLayout)
        layout.addWidget(tableCard)

        self.setLayout(layout)

    # =========================================================
    # LOAD VIOLATIONS
    # =========================================================

    def load_violations(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    v.id,
                    s.name AS student_name,
                    v.register_no,
                    e.exam_name,
                    v.violation_type,
                    v.date_time,
                    v.screenshot

                FROM violations v

                LEFT JOIN students s
                    ON v.register_no = s.register_no

                LEFT JOIN student_assignment sa
                    ON s.id = sa.student_id

                LEFT JOIN exams e
                    ON sa.exam_id = e.id

                ORDER BY
                    v.date_time DESC
            """)

            violations = cursor.fetchall()
            conn.close()

            self.table.setRowCount(0)

            for violation in violations:

                row = self.table.rowCount()
                self.table.insertRow(row)

                # -------------------------------------------------
                # Student Name
                # -------------------------------------------------
                student_name = violation["student_name"] if violation["student_name"] else "Unknown Examinee"
                nameItem = QTableWidgetItem(f"👨‍🎓 {student_name}")
                nameItem.setFont(QFont("Segoe UI", 11, QFont.Bold))
                self.table.setItem(row, 0, nameItem)

                # -------------------------------------------------
                # Register Number
                # -------------------------------------------------
                register_no = violation["register_no"] if violation["register_no"] else "-"
                regItem = QTableWidgetItem(register_no)
                regItem.setTextAlignment(Qt.AlignCenter)
                regItem.setFont(QFont("Segoe UI", 11))
                self.table.setItem(row, 1, regItem)

                # -------------------------------------------------
                # Exam
                # -------------------------------------------------
                exam_name = violation["exam_name"] if violation["exam_name"] else "General Exam"
                examItem = QTableWidgetItem(exam_name)
                examItem.setFont(QFont("Segoe UI", 11))
                self.table.setItem(row, 2, examItem)

                # -------------------------------------------------
                # Violation Type (Status Tag Badge)
                # -------------------------------------------------
                violation_type = violation["violation_type"] if violation["violation_type"] else "Suspicious Motion"
                badgeWidget = create_badge_widget(violation_type, "danger")
                self.table.setCellWidget(row, 3, badgeWidget)

                # -------------------------------------------------
                # Date / Time
                # -------------------------------------------------
                date_time = violation["date_time"] if violation["date_time"] else "-"
                timeItem = QTableWidgetItem(date_time)
                timeItem.setTextAlignment(Qt.AlignCenter)
                timeItem.setFont(QFont("Segoe UI", 11))
                self.table.setItem(row, 4, timeItem)

                # -------------------------------------------------
                # Evidence Button
                # -------------------------------------------------
                screenshot = violation["screenshot"]

                viewBtn = QPushButton("👁 View Snapshot")
                viewBtn.setCursor(Qt.PointingHandCursor)
                viewBtn.setObjectName("secondaryBtn")
                viewBtn.setMinimumWidth(120)
                viewBtn.setMinimumHeight(32)

                viewBtn.clicked.connect(
                    lambda checked=False, path=screenshot: self.view_evidence(path)
                )

                btnContainer = QWidget()
                btnContainer.setStyleSheet("background: transparent;")
                btnLayout = QHBoxLayout(btnContainer)
                btnLayout.setContentsMargins(4, 2, 4, 2)
                btnLayout.setAlignment(Qt.AlignCenter)
                btnLayout.addWidget(viewBtn)

                self.table.setCellWidget(row, 5, btnContainer)

                # -------------------------------------------------
                # Status Tag Badge
                # -------------------------------------------------
                statusBadge = create_badge_widget("Recorded Flag", "rose")
                self.table.setCellWidget(row, 6, statusBadge)

            self.countLabel.setText(
                f"Total Infraction Logs: {len(violations)}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load violations.\n\n{str(e)}"
            )

    # =========================================================
    # VIEW EVIDENCE
    # =========================================================

    def view_evidence(self, screenshot_path):

        if not screenshot_path:

            QMessageBox.information(
                self,
                "Evidence",
                "No screenshot was saved for this violation."
            )
            return

        if not os.path.isabs(screenshot_path):
            screenshot_path = os.path.abspath(screenshot_path)

        if not os.path.exists(screenshot_path):

            QMessageBox.warning(
                self,
                "Evidence Not Found",
                "The screenshot file could not be found.\n\n" + screenshot_path
            )
            return

        try:
            os.startfile(screenshot_path)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Unable to Open Evidence",
                str(e)
            )
