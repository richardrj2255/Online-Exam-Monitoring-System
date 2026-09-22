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
from ui.theme_manager import (
    get_theme_palette,
    register_theme_listener,
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
        self.is_disconnected = False

        self.setObjectName("cameraCard")
        self.setMinimumSize(
            440,
            380
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # =================================================
        # STUDENT HEADER (Interactive Top Status Bar Overlay)
        # =================================================

        self.topStatusBar = QFrame()
        self.topStatusBar.setObjectName("topStatusBar")
        self.topStatusBar.setStyleSheet("background: transparent; border: none;")

        headerLayout = QHBoxLayout(self.topStatusBar)
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(12)

        # -------------------------------------------------
        # Student Avatar + Info
        # -------------------------------------------------
        self.avatar = QLabel("👨‍🎓")
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setFixedSize(38, 38)
        self.avatar.setFont(QFont("Segoe UI Emoji", 16))

        studentInfoLayout = QVBoxLayout()
        studentInfoLayout.setSpacing(2)

        self.studentLabel = QLabel(
            self.student_name
        )
        self.studentLabel.setFont(
            QFont("Segoe UI", 13, QFont.Bold)
        )
        self.studentLabel.setStyleSheet("font-size: 14px; font-weight: 700; background: transparent; border: none;")

        subRow = QHBoxLayout()
        subRow.setSpacing(8)

        self.registerLabel = QLabel(
            f"ID: {self.register_no}"
        )
        self.registerLabel.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent; border: none;")

        self.subjectLabel = QLabel(
            f"📚 {self.subject}"
        )
        self.subjectLabel.setStyleSheet("font-size: 12px; font-weight: 600; background: transparent; border: none;")

        subRow.addWidget(self.registerLabel)
        subRow.addWidget(self.subjectLabel)

        studentInfoLayout.addWidget(self.studentLabel)
        studentInfoLayout.addLayout(subRow)

        headerLayout.addWidget(self.avatar)
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

        headerLayout.addWidget(self.statusLabel)
        layout.addWidget(self.topStatusBar)

        # =================================================
        # CAMERA STREAM CONTAINER
        # =================================================

        self.cameraLabel = QLabel(
            "📡 Initializing Video Stream...\nWaiting for examinee feed"
        )
        self.cameraLabel.setObjectName("cameraFeed")
        self.cameraLabel.setAlignment(
            Qt.AlignCenter
        )
        self.cameraLabel.setMinimumSize(
            400,
            270
        )

        layout.addWidget(self.cameraLabel)
        self.setLayout(layout)

        self._apply_theme_styles()
        register_theme_listener(self._on_theme_changed)

    def _on_theme_changed(self, theme_name):
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        p = get_theme_palette()

        self.avatar.setStyleSheet(f"""
            background-color: {p['bg_card_alt']};
            border: 1px solid {p['border_subtle']};
            border-radius: 19px;
        """)

        self.registerLabel.setStyleSheet(f"color: {p['text_secondary']}; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        self.subjectLabel.setStyleSheet(f"color: {p['color_primary']}; font-size: 12px; font-weight: 600; background: transparent; border: none;")

        if not self.is_disconnected:
            self.statusLabel.setStyleSheet(f"""
                QLabel {{
                    background-color: {p['badge_success_bg']};
                    color: {p['badge_success_text']};
                    border: 1px solid {p['badge_success_border']};
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                }}
            """)
        else:
            self.statusLabel.setStyleSheet(f"""
                QLabel {{
                    background-color: {p['badge_danger_bg']};
                    color: {p['badge_danger_text']};
                    border: 1px solid {p['badge_danger_border']};
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 700;
                }}
            """)

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

        self.is_disconnected = True
        p = get_theme_palette()

        self.statusLabel.setText(
            "● SESSION ENDED"
        )

        self.statusLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {p['badge_danger_bg']};
                color: {p['badge_danger_text']};
                border: 1px solid {p['badge_danger_border']};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
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
                background-color: {p['bg_card_alt']};
                color: {p['badge_danger_text']};
                border: 1px dashed {p['badge_danger_border']};
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
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
        register_theme_listener(self._on_theme_changed)

    # =====================================================
    # UI
    # =====================================================

    def setupUI(self):

        self.setObjectName("pageWidget")

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(28, 24, 28, 24)
        mainLayout.setSpacing(20)

        # =================================================
        # TOP HEADER BAR
        # =================================================

        headerFrame = QFrame()
        headerFrame.setObjectName("headerCard")

        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(20, 16, 20, 16)
        headerLayout.setSpacing(14)

        titleLayout = QVBoxLayout()
        titleLayout.setSpacing(3)

        title = QLabel(
            "📹 Live Proctoring Surveillance Grid"
        )
        title.setObjectName("pageTitle")
        title.setFont(
            QFont("Segoe UI", 16, QFont.Bold)
        )

        subTitle = QLabel("Active webcam streams receiving real-time OpenCV proctoring feeds.")
        subTitle.setObjectName("pageSubtitle")

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

        self.refreshButton = QPushButton(
            "🔄 Refresh Grid"
        )
        self.refreshButton.setObjectName("secondaryBtn")
        self.refreshButton.setCursor(Qt.PointingHandCursor)
        self.refreshButton.setMinimumHeight(38)

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
            "📡 Waiting for examinee camera streams...\n\n"
            "Streams connect automatically when students start examinations."
        )
        self.emptyLabel.setObjectName("cameraFeed")
        self.emptyLabel.setAlignment(
            Qt.AlignCenter
        )
        self.emptyLabel.setFont(
            QFont("Segoe UI", 14)
        )
        self.emptyLabel.setMinimumHeight(240)

        self.gridLayout.addWidget(
            self.emptyLabel,
            0,
            0
        )

        self.setLayout(
            mainLayout
        )

        self._apply_server_badge()

    def _on_theme_changed(self, theme_name):
        self._apply_server_badge()

    def _apply_server_badge(self):
        p = get_theme_palette()
        self.serverStatusLabel.setStyleSheet(f"""
            QLabel {{
                background-color: {p['badge_success_bg']};
                color: {p['badge_success_text']};
                border: 1px solid {p['badge_success_border']};
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)

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

            p = get_theme_palette()
            self.serverStatusLabel.setText(
                "🔴 SERVER ERROR"
            )

            self.serverStatusLabel.setStyleSheet(f"""
                QLabel {{
                    background-color: {p['badge_danger_bg']};
                    color: {p['badge_danger_text']};
                    border: 1px solid {p['badge_danger_border']};
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
