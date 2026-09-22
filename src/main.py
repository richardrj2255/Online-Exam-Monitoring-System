import cv2
import yaml

from detection.face_detection import FaceDetector


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():

    config = load_config()

    face_detector = FaceDetector(config)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Unable to open camera.")
        return

    print("Press Q to Exit")

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        face_present = face_detector.detect_face(frame)

        if face_present:

            cv2.putText(
                frame,
                "Face Detected",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

        else:

            cv2.putText(
                frame,
                "No Face Detected",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                2
            )

        cv2.imshow("Offline Examination Monitoring System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()