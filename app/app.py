from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

from log_generator import generate_demo_logs
from loki_client import ALLOWED_LEVELS, send_log_to_loki

app = Flask(__name__)


def _result_to_dict(result: Any) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "status_code": result.status_code,
        "error": result.error,
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": os.getenv("APP_NAME", "my_app")})


@app.get("/")
def index():
    result = send_log_to_loki(
        "info",
        "Home endpoint called",
        endpoint="/",
        method=request.method,
        remote_addr=request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    return jsonify(
        {
            "message": "Flask + Loki + Grafana observability demo",
            "service": os.getenv("APP_NAME", "my_app"),
            "loki_delivery": _result_to_dict(result),
            "useful_urls": {
                "info": "/info",
                "calc": "/calc/2/3",
                "generate_logs": "/generate-logs?count=30",
            },
        }
    )


@app.get("/info")
def info():
    result = send_log_to_loki(
        "info",
        "Info endpoint called",
        endpoint="/info",
        method=request.method,
    )
    return jsonify(
        {
            "app": os.getenv("APP_NAME", "my_app"),
            "environment": os.getenv("APP_ENV", "demo"),
            "loki_push_url": os.getenv("LOKI_PUSH_URL", "http://loki:3100/loki/api/v1/push"),
            "loki_delivery": _result_to_dict(result),
        }
    )


@app.get("/calc/<a>/<b>")
def calc(a: str, b: str):
    try:
        first = float(a)
        second = float(b)
    except ValueError:
        result = send_log_to_loki(
            "error",
            "Calculation failed: invalid input",
            endpoint="/calc/<a>/<b>",
            a=a,
            b=b,
        )
        return (
            jsonify(
                {
                    "error": "Both URL parameters must be numeric.",
                    "example": "/calc/2/3",
                    "loki_delivery": _result_to_dict(result),
                }
            ),
            400,
        )

    total = first + second
    result = send_log_to_loki(
        "info",
        "Calculation request completed",
        endpoint="/calc/<a>/<b>",
        a=first,
        b=second,
        result=total,
    )
    return jsonify({"a": first, "b": second, "operation": "sum", "result": total, "loki_delivery": _result_to_dict(result)})


@app.get("/log/<level>")
def send_manual_log(level: str):
    normalized_level = level.lower().strip()
    if normalized_level not in ALLOWED_LEVELS:
        return (
            jsonify(
                {
                    "error": "Unsupported log level.",
                    "allowed_levels": sorted(ALLOWED_LEVELS),
                }
            ),
            400,
        )

    message = request.args.get("message") or f"Manual {normalized_level} log from demo endpoint"
    result = send_log_to_loki(
        normalized_level,
        message,
        endpoint="/log/<level>",
        source="manual",
    )
    return jsonify({"sent": _result_to_dict(result), "level": normalized_level, "message": message})


@app.get("/generate-logs")
def generate_logs():
    raw_count = request.args.get("count", "20")
    try:
        count = int(raw_count)
    except ValueError:
        count = 20

    logs = generate_demo_logs(count)
    delivery_results = []
    for index, log in enumerate(logs, start=1):
        result = send_log_to_loki(
            log.level,
            log.message,
            endpoint="/generate-logs",
            component=log.component,
            batch_index=index,
            batch_size=len(logs),
        )
        delivery_results.append(_result_to_dict(result))

    ok_count = sum(1 for item in delivery_results if item["ok"])
    return jsonify(
        {
            "requested_count": count,
            "generated_count": len(logs),
            "successfully_sent": ok_count,
            "failed": len(logs) - ok_count,
            "hint": "Open Grafana at http://localhost:3000 and check the Loki App Logs Demo dashboard.",
        }
    )


@app.errorhandler(404)
def not_found(_error):
    result = send_log_to_loki("warning", "Unknown endpoint requested", endpoint=request.path, method=request.method)
    return jsonify({"error": "Not found", "path": request.path, "loki_delivery": _result_to_dict(result)}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
