from enum import Enum
from typing import (
    Any,
    Callable,
    TypeVar,
)

RENDER_HELPERS: dict = {}

F = TypeVar("F", bound=Callable[..., Any])


def register(fn: F) -> F:
    """Register a render helper function."""
    global RENDER_HELPERS  # noqa
    RENDER_HELPERS[fn.__name__] = fn
    return fn


class BootstrapLevel(Enum):
    """Bootstrap levels in UI."""

    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
