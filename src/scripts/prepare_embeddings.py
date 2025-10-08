"""
Resize images in a directory and save them to a new directory.

Example:

PYTHONPATH=src py src/scripts/prepare_embeddings.py \
    --src exports/samples \
    --dst exports/samples_embeddings \
    --config config/test.toml
"""

from pathlib import Path

from app.core.settings import get_settings
from app.image_processing.batch import batch_processing
from app.image_processing.face_embeddings import create_embeddings_file

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resize images in a directory")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--src", help="Source directory with images")
    parser.add_argument("--dst", help="Destination directory for embeddings")

    args = parser.parse_args()

    settings = get_settings(args.config)
    src_dir = Path(args.src)
    dst_dir = Path(args.dst)
    dst_dir.mkdir(parents=True, exist_ok=True)

    batch_processing(
        processing_func=create_embeddings_file,
        src_dir=src_dir,
        dst_dir=dst_dir,
        display_progress=True,
        raise_errors=False,
        # Function params
        model_name=settings.deepface.model_name,
        detector_backend=settings.deepface.detector_backend,
        min_face_size=settings.deepface.min_embeddings_face_size,
    )
