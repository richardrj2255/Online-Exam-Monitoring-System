import cv2

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QFrame,
)

from PyQt5.QtGui import (
    QFont,
    QImage,
    QPixmap,
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QObject,
)

from streaming.camera_server import CameraServer
from database.database import get_connection
from ui.qss_theme import (
    BG_CANVAS,
    BG_CARD,
    BORDER_SUBTLE,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BADGE_SUCCESS_BG,
    BADGE_SUCCESS_TEXT,
    BADGE_SUCCESS_BORDER,
    BADGE_DANGER_BG,
    BADGE_DANGER_TEXT,
    BADGE_DANGER_BORDER,
    BADGE_INFO_BG,
    BADGE_INFO_TEXT,
)


# =========================================================
# CAMERA SIGNAL BRIDGE
# =========================================================

class CameraSignalBridge(QObject):

    frame_received = pyqtSignal(str, object)
    student_disconnected = pyqtSignal(str)


# =========================================================
# STUDENT CAMERA CARD
# =========================================================

class StudentCameraCard(QFrame):

    def __init__(
        self,
        register_no,
        student_name="Unknown Student",
        subject="Unknown Subject"
    ):

        super().__init__()

        self.register_no = register_no
        self.student_name = student_name
        self.subject = subject

        self.setMinimumSize(
            440,
            380
        )

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # =================================================
        # STUDENT HEADER (Glassmorphic Ribbon)
        # =================================================

        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(12)

        # -------------------------------------------------
        # Student Avatar + Info
        # -------------------------------------------------
        avatar = QLabel("👨‍🎓")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(36, 36)
        avatar.setStyleSheet(f"""
            background-color: {BG_CANVAS};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 18px;
            font-size: 16px;
        """)

        studentInfoLayout = QVBoxLayout()
        studentInfoLayout.setSpacing(2)

        self.studentLabel = QLabel(
            self.student_name
        )
        self.studentLabel.setFont(
            QFont("Segoe UI", 12, QFont.Bold)
        )
        self.studentLabel.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        subRow = QHBoxLayout()
        subRow.setSpacing(8)

        self.registerLabel = QLabel(
            f"ID: {self.register_no}"
        )
        self.registerLabel.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)

        self.subjectLabel = QLabel(
            f"📚 {self.subject}"
        )
        self.subjectLabel.setStyleSheet(f"""
            color: {BADGE_INFO_TEXT};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)

        subRow.addWidget(self.registerLabel)
        subRow.addWidget(self.subjectLabel)

        studentInfoLayout.addWidget(self.studentLabel)
        studentInfoLayout.addLayout(subRow)

        headerLayout.addWidget(avatar)
        headerLayout.addLayout(studentInfoLayout)
        headerLayout.addStretch()

        # -------------------------------------------------
        # Status Badge Pill
        # -------------------------------------------------
        self.statusLabel = QLabel(
            "● LIVE STREAM OK"
        )
        self.statusLabel.setFont(
            QFont("Segoe UI", 10, QFont.Bold)
        )
        self.statusLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_SUCCESS_BG};
                color: {BADGE_SUCCESS_TEXT};
                border: 1px solid {BADGE_SUCCESS_BORDER};
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)

        headerLayout.addWidget(self.statusLabel)
        layout.addLayout(headerLayout)

        # =================================================
        # CAMERA STREAM CONTAINER
        # =================================================

        self.cameraLabel = QLabel(
            "📡 Initializing Video Stream...\nWaiting for examinee feed"
        )
        self.cameraLabel.setAlignment(
            Qt.AlignCenter
        )
        self.cameraLabel.setMinimumSize(
            400,
            270
        )
        self.cameraLabel.setStyleSheet(f"""
            QLabel {{
                background-color: #090D16;
                color: {TEXT_MUTED};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)

        layout.addWidget(self.cameraLabel)
        self.setLayout(layout)

    # =====================================================
    # UPDATE FRAME
    # =====================================================

    def update_frame(self, frame):

        if frame is None:
            return

        try:

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            h, w, ch = rgb.shape
            bytes_per_line = ch * w

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

        except Exception as e:

            print(
                ">>> Camera card frame error:",
                e
            )

    # =====================================================
    # DISCONNECTED
    # =====================================================

    def set_disconnected(self):

        self.statusLabel.setText(
            "● SESSION ENDED"
        )

        self.statusLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_DANGER_BG};
                color: {BADGE_DANGER_TEXT};
                border: 1px solid {BADGE_DANGER_BORDER};
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 700;
            }}
        """)

        # Remove the last frozen camera frame
        self.cameraLabel.clear()

        # Show styled disconnect message
        self.cameraLabel.setText(
            "🔴 Examination Ended\n\n"
            "Examinee submitted paper or socket disconnected."
        )

        self.cameraLabel.setAlignment(
            Qt.AlignCenter
        )

        self.cameraLabel.setStyleSheet(f"""
            QLabel {{
                background-color: #0F141F;
                color: {BADGE_DANGER_TEXT};
                border: 1px dashed {BADGE_DANGER_BORDER};
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
        """)


# =========================================================
# LIVE MONITORING PAGE
# =========================================================

class LiveMonitorPage(QWidget):

    def __init__(self):

        super().__init__()

        self.cameraServer = None
        self.studentCards = {}
        self.signalBridge = CameraSignalBridge()

        # -------------------------------------------------
        # SIGNAL CONNECTIONS
        # -------------------------------------------------

        self.signalBridge.frame_received.connect(
            self.handle_frame
        )

        self.signalBridge.student_disconnected.connect(
            self.handle_disconnect
        )

        self.setupUI()
        self.start_camera_server()

    # =====================================================
    # UI
    # =====================================================

    def setupUI(self):

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CANVAS};
            }}
        """)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(28, 24, 28, 24)
        mainLayout.setSpacing(20)

        # =================================================
        # TOP HEADER BAR
        # =================================================

        headerFrame = QFrame()
        headerFrame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)

        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(20, 16, 20, 16)
        headerLayout.setSpacing(14)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(2)

        title = QLabel(
            "📹 Live Proctoring Surveillance Grid"
        )
        title.setFont(
            QFont("Segoe UI", 16, QFont.Bold)
        )
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        subTitle = QLabel("Active webcam streams receiving real-time OpenCV proctoring feeds.")
        subTitle.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        titleLayout.addWidget(title)
        titleLayout.addWidget(subTitle)

        headerLayout.addLayout(titleLayout)
        headerLayout.addStretch()

        # Server status badge
        self.serverStatusLabel = QLabel(
            "● TCP 5001 ACTIVE"
        )
        self.serverStatusLabel.setFont(
            QFont("Segoe UI", 10, QFont.Bold)
        )
        self.serverStatusLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {BADGE_SUCCESS_BG};
                color: {BADGE_SUCCESS_TEXT};
                border: 1px solid {BADGE_SUCCESS_BORDER};
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)

        self.refreshButton = QPushButton(
            "🔄 Refresh Grid"
        )
        self.refreshButton.setMinimumHeight(36)
        self.refreshButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CANVAS};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #1E293B;
                border-color: {COLOR_PRIMARY};
            }}
        """)

        self.refreshButton.clicked.connect(
            self.refresh_students
        )

        headerLayout.addWidget(self.serverStatusLabel)
        headerLayout.addWidget(self.refreshButton)

        headerFrame.setLayout(headerLayout)
        mainLayout.addWidget(headerFrame)

        # =================================================
        # SCROLL AREA (Grid Container)
        # =================================================

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background-color: transparent;")

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(18)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollWidget.setLayout(
            self.gridLayout
        )

        self.scrollArea.setWidget(
            self.scrollWidget
        )

        mainLayout.addWidget(
            self.scrollArea
        )

        # =================================================
        # EMPTY / WAITING FEED PLACEHOLDER
        # =================================================

        self.emptyLabel = QLabel(
            "📡 Waiting for examinee camera streams...\n"
            "Streams connect automatically when students start examinations."
        )
        self.emptyLabel.setAlignment(
            Qt.AlignCenter
        )
        self.emptyLabel.setFont(
            QFont("Segoe UI", 14)
        )
        self.emptyLabel.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                background-color: {BG_CARD};
                border: 1px dashed {BORDER_SUBTLE};
                border-radius: 14px;
                padding: 60px;
                font-size: 14px;
                font-weight: 600;
                line-height: 1.6;
            }}
        """)

        self.gridLayout.addWidget(
            self.emptyLabel,
            0,
            0
        )

        self.setLayout(
            mainLayout
        )

    # =====================================================
    # GET STUDENT + EXAM INFORMATION
    # =====================================================

    def get_student_exam_info(
        self,
        register_no
    ):

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            query = """
                SELECT
                    s.name AS student_name,
                    e.subject_code,
                    e.subject_name
                FROM students s

                LEFT JOIN student_assignment sa
                    ON s.id = sa.student_id

                LEFT JOIN exams e
                    ON sa.exam_id = e.id

                WHERE s.register_no = ?

                ORDER BY
                    e.exam_date DESC,
                    e.id DESC

                LIMIT 1
            """

            cursor.execute(
                query,
                (register_no,)
            )

            row = cursor.fetchone()

            if row is None:
                return (
                    "Unknown Student",
                    "Unknown Subject"
                )

            student_name = row["student_name"]
            subject_code = row["subject_code"]
            subject_name = row["subject_name"]

            if subject_code and subject_name:
                subject = f"{subject_code} - {subject_name}"
            elif subject_name:
                subject = subject_name
            elif subject_code:
                subject = subject_code
            else:
                subject = "Unknown Subject"

            return (
                student_name or "Unknown Student",
                subject
            )

        except Exception as e:

            print(
                ">>> Student database lookup error:",
                e
            )

            return (
                "Unknown Student",
                "Unknown Subject"
            )

        finally:

            if connection is not None:
                connection.close()

    # =====================================================
    # START CAMERA SERVER
    # =====================================================

    def start_camera_server(self):

        try:

            self.cameraServer = CameraServer(
                host="0.0.0.0",
                port=5001,
                on_frame=self.server_frame_received,
                on_disconnect=self.server_student_disconnected
            )

            self.cameraServer.start()

            print(
                ">>> Live Monitoring camera server started."
            )

        except Exception as e:

            print(
                ">>> Live Monitoring server error:",
                e
            )

            self.serverStatusLabel.setText(
                "🔴 SERVER ERROR"
            )

            self.serverStatusLabel.setStyleSheet(f"""
                QLabel {{
                    background-color: {BADGE_DANGER_BG};
                    color: {BADGE_DANGER_TEXT};
                    border: 1px solid {BADGE_DANGER_BORDER};
                    border-radius: 12px;
                    padding: 6px 14px;
                    font-size: 11px;
                    font-weight: 700;
                }}
            """)

    # =====================================================
    # SERVER RECEIVED FRAME
    # =====================================================

    def server_frame_received(
        self,
        register_no,
        frame
    ):

        self.signalBridge.frame_received.emit(
            str(register_no),
            frame
        )

    # =====================================================
    # SERVER DISCONNECTED
    # =====================================================

    def server_student_disconnected(
        self,
        register_no
    ):

        if register_no is None:
            return

        self.signalBridge.student_disconnected.emit(
            str(register_no)
        )

    # =====================================================
    # HANDLE FRAME - PYQT THREAD
    # =====================================================

    def handle_frame(
        self,
        register_no,
        frame
    ):

        register_no = str(
            register_no
        )

        if register_no not in self.studentCards:
            self.create_student_card(
                register_no
            )

        card = self.studentCards.get(
            register_no
        )

        if card is not None:
            card.update_frame(
                frame
            )

    # =====================================================
    # CREATE STUDENT CARD
    # =====================================================

    def create_student_card(
        self,
        register_no
    ):

        student_name, subject = (
            self.get_student_exam_info(
                register_no
            )
        )

        card = StudentCameraCard(
            register_no,
            student_name,
            subject
        )

        self.studentCards[
            register_no
        ] = card

        if self.emptyLabel is not None:
            self.emptyLabel.hide()

        index = len(self.studentCards) - 1
        row = index // 2
        column = index % 2

        self.gridLayout.addWidget(
            card,
            row,
            column
        )

        card.show()

    # =====================================================
    # HANDLE DISCONNECT
    # =====================================================

    def handle_disconnect(
        self,
        register_no
    ):

        register_no = str(
            register_no
        )

        card = self.studentCards.get(
            register_no
        )

        if card is not None:
            card.set_disconnected()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_students(self):
        print(
            ">>> Live monitoring refresh."
        )

    # =====================================================
    # CLOSE
    # =====================================================

    def closeEvent(
        self,
        event
    ):

        if self.cameraServer is not None:

            try:
                self.cameraServer.stop()
            except Exception as e:
                print(
                    ">>> Camera server stop error:",
                    e
                )

            self.cameraServer = None

        event.accept()
