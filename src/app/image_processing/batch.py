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
    """Apply function to all images in src_dir and save to dst_dir."""
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
                print(f"{processing_func.__name__} {src_path} -> {dst_path}: {result!r}")  # noqa
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
