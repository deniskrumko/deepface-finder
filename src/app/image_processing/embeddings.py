from pathlib import Path

import numpy as np
import pandas as pd
from deepface import DeepFace
from pydantic import BaseModel

from .resources import (
    DEFAULT_DETECTOR_BACKEND,
    DEFAULT_EMBEDDING_EXT,
    DEFAULT_MODEL_NAME,
)
from .utils import get_image_content


class Face(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    face: np.ndarray
    facial_area: dict
    confidence: float

    def __repr__(self) -> str:
        return f"<Face ({self.confidence:.2f})>"


class FaceEmbedding(BaseModel):
    """Model for a face embedding."""

    filename: str
    model_name: str
    embedding: list[float]
    facial_area: dict
    face_confidence: float

    def __repr__(self) -> str:
        return f"<FaceEmbedding {self.filename}/{self.model_name} ({self.face_confidence:.2f})>"


def read_embeddings_file(path: str | Path) -> list[FaceEmbedding]:
    """Read list of ``FaceEmbedding`` from parquet file."""
    df = pd.read_parquet(path, engine="fastparquet")
    return [
        FaceEmbedding(**row)  # type:ignore
        for row in df.to_dict(orient="records")
    ]


def create_embeddings_file(
    image_path: str | Path,
    embedding_path: str | Path,
    embedding_ext: str = DEFAULT_EMBEDDING_EXT,
    skip_existing: bool = True,
) -> int:
    """Create list of ``FaceEmbedding`` and save them to parquet file."""
    if embedding_ext:
        embedding_path = Path(embedding_path).with_suffix(embedding_ext)

    if skip_existing and Path(embedding_path).exists():
        return -1  # skip existing

    embeddings = get_embeddings(image_path)
    df = pd.DataFrame([emb.model_dump() for emb in embeddings])
    df.to_parquet(embedding_path, index=False, engine="fastparquet")
    return len(embeddings)


def get_embeddings(
    image_path: str | Path,
    model_name: str = DEFAULT_MODEL_NAME,
    detector_backend: str = DEFAULT_DETECTOR_BACKEND,
) -> list[FaceEmbedding]:
    """Get list of ``FaceEmbedding`` from image file."""
    filename = Path(image_path).name
    faces = DeepFace.represent(
        str(image_path),
        model_name=model_name,
        detector_backend=detector_backend,
        enforce_detection=True,
    )
    return [
        FaceEmbedding(
            **face,  # type:ignore
            filename=filename,
            model_name=model_name,
        )
        for face in faces
    ]


def get_faces(
    image_path: str | Path, detector_backend: str = DEFAULT_DETECTOR_BACKEND
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
        if f["confidence"] and f["facial_area"]["w"] > 100 and f["facial_area"]["h"] > 100
    ]  # type:ignore


def find_similar_faces(
    faces: list[Face],
    embeddings: list[FaceEmbedding],
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[str]:
    if not faces:
        raise ValueError("Faces list is empty")

    if not embeddings:
        raise ValueError("Embeddings list is empty")

    results = DeepFace.recognition.find_batched(
        [e.model_dump() for e in embeddings],
        source_objs=[f.model_dump() for f in faces],
        model_name=model_name,
    )

    filenames = set()
    for face_results in results:
        for data in face_results:
            # if data['distance'] < 0.55:  # type:ignore
            filenames.add(str(data["filename"]))  # type:ignore

    return sorted(filenames)
