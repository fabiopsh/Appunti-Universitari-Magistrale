#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1. Estrazione immagini base64"
python3 extract_images.py

echo "==> 2. Rimozione duplicati iCloud in build/md/"
find md -maxdepth 1 -name "* 2.md" ! -name "*Part 2.md" -print -delete

echo "==> 3. Risoluzione wikilink Obsidian -> images/"
python3 resolve_wikilinks.py

echo "==> 3b. Download immagini remote -> images/"
python3 fetch_remote_images.py

echo "==> 4. Rendering blocchi mermaid -> PNG"
python3 render_mermaid.py

echo "==> 4b. Rimozione blocchi 'Possibili domande d'esame'"
python3 strip_exam_questions.py

echo "==> 5. Concatenazione ordinata"
python3 concat.py

echo "==> 6. Conversione Markdown -> LaTeX"
pandoc appunti.md \
  -f markdown+raw_tex+tex_math_dollars+pipe_tables+backtick_code_blocks \
  -t latex \
  --top-level-division=chapter \
  --toc --toc-depth=2 \
  --number-sections \
  --highlight-style=tango \
  --lua-filter=callouts.lua \
  -V documentclass=book \
  -V classoption=openany \
  -V geometry:margin=2.5cm \
  -V lang=it \
  --metadata title="Datacenter Design and Operation — Appunti" \
  --metadata author="Fabio Piscitelli" \
  --metadata date="2026" \
  --include-in-header preamble.tex \
  --standalone \
  -o appunti.tex

echo "==> 7. Compilazione PDF (due pass per il TOC)"
tectonic -X compile appunti.tex
tectonic -X compile appunti.tex

echo "==> Done. Output: build/appunti.pdf"
ls -lh appunti.pdf
