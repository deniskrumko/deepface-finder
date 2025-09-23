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
    region: str
    endpoint: str
    key: str
    secret: str
    bucket: str


class Project(LowercaseKeyMixin, BaseModel):
    name: str
    source: str
    original_images: str
    resized_images: str
    embeddings: str


class Settings(BaseModel):
    """App settings."""

    sources: dict[str, SourceBucket]
    projects: dict[str, Project]

    @classmethod
    def from_config(cls, config: Mapping) -> "Settings":
        settings = cls(
            sources={
                name: SourceBucket(**params) for name, params in config.get("sources", {}).items()
            },
            projects={
                name: Project(**params) for name, params in config.get("projects", {}).items()
            },
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
