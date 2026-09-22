from PyQt5.QtWidgets import QApplication
import sys

print("Step 1")

app = QApplication(sys.argv)

print("Step 2")

from ai.face_verifier import FaceVerifier

print("Step 3")

verifier = FaceVerifier()

print("Step 4 - SUCCESS")