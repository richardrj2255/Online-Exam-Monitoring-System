import sys

from ai.face_verifier import FaceVerifier


def main():

    if len(sys.argv) != 3:
        print("FAILED")
        return

    registered_photo = sys.argv[1]
    captured_photo = sys.argv[2]

    verifier = FaceVerifier()

    success, message = verifier.verify_face(
        registered_photo,
        captured_photo
    )

    print(message)

    if success:
        print("VERIFIED")
    else:
        print("FAILED")


if __name__ == "__main__":
    main()