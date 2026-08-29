import os
import re

wiki_dir = "LLM_Wiki_Project/wiki"
for root, _, files in os.walk(wiki_dir):
    for file in files:
        if file.endswith("_moc.md"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            new_lines = []
            for line in lines:
                if not re.match(r"^\s*-\s*\[\[.*?\]\]\s*$", line):
                    new_lines.append(line)
                    
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

