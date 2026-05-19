#!/usr/bin/env python3
"""Find remote image URLs in build/md/*.md, download to images/, rewrite links.
SVG files are converted to PNG via rsvg-convert."""
import hashlib
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

BUILD = Path(__file__).resolve().parent
SRC = BUILD / "md"
IMG = BUILD / "images"
IMG.mkdir(exist_ok=True)

REMOTE_RE = re.compile(
    r"(!\[[^\]]*\]\()(https?://[^)]+\.(?:svg|png|jpe?g|gif|webp))(\))",
    re.IGNORECASE,
)

USER_AGENT = "AppuntiUniBuildBot/1.0 (fabiopiscitelli01@gmail.com) python-urllib"
THROTTLE_HOSTS = ("wikimedia.org", "wikipedia.org")
THROTTLE_SECONDS = 2.5


def slug_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parsed.path)).name
    stem = Path(name).stem
    ext = Path(name).suffix.lower().lstrip(".")
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
    if not stem:
        stem = hashlib.md5(url.encode()).hexdigest()[:10]
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{stem}-{h}.{ext}"


def fetch(url: str, dest: Path) -> bool:
    if any(h in url for h in THROTTLE_HOSTS):
        time.sleep(THROTTLE_SECONDS)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
    }
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                dest.write_bytes(r.read())
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = 8 * (attempt + 1)
                print(f"  ... 429, retry in {wait}s")
                time.sleep(wait)
                continue
            print(f"  ! fetch fail {url}: HTTP {e.code}")
            return False
        except Exception as e:
            print(f"  ! fetch fail {url}: {e}")
            return False
    return False


def maybe_convert_svg(path: Path) -> Path:
    if path.suffix.lower() != ".svg":
        return path
    png_path = path.with_suffix(".png")
    if png_path.exists():
        return png_path
    try:
        r = subprocess.run(
            ["rsvg-convert", "-d", "200", "-p", "200", str(path), "-o", str(png_path)],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode == 0 and png_path.exists():
            return png_path
        print(f"  ! rsvg-convert fail {path.name}: {r.stderr[:200]}")
    except FileNotFoundError:
        print("  ! rsvg-convert not installed; SVG kept as-is (LaTeX may fail)")
    return path


seen = {}  # url -> local filename
total_dl = 0
total_skip = 0
fail = 0

for md_file in sorted(SRC.glob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    if not REMOTE_RE.search(text):
        continue

    def repl(m):
        global total_dl, total_skip, fail
        prefix, url, suffix = m.group(1), m.group(2), m.group(3)
        if url in seen:
            return f"{prefix}images/{seen[url]}{suffix}"
        fname = slug_from_url(url)
        dest = IMG / fname
        if not dest.exists():
            ok = fetch(url, dest)
            if not ok:
                fail += 1
                return m.group(0)
            total_dl += 1
            print(f"  ✓ {fname}")
        else:
            total_skip += 1
        final = maybe_convert_svg(dest)
        seen[url] = final.name
        return f"{prefix}images/{final.name}{suffix}"

    new_text = REMOTE_RE.sub(repl, text)
    if new_text != text:
        md_file.write_text(new_text, encoding="utf-8")

print(f"\nDownloaded: {total_dl}, cached: {total_skip}, failed: {fail}")
