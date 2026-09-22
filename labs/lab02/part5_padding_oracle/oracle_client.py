"""Boolean-only client for the fixed local padding oracle."""

from __future__ import annotations

import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.service_client import TargetConnection


class OracleClient:
    def __init__(self) -> None:
        self.target = TargetConnection()
        self.queries = 0

    def query(self, ciphertext: bytes) -> bool:
        self.queries += 1
        response = self.target.request(f"P5 QUERY {ciphertext.hex()}")
        if response == "LIMIT":
            raise RuntimeError("local query limit reached; restart the target after checking your loop")
        if response not in ("VALID", "INVALID"):
            raise RuntimeError(response)
        return response == "VALID"

    def close(self) -> None:
        self.target.close()

    def __enter__(self) -> "OracleClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
