from pathlib import Path

import numpy as np
from deepface import DeepFace

from .resources import (
    Face,
    FaceEmbedding,
    SimilarFace,
)
from .utils import (
    get_image_content,
    get_image_content_from_bytes,
)


def get_faces(
    image: str | Path | bytes,
    detector_backend: str,
    min_face_size: int = 100,
) -> list[Face]:
    """Detect and extract faces from an image file.

    Args:
        image_path (str | Path): Path to the image file.
        detector_backend (str, optional): Face detection backend to use.
            Defaults to DEFAULT_DETECTOR_BACKEND.
        min_face_size (int, optional): Minimum size (in pixels) for detected faces.
            Faces smaller than this will be ignored. Defaults to 100.

    Returns:
        list[Face]: List of detected faces with details.
    """
    image_bytes: np.ndarray

    if isinstance(image, bytes):
        image_bytes = get_image_content_from_bytes(image)
    elif isinstance(image, (str, Path)):
        image_bytes = get_image_content(image)
    else:
        raise TypeError("image_path must be str, Path, or bytes")

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
    model_name: str,
) -> list[SimilarFace]:
    """Find similar faces from a list of face embeddings.

    Args:
        faces (list[Face]): List of Face objects to find similarities for.
        embeddings (list[FaceEmbedding]): List of known face embeddings to compare against.
        model_name (str, optional): Name of the face recognition model to use.
            Defaults to DEFAULT_MODEL_NAME.

    Returns:
        list[SimilarFace]: Sorted list of similar faces found.
    """
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
