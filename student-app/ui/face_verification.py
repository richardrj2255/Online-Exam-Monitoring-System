import cv2

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QApplication,
)

from PyQt5.QtGui import (
    QImage,
    QPixmap,
    QFont,
)

from PyQt5.QtCore import (
    Qt,
    QTimer,
)
from ui.instruction_page import InstructionPage

import subprocess
import sys


class FaceVerification(QWidget):

    def __init__(self, student):

        super().__init__()

        self.student = student

        self.camera = None

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_frame
        )

       # self.verifier = FaceVerifier()

        self.setupUI()

        self.start_camera()

    ##########################################################

    def setupUI(self):

        self.setWindowTitle(
            "Student Face Verification"
        )

        self.resize(950, 720)

        self.setStyleSheet("""

        QWidget{
            background:#eef3f8;
        }

        QLabel{
            border:none;
            color:#1f2937;
        }

        QPushButton{

            background:#2563eb;
            color:white;

            border:none;

            border-radius:8px;

            padding:12px;

            font-size:15px;

            font-weight:bold;

        }

        QPushButton:hover{

            background:#1d4ed8;

        }

        """)

        ##################################################

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignCenter)

        ##################################################

        title = QLabel("Face Verification")

        title.setAlignment(Qt.AlignCenter)

        title.setFont(
            QFont("Arial", 22, QFont.Bold)
        )

        ##################################################

        info = QLabel(

            f"{self.student['name']}\n"
            f"Register No : {self.student['register_no']}"

        )

        info.setAlignment(Qt.AlignCenter)

        info.setFont(
            QFont("Arial", 12)
        )

        ##################################################

        self.cameraLabel = QLabel()

        self.cameraLabel.setFixedSize(
            700,
            500
        )

        self.cameraLabel.setAlignment(
            Qt.AlignCenter
        )

        self.cameraLabel.setStyleSheet("""

        QLabel{

            background:black;

            border:2px solid #cbd5e1;

            border-radius:10px;

        }

        """)

        ##################################################

        self.statusLabel = QLabel(
            "Camera Initializing..."
        )

        self.statusLabel.setAlignment(
            Qt.AlignCenter
        )

        self.statusLabel.setFont(
            QFont("Arial", 11)
        )

        ##################################################

        self.verifyBtn = QPushButton(
            "Verify Face"
        )

        self.verifyBtn.setFixedHeight(45)

        self.verifyBtn.clicked.connect(
            self.verify_face
        )

        ##################################################

        layout.addSpacing(20)

        layout.addWidget(title)

        layout.addWidget(info)

        layout.addSpacing(20)

        layout.addWidget(
            self.cameraLabel,
            alignment=Qt.AlignCenter
        )

        layout.addSpacing(15)

        layout.addWidget(self.statusLabel)

        layout.addSpacing(10)

        layout.addWidget(self.verifyBtn)

        layout.addStretch()

        self.setLayout(layout)
    ##########################################################
    # Start Camera
    ##########################################################

    def start_camera(self):

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():

            QMessageBox.critical(
                self,
                "Camera Error",
                "Unable to access webcam."
            )

            return

        self.statusLabel.setText(
            "Camera Ready"
        )

        self.timer.start(30)

    ##########################################################
    # Update Camera Frame
    ##########################################################

    def update_frame(self):

        if self.camera is None:
            return

        success, frame = self.camera.read()

        if not success:
            return
        self.current_frame = frame.copy()

        frame = cv2.flip(frame, 1)

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

        pixmap = QPixmap.fromImage(image)

        self.cameraLabel.setPixmap(

            pixmap.scaled(

                self.cameraLabel.width(),
                self.cameraLabel.height(),

                Qt.KeepAspectRatio,

                Qt.SmoothTransformation

            )

        )
##########################################################
# Verify Face
##########################################################

    def verify_face(self):

        self.verifyBtn.setEnabled(False)

        self.statusLabel.setText(
            "Verifying Face..."
        )

        QApplication.processEvents()

        # Stop live camera preview
        self.timer.stop()

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()
        import os

        registered_photo = self.student["photo"]
        os.makedirs("temp", exist_ok=True)

        captured_path = os.path.join(
            "temp",
            "captured.jpg"
        )
        print("Registered Photo:", registered_photo)
        print("Captured Photo :", captured_path)
        cv2.imwrite(
            captured_path,
            self.current_frame
        )

        result = subprocess.run(
            [
                sys.executable,
                "verify_face.py",
                registered_photo,
                captured_path
            ],
            capture_output=True,
            text=True,
            cwd="."
        )

        output = result.stdout.strip()

        print("\n========== Helper Output ==========")
        print(output)

        print("\n========== Helper Error ==========")
        print(result.stderr)

        if "VERIFIED" in output:

            self.statusLabel.setText(
                "✅ Face Verified Successfully"
            )

            QMessageBox.information(
                self,
                "Success",
                "Face Verified Successfully!"
            )

            self.instructionWindow = InstructionPage(self.student)

            self.instructionWindow.show()

            self.close()

        else:

            self.statusLabel.setText(
                "❌ Face Verification Failed"
            )

            QMessageBox.warning(
                self,
                "Verification Failed",
                output if output else "Face Verification Failed"
            )

            self.verifyBtn.setEnabled(True)

        # Restart camera preview
            self.start_camera()
    ##########################################################
    # Close Camera
    ##########################################################

    def closeEvent(self, event):

        self.timer.stop()

        if self.camera is not None:
            self.camera.release()

        event.accept()