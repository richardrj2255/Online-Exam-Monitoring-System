import sys
import os
import random

# Add admin-app directory to sys.path if running as standalone
current_dir = os.path.dirname(os.path.abspath(__file__))
admin_app_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if admin_app_dir not in sys.path:
    sys.path.insert(0, admin_app_dir)

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QListView,
    QFrame,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.exam_model import ExamModel
from models.question_model import QuestionModel
from ui.theme_manager import get_theme_palette, register_theme_listener


class ExamQuestionsPage(QWidget):

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self):
        super().__init__()

        self.selected_exam_id = None
        self._all_exams_cache = []

        self.setup_ui()

        self.load_exams()
        self.load_categories()
        register_theme_listener(self._on_theme_changed)

    # ==========================================================
    # UI SETUP
    # ==========================================================

    def setup_ui(self):

        self.setObjectName("pageWidget")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setObjectName("pageCanvas")
        container.setStyleSheet("""
            QWidget#pageCanvas {
                background-color: #F8FAFC;
            }
            .QFrame[objectName^="card_"] {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(28, 22, 28, 24)
        main_layout.setSpacing(18)

        # ======================================================
        # 1. HEADER CARD (Blue square icon + titles)
        # ======================================================

        self.headerCard = QFrame()
        self.headerCard.setObjectName("card_header")
        headerLayout = QHBoxLayout(self.headerCard)
        headerLayout.setContentsMargins(20, 16, 20, 16)
        headerLayout.setSpacing(16)

        # Blue square badge icon
        self.headerIconBox = QLabel("📋")
        self.headerIconBox.setFixedSize(46, 46)
        self.headerIconBox.setAlignment(Qt.AlignCenter)
        self.headerIconBox.setFont(QFont("Segoe UI Emoji", 18))
        self.headerIconBox.setStyleSheet("""
            background-color: #2563EB;
            color: #FFFFFF;
            border-radius: 10px;
        """)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel("Examination Question Assembly & Mapping")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Assign question sets to examinations manually or synthesize random balanced exams via automated selection.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setFont(QFont("Segoe UI", 11))

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)

        headerLayout.addWidget(self.headerIconBox)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        main_layout.addWidget(self.headerCard)

        # ======================================================
        # 2. TOP SUMMARY / CONTROL BAR (Structured Metric Cards)
        # ======================================================

        self.summaryCard = QFrame()
        self.summaryCard.setObjectName("card_metrics")
        self.summaryCard.setStyleSheet("background: transparent; border: none;")
        summaryLayout = QHBoxLayout(self.summaryCard)
        summaryLayout.setContentsMargins(0, 0, 0, 0)
        summaryLayout.setSpacing(14)

        # --- Card 1: Active Examination ---
        self.examPod = QFrame()
        self.examPod.setObjectName("examPod")
        examPodLayout = QHBoxLayout(self.examPod)
        examPodLayout.setContentsMargins(14, 10, 14, 10)
        examPodLayout.setSpacing(12)

        calIcon = QLabel("📅")
        calIcon.setFont(QFont("Segoe UI Emoji", 16))
        calIcon.setAlignment(Qt.AlignCenter)
        calIcon.setFixedSize(36, 36)
        calIcon.setStyleSheet("background-color: #DBEAFE; border-radius: 8px;")

        examTextLayout = QVBoxLayout()
        examTextLayout.setSpacing(2)

        examHeaderLbl = QLabel("ACTIVE EXAMINATION")
        examHeaderLbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.5px; background: transparent; border: none;")

        self.exam_combo = QComboBox()
        self.exam_combo.setView(QListView())
        self.exam_combo.setMinimumHeight(28)
        self.exam_combo.setCursor(Qt.PointingHandCursor)
        self.exam_combo.setStyleSheet("""
            QComboBox {
                font-weight: 700;
                font-size: 13px;
                color: #1E293B;
                background: transparent;
                border: none;
                padding-right: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 16px;
            }
        """)
        self.exam_combo.currentIndexChanged.connect(self.exam_changed)

        self.exam_date_label = QLabel("Loading schedule...")
        self.exam_date_label.setStyleSheet("font-size: 11px; color: #64748B; background: transparent; border: none;")

        examTextLayout.addWidget(examHeaderLbl)
        examTextLayout.addWidget(self.exam_combo)
        examTextLayout.addWidget(self.exam_date_label)

        examPodLayout.addWidget(calIcon)
        examPodLayout.addLayout(examTextLayout)
        summaryLayout.addWidget(self.examPod, 3)

        # --- Card 2: Category Metric Card ---
        self.catCard = QFrame()
        self.catCard.setObjectName("card_metric")
        catPodLayout = QHBoxLayout(self.catCard)
        catPodLayout.setContentsMargins(14, 10, 14, 10)
        catPodLayout.setSpacing(12)

        catIconBox = QLabel("📁")
        catIconBox.setFont(QFont("Segoe UI Emoji", 15))
        catIconBox.setAlignment(Qt.AlignCenter)
        catIconBox.setFixedSize(36, 36)
        catIconBox.setStyleSheet("background-color: #F1F5F9; border-radius: 8px;")

        catTextLayout = QVBoxLayout()
        catTextLayout.setSpacing(2)
        catHeaderLbl = QLabel("Category")
        catHeaderLbl.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.top_category_label = QLabel("All Categories")
        self.top_category_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        catTextLayout.addWidget(catHeaderLbl)
        catTextLayout.addWidget(self.top_category_label)
        catPodLayout.addWidget(catIconBox)
        catPodLayout.addLayout(catTextLayout)
        summaryLayout.addWidget(self.catCard, 2)

        # --- Card 3: Total Questions Metric Card ---
        self.totalCard = QFrame()
        self.totalCard.setObjectName("card_metric")
        totPodLayout = QHBoxLayout(self.totalCard)
        totPodLayout.setContentsMargins(14, 10, 14, 10)
        totPodLayout.setSpacing(12)

        totIconBox = QLabel("📄")
        totIconBox.setFont(QFont("Segoe UI Emoji", 15))
        totIconBox.setAlignment(Qt.AlignCenter)
        totIconBox.setFixedSize(36, 36)
        totIconBox.setStyleSheet("background-color: #F1F5F9; border-radius: 8px;")

        totTextLayout = QVBoxLayout()
        totTextLayout.setSpacing(2)
        totHeaderLbl = QLabel("Total Questions")
        totHeaderLbl.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.total_questions_label = QLabel("0")
        self.total_questions_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        totTextLayout.addWidget(totHeaderLbl)
        totTextLayout.addWidget(self.total_questions_label)
        totPodLayout.addWidget(totIconBox)
        totPodLayout.addLayout(totTextLayout)
        summaryLayout.addWidget(self.totalCard, 2)

        # --- Card 4: Available Questions Metric Card ---
        self.availCard = QFrame()
        self.availCard.setObjectName("card_metric")
        availPodLayout = QHBoxLayout(self.availCard)
        availPodLayout.setContentsMargins(14, 10, 14, 10)
        availPodLayout.setSpacing(12)

        availIconBox = QLabel("📚")
        availIconBox.setFont(QFont("Segoe UI Emoji", 15))
        availIconBox.setAlignment(Qt.AlignCenter)
        availIconBox.setFixedSize(36, 36)
        availIconBox.setStyleSheet("background-color: #DCFCE7; border-radius: 8px;")

        availTextLayout = QVBoxLayout()
        availTextLayout.setSpacing(2)
        availHeaderLbl = QLabel("Available")
        availHeaderLbl.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.available_label = QLabel("0")
        self.available_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        availTextLayout.addWidget(availHeaderLbl)
        availTextLayout.addWidget(self.available_label)
        availPodLayout.addWidget(availIconBox)
        availPodLayout.addLayout(availTextLayout)
        summaryLayout.addWidget(self.availCard, 2)

        # --- Action Button: View Exam Details ---
        self.viewExamDetailsBtn = QPushButton("👁  View Exam Details")
        self.viewExamDetailsBtn.setObjectName("secondaryBtn")
        self.viewExamDetailsBtn.setCursor(Qt.PointingHandCursor)
        self.viewExamDetailsBtn.setMinimumHeight(44)
        self.viewExamDetailsBtn.clicked.connect(self.show_exam_details)
        summaryLayout.addWidget(self.viewExamDetailsBtn, 2)

        main_layout.addWidget(self.summaryCard)

        # ======================================================
        # 3. BOX 1: AUTOMATED QUESTION GENERATION ENGINE CARD (QFrame#card_auto_generation)
        # ======================================================

        self.card_auto_generation = QFrame()
        self.card_auto_generation.setObjectName("card_auto_generation")
        self.genCard = self.card_auto_generation  # Backward-compatible alias
        genCardLayout = QVBoxLayout(self.card_auto_generation)
        genCardLayout.setContentsMargins(20, 18, 20, 18)
        genCardLayout.setSpacing(14)

        # Header with blue badge icon
        genHeaderRow = QHBoxLayout()
        genHeaderRow.setSpacing(10)

        genIconBadge = QLabel("✦")
        genIconBadge.setFont(QFont("Segoe UI", 12, QFont.Bold))
        genIconBadge.setAlignment(Qt.AlignCenter)
        genIconBadge.setFixedSize(28, 28)
        genIconBadge.setStyleSheet("""
            background-color: #2563EB;
            color: #FFFFFF;
            border-radius: 6px;
            font-weight: 900;
        """)

        genTitleLayout = QVBoxLayout()
        genTitleLayout.setSpacing(1)

        genHeader = QLabel("✦  Automated Question Generation Engine")
        genHeader.setObjectName("sectionHeader")
        genHeader.setFont(QFont("Segoe UI", 13, QFont.Bold))
        genHeader.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")

        genSubheader = QLabel("Randomly synthesize and balance questions across categories for this examination.")
        genSubheader.setStyleSheet("color: #64748B; font-size: 11px;")

        genTitleLayout.addWidget(genHeader)
        genTitleLayout.addWidget(genSubheader)

        genHeaderRow.addWidget(genIconBadge)
        genHeaderRow.addLayout(genTitleLayout)
        genHeaderRow.addStretch()
        genCardLayout.addLayout(genHeaderRow)

        # Controls Row
        genRow = QHBoxLayout()
        genRow.setSpacing(16)

        catLbl = QLabel("Category:")
        catLbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        catLbl.setStyleSheet("color: #475569; font-weight: 700;")

        self.category_combo = QComboBox()
        self.category_combo.setView(QListView())
        self.category_combo.setMinimumHeight(38)
        self.category_combo.setCursor(Qt.PointingHandCursor)
        self.category_combo.currentIndexChanged.connect(self.category_changed)

        countLbl = QLabel("Questions Count:")
        countLbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        countLbl.setStyleSheet("color: #475569; font-weight: 700;")

        self.number_spin = QSpinBox()
        self.number_spin.setMinimum(1)
        self.number_spin.setMaximum(1000)
        self.number_spin.setValue(10)
        self.number_spin.setMinimumHeight(38)
        self.number_spin.setMinimumWidth(100)

        self.auto_select_button = QPushButton("✦  Auto Select Questions")
        self.auto_select_button.setObjectName("primaryAutoSelectBtn")
        self.auto_select_button.setCursor(Qt.PointingHandCursor)
        self.auto_select_button.setMinimumHeight(38)
        self.auto_select_button.clicked.connect(self.auto_select_questions)

        # Aliases for backwards compatibility with any callers or tests
        self.questions_count_spin = self.number_spin
        self.count_spin = self.number_spin
        self.autoSelectToggleBtn = self.auto_select_button
        self.auto_select_btn = self.auto_select_button

        genRow.addWidget(catLbl)
        genRow.addWidget(self.category_combo, 3)
        genRow.addWidget(countLbl)
        genRow.addWidget(self.number_spin, 1)
        genRow.addWidget(self.auto_select_button, 2)

        genCardLayout.addLayout(genRow)
        main_layout.addWidget(self.card_auto_generation)

        # ======================================================
        # 4. BOX 2: AVAILABLE QUESTION BANK CARD (QFrame#card_available_questions)
        # ======================================================

        self.card_available_questions = QFrame()
        self.card_available_questions.setObjectName("card_available_questions")
        self.availCard = self.card_available_questions  # Backward-compatible alias
        availCardLayout = QVBoxLayout(self.card_available_questions)
        availCardLayout.setContentsMargins(18, 16, 18, 16)
        availCardLayout.setSpacing(12)

        availHeaderRow = QHBoxLayout()
        availHeaderRow.setSpacing(12)

        availTitle = QLabel("🗄️  Available Question Bank")
        availTitle.setObjectName("sectionHeader")
        availTitle.setFont(QFont("Segoe UI", 12, QFont.Bold))
        availTitle.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")

        self.search_available = QLineEdit()
        self.search_available.setObjectName("searchAvailableInput")
        self.search_available.setPlaceholderText("🔍 Search questions by prompt or category...")
        self.search_available.setMinimumHeight(38)
        self.search_available.setMinimumWidth(300)
        self.search_available.textChanged.connect(self.filter_available_questions)

        availHeaderRow.addWidget(availTitle)
        availHeaderRow.addStretch()
        availHeaderRow.addWidget(self.search_available)
        availCardLayout.addLayout(availHeaderRow)

        # Table
        self.available_table = QTableWidget()
        self.available_table.setObjectName("availableQuestionsTable")
        self.available_table.setColumnCount(6)
        self.available_table.setHorizontalHeaderLabels([
            "ID",
            "QUESTION",
            "CATEGORY",
            "MARKS",
            "NEGATIVE MARKS",
            "ACTION"
        ])

        self.available_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.available_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.available_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.available_table.setAlternatingRowColors(True)
        self.available_table.setShowGrid(False)
        self.available_table.verticalHeader().setVisible(False)
        self.available_table.verticalHeader().setDefaultSectionSize(44)
        self.available_table.setMinimumHeight(200)

        avail_header = self.available_table.horizontalHeader()
        avail_header.setSectionResizeMode(QHeaderView.Stretch)
        avail_header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.available_table.setColumnWidth(0, 70)
        avail_header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.available_table.setColumnWidth(2, 150)
        avail_header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.available_table.setColumnWidth(3, 90)
        avail_header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.available_table.setColumnWidth(4, 130)
        avail_header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.available_table.setColumnWidth(5, 100)

        availCardLayout.addWidget(self.available_table)

        # Bottom Action Bar
        availBottomRow = QHBoxLayout()
        availBottomRow.setSpacing(10)

        self.assign_button = QPushButton("➕  Assign Selected Questions")
        self.assign_button.setObjectName("primaryAssignBtn")
        self.assign_button.setCursor(Qt.PointingHandCursor)
        self.assign_button.setMinimumHeight(38)
        self.assign_button.clicked.connect(self.assign_selected_questions)

        self.refresh_button = QPushButton("↻  Refresh Bank")
        self.refresh_button.setObjectName("neutralRefreshBtn")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setMinimumHeight(38)
        self.refresh_button.clicked.connect(self.refresh_page)

        # Aliases
        self.available_questions_table = self.available_table
        self.add_btn = self.assign_button
        self.assign_btn = self.assign_button
        self.refresh_btn = self.refresh_button

        availBottomRow.addWidget(self.assign_button)
        availBottomRow.addStretch()
        availBottomRow.addWidget(self.refresh_button)

        availCardLayout.addLayout(availBottomRow)
        main_layout.addWidget(self.card_available_questions)

        # ======================================================
        # 5. BOX 3: ASSIGNED EXAMINATION QUESTIONS CARD (QFrame#card_assigned_questions)
        # ======================================================

        self.card_assigned_questions = QFrame()
        self.card_assigned_questions.setObjectName("card_assigned_questions")
        self.assignedCard = self.card_assigned_questions  # Backward-compatible alias
        assignedCardLayout = QVBoxLayout(self.card_assigned_questions)
        assignedCardLayout.setContentsMargins(18, 16, 18, 16)
        assignedCardLayout.setSpacing(12)

        assignedHeaderRow = QHBoxLayout()
        assignedHeaderRow.setSpacing(12)

        assignedTitle = QLabel("🔗  Assigned Examination Questions")
        assignedTitle.setObjectName("sectionHeader")
        assignedTitle.setFont(QFont("Segoe UI", 12, QFont.Bold))
        assignedTitle.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")

        self.assigned_count_label = QLabel("Assigned: 0")
        self.assigned_count_label.setObjectName("assignedCountBadge")
        self.assigned_count_label.setStyleSheet("""
            QLabel#assignedCountBadge {
                background-color: #EEF2FF;
                color: #4F46E5;
                border: 1px solid #C7D2FE;
                border-radius: 12px;
                padding: 4px 14px;
                font-weight: 700;
                font-size: 11px;
            }
        """)

        assignedHeaderRow.addWidget(assignedTitle)
        assignedHeaderRow.addStretch()
        assignedHeaderRow.addWidget(self.assigned_count_label)
        assignedCardLayout.addLayout(assignedHeaderRow)

        # Assigned Table
        self.assigned_table = QTableWidget()
        self.assigned_table.setObjectName("assignedQuestionsTable")
        self.assigned_table.setColumnCount(6)
        self.assigned_table.setHorizontalHeaderLabels([
            "ORDER",
            "QUESTION ID",
            "QUESTION",
            "CATEGORY",
            "MARKS",
            "ACTION"
        ])

        self.assigned_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.assigned_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.assigned_table.setAlternatingRowColors(True)
        self.assigned_table.setShowGrid(False)
        self.assigned_table.verticalHeader().setVisible(False)
        self.assigned_table.verticalHeader().setDefaultSectionSize(44)
        self.assigned_table.setMinimumHeight(200)

        assigned_header = self.assigned_table.horizontalHeader()
        assigned_header.setSectionResizeMode(QHeaderView.Stretch)
        assigned_header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(0, 80)
        assigned_header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(1, 110)
        assigned_header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(3, 150)
        assigned_header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(4, 90)
        assigned_header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(5, 110)

        assignedCardLayout.addWidget(self.assigned_table)

        # Assigned Bottom Action Bar
        assignedBottomRow = QHBoxLayout()
        assignedBottomRow.addStretch()

        self.clear_all_button = QPushButton("🗑  Remove All Assigned Questions")
        self.clear_all_button.setObjectName("dangerRemoveAllBtn")
        self.clear_all_button.setCursor(Qt.PointingHandCursor)
        self.clear_all_button.setMinimumHeight(38)
        self.clear_all_button.clicked.connect(self.remove_all_questions)

        # Aliases
        self.assigned_questions_table = self.assigned_table
        self.remove_btn = self.clear_all_button
        self.remove_all_btn = self.clear_all_button

        assignedBottomRow.addWidget(self.clear_all_button)
        assignedCardLayout.addLayout(assignedBottomRow)
        main_layout.addWidget(self.card_assigned_questions)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)
        self._apply_theme_colors()

    # ==========================================================
    # THEME REACTIVITY
    # ==========================================================

    def _on_theme_changed(self, theme_name):
        self._apply_theme_colors()

    def _apply_theme_colors(self):
        p = get_theme_palette()
        is_dark = p.get("name") == "dark"

        if is_dark:
            card_bg = "#1E293B"
            card_border = "#334155"
            text_main = "#F8FAFC"
            text_muted = "#94A3B8"
            input_bg = "#0F172A"
            input_border = "#334155"
            focus_color = "#6366F1"
            combo_view_bg = "#1E293B"
            combo_view_select = "#312E81"
            table_bg = "#1E293B"
            table_alt_bg = "#162032"
            table_hover = "#243248"
            table_select_bg = "#312E81"
            table_select_fg = "#FFFFFF"
            table_header_bg = "#0F172A"
            table_header_fg = "#94A3B8"
            table_border = "#334155"
            table_line = "#273549"

            self.examPod.setStyleSheet("""
                QFrame#examPod {
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 4px;
                }
            """)
            self.exam_combo.setStyleSheet("""
                QComboBox {
                    font-weight: 700;
                    font-size: 13px;
                    color: #F8FAFC;
                    background: transparent;
                    border: none;
                    padding-right: 20px;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 16px;
                }
                QComboBox QAbstractItemView, QComboBox QListView {
                    background-color: #1E293B;
                    color: #F8FAFC;
                    selection-background-color: #312E81;
                    selection-color: #FFFFFF;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 4px;
                    outline: none;
                }
                QComboBox QAbstractItemView::item, QComboBox QListView::item {
                    padding: 6px 10px;
                    color: #F8FAFC;
                    background-color: #1E293B;
                }
                QComboBox QAbstractItemView::item:hover, QComboBox QListView::item:hover,
                QComboBox QAbstractItemView::item:selected, QComboBox QListView::item:selected {
                    background-color: #312E81;
                    color: #FFFFFF;
                }
            """)
            metric_card_style = """
                QFrame#card_metric {
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 4px;
                }
                QFrame#card_metric:hover {
                    border: 1px solid #4F46E5;
                }
            """
            self.catCard.setStyleSheet(metric_card_style)
            self.totalCard.setStyleSheet(metric_card_style)
            self.availCard.setStyleSheet(metric_card_style)

            self.top_category_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.total_questions_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.available_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #34D399; background: transparent; border: none;")

            self.viewExamDetailsBtn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #818CF8;
                    border: 1px solid #4F46E5;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1E1B4B;
                    border-color: #6366F1;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #312E81;
                }
            """)

            # Buttons in dark
            self.auto_select_button.setStyleSheet("""
                QPushButton#primaryAutoSelectBtn {
                    background-color: #4F46E5;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#primaryAutoSelectBtn:hover {
                    background-color: #4338CA;
                }
                QPushButton#primaryAutoSelectBtn:pressed {
                    background-color: #3730A3;
                }
            """)

            self.assign_button.setStyleSheet("""
                QPushButton#primaryAssignBtn {
                    background-color: #064E3B;
                    color: #34D399;
                    border: 1px solid #059669;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton#primaryAssignBtn:hover {
                    background-color: #047857;
                    color: #FFFFFF;
                }
            """)

            self.refresh_button.setStyleSheet("""
                QPushButton#neutralRefreshBtn {
                    background-color: #1E293B;
                    color: #CBD5E1;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton#neutralRefreshBtn:hover {
                    background-color: #334155;
                    color: #FFFFFF;
                }
            """)

            self.clear_all_button.setStyleSheet("""
                QPushButton#dangerRemoveAllBtn {
                    background-color: #881337;
                    color: #FDA4AF;
                    border: 1px solid #E11D48;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton#dangerRemoveAllBtn:hover {
                    background-color: #BE123C;
                    color: #FFFFFF;
                }
            """)

            self.assigned_count_label.setStyleSheet("""
                QLabel#assignedCountBadge {
                    background-color: #1E1B4B;
                    color: #A5B4FC;
                    border: 1px solid #4F46E5;
                    border-radius: 12px;
                    padding: 4px 14px;
                    font-weight: 700;
                    font-size: 11px;
                }
            """)

        else:
            card_bg = "#FFFFFF"
            card_border = "#E2E8F0"
            text_main = "#0F172A"
            text_muted = "#64748B"
            input_bg = "#FFFFFF"
            input_border = "#CBD5E1"
            focus_color = "#2563EB"
            combo_view_bg = "#FFFFFF"
            combo_view_select = "#EFF6FF"
            table_bg = "#FFFFFF"
            table_alt_bg = "#F8FAFC"
            table_hover = "#EFF6FF"
            table_select_bg = "#DBEAFE"
            table_select_fg = "#1E3A8A"
            table_header_bg = "#F8FAFC"
            table_header_fg = "#475569"
            table_border = "#E2E8F0"
            table_line = "#F1F5F9"

            self.examPod.setStyleSheet("""
                QFrame#examPod {
                    background-color: #EEF2FF;
                    border: 1px solid #DDE7FF;
                    border-radius: 10px;
                    padding: 4px;
                }
            """)
            self.exam_combo.setStyleSheet("""
                QComboBox {
                    font-weight: 700;
                    font-size: 13px;
                    color: #1E293B;
                    background: transparent;
                    border: none;
                    padding-right: 20px;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 16px;
                }
                QComboBox QAbstractItemView, QComboBox QListView {
                    background-color: #FFFFFF;
                    color: #0F172A;
                    selection-background-color: #EFF6FF;
                    selection-color: #2563EB;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 4px;
                    outline: none;
                }
                QComboBox QAbstractItemView::item, QComboBox QListView::item {
                    padding: 6px 10px;
                    color: #0F172A;
                    background-color: #FFFFFF;
                }
                QComboBox QAbstractItemView::item:hover, QComboBox QListView::item:hover,
                QComboBox QAbstractItemView::item:selected, QComboBox QListView::item:selected {
                    background-color: #EFF6FF;
                    color: #2563EB;
                }
            """)
            metric_card_style = """
                QFrame#card_metric {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                    padding: 4px;
                }
                QFrame#card_metric:hover {
                    border: 1px solid #CBD5E1;
                }
            """
            self.catCard.setStyleSheet(metric_card_style)
            self.totalCard.setStyleSheet(metric_card_style)
            self.availCard.setStyleSheet(metric_card_style)

            self.top_category_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A; background: transparent; border: none;")
            self.total_questions_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A; background: transparent; border: none;")
            self.available_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #15803D; background: transparent; border: none;")

            self.viewExamDetailsBtn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #2563EB;
                    border: 1px solid #BFDBFE;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #EFF6FF;
                    border-color: #2563EB;
                }
                QPushButton:pressed {
                    background-color: #DBEAFE;
                }
            """)

            # Buttons in light
            self.auto_select_button.setStyleSheet("""
                QPushButton#primaryAutoSelectBtn {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton#primaryAutoSelectBtn:hover {
                    background-color: #1D4ED8;
                }
                QPushButton#primaryAutoSelectBtn:pressed {
                    background-color: #1E40AF;
                }
            """)

            self.assign_button.setStyleSheet("""
                QPushButton#primaryAssignBtn {
                    background-color: #ECFDF5;
                    color: #059669;
                    border: 1px solid #A7F3D0;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton#primaryAssignBtn:hover {
                    background-color: #D1FAE5;
                    border-color: #059669;
                }
            """)

            self.refresh_button.setStyleSheet("""
                QPushButton#neutralRefreshBtn {
                    background-color: #F8FAFC;
                    color: #475569;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton#neutralRefreshBtn:hover {
                    background-color: #F1F5F9;
                    color: #0F172A;
                    border-color: #94A3B8;
                }
            """)

            self.clear_all_button.setStyleSheet("""
                QPushButton#dangerRemoveAllBtn {
                    background-color: #FEF2F2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton#dangerRemoveAllBtn:hover {
                    background-color: #FEE2E2;
                    border-color: #DC2626;
                }
            """)

            self.assigned_count_label.setStyleSheet("""
                QLabel#assignedCountBadge {
                    background-color: #EEF2FF;
                    color: #4F46E5;
                    border: 1px solid #C7D2FE;
                    border-radius: 12px;
                    padding: 4px 14px;
                    font-weight: 700;
                    font-size: 11px;
                }
            """)

        # Style card containers
        card_qss = f"""
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 12px;
        """
        self.headerCard.setStyleSheet(f"QFrame#card_header {{ {card_qss} }}")
        self.card_auto_generation.setStyleSheet(f"QFrame#card_auto_generation {{ {card_qss} }}")
        self.card_available_questions.setStyleSheet(f"QFrame#card_available_questions {{ {card_qss} }}")
        self.card_assigned_questions.setStyleSheet(f"QFrame#card_assigned_questions {{ {card_qss} }}")

        # Category combo styling
        self.category_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {input_bg};
                color: {text_main};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QComboBox:focus {{
                border-color: {focus_color};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: 1px solid {card_border};
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: {card_bg};
            }}
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {text_muted};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView, QComboBox QListView {{
                background-color: {combo_view_bg};
                color: {text_main};
                selection-background-color: {combo_view_select};
                selection-color: {focus_color};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item, QComboBox QListView::item {{
                padding: 6px 10px;
                color: {text_main};
                background-color: {combo_view_bg};
                border-radius: 4px;
                min-height: 24px;
            }}
            QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected,
            QComboBox QListView::item:hover, QComboBox QListView::item:selected {{
                background-color: {combo_view_select};
                color: {focus_color};
            }}
        """)

        # Spinbox styling
        self.number_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {input_bg};
                color: {text_main};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QSpinBox:focus {{
                border-color: {focus_color};
            }}
        """)

        # Search input styling
        self.search_available.setStyleSheet(f"""
            QLineEdit#searchAvailableInput {{
                border-radius: 8px;
                padding: 6px 14px;
                border: 1px solid {input_border};
                background-color: {input_bg};
                color: {text_main};
                font-size: 12px;
            }}
            QLineEdit#searchAvailableInput:focus {{
                border-color: {focus_color};
            }}
        """)

        # Table styling
        table_qss = f"""
            QTableWidget {{
                background-color: {table_bg};
                alternate-background-color: {table_alt_bg};
                color: {text_main};
                border: 1px solid {table_border};
                border-radius: 10px;
                gridline-color: transparent;
                selection-background-color: {table_select_bg};
                selection-color: {table_select_fg};
                font-size: 13px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {table_line};
            }}
            QTableWidget::item:selected {{
                background-color: {table_select_bg};
                color: {table_select_fg};
            }}
            QTableWidget::item:hover {{
                background-color: {table_hover};
            }}
            QHeaderView::section {{
                background-color: {table_header_bg};
                color: {table_header_fg};
                padding: 10px 14px;
                border: none;
                border-bottom: 1px solid {table_border};
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """
        self.available_table.setStyleSheet(table_qss)
        self.assigned_table.setStyleSheet(table_qss)

    # ==========================================================
    # LOAD EXAMINATIONS
    # ==========================================================

    def load_exams(self):

        self.exam_combo.blockSignals(True)
        self.exam_combo.clear()

        try:
            exams = ExamModel.get_all_exams()
            self._all_exams_cache = exams or []

            for exam in self._all_exams_cache:
                self.exam_combo.addItem(
                    f"{exam['exam_name']} | {exam['subject_code']}",
                    exam["id"]
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load examinations:\n\n{e}"
            )

        self.exam_combo.blockSignals(False)

        if self.exam_combo.count() > 0:
            self.exam_combo.setCurrentIndex(0)
            self.selected_exam_id = self.exam_combo.currentData()
            self._update_exam_details_card()
            self.load_available_questions()
            self.load_assigned_questions()
        else:
            self.selected_exam_id = None
            self.clear_tables()

    def _update_exam_details_card(self):
        if not self._all_exams_cache or self.selected_exam_id is None:
            self.exam_date_label.setText("No exam selected")
            self.total_questions_label.setText("0")
            return

        for ex in self._all_exams_cache:
            if ex["id"] == self.selected_exam_id:
                date_str = str(ex["exam_date"] if "exam_date" in ex.keys() else "N/A")
                self.exam_date_label.setText(f"Date: {date_str}")
                break

        assigned_cnt = QuestionModel.get_exam_question_count(self.selected_exam_id)
        self.total_questions_label.setText(str(assigned_cnt))

    # ==========================================================
    # LOAD CATEGORIES
    # ==========================================================

    def load_categories(self):

        self.category_combo.blockSignals(True)
        self.category_combo.clear()

        self.category_combo.addItem("All Categories", None)

        try:
            categories = QuestionModel.get_all_categories()
            for category in categories:
                self.category_combo.addItem(
                    category["name"],
                    category["id"]
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load categories:\n\n{e}"
            )

        self.category_combo.blockSignals(False)
        self.top_category_label.setText(self.category_combo.currentText())
        self.update_available_count()

    # ==========================================================
    # EXAM CHANGED
    # ==========================================================

    def exam_changed(self):
        self.selected_exam_id = self.exam_combo.currentData()
        self._update_exam_details_card()
        self.load_available_questions()
        self.load_assigned_questions()

    # ==========================================================
    # CATEGORY CHANGED
    # ==========================================================

    def category_changed(self):
        self.top_category_label.setText(self.category_combo.currentText())
        self.load_available_questions()

    # ==========================================================
    # SEARCH FILTER
    # ==========================================================

    def filter_available_questions(self, query):
        text = (query or "").strip().lower()
        for row in range(self.available_table.rowCount()):
            match = False
            for col in range(5):
                item = self.available_table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.available_table.setRowHidden(row, not match)

    # ==========================================================
    # LOAD AVAILABLE QUESTIONS
    # ==========================================================

    def load_available_questions(self):

        self.available_table.setRowCount(0)

        if self.selected_exam_id is None:
            self.available_label.setText("0")
            return

        category_id = self.category_combo.currentData()

        try:
            questions = QuestionModel.get_unassigned_questions(
                self.selected_exam_id,
                category_id
            )

            self.available_table.setRowCount(len(questions))

            for row, question in enumerate(questions):

                id_item = QTableWidgetItem(str(question["id"]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.available_table.setItem(row, 0, id_item)

                self.available_table.setItem(
                    row,
                    1,
                    QTableWidgetItem(question["question_text"])
                )

                cat_item = QTableWidgetItem(
                    question["category_name"] or "Uncategorized"
                )
                self.available_table.setItem(row, 2, cat_item)

                marks_item = QTableWidgetItem(str(question["marks"]))
                marks_item.setTextAlignment(Qt.AlignCenter)
                self.available_table.setItem(row, 3, marks_item)

                neg_item = QTableWidgetItem(str(question["negative_marks"]))
                neg_item.setTextAlignment(Qt.AlignCenter)
                self.available_table.setItem(row, 4, neg_item)

                # Action button: + Add
                add_btn = QPushButton("+ Add")
                add_btn.setCursor(Qt.PointingHandCursor)
                add_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #2563EB;
                        border: 1px solid #BFDBFE;
                        border-radius: 6px;
                        padding: 3px 10px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #EFF6FF;
                        border-color: #2563EB;
                    }
                """)
                add_btn.clicked.connect(
                    lambda checked, qid=question["id"]: self.assign_single_question(qid)
                )
                self.available_table.setCellWidget(row, 5, add_btn)

            self.available_label.setText(str(len(questions)))

            # Re-apply any existing filter
            curr_filter = self.search_available.text()
            if curr_filter:
                self.filter_available_questions(curr_filter)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load available questions:\n\n{e}"
            )
            self.available_label.setText("0")

    # ==========================================================
    # ASSIGN SINGLE QUESTION
    # ==========================================================

    def assign_single_question(self, question_id):
        if self.selected_exam_id is None:
            QMessageBox.warning(self, "No Exam", "Please select an examination first.")
            return

        assigned_count = QuestionModel.get_exam_question_count(self.selected_exam_id)
        success = QuestionModel.assign_question_to_exam(
            self.selected_exam_id,
            question_id,
            assigned_count + 1
        )
        if success:
            self.load_available_questions()
            self.load_assigned_questions()
            self._update_exam_details_card()
        else:
            QMessageBox.warning(self, "Assignment Failed", "Unable to assign question.")

    # ==========================================================
    # LOAD ASSIGNED QUESTIONS
    # ==========================================================

    def load_assigned_questions(self):

        self.assigned_table.setRowCount(0)

        if self.selected_exam_id is None:
            self.assigned_count_label.setText("Assigned: 0")
            return

        try:
            questions = QuestionModel.get_questions_for_exam(
                self.selected_exam_id
            )

            self.assigned_table.setRowCount(len(questions))

            for row, question in enumerate(questions):

                order_item = QTableWidgetItem(str(question["display_order"]))
                order_item.setTextAlignment(Qt.AlignCenter)
                self.assigned_table.setItem(row, 0, order_item)

                qid_item = QTableWidgetItem(str(question["question_id"]))
                qid_item.setTextAlignment(Qt.AlignCenter)
                self.assigned_table.setItem(row, 1, qid_item)

                self.assigned_table.setItem(
                    row,
                    2,
                    QTableWidgetItem(question["question_text"])
                )

                self.assigned_table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        question["category_name"] or "Uncategorized"
                    )
                )

                marks_item = QTableWidgetItem(str(question["marks"]))
                marks_item.setTextAlignment(Qt.AlignCenter)
                self.assigned_table.setItem(row, 4, marks_item)

                # Remove Button
                remove_button = QPushButton("🗑  Remove")
                remove_button.setCursor(Qt.PointingHandCursor)
                remove_button.setStyleSheet("""
                    QPushButton {
                        background-color: #FEF2F2;
                        color: #DC2626;
                        border: 1px solid #FECACA;
                        border-radius: 6px;
                        padding: 3px 10px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #FEE2E2;
                        border-color: #DC2626;
                    }
                """)

                remove_button.clicked.connect(
                    lambda checked,
                    eqid=question["exam_question_id"]:
                    self.remove_question(eqid)
                )

                self.assigned_table.setCellWidget(
                    row,
                    5,
                    remove_button
                )

            self.assigned_count_label.setText(
                f"Assigned: {len(questions)}"
            )
            self._update_exam_details_card()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load assigned questions:\n\n{e}"
            )

    # ==========================================================
    # ASSIGN SELECTED QUESTIONS
    # ==========================================================

    def assign_selected_questions(self):

        if self.selected_exam_id is None:
            QMessageBox.warning(
                self,
                "No Exam",
                "Please select an examination first."
            )
            return

        selected_rows = (
            self.available_table.selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Questions Selected",
                "Please select one or more questions from the table."
            )
            return

        assigned_count = QuestionModel.get_exam_question_count(
            self.selected_exam_id
        )

        success_count = 0

        for row_index in selected_rows:
            row = row_index.row()
            question_item = self.available_table.item(row, 0)
            if question_item is None:
                continue

            question_id = int(question_item.text())
            display_order = assigned_count + success_count + 1

            success = QuestionModel.assign_question_to_exam(
                self.selected_exam_id,
                question_id,
                display_order
            )

            if success:
                success_count += 1

        if success_count > 0:
            QMessageBox.information(
                self,
                "Questions Assigned",
                f"{success_count} question(s) assigned successfully."
            )
            self.load_available_questions()
            self.load_assigned_questions()
            self._update_exam_details_card()
        else:
            QMessageBox.warning(
                self,
                "Assignment Failed",
                "No questions were assigned."
            )

    # ==========================================================
    # AUTO SELECT QUESTIONS
    # ==========================================================

    def auto_select_questions(self):

        if self.selected_exam_id is None:
            QMessageBox.warning(
                self,
                "No Exam",
                "Please select an examination first."
            )
            return

        category_id = self.category_combo.currentData()
        number_to_select = self.number_spin.value()

        try:
            available_questions = QuestionModel.get_unassigned_questions(
                self.selected_exam_id,
                category_id
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load questions:\n\n{e}"
            )
            return

        available_count = len(available_questions)

        if available_count == 0:
            QMessageBox.warning(
                self,
                "No Questions",
                "There are no unassigned questions in this category."
            )
            return

        if number_to_select > available_count:
            QMessageBox.warning(
                self,
                "Not Enough Questions",
                f"You requested {number_to_select} question(s), but only {available_count} are available in this category."
            )
            return

        selected_questions = random.sample(
            available_questions,
            number_to_select
        )

        assigned_count = QuestionModel.get_exam_question_count(
            self.selected_exam_id
        )

        success_count = 0

        for index, question in enumerate(selected_questions):
            display_order = assigned_count + index + 1
            success = QuestionModel.assign_question_to_exam(
                self.selected_exam_id,
                question["id"],
                display_order
            )
            if success:
                success_count += 1

        if success_count > 0:
            QMessageBox.information(
                self,
                "Automatic Selection Complete",
                f"{success_count} question(s) were randomly selected and assigned to the examination."
            )
            self.load_available_questions()
            self.load_assigned_questions()
            self._update_exam_details_card()
        else:
            QMessageBox.warning(
                self,
                "Assignment Failed",
                "Unable to automatically assign questions."
            )

    # ==========================================================
    # REMOVE QUESTION
    # ==========================================================

    def remove_question(self, exam_question_id):

        reply = QMessageBox.question(
            self,
            "Remove Question",
            "Remove this question from the examination?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = QuestionModel.remove_question_from_exam(
            exam_question_id
        )

        if success:
            QMessageBox.information(
                self,
                "Removed",
                "Question removed from the examination."
            )
            self.load_available_questions()
            self.load_assigned_questions()
            self._update_exam_details_card()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Unable to remove question."
            )

    # ==========================================================
    # REMOVE ALL QUESTIONS
    # ==========================================================

    def remove_all_questions(self):

        if self.selected_exam_id is None:
            QMessageBox.warning(
                self,
                "No Exam",
                "Please select an examination first."
            )
            return

        count = QuestionModel.get_exam_question_count(
            self.selected_exam_id
        )

        if count == 0:
            QMessageBox.information(
                self,
                "No Questions",
                "There are no questions assigned to this examination."
            )
            return

        reply = QMessageBox.question(
            self,
            "Remove All Questions",
            f"This will remove all {count} assigned questions from this examination.\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = QuestionModel.remove_all_questions_from_exam(
            self.selected_exam_id
        )

        if success:
            QMessageBox.information(
                self,
                "Questions Removed",
                "All questions have been removed from the examination."
            )
            self.load_available_questions()
            self.load_assigned_questions()
            self._update_exam_details_card()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Unable to remove questions."
            )

    # ==========================================================
    # SHOW EXAM DETAILS
    # ==========================================================

    def show_exam_details(self):
        if self.selected_exam_id is None:
            QMessageBox.information(self, "Exam Details", "No active examination selected.")
            return

        exam = ExamModel.get_exam(self.selected_exam_id)
        if not exam:
            QMessageBox.warning(self, "Error", "Exam details not found.")
            return

        assigned_count = QuestionModel.get_exam_question_count(self.selected_exam_id)

        exam_name = exam["exam_name"] if "exam_name" in exam.keys() else "N/A"
        sub_name = exam["subject_name"] if "subject_name" in exam.keys() else "N/A"
        sub_code = exam["subject_code"] if "subject_code" in exam.keys() else "N/A"
        dept = exam["department"] if "department" in exam.keys() else "N/A"
        sem = exam["semester"] if "semester" in exam.keys() else "N/A"
        date_val = exam["exam_date"] if "exam_date" in exam.keys() else "N/A"
        st = exam["start_time"] if "start_time" in exam.keys() else "N/A"
        et = exam["end_time"] if "end_time" in exam.keys() else "N/A"
        hall = exam["hall"] if "hall" in exam.keys() else "N/A"
        status = exam["exam_status"] if "exam_status" in exam.keys() else "Scheduled"

        info = f"""
<b>Exam Name:</b> {exam_name}<br>
<b>Subject:</b> {sub_name} ({sub_code})<br>
<b>Department / Semester:</b> {dept} - Sem {sem}<br>
<b>Date & Time:</b> {date_val} ({st} - {et})<br>
<b>Hall:</b> {hall}<br>
<b>Status:</b> {status}<br>
<b>Assigned Questions:</b> {assigned_count}
"""
        QMessageBox.information(self, "Active Examination Overview", info)

    # ==========================================================
    # UPDATE AVAILABLE COUNT
    # ==========================================================

    def update_available_count(self):
        self.load_available_questions()

    # ==========================================================
    # REFRESH PAGE
    # ==========================================================

    def refresh_page(self):

        current_exam_id = self.selected_exam_id
        self.load_exams()
        self.load_categories()

        if current_exam_id is not None:
            index = self.exam_combo.findData(current_exam_id)
            if index >= 0:
                self.exam_combo.setCurrentIndex(index)
                self.selected_exam_id = current_exam_id

        self.load_available_questions()
        self.load_assigned_questions()
        self._update_exam_details_card()

    # ==========================================================
    # CLEAR TABLES
    # ==========================================================

    def clear_tables(self):
        self.available_table.setRowCount(0)
        self.assigned_table.setRowCount(0)
        self.available_label.setText("0")
        self.assigned_count_label.setText("Assigned: 0")
        self.total_questions_label.setText("0")
        self.exam_date_label.setText("No exam selected")


# ==============================================================
# DIRECT TEST
# ==============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExamQuestionsPage()
    window.setWindowTitle("Exam Question Management")
    window.resize(1400, 850)
    window.show()
    sys.exit(app.exec_())
