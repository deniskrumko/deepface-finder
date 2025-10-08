from contextlib import suppress
from typing import Any

import pydantic

VERSION_UNDEFINED = "undefined"


def get_version() -> str | None:
    """Get app version."""
    with suppress(Exception), open(".version", "r") as f:
        if (version := f.read().strip()) != VERSION_UNDEFINED:
            return version
    return None


def make_list(value: Any) -> list:
    """Convert value to list if not already."""
    return [value] if not isinstance(value, list) else value


def flatten_dict(data: dict, parent_key: str = "", sep: str = ".") -> dict:
    items = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


class LowercaseKeyMixin:
    """Mixin to normalize keys to lowercase before validation."""

    @pydantic.model_validator(mode="before")
    def normalize_keys(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k.lower(): v for k, v in data.items()}
