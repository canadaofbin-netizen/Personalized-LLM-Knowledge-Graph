import json
path = ".obsidian/workspace.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# we can just ignore workspace.json, it will be overwritten. But we can just replace Kyubin with Template_User
with open(path, "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace("Kyubin_Yun", "Template_User").replace("Kyubin_I", "Template_User")
with open(path, "w", encoding="utf-8") as f:
    f.write(text)

moc_path = "LLM_Wiki_Project/wiki/people/_moc.md"
with open(moc_path, "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace("- [[Kyubin_Yun]]", "")
with open(moc_path, "w", encoding="utf-8") as f:
    f.write(text)

