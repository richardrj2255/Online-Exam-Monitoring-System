import torch
import cv2

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QScrollArea,
)

from PyQt5.QtGui import (
    QFont,
    QImage,
    QPixmap,
)

from PyQt5.QtCore import (
    Qt,
    QTimer,
)

from models.question_model import QuestionModel
from ai.ai_monitoring import ExamAIMonitor
from streaming.camera_stream import CameraStreamer


class MonitoringPage(QWidget):

    def __init__(self, student, exam):

        super().__init__()

        self.student = student
        self.exam = exam

        self.attempt_id = None

        try:
            self.attempt_id = QuestionModel.create_exam_attempt(
                self.student["id"],
                self.exam["id"]
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Examination Already Completed",
                str(e)
            )

            self.attempt_id = None

    # Prevent the examination UI from continuing
            QTimer.singleShot(0, self.close)
            return

        # =====================================================
        # QUESTIONS
        # =====================================================

        self.questions = []

        self.current_question_index = 0

        # Stores selected answers.
        #
        # Example:
        # {
        #     question_id: "A",
        #     question_id: "C"
        # }
        #
        self.answers = {}

        # =====================================================
        # CAMERA
        # =====================================================

        self.camera = None
        self.camera_streamer = CameraStreamer(
            register_no=self.student["register_no"],
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

        self.aiTimer.timeout.connect(
            self.process_ai_monitoring
        )

        self.ai_processing = False

        try:

            self.ai_monitor = ExamAIMonitor(
                self.student["register_no"],
                screenshot_dir="captured/ai"
            )

            print(
                ">>> AI monitoring engine initialized."
            )

        except Exception as e:

            print(
                ">>> AI monitoring initialization failed:",
                e
            )

        
        self.cameraTimer = QTimer()
        self.cameraTimer.timeout.connect(
            self.update_camera
        )

        # =====================================================
        # EXAM TIMER
        # =====================================================

        self.remaining_seconds = (
            int(exam["duration"]) * 60
        )

        self.examTimer = QTimer()
        self.examTimer.timeout.connect(
            self.update_countdown
        )

        # =====================================================
        # LOAD QUESTIONS
        # =====================================================

        self.load_questions()

        # =====================================================
        # UI
        # =====================================================

        self.setupUI()

        # =====================================================
        # START CAMERA
        # =====================================================

        self.start_camera()
        self.camera_streamer.start()
        # =====================================================
        # START AI MONITORING
        # =====================================================

        self.start_ai_monitoring()

        # =====================================================
        # START TIMER
        # =====================================================

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

            self.questions = (
                QuestionModel.get_questions_for_exam(
                    self.exam["id"]
                )
            )

        except Exception as e:

            print(
                "Error loading exam questions:",
                e
            )

            self.questions = []

    # =========================================================
    # UI
    # =========================================================

    def setupUI(self):

        self.setWindowTitle(
            "Online Examination"
        )

        self.showMaximized()

        self.setStyleSheet("""
            QWidget {
                background:#eef3f8;
                font-family:Arial;
            }

            QFrame {
                background:white;
                border:1px solid #d9dee5;
                border-radius:12px;
            }

            QLabel {
                color:#1f2937;
            }

            QPushButton {
                background:#2563eb;
                color:white;
                border:none;
                border-radius:7px;
                padding:10px 18px;
                font-size:13px;
            }

            QPushButton:hover {
                background:#1d4ed8;
            }

            QPushButton:disabled {
                background:#9ca3af;
            }

            QRadioButton {
                background:white;
                padding:12px;
                font-size:14px;
            }
        """)

        mainLayout = QVBoxLayout()

        mainLayout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        mainLayout.setSpacing(12)

        # =====================================================
        # HEADER
        # =====================================================

        header = QFrame()

        headerLayout = QHBoxLayout()

        title = QLabel(
            "ONLINE EXAMINATION"
        )

        title.setFont(
            QFont(
                "Arial",
                20,
                QFont.Bold
            )
        )

        examTitle = QLabel(
            str(self.exam["exam_name"])
        )

        examTitle.setFont(
            QFont(
                "Arial",
                13,
                QFont.Bold
            )
        )

        self.headerTimeLabel = QLabel(
            "00:00:00"
        )

        self.headerTimeLabel.setFont(
            QFont(
                "Arial",
                16,
                QFont.Bold
            )
        )

        self.headerTimeLabel.setStyleSheet(
            "color:#dc2626;"
        )

        headerLayout.addWidget(
            title
        )

        headerLayout.addSpacing(20)

        headerLayout.addWidget(
            examTitle
        )

        headerLayout.addStretch()

        headerLayout.addWidget(
            QLabel("TIME REMAINING")
        )

        headerLayout.addWidget(
            self.headerTimeLabel
        )

        header.setLayout(
            headerLayout
        )

        # =====================================================
        # STUDENT INFO
        # =====================================================

        infoFrame = QFrame()

        infoLayout = QHBoxLayout()

        studentInfo = QLabel(
            f"""
Student: {self.student["name"]}
Register No: {self.student["register_no"]}
Department: {self.student["department"]}
Semester: {self.student["semester"]}
"""
        )

        studentInfo.setFont(
            QFont(
                "Arial",
                10
            )
        )

        subjectInfo = QLabel(
            f"""
Subject: {self.exam["subject_name"]}
Subject Code: {self.exam["subject_code"]}
"""
        )

        subjectInfo.setFont(
            QFont(
                "Arial",
                10
            )
        )

        infoLayout.addWidget(
            studentInfo
        )

        infoLayout.addStretch()

        infoLayout.addWidget(
            subjectInfo
        )

        infoFrame.setLayout(
            infoLayout
        )

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        contentLayout = QHBoxLayout()

        # =====================================================
        # QUESTION AREA
        # =====================================================

        questionFrame = QFrame()

        questionLayout = QVBoxLayout()

        # -----------------------------------------------------
        # Question header
        # -----------------------------------------------------

        self.questionNumberLabel = QLabel(
            "Question 1"
        )

        self.questionNumberLabel.setFont(
            QFont(
                "Arial",
                17,
                QFont.Bold
            )
        )

        questionLayout.addWidget(
            self.questionNumberLabel
        )

        # -----------------------------------------------------
        # Question text
        # -----------------------------------------------------

        self.questionTextLabel = QLabel(
            ""
        )

        self.questionTextLabel.setWordWrap(
            True
        )

        self.questionTextLabel.setFont(
            QFont(
                "Arial",
                15
            )
        )

        self.questionTextLabel.setMinimumHeight(
            100
        )

        questionLayout.addWidget(
            self.questionTextLabel
        )

        # -----------------------------------------------------
        # Options
        # -----------------------------------------------------

        self.optionA = QRadioButton()
        self.optionB = QRadioButton()
        self.optionC = QRadioButton()
        self.optionD = QRadioButton()

        self.optionGroup = QButtonGroup(
            self
        )

        self.optionGroup.addButton(
            self.optionA,
            1
        )

        self.optionGroup.addButton(
            self.optionB,
            2
        )

        self.optionGroup.addButton(
            self.optionC,
            3
        )

        self.optionGroup.addButton(
            self.optionD,
            4
        )

        for option in [
            self.optionA,
            self.optionB,
            self.optionC,
            self.optionD
        ]:

            option.setMinimumHeight(
                45
            )

            questionLayout.addWidget(
                option
            )

        questionLayout.addStretch()

        # -----------------------------------------------------
        # Navigation
        # -----------------------------------------------------

        navigationLayout = QHBoxLayout()

        self.previousBtn = QPushButton(
            "← Previous"
        )

        self.nextBtn = QPushButton(
            "Save & Next →"
        )

        self.submitBtn = QPushButton(
            "Submit Exam"
        )

        self.previousBtn.clicked.connect(
            self.previous_question
        )

        self.nextBtn.clicked.connect(
            self.next_question
        )

        self.submitBtn.clicked.connect(
            self.submit_exam
        )

        navigationLayout.addWidget(
            self.previousBtn
        )

        navigationLayout.addStretch()

        navigationLayout.addWidget(
            self.nextBtn
        )

        navigationLayout.addSpacing(10)

        navigationLayout.addWidget(
            self.submitBtn
        )

        questionLayout.addLayout(
            navigationLayout
        )

        questionFrame.setLayout(
            questionLayout
        )

        # =====================================================
        # MONITORING PANEL
        # =====================================================

        monitoringFrame = QFrame()

        monitoringLayout = QVBoxLayout()

        monitoringTitle = QLabel(
            "🎥 Exam Monitoring"
        )

        monitoringTitle.setFont(
            QFont(
                "Arial",
                15,
                QFont.Bold
            )
        )

        monitoringLayout.addWidget(
            monitoringTitle
        )

        # -----------------------------------------------------
        # Camera
        # -----------------------------------------------------

        self.cameraLabel = QLabel(
            "Initializing Camera..."
        )

        self.cameraLabel.setAlignment(
            Qt.AlignCenter
        )

        self.cameraLabel.setMinimumSize(
            300,
            220
        )

        self.cameraLabel.setMaximumHeight(
            280
        )

        self.cameraLabel.setStyleSheet("""
            QLabel {
                background:black;
                color:white;
                border-radius:10px;
            }
        """)

        monitoringLayout.addWidget(
            self.cameraLabel
        )

        # -----------------------------------------------------
        # Dynamic AI Detection Status
        # -----------------------------------------------------

        self.detectionStatus = QLabel(
            "🟢 Face Detected"
        )

        self.detectionStatus.setFont(
            QFont(
                "Arial",
                11,
                QFont.Bold
            )
        )

        self.detectionStatus.setAlignment(
            Qt.AlignCenter
        )

        self.detectionStatus.setStyleSheet("""
            QLabel {
                padding:12px;
                background:#ecfdf5;
                border:1px solid #86efac;
                border-radius:8px;
                color:#166534;
            }
        """)

        monitoringLayout.addWidget(
            self.detectionStatus
        )

        monitoringLayout.addStretch()

        monitoringFrame.setLayout(
            monitoringLayout
        )

        # =====================================================
        # ADD MAIN AREAS
        # =====================================================

        contentLayout.addWidget(
            questionFrame,
            3
        )

        contentLayout.addWidget(
            monitoringFrame,
            1
        )

        # =====================================================
        # QUESTION NAVIGATION
        # =====================================================

        questionNavFrame = QFrame()

        questionNavLayout = QVBoxLayout()

        questionNavTitle = QLabel(
            "Questions"
        )

        questionNavTitle.setFont(
            QFont(
                "Arial",
                13,
                QFont.Bold
            )
        )

        questionNavLayout.addWidget(
            questionNavTitle
        )

        # Scroll area for question buttons

        scrollArea = QScrollArea()

        scrollArea.setWidgetResizable(
            True
        )

        scrollWidget = QWidget()

        self.questionButtonsLayout = QHBoxLayout()

        self.create_question_buttons()

        scrollWidget.setLayout(
            self.questionButtonsLayout
        )

        scrollArea.setWidget(
            scrollWidget
        )

        questionNavLayout.addWidget(
            scrollArea
        )

        questionNavFrame.setLayout(
            questionNavLayout
        )

        # =====================================================
        # ADD EVERYTHING
        # =====================================================

        mainLayout.addWidget(
            header
        )

        mainLayout.addWidget(
            infoFrame
        )

        mainLayout.addLayout(
            contentLayout
        )

        mainLayout.addWidget(
            questionNavFrame
        )

        self.setLayout(
            mainLayout
        )

        # =====================================================
        # INITIAL TIMER
        # =====================================================

        self.update_time_label()

    # =========================================================
    # CREATE QUESTION BUTTONS
    # =========================================================

    def create_question_buttons(self):

        for i in range(
            len(self.questions)
        ):

            button = QPushButton(
                str(i + 1)
            )

            button.setFixedSize(
                45,
                40
            )

            button.clicked.connect(
                lambda checked,
                index=i:
                self.go_to_question(index)
            )

            self.questionButtonsLayout.addWidget(
                button
            )

    # =========================================================
    # SHOW QUESTION
    # =========================================================

    def show_question(self, index):

        if not self.questions:

            return

        if index < 0 or index >= len(
            self.questions
        ):

            return

        self.current_question_index = index

        question = self.questions[index]

        # =====================================================
        # QUESTION DATA
        # =====================================================

        question_id = question[2]

        question_text = question[4]

        option_a = question[5]
        option_b = question[6]
        option_c = question[7]
        option_d = question[8]

        # =====================================================
        # QUESTION NUMBER
        # =====================================================

        self.questionNumberLabel.setText(
            f"Question {index + 1} of {len(self.questions)}"
        )

        # =====================================================
        # QUESTION TEXT
        # =====================================================

        self.questionTextLabel.setText(
            question_text
        )

        # =====================================================
        # OPTIONS
        # =====================================================

        self.optionA.setText(
            f"A. {option_a}"
        )

        self.optionB.setText(
            f"B. {option_b}"
        )

        self.optionC.setText(
            f"C. {option_c}"
        )

        self.optionD.setText(
            f"D. {option_d}"
        )

        # =====================================================
        # CLEAR CURRENT SELECTION
        # =====================================================

        self.optionGroup.setExclusive(
            False
        )

        for option in [
            self.optionA,
            self.optionB,
            self.optionC,
            self.optionD
        ]:

            option.setChecked(
                False
            )

        self.optionGroup.setExclusive(
            True
        )

        # =====================================================
        # RESTORE SAVED ANSWER
        # =====================================================

        saved_answer = self.answers.get(
            question_id
        )

        if saved_answer == "A":
            self.optionA.setChecked(True)

        elif saved_answer == "B":
            self.optionB.setChecked(True)

        elif saved_answer == "C":
            self.optionC.setChecked(True)

        elif saved_answer == "D":
            self.optionD.setChecked(True)

        # =====================================================
        # BUTTON STATES
        # =====================================================

        self.previousBtn.setEnabled(
            index > 0
        )

        if index == len(self.questions) - 1:

            self.nextBtn.setText(
                "Save"
            )

        else:

            self.nextBtn.setText(
                "Save & Next →"
            )

# =========================================================
# SAVE CURRENT ANSWER
# =========================================================

    def save_current_answer(self):

        if not self.questions:

            return

        if self.attempt_id is None:

            print(
                ">>> ERROR: No exam attempt ID."
            )

            return

        question = self.questions[
            self.current_question_index
        ]

        question_id = question[2]

        selected_button = (
            self.optionGroup.checkedButton()
        )

    # -----------------------------------------------------
    # No answer selected
    # -----------------------------------------------------

        if selected_button is None:

            self.answers.pop(
                question_id,
                None
            )

            print(
                ">>> No answer selected for question:",
                question_id
            )

            return

    # -----------------------------------------------------
    # Convert button ID to option letter
    # -----------------------------------------------------

        button_id = (
            self.optionGroup.id(
                selected_button
            )
        )

        option_map = {
            1: "A",
            2: "B",
            3: "C",
            4: "D"
        }

        answer = option_map.get(
            button_id
        )

        if answer is None:

            return

    # -----------------------------------------------------
    # Store locally
    # -----------------------------------------------------

        self.answers[
            question_id
        ] = answer

    # -----------------------------------------------------
    # SAVE TO DATABASE
    # -----------------------------------------------------

        success = (
            QuestionModel.save_student_answer(
                self.attempt_id,
                question_id,
                answer
            )
        )

        if success:

            print(
                ">>> Student answer saved:",
                "Attempt:",
                self.attempt_id,
                "Question:",
                question_id,
                "Answer:",
                answer
            )

        else:

            print(
                ">>> ERROR: Failed to save student answer:",
                question_id,
                answer
            )

    # =========================================================
    # NEXT QUESTION
    # =========================================================

    def next_question(self):

        self.save_current_answer()

        if (
            self.current_question_index
            <
            len(self.questions) - 1
        ):

            self.show_question(
                self.current_question_index + 1
            )

        else:

            QMessageBox.information(
                self,
                "Exam",
                "You are on the last question."
            )

    # =========================================================
    # PREVIOUS QUESTION
    # =========================================================

    def previous_question(self):

        self.save_current_answer()

        if self.current_question_index > 0:

            self.show_question(
                self.current_question_index - 1
            )

    # =========================================================
    # GO TO QUESTION
    # =========================================================

    def go_to_question(self, index):

        self.save_current_answer()

        self.show_question(
            index
        )

    # =========================================================
    # NO QUESTIONS
    # =========================================================

    def show_no_questions_message(self):

        self.questionNumberLabel.setText(
            "No Questions Assigned"
        )

        self.questionTextLabel.setText(
            "There are currently no questions assigned to this examination."
        )

        for option in [
            self.optionA,
            self.optionB,
            self.optionC,
            self.optionD
        ]:

            option.setDisabled(
                True
            )

        self.nextBtn.setDisabled(
            True
        )

        self.previousBtn.setDisabled(
            True
        )

    # =========================================================
    # TIME LABEL
    # =========================================================

    def update_time_label(self):

        hours = (
            self.remaining_seconds // 3600
        )

        minutes = (
            (self.remaining_seconds % 3600)
            // 60
        )

        seconds = (
            self.remaining_seconds % 60
        )

        time_text = (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        self.headerTimeLabel.setText(
            time_text
        )

    # =========================================================
    # COUNTDOWN
    # =========================================================

    def update_countdown(self):

        if self.remaining_seconds <= 0:

            self.examTimer.stop()

            self.headerTimeLabel.setText(
                "00:00:00"
            )

            self.submit_exam(
                automatic=True
            )

            return

        self.remaining_seconds -= 1

        self.update_time_label()

    # =========================================================
    # SUBMIT EXAM
    # =========================================================

    def submit_exam(
        self,
        automatic=False
    ):

        self.save_current_answer()

        if automatic:

            QMessageBox.information(
                self,
                "Time Expired",
                "The examination time has expired. Your examination will now be submitted."
            )

        else:

            reply = QMessageBox.question(
                self,
                "Submit Examination",
                "Are you sure you want to submit the examination?",
                QMessageBox.Yes |
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:

                return

        # =====================================================
        # STOP EXAM
        # =====================================================

        self.examTimer.stop()

        self.cameraTimer.stop()
        self.camera_streamer.stop()

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        # =====================================================
        # SAVE FINAL ANSWER
        # =====================================================



        # =====================================================
        # SUBMIT EXAM ATTEMPT
        # =====================================================

        if self.attempt_id is not None:

            score = (
                QuestionModel.submit_exam_attempt(
                    self.attempt_id
                )
            )

            if score is None:

                QMessageBox.warning(
                    self,
                    "Submission Error",
                    "There was a problem submitting your examination."
                )

                return

            print(
                ">>> EXAM SUBMITTED"
            )

            print(
                ">>> Attempt ID:",
                self.attempt_id
            )

            print(
                ">>> Final Score:",
                score
            )

        else:

            print(
                ">>> ERROR: No exam attempt ID."
            )

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
    # CAMERA
    # =========================================================

    def start_camera(self):

        self.camera = cv2.VideoCapture(
            0
        )

        if not self.camera.isOpened():

            self.cameraLabel.setText(
                "Unable to access webcam"
            )

            return

        self.cameraTimer.start(
            30
        )

    # =========================================================
    # UPDATE CAMERA
    # =========================================================

    def update_camera(self):

        if self.camera is None:

            return

        success, frame = (
            self.camera.read()
        )

        if not success:

            return

        frame = cv2.flip(
            frame,
            1
        )
        self.current_frame = frame.copy()

        self.camera_streamer.update_frame(
            self.current_frame
        )
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        bytes_per_line = (
            ch * w
        )

        image = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(
            image
        )

        self.cameraLabel.setPixmap(
            pixmap.scaled(
                self.cameraLabel.width(),
                self.cameraLabel.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        # =========================================================
# START AI MONITORING
# =========================================================

    def start_ai_monitoring(self):

        if self.ai_monitor is None:

            print(
                ">>> AI monitor unavailable."
            )

            self.detectionStatus.setText(
                "🔴 AI Monitoring Unavailable"
            )

            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding:12px;
                    background:#fef2f2;
                    border:1px solid #fca5a5;
                    border-radius:8px;
                    color:#991b1b;
                    font-weight:bold;
                }
            """)

            return

        try:

            self.ai_monitor.start()

        # AI processing runs separately from
        # the camera display timer.
        #
        # Camera:
        # approximately 33 FPS
        #
        # AI:
        # approximately 4 FPS

            self.aiTimer.start(
                250
            )

            self.detectionStatus.setText(
                "🟢 AI Monitoring Active"
            )

            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding:12px;
                    background:#ecfdf5;
                    border:1px solid #86efac;
                    border-radius:8px;
                    color:#166534;
                    font-weight:bold;
                }
            """)

            print(
                ">>> AI monitoring started."
            )

        except Exception as e:

            print(
                ">>> AI start error:",
                e
            )

            self.detectionStatus.setText(
                "🔴 AI Monitoring Error"
            )

            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding:12px;
                    background:#fef2f2;
                    border:1px solid #fca5a5;
                    border-radius:8px;
                    color:#991b1b;
                    font-weight:bold;
                }
            """)
    # =========================================================
# PROCESS AI MONITORING
# =========================================================

    def process_ai_monitoring(self):

        if self.ai_monitor is None:
            return

        if self.camera is None:
            return

        if self.ai_processing:
            return

        self.ai_processing = True

        try:

        # -------------------------------------------------
        # Get latest camera frame
        # -------------------------------------------------

            frame = getattr(
                self,
                "current_frame",
                None
            )

            if frame is None:
                return

        # -------------------------------------------------
        # Process frame through AI
        # -------------------------------------------------

            self.ai_monitor.process_frame(
                frame
            )

            status = (
                self.ai_monitor.get_status()
            )

        # -------------------------------------------------
        # Dynamic detection priority
        # -------------------------------------------------
        #
        # If multiple violations happen at the same
        # time, the first matching condition is displayed.
        #
        # Priority:
        #
        # 1. Multiple faces
        # 2. Face disappeared
        # 3. Forbidden object
        # 4. Mouth movement
        # 5. Eye movement
        # 6. Voice detected
        # 7. Normal face detected
        #
        # -------------------------------------------------

            if status.get("multiple_faces", False):

                self.show_detection_status(
                    "🔴 Multiple Faces Detected",
                    "violation"
                )

            elif not status.get("face_present", True):

                self.show_detection_status(
                    "🔴 Face Disappeared",
                    "violation"
                )

            elif status.get("forbidden_object", False):

                self.show_detection_status(
                    "🔴 Forbidden Object Detected",
                    "violation"
                )

            elif status.get("mouth_movement", False):

                self.show_detection_status(
                    "🟠 Mouth Movement Detected",
                    "warning"
                )

            elif status.get("eye_movement", False):

                self.show_detection_status(
                    "🟠 Eye Movement Detected",
                    "warning"
                )

            elif status.get("voice_detected", False):

                self.show_detection_status(
                    "🟠 Voice Detected",
                    "warning"
                )

            else:

                self.show_detection_status(
                    "🟢 Face Detected",
                    "normal"
                )

        except Exception as e:

            print(
                ">>> AI frame processing error:",
                e
            )

        finally:

            self.ai_processing = False
    # =========================================================
    # UPDATE DYNAMIC DETECTION STATUS
    # =========================================================

    def show_detection_status(
        self,
        message,
        status_type="normal"
    ):

        self.detectionStatus.setText(
            message
        )

        if status_type == "normal":

            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding:12px;
                    background:#ecfdf5;
                    border:1px solid #86efac;
                    border-radius:8px;
                    color:#166534;
                }
            """)

        elif status_type == "warning":

            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding:12px;
                    background:#fffbeb;
                    border:1px solid #fcd34d;
                    border-radius:8px;
                    color:#92400e;
                }
            """)

        elif status_type == "violation":

            self.detectionStatus.setStyleSheet("""
                QLabel {
                    padding:12px;
                    background:#fef2f2;
                    border:1px solid #fca5a5;
                    border-radius:8px;
                    color:#991b1b;
                }
            """)
    # =========================================================
    # STOP AI MONITORING
    # =========================================================

    def stop_ai_monitoring(self):

        self.aiTimer.stop()

        if self.ai_monitor is not None:

            try:

                self.ai_monitor.stop()

            except Exception as e:

                print(
                    ">>> AI stop error:",
                    e
                )

        print(
            ">>> AI monitoring stopped."
        )    
    # =========================================================
    # CLOSE
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