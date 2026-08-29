import os
import re

target_dirs = [".agents", "LLM_Wiki_Project/scripts", "LLM_Wiki_Project/templates"]
prefix_url_1 = r"file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/"
prefix_url_2 = r"file:///G:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/"
prefix_url_3 = r"file:///G:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/02_AI_Lab_Obsidian_Templates/Personalized%20LLM%20Knowledge%20Graph%20Template/"
prefix_url_4 = r"file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/02_AI_Lab_Obsidian_Templates/Personalized%20LLM%20Knowledge%20Graph%20Template/"

prefix_win_1 = r"g:\\My Drive\\Kyubin_Yun_Workspace\\06_Obsidian_System\\01_Obsidian_Vault\\03_General\\"
prefix_win_2 = r"G:\\My Drive\\Kyubin_Yun_Workspace\\06_Obsidian_System\\01_Obsidian_Vault\\03_General\\"
prefix_win_3 = r"G:\\My Drive\\Kyubin_Yun_Workspace\\06_Obsidian_System\\02_AI_Lab_Obsidian_Templates\\Personalized LLM Knowledge Graph Template\\"
prefix_win_4 = r"g:\\My Drive\\Kyubin_Yun_Workspace\\06_Obsidian_System\\02_AI_Lab_Obsidian_Templates\\Personalized LLM Knowledge Graph Template\\"

prefix_unix_1 = r"g:/My Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/"
prefix_unix_2 = r"G:/My Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/"
prefix_unix_3 = r"G:/My Drive/Kyubin_Yun_Workspace/06_Obsidian_System/02_AI_Lab_Obsidian_Templates/Personalized LLM Knowledge Graph Template/"
prefix_unix_4 = r"g:/My Drive/Kyubin_Yun_Workspace/06_Obsidian_System/02_AI_Lab_Obsidian_Templates/Personalized LLM Knowledge Graph Template/"

urls = [prefix_url_1, prefix_url_2, prefix_url_3, prefix_url_4]
wins = [prefix_win_1, prefix_win_2, prefix_win_3, prefix_win_4]
unixs = [prefix_unix_1, prefix_unix_2, prefix_unix_3, prefix_unix_4]

def get_relative_path(file_path, target_path_from_root):
    file_dir = os.path.dirname(file_path)
    if not file_dir:
        return target_path_from_root
    rel_path = os.path.relpath(target_path_from_root, file_dir)
    return rel_path.replace(r"\\", "/")

for d in target_dirs:
    for root, _, files in os.walk(d):
        for file in files:
            if not file.endswith(".md") and not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            def replace_url(match):
                target = match.group(1)
                rel = get_relative_path(file_path.replace(r"\\", "/"), target)
                return rel
            
            for url in urls:
                content = re.sub(url + r"([^)\s]+)", replace_url, content, flags=re.IGNORECASE)
            
            for win in wins:
                content = re.sub(re.escape(win), "./", content, flags=re.IGNORECASE)
                
            for unix in unixs:
                content = re.sub(re.escape(unix), "./", content, flags=re.IGNORECASE)
            
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated {file_path}")

