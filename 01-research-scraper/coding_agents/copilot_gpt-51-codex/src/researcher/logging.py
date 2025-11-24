from __future__ import annotations

import logging
import sys
from typing import Any, Dict

import orjson


class ORJSONFormatter(logging.Formatter):
    """Structured log formatter using orjson for fast serialization."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key.startswith('_') or key in payload:
                continue
            try:
                orjson.dumps({key: value})
            except TypeError:
                continue
            payload[key] = value
        return orjson.dumps(payload).decode('utf-8')


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(ORJSONFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

