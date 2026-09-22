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
    QFileDialog,
    QFrame,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from database.database import get_connection
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
    BADGE_DANGER_BG,
    BADGE_DANGER_TEXT,
    BADGE_DANGER_BORDER,
    BADGE_SUCCESS_BG,
    BADGE_SUCCESS_TEXT,
    BADGE_SUCCESS_BORDER,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
    BADGE_INFO_BORDER,
    create_badge_widget
)


class ViolationDetailsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.load_violations()

    # =========================================================
    # SETUP UI
    # =========================================================

    def setup_ui(self):

        self.setStyleSheet(f"background-color: {BG_CANVAS};")

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        # =====================================================
        # HEADER
        # =====================================================

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
        headerLayout.setSpacing(14)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("⚠ Real-Time Proctoring Infraction Logs")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel(
            "Review automated AI detection flags, suspicious examinee behaviors, and screenshot evidence."
        )
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

        # Refresh button
        self.refreshBtn = QPushButton("🔄 Refresh Logs")
        self.refreshBtn.setMinimumHeight(38)
        self.refreshBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        self.refreshBtn.clicked.connect(self.load_violations)
        headerLayout.addWidget(self.refreshBtn)

        layout.addWidget(headerCard)

        # =====================================================
        # TABLE
        # =====================================================

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
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

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
                padding: 10px 14px;
                font-weight: 700;
                font-size: 11px;
                border: none;
                border-bottom: 1px solid {BORDER_SUBTLE};
                letter-spacing: 0.5px;
            }}

            QTableWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid #1E293B;
            }}

            QTableWidget::item:selected {{
                background-color: #312E81;
                color: #FFFFFF;
            }}
        """)

        tableLayout.addWidget(self.table)

        # =====================================================
        # FOOTER INFO BAR
        # =====================================================

        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(4, 0, 4, 0)

        self.countLabel = QLabel("Total Violations: 0")
        self.countLabel.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }}
        """)

        securityHint = QLabel("🛡️ Infractions are flagged automatically by OpenCV pose & device classifiers.")
        securityHint.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                font-size: 11px;
                background: transparent;
            }}
        """)

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
                nameItem.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.table.setItem(row, 0, nameItem)

                # -------------------------------------------------
                # Register Number
                # -------------------------------------------------
                register_no = violation["register_no"] if violation["register_no"] else "-"
                regItem = QTableWidgetItem(register_no)
                regItem.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, regItem)

                # -------------------------------------------------
                # Exam
                # -------------------------------------------------
                exam_name = violation["exam_name"] if violation["exam_name"] else "General Exam"
                examItem = QTableWidgetItem(exam_name)
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
                timeItem.setForeground(Qt.gray)
                self.table.setItem(row, 4, timeItem)

                # -------------------------------------------------
                # Evidence Button
                # -------------------------------------------------
                screenshot = violation["screenshot"]

                viewBtn = QPushButton("👁 View Snapshot")
                viewBtn.setMinimumWidth(110)
                viewBtn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BADGE_INFO_BG};
                        color: {BADGE_INFO_TEXT};
                        border: 1px solid {BADGE_INFO_BORDER};
                        border-radius: 6px;
                        padding: 6px 10px;
                        font-size: 11px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: #312E81;
                        color: #FFFFFF;
                    }}
                """)

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
