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

from ui.theme_manager import (
    apply_theme,
    toggle_theme,
    get_current_theme,
    get_theme_palette,
    register_theme_listener,
)
from ui.qss_theme import get_main_stylesheet


class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Online Examination & AI Proctoring System - Admin Dashboard"
        )

        self.resize(1480, 880)

        self.navButtons = []
        self._active_btn = None
        self.kpi_cards = []

        self.setupUI()
        register_theme_listener(self._on_theme_changed)

    # =========================================================
    # SETUP UI
    # =========================================================

    def setupUI(self):

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # =====================================================
        # SIDEBAR (220px width)
        # =====================================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(225)

        sideLayout = QVBoxLayout()
        sideLayout.setContentsMargins(14, 20, 14, 20)
        sideLayout.setSpacing(6)

        # -----------------------------------------------------
        # Brand Logo Header
        # -----------------------------------------------------
        brandContainer = QFrame()
        brandContainer.setObjectName("brandContainer")
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
        title.setObjectName("brandTitle")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 1.2px;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("Online Exam Monitor")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("brandSubtitle")
        subtitle.setStyleSheet("""
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
        sep.setObjectName("sidebarSep")
        sep.setStyleSheet("max-height: 1px; margin-bottom: 8px; opacity: 0.5;")
        sideLayout.addWidget(sep)

        # Section Label
        sectionLbl = QLabel("NAVIGATION")
        sectionLbl.setObjectName("sectionHeader")
        sectionLbl.setStyleSheet("font-size: 11px; font-weight: 700; padding: 4px 10px; letter-spacing: 1px;")
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
            btn.setObjectName("navBtn")
            btn.setCursor(Qt.PointingHandCursor)
            sideLayout.addWidget(btn)

        sideLayout.addStretch()

        # -----------------------------------------------------
        # Logout
        # -----------------------------------------------------
        self.logoutBtn = QPushButton("🚪  Logout")
        self.logoutBtn.setObjectName("dangerBtn")
        self.logoutBtn.setCursor(Qt.PointingHandCursor)
        self.logoutBtn.setMinimumHeight(40)
        sideLayout.addWidget(self.logoutBtn)

        sidebar.setLayout(sideLayout)

        # =====================================================
        # WORKSPACE AREA (Header + Stacked Pages)
        # =====================================================

        workspace = QWidget()
        workspace.setObjectName("pageWidget")
        workspaceLayout = QVBoxLayout()
        workspaceLayout.setContentsMargins(0, 0, 0, 0)
        workspaceLayout.setSpacing(0)

        # -----------------------------------------------------
        # Top Header Bar
        # -----------------------------------------------------
        topHeader = QFrame()
        topHeader.setObjectName("topHeader")
        topHeader.setFixedHeight(64)

        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(24, 0, 24, 0)
        headerLayout.setSpacing(16)

        # Left status badge
        self.statusPill = QFrame()
        self.statusPill.setObjectName("statusPill")
        pillLayout = QHBoxLayout(self.statusPill)
        pillLayout.setContentsMargins(10, 4, 12, 4)
        pillLayout.setSpacing(6)

        self.liveDot = QLabel("●")
        self.liveDot.setStyleSheet("font-size: 10px; background: transparent; border: none;")
        self.liveText = QLabel("AI PROCTORING ACTIVE • NOMINAL")
        self.liveText.setStyleSheet("font-size: 11px; font-weight: 700; background: transparent; border: none;")
        pillLayout.addWidget(self.liveDot)
        pillLayout.addWidget(self.liveText)

        headerLayout.addWidget(self.statusPill)

        # Telemetry chip
        self.telemetryChip = QLabel("⚡ Latency: 16ms | 🔒 Secure Stream")
        self.telemetryChip.setObjectName("telemetryChip")
        self.telemetryChip.setStyleSheet("font-size: 13px; font-weight: 500; background: transparent; border: none;")
        headerLayout.addWidget(self.telemetryChip)

        headerLayout.addStretch()

        # -----------------------------------------------------
        # THEME TOGGLE SWITCH BUTTON
        # -----------------------------------------------------
        self.themeToggleBtn = QPushButton()
        self.themeToggleBtn.setObjectName("themeToggleBtn")
        self.themeToggleBtn.setCursor(Qt.PointingHandCursor)
        self.themeToggleBtn.setMinimumHeight(36)
        self.update_theme_toggle_text()
        self.themeToggleBtn.clicked.connect(self.toggle_theme)
        headerLayout.addWidget(self.themeToggleBtn)

        # Admin Avatar / Profile Pill
        self.adminPill = QFrame()
        self.adminPill.setObjectName("adminPill")
        self.adminPill.setStyleSheet("""
            QFrame#adminPill {
                border-radius: 20px;
                padding: 4px 12px;
            }
        """)
        adminLayout = QHBoxLayout(self.adminPill)
        adminLayout.setContentsMargins(4, 2, 8, 2)
        adminLayout.setSpacing(8)

        self.avatar = QLabel("AD")
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setFixedSize(28, 28)
        self.avatar.setStyleSheet("""
            color: #FFFFFF;
            font-weight: 700;
            font-size: 11px;
            border-radius: 14px;
        """)

        self.adminName = QLabel("Admin User")
        self.adminName.setStyleSheet("font-weight: 600; font-size: 13px; background: transparent; border: none;")

        self.roleBadge = QLabel("SUPERUSER")
        self.roleBadge.setStyleSheet("""
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
        """)

        adminLayout.addWidget(self.avatar)
        adminLayout.addWidget(self.adminName)
        adminLayout.addWidget(self.roleBadge)

        headerLayout.addWidget(self.adminPill)
        topHeader.setLayout(headerLayout)

        workspaceLayout.addWidget(topHeader)

        # =====================================================
        # STACKED PAGES
        # =====================================================

        self.stack = QStackedWidget()
        self.stack.setObjectName("pageWidget")

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

        # Apply initial theme badge styles
        self._apply_header_styles()

        # Initial refresh
        self.refresh_dashboard()

    # =========================================================
    # THEME SWITCHER
    # =========================================================

    def update_theme_toggle_text(self):
        current = get_current_theme()
        if current == "dark":
            self.themeToggleBtn.setText("🌙 Dark Mode")
            self.themeToggleBtn.setToolTip("Click to switch to Light Mode")
        else:
            self.themeToggleBtn.setText("☀️ Light Mode")
            self.themeToggleBtn.setToolTip("Click to switch to Dark Mode")

    def toggle_theme(self):
        new_theme = toggle_theme(QApplication.instance())
        self.update_theme_toggle_text()
        self._apply_header_styles()
        if self._active_btn:
            self._set_active_button(self._active_btn)

    def _on_theme_changed(self, theme_name):
        self.update_theme_toggle_text()
        self._apply_header_styles()

    def _apply_header_styles(self):
        p = get_theme_palette()

        # Status Pill styling
        self.statusPill.setStyleSheet(f"""
            QFrame#statusPill {{
                background-color: {p['badge_success_bg']};
                border: 1px solid {p['badge_success_border']};
                border-radius: 14px;
            }}
        """)
        self.liveDot.setStyleSheet(f"color: {p['badge_success_text']}; font-size: 10px; background: transparent; border: none;")
        self.liveText.setStyleSheet(f"color: {p['badge_success_text']}; font-size: 11px; font-weight: 700; background: transparent; border: none;")

        # Telemetry styling
        self.telemetryChip.setStyleSheet(f"color: {p['text_secondary']}; font-size: 13px; font-weight: 500; background: transparent; border: none;")

        # Admin Pill styling
        self.adminPill.setStyleSheet(f"""
            QFrame#adminPill {{
                background-color: {p['bg_card_alt']};
                border: 1px solid {p['border_subtle']};
                border-radius: 20px;
            }}
        """)
        self.avatar.setStyleSheet(f"""
            background-color: {p['color_primary']};
            color: #FFFFFF;
            font-weight: 700;
            font-size: 11px;
            border-radius: 14px;
        """)
        self.adminName.setStyleSheet(f"color: {p['text_primary']}; font-weight: 600; font-size: 13px; background: transparent; border: none;")
        self.roleBadge.setStyleSheet(f"""
            background-color: {p['badge_info_bg']};
            color: {p['badge_info_text']};
            border: 1px solid {p['badge_info_border']};
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
        """)

        # Re-apply card badge styling for registered KPI cards
        for card_info in self.kpi_cards:
            badge = card_info["badge"]
            v_type = card_info["variant"]
            if v_type == "success":
                bg, fg, border = p['badge_success_bg'], p['badge_success_text'], p['badge_success_border']
            elif v_type == "danger":
                bg, fg, border = p['badge_danger_bg'], p['badge_danger_text'], p['badge_danger_border']
            elif v_type == "info":
                bg, fg, border = p['badge_info_bg'], p['badge_info_text'], p['badge_info_border']
            elif v_type == "warning":
                bg, fg, border = p['badge_warning_bg'], p['badge_warning_text'], p['badge_warning_border']
            else:
                bg, fg, border = p['badge_neutral_bg'], p['badge_neutral_text'], p['badge_neutral_border']

            badge.setStyleSheet(f"""
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: 700;
            """)

    # =========================================================
    # ACTIVE BUTTON STATE HELPER
    # =========================================================

    def _set_active_button(self, active_btn):
        self._active_btn = active_btn
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
        card.setCursor(Qt.PointingHandCursor)
        card.setMinimumHeight(135)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        # Top row: Title + Micro Badge
        topRow = QHBoxLayout()
        lblTitle = QLabel(title)
        lblTitle.setObjectName("kpiTitle")

        microBadge = QLabel(badge_text)

        # Determine variant
        variant = "info"
        if "live" in badge_text.lower() or "active" in badge_text.lower():
            variant = "success"
        elif "alert" in badge_text.lower() or "flag" in badge_text.lower():
            variant = "danger"
        elif "roster" in badge_text.lower():
            variant = "info"
        elif "schedule" in badge_text.lower():
            variant = "warning"

        self.kpi_cards.append({
            "badge": microBadge,
            "variant": variant
        })

        topRow.addWidget(lblTitle)
        topRow.addStretch()
        topRow.addWidget(microBadge)

        # Value
        lblValue = QLabel(str(value))
        lblValue.setObjectName("kpiValue")

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
        page.setObjectName("pageWidget")
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(22)

        # =====================================================
        # HEADER
        # =====================================================

        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(4)

        header = QLabel("System Dashboard")
        header.setObjectName("pageTitle")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))

        subtitle = QLabel("Real-time telemetry, examinee metrics, and proctoring controls.")
        subtitle.setObjectName("pageSubtitle")

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
        monitor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        monitorLayout = QVBoxLayout()
        monitorLayout.setContentsMargins(24, 20, 24, 20)
        monitorLayout.setSpacing(14)

        # Preview Header
        previewTop = QHBoxLayout()
        monitorTitle = QLabel("📹 Live Proctoring Surveillance Feeds")
        monitorTitle.setObjectName("sectionHeader")

        openStreamBtn = QPushButton("Open Surveillance Grid →")
        openStreamBtn.setCursor(Qt.PointingHandCursor)
        openStreamBtn.setMinimumHeight(38)
        openStreamBtn.clicked.connect(self.show_live_monitoring)

        previewTop.addWidget(monitorTitle)
        previewTop.addStretch()
        previewTop.addWidget(openStreamBtn)
        monitorLayout.addLayout(previewTop)

        info = QLabel("Real-time OpenCV proctoring feeds from examinee webcams are streamed via TCP port 5001.")
        info.setObjectName("pageSubtitle")
        monitorLayout.addWidget(info)

        # Inner screen console
        screenConsole = QFrame()
        screenConsole.setObjectName("cameraFeed")
        screenLayout = QVBoxLayout()
        screenLayout.setAlignment(Qt.AlignCenter)
        screenLayout.setSpacing(10)

        radarIcon = QLabel("📡")
        radarIcon.setAlignment(Qt.AlignCenter)
        radarIcon.setFont(QFont("Segoe UI Emoji", 34))
        radarIcon.setStyleSheet("background: transparent; border: none;")

        placeholder = QLabel("Proctoring Server Listening on 0.0.0.0:5001")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setObjectName("sectionHeader")

        placeholderSub = QLabel("Student video streams will automatically appear here and in Live Monitoring when exams commence.")
        placeholderSub.setAlignment(Qt.AlignCenter)
        placeholderSub.setObjectName("pageSubtitle")

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
    apply_theme(app, "light")

    window = Dashboard()
    window.show()

    sys.exit(
        app.exec_()
    )
