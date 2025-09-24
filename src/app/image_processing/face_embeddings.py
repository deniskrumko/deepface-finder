from pathlib import Path
from typing import Any

import pandas as pd
from deepface import DeepFace

from .resources import (
    DEFAULT_DETECTOR_BACKEND,
    DEFAULT_EMBEDDING_EXT,
    DEFAULT_MODEL_NAME,
    FaceEmbedding,
)


def get_embeddings(
    image_path: str | Path,
    model_name: str = DEFAULT_MODEL_NAME,
    detector_backend: str = DEFAULT_DETECTOR_BACKEND,
    min_face_size: int = 20,
) -> list[FaceEmbedding]:
    """Get list of embeddings from image file."""
    filename = Path(image_path).name
    faces = DeepFace.represent(
        str(image_path),
        model_name=model_name,
        detector_backend=detector_backend,
        enforce_detection=False,
    )

    return [
        FaceEmbedding(
            **face,  # type:ignore
            filename=filename,
            model_name=model_name,
        )
        for face in faces
        if face["face_confidence"]  # type:ignore
        and face["facial_area"]["w"] > min_face_size  # type:ignore
        and face["facial_area"]["h"] > min_face_size  # type:ignore
    ]


def create_embeddings_file(
    image_path: str | Path,
    embedding_path: str | Path,
    embedding_ext: str = DEFAULT_EMBEDDING_EXT,
    skip_existing: bool = True,
    **kwargs: Any,
) -> int:
    """Get image embeddings and save them to parquet file."""
    embedding_path = Path(embedding_path)
    if embedding_ext:
        embedding_path = embedding_path.with_suffix(embedding_ext)

    if skip_existing and embedding_path.exists():
        return -1  # skip existing

    if not embedding_path.parent.exists():
        embedding_path.parent.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings(image_path=image_path, **kwargs)
    if not embeddings:
        return 0

    df = pd.DataFrame([emb.model_dump() for emb in embeddings])
    df.to_parquet(embedding_path, index=False, engine="fastparquet")
    return len(embeddings)


def read_embeddings_file(path: str | Path) -> list[FaceEmbedding]:
    """Read list of embeddings from parquet file."""
    df = pd.read_parquet(path, engine="fastparquet")
    return [
        FaceEmbedding(**row)  # type:ignore
        for row in df.to_dict(orient="records")
    ]


def read_embeddings_dir(
    path: str | Path,
    embedding_ext: str = DEFAULT_EMBEDDING_EXT,
) -> list[FaceEmbedding]:
    """Read list of embeddings from all parquet files in directory."""
    directory = Path(path)
    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    embeddings = []
    for emb_file in directory.glob(f"*.{embedding_ext.lstrip('.')}"):
        emb = read_embeddings_file(emb_file)
        embeddings.extend(emb)

    return embeddings
