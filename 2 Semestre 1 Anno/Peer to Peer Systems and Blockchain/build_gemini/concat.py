#!/usr/bin/env python3
"""Concatenate normalized .md files into a single appunti.md (P2P version)."""
import re
from pathlib import Path

BUILD = Path(__file__).resolve().parent
SRC = BUILD / "md"
OUT = BUILD / "appunti.md"

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
LEFTOVER_WIKILINK_RE = re.compile(r"!\[\[[^\]]+\]\]")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1).lstrip()


def remove_leftover_wikilink_images(text: str) -> str:
    return LEFTOVER_WIKILINK_RE.sub("", text)


def shift_headers(text: str, delta: int) -> str:
    if delta == 0:
        return text

    def repl(m):
        hashes, title = m.group(1), m.group(2)
        new_level = len(hashes) + delta
        new_level = max(1, min(6, new_level))
        return "#" * new_level + " " + title

    return HEADER_RE.sub(repl, text)


def normalize(text: str, fallback_title: str) -> str:
    text = strip_frontmatter(text)
    text = remove_leftover_wikilink_images(text)
    # Repair: form-feed (0x0C) char in markdown was originally "\f" in a LaTeX macro
    # (e.g. \frac) but got serialized as literal FF char. Restore as backslash-f.
    text = text.replace("\x0c", "\\f")

    headers = HEADER_RE.findall(text)
    levels = [len(h[0]) for h in headers]

    if not levels:
        return f"# {fallback_title}\n\n{text}"

    min_level = min(levels)
    if min_level > 1:
        text = shift_headers(text, -(min_level - 1))
        levels = [l - (min_level - 1) for l in levels]

    h1_count = sum(1 for l in levels if l == 1)

    if h1_count == 0:
        text = f"# {fallback_title}\n\n{text}"
    elif h1_count >= 2:
        text = shift_headers(text, +1)
        text = f"# {fallback_title}\n\n{text}"

    return text


def lesson_sort_key(path: Path):
    m = re.match(r"Lezione\s+(\d+)", path.stem)
    return int(m.group(1)) if m else 9999


def title_from_filename(stem: str) -> str:
    return stem.replace(" - ", " — ", 1)


def dedupe_by_lesson_number(paths):
    by_num = {}
    for p in paths:
        m = re.match(r"Lezione\s+(\d+)", p.stem)
        if not m:
            continue
        n = int(m.group(1))
        if n not in by_num or len(p.stem) < len(by_num[n].stem):
            by_num[n] = p
    return sorted(by_num.values(), key=lesson_sort_key)


def dedupe_progetto(paths):
    by_key = {}
    for p in paths:
        key = re.sub(r"\s+2$", "", p.stem)
        if key not in by_key or len(p.stem) < len(by_key[key].stem):
            by_key[key] = p
    return sorted(by_key.values())


lessons = dedupe_by_lesson_number(SRC.glob("Lezione*.md"))

parts = []
for p in lessons:
    title = title_from_filename(p.stem)
    body = normalize(p.read_text(encoding="utf-8"), title)
    parts.append(body.rstrip() + "\n\n```{=latex}\n\\newpage\n```\n\n")

OUT.write_text("".join(parts), encoding="utf-8")

print(f"Scritto {OUT}")
print(f"  lezioni: {len(lessons)}")
print(f"  righe:   {sum(1 for _ in OUT.open())}")
