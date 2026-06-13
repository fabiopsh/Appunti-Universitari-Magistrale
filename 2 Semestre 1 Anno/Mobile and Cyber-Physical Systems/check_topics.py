import re
from pathlib import Path

def check(exam_file, appunti_file):
    exam = Path(exam_file).read_text()
    appunti = Path(appunti_file).read_text()
    
    topics = re.findall(r'^##\s+(.*)', exam, re.MULTILINE)
    missing = []
    found = []
    
    for t in topics:
        # Simplify the topic to a few keywords to search in appunti
        # E.g. "ZigBee - I (Join through Association)" -> "Join through Association"
        kw = re.sub(r'^.*?\-\s*[IV]+\s*\((.*?)\).*', r'\1', t)
        if kw == t: 
            kw = t.split('(')[0].strip()
        
        # Check if the keyword exists
        if kw.lower() in appunti.lower():
            found.append(t)
        else:
            missing.append(t)
            
    print(f"=== {exam_file} ===")
    print(f"Found {len(found)}/{len(topics)}")
    print(f"Missing: {missing}")

check("Esame Chessa.md", "latex/chessa/appunti_riassunti.tex")
check("Esame Paganelli.md", "latex/paganelli/appunti_riassunti.tex")
