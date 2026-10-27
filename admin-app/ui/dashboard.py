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
    QMessageBox,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtCore import QDate, QTime, Qt, QTimer

from ui.pages.students_page import StudentsPage
from ui.pages.exams_page import ExamsPage
from ui.pages.student_assignment_page import StudentAssignmentPage
from ui.pages.exam_questions_page import ExamQuestionsPage
from ui.pages.questions_page import QuestionsPage
from ui.admin.admin_results_page import AdminResultsPage
from ui.pages.violation_details_page import ViolationDetailsPage
from ui.pages.live_monitor_page import LiveMonitorPage
from ui.pages.reports_page import ReportsPage, report_icon

from models.student_model import StudentModel
from models.exam_model import ExamModel
from database.database import get_connection

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
        register_theme_listener(self._on_dashboard_theme_changed)

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
            self.reportsBtn
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
        self.reportsPage = ReportsPage()

        self.stack.addWidget(self.dashboardPage)
        self.stack.addWidget(self.studentsPage)
        self.stack.addWidget(self.examsPage)
        self.stack.addWidget(self.questionsPage)
        self.stack.addWidget(self.examQuestionsPage)
        self.stack.addWidget(self.assignmentPage)
        self.stack.addWidget(self.resultsPage)
        self.stack.addWidget(self.violationPage)
        self.stack.addWidget(self.liveMonitorPage)
        self.stack.addWidget(self.reportsPage)

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
        self.logoutBtn.clicked.connect(self.logout)

        # Set initial active button
        self._set_active_button(self.dashboardBtn)

        # Apply initial theme badge styles
        self._apply_header_styles()

        # Initial refresh
        self.refresh_dashboard()
        self._dashboard_tick_count = 0
        self.dashboardPreviewTimer = QTimer(self)
        self.dashboardPreviewTimer.setInterval(500)
        self.dashboardPreviewTimer.timeout.connect(self._dashboard_tick)
        self.dashboardPreviewTimer.start()

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

    def createCard(self, title, value, badge_text="", badge_color="#2563EB"):
        """A compact dashboard metric; its value is filled by refresh_dashboard."""
        card = QFrame()
        card.setObjectName("dashboardMetric")
        card.setProperty("accent", {
            "#2563EB": "blue", "#10B981": "green",
            "#4F46E5": "indigo", "#EF4444": "red",
        }.get(badge_color, "blue"))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 11)
        layout.setSpacing(3)
        icon = QLabel()
        icon.setObjectName("dashboardMetricIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(31, 31)
        icon_background = {
            "#2563EB": "#E8F0FF", "#10B981": "#E0F8ED",
            "#4F46E5": "#ECEAFF", "#EF4444": "#FFE9ED",
        }.get(badge_color, "#E8F0FF")
        icon.setPixmap(report_icon({
            "Total Students": "users", "Total Exams": "document",
            "Active Sessions": "chart", "Violations Today": "pie",
        }.get(title, "chart"), 31, badge_color, icon_background))
        title_label = QLabel(title)
        title_label.setObjectName("dashboardMetricTitle")
        value_label = QLabel(str(value))
        value_label.setObjectName("dashboardMetricValue")
        note = QLabel(badge_text)
        note.setObjectName("dashboardMetricNote")
        note.setStyleSheet(f"color: {badge_color}; background: transparent; border: none;")
        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(note)
        card.valueLabel = value_label
        return card

    # =========================================================
    # REFRESH DASHBOARD
    # =========================================================

    def refresh_dashboard(self):
        try:
            total_students = StudentModel.get_student_count()
        except Exception as error:
            print(">>> Dashboard student count error:", error)
            total_students = "—"

        try:
            total_exams = ExamModel.get_exam_count()
        except Exception as error:
            print(">>> Dashboard exam count error:", error)
            total_exams = "—"

        self.studentCard.valueLabel.setText(str(total_students))
        self.examCard.valueLabel.setText(str(total_exams))
        connection = None
        try:
            connection = get_connection()
            connection.execute("SELECT 1").fetchone()
            active_sessions = connection.execute("""
                SELECT COUNT(*) FROM exam_attempts ea
                JOIN exams e ON e.id = ea.exam_id
                WHERE e.exam_status = 'Started' AND ea.status = 'IN_PROGRESS'
            """).fetchone()[0]
            violations_today = connection.execute("""
                SELECT COUNT(*) FROM violations
                WHERE date(date_time) = date('now', 'localtime')
            """).fetchone()[0]
            recent_exams = connection.execute("""
                SELECT e.exam_name, e.subject_name, e.exam_date, e.exam_status,
                       COUNT(sa.student_id) AS assigned_count
                FROM exams e
                LEFT JOIN student_assignment sa ON sa.exam_id = e.id
                GROUP BY e.id
                ORDER BY e.exam_date DESC, e.id DESC LIMIT 5
            """).fetchall()
        except Exception as error:
            print(">>> Dashboard summary refresh error:", error)
            self.studentCard.valueLabel.setText("—")
            self.examCard.valueLabel.setText("—")
            self.sessionCard.valueLabel.setText("—")
            self.violationCard.valueLabel.setText("—")
            self.recentTable.setRowCount(0)
            self.recentEmpty.setText("Examinations are temporarily unavailable.")
            self.recentEmpty.show()
            self._dashboard_database_ok = False
        else:
            self.sessionCard.valueLabel.setText(str(active_sessions))
            self.violationCard.valueLabel.setText(str(violations_today))
            self.recentTable.setRowCount(len(recent_exams))
            self.recentEmpty.setText("No examinations yet.")
            self.recentEmpty.setVisible(not recent_exams)
            for row_index, exam in enumerate(recent_exams):
                date = QDate.fromString(str(exam["exam_date"]), "yyyy-MM-dd")
                values = (
                    exam["exam_name"], exam["subject_name"],
                    date.toString("dd MMM yyyy") if date.isValid() else exam["exam_date"],
                    str(exam["assigned_count"]), exam["exam_status"] or "Unknown",
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setToolTip(str(value))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    if column == 4:
                        color = {
                            "Started": "#059669", "Scheduled": "#2563EB",
                            "Completed": "#64748B",
                        }.get(value, "#B45309")
                        item.setForeground(QColor(color))
                    self.recentTable.setItem(row_index, column, item)
            self._dashboard_database_ok = True
        finally:
            if connection is not None:
                connection.close()
        self._refresh_dashboard_previews()

    # =========================================================
    # CREATE DASHBOARD PAGE
    # =========================================================

    def createDashboardPage(self):
        page = QWidget()
        page.setObjectName("systemDashboardPage")
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        page_layout.addWidget(scroll)
        canvas = QWidget()
        canvas.setObjectName("dashboardCanvas")
        canvas.setMinimumWidth(760)
        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        scroll.setWidget(canvas)

        heading = QHBoxLayout()
        title_group = QVBoxLayout()
        title_group.setSpacing(2)
        hour = QTime.currentTime().hour()
        greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
        title = QLabel(f"{greeting}, Admin!")
        title.setObjectName("dashboardTitle")
        subtitle = QLabel("Here's a quick overview of your examination system.")
        subtitle.setObjectName("dashboardMuted")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        heading.addLayout(title_group)
        heading.addStretch()
        self.dashboardDate = QLabel(QDate.currentDate().toString("dd MMM yyyy"))
        self.dashboardDate.setObjectName("dashboardMuted")
        heading.addWidget(self.dashboardDate, alignment=Qt.AlignVCenter)
        layout.addLayout(heading)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.studentCard = self.createCard("Total Students", "—", "Registered students", "#2563EB")
        self.examCard = self.createCard("Total Exams", "—", "Examinations created", "#10B981")
        self.sessionCard = self.createCard("Active Sessions", "—", "In-progress attempts", "#4F46E5")
        self.violationCard = self.createCard("Violations Today", "—", "Recorded today", "#EF4444")
        for card in (self.studentCard, self.examCard, self.sessionCard, self.violationCard):
            cards.addWidget(card, 1)
        layout.addLayout(cards)

        middle = QHBoxLayout()
        middle.setSpacing(12)
        recent = QFrame()
        recent.setObjectName("dashboardPanel")
        recent_layout = QVBoxLayout(recent)
        recent_layout.setContentsMargins(14, 12, 14, 12)
        recent_layout.setSpacing(8)
        recent_heading = QHBoxLayout()
        recent_title = QLabel("Recent Examinations")
        recent_title.setObjectName("dashboardSectionTitle")
        recent_heading.addWidget(recent_title)
        recent_heading.addStretch()
        view_all = QPushButton("View All →")
        view_all.setObjectName("dashboardLink")
        view_all.clicked.connect(lambda: self.show_page(self.examsPage, self.examsBtn))
        recent_heading.addWidget(view_all)
        recent_layout.addLayout(recent_heading)
        self.recentTable = QTableWidget(0, 5)
        self.recentTable.setObjectName("dashboardRecentTable")
        self.recentTable.setHorizontalHeaderLabels(
            ["Exam Name", "Subject", "Date", "Assigned", "Status"]
        )
        self.recentTable.verticalHeader().hide()
        self.recentTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recentTable.horizontalHeader().setFixedHeight(27)
        self.recentTable.verticalHeader().setDefaultSectionSize(29)
        self.recentTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recentTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.recentTable.setShowGrid(False)
        self.recentTable.setMinimumHeight(166)
        recent_layout.addWidget(self.recentTable, 1)
        self.recentEmpty = QLabel("No examinations yet.")
        self.recentEmpty.setObjectName("dashboardMuted")
        self.recentEmpty.hide()
        recent_layout.addWidget(self.recentEmpty)
        middle.addWidget(recent, 3)

        status_panel = QFrame()
        status_panel.setObjectName("dashboardPanel")
        status_layout = QVBoxLayout(status_panel)
        status_layout.setContentsMargins(14, 12, 14, 12)
        status_layout.setSpacing(10)
        status_title = QLabel("System Status")
        status_title.setObjectName("dashboardSectionTitle")
        status_layout.addWidget(status_title)
        self.systemStatusValues = {}
        for name in ("Database", "AI Proctoring Service", "Video Streaming (TCP 5001)", "Camera Connection"):
            row = QHBoxLayout()
            label = QLabel(name)
            label.setObjectName("dashboardStatusName")
            value = QLabel("Checking…")
            value.setObjectName("dashboardStatusValue")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            status_layout.addLayout(row, 1)
            self.systemStatusValues[name] = value
        self.systemStatusValues["AI Proctoring Service"].setToolTip(
            "AI detection runs in Student-App; no service heartbeat is available to Admin-App."
        )
        middle.addWidget(status_panel, 2)
        layout.addLayout(middle)

        monitor = QFrame()
        monitor.setObjectName("dashboardPanel")
        monitorLayout = QVBoxLayout(monitor)
        monitorLayout.setContentsMargins(14, 12, 14, 12)
        monitorLayout.setSpacing(9)
        previewTop = QHBoxLayout()
        monitorTitle = QLabel("Live Proctoring Feeds")
        monitorTitle.setObjectName("dashboardSectionTitle")
        openStreamBtn = QPushButton("Open Surveillance Grid →")
        openStreamBtn.setObjectName("dashboardPrimaryButton")
        openStreamBtn.setCursor(Qt.PointingHandCursor)
        openStreamBtn.setMinimumHeight(31)
        openStreamBtn.clicked.connect(self.show_live_monitoring)
        previewTop.addWidget(monitorTitle)
        previewTop.addStretch()
        previewTop.addWidget(openStreamBtn)
        monitorLayout.addLayout(previewTop)
        info = QLabel("Camera previews mirror active student streams from TCP port 5001.")
        info.setObjectName("dashboardMuted")
        monitorLayout.addWidget(info)
        feeds = QHBoxLayout()
        feeds.setSpacing(9)
        self.dashboardPreviewSlots = []
        for number in range(1, 5):
            tile = QFrame()
            tile.setObjectName("dashboardCameraTile")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(7, 7, 7, 7)
            tile_layout.setSpacing(4)
            tile_top = QHBoxLayout()
            camera_name = QLabel(f"Camera {number}")
            camera_name.setObjectName("dashboardCameraName")
            state_label = QLabel("Offline")
            state_label.setObjectName("dashboardCameraState")
            state_label.setMinimumWidth(65)
            state_label.setAlignment(Qt.AlignCenter)
            tile_top.addWidget(camera_name)
            tile_top.addStretch()
            tile_top.addWidget(state_label)
            tile_layout.addLayout(tile_top)
            screen = QLabel("No feed")
            screen.setObjectName("dashboardVideoScreen")
            screen.setAlignment(Qt.AlignCenter)
            screen.setMinimumHeight(90)
            screen.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
            tile_layout.addWidget(screen, 1)
            student = QLabel("No student assigned")
            student.setObjectName("dashboardCameraStudent")
            student.setToolTip("No student assigned")
            student.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            tile_layout.addWidget(student)
            feeds.addWidget(tile, 1)
            self.dashboardPreviewSlots.append((screen, state_label, student))

        session_panel = QFrame()
        session_panel.setObjectName("dashboardSessionsPanel")
        session_layout = QVBoxLayout(session_panel)
        session_layout.setContentsMargins(12, 12, 12, 12)
        session_layout.setSpacing(5)
        session_title = QLabel("Live Sessions")
        session_title.setObjectName("dashboardSectionTitle")
        self.liveSessionValue = QLabel("0")
        self.liveSessionValue.setObjectName("dashboardMetricValue")
        self.liveSessionCaption = QLabel("No camera connected")
        self.liveSessionCaption.setObjectName("dashboardMuted")
        session_layout.addWidget(session_title)
        session_layout.addWidget(self.liveSessionValue)
        session_layout.addWidget(self.liveSessionCaption)
        session_layout.addStretch()
        feeds.addWidget(session_panel, 1)
        monitorLayout.addLayout(feeds)
        layout.addWidget(monitor)
        layout.addStretch(1)
        self._style_dashboard_page(page)
        return page

    def _style_dashboard_page(self, page):
        """Style only the System Dashboard; navigation and other pages keep their QSS."""
        css = """
            QWidget#systemDashboardPage, QWidget#dashboardCanvas, QScrollArea {
                background: #F8FAFC; color: #1D3159; font-family: 'Segoe UI';
            }
            QFrame#dashboardPanel, QFrame#dashboardMetric, QFrame#dashboardCameraTile {
                background: white; border: 1px solid #DFE7F4; border-radius: 10px;
            }
            QFrame#dashboardMetric[accent="blue"] { background: #F8FAFF; border-color: #C9D7FF; }
            QFrame#dashboardMetric[accent="green"] { background: #F6FCF9; border-color: #B8E8D0; }
            QFrame#dashboardMetric[accent="indigo"] { background: #F8F8FF; border-color: #D3D1FF; }
            QFrame#dashboardMetric[accent="red"] { background: #FFFAFB; border-color: #FFCFD4; }
            QLabel { background: transparent; border: none; color: #1D3159; }
            QLabel#dashboardTitle { font-size: 20px; font-weight: 700; }
            QLabel#dashboardMuted { color: #7184A7; font-size: 11px; }
            QLabel#dashboardMetricTitle { color: #65799F; font-size: 11px; }
            QLabel#dashboardMetricValue { font-size: 24px; font-weight: 700; color: #1D3159; }
            QLabel#dashboardMetricNote { font-size: 10px; }
            QLabel#dashboardSectionTitle { font-size: 13px; font-weight: 700; }
            QLabel#dashboardStatusName { font-size: 11px; color: #405579; }
            QLabel#dashboardStatusValue { font-size: 11px; font-weight: 600; }
            QLabel#dashboardCameraName { font-size: 11px; font-weight: 700; }
            QLabel#dashboardCameraStudent { font-size: 10px; color: #52698E; }
            QLabel#dashboardVideoScreen {
                background: #182235; color: #B6C4D8; border: none;
                border-radius: 6px; font-size: 11px;
            }
            QFrame#dashboardSessionsPanel {
                background: #F3F7FF; border: 1px solid #E0E8F7; border-radius: 9px;
            }
            QTableWidget#dashboardRecentTable {
                background: white; alternate-background-color: #F9FBFF;
                border: none; color: #34496D; font-size: 11px;
            }
            QTableWidget#dashboardRecentTable::item {
                padding: 4px 6px; border-bottom: 1px solid #EDF1F8;
            }
            QTableWidget#dashboardRecentTable QHeaderView::section {
                background: #F1F5FA; color: #405579; border: none;
                padding: 5px 6px; font-size: 10px; font-weight: 700;
            }
            QPushButton#dashboardLink {
                background: transparent; border: none; color: #4164D9;
                font-size: 11px; font-weight: 600; padding: 4px;
            }
            QPushButton#dashboardLink:hover { color: #274DBB; }
            QPushButton#dashboardPrimaryButton {
                background: #4264EC; color: white; border: none;
                border-radius: 8px; padding: 6px 12px; font-size: 11px;
                font-weight: 600;
            }
            QPushButton#dashboardPrimaryButton:hover { background: #3152D4; }
        """
        if get_current_theme() == "dark":
            css += """
                QWidget#systemDashboardPage, QWidget#dashboardCanvas, QScrollArea {
                    background: #0F172A; color: #E2E8F0;
                }
                QFrame#dashboardPanel, QFrame#dashboardMetric, QFrame#dashboardCameraTile {
                    background: #1E293B; border-color: #334155;
                }
                QFrame#dashboardMetric[accent="blue"], QFrame#dashboardMetric[accent="green"],
                QFrame#dashboardMetric[accent="indigo"], QFrame#dashboardMetric[accent="red"] {
                    background: #1E293B; border-color: #334155;
                }
                QLabel { color: #E2E8F0; }
                QLabel#dashboardMuted, QLabel#dashboardMetricTitle,
                QLabel#dashboardCameraStudent, QLabel#dashboardStatusName { color: #94A3B8; }
                QLabel#dashboardMetricValue, QLabel#dashboardSectionTitle,
                QLabel#dashboardTitle { color: #F8FAFC; }
                QFrame#dashboardSessionsPanel { background: #172338; border-color: #334155; }
                QTableWidget#dashboardRecentTable {
                    background: #1E293B; alternate-background-color: #172338; color: #E2E8F0;
                }
                QTableWidget#dashboardRecentTable::item { border-bottom-color: #334155; }
                QTableWidget#dashboardRecentTable QHeaderView::section {
                    background: #172338; color: #CBD5E1;
                }
            """
        page.setStyleSheet(css)

    def _on_dashboard_theme_changed(self, *_):
        self._style_dashboard_page(self.dashboardPage)

    def _dashboard_status(self, name, text, color):
        value = self.systemStatusValues[name]
        value.setText("●  " + text)
        value.setStyleSheet(f"color: {color}; background: transparent; border: none;")

    def _refresh_dashboard_previews(self):
        monitor = getattr(self, "liveMonitorPage", None)
        slots = monitor.camera_slots if monitor is not None else {}
        for number, (screen, state_label, student_label) in enumerate(self.dashboardPreviewSlots, 1):
            card = slots.get(number)
            state = card.state if card is not None and monitor.active_exam_id is not None else "offline"
            label, color, background = {
                "normal": ("Live", "#047857", "#DDF7EB"),
                "violation": ("Alert", "#B91C1C", "#FEE2E2"),
                "waiting": ("Waiting", "#B45309", "#FEF3C7"),
                "submitted": ("Completed", "#2563EB", "#DBEAFE"),
                "offline": ("Offline", "#64748B", "#E8EDF4"),
            }.get(state, ("Offline", "#64748B", "#E8EDF4"))
            state_label.setText("● " + label)
            state_label.setStyleSheet(
                f"color: {color}; background: {background}; border: none;"
                "border-radius: 8px; padding: 2px 5px; font-size: 10px;"
            )
            if card is not None and card.register_no and monitor.active_exam_id is not None:
                details = f"{card.student_name} · {card.register_no}"
            else:
                details = "No student assigned"
            student_label.setText(details)
            student_label.setToolTip(details)
            source = card.cameraLabel._source_pixmap if card is not None else None
            if state in ("normal", "violation") and source is not None and not source.isNull():
                screen.setText("")
                screen.setPixmap(source.scaled(screen.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                screen.setPixmap(QPixmap())
                screen.setText({
                    "waiting": "Waiting for student",
                    "submitted": "Exam submitted",
                    "offline": "No feed",
                }.get(state, "No feed"))

        connected = sum(
            card.state in ("normal", "violation")
            for card in monitor.studentCards.values()
        ) if monitor is not None and monitor.active_exam_id is not None else 0
        assigned = len(monitor.students_list) if monitor is not None and monitor.active_exam_id is not None else 0
        self.liveSessionValue.setText(str(connected))
        self.liveSessionCaption.setText(
            f"{connected} of {assigned} assigned cameras online" if assigned else "No active camera connection"
        )
        self._dashboard_status(
            "Database", "Online" if getattr(self, "_dashboard_database_ok", False) else "Unavailable",
            "#059669" if getattr(self, "_dashboard_database_ok", False) else "#DC2626",
        )
        self._dashboard_status("AI Proctoring Service", "Not reported", "#64748B")
        server = monitor.cameraServer if monitor is not None else None
        streaming = bool(server and server.running and server.server_socket is not None)
        self._dashboard_status(
            "Video Streaming (TCP 5001)", "Listening" if streaming else "Unavailable",
            "#059669" if streaming else "#DC2626",
        )
        self._dashboard_status(
            "Camera Connection", f"{connected} connected" if connected else "No camera",
            "#059669" if connected else "#B45309",
        )

    def _dashboard_tick(self):
        if not self.isVisible() or self.stack.currentWidget() is not self.dashboardPage:
            return
        self._dashboard_tick_count += 1
        if self._dashboard_tick_count % 10 == 0:
            self.refresh_dashboard()
            self.dashboardDate.setText(QDate.currentDate().toString("dd MMM yyyy"))
        else:
            self._refresh_dashboard_previews()

    # =========================================================
    # LIVE MONITORING
    # =========================================================

    def show_live_monitoring(self):
        self._set_active_button(self.liveBtn)
        self.stack.setCurrentWidget(self.liveMonitorPage)

    # =========================================================
    # REPORTS
    # =========================================================

    def show_reports(self):
        self._set_active_button(self.reportsBtn)
        self.stack.setCurrentWidget(self.reportsPage)

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
