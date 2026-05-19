#!/usr/bin/env python3
"""Find Obsidian ![[file.png]] wikilinks, copy referenced files into build/images/,
rewrite the link to ![](images/...)."""
import re
import shutil
import unicodedata
from pathlib import Path

BUILD = Path(__file__).resolve().parent
SRC = BUILD / "md"
IMG = BUILD / "images"
IMG.mkdir(exist_ok=True)

# Obsidian vault root — search globally for assets
VAULT_ROOT = Path("/Users/fabiopsh/Library/Mobile Documents/com~apple~CloudDocs/UNIPI - Magistrale Pisa/Unipi - Obsidian")

WIKILINK_RE = re.compile(r"!\[\[([^\]]+?)\]\]")


def slugify_filename(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    stem = Path(s).stem
    ext = Path(s).suffix
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
    return f"{stem}{ext}"


# Build index of vault image files (cached)
print("Indexing vault assets...")
INDEX = {}
for p in VAULT_ROOT.rglob("*"):
    if not p.is_file():
        continue
    if ".trash" in p.parts:
        continue
    if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf"):
        continue
    INDEX.setdefault(p.name, p)
print(f"  indexed {len(INDEX)} asset files")

total_resolved = 0
total_miss = 0

for md_file in sorted(SRC.glob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    if "![[" not in text:
        continue

    def repl(m):
        global total_resolved, total_miss
        target = m.group(1).strip()
        # Strip alt text after pipe ("![[file.png|alt]]")
        target = target.split("|", 1)[0].strip()
        # Strip optional anchor
        target = target.split("#", 1)[0].strip()
        if target not in INDEX:
            print(f"  ! MISS in {md_file.name}: {target}")
            total_miss += 1
            return ""
        src_path = INDEX[target]
        dest_name = slugify_filename(target)
        dest_path = IMG / dest_name
        if not dest_path.exists():
            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"  ! copy fail {target}: {e}")
                total_miss += 1
                return ""
        total_resolved += 1
        return f"![](images/{dest_name})"

    new_text = WIKILINK_RE.sub(repl, text)
    if new_text != text:
        md_file.write_text(new_text, encoding="utf-8")

print(f"\nResolved: {total_resolved}, missed: {total_miss}")
