#!/usr/bin/env python3
"""Substitui U+2014 (travessão) e U+2013 (meia-raia) por pontuação ASCII.

Útil se novos textos trouxerem esses caracteres de novo. Uso:
  python scripts/replace_typographic_dashes.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".py", ".html", ".md", ".css", ".txt", ".sh", ".json", ".toml", ".ini"}
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    ".cursor",
}

EM = "\u2014"
EN = "\u2013"


def transform(content: str) -> str:
    s = content

    s = s.replace(f"<td>{EM}</td>", "<td>-</td>")
    s = s.replace(f"{EM} em branco {EM}", "(em branco)")
    s = s.replace(f"|| '{EM}'", "|| '-'")
    s = s.replace(f'|| "{EM}"', '|| "-"')

    s = re.sub(rf"(\d){EN}(\d)", r"\1-\2", s)
    s = re.sub(rf"(\d){EM}(\d)", r"\1-\2", s)

    s = s.replace(f" {EM} ", ", ")
    s = s.replace(f" {EN} ", " - ")

    s = s.replace(EM, ", ")
    s = s.replace(EN, "-")

    s = re.sub(r",\s*,", ", ", s)

    return s


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(should_skip_dir(p) for p in path.relative_to(ROOT).parts):
            continue
        raw = path.read_text(encoding="utf-8")
        new = transform(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
            print(path.relative_to(ROOT))
    print(f"Arquivos alterados: {changed}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
