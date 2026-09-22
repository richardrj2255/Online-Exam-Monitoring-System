import cv2
import numpy as np

from insightface.app import FaceAnalysis


print(">>> face_verifier.py loaded")


class FaceVerifier:

    def __init__(self):

        print(">>> FaceVerifier initialized")

        self.app = FaceAnalysis(
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    ########################################################
    # Get Face Embedding
    ########################################################

    def get_embedding(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            print("Unable to read:", image_path)
            return None

        faces = self.app.get(image)

        if len(faces) == 0:
            print("No face detected:", image_path)
            return None

        return faces[0].embedding

    ########################################################
    # Cosine Similarity
    ########################################################

    def cosine_similarity(self, emb1, emb2):

        emb1 = np.array(emb1)
        emb2 = np.array(emb2)

        return np.dot(
            emb1,
            emb2
        ) / (
            np.linalg.norm(emb1)
            *
            np.linalg.norm(emb2)
        )

    ########################################################
    # Verify Face
    ########################################################

    def verify_face(
        self,
        registered_image,
        captured_image
    ):

        registered_embedding = self.get_embedding(
            registered_image
        )

        if registered_embedding is None:
            return False, "No face found in registered photo."

        captured_embedding = self.get_embedding(
            captured_image
        )

        if captured_embedding is None:
            return False, "No face detected from webcam."

        similarity = self.cosine_similarity(
            registered_embedding,
            captured_embedding
        )

        print(f"Similarity : {similarity:.4f}")

        THRESHOLD = 0.60

        if similarity >= THRESHOLD:
            return True, "Face Verified"

        return False, "Face Mismatch"