"""Small Loki Push API client for the demo Flask application.

The client intentionally avoids high-cardinality labels. Request details are
stored inside the JSON log line, while labels remain stable: app, level, env.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests
from requests import Response


ALLOWED_LEVELS = {"debug", "info", "warning", "error", "critical"}


@dataclass(frozen=True)
class LokiResult:
    """Result of an attempt to send one log entry to Loki."""

    ok: bool
    status_code: int | None = None
    error: str | None = None


def _safe_timeout() -> float:
    raw_value = os.getenv("LOKI_TIMEOUT_SECONDS", "3")
    try:
        return max(0.5, float(raw_value))
    except ValueError:
        return 3.0


def _normalize_level(level: str) -> str:
    normalized = (level or "info").lower().strip()
    if normalized not in ALLOWED_LEVELS:
        return "info"
    return normalized


def build_loki_payload(level: str, message: str, **fields: Any) -> dict[str, Any]:
    """Build a JSON payload for Loki /loki/api/v1/push.

    Loki Push API expects timestamps as strings. Epoch values are interpreted as
    Unix timestamps in nanoseconds, so time.time_ns() is a natural fit here.
    """

    app_name = os.getenv("APP_NAME", "my_app")
    app_env = os.getenv("APP_ENV", "demo")
    normalized_level = _normalize_level(level)

    log_line = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": app_name,
        "env": app_env,
        "level": normalized_level,
        "message": message,
        **{key: value for key, value in fields.items() if value is not None},
    }

    return {
        "streams": [
            {
                "stream": {
                    "app": app_name,
                    "env": app_env,
                    "level": normalized_level,
                },
                "values": [[str(time.time_ns()), json.dumps(log_line, ensure_ascii=False)]],
            }
        ]
    }


def send_log_to_loki(level: str, message: str, **fields: Any) -> LokiResult:
    """Send a single log entry to Loki.

    The application should remain usable even if Loki is temporarily unavailable,
    so this function returns a structured result instead of raising exceptions to
    Flask route handlers.
    """

    loki_push_url = os.getenv("LOKI_PUSH_URL", "http://loki:3100/loki/api/v1/push")
    payload = build_loki_payload(level=level, message=message, **fields)

    try:
        response: Response = requests.post(
            loki_push_url,
            json=payload,
            timeout=_safe_timeout(),
        )
        if response.status_code == 204:
            return LokiResult(ok=True, status_code=response.status_code)

        error_text = response.text.strip()[:500] or "Unexpected Loki response"
        return LokiResult(ok=False, status_code=response.status_code, error=error_text)
    except requests.RequestException as exc:
        return LokiResult(ok=False, error=str(exc))
