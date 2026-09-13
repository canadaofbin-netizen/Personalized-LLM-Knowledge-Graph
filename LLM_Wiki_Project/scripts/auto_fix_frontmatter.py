import os
import yaml
import re
from datetime import datetime

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
REQUIRED_FIELDS = ['type', 'title', 'description', 'tags', 'timestamp', 'sources']

def main():
    fixed = 0
    for root, _, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith('.md') or file == '_moc.md': continue
            
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            fm = {}
            body = content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                    except:
                        pass
                    body = parts[2]
            
            if not isinstance(fm, dict): fm = {}
            
            changed = False
            
            if 'type' not in fm: fm['type'] = 'concept'; changed = True
            if 'title' not in fm: fm['title'] = file.replace('.md', '').replace('_', ' ').title(); changed = True
            if 'description' not in fm: fm['description'] = ''; changed = True
            if 'tags' not in fm or not isinstance(fm['tags'], list): fm['tags'] = ['uncategorized']; changed = True
            if 'timestamp' not in fm: fm['timestamp'] = datetime.now().strftime("%Y-%m-%d"); changed = True
            if 'sources' not in fm: fm['sources'] = []; changed = True
            
            if changed:
                new_yaml = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
                new_content = f"---\n{new_yaml}---{body}"
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed += 1
                
    print(f"Injected missing frontmatter in {fixed} files.")

if __name__ == '__main__':
    main()
