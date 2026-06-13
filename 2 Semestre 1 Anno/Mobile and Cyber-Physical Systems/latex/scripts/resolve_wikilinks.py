#!/usr/bin/env python3
"""Resolve Obsidian ![[file.png]] wikilinks: find the real asset in the vault,
copy it into <module>/images/, rewrite the link as ![](images/...).

Usage: resolve_wikilinks.py <module>
Operates in-place on <module>/md/*.md.
"""
import re
import shutil
import sys
import unicodedata
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LATEX = SCRIPTS.parent

# Obsidian vault root — search globally for assets
VAULT_ROOT = Path(
    "/Users/fabiopsh/Library/Mobile Documents/com~apple~CloudDocs/UNIPI - Magistrale Pisa/Unipi - Obsidian"
)

WIKILINK_RE = re.compile(r"!\[\[([^\]]+?)\]\]")
ASSET_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf")


def slugify_filename(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    stem = Path(s).stem
    ext = Path(s).suffix
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
    return f"{stem}{ext}"


def build_index():
    print("Indexing vault assets...")
    index = {}
    for p in VAULT_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if ".trash" in p.parts:
            continue
        if p.suffix.lower() not in ASSET_EXTS:
            continue
        index.setdefault(p.name, p)
    print(f"  indexed {len(index)} asset files")
    return index


def main(module: str):
    mod = LATEX / module
    src = mod / "md"
    img = mod / "images"
    img.mkdir(parents=True, exist_ok=True)

    index = build_index()
    total_resolved = 0
    total_miss = 0

    for md_file in sorted(src.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if "![[" not in text:
            continue

        def repl(m):
            nonlocal total_resolved, total_miss
            target = m.group(1).strip().split("|", 1)[0].strip().split("#", 1)[0].strip()
            if target not in index:
                print(f"  ! MISS in {md_file.name}: {target}")
                total_miss += 1
                return ""
            src_path = index[target]
            dest_name = slugify_filename(target)
            dest_path = img / dest_name
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

    print(f"[{module}] Resolved: {total_resolved}, missed: {total_miss}")


if __name__ == "__main__":
    main(sys.argv[1])
