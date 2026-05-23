import os
import re

md_dir = '.'
for filename in sorted(os.listdir(md_dir)):
    if not filename.endswith('.md'): continue
    with open(os.path.join(md_dir, filename), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if re.search(r'!\[.*?\]\(.*?\)', line):
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if not next_line.startswith('*Fig'):
                    print(f'{filename}:{i+1}: {line.strip()}')
                    print(f'Next line: {next_line}')
                    print('---')
            else:
                print(f'{filename}:{i+1}: {line.strip()}')
                print('Next line: EOF')
                print('---')
