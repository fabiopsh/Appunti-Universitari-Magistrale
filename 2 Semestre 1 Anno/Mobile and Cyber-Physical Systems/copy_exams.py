import re
from pathlib import Path

def process_exam(src_file, dst_file, new_title):
    text = Path(src_file).read_text(encoding='utf-8')
    
    # Strip YAML frontmatter
    text = re.sub(r'\A---\n.*?\n---\n', '', text, flags=re.DOTALL).lstrip()
    
    # Replace top level heading
    text = re.sub(r'^#\s+.*$', f'# {new_title}', text, count=1, flags=re.MULTILINE)
    
    Path(dst_file).write_text(text, encoding='utf-8')
    print(f"Written {dst_file}")

process_exam(
    "Esame Chessa.md", 
    "latex/chessa/riassunto_md/05 - Preparazione Esame Orale.md", 
    "05 - Preparazione Esame Orale"
)

process_exam(
    "Esame Paganelli.md", 
    "latex/paganelli/riassunto_md/05 - Preparazione Esame Orale.md", 
    "05 - Preparazione Esame Orale"
)
