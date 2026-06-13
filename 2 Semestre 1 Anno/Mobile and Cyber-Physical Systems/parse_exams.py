import re
from collections import defaultdict
from pathlib import Path

def parse_exam(filepath):
    text = Path(filepath).read_text(encoding='utf-8')
    # Split by ## 
    sections = re.split(r'^##\s+', text, flags=re.MULTILINE)[1:] # skip frontmatter
    
    mapping = defaultdict(list)
    images = []
    
    for sec in sections:
        lines = sec.strip().split('\n')
        title = lines[0].strip()
        
        # Find images
        imgs = re.findall(r'!\[\[(.*?)\]\]', sec)
        images.extend(imgs)
        
        # Find references
        refs = re.findall(r'\[\[(.*?)\]\]', sec)
        if not refs:
            # Maybe there are no explicit [[Lezione ...]] links?
            # Assign to "Unknown"
            mapping["Unknown"].append(title)
        else:
            for r in refs:
                mapping[r].append(title)
                
    print(f"--- {filepath} ---")
    for lesson, tops in mapping.items():
        print(f"{lesson}:")
        for t in tops:
            print(f"  - {t}")
            
parse_exam("Esame Chessa.md")
parse_exam("Esame Paganelli.md")
