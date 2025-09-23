"""
Resize images in a directory and save them to a new directory.

Example:

PYTHONPATH=src py src/scripts/prepare_embeddings.py exports/samples exports/samples_embeddings
"""

from pathlib import Path

from app.image_processing import (
    batch_processing,
    create_embeddings_file,
)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resize images in a directory")
    parser.add_argument("src_dir", help="Source directory with images")
    parser.add_argument("dst_dir", help="Destination directory for embeddings")

    args = parser.parse_args()
    src_dir = Path(args.src_dir)
    dst_dir = Path(args.dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    batch_processing(
        create_embeddings_file,
        src_dir,
        dst_dir,
        display_progress=True,
        raise_errors=False,
    )
