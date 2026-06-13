#!/usr/bin/env bash
# Pipeline completa multi-modulo:
#   split per (Lab) -> extract base64 -> resolve wikilink -> mermaid -> strip esame
#   -> concat -> pandoc -> tectonic, una volta per modulo (chessa, paganelli).
set -euo pipefail

cd "$(dirname "$0")"
LATEX="$(pwd)"

# Titolo PDF per modulo (bash 3.2 friendly: niente array associativi)
title_for() {
  case "$1" in
    chessa)    echo "Mobile & CPS — Modulo Chessa (CPS/IoT)" ;;
    paganelli) echo "Mobile & CPS — Modulo Paganelli (Reti Mobili)" ;;
    *)         echo "Mobile & CPS — $1" ;;
  esac
}

echo "==> 0. Split lezioni nei moduli (tag (Lab))"
python3 scripts/split_modules.py

for mod in chessa paganelli; do
  echo
  echo "########## MODULO: $mod ##########"

  echo "==> 1. [$mod] Estrazione immagini base64"
  python3 scripts/extract_images.py "$mod"

  echo "==> 1b. [$mod] Copia asset esterni condivisi (SVG Wikimedia -> PNG locali)"
  mkdir -p "$mod/images"
  cp -f common/assets/* "$mod/images/" 2>/dev/null || true

  echo "==> 2. [$mod] Rimozione duplicati iCloud in $mod/md/"
  find "$mod/md" -maxdepth 1 -name "* 2.md" ! -name "*Part 2.md" -print -delete || true

  echo "==> 3. [$mod] Risoluzione wikilink immagini dal vault"
  python3 scripts/resolve_wikilinks.py "$mod"

  echo "==> 4. [$mod] Rendering blocchi mermaid -> PNG"
  python3 scripts/render_mermaid.py "$mod"

  echo "==> 5. [$mod] Rimozione blocchi 'Possibili domande d'esame'"
  python3 scripts/strip_exam_questions.py "$mod"

  echo "==> 6. [$mod] Concatenazione ordinata"
  python3 scripts/concat.py "$mod"

  echo "==> 7. [$mod] Conversione Markdown -> LaTeX"
  ( cd "$mod" && pandoc appunti.md \
      -f markdown+raw_tex+tex_math_dollars+pipe_tables+backtick_code_blocks \
      -t latex \
      --top-level-division=chapter \
      --toc --toc-depth=2 \
      --number-sections \
      --highlight-style=tango \
      --lua-filter="$LATEX/common/callouts.lua" \
      --lua-filter="$LATEX/common/figures.lua" \
      -V documentclass=book \
      -V classoption=openany \
      -V geometry:margin=2.5cm \
      -V lang=it \
      --metadata title="$(title_for "$mod")" \
      --metadata author="Fabio Piscitelli" \
      --metadata date="2026" \
      --include-in-header "$LATEX/common/preamble.tex" \
      --standalone \
      -o appunti.tex )

  echo "==> 8. [$mod] Compilazione PDF (due pass per il TOC)"
  ( cd "$mod" && tectonic -X compile appunti.tex && tectonic -X compile appunti.tex )

  echo "==> [$mod] Done: $mod/appunti.pdf"
done

echo
echo "==> Tutti i moduli compilati."
ls -lh chessa/appunti.pdf paganelli/appunti.pdf
