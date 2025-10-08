import logging
from pathlib import Path

from app.core.fastapi import init_fastapi_app
from app.core.settings import get_settings
from app.image_processing.face_embeddings import read_embeddings_dir
from app.storages import (
    S3Client,
    S3Proxy,
)

logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = init_fastapi_app()

settings = get_settings()
app.settings = settings  # type:ignore

s3_client = S3Client.from_config(settings.s3)
app.s3_client = s3_client  # type:ignore

s3_proxy = S3Proxy(
    url=settings.proxy.url,
    bucket=settings.images.bucket,
)
app.s3_proxy = s3_proxy  # type:ignore


def load_files_lists() -> None:
    """Load lists of image and embedding files from S3."""
    for attr in ("original", "resized", "embeddings"):
        objects = s3_client.list_files_in_s3_prefix(
            bucket_name=settings.images.bucket,
            s3_prefix=getattr(settings.images, attr),
        )

        if not objects:
            raise ValueError(f"No {attr} objects found")

        setattr(app, f"{attr}_list", objects)


def load_embeddings() -> None:
    """Load face embeddings for all configured projects."""
    embeddings_list: list[str] = app.embeddings_list  # type:ignore
    if not embeddings_list:
        raise ValueError("No embedding files found")

    embeddings_dir = Path("/tmp/embeddings")
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    for filename in embeddings_list:
        local_path = embeddings_dir / Path(filename).name
        if local_path.exists():
            logger.info(f"Embedding already exists: {local_path}")
            continue

        s3_client.download_file_from_s3(
            bucket_name=settings.images.bucket,
            s3_key=filename,
            local_path=local_path,
        )
        logger.info(f"Downloaded embedding: {local_path}")

    app.embeddings = read_embeddings_dir(embeddings_dir)  # type:ignore


load_files_lists()
load_embeddings()
