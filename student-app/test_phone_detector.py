import cv2

from ai.phone_detector import PhoneDetector


def main():

    print()
    print("==============================")
    print(" MOBILE PHONE DETECTION TEST")
    print("==============================")

    detector = PhoneDetector()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Unable to open camera.")
        return

    print()
    print("Camera started.")
    print("Show a mobile phone to the camera.")
    print("Press Q to quit.")
    print()

    while True:

        success, frame = camera.read()

        if not success:

            print("Unable to read camera frame.")
            break

        frame = cv2.flip(
            frame,
            1
        )

        phone_detected = detector.detect(
            frame
        )

        frame = detector.draw_results(
            frame,
            phone_detected
        )

        # -------------------------------------------------
        # Console status
        # -------------------------------------------------

        if phone_detected:

            print(
                "⚠ MOBILE PHONE DETECTED"
            )

        else:

            print(
                "No phone detected",
                end="\r"
            )

        cv2.imshow(
            "Mobile Phone Detection",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()