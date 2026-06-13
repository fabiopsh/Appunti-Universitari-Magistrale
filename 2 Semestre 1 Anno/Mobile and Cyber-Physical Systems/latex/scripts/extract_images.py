#!/usr/bin/env python3
"""Extract base64-embedded images from <module>/src/*.md, rewrite links to file paths.

Usage: extract_images.py <module>
Reads  <module>/src/*.md, writes images to <module>/images/, processed md to <module>/md/.
"""
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
    out_img = mod / "images"
    out_md = mod / "md"
    out_img.mkdir(parents=True, exist_ok=True)
    out_md.mkdir(parents=True, exist_ok=True)

    total_imgs = 0
    per_file_counts = {}

    for md_file in sorted(src.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        slug = slugify(md_file.stem)
        counter = {"n": 0}

        def repl(m):
            alt = m.group(1)
            ext = m.group(2)
            if ext == "jpg":
                ext = "jpeg"
            b64 = m.group(3)
            counter["n"] += 1
            file_ext = "jpg" if ext == "jpeg" else ext
            fname = f"{slug}-img-{counter['n']:02d}.{file_ext}"
            out_path = out_img / fname
            try:
                data = base64.b64decode(b64, validate=False)
                out_path.write_bytes(data)
            except Exception as e:
                print(f"  ! decode error in {md_file.name} img {counter['n']}: {e}")
                return m.group(0)
            return f"![{alt}](images/{fname})"

        new_text = DATA_URI_RE.sub(repl, text)
        (out_md / md_file.name).write_text(new_text, encoding="utf-8")
        if counter["n"] > 0:
            per_file_counts[md_file.name] = counter["n"]
            total_imgs += counter["n"]

    print(f"[{module}] Estratte {total_imgs} immagini base64 in {out_img}")
    for f, n in per_file_counts.items():
        print(f"  {n:3d}  {f}")


if __name__ == "__main__":
    main(sys.argv[1])
