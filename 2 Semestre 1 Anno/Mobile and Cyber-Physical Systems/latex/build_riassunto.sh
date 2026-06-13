#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
LATEX="$(pwd)"

title_for() {
  case "$1" in
    chessa)    echo "Mobile & CPS — Modulo Chessa (Riassunto)" ;;
    paganelli) echo "Mobile & CPS — Modulo Paganelli (Riassunto)" ;;
    *)         echo "Mobile & CPS — $1 (Riassunto)" ;;
  esac
}

for mod in chessa paganelli; do
  echo
  echo "########## MODULO: $mod (RIASSUNTO) ##########"

  if [ -d "$mod/md_original_backup" ]; then
      rm -rf "$mod/md"
  elif [ -d "$mod/md" ]; then
      mv "$mod/md" "$mod/md_original_backup"
  fi
  
  cp -r "$mod/riassunto_md" "$mod/md"

  echo "==> 3. [$mod] Risoluzione wikilink immagini dal vault"
  python3 scripts/resolve_wikilinks.py "$mod"

  echo "==> 4. [$mod] Rendering blocchi mermaid -> PNG"
  python3 scripts/render_mermaid.py "$mod"

  echo "==> 5. [$mod] Fixing consecutive images"
  python3 scripts/fix_images.py "$mod"

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
      -o appunti_riassunti.tex )

  echo "==> 8. [$mod] Compilazione PDF (due pass per il TOC)"
  ( cd "$mod" && tectonic -X compile appunti_riassunti.tex && tectonic -X compile appunti_riassunti.tex )

  echo "==> [$mod] Done: $mod/appunti_riassunti.pdf"

  rm -rf "$mod/md"
  if [ -d "$mod/md_original_backup" ]; then
      mv "$mod/md_original_backup" "$mod/md"
  fi

done

echo
echo "==> Tutti i moduli riassunti compilati."
ls -lh chessa/appunti_riassunti.pdf paganelli/appunti_riassunti.pdf
