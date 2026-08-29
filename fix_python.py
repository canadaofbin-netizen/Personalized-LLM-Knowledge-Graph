import os
import re

scripts_dir = "LLM_Wiki_Project/scripts"
for root, _, files in os.walk(scripts_dir):
    for file in files:
        if not file.endswith(".py"): continue
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        content = content.replace("os.path.expanduser(\\"~/.gemini/antigravity/brain\\")", "os.path.expanduser(\"~/.gemini/antigravity/brain\")")
        content = content.replace("r\\"./LLM_Wiki_Project/raw\\assets\\"", "r\"./LLM_Wiki_Project/raw/assets\"")
        content = content.replace("r\\"./LLM_Wiki_Project/raw\\imports\\.extract_all_log.json\\"", "r\"./LLM_Wiki_Project/raw/imports/.extract_all_log.json\"")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

