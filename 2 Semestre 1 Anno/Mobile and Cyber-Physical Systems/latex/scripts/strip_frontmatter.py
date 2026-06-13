import sys, re
from pathlib import Path

def strip(p):
    text = p.read_text(encoding='utf-8')
    # If the file starts with *** or ---, find the next one and remove everything up to it
    if text.startswith('***\n') or text.startswith('---\n'):
        parts = re.split(r'^(?:\*\*\*|---)\n', text, maxsplit=2, flags=re.MULTILINE)
        if len(parts) >= 3:
            text = parts[2].lstrip()
    p.write_text(text, encoding='utf-8')

for md in Path('.').glob('*/riassunto_md/*.md'):
    strip(md)
