#!/usr/bin/env python3
import base64
import re
import sys
import unicodedata
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LATEX = SCRIPTS.parent

DATA_URI_RE = re.compile(
    r"!\[((?:[^\]]|\](?!\(data:image))*)\]\(data:image/(jpeg|jpg|png|gif|webp);base64,([A-Za-z0-9+/=]+)\)"
)

def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def main(module: str):
    mod = LATEX / module
    src = mod / "src"
    out_md = mod / "md_clean"
    out_md.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(src.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        slug = slugify(md_file.stem)
        counter = {"n": 0}

        def repl(m):
            alt = m.group(1)
            ext = m.group(2)
            if ext == "jpg":
                ext = "jpeg"
            counter["n"] += 1
            file_ext = "jpg" if ext == "jpeg" else ext
            fname = f"{slug}-img-{counter['n']:02d}.{file_ext}"
            return f"![{alt}](images/{fname})"

        new_text = DATA_URI_RE.sub(repl, text)
        (out_md / md_file.name).write_text(new_text, encoding="utf-8")

if __name__ == "__main__":
    main(sys.argv[1])
