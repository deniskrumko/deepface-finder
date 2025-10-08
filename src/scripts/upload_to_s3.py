"""
Upload original images, resized images and embeddings files to S3.

Example:

PYTHONPATH=src py src/scripts/upload_to_s3.py \
    --config config/test.toml \
    --original exports/samples \
    --resized exports/samples_resized \
    --embeddings exports/samples_embeddings
"""

from app.core.settings import get_settings
from app.image_processing.batch import batch_processing
from app.image_processing.face_embeddings import DEFAULT_EMBEDDING_EXT
from app.storages import S3Client


def main(
    config_path: str,
    original_dir: str = "exports/samples",
    resized_dir: str = "exports/samples_resized",
    embeddings_dir: str = "exports/samples_embeddings",
) -> None:
    settings = get_settings(config_path)
    s3_client = S3Client.from_config(settings.s3)

    print("Uploading original images")

    batch_processing(
        s3_client.upload_file_to_s3,
        src_dir=original_dir,
        dst_dir=settings.images.original,
        # Upload params
        bucket_name=settings.images.bucket,
    )

    print("Uploading resized images")

    batch_processing(
        s3_client.upload_file_to_s3,
        src_dir=resized_dir,
        dst_dir=settings.images.resized,
        # Upload params
        bucket_name=settings.images.bucket,
    )

    print("Uploading embeddings")

    batch_processing(
        s3_client.upload_file_to_s3,
        src_dir=embeddings_dir,
        dst_dir=settings.images.embeddings,
        allowed_extensions={DEFAULT_EMBEDDING_EXT},
        # Upload params
        bucket_name=settings.images.bucket,
    )

    print("Done")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload files to S3")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument(
        "--original",
        default="exports/samples",
        help="Directory with original images",
    )
    parser.add_argument(
        "--resized",
        default="exports/samples_resized",
        help="Directory with resized images",
    )
    parser.add_argument(
        "--embeddings",
        default="exports/samples_embeddings",
        help="Directory with embeddings files",
    )

    args = parser.parse_args()
    main(
        config_path=args.config,
        original_dir=args.original,
        resized_dir=args.resized,
        embeddings_dir=args.embeddings,
    )
