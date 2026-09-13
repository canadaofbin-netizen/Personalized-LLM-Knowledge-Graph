import os, glob, yaml, shutil, re
from collections import defaultdict
from pathlib import Path

wiki_dir = Path('LLM_Wiki_Project/wiki')
tax_file = Path('LLM_Wiki_Project/taxonomy.md')

def main():
    # 1. Collect tags in _uncategorized folders
    tag_files = defaultdict(list)
    for md_file in wiki_dir.rglob('*.md'):
        if '_uncategorized' not in md_file.parts or md_file.name == '_moc.md': 
            continue
        
        domain = md_file.parent.parent.name
        if domain == 'wiki': 
            domain = md_file.parent.name # fallback if it was directly in wiki/_uncategorized
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    tags = fm.get('tags', [])
                    if isinstance(tags, str): tags = [tags]
                    if isinstance(tags, list):
                        for t in tags:
                            if t.lower() != 'uncategorized':
                                tag_files[(domain, t.lower())].append(md_file)
                except: 
                    pass

    # 2. Process groups with 3+ files
    created_folders = 0
    new_mappings = []

    for (domain, tag), files in tag_files.items():
        if len(files) >= 3:
            safe_tag = tag.replace(' ', '-').replace('/', '-')
            new_folder_rel = f'{domain}/{safe_tag}'
            new_folder_abs = wiki_dir / domain / safe_tag
            
            new_folder_abs.mkdir(parents=True, exist_ok=True)
            created_folders += 1
            
            # Move files
            for f in files:
                if f.exists():
                    shutil.move(str(f), str(new_folder_abs / f.name))
                    
            # Prepare taxonomy update
            new_mappings.append(f"| `{tag}` | `{new_folder_rel}/` | Auto-created from _uncategorized overflow |")

    # 3. Update taxonomy.md if we created new folders
    if new_mappings:
        with open(tax_file, 'r', encoding='utf-8') as f:
            tax_content = f.read()
            
        if '## Tag→Folder Mapping Reference' not in tax_content:
            tax_content += '\n\n## Tag→Folder Mapping Reference\n| Type / Tags | Destination Path | Notes |\n| ----------- | ---------------- | ----- |\n'
        
        tax_content += '\n'.join(new_mappings) + '\n'
        
        with open(tax_file, 'w', encoding='utf-8') as f:
            f.write(tax_content)
            
    print(f'Created {created_folders} new folders from overflow.')

if __name__ == '__main__':
    main()
