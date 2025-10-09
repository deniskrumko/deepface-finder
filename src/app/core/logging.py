import json
import logging as base_logging
import sys
import time
import traceback
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Dict,
    Optional,
    Union,
)

from pydantic import BaseModel

from .utils import LowercaseKeyMixin

# Log levels presented same as we want them in JSON body
LOG_LEVEL_TO_NAME: Dict[int, str] = {
    base_logging.ERROR: "error",
    base_logging.WARNING: "warn",
    base_logging.INFO: "info",
    base_logging.DEBUG: "debug",
}

LOG_NAME_TO_LEVEL: Dict[str, int] = {v: k for k, v in LOG_LEVEL_TO_NAME.items()}
LOG_NAME_TO_LEVEL["warning"] = base_logging.WARNING


class LoggingSettings(LowercaseKeyMixin, BaseModel):
    """Logging settings."""

    level: Union[int, str] = "info"
    name: Optional[str] = None
    add_time: bool = False
    default_params: Optional[dict] = None


class ABCLogger(ABC):
    """Abstract class for logger."""

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize class instance."""

    @abstractmethod
    def with_params(self, **kwargs: Any) -> "ABCLogger":
        """Create new instance of logger with extra params."""

    @abstractmethod
    def log(self, message: str, level: Union[int, str], **kwargs: Any) -> None:
        """Log message with any level."""

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""

    @abstractmethod
    def exception(self, message: str, exception: Exception, **kwargs: Any) -> None:
        """Log exception message with traceback."""


class Logger(ABCLogger):
    """Basic JSON logger."""

    TIME_FIELD = "time"
    LEVEL_FIELD = "level"
    MSG_FIELD = "message"
    EXC_INFO_FIELD = "exc_info"
    TRACEBACK_FIELD = "traceback"

    def __init__(
        self,
        name: Optional[str] = None,
        level: Union[int, str] = base_logging.INFO,
        add_time: bool = False,
        default_params: Optional[dict] = None,
    ) -> None:
        """Initialize class instance.

        :param name: logger name
        :param level: default logger level
        :param add_time: if True then time field will be added
        :param default_params: dict with default params (added to all logs)
        """
        level_int = get_int_log_level(level)

        self.name = name
        self.level = level
        self.add_time = add_time
        self.default_params = default_params or {}

        self._logger = base_logging.getLogger(name)
        self._logger.setLevel(level_int)

        if not self._logger.handlers:
            stream = base_logging.StreamHandler(sys.stdout)
            stream.setLevel(level_int)
            self._logger.addHandler(stream)

    def with_params(self, **kwargs: Any) -> "Logger":
        """Create new instance of logger with extra default params."""
        return self.__class__(
            name=self.name,
            level=self.level,
            add_time=self.add_time,
            default_params={**self.default_params, **kwargs},
        )

    def log(self, message: str, level: Union[int, str], **kwargs: Any) -> None:
        """Log message with any level."""
        level_int = get_int_log_level(level)
        self._log_message(message, level_int, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log_message(message, base_logging.INFO, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log_message(message, base_logging.DEBUG, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log_message(message, base_logging.WARNING, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log_message(message, base_logging.ERROR, **kwargs)

    def exception(self, message: str, exception: Exception, **kwargs: Any) -> None:
        """Log exception message with traceback."""
        level = base_logging.ERROR
        message_dict = self._get_default_dict(message, level, **kwargs)
        message_dict[self.EXC_INFO_FIELD] = repr(exception)
        message_dict[self.TRACEBACK_FIELD] = "".join(
            traceback.format_exception(None, exception, exception.__traceback__),
        )
        self._log_dict(message_dict, level)

    # Helper methods
    # =============================================================================================

    def _get_default_dict(self, message: str, level: int, **kwargs: Any) -> dict:
        """Get default dictionary for logging."""
        result = {
            self.MSG_FIELD: message,
            self.LEVEL_FIELD: LOG_LEVEL_TO_NAME[level],
        }

        if self.add_time:
            result[self.TIME_FIELD] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if self.default_params is not None:
            result.update(self.default_params)

        result.update(kwargs)
        return result

    def _log_message(self, message: str, level: int, **kwargs: Any) -> None:
        """Log message with custom level as JSON."""
        message_dict = self._get_default_dict(message, level, **kwargs)
        self._log_dict(message_dict, level)

    def _log_dict(self, msg_dict: dict, level: int) -> None:
        """Log dictionary with custom level as JSON."""
        self._logger.log(level, json.dumps(msg_dict, ensure_ascii=False))


def get_int_log_level(level: Union[int, str]) -> int:
    """Get int integer representation of log level."""
    if isinstance(level, str):
        try:
            return LOG_NAME_TO_LEVEL[level.lower()]
        except KeyError:
            raise ValueError(f"Unknown log level {level}")
    elif isinstance(level, int):
        return level

    raise TypeError(f"Wrong log level type ({type(level)})")


class NoopLogger(ABCLogger):
    """Logger that discards all logs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize class instance."""

    def with_params(self, **kwargs: Any) -> "ABCLogger":
        """Create new instance of logger with extra params."""
        return self.__class__(**kwargs)

    def log(self, message: str, level: Union[int, str], **kwargs: Any) -> None:
        """Log message with any level."""
        get_int_log_level(level)  # to check valid level

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""

    def exception(self, message: str, exception: Exception, **kwargs: Any) -> None:
        """Log exception message with traceback."""
