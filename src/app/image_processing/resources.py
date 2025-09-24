from typing import Any

import numpy as np
from pydantic import BaseModel

DEFAULT_MODEL_NAME = "Facenet"
DEFAULT_DETECTOR_BACKEND = "yolov8"
DEFAULT_EMBEDDING_EXT = ".parq"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".heic"}


class Face(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    face: np.ndarray
    facial_area: dict
    confidence: float

    def __repr__(self) -> str:
        return f"<Face ({self.confidence:.2f})>"


class FaceDetection(BaseModel):
    filename: str
    model_name: str
    facial_area: dict
    face_confidence: float

    def __hash__(self) -> int:
        return hash((self.filename, self.model_name))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FaceDetection):
            raise TypeError(f"Cannot compare {self} with {other}")

        return (self.filename, self.model_name) == (other.filename, other.model_name)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {self.filename}/{self.model_name} "
            f"({self.face_confidence:.2f})>"
        )


class FaceEmbedding(FaceDetection):
    """Model for a face embedding."""

    embedding: list[float]


class SimilarFace(FaceDetection):
    threshold: float
    distance: float
