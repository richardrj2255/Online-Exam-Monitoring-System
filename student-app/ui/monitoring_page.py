import torch
import cv2

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QScrollArea,
    QProgressBar,
    QDialog,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from PyQt5.QtGui import (
    QFont,
    QImage,
    QPixmap,
    QColor,
    QCursor,
)

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QSize,
)

from models.question_model import QuestionModel
from ai.ai_monitoring import ExamAIMonitor
from streaming.camera_stream import CameraStreamer


# =========================================================================
# SUBMIT CONFIRMATION DIALOG (Modern Floating Modal Card)
# =========================================================================

class SubmitConfirmDialog(QDialog):
    """
    Floating rounded confirmation modal dialog:
    - Blue exclamation icon container (!)
    - Title: 'Ready to submit?'
    - Subtitle: 'You still have X unanswered questions.'
    - Two-button action bar: [RETURN TO EXAM] and [SUBMIT NOW]
    """

    def __init__(self, unanswered=0, parent=None):
        super().__init__(parent)
        self.setObjectName("dialog_confirm_submit")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setFixedWidth(460)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 16, 16, 16)

        card = QFrame()
        card.setObjectName("dialog_card")
        card.setStyleSheet("""
            QFrame#dialog_card {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 16px;
            }
        """)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(15, 23, 42, 45))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(20)

        # Header Row: Icon + Title/Subtitle + Close Button
        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        icon_box = QLabel("!")
        icon_box.setFixedSize(40, 40)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet("""
            QLabel {
                background: #EFF6FF;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 20px;
                font-size: 20px;
                font-weight: 800;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        header_row.addWidget(icon_box, 0, Qt.AlignTop)

        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(4)

        title_label = QLabel("Ready to submit?")
        title_label.setStyleSheet("""
            color: #172B4D;
            font-size: 18px;
            font-weight: 700;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)

        if unanswered > 0:
            sub_text = f"You still have {unanswered} unanswered question{'s' if unanswered != 1 else ''}."
        else:
            sub_text = "All questions have been answered. You are ready to submit."

        subtitle_label = QLabel(sub_text)
        subtitle_label.setStyleSheet("""
            color: #5B6B84;
            font-size: 13px;
            font-weight: 500;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        subtitle_label.setWordWrap(True)

        text_vbox.addWidget(title_label)
        text_vbox.addWidget(subtitle_label)
        header_row.addLayout(text_vbox, 1)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 14px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background: #F1F5F9;
                color: #0F172A;
            }
        """)
        btn_close.clicked.connect(self.reject)
        header_row.addWidget(btn_close, 0, Qt.AlignTop)

        card_layout.addLayout(header_row)

        # Action Buttons Row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        btn_return = QPushButton("RETURN TO EXAM")
        btn_return.setCursor(Qt.PointingHandCursor)
        btn_return.setFixedHeight(40)
        btn_return.setStyleSheet("""
            QPushButton {
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                color: #334155;
                font-size: 12px;
                font-weight: 700;
                padding: 0 18px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #F8FAFC;
                border-color: #94A3B8;
            }
            QPushButton:pressed {
                background: #F1F5F9;
            }
        """)
        btn_return.clicked.connect(self.reject)

        btn_submit = QPushButton("SUBMIT NOW")
        btn_submit.setCursor(Qt.PointingHandCursor)
        btn_submit.setFixedHeight(40)
        btn_submit.setStyleSheet("""
            QPushButton {
                background: #2563EB;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                padding: 0 22px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #1D4ED8;
            }
            QPushButton:pressed {
                background: #1E40AF;
            }
        """)
        btn_submit.clicked.connect(self.accept)

        buttons_row.addWidget(btn_return)
        buttons_row.addStretch(1)
        buttons_row.addWidget(btn_submit)

        card_layout.addLayout(buttons_row)
        outer_layout.addWidget(card)


# =========================================================================
# OPTION CARD CONTAINER
# =========================================================================

