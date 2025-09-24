from pathlib import Path

from deepface import DeepFace

from .resources import (
    DEFAULT_DETECTOR_BACKEND,
    DEFAULT_MODEL_NAME,
    Face,
    FaceEmbedding,
    SimilarFace,
)
from .utils import get_image_content


def get_faces(
    image_path: str | Path,
    detector_backend: str = DEFAULT_DETECTOR_BACKEND,
    min_face_size: int = 100,
) -> list[Face]:
    image_bytes = get_image_content(image_path)
    target_faces = DeepFace.extract_faces(
        image_bytes,
        enforce_detection=False,
        detector_backend=detector_backend,
    )
    return [
        Face(**f)
        for f in target_faces
        if f["confidence"]
        and f["facial_area"]["w"] > min_face_size
        and f["facial_area"]["h"] > min_face_size
    ]  # type:ignore


def find_similar_faces(
    faces: list[Face],
    embeddings: list[FaceEmbedding],
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[SimilarFace]:
    if not faces:
        raise ValueError("Faces list is empty")

    if not embeddings:
        raise ValueError("Embeddings list is empty")

    results = DeepFace.recognition.find_batched(
        [e.model_dump() for e in embeddings],
        source_objs=[f.model_dump() for f in faces],
        model_name=model_name,
    )

    similar_faces = set()
    for face_results in results:
        for data in face_results:
            # Convert numpy types to native Python types
            converted_data = {k: v.item() if hasattr(v, "item") else v for k, v in data.items()}
            similar_faces.add(SimilarFace(**converted_data))

    return sorted(similar_faces, key=lambda sf: sf.distance)
