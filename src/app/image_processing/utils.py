from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def get_image_content(image_path: str | Path) -> np.ndarray:
    """Get image content as numpy array in BGR format."""
    image_path = Path(image_path)

    with Image.open(image_path) as img:
        if img.format in ("HEIC", "HEIF"):
            # Convert HEIC to RGB
            rgb_img = img.convert("RGB")
            # Convert PIL RGB to numpy array
            rgb_array = np.array(rgb_img)
            # Convert RGB to BGR
            bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
            return bgr_array

    # Use OpenCV to read directly as BGR
    return cv2.imread(str(image_path))  # type:ignore


def resize_image(
    src: str | Path,
    dst: str | Path,
    max_width: int = 1200,
    max_height: int = 900,
) -> None:
    """Resize an image to fit max dimensions while maintaining aspect ratio.

    Args:
        src: Source image path
        dst: Destination image path
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
    """
    src_path = Path(src)
    dst_path = Path(dst)

    with Image.open(src_path) as img:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Create destination directory if it doesn't exist
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        img.save(dst_path, optimize=True)
