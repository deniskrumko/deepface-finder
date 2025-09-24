from os import getenv
from pathlib import Path
from typing import (
    Any,
    Mapping,
)

import pydantic
from dynaconf import Dynaconf
from pydantic import BaseModel

ENV_VAR_PREFIX = "DFF"


class LowercaseKeyMixin:
    """Mixin to normalize keys to lowercase before validation."""

    @pydantic.model_validator(mode="before")
    def normalize_keys(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k.lower(): v for k, v in data.items()}


class SourceBucket(LowercaseKeyMixin, BaseModel):
    type: str = "s3"
    region: str
    endpoint: str
    key: str
    secret: str
    bucket: str


class SourceLocalFolder(LowercaseKeyMixin, BaseModel):
    type: str = "filesystem"
    path: str


class Project(LowercaseKeyMixin, BaseModel):
    name: str
    source: str
    proxy: str
    original_images: str
    resized_images: str
    embeddings: str


class Proxy(LowercaseKeyMixin, BaseModel):
    url: str


class Settings(BaseModel):
    """App settings."""

    sources: dict[str, SourceBucket | SourceLocalFolder]
    proxies: dict[str, Proxy]
    projects: dict[str, Project]

    @classmethod
    def from_config(cls, config: Mapping) -> "Settings":
        # sources: dict[str, SourceBucket | SourceLocalFolder] = {}

        # for name, params in config.get("sources", {}).items():
        #     if params.get("type") == "filesystem":
        #         sources[name] = SourceLocalFolder(**params)  # type:ignore
        #     else:
        #         sources[name] = SourceBucket(**params)  # type:ignore

        settings = cls(
            sources=config["sources"],
            proxies=config["proxies"],
            projects=config["projects"],
        )

        return settings


SETTINGS: Settings | None = None


def init_settings(settings: Settings) -> None:
    if not isinstance(settings, Settings):
        raise TypeError("Settings must be <Settings> instance")

    global SETTINGS
    SETTINGS = settings


def get_settings(settings_file: str | Path | None = None) -> Settings:
    """Get settings from .toml file or env vars."""
    if SETTINGS is not None:
        return SETTINGS

    settings = Settings.from_config(
        Dynaconf(  # type:ignore
            envvar_prefix=ENV_VAR_PREFIX + "_",
            settings_file=settings_file or getenv("APP_CONFIG", "config/default.toml"),
        ),
    )

    init_settings(settings)
    return settings
