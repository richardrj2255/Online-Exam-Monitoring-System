import sys
import os

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
    QGridLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QInputDialog,
    QFrame,
    QScrollArea,
    QListView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.question_model import QuestionModel
from ui.theme_manager import get_theme_palette, register_theme_listener


class QuestionsPage(QWidget):

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def __init__(self):
        super().__init__()

        self.selected_question_id = None
        self._all_questions_cache = []

        self.setup_ui()

        self.load_categories()
        self.load_questions()
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

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(28, 22, 28, 24)
        main_layout.setSpacing(16)

        # ======================================================
        # 1. HEADER SECTION CARD (QFrame#card_header)
        # ======================================================

        self.card_header = QFrame()
        self.card_header.setObjectName("card_header")
        self.headerCard = self.card_header  # Backward-compatible alias
        headerLayout = QHBoxLayout(self.card_header)
        headerLayout.setContentsMargins(20, 16, 20, 16)
        headerLayout.setSpacing(16)

        # Indigo icon container (#2563EB)
        self.headerIconBox = QLabel("❓")
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

        title = QLabel("Question Bank & Assessment Authoring")
        title.setObjectName("pageTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Design, manage, and configure categorized multiple-choice questions with automated grading weights.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setFont(QFont("Segoe UI", 11))

        titleLayout.addWidget(title)
        titleLayout.addWidget(subtitle)

        headerLayout.addWidget(self.headerIconBox)
        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        main_layout.addWidget(self.card_header)

        # ======================================================
        # 2. TOP METRICS SUMMARY CARD (QFrame#card_metrics)
        # ======================================================

        self.card_metrics = QFrame()
        self.card_metrics.setObjectName("card_metrics")
        self.summaryCard = self.card_metrics  # Backward-compatible alias
        metricsLayout = QHBoxLayout(self.card_metrics)
        metricsLayout.setContentsMargins(18, 14, 18, 14)
        metricsLayout.setSpacing(16)

        def create_vertical_separator():
            sep = QFrame()
            sep.setFrameShape(QFrame.VLine)
            sep.setFrameShadow(QFrame.Plain)
            sep.setObjectName("metricSeparator")
            sep.setStyleSheet("background-color: #E2E8F0; width: 1px; max-width: 1px; border: none;")
            return sep

        # --- Pod 1: Active Category ---
        self.catPod = QFrame()
        self.catPod.setObjectName("catPod")
        self.catPod.setStyleSheet("""
            QFrame#catPod {
                background-color: #EEF2FF;
                border: 1px solid #DDE7FF;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        catPodLayout = QHBoxLayout(self.catPod)
        catPodLayout.setContentsMargins(10, 6, 12, 6)
        catPodLayout.setSpacing(10)

        folderIcon = QLabel("📁")
        folderIcon.setFont(QFont("Segoe UI Emoji", 16))
        folderIcon.setAlignment(Qt.AlignCenter)
        folderIcon.setFixedSize(34, 34)
        folderIcon.setStyleSheet("background-color: #DBEAFE; border-radius: 8px;")

        catTextLayout = QVBoxLayout()
        catTextLayout.setSpacing(2)

        catHeaderLbl = QLabel("ACTIVE CATEGORY")
        catHeaderLbl.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748B; letter-spacing: 0.5px; background: transparent; border: none;")

        self.top_category_label = QLabel("All Categories")
        self.top_category_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")

        self.cat_count_label = QLabel("Repository Taxonomy")
        self.cat_count_label.setStyleSheet("font-size: 11px; color: #64748B; background: transparent; border: none;")

        catTextLayout.addWidget(catHeaderLbl)
        catTextLayout.addWidget(self.top_category_label)
        catTextLayout.addWidget(self.cat_count_label)

        catPodLayout.addWidget(folderIcon)
        catPodLayout.addLayout(catTextLayout)
        metricsLayout.addWidget(self.catPod, 3)

        # Divider 1
        metricsLayout.addWidget(create_vertical_separator())

        # --- Pod 2: Total Questions ---
        totPodLayout = QHBoxLayout()
        totPodLayout.setSpacing(10)
        totIcon = QLabel("📄")
        totIcon.setFont(QFont("Segoe UI Emoji", 15))
        totIcon.setAlignment(Qt.AlignCenter)
        totIcon.setFixedSize(32, 32)
        totIcon.setStyleSheet("background-color: #F1F5F9; border-radius: 8px; border: none;")
        totTextLayout = QVBoxLayout()
        totTextLayout.setSpacing(2)
        totHeaderLbl = QLabel("Total Questions")
        totHeaderLbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.total_questions_label = QLabel("0")
        self.total_questions_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
        totTextLayout.addWidget(totHeaderLbl)
        totTextLayout.addWidget(self.total_questions_label)
        totPodLayout.addWidget(totIcon)
        totPodLayout.addLayout(totTextLayout)
        metricsLayout.addLayout(totPodLayout, 2)

        # Divider 2
        metricsLayout.addWidget(create_vertical_separator())

        # --- Pod 3: Categories ---
        categoriesPodLayout = QHBoxLayout()
        categoriesPodLayout.setSpacing(10)
        tagIcon = QLabel("🏷️")
        tagIcon.setFont(QFont("Segoe UI Emoji", 15))
        tagIcon.setAlignment(Qt.AlignCenter)
        tagIcon.setFixedSize(32, 32)
        tagIcon.setStyleSheet("background-color: #F1F5F9; border-radius: 8px; border: none;")
        catCountTextLayout = QVBoxLayout()
        catCountTextLayout.setSpacing(2)
        catCountHeaderLbl = QLabel("Categories")
        catCountHeaderLbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.categories_count_label = QLabel("0")
        self.categories_count_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
        catCountTextLayout.addWidget(catCountHeaderLbl)
        catCountTextLayout.addWidget(self.categories_count_label)
        categoriesPodLayout.addWidget(tagIcon)
        categoriesPodLayout.addLayout(catCountTextLayout)
        metricsLayout.addLayout(categoriesPodLayout, 2)

        # Divider 3
        metricsLayout.addWidget(create_vertical_separator())

        # --- Pod 4: Default Weight ---
        weightPodLayout = QHBoxLayout()
        weightPodLayout.setSpacing(10)
        starIcon = QLabel("⭐")
        starIcon.setFont(QFont("Segoe UI Emoji", 15))
        starIcon.setAlignment(Qt.AlignCenter)
        starIcon.setFixedSize(32, 32)
        starIcon.setStyleSheet("background-color: #FEF3C7; border-radius: 8px; border: none;")
        weightTextLayout = QVBoxLayout()
        weightTextLayout.setSpacing(3)
        weightHeaderLbl = QLabel("Default Weight")
        weightHeaderLbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.weight_badge = QLabel("+1.00 / 0.00")
        self.weight_badge.setAlignment(Qt.AlignCenter)
        self.weight_badge.setStyleSheet("""
            QLabel {
                background-color: #DCFCE7;
                color: #15803D;
                border: 1px solid #BBF7D0;
                border-radius: 10px;
                padding: 2px 8px;
                font-weight: 800;
                font-size: 11px;
            }
        """)
        weightTextLayout.addWidget(weightHeaderLbl)
        weightTextLayout.addWidget(self.weight_badge)
        weightPodLayout.addWidget(starIcon)
        weightPodLayout.addLayout(weightTextLayout)
        metricsLayout.addLayout(weightPodLayout, 2)

        # Divider 4
        metricsLayout.addWidget(create_vertical_separator())

        # --- Pod 5: Editor Mode ---
        modePodLayout = QHBoxLayout()
        modePodLayout.setSpacing(10)
        penIcon = QLabel("✍️")
        penIcon.setFont(QFont("Segoe UI Emoji", 15))
        penIcon.setAlignment(Qt.AlignCenter)
        penIcon.setFixedSize(32, 32)
        penIcon.setStyleSheet("background-color: #EEF2FF; border-radius: 8px; border: none;")
        modeTextLayout = QVBoxLayout()
        modeTextLayout.setSpacing(3)
        modeHeaderLbl = QLabel("Editor Mode")
        modeHeaderLbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.editor_mode_badge = QLabel("Ready")
        self.editor_mode_badge.setAlignment(Qt.AlignCenter)
        self.editor_mode_badge.setStyleSheet("""
            QLabel {
                background-color: #EEF2FF;
                color: #4F46E5;
                border: 1px solid #C7D2FE;
                border-radius: 10px;
                padding: 2px 10px;
                font-weight: 700;
                font-size: 11px;
            }
        """)
        modeTextLayout.addWidget(modeHeaderLbl)
        modeTextLayout.addWidget(self.editor_mode_badge)
        modePodLayout.addWidget(penIcon)
        modePodLayout.addLayout(modeTextLayout)
        metricsLayout.addLayout(modePodLayout, 2)

        # Divider 5
        metricsLayout.addWidget(create_vertical_separator())

        # --- Action Button on Far Right: + Add Category ---
        self.add_category_button = QPushButton("➕  Add Category")
        self.add_category_button.setObjectName("addCategoryBtn")
        self.add_category_button.setCursor(Qt.PointingHandCursor)
        self.add_category_button.setStyleSheet("""
            QPushButton#addCategoryBtn {
                border: 1px solid #2563EB;
                color: #2563EB;
                background-color: #EFF6FF;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton#addCategoryBtn:hover {
                background-color: #DBEAFE;
                border-color: #1D4ED8;
            }
        """)
        self.add_category_button.clicked.connect(self.add_category)
        metricsLayout.addWidget(self.add_category_button)

        main_layout.addWidget(self.card_metrics)

        # ======================================================
        # 3. QUESTION AUTHORING & CONFIGURATION FORM CARD (QFrame#card_form)
        # ======================================================

        self.card_form = QFrame()
        self.card_form.setObjectName("card_form")
        self.authorCard = self.card_form  # Backward-compatible alias
        authorCardLayout = QVBoxLayout(self.card_form)
        authorCardLayout.setContentsMargins(20, 18, 20, 18)
        authorCardLayout.setSpacing(14)

        # Form Section Header: Blue icon + Bold Title
        formHeaderRow = QHBoxLayout()
        formHeaderRow.setSpacing(10)

        formIconBadge = QLabel("✦")
        formIconBadge.setFont(QFont("Segoe UI", 12, QFont.Bold))
        formIconBadge.setAlignment(Qt.AlignCenter)
        formIconBadge.setFixedSize(28, 28)
        formIconBadge.setStyleSheet("""
            background-color: #2563EB;
            color: #FFFFFF;
            border-radius: 6px;
            font-weight: 900;
        """)

        formTitleLayout = QVBoxLayout()
        formTitleLayout.setSpacing(1)

        authorHeader = QLabel("Question Authoring & Configuration")
        authorHeader.setObjectName("sectionHeader")
        authorHeader.setFont(QFont("Segoe UI", 12, QFont.Bold))
        authorHeader.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")

        authorSubheader = QLabel("Compose multiple-choice questions, set answer options, and configure scoring parameters.")
        authorSubheader.setStyleSheet("color: #64748B; font-size: 11px;")

        formTitleLayout.addWidget(authorHeader)
        formTitleLayout.addWidget(authorSubheader)

        formHeaderRow.addWidget(formIconBadge)
        formHeaderRow.addLayout(formTitleLayout)
        formHeaderRow.addStretch()
        authorCardLayout.addLayout(formHeaderRow)

        # Category Dropdown Row
        catRow = QHBoxLayout()
        catRow.setSpacing(12)
        catSelectLbl = QLabel("Category:")
        catSelectLbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        catSelectLbl.setStyleSheet("color: #475569; font-weight: 700;")

        self.category_combo = QComboBox()
        self.category_combo.setView(QListView())
        self.category_combo.setMinimumHeight(38)
        self.category_combo.setCursor(Qt.PointingHandCursor)
        self.category_combo.currentIndexChanged.connect(self._on_category_selected)

        catRow.addWidget(catSelectLbl)
        catRow.addWidget(self.category_combo, 2)
        catRow.addStretch(1)
        authorCardLayout.addLayout(catRow)

        # Question Prompt Area
        promptLayout = QVBoxLayout()
        promptLayout.setSpacing(5)
        promptLbl = QLabel("Question Prompt")
        promptLbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        promptLbl.setStyleSheet("color: #475569; font-weight: 700;")

        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Enter the examination question prompt...")
        self.question_input.setMinimumHeight(68)
        self.question_input.setMaximumHeight(90)
        promptLayout.addWidget(promptLbl)
        promptLayout.addWidget(self.question_input)
        authorCardLayout.addLayout(promptLayout)

        # Option Inputs Grid (A, B, C, D) 2x2 layout with light pill badges
        optionsGrid = QGridLayout()
        optionsGrid.setHorizontalSpacing(16)
        optionsGrid.setVerticalSpacing(10)

        # Option A
        optALayout = QHBoxLayout()
        optALayout.setSpacing(8)
        self.badge_a = QLabel("A")
        self.badge_a.setObjectName("optionBadge")
        self.badge_a.setFixedSize(30, 30)
        self.badge_a.setAlignment(Qt.AlignCenter)
        self.option_a = QLineEdit()
        self.option_a.setPlaceholderText("Option A text")
        self.option_a.setMinimumHeight(36)
        optALayout.addWidget(self.badge_a)
        optALayout.addWidget(self.option_a)
        optionsGrid.addLayout(optALayout, 0, 0)

        # Option B
        optBLayout = QHBoxLayout()
        optBLayout.setSpacing(8)
        self.badge_b = QLabel("B")
        self.badge_b.setObjectName("optionBadge")
        self.badge_b.setFixedSize(30, 30)
        self.badge_b.setAlignment(Qt.AlignCenter)
        self.option_b = QLineEdit()
        self.option_b.setPlaceholderText("Option B text")
        self.option_b.setMinimumHeight(36)
        optBLayout.addWidget(self.badge_b)
        optBLayout.addWidget(self.option_b)
        optionsGrid.addLayout(optBLayout, 0, 1)

        # Option C
        optCLayout = QHBoxLayout()
        optCLayout.setSpacing(8)
        self.badge_c = QLabel("C")
        self.badge_c.setObjectName("optionBadge")
        self.badge_c.setFixedSize(30, 30)
        self.badge_c.setAlignment(Qt.AlignCenter)
        self.option_c = QLineEdit()
        self.option_c.setPlaceholderText("Option C text")
        self.option_c.setMinimumHeight(36)
        optCLayout.addWidget(self.badge_c)
        optCLayout.addWidget(self.option_c)
        optionsGrid.addLayout(optCLayout, 1, 0)

        # Option D
        optDLayout = QHBoxLayout()
        optDLayout.setSpacing(8)
        self.badge_d = QLabel("D")
        self.badge_d.setObjectName("optionBadge")
        self.badge_d.setFixedSize(30, 30)
        self.badge_d.setAlignment(Qt.AlignCenter)
        self.option_d = QLineEdit()
        self.option_d.setPlaceholderText("Option D text")
        self.option_d.setMinimumHeight(36)
        optDLayout.addWidget(self.badge_d)
        optDLayout.addWidget(self.option_d)
        optionsGrid.addLayout(optDLayout, 1, 1)

        authorCardLayout.addLayout(optionsGrid)

        # Scoring Row
        scoreRow = QHBoxLayout()
        scoreRow.setSpacing(14)

        lbl_corr = QLabel("Correct Option:")
        lbl_corr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_corr.setStyleSheet("color: #475569; font-weight: 700;")
        self.correct_option = QComboBox()
        self.correct_option.setView(QListView())
        self.correct_option.addItems(["A", "B", "C", "D"])
        self.correct_option.setMinimumHeight(36)
        self.correct_option.setMinimumWidth(85)

        lbl_marks = QLabel("Marks (+):")
        lbl_marks.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_marks.setStyleSheet("color: #475569; font-weight: 700;")
        self.marks = QDoubleSpinBox()
        self.marks.setMinimum(0)
        self.marks.setMaximum(100)
        self.marks.setValue(1)
        self.marks.setDecimals(2)
        self.marks.setMinimumHeight(36)
        self.marks.setMinimumWidth(90)

        lbl_neg = QLabel("Negative Marks (-):")
        lbl_neg.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_neg.setStyleSheet("color: #475569; font-weight: 700;")
        self.negative_marks = QDoubleSpinBox()
        self.negative_marks.setMinimum(0)
        self.negative_marks.setMaximum(100)
        self.negative_marks.setValue(0)
        self.negative_marks.setDecimals(2)
        self.negative_marks.setMinimumHeight(36)
        self.negative_marks.setMinimumWidth(90)

        scoreRow.addWidget(lbl_corr)
        scoreRow.addWidget(self.correct_option)
        scoreRow.addSpacing(8)
        scoreRow.addWidget(lbl_marks)
        scoreRow.addWidget(self.marks)
        scoreRow.addSpacing(8)
        scoreRow.addWidget(lbl_neg)
        scoreRow.addWidget(self.negative_marks)
        scoreRow.addStretch(1)

        authorCardLayout.addLayout(scoreRow)

        # Divider line
        formSep = QFrame()
        formSep.setFrameShape(QFrame.HLine)
        formSep.setStyleSheet("background-color: #F1F5F9; max-height: 1px; border: none;")
        authorCardLayout.addWidget(formSep)

        # Action Buttons Row
        actionsRow = QHBoxLayout()
        actionsRow.setSpacing(10)

        self.add_button = QPushButton("➕  Save Question")
        self.add_button.setObjectName("primarySaveBtn")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setMinimumHeight(38)
        self.add_button.clicked.connect(self.add_question)

        self.update_button = QPushButton("✏  Update Question")
        self.update_button.setObjectName("outlineUpdateBtn")
        self.update_button.setCursor(Qt.PointingHandCursor)
        self.update_button.setMinimumHeight(38)
        self.update_button.clicked.connect(self.update_question)

        self.delete_button = QPushButton("🗑  Delete Question")
        self.delete_button.setObjectName("dangerDeleteBtn")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setMinimumHeight(38)
        self.delete_button.clicked.connect(self.delete_question)

        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setObjectName("neutralClearBtn")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setMinimumHeight(38)
        self.clear_button.clicked.connect(self.clear_form)

        self.refresh_button = QPushButton("⟳  Refresh")
        self.refresh_button.setObjectName("neutralRefreshBtn")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setMinimumHeight(38)
        self.refresh_button.clicked.connect(self.refresh_all)

        actionsRow.addWidget(self.add_button)
        actionsRow.addWidget(self.update_button)
        actionsRow.addWidget(self.delete_button)
        actionsRow.addWidget(self.clear_button)
        actionsRow.addStretch(1)
        actionsRow.addWidget(self.refresh_button)

        authorCardLayout.addLayout(actionsRow)
        main_layout.addWidget(self.card_form)

        # ======================================================
        # 4. QUESTION REPOSITORY TABLE CARD (QFrame#card_table)
        # ======================================================

        self.card_table = QFrame()
        self.card_table.setObjectName("card_table")
        self.repoCard = self.card_table  # Backward-compatible alias
        repoCardLayout = QVBoxLayout(self.card_table)
        repoCardLayout.setContentsMargins(18, 16, 18, 16)
        repoCardLayout.setSpacing(12)

        repoHeaderRow = QHBoxLayout()
        repoHeaderRow.setSpacing(12)

        repoTitle = QLabel("🗄  Question Repository")
        repoTitle.setObjectName("sectionHeader")
        repoTitle.setFont(QFont("Segoe UI", 12, QFont.Bold))
        repoTitle.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("repoSearchInput")
        self.search_input.setPlaceholderText("🔍 Search questions by prompt, category, or options...")
        self.search_input.setMinimumHeight(38)
        self.search_input.setMinimumWidth(320)
        self.search_input.textChanged.connect(self.filter_questions)

        repoHeaderRow.addWidget(repoTitle)
        repoHeaderRow.addStretch()
        repoHeaderRow.addWidget(self.search_input)
        repoCardLayout.addLayout(repoHeaderRow)

        # Table Widget
        self.table = QTableWidget()
        self.table.setObjectName("questionsTable")
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "CATEGORY",
            "QUESTION",
            "OPTION A",
            "OPTION B",
            "OPTION C",
            "OPTION D",
            "CORRECT",
            "MARKS"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setMinimumHeight(260)

        table_header = self.table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        table_header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 60)
        table_header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 150)
        table_header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 90)
        table_header.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 80)

        self.table.cellClicked.connect(self.select_question)
        repoCardLayout.addWidget(self.table)
        main_layout.addWidget(self.card_table)

        # Backward compatibility aliases for all widget names
        self.question_text_edit = self.question_input
        self.option_a_input = self.option_a
        self.option_b_input = self.option_b
        self.option_c_input = self.option_c
        self.option_d_input = self.option_d
        self.table_widget = self.table
        self.btn_save = self.add_button
        self.btn_update = self.update_button
        self.btn_delete = self.delete_button
        self.btn_clear = self.clear_button
        self.btn_refresh = self.refresh_button

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

        self._apply_theme_colors()

    # ==========================================================
    # THEME REACTIVITY & EXPLICIT CARD STYLING
    # ==========================================================

    def _on_theme_changed(self, theme_name):
        self._apply_theme_colors()

    def _apply_theme_colors(self):
        p = get_theme_palette()
        is_dark = p.get("name") == "dark"

        if is_dark:
            card_bg = "#1E293B"
            card_border = "#334155"
            canvas_bg = "#0F172A"
            text_main = "#F8FAFC"
            text_muted = "#94A3B8"
            input_bg = "#0F172A"
            input_border = "#334155"
            focus_color = "#6366F1"
            badge_bg = "#334155"
            badge_text = "#F8FAFC"
            badge_border = "#475569"
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

            # Cat pod in dark
            self.catPod.setStyleSheet("""
                QFrame#catPod {
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 4px;
                }
            """)
            self.top_category_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.total_questions_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.categories_count_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")

            # Outline update button in dark
            self.update_button.setStyleSheet("""
                QPushButton#outlineUpdateBtn {
                    background-color: #1E293B;
                    color: #818CF8;
                    border: 1px solid #6366F1;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#outlineUpdateBtn:hover {
                    background-color: #312E81;
                    color: #FFFFFF;
                }
            """)

            # Clear and refresh in dark
            btn_neutral_dark = """
                QPushButton {
                    background-color: #1E293B;
                    color: #CBD5E1;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #334155;
                    color: #FFFFFF;
                }
            """
            self.clear_button.setStyleSheet(btn_neutral_dark)
            self.refresh_button.setStyleSheet(btn_neutral_dark)

        else:
            card_bg = "#FFFFFF"
            card_border = "#E2E8F0"
            canvas_bg = "#F8FAFC"
            text_main = "#0F172A"
            text_muted = "#64748B"
            input_bg = "#FFFFFF"
            input_border = "#CBD5E1"
            focus_color = "#2563EB"
            badge_bg = "#F1F5F9"
            badge_text = "#334155"
            badge_border = "#CBD5E1"
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

            # Cat pod in light
            self.catPod.setStyleSheet("""
                QFrame#catPod {
                    background-color: #EEF2FF;
                    border: 1px solid #DDE7FF;
                    border-radius: 10px;
                    padding: 4px;
                }
            """)
            self.top_category_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
            self.total_questions_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
            self.categories_count_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B; background: transparent; border: none;")

            # Outline update button in light
            self.update_button.setStyleSheet("""
                QPushButton#outlineUpdateBtn {
                    background-color: #FFFFFF;
                    color: #2563EB;
                    border: 1px solid #2563EB;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton#outlineUpdateBtn:hover {
                    background-color: #EFF6FF;
                }
            """)

            # Clear and refresh in light
            btn_neutral_light = """
                QPushButton {
                    background-color: #F8FAFC;
                    color: #475569;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                    color: #0F172A;
                    border-color: #94A3B8;
                }
            """
            self.clear_button.setStyleSheet(btn_neutral_light)
            self.refresh_button.setStyleSheet(btn_neutral_light)

        # Style card containers
        card_style = f"""
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 12px;
        """
        self.card_header.setStyleSheet(f"QFrame#card_header {{ {card_style} }}")
        self.card_metrics.setStyleSheet(f"QFrame#card_metrics {{ {card_style} }}")
        self.card_form.setStyleSheet(f"QFrame#card_form {{ {card_style} }}")
        self.card_table.setStyleSheet(f"QFrame#card_table {{ {card_style} }}")

        # Style Question prompt text area
        self.question_input.setStyleSheet(f"""
            QTextEdit {{
                border-radius: 8px;
                padding: 10px 12px;
                border: 1px solid {input_border};
                background-color: {input_bg};
                color: {text_main};
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 1px solid {focus_color};
            }}
        """)

        # Explicit QComboBox & QAbstractItemView fix for dropdown visibility
        combo_style = f"""
            QComboBox {{
                background-color: {input_bg};
                color: {text_main};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QComboBox:focus {{
                border: 1px solid {focus_color};
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
            QComboBox QAbstractItemView,
            QComboBox QListView {{
                background-color: {combo_view_bg};
                color: {text_main};
                selection-background-color: {combo_view_select};
                selection-color: {focus_color};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item,
            QComboBox QListView::item {{
                padding: 6px 10px;
                color: {text_main};
                background-color: {combo_view_bg};
                border-radius: 4px;
                min-height: 24px;
            }}
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected,
            QComboBox QListView::item:hover,
            QComboBox QListView::item:selected {{
                background-color: {combo_view_select};
                color: {focus_color};
            }}
        """
        self.category_combo.setStyleSheet(combo_style)
        self.correct_option.setStyleSheet(combo_style)

        # Style Option Inputs and Option Badges
        option_input_style = f"""
            QLineEdit {{
                border-radius: 8px;
                padding: 6px 12px;
                border: 1px solid {input_border};
                background-color: {input_bg};
                color: {text_main};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {focus_color};
            }}
        """
        self.option_a.setStyleSheet(option_input_style)
        self.option_b.setStyleSheet(option_input_style)
        self.option_c.setStyleSheet(option_input_style)
        self.option_d.setStyleSheet(option_input_style)

        badge_style = f"""
            QLabel#optionBadge {{
                background-color: {badge_bg};
                color: {badge_text};
                border: 1px solid {badge_border};
                border-radius: 6px;
                font-weight: 800;
                font-size: 12px;
            }}
        """
        self.badge_a.setStyleSheet(badge_style)
        self.badge_b.setStyleSheet(badge_style)
        self.badge_c.setStyleSheet(badge_style)
        self.badge_d.setStyleSheet(badge_style)

        # Style Spinboxes
        spin_style = f"""
            QDoubleSpinBox {{
                background-color: {input_bg};
                color: {text_main};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QDoubleSpinBox:focus {{
                border: 1px solid {focus_color};
            }}
        """
        self.marks.setStyleSheet(spin_style)
        self.negative_marks.setStyleSheet(spin_style)

        # Style Primary Save Button
        self.add_button.setStyleSheet("""
            QPushButton#primarySaveBtn {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton#primarySaveBtn:hover {
                background-color: #1D4ED8;
            }
        """)

        # Style Soft Danger Delete Button
        self.delete_button.setStyleSheet("""
            QPushButton#dangerDeleteBtn {
                background-color: #FFF1F2;
                color: #E11D48;
                border: 1px solid #FDA4AF;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton#dangerDeleteBtn:hover {
                background-color: #FFE4E6;
                border-color: #E11D48;
            }
        """)

        # Style Search Input
        self.search_input.setStyleSheet(f"""
            QLineEdit#repoSearchInput {{
                border-radius: 8px;
                padding: 6px 14px;
                border: 1px solid {input_border};
                background-color: {input_bg};
                color: {text_main};
                font-size: 12px;
            }}
            QLineEdit#repoSearchInput:focus {{
                border: 1px solid {focus_color};
            }}
        """)

        # Style Repository Table Widget
        self.table.setStyleSheet(f"""
            QTableWidget#questionsTable {{
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
            QTableWidget#questionsTable::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {table_line};
            }}
            QTableWidget#questionsTable::item:selected {{
                background-color: {table_select_bg};
                color: {table_select_fg};
            }}
            QTableWidget#questionsTable::item:hover {{
                background-color: {table_hover};
            }}
            QTableWidget#questionsTable QHeaderView::section {{
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
        """)

    # ==========================================================
    # LOAD CATEGORIES
    # ==========================================================

    def load_categories(self):

        try:
            categories = QuestionModel.get_all_categories()
            current_category_id = self.category_combo.currentData()

            self.category_combo.blockSignals(True)
            self.category_combo.clear()

            self.category_combo.addItem("Select Category", None)

            for category in categories:
                self.category_combo.addItem(
                    category["name"],
                    category["id"]
                )

            self.category_combo.blockSignals(False)

            self.categories_count_label.setText(str(len(categories)))

            if current_category_id is not None:
                index = self.category_combo.findData(current_category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)

            self._update_category_pod()

        except Exception as e:
            self.category_combo.blockSignals(False)
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load categories:\n\n{e}"
            )

    def _on_category_selected(self):
        self._update_category_pod()

    def _update_category_pod(self):
        curr_text = self.category_combo.currentText()
        if curr_text and curr_text != "Select Category":
            self.top_category_label.setText(curr_text)
            self.cat_count_label.setText("Active Filtering")
        else:
            self.top_category_label.setText("All Categories")
            self.cat_count_label.setText("Repository Taxonomy")

    # ==========================================================
    # ADD CATEGORY
    # ==========================================================

    def add_category(self):

        name, ok = QInputDialog.getText(
            self,
            "Add Category",
            "Enter category name:"
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            QMessageBox.warning(
                self,
                "Validation",
                "Please enter a category name."
            )
            return

        categories = QuestionModel.get_all_categories()

        for category in categories:
            if category["name"].strip().lower() == name.lower():
                QMessageBox.warning(
                    self,
                    "Duplicate Category",
                    "This category already exists."
                )
                return

        category_id = QuestionModel.add_category(name)

        if category_id:
            QMessageBox.information(
                self,
                "Success",
                "Category added successfully."
            )
            self.load_categories()
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Unable to add category."
            )

    # ==========================================================
    # REFRESH ALL
    # ==========================================================

    def refresh_all(self):
        self.load_categories()
        self.load_questions()

    # ==========================================================
    # SEARCH FILTER
    # ==========================================================

    def filter_questions(self, query):
        text = (query or "").strip().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    # ==========================================================
    # LOAD QUESTIONS
    # ==========================================================

    def load_questions(self):

        try:
            questions = QuestionModel.get_all_questions()
            self._all_questions_cache = questions or []

            self.table.setRowCount(len(questions))

            for row, question in enumerate(questions):

                id_item = QTableWidgetItem(str(question["id"]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, id_item)

                category_name = question["category_name"] or "Uncategorized"
                self.table.setItem(row, 1, QTableWidgetItem(category_name))

                self.table.setItem(row, 2, QTableWidgetItem(question["question_text"]))
                self.table.setItem(row, 3, QTableWidgetItem(question["option_a"]))
                self.table.setItem(row, 4, QTableWidgetItem(question["option_b"]))
                self.table.setItem(row, 5, QTableWidgetItem(question["option_c"]))
                self.table.setItem(row, 6, QTableWidgetItem(question["option_d"]))

                corr_item = QTableWidgetItem(question["correct_option"])
                corr_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 7, corr_item)

                marks_item = QTableWidgetItem(str(question["marks"]))
                marks_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 8, marks_item)

            self.total_questions_label.setText(str(len(questions)))

            curr_search = self.search_input.text()
            if curr_search:
                self.filter_questions(curr_search)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unable to load questions:\n\n{e}"
            )

    # ==========================================================
    # SELECT QUESTION
    # ==========================================================

    def select_question(self, row, column):

        item = self.table.item(row, 0)
        if item is None:
            return

        question_id = int(item.text())
        question = QuestionModel.get_question(question_id)

        if question is None:
            return

        self.selected_question_id = question_id
        self.editor_mode_badge.setText(f"Editing #{question_id}")
        self.editor_mode_badge.setStyleSheet("""
            QLabel {
                background-color: #FEF3C7;
                color: #B45309;
                border: 1px solid #FDE68A;
                border-radius: 10px;
                padding: 2px 10px;
                font-weight: 700;
                font-size: 11px;
            }
        """)

        self.question_input.setPlainText(question["question_text"])

        category_id = question["category_id"]
        if category_id is None:
            self.category_combo.setCurrentIndex(0)
        else:
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentIndex(0)

        self.option_a.setText(question["option_a"])
        self.option_b.setText(question["option_b"])
        self.option_c.setText(question["option_c"])
        self.option_d.setText(question["option_d"])

        index = self.correct_option.findText(question["correct_option"])
        if index >= 0:
            self.correct_option.setCurrentIndex(index)

        self.marks.setValue(float(question["marks"]))
        self.negative_marks.setValue(float(question["negative_marks"]))

    # ==========================================================
    # VALIDATE FORM
    # ==========================================================

    def validate_form(self):

        question = self.question_input.toPlainText().strip()
        option_a = self.option_a.text().strip()
        option_b = self.option_b.text().strip()
        option_c = self.option_c.text().strip()
        option_d = self.option_d.text().strip()
        category_id = self.category_combo.currentData()

        if not question:
            QMessageBox.warning(self, "Validation", "Please enter a question.")
            return None

        if category_id is None:
            QMessageBox.warning(self, "Validation", "Please select a category.")
            return None

        if not option_a:
            QMessageBox.warning(self, "Validation", "Please enter Option A.")
            return None

        if not option_b:
            QMessageBox.warning(self, "Validation", "Please enter Option B.")
            return None

        if not option_c:
            QMessageBox.warning(self, "Validation", "Please enter Option C.")
            return None

        if not option_d:
            QMessageBox.warning(self, "Validation", "Please enter Option D.")
            return None

        return (
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            self.correct_option.currentText(),
            self.marks.value(),
            self.negative_marks.value(),
            category_id
        )

    # ==========================================================
    # ADD / SAVE QUESTION
    # ==========================================================

    def add_question(self):

        data = self.validate_form()
        if data is None:
            return

        question_id = QuestionModel.add_question(*data)

        if question_id:
            QMessageBox.information(
                self,
                "Success",
                "Question added successfully."
            )
            self.clear_form()
            self.load_questions()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Unable to add question."
            )

    def save_question(self):
        """Backward-compatible alias for add_question."""
        return self.add_question()

    def auto_select(self):
        """Safe stub if invoked."""
        pass

    # ==========================================================
    # UPDATE QUESTION
    # ==========================================================

    def update_question(self):

        if self.selected_question_id is None:
            QMessageBox.warning(
                self,
                "Update Question",
                "Please select a question from the repository table first."
            )
            return

        data = self.validate_form()
        if data is None:
            return

        success = QuestionModel.update_question(
            self.selected_question_id,
            *data
        )

        if success:
            QMessageBox.information(
                self,
                "Success",
                "Question updated successfully."
            )
            self.clear_form()
            self.load_questions()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Unable to update question."
            )

    # ==========================================================
    # DELETE QUESTION
    # ==========================================================

    def delete_question(self):

        if self.selected_question_id is None:
            QMessageBox.warning(
                self,
                "Delete Question",
                "Please select a question from the repository table first."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this question?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = QuestionModel.delete_question(
            self.selected_question_id
        )

        if success:
            QMessageBox.information(
                self,
                "Success",
                "Question deleted successfully."
            )
            self.clear_form()
            self.load_questions()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Unable to delete question."
            )

    # ==========================================================
    # CLEAR FORM
    # ==========================================================

    def clear_form(self):

        self.selected_question_id = None
        self.editor_mode_badge.setText("Ready")
        self.editor_mode_badge.setStyleSheet("""
            QLabel {
                background-color: #EEF2FF;
                color: #4F46E5;
                border: 1px solid #C7D2FE;
                border-radius: 10px;
                padding: 2px 10px;
                font-weight: 700;
                font-size: 11px;
            }
        """)

        self.question_input.clear()
        self.option_a.clear()
        self.option_b.clear()
        self.option_c.clear()
        self.option_d.clear()
        self.category_combo.setCurrentIndex(0)
        self.correct_option.setCurrentIndex(0)
        self.marks.setValue(1)
        self.negative_marks.setValue(0)
        self.table.clearSelection()


# ==============================================================
# TEST PAGE DIRECTLY
# ==============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuestionsPage()
    window.setWindowTitle("Question Management")
    window.resize(1400, 850)
    window.show()
    sys.exit(app.exec_())