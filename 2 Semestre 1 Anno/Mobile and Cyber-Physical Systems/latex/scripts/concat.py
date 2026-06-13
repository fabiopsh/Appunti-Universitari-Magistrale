#!/usr/bin/env python3
"""Concatenate normalized <module>/md/Lezione*.md into a single <module>/appunti.md.

Usage: concat.py <module>
Normalizes header levels so each lesson starts at H1, inserts \\newpage between lessons.
Wikilink images are already resolved upstream, so they are NOT dropped here.
"""
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LATEX = SCRIPTS.parent

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
LESSON_NUM_RE = re.compile(r"Lezione\s+(\d+)")

SVG_URL_MAP = {
    "https://upload.wikimedia.org/wikipedia/commons/8/82/MQTT_protocol_example_without_QoS.svg":
        "images/MQTT_protocol_example_without_QoS.png",
    "https://upload.wikimedia.org/wikipedia/commons/2/2b/Wifi_hidden_station_problem.svg":
        "images/Wifi_hidden_station_problem.png",
    "https://upload.wikimedia.org/wikipedia/commons/f/f2/Multipath_propagation_diagram_en.svg":
        "images/Multipath_propagation_diagram_en.png",
}


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1).lstrip()


def rewrite_remote_svg(text: str) -> str:
    for url, local in SVG_URL_MAP.items():
        text = text.replace(url, local)
    return text


def shift_headers(text: str, delta: int) -> str:
    if delta == 0:
        return text

    def repl(m):
        hashes, title = m.group(1), m.group(2)
        new_level = max(1, min(6, len(hashes) + delta))
        return "#" * new_level + " " + title

    return HEADER_RE.sub(repl, text)


def normalize(text: str, fallback_title: str) -> str:
    text = strip_frontmatter(text)
    text = rewrite_remote_svg(text)

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
    m = LESSON_NUM_RE.search(path.stem)
    return int(m.group(1)) if m else 9999


def title_from_filename(stem: str) -> str:
    return stem.replace(" - ", " — ", 1)


def main(module: str):
    mod = LATEX / module
    src = mod / "md"
    out = mod / "appunti.md"

    lessons = sorted(src.glob("*.md"))

    parts = []
    for p in lessons:
        title = title_from_filename(p.stem)
        body = normalize(p.read_text(encoding="utf-8"), title)
        parts.append(body.rstrip() + "\n\n```{=latex}\n\\newpage\n```\n\n")

    out.write_text("".join(parts), encoding="utf-8")

    print(f"[{module}] Scritto {out}")
    print(f"  lezioni: {len(lessons)}")
    print(f"  righe:   {sum(1 for _ in out.open())}")


if __name__ == "__main__":
    main(sys.argv[1])
