import os
import yaml
import re
from collections import defaultdict
import shutil

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
TAXONOMY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "taxonomy.md")
SKIP_FILES = {'_moc.md', 'log.md', 'index.md', 'overview.md'}

def extract_tag_folder_mapping():
    mapping = {} 
    if not os.path.exists(TAXONOMY_FILE):
        return mapping

    with open(TAXONOMY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    table_match = re.search(r'## Tag→Folder Mapping Reference.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)*)', content, re.DOTALL)
    if not table_match: return mapping

    for line in table_match.group(1).strip().split('\n'):
        if not line.startswith('|'): continue
        parts = line.split('|')
        if len(parts) < 3: continue

        tags_cell = parts[1].strip()
        folder_cell = parts[2].strip()

        folder_match = re.search(r'`(academic/\w+)/`', folder_cell)
        if not folder_match:
            if 'type=' in tags_cell:
                type_match = re.search(r'type=`(\w+)`', tags_cell)
                folder_match2 = re.search(r'`(academic/\w+)/`', folder_cell)
                if type_match and folder_match2:
                    mapping.setdefault(folder_match2.group(1), {'types': set(), 'tags': set()})
                    mapping[folder_match2.group(1)]['types'].add(type_match.group(1))
            continue

        folder = folder_match.group(1)
        if folder not in mapping:
            mapping[folder] = {'types': set(), 'tags': set()}

        tags_found = re.findall(r'`([^`]+)`', tags_cell)
        for tag in tags_found:
            mapping[folder]['tags'].add(tag.lower())

    return mapping

def generate_moc(folder_path, files):
    files.sort()
    moc_content = "---\ntype: moc\ndomain: academic\ntitle: Map of Content\n---\n\n# Map of Content\n\n"
    for file in files:
        basename = file.replace('.md', '')
        moc_content += f"- [[{basename}]]\n"
        
    with open(os.path.join(folder_path, '_moc.md'), 'w', encoding='utf-8') as f:
        f.write(moc_content)

def update_domain_moc(domain_dir, subfolders_dict):
    moc_path = os.path.join(domain_dir, '_moc.md')
    if not os.path.exists(moc_path):
        content = "---\ntype: moc\ndomain: academic\ntitle: Domain Map of Content\n---\n\n# Domain Map of Content\n\n"
    else:
        with open(moc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
    # Rebuild domain MOC with clustered headings
    # First, let's just parse existing frontmatter and rebuild the body
    parts = content.split('---', 2)
    fm_str = parts[1] if len(parts) >= 3 else "type: moc\n"
    
    body = "# Domain Map of Content\n\n"
    for subfolder, files in sorted(subfolders_dict.items()):
        # Title case the subfolder name
        heading = subfolder.replace('_', ' ').title()
        body += f"## {heading}\n"
        for file in sorted(files):
            basename = file.replace('.md', '')
            body += f"- [[{basename}]]\n"
        body += "\n"
        
    with open(moc_path, 'w', encoding='utf-8') as f:
        f.write(f"---\n{fm_str.strip()}\n---\n\n{body}")

def migrate_files():
    tag_folder_mapping = extract_tag_folder_mapping()
    
    moved_count = 0
    subfolders_files = defaultdict(list)
    
    # 1. Determine destination for each file
    to_move = []
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith('.md') or file in SKIP_FILES:
                continue
                
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, WIKI_DIR).replace('\\', '/')
            current_folder = os.path.dirname(relpath)
            
            if not current_folder.startswith('academic'):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                continue
                
            fm = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1])
                    except: pass
                    
            if not isinstance(fm, dict): fm = {}
            
            ftype = fm.get('type')
            tags = fm.get('tags', [])
            if isinstance(tags, str): tags = [t.strip() for t in tags.split(',')]
            if not isinstance(tags, list): tags = []
            
            expected_folder = 'academic/_uncategorized' # Default fallback
            
            if ftype == 'reading_note':
                expected_folder = 'academic/reading_notes'
            elif ftype == 'collection':
                expected_folder = 'academic/collections'
            elif file.startswith('Lecture_'):
                expected_folder = 'academic/lecture_notes'
            else:
                found = False
                for subfolder, rule in tag_folder_mapping.items():
                    if 'tags' in rule:
                        for tag in tags:
                            if tag.lower() in rule['tags']:
                                expected_folder = subfolder
                                found = True
                                break
                    if found: break
                    
            to_move.append((filepath, file, current_folder, expected_folder))

    for filepath, file, current_folder, expected_folder in to_move:
        if current_folder != expected_folder:
            dest_dir = os.path.join(WIKI_DIR, expected_folder)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, file)
            
            # Move file
            shutil.move(filepath, dest_path)
            moved_count += 1
            
            # Extract just the subfolder name
            subfolder_name = expected_folder.split('/')[-1]
            subfolders_files[subfolder_name].append(file)
        else:
            subfolder_name = current_folder.split('/')[-1]
            subfolders_files[subfolder_name].append(file)
                
    print(f"Moved {moved_count} files to correct subfolders.")
    
    # 2. Generate MOCs
    academic_dir = os.path.join(WIKI_DIR, 'academic')
    for subfolder_name, files in subfolders_files.items():
        if subfolder_name:
            folder_path = os.path.join(academic_dir, subfolder_name)
            os.makedirs(folder_path, exist_ok=True)
            generate_moc(folder_path, files)
            
    # Update Domain MOC
    update_domain_moc(academic_dir, subfolders_files)
    print("MOCs updated successfully.")

if __name__ == '__main__':
    migrate_files()
