import cv2
import time
import os

from ai.monitoring_rules import (
    FACE_ABSENCE_SECONDS,
    MULTIPLE_FACE_SECONDS,
    HEAD_TURN_SECONDS,
    HANDS_BELOW_TABLE_SECONDS,
    MAX_WARNINGS,
    SCREENSHOT_FOLDER
)


class ExamMonitor:

    def __init__(self):

        # -----------------------------------------
        # Monitoring state
        # -----------------------------------------

        self.face_count = 0

        # Face absence
        self.face_absent_since = None

        # Multiple faces
        self.multiple_face_since = None

        # Head movement
        self.head_turn_since = None

        # Hands below table
        self.hands_below_since = None

        # Warning / violation counters
        self.warning_count = 0
        self.violation_count = 0

        # Prevent repeated events
        self.last_events = {}

        # Screenshot folder
        os.makedirs(
            SCREENSHOT_FOLDER,
            exist_ok=True
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.face_count = 0

        self.face_absent_since = None
        self.multiple_face_since = None
        self.head_turn_since = None
        self.hands_below_since = None

        self.warning_count = 0
        self.violation_count = 0

        self.last_events = {}

    # =====================================================
    # FACE MONITORING
    # =====================================================

    def check_face_count(self, face_count):

        self.face_count = face_count

        current_time = time.time()

        # -----------------------------------------
        # No face
        # -----------------------------------------

        if face_count == 0:

            if self.face_absent_since is None:

                self.face_absent_since = current_time

            elapsed = (
                current_time -
                self.face_absent_since
            )

            if elapsed >= FACE_ABSENCE_SECONDS:

                return self.warning(
                    "FACE_ABSENT"
                )

        else:

            self.face_absent_since = None

        # -----------------------------------------
        # Multiple faces
        # -----------------------------------------

        if face_count > 1:

            if self.multiple_face_since is None:

                self.multiple_face_since = current_time

            elapsed = (
                current_time -
                self.multiple_face_since
            )

            if elapsed >= MULTIPLE_FACE_SECONDS:

                return self.warning(
                    "MULTIPLE_FACES"
                )

        else:

            self.multiple_face_since = None

        return None

    # =====================================================
    # HEAD MOVEMENT
    # =====================================================

    def check_head_turn(self, turned):

        current_time = time.time()

        if turned:

            if self.head_turn_since is None:

                self.head_turn_since = current_time

            elapsed = (
                current_time -
                self.head_turn_since
            )

            if elapsed >= HEAD_TURN_SECONDS:

                return self.warning(
                    "HEAD_TURNED"
                )

        else:

            self.head_turn_since = None

        return None

    # =====================================================
    # HANDS BELOW TABLE
    # =====================================================

    def check_hands_below_table(self, hands_below):

        current_time = time.time()

        if hands_below:

            if self.hands_below_since is None:

                self.hands_below_since = current_time

            elapsed = (
                current_time -
                self.hands_below_since
            )

            # -----------------------------------------
            # Must remain below table for 5 seconds
            # -----------------------------------------

            if elapsed >= HANDS_BELOW_TABLE_SECONDS:

                # Reset timer immediately.
                # This makes it one occurrence instead
                # of generating an event every frame.

                self.hands_below_since = None

                return self.warning(
                    "HANDS_BELOW_TABLE"
                )

        else:

            self.hands_below_since = None

        return None

    # =====================================================
    # WARNING SYSTEM
    # =====================================================

    def warning(self, violation_type):

        # Prevent the same event from firing repeatedly
        # every frame.

        current_time = time.time()

        last_time = self.last_events.get(
            violation_type
        )

        if last_time is not None:

            # Minimum gap between identical events
            if current_time - last_time < 2:

                return None

        self.last_events[
            violation_type
        ] = current_time

        # -----------------------------------------
        # First 3 occurrences = warning
        # 4th = violation
        # -----------------------------------------

        if self.warning_count < MAX_WARNINGS:

            self.warning_count += 1

            return {
                "type": "WARNING",
                "violation": violation_type,
                "count": self.warning_count,
                "message": self.warning_message(
                    violation_type
                )
            }

        else:

            self.violation_count += 1

            return {
                "type": "VIOLATION",
                "violation": violation_type,
                "count": self.violation_count,
                "message": self.violation_message(
                    violation_type
                )
            }

    # =====================================================
    # WARNING MESSAGE
    # =====================================================

    def warning_message(self, violation_type):

        messages = {

            "FACE_ABSENT":
                "Please keep your face visible.",

            "MULTIPLE_FACES":
                "Multiple faces detected.",

            "HEAD_TURNED":
                "Please look towards the examination screen.",

            "HANDS_BELOW_TABLE":
                "Please keep your hands visible."
        }

        return messages.get(
            violation_type,
            "Suspicious activity detected."
        )

    # =====================================================
    # VIOLATION MESSAGE
    # =====================================================

    def violation_message(self, violation_type):

        messages = {

            "FACE_ABSENT":
                "Repeated face absence detected.",

            "MULTIPLE_FACES":
                "Repeated multiple-face detection.",

            "HEAD_TURNED":
                "Repeated head movement detected.",

            "HANDS_BELOW_TABLE":
                "Repeated hands-below-table activity detected."
        }

        return messages.get(
            violation_type,
            "Examination violation detected."
        )

    # =====================================================
    # CAPTURE VIOLATION
    # =====================================================

    def capture_violation(self, frame, violation_type):

        if frame is None:

            return None

        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"{violation_type}_"
            f"{timestamp}.jpg"
        )

        path = os.path.join(
            SCREENSHOT_FOLDER,
            filename
        )

        cv2.imwrite(
            path,
            frame
        )

        return path