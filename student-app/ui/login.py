import os

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QFrame
)

from PyQt5.QtGui import (
    QFont,
    QPixmap
)

from PyQt5.QtCore import Qt

from models.student_model import StudentModel


class StudentLogin(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Offline Examination Monitoring System"
        )

        self.setFixedSize(760, 620)

        self.setupUI()

    ############################################################

    def setupUI(self):

        self.setStyleSheet("""
            QWidget{
                background:#eef3f8;
                font-family:Arial;
            }
        """)

        ########################################################

        mainLayout = QVBoxLayout()

        mainLayout.setContentsMargins(
            30,
            30,
            30,
            25
        )

        mainLayout.setAlignment(Qt.AlignCenter)

        ########################################################
        # Login Card
        ########################################################

        card = QFrame()

        card.setFixedSize(600, 520)

        card.setStyleSheet("""
            QFrame{
                background:white;
                border:1px solid #d8d8d8;
                border-radius:18px;
            }
        """)

        cardLayout = QVBoxLayout()

        cardLayout.setContentsMargins(
            45,
            30,
            45,
            30
        )

        cardLayout.setSpacing(12)

        ########################################################
        # College Logo
        ########################################################

        logo = QLabel()

        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "sjcet_logo.png"
        )

        pixmap = QPixmap(logo_path)

        if not pixmap.isNull():

            logo.setPixmap(
                pixmap.scaled(
                    170,
                    170,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
            logo.setFixedHeight(180)

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet("""
            border:none;
            background:transparent;
        """)

        ########################################################
        # College Name
        ########################################################

        college = QLabel(
            ""
        )

        college.setAlignment(Qt.AlignCenter)

        college.setFont(
            QFont("Arial", 14, QFont.Bold)
        )

        college.setStyleSheet("""
            color:#b91c1c;
            border:none;
            background:transparent;
        """)

        ########################################################

        place = QLabel("")

        place.setAlignment(Qt.AlignCenter)

        place.setFont(
            QFont("Arial", 12)
        )

        place.setStyleSheet("""
            color:#4b5563;
            border:none;
            background:transparent;
        """)

        ########################################################

        title = QLabel(
            ""
        )

        title.setAlignment(Qt.AlignCenter)

        title.setFont(
            QFont("Arial", 18, QFont.Bold)
        )

        title.setStyleSheet("""
            color:#1e3a5f;
            border:none;
            background:transparent;
        """)

        ########################################################

        subtitle = QLabel(
            "Student Authentication"
        )

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setFont(
            QFont("Arial", 11)
        )

        subtitle.setStyleSheet("""
            color:#6b7280;
            border:none;
            background:transparent;
        """)

        ########################################################

        registerLabel = QLabel(
            "Register Number"
        )

        registerLabel.setFont(
            QFont("Arial", 11, QFont.Bold)
        )

        registerLabel.setStyleSheet("""
            border:none;
            background:transparent;
            color:#2c3e50;
        """)

        ########################################################

        self.regInput = QLineEdit()

        self.regInput.setPlaceholderText(
            "Enter your Register Number"
        )

        self.regInput.setMinimumHeight(48)

        self.regInput.setStyleSheet("""
            QLineEdit{
                background:white;
                border:1px solid #cbd5e1;
                border-radius:8px;
                padding-left:12px;
                font-size:14px;
            }

            QLineEdit:focus{
                border:2px solid #2563eb;
            }
        """)

        self.regInput.returnPressed.connect(
            self.login
        )

        ########################################################
        # Add Widgets
        ########################################################

        cardLayout.addWidget(logo)

        cardLayout.addWidget(college)

        cardLayout.addWidget(place)

        cardLayout.addSpacing(5)

        cardLayout.addWidget(title)

        cardLayout.addWidget(subtitle)

        cardLayout.addSpacing(20)

        cardLayout.addWidget(registerLabel)

        cardLayout.addWidget(self.regInput)
        ########################################################
        # Continue Button
        ########################################################

        cardLayout.addSpacing(18)

        self.loginBtn = QPushButton("Continue")

        self.loginBtn.setMinimumHeight(48)

        self.loginBtn.setStyleSheet("""
            QPushButton{
                background:#2563eb;
                color:white;
                border:none;
                border-radius:8px;
                font-size:15px;
                font-weight:bold;
            }

            QPushButton:hover{
                background:#1d4ed8;
            }

            QPushButton:pressed{
                background:#1e40af;
            }
        """)

        self.loginBtn.clicked.connect(self.login)

        cardLayout.addWidget(self.loginBtn)

        ########################################################
        # Information
        ########################################################

        cardLayout.addSpacing(15)

        info = QLabel(
            "Please verify your identity before entering the examination."
        )

        info.setAlignment(Qt.AlignCenter)

        info.setFont(
            QFont("Arial", 10)
        )

        info.setStyleSheet("""
            color:#6b7280;
            border:none;
            background:transparent;
        """)

        cardLayout.addWidget(info)

        ########################################################

        card.setLayout(cardLayout)

        ########################################################
        # Footer
        ########################################################

        footer = QLabel(
            "© 2026 Offline Examination Monitoring System"
        )

        footer.setAlignment(Qt.AlignCenter)

        footer.setStyleSheet("""
            color:#7f8c8d;
            background:transparent;
            border:none;
            font-size:10pt;
        """)

        ########################################################

        mainLayout.addStretch()

        mainLayout.addWidget(
            card,
            alignment=Qt.AlignCenter
        )

        mainLayout.addSpacing(15)

        mainLayout.addWidget(
            footer,
            alignment=Qt.AlignCenter
        )

        self.setLayout(mainLayout)

    ############################################################
    # Login
    ############################################################

    def login(self):

        register_no = self.regInput.text().strip()

        if register_no == "":

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter your Register Number."
            )

            return

        student = StudentModel.get_student(register_no)

        if student is None:

            QMessageBox.warning(
                self,
                "Student Not Found",
                "No student exists with this Register Number."
            )

            return

        from ui.face_verification import FaceVerification

        self.faceWindow = FaceVerification(student)
        self.faceWindow.show()

        self.close()

        # -----------------------------------------------------
        # NEXT STEP
        # Open Face Verification Window here
        # -----------------------------------------------------