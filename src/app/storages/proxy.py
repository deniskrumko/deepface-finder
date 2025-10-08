from pydantic import BaseModel


class S3Proxy(BaseModel):
    url: str
    bucket: str

    def get_proxy_path(self, filename: str, prefix: str = "") -> str:
        """Construct the full URL for accessing a file in S3."""
        parts = [self.url, self.bucket, filename]
        if prefix:
            parts.insert(2, prefix)

        return "/".join(part.strip("/") for part in parts if part)
