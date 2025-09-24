from pathlib import Path
from typing import Any

import boto3
from botocore.client import BaseClient


def get_s3_client(
    region: str,
    endpoint: str,
    key: str,
    secret: str,
    **kwargs: Any,
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


def list_files_in_s3_prefix(
    s3_client: BaseClient,
    bucket_name: str,
    s3_prefix: str,
) -> list[str]:
    """List all files in a specific S3 prefix.

    Args:
        s3_client (BaseClient): Boto3 S3 client
        bucket_name (str): S3 bucket name
        s3_prefix (str): S3 prefix to list files from
    """
    files = []
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

    for page in pages:
        for obj in page.get("Contents", []):
            files.append(obj["Key"])

    return files


def download_file_from_s3(
    s3_client: BaseClient,
    bucket_name: str,
    s3_key: str,
    local_path: str | Path,
) -> None:
    """Download a single file from S3 bucket.

    Args:
        s3_client (BaseClient): Boto3 S3 client
        bucket_name (str): S3 bucket name
        s3_key (str): S3 key of the file to download
        local_path (str | Path): Local path to save the downloaded file
    """
    local_dir = Path(local_path).parent
    local_dir.mkdir(parents=True, exist_ok=True)

    s3_client.download_file(
        Bucket=bucket_name,
        Key=s3_key,
        Filename=str(local_path),
    )


def download_dir_from_s3(
    s3_client: BaseClient,
    bucket_name: str,
    s3_prefix: str,
    local_dir: str | Path,
) -> None:
    """Download all files from a specific S3 prefix to a local directory.

    Args:
        s3_client (BaseClient): Boto3 S3 client
        bucket_name (str): S3 bucket name
        s3_prefix (str): S3 prefix to download files from
        local_dir (str | Path): Local directory to save the downloaded files
    """
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

    for page in pages:
        for obj in page.get("Contents", []):
            s3_key = obj["Key"]
            relative_path = Path(s3_key).relative_to(s3_prefix)
            local_file_path = local_dir / relative_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)

            s3_client.download_file(
                Bucket=bucket_name,
                Key=s3_key,
                Filename=str(local_file_path),
            )
