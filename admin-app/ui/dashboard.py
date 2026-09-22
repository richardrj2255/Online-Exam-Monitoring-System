import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
    QSizePolicy,
    QGridLayout,
    QMessageBox,
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ui.pages.students_page import StudentsPage
from ui.pages.exams_page import ExamsPage
from ui.pages.student_assignment_page import StudentAssignmentPage
from ui.pages.exam_questions_page import ExamQuestionsPage
from ui.pages.questions_page import QuestionsPage
from ui.admin.admin_results_page import AdminResultsPage
from ui.pages.violation_details_page import ViolationDetailsPage
from ui.pages.live_monitor_page import LiveMonitorPage

from models.student_model import StudentModel
from models.exam_model import ExamModel

from ui.qss_theme import (
    get_main_stylesheet,
    BG_CANVAS,
    BG_CARD,
    BG_SIDEBAR,
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
)


class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Online Examination & AI Proctoring System - Admin Dashboard"
        )

        self.resize(1480, 880)

        self.navButtons = []

        self.setupUI()

    # =========================================================
    # SETUP UI
    # =========================================================

    def setupUI(self):

        central = QWidget()
        central.setStyleSheet(f"background-color: {BG_CANVAS};")
        self.setCentralWidget(central)

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # =====================================================
        # SIDEBAR (180px - 220px -> 220px width)
        # =====================================================

        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border-right: 1px solid {BORDER_SUBTLE};
            }}

            QPushButton {{
                color: {TEXT_SECONDARY};
                background-color: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 11px 16px;
                font-size: 13px;
                font-weight: 500;
            }}

            QPushButton:hover {{
                color: {TEXT_PRIMARY};
                background-color: #1E293B;
            }}

            QPushButton[active="true"] {{
                color: #FFFFFF;
                background-color: #312E81;
                border-left: 3px solid {COLOR_PRIMARY};
                font-weight: 700;
            }}
        """)

        sideLayout = QVBoxLayout()
        sideLayout.setContentsMargins(14, 20, 14, 20)
        sideLayout.setSpacing(6)

        # -----------------------------------------------------
        # Brand Logo Header
        # -----------------------------------------------------
        brandContainer = QFrame()
        brandContainer.setStyleSheet("background: transparent; border: none;")
        brandLayout = QVBoxLayout()
        brandLayout.setContentsMargins(4, 4, 4, 16)
        brandLayout.setSpacing(4)

        logoBadge = QLabel("🛡️")
        logoBadge.setAlignment(Qt.AlignCenter)
        logoBadge.setFont(QFont("Segoe UI Emoji", 26))
        logoBadge.setStyleSheet("background: transparent; border: none;")

        title = QLabel("PROCTOR AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Online Exam Monitor")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {COLOR_PRIMARY};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: transparent;
            border: none;
        """)

        brandLayout.addWidget(logoBadge)
        brandLayout.addWidget(title)
        brandLayout.addWidget(subtitle)
        brandContainer.setLayout(brandLayout)

        sideLayout.addWidget(brandContainer)

        # Subtle separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {BORDER_SUBTLE}; background-color: {BORDER_SUBTLE}; max-height: 1px; margin-bottom: 8px;")
        sideLayout.addWidget(sep)

        # Section Label
        sectionLbl = QLabel("NAVIGATION")
        sectionLbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 700; padding: 4px 10px; letter-spacing: 1px;")
        sideLayout.addWidget(sectionLbl)

        # =====================================================
        # NAVIGATION BUTTONS
        # =====================================================

        self.dashboardBtn = QPushButton("🏠  Dashboard")
        self.studentsBtn = QPushButton("👨‍🎓  Students")
        self.examsBtn = QPushButton("📝  Exams")
        self.questionsBtn = QPushButton("❓  Questions")
        self.examQuestionsBtn = QPushButton("🎯  Exam Questions")
        self.assignmentBtn = QPushButton("📋  Student Assignment")
        self.liveBtn = QPushButton("📹  Live Monitoring")
        self.resultsBtn = QPushButton("📊  Results")
        self.violationBtn = QPushButton("⚠  Violation Details")
        self.reportsBtn = QPushButton("📄  Reports")
        self.settingsBtn = QPushButton("⚙  Settings")

        self.navButtons = [
            self.dashboardBtn,
            self.studentsBtn,
            self.examsBtn,
            self.questionsBtn,
            self.examQuestionsBtn,
            self.assignmentBtn,
            self.liveBtn,
            self.resultsBtn,
            self.violationBtn,
            self.reportsBtn,
            self.settingsBtn
        ]

        for btn in self.navButtons:
            sideLayout.addWidget(btn)

        sideLayout.addStretch()

        # -----------------------------------------------------
        # Logout
        # -----------------------------------------------------
        self.logoutBtn = QPushButton("🚪  Logout")
        self.logoutBtn.setStyleSheet(f"""
            QPushButton {{
                color: {BADGE_DANGER_TEXT};
                background-color: transparent;
                border: 1px solid {BADGE_DANGER_BORDER};
                border-radius: 8px;
                padding: 10px;
                text-align: center;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {BADGE_DANGER_BG};
                color: #FFFFFF;
            }}
        """)
        sideLayout.addWidget(self.logoutBtn)

        sidebar.setLayout(sideLayout)

        # =====================================================
        # WORKSPACE AREA (Header + Stacked Pages)
        # =====================================================

        workspace = QWidget()
        workspaceLayout = QVBoxLayout()
        workspaceLayout.setContentsMargins(0, 0, 0, 0)
        workspaceLayout.setSpacing(0)

        # -----------------------------------------------------
        # Top Header Bar
        # -----------------------------------------------------
        topHeader = QFrame()
        topHeader.setFixedHeight(64)
        topHeader.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-bottom: 1px solid {BORDER_SUBTLE};
            }}
        """)

        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(24, 0, 24, 0)
        headerLayout.setSpacing(16)

        # Left status badge
        statusPill = QFrame()
        statusPill.setStyleSheet(f"""
            QFrame {{
                background-color: {BADGE_SUCCESS_BG};
                border: 1px solid {BADGE_SUCCESS_BORDER};
                border-radius: 14px;
                padding: 4px 12px;
            }}
        """)
        pillLayout = QHBoxLayout(statusPill)
        pillLayout.setContentsMargins(6, 2, 6, 2)
        pillLayout.setSpacing(6)

        liveDot = QLabel("●")
        liveDot.setStyleSheet(f"color: {BADGE_SUCCESS_TEXT}; font-size: 10px; background: transparent; border: none;")
        liveText = QLabel("AI PROCTORING ACTIVE • NOMINAL")
        liveText.setStyleSheet(f"color: {BADGE_SUCCESS_TEXT}; font-size: 11px; font-weight: 700; background: transparent; border: none;")
        pillLayout.addWidget(liveDot)
        pillLayout.addWidget(liveText)

        headerLayout.addWidget(statusPill)

        # Telemetry chip
        telemetryChip = QLabel("⚡ Latency: 16ms | 🔒 Secure Stream")
        telemetryChip.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        headerLayout.addWidget(telemetryChip)

        headerLayout.addStretch()

        # Admin Avatar / Profile Pill
        adminPill = QFrame()
        adminPill.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CANVAS};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 20px;
                padding: 4px 12px;
            }}
        """)
        adminLayout = QHBoxLayout(adminPill)
        adminLayout.setContentsMargins(4, 2, 8, 2)
        adminLayout.setSpacing(8)

        avatar = QLabel("AD")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(28, 28)
        avatar.setStyleSheet(f"""
            background-color: {COLOR_PRIMARY};
            color: #FFFFFF;
            font-weight: 700;
            font-size: 11px;
            border-radius: 14px;
        """)

        adminName = QLabel("Admin User")
        adminName.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 12px; background: transparent; border: none;")

        roleBadge = QLabel("SUPERUSER")
        roleBadge.setStyleSheet(f"""
            background-color: {BADGE_INFO_BG};
            color: {BADGE_INFO_TEXT};
            border: 1px solid {BADGE_INFO_BORDER};
            border-radius: 4px;
            font-size: 9px;
            font-weight: 700;
            padding: 1px 4px;
        """)

        adminLayout.addWidget(avatar)
        adminLayout.addWidget(adminName)
        adminLayout.addWidget(roleBadge)

        headerLayout.addWidget(adminPill)
        topHeader.setLayout(headerLayout)

        workspaceLayout.addWidget(topHeader)

        # =====================================================
        # STACKED PAGES
        # =====================================================

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {BG_CANVAS};")

        self.dashboardPage = self.createDashboardPage()
        self.studentsPage = StudentsPage()
        self.examsPage = ExamsPage()
        self.questionsPage = QuestionsPage()
        self.examQuestionsPage = ExamQuestionsPage()
        self.assignmentPage = StudentAssignmentPage()
        self.resultsPage = AdminResultsPage()
        self.violationPage = ViolationDetailsPage()
        self.liveMonitorPage = LiveMonitorPage()

        self.stack.addWidget(self.dashboardPage)
        self.stack.addWidget(self.studentsPage)
        self.stack.addWidget(self.examsPage)
        self.stack.addWidget(self.questionsPage)
        self.stack.addWidget(self.examQuestionsPage)
        self.stack.addWidget(self.assignmentPage)
        self.stack.addWidget(self.resultsPage)
        self.stack.addWidget(self.violationPage)
        self.stack.addWidget(self.liveMonitorPage)

        workspaceLayout.addWidget(self.stack)
        workspace.setLayout(workspaceLayout)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(workspace)

        central.setLayout(mainLayout)

        # =====================================================
        # NAVIGATION CONNECTIONS
        # =====================================================

        self.dashboardBtn.clicked.connect(self.show_dashboard)
        self.studentsBtn.clicked.connect(lambda: self.show_page(self.studentsPage, self.studentsBtn))
        self.examsBtn.clicked.connect(lambda: self.show_page(self.examsPage, self.examsBtn))
        self.questionsBtn.clicked.connect(lambda: self.show_page(self.questionsPage, self.questionsBtn))
        self.examQuestionsBtn.clicked.connect(lambda: self.show_page(self.examQuestionsPage, self.examQuestionsBtn))
        self.assignmentBtn.clicked.connect(lambda: self.show_page(self.assignmentPage, self.assignmentBtn))
        self.resultsBtn.clicked.connect(lambda: self.show_page(self.resultsPage, self.resultsBtn))
        self.violationBtn.clicked.connect(lambda: self.show_page(self.violationPage, self.violationBtn))
        self.liveBtn.clicked.connect(self.show_live_monitoring)
        self.reportsBtn.clicked.connect(self.show_reports)
        self.settingsBtn.clicked.connect(self.show_settings)
        self.logoutBtn.clicked.connect(self.logout)

        # Set initial active button
        self._set_active_button(self.dashboardBtn)

        # Initial refresh
        self.refresh_dashboard()

    # =========================================================
    # ACTIVE BUTTON STATE HELPER
    # =========================================================

    def _set_active_button(self, active_btn):
        for btn in self.navButtons:
            is_active = (btn == active_btn)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # =========================================================
    # GENERIC PAGE NAVIGATION
    # =========================================================

    def show_page(self, page, sender_btn=None):
        if sender_btn:
            self._set_active_button(sender_btn)
        self.stack.setCurrentWidget(page)

    # =========================================================
    # SHOW DASHBOARD
    # =========================================================

    def show_dashboard(self):
        self._set_active_button(self.dashboardBtn)
        self.refresh_dashboard()
        self.stack.setCurrentWidget(self.dashboardPage)

    # =========================================================
    # CREATE DASHBOARD CARD
    # =========================================================

    def createCard(self, title, value, badge_text="+ Active", badge_color="#34D399"):

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QFrame#card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
            }}
            QFrame#card:hover {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        card.setMinimumHeight(130)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        # Top row: Title + Micro Badge
        topRow = QHBoxLayout()
        lblTitle = QLabel(title)
        lblTitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; font-weight: 600; background: transparent; border: none;")

        microBadge = QLabel(badge_text)
        microBadge.setStyleSheet(f"""
            background-color: #0B1726;
            color: {badge_color};
            border: 1px solid #1E3A5F;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
        """)

        topRow.addWidget(lblTitle)
        topRow.addStretch()
        topRow.addWidget(microBadge)

        # Value
        lblValue = QLabel(str(value))
        lblValue.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 32px; font-weight: 800; background: transparent; border: none;")

        # Store label for updating later
        card.valueLabel = lblValue

        layout.addLayout(topRow)
        layout.addWidget(lblValue)
        layout.addStretch()

        card.setLayout(layout)
        return card

    # =========================================================
    # REFRESH DASHBOARD
    # =========================================================

    def refresh_dashboard(self):

        try:
            total_students = StudentModel.get_student_count()
        except Exception:
            total_students = 0

        try:
            total_exams = ExamModel.get_exam_count()
        except Exception:
            total_exams = 0

        self.studentCard.valueLabel.setText(str(total_students))
        self.examCard.valueLabel.setText(str(total_exams))

    # =========================================================
    # CREATE DASHBOARD PAGE
    # =========================================================

    def createDashboardPage(self):

        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(22)

        # =====================================================
        # HEADER
        # =====================================================

        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(4)

        header = QLabel("System Dashboard")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 24px; font-weight: 800;")

        subtitle = QLabel("Real-time telemetry, examinee metrics, and proctoring controls.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")

        headerLayout.addWidget(header)
        headerLayout.addWidget(subtitle)
        layout.addLayout(headerLayout)

        # =====================================================
        # STATISTICS (KPI CARDS)
        # =====================================================

        cards = QGridLayout()
        cards.setSpacing(18)

        self.studentCard = self.createCard("👨‍🎓 Examinees Registered", "0", "Roster", "#38BDF8")
        self.examCard = self.createCard("📝 Active Examinations", "0", "Scheduled", "#A78BFA")
        self.cameraCard = self.createCard("📹 Connected Cameras", "1", "🟢 Live", "#34D399")
        self.violationCard = self.createCard("⚠ AI Infractions Raised", "0", "Alerts", "#FDA4AF")

        cards.addWidget(self.studentCard, 0, 0)
        cards.addWidget(self.examCard, 0, 1)
        cards.addWidget(self.cameraCard, 0, 2)
        cards.addWidget(self.violationCard, 0, 3)

        layout.addLayout(cards)

        # =====================================================
        # LIVE MONITORING PREVIEW CONSOLE
        # =====================================================

        monitor = QFrame()
        monitor.setObjectName("card")
        monitor.setStyleSheet(f"""
            QFrame#card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)
        monitor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        monitorLayout = QVBoxLayout()
        monitorLayout.setContentsMargins(24, 20, 24, 20)
        monitorLayout.setSpacing(14)

        # Preview Header
        previewTop = QHBoxLayout()
        monitorTitle = QLabel("📹 Live Proctoring Surveillance Feeds")
        monitorTitle.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: 700; background: transparent; border: none;")

        openStreamBtn = QPushButton("Open Surveillance Grid →")
        openStreamBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_HOVER};
            }}
        """)
        openStreamBtn.clicked.connect(self.show_live_monitoring)

        previewTop.addWidget(monitorTitle)
        previewTop.addStretch()
        previewTop.addWidget(openStreamBtn)
        monitorLayout.addLayout(previewTop)

        info = QLabel("Real-time OpenCV proctoring feeds from examinee webcams are streamed via TCP port 5001.")
        info.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent; border: none;")
        monitorLayout.addWidget(info)

        # Inner dark screen console
        screenConsole = QFrame()
        screenConsole.setStyleSheet(f"""
            QFrame {{
                background-color: #090D16;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        screenLayout = QVBoxLayout()
        screenLayout.setAlignment(Qt.AlignCenter)
        screenLayout.setSpacing(10)

        radarIcon = QLabel("📡")
        radarIcon.setAlignment(Qt.AlignCenter)
        radarIcon.setFont(QFont("Segoe UI Emoji", 32))
        radarIcon.setStyleSheet("background: transparent; border: none;")

        placeholder = QLabel("Proctoring Server Listening on 0.0.0.0:5001")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 700; background: transparent; border: none;")

        placeholderSub = QLabel("Student video streams will automatically appear here and in Live Monitoring when exams commence.")
        placeholderSub.setAlignment(Qt.AlignCenter)
        placeholderSub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; background: transparent; border: none;")

        screenLayout.addWidget(radarIcon)
        screenLayout.addWidget(placeholder)
        screenLayout.addWidget(placeholderSub)
        screenConsole.setLayout(screenLayout)

        monitorLayout.addWidget(screenConsole)
        monitor.setLayout(monitorLayout)

        layout.addWidget(monitor)
        page.setLayout(layout)

        return page

    # =========================================================
    # LIVE MONITORING
    # =========================================================

    def show_live_monitoring(self):
        self._set_active_button(self.liveBtn)
        self.stack.setCurrentWidget(self.liveMonitorPage)

    # =========================================================
    # REPORTS PLACEHOLDER
    # =========================================================

    def show_reports(self):
        self._set_active_button(self.reportsBtn)
        QMessageBox.information(
            self,
            "Reports",
            "Examination reports and export analytics module."
        )

    # =========================================================
    # SETTINGS PLACEHOLDER
    # =========================================================

    def show_settings(self):
        self._set_active_button(self.settingsBtn)
        QMessageBox.information(
            self,
            "Settings",
            "Proctoring sensitivity and network settings module."
        )

    # =========================================================
    # LOGOUT
    # =========================================================

    def logout(self):

        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout of the admin console?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            QApplication.quit()


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )
    app.setStyleSheet(get_main_stylesheet())

    window = Dashboard()
    window.show()

    sys.exit(
        app.exec_()
    )
