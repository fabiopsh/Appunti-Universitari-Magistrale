import sys, re
from pathlib import Path

def fix(p):
    text = p.read_text(encoding='utf-8')
    text = re.sub(r'\)\s*!\[', ')\n\n![', text)
    text = re.sub(r'```\s*!\[', '```\n\n![', text)
    p.write_text(text, encoding='utf-8')

if len(sys.argv) > 1:
    src_dir = Path(sys.argv[1]) / "md"
    for md in src_dir.glob("*.md"):
        fix(md)
