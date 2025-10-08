from pydantic import BaseModel

from app.core.utils import LowercaseKeyMixin


class S3Settings(LowercaseKeyMixin, BaseModel):
    region: str
    endpoint: str
    key: str
    secret: str


class ProxySettings(LowercaseKeyMixin, BaseModel):
    url: str
