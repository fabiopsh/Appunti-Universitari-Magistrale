#!/usr/bin/env python3
"""Remove 'Possibili domande d'esame' blocks (callouts and headings) from build/md/*.md."""
import re
from pathlib import Path

BUILD = Path(__file__).resolve().parent
SRC = BUILD / "md"

# Match a > [!question] callout titled "Possibili domande" and all following lines starting with ">"
CALLOUT_RE = re.compile(
    r"(?ms)^>\s*\[!\w+\][^\n]*Possibili domande[^\n]*\n(?:^>.*\n)*",
)

# Match a heading "## Possibili domande..." (any level >=2) and content until next heading of same/higher level
HEADING_RE = re.compile(
    r"(?ms)^(#{1,6})\s*Possibili domande[^\n]*\n(?:(?!^#{1,6}\s).*\n)*",
)


def strip_to_next_heading(text: str) -> str:
    """Remove headings 'Possibili domande...' and content until next heading of same or higher level."""
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


total_removed = 0
for md_file in sorted(SRC.glob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    orig = text

    # Strip callouts
    new = CALLOUT_RE.sub("", text)
    if new != text:
        total_removed += 1
        text = new

    # Strip headings + content
    new = strip_to_next_heading(text)
    if new != text:
        if orig == text:
            total_removed += 1
        text = new

    if text != orig:
        # Clean up resulting double-blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        md_file.write_text(text, encoding="utf-8")

print(f"Files modified: {total_removed}")
