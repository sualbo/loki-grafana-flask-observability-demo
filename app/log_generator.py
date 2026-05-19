"""Demo log generator used by /generate-logs endpoint."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class DemoLog:
    level: str
    message: str
    component: str


_MESSAGES: list[DemoLog] = [
    DemoLog("info", "User opened the home page", "web"),
    DemoLog("info", "Calculation request completed", "calculator"),
    DemoLog("info", "Application info endpoint called", "api"),
    DemoLog("warning", "Request latency is higher than expected", "api"),
    DemoLog("warning", "Demo cache miss detected", "cache"),
    DemoLog("error", "Demo payment provider timeout", "integration"),
    DemoLog("error", "Demo validation error: invalid numeric input", "calculator"),
    DemoLog("debug", "Debug trace for local observability demo", "debugger"),
]


def generate_demo_logs(count: int = 20) -> list[DemoLog]:
    """Return a bounded list of pseudo-random demo logs."""

    safe_count = min(max(count, 1), 100)
    return [random.choice(_MESSAGES) for _ in range(safe_count)]
