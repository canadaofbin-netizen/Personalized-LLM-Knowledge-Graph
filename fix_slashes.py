import os
import re
target_dirs = [".agents"]
for root, _, files in os.walk(target_dirs[0]):
    for file in files:
        if not file.endswith(".md"): continue
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        def replace_slash(match):
            return match.group(0).replace(chr(92), "/")
        content = re.sub(r"\]\([^)]+\)", replace_slash, content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

