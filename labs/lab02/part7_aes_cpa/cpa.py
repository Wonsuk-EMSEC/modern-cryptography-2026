#!/usr/bin/env python3
"""Compatibility entry point for the student-written aes_cpa.py program."""

from __future__ import annotations

from importlib import import_module


def __getattr__(name: str):
    """Resolve old imports only when completed student code is actually used."""
    module = import_module(".aes_cpa", __package__) if __package__ else import_module("aes_cpa")
    try:
        return getattr(module, name)
    except AttributeError:
        raise AttributeError(f"implement {name} in aes_cpa.py first") from None


if __name__ == "__main__":
    try:
        main = __getattr__("main")
    except AttributeError as error:
        raise SystemExit(str(error)) from None
    main()
