#!/usr/bin/env python3
"""Render the five student-facing Lab 01 part READMEs as simple PDF documents."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "lab01"
PARTS = (
    "part1_hashing",
    "part2_dictionary_attack",
    "part3_password_kdfs",
    "part4_system_hashes",
    "part5_wpa2",
)

UNICODE_FALLBACKS = str.maketrans(
    {
        "→": "->",
        "–": "-",
        "—": "-",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "≤": "<=",
        "≥": ">=",
        "×": "x",
    }
)


def pdf_escape(text: str) -> str:
    """Escape a Latin-1 string for use inside a PDF literal string."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def markdown_lines(markdown: str) -> list[tuple[str, str, int]]:
    """Convert the small Markdown subset used by the lab into styled lines."""
    output: list[tuple[str, str, int]] = []
    in_code = False
    for raw in markdown.splitlines():
        if raw.startswith("```"):
            in_code = not in_code
            output.append(("", "F2", 9))
            continue

        line = raw.translate(UNICODE_FALLBACKS).encode("latin-1", "replace").decode("latin-1")
        if in_code:
            wrapped = textwrap.wrap(line, width=92, replace_whitespace=False) or [""]
            output.extend((item, "F2", 9) for item in wrapped)
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2)
            output.append(("", "F1", 10))
            output.append((text, "F1", {1: 18, 2: 14, 3: 12}[level]))
            continue

        line = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", line)
        line = line.replace("**", "").replace("`", "")
        indent = "  " if line.startswith(("- ", "1. ", "2. ", "3. ", "4. ", "5. ")) else ""
        wrapped = textwrap.wrap(
            line,
            width=92,
            initial_indent=indent,
            subsequent_indent="    " if indent else "",
        ) or [""]
        output.extend((item, "F1", 10) for item in wrapped)
    return output


def content_stream(lines: list[tuple[str, str, int]]) -> bytes:
    commands = ["BT", "54 760 Td"]
    current_font = ""
    for text, font, size in lines:
        if font != current_font:
            commands.append(f"/{font} {size} Tf")
            current_font = font
        else:
            commands.append(f"/{font} {size} Tf")
        commands.append(f"({pdf_escape(text)}) Tj")
        commands.append("0 -14 Td")
    commands.append("ET")
    return "\n".join(commands).encode("latin-1")


def write_pdf(lines: list[tuple[str, str, int]], destination: Path) -> None:
    """Write a dependency-free PDF 1.4 document with paginated text."""
    pages = [lines[index : index + 51] for index in range(0, len(lines), 51)] or [[]]
    page_count = len(pages)
    helvetica_id = 3 + 2 * page_count
    courier_id = helvetica_id + 1
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + 2 * index} 0 R" for index in range(page_count))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode())
    for index, page_lines in enumerate(pages):
        content_id = 4 + 2 * index
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {helvetica_id} 0 R /F2 {courier_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode()
        )
        stream = content_stream(page_lines)
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(document))
        document.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(document)
    document.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode())
    document.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    destination.write_bytes(document)


def main() -> None:
    for part in PARTS:
        source = LAB / part / "README.md"
        destination = LAB / part / f"{part.upper()}_GUIDE.pdf"
        write_pdf(markdown_lines(source.read_text(encoding="utf-8")), destination)
        print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()
