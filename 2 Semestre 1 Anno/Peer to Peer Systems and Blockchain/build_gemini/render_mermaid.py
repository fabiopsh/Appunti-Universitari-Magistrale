#!/usr/bin/env python3
"""Find mermaid code blocks in build/md/*.md, render to PNG, replace block with image link."""
import re
import subprocess
import tempfile
from pathlib import Path

BUILD = Path(__file__).resolve().parent
SRC = BUILD / "md"
IMG = BUILD / "images"
IMG.mkdir(exist_ok=True)

MERMAID_RE = re.compile(r"^```mermaid\n(.*?)\n```\s*$", re.DOTALL | re.MULTILINE)

total = 0
fail = 0

for md_file in sorted(SRC.glob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    if "```mermaid" not in text:
        continue

    slug = re.sub(r"[^a-z0-9]+", "-", md_file.stem.lower()).strip("-")
    counter = {"n": 0}

    def repl(m):
        counter["n"] += 1
        code = m.group(1)
        fname = f"mermaid-{slug}-{counter['n']:02d}.png"
        out_path = IMG / fname
        with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as tf:
            tf.write(code)
            tf_path = tf.name
        try:
            r = subprocess.run(
                ["mmdc", "-i", tf_path, "-o", str(out_path),
                 "-w", "1600", "-H", "1000", "-b", "white",
                 "--puppeteerConfigFile", "/dev/null"],
                capture_output=True, text=True, timeout=60,
            )
            if r.returncode != 0 or not out_path.exists():
                # Try without puppeteer config
                r = subprocess.run(
                    ["mmdc", "-i", tf_path, "-o", str(out_path),
                     "-w", "1600", "-H", "1000", "-b", "white"],
                    capture_output=True, text=True, timeout=60,
                )
            if r.returncode != 0 or not out_path.exists():
                print(f"  ! mmdc fail {md_file.name}#{counter['n']}: {r.stderr[:200]}")
                nonlocal_fail()
                return m.group(0)
            print(f"  ✓ {fname}")
            return f"![Diagramma Mermaid]({IMG.name}/{fname})"
        finally:
            Path(tf_path).unlink(missing_ok=True)

    fail_list = []
    def nonlocal_fail():
        fail_list.append(1)

    new_text = MERMAID_RE.sub(repl, text)
    if new_text != text:
        md_file.write_text(new_text, encoding="utf-8")
    total += counter["n"] - len(fail_list)
    fail += len(fail_list)

print(f"\nDone. Rendered: {total}, failed: {fail}")
