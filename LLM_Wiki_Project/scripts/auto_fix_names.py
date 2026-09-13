import os
import glob
import re

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
FORBIDDEN_CHARS = set('()[]{}#%&*|\\/:"<>?—.')

def main():
    renamed = 0
    for root, _, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith('.md'): continue
            if file == '_moc.md': continue
            
            # Remove forbidden chars (except we keep . for .md)
            base, ext = os.path.splitext(file)
            new_base = "".join([c for c in base if c not in FORBIDDEN_CHARS])
            # Replace spaces with underscores
            new_base = new_base.replace(' ', '_')
            # Collapse consecutive underscores
            new_base = re.sub(r'_+', '_', new_base)
            
            new_name = new_base + ext
            
            if new_name != file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                
                # If target already exists, merge or skip (we'll just append a number for safety)
                if os.path.exists(new_path) and old_path.lower() != new_path.lower():
                    counter = 1
                    while os.path.exists(f"{new_path[:-3]}_{counter}.md"):
                        counter += 1
                    new_path = f"{new_path[:-3]}_{counter}.md"
                
                os.rename(old_path, new_path)
                renamed += 1
                
    print(f"Renamed {renamed} files to fix naming conventions.")

if __name__ == '__main__':
    main()
