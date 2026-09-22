from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

from models.assignment_model import AssignmentModel
from ui.monitoring_page import MonitoringPage


class InstructionPage(QWidget):

    def __init__(self, student):

        super().__init__()

        self.student = student

        self.exam = AssignmentModel.get_assigned_exam(
            student["id"]
        )

        self.setWindowTitle(
            "Examination Instructions"
        )

        self.resize(900, 700)

        self.setupUI()
        self.load_data()
        # Check exam status every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_exam_status)
        self.timer.start(1000)
    ####################################################

    def setupUI(self):

        self.setStyleSheet("""

            QWidget{

                background:#eef3f8;

                font-family:Arial;

            }

            QFrame{

                background:white;

                border-radius:15px;

                border:1px solid #dddddd;

            }

        """)

        mainLayout = QVBoxLayout()

        card = QFrame()

        cardLayout = QVBoxLayout()

        ################################################

        title = QLabel(
            "OFFLINE EXAMINATION MONITORING SYSTEM"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setFont(
            QFont("Arial",18,QFont.Bold)
        )

        ################################################

        self.studentLabel = QLabel()

        self.examLabel = QLabel()

        ################################################

        instructionTitle = QLabel(
            "Instructions"
        )

        instructionTitle.setFont(
            QFont("Arial",14,QFont.Bold)
        )

        ################################################

        instructions = QLabel(

"""
• Keep your face visible throughout the examination.

• Mobile phones are strictly prohibited.

• Multiple persons are not allowed.

• Do not switch applications.

• Every violation will be recorded automatically.

• Wait until the administrator starts the examination.

"""
        )

        instructions.setWordWrap(True)

        ################################################

        self.statusLabel = QLabel(

            "⏳ Waiting for Administrator..."

        )

        self.statusLabel.setAlignment(
            Qt.AlignCenter
        )

        self.statusLabel.setFont(
            QFont("Arial",15,QFont.Bold)
        )

        self.statusLabel.setStyleSheet("""

            color:#2563eb;

        """)

        ################################################

        cardLayout.addWidget(title)

        cardLayout.addSpacing(20)

        cardLayout.addWidget(self.studentLabel)

        cardLayout.addSpacing(10)

        cardLayout.addWidget(self.examLabel)

        cardLayout.addSpacing(20)

        cardLayout.addWidget(instructionTitle)

        cardLayout.addWidget(instructions)

        cardLayout.addStretch()

        cardLayout.addWidget(self.statusLabel)

        card.setLayout(cardLayout)

        mainLayout.addWidget(card)

        self.setLayout(mainLayout)

    ####################################################
    # Load Student and Exam Details
    ####################################################

    def load_data(self):

        self.studentLabel.setText(

            f"""
Student Name : {self.student["name"]}

Register No  : {self.student["register_no"]}

Department   : {self.student["department"]}

Semester     : {self.student["semester"]}
"""
        )

        if self.exam:

            self.examLabel.setText(

                f"""
Exam Name    : {self.exam["exam_name"]}

Subject      : {self.exam["subject_name"]}

Subject Code : {self.exam["subject_code"]}

Date         : {self.exam["exam_date"]}

Time         : {self.exam["start_time"]} - {self.exam["end_time"]}

Duration     : {self.exam["duration"]}

Hall         : {self.exam["hall"]}
"""
            )

        else:

            self.examLabel.setText(
                "No examination has been assigned."
            )
####################################################
# Check Exam Status
####################################################

    def check_exam_status(self):

        exam = AssignmentModel.get_assigned_exam(
            self.student["id"]
        )

        if exam is None:
            return

        status = exam["exam_status"]

        print("Exam Status:", status)

        if status == "Started":

            self.timer.stop()

            print(">>> ADMIN STARTED THE EXAM")
            print(">>> Opening Monitoring Page")

            self.monitoringWindow = MonitoringPage(
                self.student,
                exam
            )

            self.monitoringWindow.show()

            self.close()

        # --------------------------------------------
        # NEXT STEP:
        # Open actual examination page here
        # --------------------------------------------
