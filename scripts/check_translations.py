#!/usr/bin/env python3
"""Detect documentation changes since the last reviewed Korean/English pair."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "en" / ".translation-status.json"


def source_documents() -> list[str]:
    documents = {"README.md", "CONTRIBUTING.md"}
    for directory in ("docker", "labs"):
        documents.update(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / directory).rglob("*.md")
        )
    return sorted(documents)


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair_status(name: str) -> dict[str, str]:
    return {
        "korean_sha256": fingerprint(ROOT / name),
        "english_sha256": fingerprint(ROOT / "en" / name),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record",
        nargs="+",
        metavar="PATH",
        help="record reviewed translations; paths name Korean documents from repo root",
    )
    args = parser.parse_args()
    try:
        status = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {
            "version": 1, "documents": {}
        }
        if (
            not isinstance(status, dict)
            or status.get("version") != 1
            or not isinstance(status.get("documents"), dict)
        ):
            raise ValueError("unsupported translation status format")
    except (OSError, ValueError) as error:
        parser.exit(2, f"Cannot read translation status: {error}\n")

    documents = source_documents()
    recorded = status["documents"]
    if args.record:
        for name in args.record:
            if name not in documents:
                parser.error(f"not a Korean document in the translation scope: {name}")
            if not (ROOT / name).is_file() or not (ROOT / "en" / name).is_file():
                parser.error(f"both Korean and English documents must exist: {name}")
        for name in args.record:
            recorded[name] = pair_status(name)
        # Remove entries for deleted Korean sources when recording reviewed changes.
        status["documents"] = {name: recorded[name] for name in sorted(recorded) if name in documents}
        STATUS.parent.mkdir(parents=True, exist_ok=True)
        STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Recorded {len(set(args.record))} reviewed translation(s).")
        return 0

    problems = []
    for name in documents:
        if not (ROOT / name).is_file():
            problems.append(f"Missing Korean source: {name}")
        elif not (ROOT / "en" / name).is_file():
            problems.append(f"Missing English translation: en/{name}")
        elif name not in recorded:
            problems.append(f"Translation review not recorded: {name}")
        elif pair_status(name) != recorded[name]:
            problems.append(f"Translation review needed: {name} <-> en/{name}")
    for name in sorted(set(recorded) - set(documents)):
        problems.append(f"Korean source removed; review its English counterpart: {name}")
    for translation in sorted((ROOT / "en").rglob("*.md")):
        name = translation.relative_to(ROOT / "en").as_posix()
        if name not in documents:
            problems.append(f"English document has no source in translation scope: en/{name}")
    if problems:
        print("\n".join(problems))
        return 1
    print(f"All {len(documents)} translation pairs match their reviewed baselines.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
