"""
PYTHONPATH=src py src/scripts/upload_to_s3.py
"""

from app.core.settings import get_settings
from app.image_processing import (
    DEFAULT_EMBEDDING_EXT,
    batch_processing,
    get_s3_client,
    upload_file_to_s3,
)


def main() -> None:
    settings = get_settings("config/test.toml")

    source = settings.sources["default"]
    project = settings.projects["kolesa_birthday_2025"]

    s3_client = get_s3_client(
        region=source.region,
        endpoint=source.endpoint,
        key=source.key,
        secret=source.secret,
    )

    print("Uploading original images")

    batch_processing(
        upload_file_to_s3,
        src_dir="exports/samples",
        dst_dir=project.original_images,
        # Upload params
        s3_client=s3_client,
        bucket_name=source.bucket,
    )

    print("Uploading resized images")

    batch_processing(
        upload_file_to_s3,
        src_dir="exports/samples_resized",
        dst_dir=project.resized_images,
        # Upload params
        s3_client=s3_client,
        bucket_name=source.bucket,
    )

    print("Uploading embeddings")

    batch_processing(
        upload_file_to_s3,
        src_dir="exports/samples_embeddings",
        dst_dir=project.embeddings,
        allowed_extensions={DEFAULT_EMBEDDING_EXT},
        # Upload params
        s3_client=s3_client,
        bucket_name=source.bucket,
    )

    print("Done")


if __name__ == "__main__":
    main()
