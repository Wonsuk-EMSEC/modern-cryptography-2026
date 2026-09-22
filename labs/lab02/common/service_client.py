"""Fixed local target connection used by Parts 4–6."""

from __future__ import annotations

import socket

TARGET_HOST = "lab02-target"
TARGET_PORT = 8080
MAX_RESPONSE = 1_000_000
MAX_REQUEST = 16_384


class TargetConnection:
    def __init__(self) -> None:
        self._socket = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=10)
        self._stream = self._socket.makefile("rwb")

    def request(self, command: str) -> str:
        if "\n" in command or len(command) > MAX_REQUEST:
            raise ValueError("invalid request")
        self._stream.write(command.encode("ascii") + b"\n")
        self._stream.flush()
        response = self._stream.readline(MAX_RESPONSE + 1)
        if not response or len(response) > MAX_RESPONSE:
            raise RuntimeError("target closed the connection or returned too much data")
        return response.rstrip(b"\r\n").decode("ascii")

    def close(self) -> None:
        try:
            self._stream.close()
        finally:
            self._socket.close()

    def __enter__(self) -> "TargetConnection":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
