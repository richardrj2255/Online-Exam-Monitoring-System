from ultralytics import YOLO


class PhoneDetector:

    def __init__(self):

        print(">>> Initializing Phone Detector...")

        self.model = YOLO("yolo11n.pt")

        print(">>> Phone Detector Ready")

    # =====================================================
    # Detect Mobile Phone
    # =====================================================

    def detect(self, frame):

        if frame is None:

            return False

        results = self.model(
            frame,
            imgsz=416,
            conf=0.30,
            iou=0.45,
            verbose=False
        )

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                class_name = self.model.names[
                    class_id
                ]

                # -------------------------------------------------
                # COCO class name for mobile phone
                # -------------------------------------------------

                if (
                    class_name == "cell phone"
                    and confidence >= 0.50
                ):

                    return True

        return False

    # =====================================================
    # Draw Detection
    # =====================================================

    def draw_results(
        self,
        frame,
        phone_detected
    ):

        if phone_detected:

            cv2_text = "MOBILE PHONE DETECTED"

            import cv2

            cv2.putText(
                frame,
                cv2_text,
                (20, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        return frame