class OptionCard(QFrame):
    """
    Full-width rounded card container wrapping a QRadioButton:
    - Responsive height (~70px–90px depending on screen resolution)
    - #FFFFFF background, 1.5px solid #E2E8F0 border, 12px radius
    - Active/checked: 2px solid #2563EB border with #EFF6FF background
    - Hover: subtle border & background transition
    """

    def __init__(self, radio, on_selected=None, parent=None):
        super().__init__(parent)
        self.radio = radio
        self.on_selected = on_selected
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("option_card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(64)
        self.setMaximumHeight(96)
        self.setSelected(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 8, 24, 8)
        layout.setSpacing(16)
        layout.addWidget(self.radio, 1, Qt.AlignVCenter)
        self.setLayout(layout)

    def setSelected(self, selected=True):
        if selected:
            self.setStyleSheet("""
                QFrame#option_card {
                    background-color: #EFF6FF;
                    border: 2px solid #2563EB;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#option_card {
                    background-color: #FFFFFF;
                    border: 1.5px solid #E2E8F0;
                    border-radius: 12px;
                }
                QFrame#option_card:hover {
                    background-color: #F8FAFC;
                    border: 1.5px solid #93C5FD;
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.radio.setChecked(True)
            if self.on_selected:
                self.on_selected()
        super().mousePressEvent(event)


# =========================================================================
# MAIN MONITORING PAGE
# =========================================================================

class MonitoringPage(QWidget):

    def __init__(self, student, exam):
        super().__init__()

        # Defensive conversion: handles sqlite3.Row as well as native dicts
        try:
            self.student = dict(student) if student is not None else {}
        except Exception:
            self.student = student

        try:
            self.exam = dict(exam) if exam is not None else {}
        except Exception:
            self.exam = exam

        self.attempt_id = None

        try:
            student_id = self.student.get("id") if hasattr(self.student, "get") else self.student["id"]
            exam_id = self.exam.get("id") if hasattr(self.exam, "get") else self.exam["id"]
            self.attempt_id = QuestionModel.create_exam_attempt(student_id, exam_id)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Examination Already Completed",
                str(e)
            )
            self.attempt_id = None
            QTimer.singleShot(0, self.close)
            return

        # =====================================================
        # QUESTIONS STATE
        # =====================================================
        self.questions = []
        self.current_question_index = 0
        self.answers = {}
        self.flagged_questions = set()
        self.paletteButtons = []

        # =====================================================
        # CAMERA & STREAMING
        # =====================================================
        self.camera = None
        register_no = self.student.get("register_no", "") if hasattr(self.student, "get") else self.student["register_no"]
        self.camera_streamer = CameraStreamer(
            register_no=register_no,
            host="127.0.0.1",
            port=5001,
            quality=60,
            fps=8
        )

        # =====================================================
        # AI MONITORING
        # =====================================================
        self.ai_monitor = None
        self.aiTimer = QTimer()
        self.aiTimer.timeout.connect(self.process_ai_monitoring)
        self.ai_processing = False

        try:
            self.ai_monitor = ExamAIMonitor(
                register_no,
                screenshot_dir="captured/ai"
            )
            print(">>> AI monitoring engine initialized.")
        except Exception as e:
            print(">>> AI monitoring initialization failed:", e)

        self.cameraTimer = QTimer()
        self.cameraTimer.timeout.connect(self.update_camera)

        # =====================================================
        # EXAM TIMER
        # =====================================================
        try:
            duration = self.exam.get("duration", 60) if hasattr(self.exam, "get") else self.exam["duration"]
            self.remaining_seconds = int(duration or 60) * 60
        except Exception:
            self.remaining_seconds = 3600

        self.examTimer = QTimer()
        self.examTimer.timeout.connect(self.update_countdown)

        # =====================================================
        # LOAD QUESTIONS & BUILD UI
        # =====================================================
        self.load_questions()
        self.setupUI()

        # =====================================================
        # START SERVICES
        # =====================================================
        self.start_camera()
        self.camera_streamer.start()
        self.start_ai_monitoring()
        self.examTimer.start(1000)

        # =====================================================
        # SHOW FIRST QUESTION
        # =====================================================
        if self.questions:
            self.show_question(0)
        else:
            self.show_no_questions_message()

    # =========================================================
    # LOAD QUESTIONS
    # =========================================================
    def load_questions(self):
        try:
            exam_id = self.exam.get("id") if hasattr(self.exam, "get") else self.exam["id"]
            self.questions = QuestionModel.get_questions_for_exam(exam_id)
        except Exception as e:
            print("Error loading exam questions:", e)
            self.questions = []

    # =========================================================
    # MODULAR UI CONSTRUCTOR
    # =========================================================
    def setupUI(self):
        exam_name = str(self.exam.get("exam_name", "Online Examination") if hasattr(self.exam, "get") else "Online Examination")
        self.setWindowTitle(f"Online Examination - {exam_name}")
        self.showMaximized()

        self._apply_qss_theme()

        main_root_vbox = QVBoxLayout(self)
        main_root_vbox.setContentsMargins(0, 0, 0, 0)
        main_root_vbox.setSpacing(0)

        # 1. Dark Blue Top Header Bar
        self.header_bar = self._build_header()
        main_root_vbox.addWidget(self.header_bar)

        # Central Canvas Container
        canvas_widget = QWidget()
        canvas_widget.setObjectName("canvas_widget")
        canvas_widget.setStyleSheet("background-color: #F5F8FC;")

        canvas_layout = QHBoxLayout(canvas_widget)
        canvas_layout.setContentsMargins(20, 16, 20, 12)
        canvas_layout.setSpacing(18)

        # 2 & 4. Left Column: Main Question Area (~75%) + Navigation Footer
        left_column_vbox = QVBoxLayout()
        left_column_vbox.setSpacing(14)

        self.card_question_panel = self._build_question_card()
        left_column_vbox.addWidget(self.card_question_panel, 1)

        self.card_nav_footer = self._build_navigation_footer()
        left_column_vbox.addWidget(self.card_nav_footer, 0)

        canvas_layout.addLayout(left_column_vbox, 3)

        # 3. Right Sidebar (~25%)
        self.card_sidebar_panel = self._build_sidebar()
        canvas_layout.addWidget(self.card_sidebar_panel, 1)

        main_root_vbox.addWidget(canvas_widget, 1)

        # 5. Application Footer
        self.app_footer = self._build_app_footer()
        main_root_vbox.addWidget(self.app_footer, 0)

        # Compatibility widget references
        student_name = self.student.get("name", "") if hasattr(self.student, "get") else ""
        student_reg = self.student.get("register_no", "") if hasattr(self.student, "get") else ""
        subject_name = self.exam.get("subject_name", "") if hasattr(self.exam, "get") else ""

        self.studentInfo = QLabel(f"Student: {student_name} | {student_reg}")
        self.subjectInfo = QLabel(f"Subject: {subject_name}")

        self.update_time_label()

    # =========================================================
    # 1. TOP HEADER BAR (#183A7A)
    # =========================================================
    def _build_header(self):
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame#header_bar {
                background-color: #183A7A;
                border: none;
                border-bottom: 1px solid #102B5C;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        header_layout.setSpacing(20)

        # Left Section: Icon Container + Exam Title & Subject Info
        left_hbox = QHBoxLayout()
        left_hbox.setSpacing(14)

        doc_icon_box = QLabel("📑")
        doc_icon_box.setFixedSize(44, 44)
        doc_icon_box.setAlignment(Qt.AlignCenter)
        doc_icon_box.setStyleSheet("""
            QLabel {
                background-color: #2563EB;
                color: #FFFFFF;
                border-radius: 10px;
                font-size: 20px;
            }
        """)
        left_hbox.addWidget(doc_icon_box)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        title_vbox.setAlignment(Qt.AlignVCenter)

        exam_name = str(self.exam.get("exam_name", "Online Examination") if hasattr(self.exam, "get") else "Online Examination")
        subject_name = str(self.exam.get("subject_name", "General") if hasattr(self.exam, "get") else "General")

        self.examTitleLabel = QLabel(exam_name)
        self.examTitleLabel.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        title_vbox.addWidget(self.examTitleLabel)

        self.examSubtitleLabel = QLabel(f"{subject_name}  •  1 Mark")
        self.examSubtitleLabel.setStyleSheet("""
            color: #93C5FD;
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        title_vbox.addWidget(self.examSubtitleLabel)

        left_hbox.addLayout(title_vbox)
        header_layout.addLayout(left_hbox, 0)

        header_layout.addSpacing(20)

        # Center Section: Linear Progress Bar + Dynamic Status Indicator
        center_hbox = QHBoxLayout()
        center_hbox.setSpacing(14)
        center_hbox.setAlignment(Qt.AlignVCenter)

        self.progressBar = QProgressBar()
        self.progress_bar = self.progressBar
        self.progressBar.setFixedWidth(240)
        self.progressBar.setFixedHeight(8)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: rgba(255, 255, 255, 0.22);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 4px;
            }
        """)
        center_hbox.addWidget(self.progressBar)

        self.progressTextLabel = QLabel("Question 1 of 1  |  0% Completed")
        self.questionTrackerLabel = self.progressTextLabel
        self.questionNumberLabel = self.progressTextLabel
        self.progressTextLabel.setStyleSheet("""
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        center_hbox.addWidget(self.progressTextLabel)

        header_layout.addLayout(center_hbox, 1)

        # Right Section: Prominent Timer Box + Auto-Save Badge
        right_hbox = QHBoxLayout()
        right_hbox.setSpacing(14)
        right_hbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Timer Box
        timer_box = QFrame()
        timer_box.setObjectName("frame_timer_box")
        timer_box.setStyleSheet("""
            QFrame#frame_timer_box {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 10px;
            }
        """)
        timer_box_layout = QHBoxLayout(timer_box)
        timer_box_layout.setContentsMargins(14, 6, 16, 6)
        timer_box_layout.setSpacing(10)

        clock_icon = QLabel("⏱")
        clock_icon.setStyleSheet("""
            color: #FFFFFF;
            font-size: 20px;
            background: transparent;
            border: none;
        """)
        timer_box_layout.addWidget(clock_icon)

        timer_vbox = QVBoxLayout()
        timer_vbox.setSpacing(0)
        timer_vbox.setAlignment(Qt.AlignVCenter)

        self.headerTimeLabel = QLabel("00:00")
        self.timer_label = self.headerTimeLabel
        self.headerTimeLabel.setStyleSheet("""
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 700;
            line-height: 1.1;
            background: transparent;
            border: none;
        """)
        timer_vbox.addWidget(self.headerTimeLabel)

        remaining_sub = QLabel("Remaining")
        remaining_sub.setStyleSheet("""
            color: #93C5FD;
            font-size: 10px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        timer_vbox.addWidget(remaining_sub)

        timer_box_layout.addLayout(timer_vbox)
        right_hbox.addWidget(timer_box)

        # Auto-save status badge
        self.autosave_badge = QLabel("✔ Auto-save enabled")
        self.autosave_badge.setStyleSheet("""
            QLabel {
                background-color: #16B364;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                padding: 10px 16px;
                border-radius: 10px;
                border: none;
            }
        """)
        right_hbox.addWidget(self.autosave_badge)

        header_layout.addLayout(right_hbox, 0)
        return header

    # =========================================================
    # 2. MAIN QUESTION CARD PANEL (~75% Width)
    # =========================================================
    def _build_question_card(self):
        card = QFrame()
        card.setObjectName("card_question_panel")
        card.setStyleSheet("""
            QFrame#card_question_panel {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 14px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(16)

        # 1. Top Bar: Pill Tag on Left + Category/Marks on Right
        top_meta_widget = QWidget()
        top_meta_widget.setFixedHeight(34)
        top_meta_widget.setStyleSheet("background: transparent; border: none;")
        top_meta_row = QHBoxLayout(top_meta_widget)
        top_meta_row.setContentsMargins(0, 0, 0, 0)
        top_meta_row.setSpacing(12)

        self.badgeQuestionType = QLabel(":: Multiple Choice")
        self.badgeQuestionType.setFixedHeight(34)
        self.badgeQuestionType.setStyleSheet("""
            QLabel {
                background-color: #EFF6FF;
                color: #2563EB;
                font-size: 13px;
                font-weight: 700;
                padding: 0 16px;
                border-radius: 14px;
                border: 1px solid #DBEAFE;
            }
        """)
        top_meta_row.addWidget(self.badgeQuestionType, 0, Qt.AlignVCenter)

        top_meta_row.addStretch(1)

        subject_name = str(self.exam.get("subject_name", "Mathematics") if hasattr(self.exam, "get") else "Mathematics")
        self.metadataLabel = QLabel(f"📖 {subject_name}  •  1 Mark")
        self.metadataLabel.setFixedHeight(34)
        self.metadataLabel.setStyleSheet("""
            QLabel {
                background-color: #F8FAFC;
                color: #5B6B84;
                font-size: 12px;
                font-weight: 600;
                padding: 0 16px;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
            }
        """)
        top_meta_row.addWidget(self.metadataLabel, 0, Qt.AlignVCenter)
        card_layout.addWidget(top_meta_widget, 0)

        # 2. Question Header Container (Number Badge + Prompt + Sub-prompt)
        prompt_box = QFrame()
        prompt_box.setStyleSheet("background: transparent; border: none;")
        prompt_hbox = QHBoxLayout(prompt_box)
        prompt_hbox.setContentsMargins(0, 6, 0, 10)
        prompt_hbox.setSpacing(18)

        self.questionNumberBadge = QLabel("1")
        self.questionNumberBadge.setFixedSize(46, 46)
        self.questionNumberBadge.setAlignment(Qt.AlignCenter)
        self.questionNumberBadge.setStyleSheet("""
            QLabel {
                background-color: #2563EB;
                color: #FFFFFF;
                font-size: 19px;
                font-weight: 700;
                border-radius: 12px;
                border: none;
            }
        """)
        prompt_hbox.addWidget(self.questionNumberBadge, 0, Qt.AlignTop)

        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(6)
        text_vbox.setAlignment(Qt.AlignTop)

        self.questionTextLabel = QLabel("")
        self.question_text_label = self.questionTextLabel
        self.question_label = self.questionTextLabel
        self.questionTextLabel.setWordWrap(True)
        self.questionTextLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.questionTextLabel.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 22px;
                font-weight: 700;
                line-height: 1.35;
                background: transparent;
                border: none;
            }
        """)
        text_vbox.addWidget(self.questionTextLabel)

        self.subPromptLabel = QLabel("Choose the correct option.")
        self.subPromptLabel.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                border: none;
            }
        """)
        text_vbox.addWidget(self.subPromptLabel)

        prompt_hbox.addLayout(text_vbox, 1)
        card_layout.addWidget(prompt_box, 0)

        # 3. Option Cards (A, B, C, D)
        options_container = QVBoxLayout()
        options_container.setSpacing(14)

        radio_qss = """
            QRadioButton {
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: 600;
                color: #1E293B;
                spacing: 18px;
            }
            QRadioButton::indicator {
                width: 24px;
                height: 24px;
                border-radius: 12px;
                border: 2px solid #CBD5E1;
                background: #FFFFFF;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #2563EB;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #2563EB;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.42, fx:0.5, fy:0.5, stop:0 #2563EB, stop:0.55 #2563EB, stop:0.58 #FFFFFF, stop:1 #FFFFFF);
            }
        """

        self.optionA = QRadioButton()
        self.optionB = QRadioButton()
        self.optionC = QRadioButton()
        self.optionD = QRadioButton()

        for opt in [self.optionA, self.optionB, self.optionC, self.optionD]:
            opt.setStyleSheet(radio_qss)

        self.optionGroup = QButtonGroup(self)
        self.options_group = self.optionGroup
        self.option_buttons = [self.optionA, self.optionB, self.optionC, self.optionD]

        self.optionGroup.addButton(self.optionA, 1)
        self.optionGroup.addButton(self.optionB, 2)
        self.optionGroup.addButton(self.optionC, 3)
        self.optionGroup.addButton(self.optionD, 4)
        self.optionGroup.buttonClicked.connect(lambda _: self.on_option_selected())

        self.cardOptionA = OptionCard(self.optionA, on_selected=self.on_option_selected)
        self.cardOptionB = OptionCard(self.optionB, on_selected=self.on_option_selected)
        self.cardOptionC = OptionCard(self.optionC, on_selected=self.on_option_selected)
        self.cardOptionD = OptionCard(self.optionD, on_selected=self.on_option_selected)

        for card_opt in [self.cardOptionA, self.cardOptionB, self.cardOptionC, self.cardOptionD]:
            options_container.addWidget(card_opt, 1)

        card_layout.addLayout(options_container, 1)

        # 4. Action Utilities Bar (Flag & Clear)
        action_utility_widget = QWidget()
        action_utility_widget.setFixedHeight(44)
        action_utility_widget.setStyleSheet("background: transparent; border: none;")
        action_utility_row = QHBoxLayout(action_utility_widget)
        action_utility_row.setContentsMargins(0, 0, 0, 0)
        action_utility_row.setSpacing(14)

        self.flagBtn = QPushButton("⚐ Flag Question")
        self.btn_flag = self.flagBtn
        self.flagBtn.setFixedHeight(44)
        self.flagBtn.setCursor(Qt.PointingHandCursor)
        self.flagBtn.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                color: #2563EB;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #DBEAFE;
            }
        """)
        self.flagBtn.clicked.connect(self.toggle_flag_current_question)

        self.clearBtn = QPushButton("↺ Clear Answer")
        self.btn_clear = self.clearBtn
        self.clearBtn.setFixedHeight(44)
        self.clearBtn.setCursor(Qt.PointingHandCursor)
        self.clearBtn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 8px;
                color: #5B6B84;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                border-color: #CBD5E1;
                color: #172B4D;
            }
        """)
        self.clearBtn.clicked.connect(self.clear_current_answer)

        action_utility_row.addWidget(self.flagBtn)
        action_utility_row.addWidget(self.clearBtn)
        action_utility_row.addStretch(1)
        card_layout.addWidget(action_utility_widget, 0)

        return card

    # =========================================================
    # 4. QUESTION NAVIGATION FOOTER (Card Container)
    # =========================================================
    def _build_navigation_footer(self):
        nav_card = QFrame()
        nav_card.setObjectName("card_nav_footer")
        nav_card.setFixedHeight(54)
        nav_card.setStyleSheet("""
            QFrame#card_nav_footer {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 12px;
            }
        """)

        nav_layout = QHBoxLayout(nav_card)
        nav_layout.setContentsMargins(20, 0, 20, 0)
        nav_layout.setSpacing(16)

        # Left: Previous Button
        self.previousBtn = QPushButton("‹ Previous")
        self.btn_prev = self.previousBtn
        self.previousBtn.setCursor(Qt.PointingHandCursor)
        self.previousBtn.setFixedHeight(40)
        self.previousBtn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 8px;
                color: #172B4D;
                font-size: 13px;
                font-weight: 600;
                padding: 0 22px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                border-color: #CBD5E1;
            }
            QPushButton:disabled {
                background-color: #F8FAFC;
                border-color: #E2E8F0;
                color: #94A3B8;
            }
        """)
        self.previousBtn.clicked.connect(self.previous_question)
        nav_layout.addWidget(self.previousBtn)

        nav_layout.addStretch(1)

        # Center: Dynamic Status Summary Badges
        center_status_hbox = QHBoxLayout()
        center_status_hbox.setSpacing(16)

        self.footerAnsweredLabel = QLabel("✔ 0 answered")
        self.footerAnsweredLabel.setStyleSheet("""
            color: #16B364;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        center_status_hbox.addWidget(self.footerAnsweredLabel)

        self.footerFlaggedLabel = QLabel("🚩 0 flagged")
        self.footerFlaggedLabel.setStyleSheet("""
            color: #EF4444;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        center_status_hbox.addWidget(self.footerFlaggedLabel)

        self.footerRemainingLabel = QLabel("○ 0 remaining")
        self.footerRemainingLabel.setStyleSheet("""
            color: #5B6B84;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        center_status_hbox.addWidget(self.footerRemainingLabel)

        nav_layout.addLayout(center_status_hbox)

        nav_layout.addStretch(1)

        # Right: Next Primary Button
        self.nextBtn = QPushButton("Next ›")
        self.btn_next = self.nextBtn
        self.nextBtn.setCursor(Qt.PointingHandCursor)
        self.nextBtn.setFixedHeight(40)
        self.nextBtn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                padding: 0 28px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #94A3B8;
            }
        """)
        self.nextBtn.clicked.connect(self.next_question)
        nav_layout.addWidget(self.nextBtn)

        return nav_card

    # =========================================================
    # 3. RIGHT SIDEBAR PANEL (~25% Width)
    # =========================================================
    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("card_sidebar_panel")
        sidebar.setFixedWidth(340)
        sidebar.setStyleSheet("background: transparent; border: none;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(14)

        # -----------------------------------------------------
        # Card 1: Exam Progress
        # -----------------------------------------------------
        card_progress = QFrame()
        card_progress.setObjectName("card_progress")
        card_progress.setStyleSheet("""
            QFrame#card_progress {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 14px;
            }
        """)
        progress_layout = QVBoxLayout(card_progress)
        progress_layout.setContentsMargins(18, 16, 18, 16)
        progress_layout.setSpacing(14)

        progress_title = QLabel("📊 Exam Progress")
        progress_title.setStyleSheet("""
            color: #172B4D;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        progress_layout.addWidget(progress_title)

        # Step badges / grid container
        self.step_container = QWidget()
        self.step_container.setStyleSheet("background: transparent;")
        self.questionButtonsLayout = QGridLayout(self.step_container)
        self.question_grid = self.questionButtonsLayout
        self.questionButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.questionButtonsLayout.setSpacing(8)

        self.create_question_buttons()
        progress_layout.addWidget(self.step_container)

        # Status Legend Row
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(8)

        self.legendAnswered = QLabel("● Answered (0)")
        self.legendAnswered.setStyleSheet("color: #16B364; font-size: 11px; font-weight: 600;")
        self.legendCurrent = QLabel("● Current (1)")
        self.legendCurrent.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 600;")
        self.legendNotAnswered = QLabel("● Not Answered (0)")
        self.legendNotAnswered.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600;")

        legend_layout.addWidget(self.legendAnswered)
        legend_layout.addWidget(self.legendCurrent)
        legend_layout.addWidget(self.legendNotAnswered)

        progress_layout.addLayout(legend_layout)
        sidebar_layout.addWidget(card_progress)

        # -----------------------------------------------------
        # Card 2: Live Proctoring
        # -----------------------------------------------------
        card_proctoring = QFrame()
        card_proctoring.setObjectName("card_proctoring")
        card_proctoring.setStyleSheet("""
            QFrame#card_proctoring {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 14px;
            }
        """)
        proctoring_layout = QVBoxLayout(card_proctoring)
        proctoring_layout.setContentsMargins(18, 14, 18, 14)
        proctoring_layout.setSpacing(10)

        proctor_header_hbox = QHBoxLayout()
        proctor_title = QLabel("🔴 Live Proctoring")
        proctor_title.setStyleSheet("""
            color: #172B4D;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        proctor_header_hbox.addWidget(proctor_title)
        proctor_header_hbox.addStretch(1)

        live_badge = QLabel("📹 Live")
        live_badge.setStyleSheet("""
            color: #2563EB;
            background-color: #EFF6FF;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid #DBEAFE;
        """)
        proctor_header_hbox.addWidget(live_badge)
        proctoring_layout.addLayout(proctor_header_hbox)

        # Camera Display Label
        self.cameraLabel = QLabel("Initializing Camera...")
        self.camera_feed_label = self.cameraLabel
        self.webcam_label = self.cameraLabel
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setMinimumSize(270, 150)
        self.cameraLabel.setMaximumHeight(165)
        self.cameraLabel.setStyleSheet("""
            QLabel {
                background-color: #0F172A;
                color: #94A3B8;
                border-radius: 8px;
                border: none;
            }
        """)
        proctoring_layout.addWidget(self.cameraLabel)

        # Dynamic AI Detection Banner
        self.detectionStatus = QLabel("● Face Detected")
        self.status_label = self.detectionStatus
        self.detectionStatus.setAlignment(Qt.AlignCenter)
        self.detectionStatus.setStyleSheet("""
            QLabel {
                padding: 6px 12px;
                background-color: #E9FFF3;
                border: 1px solid #A6F4C5;
                border-radius: 6px;
                color: #16B364;
                font-size: 12px;
                font-weight: 700;
            }
        """)
        proctoring_layout.addWidget(self.detectionStatus)

        sidebar_layout.addWidget(card_proctoring)

        # -----------------------------------------------------
        # Card 3: Exam Status & Submit
        # -----------------------------------------------------
        card_status = QFrame()
        card_status.setObjectName("card_status")
        card_status.setStyleSheet("""
            QFrame#card_status {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 14px;
            }
        """)
        status_layout = QVBoxLayout(card_status)
        status_layout.setContentsMargins(18, 14, 18, 16)
        status_layout.setSpacing(10)

        status_title = QLabel("🛡 Exam Status")
        status_title.setStyleSheet("""
            color: #172B4D;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        status_layout.addWidget(status_title)

        for check_text in [
            "✔  Auto-save enabled",
            "✔  Connection stable",
            "✔  Camera shared automatically"
        ]:
            item_lbl = QLabel(check_text)
            item_lbl.setStyleSheet("""
                color: #334155;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
            """)
            status_layout.addWidget(item_lbl)

        # Summary Pill Strip
        self.sidebarSummaryStrip = QLabel("ℹ  0 questions answered  •  0 unanswered")
        self.submissionSummaryLabel = self.sidebarSummaryStrip
        self.sidebarSummaryStrip.setStyleSheet("""
            QLabel {
                background-color: #EFF6FF;
                border: 1px solid #DBEAFE;
                border-radius: 8px;
                color: #1D4ED8;
                font-size: 11px;
                font-weight: 600;
                padding: 8px 10px;
            }
        """)
        status_layout.addWidget(self.sidebarSummaryStrip)

        # Primary Submit Exam Button
        self.submitBtn = QPushButton("SUBMIT EXAM")
        self.btn_submit = self.submitBtn
        self.submitBtn.setFixedHeight(44)
        self.submitBtn.setCursor(Qt.PointingHandCursor)
        self.submitBtn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 10px;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #94A3B8;
            }
        """)
        self.submitBtn.clicked.connect(self.submit_exam)
        status_layout.addWidget(self.submitBtn)

        sidebar_layout.addWidget(card_status)
        sidebar_layout.addStretch(1)

        return sidebar

    # =========================================================
    # 5. APPLICATION FOOTER
    # =========================================================
    def _build_app_footer(self):
        footer = QFrame()
        footer.setObjectName("app_footer")
        footer.setFixedHeight(30)
        footer.setStyleSheet("""
            QFrame#app_footer {
                background-color: #F5F8FC;
                border-top: 1px solid #E2E8F0;
            }
        """)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 0, 24, 0)

        left_lbl = QLabel("🛡 AI Powered Exam Monitoring System")
        left_lbl.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        layout.addWidget(left_lbl)

        layout.addStretch(1)

        right_lbl = QLabel("✨ Good Luck!")
        right_lbl.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        layout.addWidget(right_lbl)

        return footer

    # =========================================================
    # GLOBAL QSS THEME
    # =========================================================
    def _apply_qss_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F8FC;
                color: #172B4D;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #D9E3F0;
                border-radius: 12px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    # =========================================================
    # CREATE QUESTION PALETTE BUTTONS
    # =========================================================
    def create_question_buttons(self):
        self.paletteButtons = []
        total = len(self.questions)

        # Clear existing layout
        while self.questionButtonsLayout.count():
            item = self.questionButtonsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Step-based chain layout when questions <= 6
        if 0 < total <= 6:
            for i in range(total):
                btn = QPushButton(f"{i + 1:02d}")
                btn.setFixedSize(36, 36)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, idx=i: self.go_to_question(idx))
                self.questionButtonsLayout.addWidget(btn, 0, i * 2, Qt.AlignCenter)
                self.paletteButtons.append(btn)

                # Connecting horizontal line between steps
                if i < total - 1:
                    line = QFrame()
                    line.setFixedHeight(2)
                    line.setStyleSheet("background-color: #D9E3F0; border: none;")
                    self.questionButtonsLayout.addWidget(line, 0, i * 2 + 1, Qt.AlignVCenter)
        else:
            # 5-Column Grid layout for larger question sets
            for i in range(total):
                btn = QPushButton(f"{i + 1:02d}")
                btn.setFixedSize(42, 38)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, idx=i: self.go_to_question(idx))
                row = i // 5
                col = i % 5
                self.questionButtonsLayout.addWidget(btn, row, col, Qt.AlignCenter)
                self.paletteButtons.append(btn)

        self.update_question_buttons_state()

    # =========================================================
    # UPDATE QUESTION PALETTE BUTTONS STATE
    # =========================================================
    def update_question_buttons_state(self):
        for i, button in enumerate(self.paletteButtons):
            question_id = self.questions[i][2] if i < len(self.questions) else None
            is_current = (i == self.current_question_index)
            is_flagged = (i in self.flagged_questions)
            is_answered = (question_id in self.answers)

            if is_current:
                button.setText(f"{i + 1:02d}")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2563EB;
                        color: #FFFFFF;
                        font-weight: 700;
                        font-size: 12px;
                        border: 2px solid #1D4ED8;
                        border-radius: 18px;
                    }
                """)
            elif is_flagged:
                button.setText(f"{i + 1:02d}🚩")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FEE2E2;
                        color: #DC2626;
                        font-weight: 700;
                        font-size: 11px;
                        border: 1px solid #FCA5A5;
                        border-radius: 18px;
                    }
                    QPushButton:hover {
                        background-color: #FECDD3;
                    }
                """)
            elif is_answered:
                button.setText(f"{i + 1:02d}")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #E9FFF3;
                        color: #16B364;
                        font-weight: 700;
                        font-size: 12px;
                        border: 1px solid #A6F4C5;
                        border-radius: 18px;
                    }
                    QPushButton:hover {
                        background-color: #D1FADF;
                    }
                """)
            else:
                button.setText(f"{i + 1:02d}")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #F1F5F9;
                        color: #64748B;
                        font-weight: 600;
                        font-size: 12px;
                        border: 1px solid #D9E3F0;
                        border-radius: 18px;
                    }
                    QPushButton:hover {
                        background-color: #E2E8F0;
                        border-color: #CBD5E1;
                    }
                """)

    # =========================================================
    # UPDATE HEADER PROGRESS & SUMMARY
    # =========================================================
    def update_header_progress(self):
        total = len(self.questions)
        answered = len(self.answers)
        flagged = len(self.flagged_questions)
        unanswered = max(0, total - answered)
        percent = int((answered / total) * 100) if total > 0 else 0

        # Header progress bar and tracker
        self.progressBar.setRange(0, max(1, total))
        self.progressBar.setValue(answered)
        self.progressTextLabel.setText(
            f"Question {self.current_question_index + 1} of {total}  |  {percent}% Completed"
        )

        # Question card number badge
        self.questionNumberBadge.setText(str(self.current_question_index + 1))

        # Footer dynamic status badges
        self.footerAnsweredLabel.setText(f"✔ {answered} answered")
        self.footerFlaggedLabel.setText(f"🚩 {flagged} flagged")
        self.footerRemainingLabel.setText(f"○ {unanswered} remaining")

        # Sidebar Card 1 legend counts
        self.legendAnswered.setText(f"● Answered ({answered})")
        self.legendCurrent.setText("● Current (1)")
        self.legendNotAnswered.setText(f"● Not Answered ({unanswered})")

        # Sidebar Card 3 summary pill strip
        self.sidebarSummaryStrip.setText(f"ℹ  {answered} questions answered  •  {unanswered} unanswered")

    # =========================================================
    # OPTION CARDS SELECTION STYLES
    # =========================================================
    def update_option_card_styles(self):
        self.cardOptionA.setSelected(self.optionA.isChecked())
        self.cardOptionB.setSelected(self.optionB.isChecked())
        self.cardOptionC.setSelected(self.optionC.isChecked())
        self.cardOptionD.setSelected(self.optionD.isChecked())

    def on_option_selected(self):
        self.update_option_card_styles()
        self.save_current_answer()
        self.update_question_buttons_state()
        self.update_header_progress()

    # =========================================================
    # FLAG & CLEAR ACTIONS
    # =========================================================
    def toggle_flag_current_question(self):
        if not self.questions:
            return

        if self.current_question_index in self.flagged_questions:
            self.flagged_questions.remove(self.current_question_index)
            self.flagBtn.setText("⚐ Flag Question")
            self.flagBtn.setStyleSheet("""
                QPushButton {
                    background-color: #EFF6FF;
                    border: 1px solid #BFDBFE;
                    border-radius: 8px;
                    color: #2563EB;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                }
            """)
        else:
            self.flagged_questions.add(self.current_question_index)
            self.flagBtn.setText("⚑ Flagged")
            self.flagBtn.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    border: 1px solid #FCA5A5;
                    border-radius: 8px;
                    color: #DC2626;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #FECDD3;
                }
            """)

        self.update_question_buttons_state()
        self.update_header_progress()

    def clear_current_answer(self):
        if not self.questions:
            return

        self.optionGroup.setExclusive(False)
        for opt in [self.optionA, self.optionB, self.optionC, self.optionD]:
            opt.setChecked(False)
        self.optionGroup.setExclusive(True)

        question = self.questions[self.current_question_index]
        question_id = question[2]
        self.answers.pop(question_id, None)

        if self.attempt_id is not None:
            try:
                QuestionModel.save_student_answer(self.attempt_id, question_id, None)
            except Exception:
                pass

        self.update_option_card_styles()
        self.update_question_buttons_state()
        self.update_header_progress()

    # =========================================================
    # SHOW QUESTION
    # =========================================================
    def show_question(self, index):
        if not self.questions:
            return

        if index < 0 or index >= len(self.questions):
            return

        self.current_question_index = index
        question = self.questions[index]

        # Question Data
        question_id = question[2]
        question_text = question[4]
        option_a = question[5] or ""
        option_b = question[6] or ""
        option_c = question[7] or ""
        option_d = question[8] or ""

        # Marks and Subject
        marks = question[9] if len(question) > 9 and question[9] is not None else 1
        subject_name = str(self.exam.get("subject_name", "Mathematics") if hasattr(self.exam, "get") else "Mathematics")

        self.examSubtitleLabel.setText(f"{subject_name}  •  {marks} Mark{'s' if marks != 1 else ''}")
        self.metadataLabel.setText(f"📖 {subject_name}  •  {marks} Mark{'s' if marks != 1 else ''}")
        self.questionTextLabel.setText(str(question_text))

        # Update Options
        self.optionA.setText(f"A.   {option_a}")
        self.optionB.setText(f"B.   {option_b}")
        self.optionC.setText(f"C.   {option_c}")
        self.optionD.setText(f"D.   {option_d}")

        # Show/Hide options if empty
        self.cardOptionC.setVisible(bool(str(option_c).strip()))
        self.cardOptionD.setVisible(bool(str(option_d).strip()))

        # Reset selection state
        self.optionGroup.setExclusive(False)
        for option in [self.optionA, self.optionB, self.optionC, self.optionD]:
            option.setChecked(False)
        self.optionGroup.setExclusive(True)

        # Restore saved answer
        saved_answer = self.answers.get(question_id)
        if saved_answer == "A":
            self.optionA.setChecked(True)
        elif saved_answer == "B":
            self.optionB.setChecked(True)
        elif saved_answer == "C":
            self.optionC.setChecked(True)
        elif saved_answer == "D":
            self.optionD.setChecked(True)

        self.update_option_card_styles()

        # Update Flag button style
        if index in self.flagged_questions:
            self.flagBtn.setText("⚑ Flagged")
            self.flagBtn.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    border: 1px solid #FCA5A5;
                    border-radius: 8px;
                    color: #DC2626;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #FECDD3;
                }
            """)
        else:
            self.flagBtn.setText("⚐ Flag Question")
            self.flagBtn.setStyleSheet("""
                QPushButton {
                    background-color: #EFF6FF;
                    border: 1px solid #BFDBFE;
                    border-radius: 8px;
                    color: #2563EB;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                }
            """)

        # Button states
        self.previousBtn.setEnabled(index > 0)
        if index == len(self.questions) - 1:
            self.nextBtn.setText("Save")
        else:
            self.nextBtn.setText("Next ›")

        # Update overall states
        self.update_question_buttons_state()
        self.update_header_progress()

    # =========================================================
    # SAVE CURRENT ANSWER (PRESERVED BACKEND LOGIC)
    # =========================================================
    def save_current_answer(self):
        if not self.questions:
            return

        if self.attempt_id is None:
            print(">>> ERROR: No exam attempt ID.")
            return

        question = self.questions[self.current_question_index]
        question_id = question[2]

        selected_button = self.optionGroup.checkedButton()

        if selected_button is None:
            self.answers.pop(question_id, None)
            self.update_question_buttons_state()
            self.update_header_progress()
            return

        button_id = self.optionGroup.id(selected_button)
        option_map = {1: "A", 2: "B", 3: "C", 4: "D"}
        answer = option_map.get(button_id)

        if answer is None:
            return

        self.answers[question_id] = answer

        success = QuestionModel.save_student_answer(
            self.attempt_id,
            question_id,
            answer
        )

        if success:
            print(">>> Student answer saved: Attempt:", self.attempt_id, "Question:", question_id, "Answer:", answer)
        else:
            print(">>> ERROR: Failed to save student answer:", question_id, answer)

        self.update_question_buttons_state()
        self.update_header_progress()

    # =========================================================
    # NAVIGATION METHODS
    # =========================================================
    def next_question(self):
        self.save_current_answer()

        if self.current_question_index < len(self.questions) - 1:
            self.show_question(self.current_question_index + 1)
        else:
            QMessageBox.information(
                self,
                "Exam",
                "You are on the last question."
            )

    def previous_question(self):
        self.save_current_answer()

        if self.current_question_index > 0:
            self.show_question(self.current_question_index - 1)

    def go_to_question(self, index):
        self.save_current_answer()
        self.show_question(index)

    # =========================================================
    # NO QUESTIONS ASSIGNED
    # =========================================================
    def show_no_questions_message(self):
        self.progressTextLabel.setText("No Questions Assigned")
        self.questionTextLabel.setText("There are currently no questions assigned to this examination.")

        for option in [self.optionA, self.optionB, self.optionC, self.optionD]:
            option.setDisabled(True)

        self.nextBtn.setDisabled(True)
        self.previousBtn.setDisabled(True)
        self.submitBtn.setDisabled(True)

    # =========================================================
    # TIME FORMATTING & COUNTDOWN
    # =========================================================
    def update_time_label(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        if hours > 0:
            time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_text = f"{minutes:02d}:{seconds:02d}"

        self.headerTimeLabel.setText(time_text)

    def update_countdown(self):
        if self.remaining_seconds <= 0:
            self.examTimer.stop()
            self.headerTimeLabel.setText("00:00")
            self.submit_exam(automatic=True)
            return

        self.remaining_seconds -= 1
        self.update_time_label()

    # =========================================================
    # SUBMIT EXAM (Modern Confirmation Modal + Backend Submission)
    # =========================================================
    def submit_exam(self, automatic=False):
        self.save_current_answer()

        if automatic:
            QMessageBox.information(
                self,
                "Time Expired",
                "The examination time has expired. Your examination will now be submitted."
            )
        else:
            total = len(self.questions)
            answered = len(self.answers)
            unanswered = max(0, total - answered)

            dialog = SubmitConfirmDialog(unanswered=unanswered, parent=self)
            if dialog.exec_() != QDialog.Accepted:
                return

        # Stop exam timers & streaming
        self.examTimer.stop()
        self.cameraTimer.stop()
        self.camera_streamer.stop()

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        # Submit attempt to database
        if self.attempt_id is not None:
            score = QuestionModel.submit_exam_attempt(self.attempt_id)
            if score is None:
                QMessageBox.warning(
                    self,
                    "Submission Error",
                    "There was a problem submitting your examination."
                )
                return

            print(">>> EXAM SUBMITTED. Attempt ID:", self.attempt_id, "Final Score:", score)
        else:
            print(">>> ERROR: No exam attempt ID.")
            QMessageBox.warning(
                self,
                "Submission Error",
                "The examination attempt could not be found."
            )
            return

        QMessageBox.information(
            self,
            "Examination Submitted",
            "Your examination has been submitted successfully."
        )
        self.close()

    # =========================================================
    # CAMERA (PRESERVED BACKEND LOGIC)
    # =========================================================
    def start_camera(self):
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            self.cameraLabel.setText("Unable to access webcam")
            return

        self.cameraTimer.start(30)

    def update_camera(self):
        if self.camera is None:
            return

        success, frame = self.camera.read()
        if not success:
            return

        frame = cv2.flip(frame, 1)
        self.current_frame = frame.copy()

        self.camera_streamer.update_frame(self.current_frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        image = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        target_w = max(1, self.cameraLabel.width())
        target_h = max(1, self.cameraLabel.height())

        self.cameraLabel.setPixmap(
            pixmap.scaled(
                target_w,
                target_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # =========================================================
    # START AI MONITORING (PRESERVED BACKEND LOGIC)
    # =========================================================
    def start_ai_monitoring(self):
        if self.ai_monitor is None:
            print(">>> AI monitor unavailable.")
            self.detectionStatus.setText("● AI Monitoring Unavailable")
            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #FEF2F2;
                    border: 1px solid #FCA5A5;
                    border-radius: 6px;
                    color: #991B1B;
                    font-size: 12px;
                    font-weight: 700;
                }
            """)
            return

        try:
            self.ai_monitor.start()
            self.aiTimer.start(250)
            self.detectionStatus.setText("● AI Monitoring Active")
            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #E9FFF3;
                    border: 1px solid #A6F4C5;
                    border-radius: 6px;
                    color: #16B364;
                    font-size: 12px;
                    font-weight: 700;
                }
            """)
            print(">>> AI monitoring started.")
        except Exception as e:
            print(">>> AI start error:", e)
            self.detectionStatus.setText("● AI Monitoring Error")
            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #FEF2F2;
                    border: 1px solid #FCA5A5;
                    border-radius: 6px;
                    color: #991B1B;
                    font-size: 12px;
                    font-weight: 700;
                }
            """)

    # =========================================================
    # PROCESS AI MONITORING (PRESERVED BACKEND LOGIC)
    # =========================================================
    def process_ai_monitoring(self):
        if self.ai_monitor is None or self.camera is None or self.ai_processing:
            return

        self.ai_processing = True

        try:
            frame = getattr(self, "current_frame", None)
            if frame is None:
                return

            self.ai_monitor.process_frame(frame)
            status = self.ai_monitor.get_status()

            if status.get("multiple_faces", False):
                self.show_detection_status("● Multiple Faces Detected", "violation")
            elif not status.get("face_present", True):
                self.show_detection_status("● Face Disappeared", "violation")
            elif status.get("forbidden_object", False):
                self.show_detection_status("● Forbidden Object Detected", "violation")
            elif status.get("mouth_movement", False):
                self.show_detection_status("● Mouth Movement Detected", "warning")
            elif status.get("eye_movement", False):
                self.show_detection_status("● Eye Movement Detected", "warning")
            elif status.get("voice_detected", False):
                self.show_detection_status("● Voice Detected", "warning")
            else:
                self.show_detection_status("● Face Detected", "normal")

        except Exception as e:
            print(">>> AI frame processing error:", e)
        finally:
            self.ai_processing = False

    # =========================================================
    # UPDATE DYNAMIC DETECTION STATUS (MODERN STYLES)
    # =========================================================
    def show_detection_status(self, message, status_type="normal"):
        self.detectionStatus.setText(message)

        if status_type == "normal":
            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #E9FFF3;
                    border: 1px solid #A6F4C5;
                    border-radius: 6px;
                    color: #16B364;
                    font-size: 12px;
                    font-weight: 700;
                }
            """)
        elif status_type == "warning":
            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #FFFBEB;
                    border: 1px solid #FCD34D;
                    border-radius: 6px;
                    color: #92400E;
                    font-size: 12px;
                    font-weight: 700;
                }
            """)
        elif status_type == "violation":
            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #FEF2F2;
                    border: 1px solid #FCA5A5;
                    border-radius: 6px;
                    color: #991B1B;
                    font-size: 12px;
                    font-weight: 700;
                }
            """)

    # =========================================================
    # STOP AI MONITORING (PRESERVED BACKEND LOGIC)
    # =========================================================
    def stop_ai_monitoring(self):
        self.aiTimer.stop()
        if self.ai_monitor is not None:
            try:
                self.ai_monitor.stop()
            except Exception as e:
                print(">>> AI stop error:", e)
        print(">>> AI monitoring stopped.")

    # =========================================================
    # CLOSE EVENT (PRESERVED CLEANUP LOGIC)
    # =========================================================
    def closeEvent(self, event):
        self.cameraTimer.stop()
        self.examTimer.stop()
        self.stop_ai_monitoring()
        self.camera_streamer.stop()

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        event.accept()