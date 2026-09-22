import cv2
import mediapipe as mp
import numpy as np

from insightface.app import FaceAnalysis


class ExamDetector:

    def __init__(self):

        print(">>> Initializing Exam Detector...")

        # =================================================
        # INSIGHTFACE
        # =================================================

        self.face_app = FaceAnalysis(
            providers=["CPUExecutionProvider"]
        )

        self.face_app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

        # =================================================
        # MEDIAPIPE HANDS
        # =================================================

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        print(">>> Exam Detector Ready")

    # =====================================================
    # MAIN DETECTION
    # =====================================================

    def detect(self, frame):

        if frame is None:

            return {
                "face_count": 0,
                "hands_detected": 0,
                "hands_below": False,
                "head_turned": False
            }

        # -------------------------------------------------
        # FACE DETECTION
        # -------------------------------------------------

        faces = self.face_app.get(frame)

        face_count = len(faces)

        # -------------------------------------------------
        # HAND DETECTION
        # -------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        hand_results = self.hands.process(rgb)

        hands_detected = 0

        if hand_results.multi_hand_landmarks:

            hands_detected = len(
                hand_results.multi_hand_landmarks
            )

        # -------------------------------------------------
        # HANDS BELOW TABLE
        #
        # DISABLED FOR NOW
        # Detection was not sufficiently accurate.
        # -------------------------------------------------

        hands_below = False

        # -------------------------------------------------
        # HEAD MOVEMENT
        # -------------------------------------------------

        head_turned = self.detect_head_turn(
            faces
        )

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        return {

            "face_count":
                face_count,

            "hands_detected":
                hands_detected,

            "hands_below":
                hands_below,

            "head_turned":
                head_turned
        }

    # =====================================================
    # HEAD TURN DETECTION
    # =====================================================

    def detect_head_turn(
        self,
        faces
    ):

        # No face
        if len(faces) == 0:

            return False

        face = faces[0]

        # -------------------------------------------------
        # Check facial landmarks
        # -------------------------------------------------

        if not hasattr(
            face,
            "kps"
        ):

            return False

        kps = face.kps

        if kps is None:

            return False

        # -------------------------------------------------
        # Five landmarks
        #
        # 0 = left eye
        # 1 = right eye
        # 2 = nose
        # 3 = left mouth
        # 4 = right mouth
        # -------------------------------------------------

        left_eye = kps[0]

        right_eye = kps[1]

        nose = kps[2]

        # -------------------------------------------------
        # Eye center
        # -------------------------------------------------

        eye_center = (
            left_eye +
            right_eye
        ) / 2

        # -------------------------------------------------
        # Distance between eyes
        # -------------------------------------------------

        eye_distance = np.linalg.norm(
            right_eye -
            left_eye
        )

        if eye_distance == 0:

            return False

        # -------------------------------------------------
        # Horizontal head position
        # -------------------------------------------------

        horizontal_ratio = (
            nose[0] -
            eye_center[0]
        ) / eye_distance

        # -------------------------------------------------
        # Threshold
        # -------------------------------------------------

        if abs(horizontal_ratio) > 0.35:

            return True

        return False

    # =====================================================
    # DRAW MONITORING INFORMATION
    # =====================================================

    def draw_results(
        self,
        frame,
        results
    ):

        face_count = results[
            "face_count"
        ]

        hands_detected = results[
            "hands_detected"
        ]

        head_turned = results[
            "head_turned"
        ]

        # -------------------------------------------------
        # Face count
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"Faces: {face_count}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # -------------------------------------------------
        # Hands
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"Hands: {hands_detected}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # -------------------------------------------------
        # Head
        # -------------------------------------------------

        head_text = (
            "HEAD TURNED"
            if head_turned
            else "HEAD NORMAL"
        )

        cv2.putText(
            frame,
            head_text,
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,

            (0, 0, 255)
            if head_turned
            else (0, 255, 0),

            2
        )

        return frame

    # =====================================================
    # RELEASE
    # =====================================================

    def close(self):

        self.hands.close()