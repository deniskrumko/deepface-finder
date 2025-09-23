from pathlib import Path

import boto3
from botocore.client import BaseClient


def get_s3_client(
    region: str,
    endpoint: str,
    key: str,
    secret: str,
) -> BaseClient:
    """Create Boto3 S3 client."""
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=endpoint,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
    )


def upload_file_to_s3(
    src_path: str | Path,
    dst_path: str | Path,
    s3_client: BaseClient,
    bucket_name: str,
) -> None:
    """Upload a single file to S3 bucket

    Args:
        src_path (str): Path to the file to upload
        dst_path (str): Destination path in the S3 bucket
        s3_client (BaseClient): Boto3 S3 client
        bucket_name (str): S3 bucket name
    """
    src_path = Path(src_path)
    if not src_path.exists() or not src_path.is_file():
        raise ValueError(f"File '{src_path}' does not exist or is not a file")

    s3_client.upload_file(
        Filename=str(src_path),
        Bucket=bucket_name,
        Key=str(dst_path),
    )
