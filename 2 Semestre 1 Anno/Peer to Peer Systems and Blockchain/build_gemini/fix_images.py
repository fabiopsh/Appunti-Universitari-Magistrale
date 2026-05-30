import re
from pathlib import Path

md_dir = Path("md")

# Regex to match:
# Optional blank line
# ![alt text](image path)
# *caption prefix: caption text*
# We use re.MULTILINE and capture groups.

pattern = re.compile(
    r"(!\[.*?\]\((images/[^)]+)\))\n\*+(?:Figura\s*\d*:|Fig\.\s*[—\-:]+|Figura:)\s*(.*?)\*+",
    re.MULTILINE
)

for md_file in md_dir.glob("Capitolo*.md"):
    text = md_file.read_text(encoding="utf-8")
    
    def repl(m):
        # m.group(1) is the original image tag (e.g. ![alt](path))
        # m.group(2) is the image path
        # m.group(3) is the caption text
        caption = m.group(3).strip()
        path = m.group(2).strip()
        # Ensure there are blank lines around it for Pandoc to treat it as a Figure block
        return f"\n\n![{caption}]({path})\n\n"
        
    new_text = pattern.sub(repl, text)
    
    if new_text != text:
        # Also clean up multiple blank lines just in case
        new_text = re.sub(r"\n{3,}", "\n\n", new_text)
        md_file.write_text(new_text, encoding="utf-8")
        print(f"Fixed images in {md_file.name}")

