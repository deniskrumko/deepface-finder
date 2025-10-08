from pathlib import Path
from typing import (
    Any,
    Callable,
)

from .resources import IMAGE_EXTENSIONS


def batch_processing(
    processing_func: Callable,
    src_dir: str | Path,
    dst_dir: str | Path | None = None,
    display_progress: bool = True,
    raise_errors: bool = False,
    allowed_extensions: set[str] = IMAGE_EXTENSIONS,
    **processing_func_kwargs: Any,
) -> int:
    """Apply a processing function to all images in a source directory.

    Recursively processes all files in the source directory that match the allowed
    extensions, applying the specified processing function to each file. Optionally
    saves results to a destination directory maintaining the same directory structure.

    Args:
        processing_func (Callable): Function to apply to each image. Should accept
            either (src_path, **kwargs) or (src_path, dst_path, **kwargs) signature.
        src_dir (str | Path): Source directory containing images to process.
        dst_dir (str | Path | None, optional): Destination directory for processed
            images. If None, processing_func is called without dst_path. Defaults to None.
        display_progress (bool, optional): Whether to print progress messages and
            results. Defaults to True.
        raise_errors (bool, optional): Whether to raise exceptions on processing
            errors or continue with next file. Defaults to False.
        allowed_extensions (set[str], optional): Set of allowed file extensions
            to process. Defaults to IMAGE_EXTENSIONS.
        **processing_func_kwargs (Any): Additional keyword arguments to pass to
            the processing function.

    Returns:
        int: Number of successfully processed files.

    Example:
        >>> def resize_image(src_path, dst_path, size=(100, 100)):
        ...     # Image resizing logic here
        ...     return "resized"
        >>>
        >>> processed_count = batch_processing(
        ...     resize_image,
        ...     "input_images/",
        ...     "output_images/",
        ...     size=(200, 200)
        ... )
    """
    if not callable(processing_func):
        raise ValueError("processing_func must be a callable function")

    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir) if dst_dir else None

    if not src_dir.exists() or not src_dir.is_dir():
        raise ValueError(f"Source directory '{src_dir}' does not exist or is not a directory.")

    processed = 0

    for src_path in src_dir.rglob("*"):
        if allowed_extensions and src_path.suffix.lower() not in allowed_extensions:
            if display_progress:
                print(f"Skipping {src_path}")  # noqa
            continue

        relative_path = src_path.relative_to(src_dir)
        dst_path = (dst_dir / relative_path) if dst_dir else None

        try:
            if dst_path is None:
                result = processing_func(src_path, **processing_func_kwargs)
            else:
                result = processing_func(src_path, dst_path, **processing_func_kwargs)

            processed += 1
            if display_progress:
                result_repr = f": {result!r}" if result is not None else ""
                print(f"{processing_func.__name__} {src_path} -> {dst_path}{result_repr}")  # noqa
        except KeyboardInterrupt:
            if display_progress:
                print("Process interrupted by user.")  # noqa
            raise
        except Exception as e:
            if display_progress:
                print(f"Error processing {src_path}: {e}")  # noqa

            if raise_errors:
                raise e

    if display_progress:
        print(f"Total images processed: {processed}")  # noqa

    return processed
