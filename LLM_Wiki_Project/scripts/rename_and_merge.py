import os
import re
import yaml
from collections import defaultdict

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
SKIP_FILES = {'_moc.md', 'log.md', 'index.md', 'overview.md'}

def normalize_filename(filename):
    if filename in SKIP_FILES:
        return filename
    
    # E.g., "Between-Subjects Design.md" -> "Between-Subjects_Design.md"
    # Or "Brain-Computer Interface (BCI).md" -> "Brain-Computer_Interface.md"
    name = filename.replace('.md', '')
    
    # Remove parentheticals
    name = re.sub(r'\s*\(.*?\)', '', name)
    
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Remove forbidden characters except hyphens and underscores
    forbidden = set('()[]{}#%&*|\\/:"<>?—')
    name = ''.join(c for c in name if c not in forbidden)
    
    # Capitalize first letter of words? We'll just leave case as is for now, but spaces to underscores is key
    return name + '.md'

def parse_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                return fm if fm else {}, parts[2]
            except:
                pass
    return {}, content

def format_md(fm, body):
    fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{fm_str}---{body}"

def process_renames_and_merges():
    # 1. Map normalized name to existing files
    norm_map = defaultdict(list)
    norm_case_map = {} # Maps lower_norm_name -> proper_norm_name
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith('.md'): continue
            if file in SKIP_FILES: continue
            
            relpath = os.path.relpath(os.path.join(root, file), WIKI_DIR)
            norm_name = normalize_filename(file)
            # For grouping, also normalize hyphens and periods to underscores to catch duplicates like
            # Brain-Computer_Interface vs Brain_Computer_Interface and Young_D._Kwon vs Young_D_Kwon
            lower_name = norm_name.lower().replace('-', '_').replace('.', '_')
            # Remove consecutive underscores that might have been created by replacing punctuation
            lower_name = re.sub(r'_+', '_', lower_name)
            
            # Prefer the TitleCase version as the canonical one
            if lower_name not in norm_case_map or norm_name.isupper() or any(c.isupper() for c in norm_name):
                norm_case_map[lower_name] = norm_name
                
            norm_map[lower_name].append(os.path.join(WIKI_DIR, relpath))

    link_updates = {} # old_name (no ext) -> new_name (no ext)

    # 2. Rename and Merge
    for lower_name, paths in norm_map.items():
        norm_name = norm_case_map[lower_name]
        if len(paths) == 1:
            # Just rename if needed
            old_path = paths[0]
            new_path = os.path.join(os.path.dirname(old_path), norm_name)
            
            old_base = os.path.basename(old_path)
            if old_base != norm_name:
                # Windows case-only rename safe approach
                if old_path.lower() == new_path.lower():
                    temp_path = old_path + ".tmp"
                    os.rename(old_path, temp_path)
                    os.rename(temp_path, new_path)
                else:
                    os.rename(old_path, new_path)
                safe_old = old_base.encode('ascii', 'ignore').decode('ascii')
                safe_new = norm_name.encode('ascii', 'ignore').decode('ascii')
                print(f"Renamed: {safe_old} -> {safe_new}")
                link_updates[old_base.replace('.md', '')] = norm_name.replace('.md', '')
        else:
            # Merge
            print(f"Merging {len(paths)} files into {norm_name}")
            base_path = paths[0]
            base_dir = os.path.dirname(base_path)
            new_path = os.path.join(base_dir, norm_name)
            
            merged_fm = {}
            merged_body = ""
            
            for p in paths:
                fm, body = parse_md(p)
                
                # Merge tags
                tags1 = merged_fm.get('tags', [])
                if isinstance(tags1, str): tags1 = [tags1]
                tags2 = fm.get('tags', [])
                if isinstance(tags2, str): tags2 = [tags2]
                merged_fm['tags'] = sorted(list(set(tags1 + tags2)))
                
                # Take other fields from first non-empty
                for k, v in fm.items():
                    if k != 'tags' and k not in merged_fm:
                        merged_fm[k] = v
                
                if merged_body:
                    merged_body += "\n\n---\n\n"
                merged_body += body.strip()
                
                old_base = os.path.basename(p)
                if old_base != norm_name:
                    link_updates[old_base.replace('.md', '')] = norm_name.replace('.md', '')
                    
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(format_md(merged_fm, merged_body))
                
            # Delete old files if they have different names
            for p in paths:
                if p != new_path and os.path.exists(p):
                    os.remove(p)
                    
    # 3. Update all wikilinks
    print(f"Updating links for {len(link_updates)} renamed files...")
    # Also we want to update links that used spaces to use underscores.
    
    updated_files = 0
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith('.md'): continue
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            new_content = content
            for old_link, new_link in link_updates.items():
                escaped_old = re.escape(old_link)
                # Replace [[old_link|alias]] -> [[new_link|alias]]
                new_content = re.sub(rf'\[\[{escaped_old}\|(.*?)\]\]', rf'[[{new_link}|\1]]', new_content)
                # Replace [[old_link]] -> [[new_link]]
                new_content = re.sub(rf'\[\[{escaped_old}\]\]', f'[[{new_link}]]', new_content)
                
            if content != new_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_files += 1

    print(f"Link updates applied to {updated_files} files.")

if __name__ == '__main__':
    process_renames_and_merges()
