from os import getenv
from pathlib import Path
from typing import Mapping

from dynaconf import Dynaconf
from pydantic import BaseModel

from app.image_processing.resources import (
    DeepfaceSettings,
    ImagesSettings,
)
from app.storages.resources import (
    ProxySettings,
    S3Settings,
)

from .utils import LowercaseKeyMixin

ENV_VAR_PREFIX = "DFF"


class UISettings(LowercaseKeyMixin, BaseModel):
    language: str = "en"
    branding_title: str | None = None
    branding_image: str | None = None
    branding_text: str | None = None


class Settings(BaseModel):
    """App settings."""

    ui: UISettings
    s3: S3Settings
    proxy: ProxySettings
    images: ImagesSettings
    deepface: DeepfaceSettings

    @classmethod
    def from_config(cls, config: Mapping) -> "Settings":
        return cls(
            ui=config.get("ui", {}),
            s3=config["s3"],
            proxy=config["proxy"],
            images=config["images"],
            deepface=config.get("deepface", {}),
        )


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
