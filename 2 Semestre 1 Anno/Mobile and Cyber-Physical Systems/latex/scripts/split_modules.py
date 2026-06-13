#!/usr/bin/env python3
"""Split lesson notes into two module folders by the '(Lab)' tag in the filename.

  filename contains "(Lab)"  -> paganelli/src   (modulo Lab)
  otherwise                  -> chessa/src      (modulo non-Lab)

Copies the raw `Lezione N - *.md` files; deduplicates iCloud '* 2.md' copies.
Rebuilds <module>/src/ from scratch on every run (idempotent).
"""
import re
import shutil
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LATEX = SCRIPTS.parent
COURSE = LATEX.parent

LAB_MODULE = "paganelli"
NONLAB_MODULE = "chessa"

LESSON_RE = re.compile(r"^Lezione\s+(\d+)\b")


def module_for(name: str) -> str:
    return LAB_MODULE if "(Lab)" in name else NONLAB_MODULE


def dedupe_icloud(paths):
    """Drop iCloud ' 2.md' duplicates: keep the shortest stem per lesson number."""
    by_num = {}
    for p in paths:
        m = LESSON_RE.match(p.stem)
        if not m:
            continue
        n = int(m.group(1))
        if n not in by_num or len(p.stem) < len(by_num[n].stem):
            by_num[n] = p
    return sorted(by_num.values(), key=lambda p: int(LESSON_RE.match(p.stem).group(1)))


def main():
    lessons = dedupe_icloud(COURSE.glob("Lezione*.md"))

    # Fresh src/ dirs
    for mod in (LAB_MODULE, NONLAB_MODULE):
        src = LATEX / mod / "src"
        if src.exists():
            shutil.rmtree(src)
        src.mkdir(parents=True)

    counts = {LAB_MODULE: [], NONLAB_MODULE: []}
    for p in lessons:
        mod = module_for(p.name)
        shutil.copy2(p, LATEX / mod / "src" / p.name)
        counts[mod].append(int(LESSON_RE.match(p.stem).group(1)))

    for mod, nums in counts.items():
        nums.sort()
        tag = "Lab" if mod == LAB_MODULE else "non-Lab"
        print(f"{mod:10s} ({tag}): {len(nums):2d} lezioni -> {nums}")


if __name__ == "__main__":
    main()
