import sys

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
        self.headerIconBox = QLabel("❓")
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

        main_layout.addWidget(headerCard)

        # ======================================================
        # 2. TOP SUMMARY / CONTROL BAR (Pods Card)
        # ======================================================

        self.summaryCard = QFrame()
        self.summaryCard.setObjectName("card")
        summaryLayout = QHBoxLayout(self.summaryCard)
        summaryLayout.setContentsMargins(14, 12, 14, 12)
        summaryLayout.setSpacing(14)

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
        folderIcon.setFixedSize(32, 32)
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
        summaryLayout.addWidget(self.catPod, 3)

        # Divider 1
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet("color: #E2E8F0; max-width: 1px;")
        summaryLayout.addWidget(sep1)

        # --- Pod 2: Total Questions ---
        totPodLayout = QHBoxLayout()
        totPodLayout.setSpacing(8)
        totIcon = QLabel("📄")
        totIcon.setFont(QFont("Segoe UI Emoji", 15))
        totIcon.setStyleSheet("background: transparent; border: none;")
        totTextLayout = QVBoxLayout()
        totTextLayout.setSpacing(2)
        totHeaderLbl = QLabel("Total Questions")
        totHeaderLbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.total_questions_label = QLabel("0")
        self.total_questions_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
        totTextLayout.addWidget(totHeaderLbl)
        totTextLayout.addWidget(self.total_questions_label)
        totPodLayout.addWidget(totIcon)
        totPodLayout.addLayout(totTextLayout)
        summaryLayout.addLayout(totPodLayout, 1)

        # Divider 2
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #E2E8F0; max-width: 1px;")
        summaryLayout.addWidget(sep2)

        # --- Pod 3: Categories Count ---
        categoriesPodLayout = QHBoxLayout()
        categoriesPodLayout.setSpacing(8)
        tagIcon = QLabel("🏷️")
        tagIcon.setFont(QFont("Segoe UI Emoji", 15))
        tagIcon.setStyleSheet("background: transparent; border: none;")
        catCountTextLayout = QVBoxLayout()
        catCountTextLayout.setSpacing(2)
        catCountHeaderLbl = QLabel("Categories")
        catCountHeaderLbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600; background: transparent; border: none;")
        self.categories_count_label = QLabel("0")
        self.categories_count_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
        catCountTextLayout.addWidget(catCountHeaderLbl)
        catCountTextLayout.addWidget(self.categories_count_label)
        categoriesPodLayout.addWidget(tagIcon)
        categoriesPodLayout.addLayout(catCountTextLayout)
        summaryLayout.addLayout(categoriesPodLayout, 1)

        # Divider 3
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.VLine)
        sep3.setStyleSheet("color: #E2E8F0; max-width: 1px;")
        summaryLayout.addWidget(sep3)

        # --- Pod 4: Default Weight ---
        weightPodLayout = QHBoxLayout()
        weightPodLayout.setSpacing(8)
        starIcon = QLabel("⭐")
        starIcon.setFont(QFont("Segoe UI Emoji", 15))
        starIcon.setStyleSheet("background: transparent; border: none;")
        weightTextLayout = QVBoxLayout()
        weightTextLayout.setSpacing(2)
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
        summaryLayout.addLayout(weightPodLayout, 1)

        # Divider 4
        sep4 = QFrame()
        sep4.setFrameShape(QFrame.VLine)
        sep4.setStyleSheet("color: #E2E8F0; max-width: 1px;")
        summaryLayout.addWidget(sep4)

        # --- Pod 5: Editor Mode ---
        modePodLayout = QHBoxLayout()
        modePodLayout.setSpacing(8)
        penIcon = QLabel("✍️")
        penIcon.setFont(QFont("Segoe UI Emoji", 15))
        penIcon.setStyleSheet("background: transparent; border: none;")
        modeTextLayout = QVBoxLayout()
        modeTextLayout.setSpacing(2)
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
        summaryLayout.addLayout(modePodLayout, 1)

        # --- Pod 6: Add Category Action Button ---
        self.add_category_button = QPushButton("➕  Add Category")
        self.add_category_button.setObjectName("secondaryBtn")
        self.add_category_button.setCursor(Qt.PointingHandCursor)
        self.add_category_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #EFF6FF;
                border-color: #2563EB;
            }
        """)
        self.add_category_button.clicked.connect(self.add_category)
        summaryLayout.addWidget(self.add_category_button)

        main_layout.addWidget(self.summaryCard)

        # ======================================================
        # 3. CARD: QUESTION AUTHORING & CONFIGURATION
        # ======================================================

        authorCard = QFrame()
        authorCard.setObjectName("card")
        authorCardLayout = QVBoxLayout(authorCard)
        authorCardLayout.setContentsMargins(18, 16, 18, 16)
        authorCardLayout.setSpacing(14)

        authorHeader = QLabel("✦  Question Authoring & Configuration")
        authorHeader.setObjectName("sectionHeader")
        authorHeader.setFont(QFont("Segoe UI", 12, QFont.Bold))
        authorCardLayout.addWidget(authorHeader)

        # Prompt input
        promptLayout = QVBoxLayout()
        promptLayout.setSpacing(4)
        promptLbl = QLabel("Question Prompt")
        promptLbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        promptLbl.setStyleSheet("color: #475569;")

        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Enter the examination question prompt...")
        self.question_input.setMinimumHeight(65)
        self.question_input.setMaximumHeight(85)
        self.question_input.setStyleSheet("""
            QTextEdit {
                border-radius: 8px;
                padding: 8px 12px;
                border: 1px solid #E2E8F0;
                background-color: #FFFFFF;
                color: #0F172A;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #2563EB;
            }
        """)
        promptLayout.addWidget(promptLbl)
        promptLayout.addWidget(self.question_input)
        authorCardLayout.addLayout(promptLayout)

        # Category Row
        catRow = QHBoxLayout()
        catRow.setSpacing(12)
        catSelectLbl = QLabel("Category:")
        catSelectLbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        catSelectLbl.setStyleSheet("color: #475569;")

        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(38)
        self.category_combo.setCursor(Qt.PointingHandCursor)
        self.category_combo.currentIndexChanged.connect(self._on_category_selected)

        catRow.addWidget(catSelectLbl)
        catRow.addWidget(self.category_combo, 2)
        catRow.addStretch(1)
        authorCardLayout.addLayout(catRow)

        # Options Grid (2 rows x 2 columns)
        optionsGrid = QGridLayout()
        optionsGrid.setHorizontalSpacing(14)
        optionsGrid.setVerticalSpacing(8)

        # Option A
        optALayout = QHBoxLayout()
        badgeA = QLabel("A")
        badgeA.setFixedSize(26, 26)
        badgeA.setAlignment(Qt.AlignCenter)
        badgeA.setStyleSheet("background-color: #EEF2FF; color: #4F46E5; border-radius: 6px; font-weight: 800; font-size: 11px;")
        self.option_a = QLineEdit()
        self.option_a.setPlaceholderText("Option A text")
        self.option_a.setMinimumHeight(36)
        optALayout.addWidget(badgeA)
        optALayout.addWidget(self.option_a)
        optionsGrid.addLayout(optALayout, 0, 0)

        # Option B
        optBLayout = QHBoxLayout()
        badgeB = QLabel("B")
        badgeB.setFixedSize(26, 26)
        badgeB.setAlignment(Qt.AlignCenter)
        badgeB.setStyleSheet("background-color: #EEF2FF; color: #4F46E5; border-radius: 6px; font-weight: 800; font-size: 11px;")
        self.option_b = QLineEdit()
        self.option_b.setPlaceholderText("Option B text")
        self.option_b.setMinimumHeight(36)
        optBLayout.addWidget(badgeB)
        optBLayout.addWidget(self.option_b)
        optionsGrid.addLayout(optBLayout, 0, 1)

        # Option C
        optCLayout = QHBoxLayout()
        badgeC = QLabel("C")
        badgeC.setFixedSize(26, 26)
        badgeC.setAlignment(Qt.AlignCenter)
        badgeC.setStyleSheet("background-color: #EEF2FF; color: #4F46E5; border-radius: 6px; font-weight: 800; font-size: 11px;")
        self.option_c = QLineEdit()
        self.option_c.setPlaceholderText("Option C text")
        self.option_c.setMinimumHeight(36)
        optCLayout.addWidget(badgeC)
        optCLayout.addWidget(self.option_c)
        optionsGrid.addLayout(optCLayout, 1, 0)

        # Option D
        optDLayout = QHBoxLayout()
        badgeD = QLabel("D")
        badgeD.setFixedSize(26, 26)
        badgeD.setAlignment(Qt.AlignCenter)
        badgeD.setStyleSheet("background-color: #EEF2FF; color: #4F46E5; border-radius: 6px; font-weight: 800; font-size: 11px;")
        self.option_d = QLineEdit()
        self.option_d.setPlaceholderText("Option D text")
        self.option_d.setMinimumHeight(36)
        optDLayout.addWidget(badgeD)
        optDLayout.addWidget(self.option_d)
        optionsGrid.addLayout(optDLayout, 1, 1)

        authorCardLayout.addLayout(optionsGrid)

        # Scoring Row
        scoreRow = QHBoxLayout()
        scoreRow.setSpacing(14)

        lbl_corr = QLabel("Correct Option:")
        lbl_corr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_corr.setStyleSheet("color: #475569;")
        self.correct_option = QComboBox()
        self.correct_option.addItems(["A", "B", "C", "D"])
        self.correct_option.setMinimumHeight(36)
        self.correct_option.setMinimumWidth(80)

        lbl_marks = QLabel("Marks (+):")
        lbl_marks.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_marks.setStyleSheet("color: #475569;")
        self.marks = QDoubleSpinBox()
        self.marks.setMinimum(0)
        self.marks.setMaximum(100)
        self.marks.setValue(1)
        self.marks.setDecimals(2)
        self.marks.setMinimumHeight(36)
        self.marks.setMinimumWidth(85)

        lbl_neg = QLabel("Negative Marks (-):")
        lbl_neg.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_neg.setStyleSheet("color: #475569;")
        self.negative_marks = QDoubleSpinBox()
        self.negative_marks.setMinimum(0)
        self.negative_marks.setMaximum(100)
        self.negative_marks.setValue(0)
        self.negative_marks.setDecimals(2)
        self.negative_marks.setMinimumHeight(36)
        self.negative_marks.setMinimumWidth(85)

        scoreRow.addWidget(lbl_corr)
        scoreRow.addWidget(self.correct_option)
        scoreRow.addSpacing(10)
        scoreRow.addWidget(lbl_marks)
        scoreRow.addWidget(self.marks)
        scoreRow.addSpacing(10)
        scoreRow.addWidget(lbl_neg)
        scoreRow.addWidget(self.negative_marks)
        scoreRow.addStretch(1)

        authorCardLayout.addLayout(scoreRow)

        # Action Buttons Row
        actionsRow = QHBoxLayout()
        actionsRow.setSpacing(10)

        self.add_button = QPushButton("➕  Save Question")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setMinimumHeight(38)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 6px 18px;
                font-weight: 700;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.add_button.clicked.connect(self.add_question)

        self.update_button = QPushButton("✏  Update Question")
        self.update_button.setObjectName("secondaryBtn")
        self.update_button.setCursor(Qt.PointingHandCursor)
        self.update_button.setMinimumHeight(38)
        self.update_button.clicked.connect(self.update_question)

        self.delete_button = QPushButton("🗑  Delete Question")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setMinimumHeight(38)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border-color: #DC2626;
            }
        """)
        self.delete_button.clicked.connect(self.delete_question)

        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setObjectName("secondaryBtn")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setMinimumHeight(38)
        self.clear_button.clicked.connect(self.clear_form)

        self.refresh_button = QPushButton("⟳  Refresh")
        self.refresh_button.setObjectName("secondaryBtn")
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
        main_layout.addWidget(authorCard)

        # ======================================================
        # 4. CARD: QUESTION REPOSITORY
        # ======================================================

        repoCard = QFrame()
        repoCard.setObjectName("card")
        repoCardLayout = QVBoxLayout(repoCard)
        repoCardLayout.setContentsMargins(18, 16, 18, 16)
        repoCardLayout.setSpacing(12)

        repoHeaderRow = QHBoxLayout()
        repoTitle = QLabel("🗄  Question Repository")
        repoTitle.setObjectName("sectionHeader")
        repoTitle.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search questions...")
        self.search_input.setMinimumHeight(36)
        self.search_input.setMaximumWidth(280)
        self.search_input.setStyleSheet("""
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
        self.search_input.textChanged.connect(self.filter_questions)

        repoHeaderRow.addWidget(repoTitle)
        repoHeaderRow.addStretch()
        repoHeaderRow.addWidget(self.search_input)
        repoCardLayout.addLayout(repoHeaderRow)

        # Table
        self.table = QTableWidget()
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 140)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 90)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setMinimumHeight(240)
        self.table.setShowGrid(False)

        self.table.cellClicked.connect(self.select_question)
        repoCardLayout.addWidget(self.table)
        main_layout.addWidget(repoCard)

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
            self.catPod.setStyleSheet("""
                QFrame#catPod {
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 4px;
                }
            """)
            self.top_category_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.total_questions_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.categories_count_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC; background: transparent; border: none;")
            self.search_input.setStyleSheet("""
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
            self.question_input.setStyleSheet("""
                QTextEdit {
                    border-radius: 8px;
                    padding: 8px 12px;
                    border: 1px solid #334155;
                    background-color: #1E293B;
                    color: #F8FAFC;
                    font-size: 13px;
                }
                QTextEdit:focus {
                    border-color: #6366F1;
                }
            """)
        else:
            self.catPod.setStyleSheet("""
                QFrame#catPod {
                    background-color: #EEF2FF;
                    border: 1px solid #DDE7FF;
                    border-radius: 10px;
                    padding: 4px;
                }
            """)
            self.top_category_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
            self.total_questions_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
            self.categories_count_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; background: transparent; border: none;")
            self.search_input.setStyleSheet("""
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
            self.question_input.setStyleSheet("""
                QTextEdit {
                    border-radius: 8px;
                    padding: 8px 12px;
                    border: 1px solid #E2E8F0;
                    background-color: #FFFFFF;
                    color: #0F172A;
                    font-size: 13px;
                }
                QTextEdit:focus {
                    border-color: #2563EB;
                }
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
    # ADD QUESTION
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