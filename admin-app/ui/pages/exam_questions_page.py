import sys
import random

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
        container.setObjectName("pageWidget")

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(28, 22, 28, 24)
        main_layout.setSpacing(16)

        # ======================================================
        # 1. HEADER CARD (Blue square icon + titles)
        # ======================================================

        headerCard = QFrame()
        headerCard.setObjectName("headerCard")
        headerLayout = QHBoxLayout(headerCard)
        headerLayout.setContentsMargins(18, 14, 18, 14)
        headerLayout.setSpacing(16)

        # Blue square badge icon
        self.headerIconBox = QLabel("📋")
        self.headerIconBox.setFixedSize(44, 44)
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

        main_layout.addWidget(headerCard)

        # ======================================================
        # 2. TOP SUMMARY / CONTROL BAR (Structured Metric Cards)
        # ======================================================

        self.summaryCard = QFrame()
        self.summaryCard.setObjectName("summaryCard")
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
        # 3. CARD: AUTOMATED QUESTION GENERATION ENGINE
        # ======================================================

        genCard = QFrame()
        genCard.setObjectName("card")
        genCardLayout = QVBoxLayout(genCard)
        genCardLayout.setContentsMargins(20, 18, 20, 18)
        genCardLayout.setSpacing(14)

        genHeader = QLabel("✦  Automated Question Generation Engine")
        genHeader.setObjectName("sectionHeader")
        genHeader.setFont(QFont("Segoe UI", 13, QFont.Bold))
        genCardLayout.addWidget(genHeader)

        genRow = QHBoxLayout()
        genRow.setSpacing(16)

        catLbl = QLabel("Category")
        catLbl.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.category_combo = QComboBox()
        self.category_combo.setView(QListView())
        self.category_combo.setMinimumHeight(40)
        self.category_combo.currentIndexChanged.connect(self.category_changed)

        countLbl = QLabel("Questions Count")
        countLbl.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.number_spin = QSpinBox()
        self.number_spin.setMinimum(1)
        self.number_spin.setMaximum(1000)
        self.number_spin.setValue(10)
        self.number_spin.setMinimumHeight(40)
        self.number_spin.setMinimumWidth(100)

        self.auto_select_button = QPushButton("✦  Auto Select Questions")
        self.auto_select_button.setCursor(Qt.PointingHandCursor)
        self.auto_select_button.setMinimumHeight(40)
        self.auto_select_button.clicked.connect(self.auto_select_questions)

        # Aliases for backwards compatibility with any callers or tests
        self.autoSelectToggleBtn = self.auto_select_button
        self.auto_select_btn = self.auto_select_button

        genRow.addWidget(catLbl)
        genRow.addWidget(self.category_combo, 3)
        genRow.addWidget(countLbl)
        genRow.addWidget(self.number_spin, 1)
        genRow.addWidget(self.auto_select_button, 2)

        genCardLayout.addLayout(genRow)
        main_layout.addWidget(genCard)

        # ======================================================
        # 4. CARD: AVAILABLE QUESTION BANK
        # ======================================================

        availCard = QFrame()
        availCard.setObjectName("card")
        availCardLayout = QVBoxLayout(availCard)
        availCardLayout.setContentsMargins(18, 16, 18, 16)
        availCardLayout.setSpacing(12)

        availHeaderRow = QHBoxLayout()
        availTitle = QLabel("🗄  Available Question Bank")
        availTitle.setObjectName("sectionHeader")
        availTitle.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.search_available = QLineEdit()
        self.search_available.setPlaceholderText("🔍 Search questions...")
        self.search_available.setMinimumHeight(36)
        self.search_available.setMaximumWidth(280)
        self.search_available.setStyleSheet("""
            QLineEdit {
                border-radius: 8px;
                padding: 4px 12px;
                border: 1px solid #E2E8F0;
                background-color: #FFFFFF;
                color: #0F172A;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2563EB;
            }
        """)
        self.search_available.textChanged.connect(self.filter_available_questions)

        availHeaderRow.addWidget(availTitle)
        availHeaderRow.addStretch()
        availHeaderRow.addWidget(self.search_available)
        availCardLayout.addLayout(availHeaderRow)

        # Table
        self.available_table = QTableWidget()
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
        self.available_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.available_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.available_table.setColumnWidth(0, 70)
        self.available_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.available_table.setColumnWidth(3, 90)
        self.available_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.available_table.setColumnWidth(4, 130)
        self.available_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.available_table.setColumnWidth(5, 95)
        self.available_table.verticalHeader().setVisible(False)
        self.available_table.verticalHeader().setDefaultSectionSize(44)
        self.available_table.setMinimumHeight(190)
        self.available_table.setShowGrid(False)

        availCardLayout.addWidget(self.available_table)

        # Bottom Action Bar
        availBottomRow = QHBoxLayout()

        self.assign_button = QPushButton("➕  Assign Selected Questions")
        self.assign_button.setCursor(Qt.PointingHandCursor)
        self.assign_button.setMinimumHeight(38)
        self.assign_button.setStyleSheet("""
            QPushButton {
                background-color: #ECFDF5;
                color: #059669;
                border: 1px solid #A7F3D0;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D1FAE5;
                border-color: #059669;
            }
        """)
        self.assign_button.clicked.connect(self.assign_selected_questions)

        self.refresh_button = QPushButton("⟳  Refresh Bank")
        self.refresh_button.setObjectName("secondaryBtn")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setMinimumHeight(38)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                border-color: #94A3B8;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_page)

        availBottomRow.addWidget(self.assign_button)
        availBottomRow.addStretch()
        availBottomRow.addWidget(self.refresh_button)

        availCardLayout.addLayout(availBottomRow)
        main_layout.addWidget(availCard)

        # ======================================================
        # 5. CARD: ASSIGNED EXAMINATION QUESTIONS
        # ======================================================

        assignedCard = QFrame()
        assignedCard.setObjectName("card")
        assignedCardLayout = QVBoxLayout(assignedCard)
        assignedCardLayout.setContentsMargins(18, 16, 18, 16)
        assignedCardLayout.setSpacing(12)

        assignedHeaderRow = QHBoxLayout()
        assignedTitle = QLabel("🔗  Assigned Examination Questions")
        assignedTitle.setObjectName("sectionHeader")
        assignedTitle.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.assigned_count_label = QLabel("Assigned: 0")
        self.assigned_count_label.setStyleSheet("""
            QLabel {
                background-color: #EEF2FF;
                color: #4F46E5;
                border: 1px solid #C7D2FE;
                border-radius: 12px;
                padding: 3px 12px;
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
        self.assigned_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.assigned_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(0, 80)
        self.assigned_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(1, 110)
        self.assigned_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(4, 90)
        self.assigned_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.assigned_table.setColumnWidth(5, 105)
        self.assigned_table.verticalHeader().setVisible(False)
        self.assigned_table.verticalHeader().setDefaultSectionSize(44)
        self.assigned_table.setMinimumHeight(190)
        self.assigned_table.setShowGrid(False)

        assignedCardLayout.addWidget(self.assigned_table)

        # Assigned Bottom Action Bar
        assignedBottomRow = QHBoxLayout()
        assignedBottomRow.addStretch()

        self.clear_all_button = QPushButton("🗑  Remove All Assigned Questions")
        self.clear_all_button.setCursor(Qt.PointingHandCursor)
        self.clear_all_button.setMinimumHeight(38)
        self.clear_all_button.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 8px;
                padding: 6px 18px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border-color: #DC2626;
            }
        """)
        self.clear_all_button.clicked.connect(self.remove_all_questions)
        assignedBottomRow.addWidget(self.clear_all_button)

        assignedCardLayout.addLayout(assignedBottomRow)
        main_layout.addWidget(assignedCard)

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

            self.category_combo.setStyleSheet("""
                QComboBox {
                    background-color: #0F172A;
                    color: #F8FAFC;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QComboBox:hover {
                    border-color: #64748B;
                }
                QComboBox:focus {
                    border-color: #6366F1;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 28px;
                    border-left: 1px solid #334155;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    background: #162032;
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
                    padding: 8px 12px;
                    color: #F8FAFC;
                    background-color: #1E293B;
                    border-radius: 4px;
                }
                QComboBox QAbstractItemView::item:hover, QComboBox QListView::item:hover,
                QComboBox QAbstractItemView::item:selected, QComboBox QListView::item:selected {
                    background-color: #312E81;
                    color: #FFFFFF;
                }
            """)

            self.number_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #0F172A;
                    color: #F8FAFC;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                }
                QSpinBox:focus {
                    border-color: #6366F1;
                }
            """)

            self.auto_select_button.setStyleSheet("""
                QPushButton {
                    background-color: #4F46E5;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 18px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #4338CA;
                }
                QPushButton:pressed {
                    background-color: #3730A3;
                }
            """)

            self.search_available.setStyleSheet("""
                QLineEdit {
                    border-radius: 8px;
                    padding: 4px 12px;
                    border: 1px solid #334155;
                    background-color: #1E293B;
                    color: #F8FAFC;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border-color: #6366F1;
                }
            """)
        else:
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

            # Explicit styling for the QComboBox popup list view as instructed:
            self.category_combo.setStyleSheet("""
                QComboBox {
                    background-color: #FFFFFF;
                    color: #0F172A;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QComboBox:hover {
                    border-color: #94A3B8;
                }
                QComboBox:focus {
                    border-color: #2563EB;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 28px;
                    border-left: 1px solid #E2E8F0;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    background: #F8FAFC;
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
                    padding: 8px 12px;
                    color: #0F172A;
                    background-color: #FFFFFF;
                    border-radius: 4px;
                }
                QComboBox QAbstractItemView::item:hover, QComboBox QListView::item:hover,
                QComboBox QAbstractItemView::item:selected, QComboBox QListView::item:selected {
                    background-color: #EFF6FF;
                    color: #2563EB;
                }
            """)

            self.number_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #FFFFFF;
                    color: #0F172A;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                }
                QSpinBox:focus {
                    border-color: #2563EB;
                }
            """)

            self.auto_select_button.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 18px;
                    font-weight: 700;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1D4ED8;
                }
                QPushButton:pressed {
                    background-color: #1E40AF;
                }
            """)

            self.search_available.setStyleSheet("""
                QLineEdit {
                    border-radius: 8px;
                    padding: 4px 12px;
                    border: 1px solid #E2E8F0;
                    background-color: #FFFFFF;
                    color: #0F172A;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border-color: #2563EB;
                }
            """)

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
