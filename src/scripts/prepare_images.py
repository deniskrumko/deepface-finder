"""
Resize images in a directory and save them to a new directory.

Example:

PYTHONPATH=src py src/scripts/prepare_images.py \
    --src exports/samples \
    --dst exports/samples_resized
"""

from pathlib import Path

from app.image_processing.batch import batch_processing
from app.image_processing.utils import resize_image

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resize images in a directory")
    parser.add_argument("--src", help="Source directory with images")
    parser.add_argument("--dst", help="Destinaction directory for resized images")

    args = parser.parse_args()
    src_dir = Path(args.src)
    dst_dir = Path(args.dst)
    dst_dir.mkdir(parents=True, exist_ok=True)

    batch_processing(
        processing_func=resize_image,
        src_dir=src_dir,
        dst_dir=dst_dir,
        display_progress=True,
        raise_errors=False,
    )
