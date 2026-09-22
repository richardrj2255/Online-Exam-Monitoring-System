import cv2

from ai.detector import ExamDetector


def main():

    print("================================")
    print(" AI EXAM MONITORING TEST")
    print("================================")

    detector = ExamDetector()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Unable to open camera.")

        detector.close()

        return

    print()
    print("Camera started.")
    print("Press Q to exit.")
    print()

    while True:

        success, frame = camera.read()

        if not success:

            print("Unable to read camera frame.")

            break

        # ---------------------------------------------
        # Run AI detection
        # ---------------------------------------------

        results = detector.detect(frame)

        # ---------------------------------------------
        # Print results
        # ---------------------------------------------

        print(
            f"\rFaces: {results['face_count']} | "
            f"Hands: {results['hands_detected']} | "
            f"Hands Below: {results['hands_below']} | "
            f"Head Turned: {results['head_turned']}",
            end=""
        )

        # ---------------------------------------------
        # Draw results on camera
        # ---------------------------------------------

        frame = detector.draw_results(
            frame,
            results
        )

        cv2.imshow(
            "AI Exam Monitoring Test",
            frame
        )

        # ---------------------------------------------
        # Exit
        # ---------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    # ---------------------------------------------
    # Cleanup
    # ---------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    detector.close()

    print()
    print()
    print("Monitoring test closed.")


if __name__ == "__main__":

    main()