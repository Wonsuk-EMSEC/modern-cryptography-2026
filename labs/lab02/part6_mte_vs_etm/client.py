"""Client for locally named Service A and Service B."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.service_client import TargetConnection


class ServiceClient:
    def __init__(self, name: str) -> None:
        if name not in ("A", "B"):
            raise ValueError("service name must be A or B")
        self.name = name
        self.target = TargetConnection()
        self.queries = 0

    def item(self) -> bytes:
        response = self.target.request(f"P6 {self.name} ITEM")
        if not response.startswith("ITEM "):
            raise RuntimeError(response)
        return base64.b64decode(response.removeprefix("ITEM "), validate=True)

    def query(self, packet: bytes) -> str:
        self.queries += 1
        encoded = base64.b64encode(packet).decode("ascii")
        response = self.target.request(f"P6 {self.name} QUERY {encoded}")
        if response == "LIMIT":
            raise RuntimeError("local query limit reached")
        return response

    def padding_valid(self, packet: bytes) -> bool:
        return self.query(packet) in ("PADDING_OK", "ACCEPTED")

    def close(self) -> None:
        self.target.close()

    def __enter__(self) -> "ServiceClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
