#!/usr/bin/env python3
"""Remove 'Possibili domande d'esame' blocks (callouts and headings) from <module>/md/*.md.

Usage: strip_exam_questions.py <module>
"""
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LATEX = SCRIPTS.parent

# Match a > [!type] callout titled "Possibili domande" and all following ">" lines
CALLOUT_RE = re.compile(
    r"(?ms)^>\s*\[!\w+\][^\n]*Possibili domande[^\n]*\n(?:^>.*\n)*",
)


def strip_to_next_heading(text: str) -> str:
    """Remove 'Possibili domande...' headings and content until next heading of same/higher level."""
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+Possibili domande", line, re.IGNORECASE)
        if m:
            level = len(m.group(1))
            i += 1
            while i < len(lines):
                m2 = re.match(r"^(#{1,6})\s+", lines[i])
                if m2 and len(m2.group(1)) <= level:
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def main(module: str):
    src = LATEX / module / "md"
    total_removed = 0
    for md_file in sorted(src.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        orig = text

        new = CALLOUT_RE.sub("", text)
        if new != text:
            total_removed += 1
            text = new

        new = strip_to_next_heading(text)
        if new != text:
            if orig == text:
                total_removed += 1
            text = new

        if text != orig:
            text = re.sub(r"\n{3,}", "\n\n", text)
            md_file.write_text(text, encoding="utf-8")

    print(f"[{module}] File modificati (domande esame rimosse): {total_removed}")


if __name__ == "__main__":
    main(sys.argv[1])
