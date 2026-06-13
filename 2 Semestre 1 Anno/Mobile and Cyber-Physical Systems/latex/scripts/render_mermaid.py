#!/usr/bin/env python3
"""Render mermaid code blocks in <module>/md/*.md to PNG, replace block with image link.

Usage: render_mermaid.py <module>
Requires the `mmdc` CLI (mermaid-cli). Failures are non-fatal.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LATEX = SCRIPTS.parent

MERMAID_RE = re.compile(r"^```mermaid\n(.*?)\n```\s*$", re.DOTALL | re.MULTILINE)


def main(module: str):
    mod = LATEX / module
    src = mod / "md"
    img = mod / "images"
    img.mkdir(parents=True, exist_ok=True)

    total = 0
    fail = 0

    for md_file in sorted(src.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if "```mermaid" not in text:
            continue

        slug = re.sub(r"[^a-z0-9]+", "-", md_file.stem.lower()).strip("-")
        counter = {"n": 0}
        fail_list = []

        def repl(m):
            counter["n"] += 1
            code = m.group(1)
            fname = f"mermaid-{slug}-{counter['n']:02d}.png"
            out_path = img / fname
            caption_match = re.search(r"^\s*%%\s*CAPTION:\s*(.*?)$", code, re.MULTILINE)
            caption = caption_match.group(1).strip() if caption_match else "Diagramma Mermaid"
            
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
                    r = subprocess.run(
                        ["mmdc", "-i", tf_path, "-o", str(out_path),
                         "-w", "1600", "-H", "1000", "-b", "white"],
                        capture_output=True, text=True, timeout=60,
                    )
                if r.returncode != 0 or not out_path.exists():
                    print(f"  ! mmdc fail {md_file.name}#{counter['n']}: {r.stderr[:200]}")
                    fail_list.append(1)
                    return m.group(0)
                print(f"  ✓ {fname}")
                return f"![{caption}](images/{fname})\n\n"
            finally:
                Path(tf_path).unlink(missing_ok=True)

        new_text = MERMAID_RE.sub(repl, text)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
        total += counter["n"] - len(fail_list)
        fail += len(fail_list)

    print(f"[{module}] Mermaid renderizzati: {total}, falliti: {fail}")


if __name__ == "__main__":
    main(sys.argv[1])
