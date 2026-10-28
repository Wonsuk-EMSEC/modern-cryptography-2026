"""Bounded HTTP client for the local or instructor-hosted Lab03 target."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULT_TARGET_URL = "http://lab03-target:8080"
MAX_RESPONSE = 16_384
MAX_REQUEST = 16_384


class TargetError(RuntimeError):
    def __init__(self, status: int, response: dict):
        self.status = status
        self.response = response
        super().__init__(f"HTTP {status}: {response.get('error', 'target error')}")


class TargetClient:
    def __init__(self, url: str | None = None, timeout: float = 8):
        self.url = (url or os.environ.get("LAB03_TARGET_URL", DEFAULT_TARGET_URL)).rstrip("/")
        parsed = urlsplit(self.url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.query or parsed.fragment:
            raise ValueError("target URL must be an http(s) base URL")
        self.timeout = timeout

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        if method not in {"GET", "POST"} or not path.startswith("/") or path.startswith("//"):
            raise ValueError("invalid request")
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        if data is not None and len(data) > MAX_REQUEST:
            raise ValueError("request too large")
        request = Request(self.url + path, data=data, method=method, headers={"Content-Type": "application/json"})
        status = 200
        try:
            response = urlopen(request, timeout=self.timeout)
        except HTTPError as error:
            response, status = error, error.code
        except URLError as error:
            raise RuntimeError(f"Lab03 target unavailable: {error.reason}") from error
        with response:
            raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise RuntimeError("target response too large")
        try:
            result = json.loads(raw)
        except (ValueError, UnicodeError) as error:
            raise RuntimeError("target returned invalid JSON") from error
        if not isinstance(result, dict):
            raise RuntimeError("target response must be a JSON object")
        if status != 200:
            raise TargetError(status, result)
        return result
