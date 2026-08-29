import os
import yaml
import re

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")

def normalize_tags_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        return False

    try:
        fm = yaml.safe_load(parts[1])
    except Exception as e:
        print(f"Error parsing YAML in {filepath}: {e}")
        return False

    if not isinstance(fm, dict):
        return False

    tags = fm.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',')]
    if not isinstance(tags, list):
        return False

    new_tags = set()
    changed = False

    for tag in tags:
        orig_tag = tag
        # 1. Lowercase
        tag = tag.lower()
        
        # 2. Remove prefixes (e.g., type/concept -> concept, academic/statistics -> statistics)
        if '/' in tag:
            tag = tag.split('/')[-1]
            
        # 3. Handle plurals/specific mappings
        if tag == 'concepts':
            tag = 'concept'
        if tag == 'papers':
            tag = 'reading-notes' # Map academic/papers to reading-notes, though they should be classified by type.
            
        # 4. Remove meaningless migration tags
        if tag in ['consolidated', 'reading_note', 'entity']:
            tag = None # Drop 'consolidated', or type-based tags that shouldn't be in the tags array
            
        if tag and orig_tag != tag:
            changed = True
            
        if tag:
            new_tags.add(tag)

    if len(new_tags) != len(tags) or changed:
        # Sort for deterministic output
        fm['tags'] = sorted(list(new_tags))
        
        # Format YAML properly without changing other fields unexpectedly
        # We'll just dump the whole frontmatter. We need to preserve the order if possible, but PyYAML doesn't preserve order by default.
        # Let's use a simple regex replacement to only replace the tags line to preserve file structure.
        
        # Actually, using yaml.dump with sort_keys=False is available in PyYAML 5.1+
        new_yaml = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{new_yaml}---{parts[2]}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    modified_count = 0
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                if normalize_tags_in_file(filepath):
                    modified_count += 1
                    safe_name = file.encode('ascii', 'ignore').decode('ascii')
                    print(f"Updated tags in {safe_name}")

    print(f"Total files updated: {modified_count}")

if __name__ == '__main__':
    main()
