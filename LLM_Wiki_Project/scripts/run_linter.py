import os
import sys
import yaml
import re
from collections import defaultdict, Counter
import math
from difflib import SequenceMatcher
from datetime import datetime, date

WIKI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
TAXONOMY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "taxonomy.md")
REPORT_FILE = os.path.join(os.path.dirname(WIKI_DIR), "reports", "lint_report.md")

SCHEMA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.yaml")
with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
    schema = yaml.safe_load(f)

REQUIRED_FIELDS = schema.get('required_fields', [])
VALID_TYPES = set(schema.get('valid_types', []))
TYPE_FIELDS = schema.get('type_specific_fields', {})

SKIP_FILES = {'_moc.md', 'log.md', 'index.md', 'overview.md'}
FORBIDDEN_CHARS = set('()[]{}#%&*|\\/:"<>?—.')


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                return fm if isinstance(fm, dict) else {}, parts[2]
            except Exception:
                return {}, content
    return {}, content




def get_words(text):
    return re.findall(r'\w+', text.lower())

def cosine_similarity(text1, text2):
    vec1 = Counter(get_words(text1))
    vec2 = Counter(get_words(text2))
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def extract_links(content):
    """Extract [[wikilinks]] from content."""
    return re.findall(r'\[\[(.*?)\]\]', content)


def extract_taxonomy_tags():
    """Parse taxonomy.md and extract ALL valid tags from our format:
    - category: tag1, tag2, tag3
    Also extracts section headers (### header) as valid tags.
    """
    tags = set()
    if not os.path.exists(TAXONOMY_FILE):
        return tags

    with open(TAXONOMY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Extract ### section headers as tags (e.g., ### statistics → statistics)
            if line.startswith('### '):
                header = line[4:].strip().lower()
                if header and not header.startswith('('):
                    tags.add(header)
                continue

            # Extract from "- category: tag1, tag2, tag3" format
            match = re.match(r'^-\s+(.+)', line)
            if match:
                content = match.group(1)

                # Handle "key: value1, value2" format
                if ':' in content:
                    key, values = content.split(':', 1)
                    key = key.strip().lower()
                    if key and not key.startswith('(') and not key.startswith('→'):
                        tags.add(key)
                    for v in values.split(','):
                        v = v.strip().lower()
                        if v and not v.startswith('('):
                            tags.add(v)
                else:
                    # Handle "- tag1, tag2, tag3" format (no key)
                    for v in content.split(','):
                        v = v.strip().lower()
                        if v and not v.startswith('('):
                            tags.add(v)

    return tags


def extract_tag_folder_mapping():
    """Dynamically parse Tag→Folder Mapping table from taxonomy.md.
    Reads the table at the bottom of taxonomy.md.
    """
    mapping = {}  # subfolder_name -> set of tags
    if not os.path.exists(TAXONOMY_FILE):
        return mapping

    with open(TAXONOMY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the mapping table section
    table_match = re.search(r'## Tag→Folder Mapping Reference.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)*)', content, re.DOTALL)
    if not table_match:
        return mapping

    for line in table_match.group(1).strip().split('\n'):
        if not line.startswith('|'):
            continue
        parts = line.split('|')
        if len(parts) < 3:
            continue

        tags_cell = parts[1].strip()
        folder_cell = parts[2].strip()

        # Extract folder name
        folder_match = re.search(r'`([\w-]+/[\w-]+)/`', folder_cell)
        if not folder_match:
            # Handle type= and filename= rules
            if 'type=' in tags_cell:
                type_match = re.search(r'type=`(\w+)`', tags_cell)
                folder_match2 = re.search(r'`([\w-]+/[\w-]+)/`', folder_cell)
                if type_match and folder_match2:
                    mapping.setdefault(folder_match2.group(1), {'types': set(), 'tags': set()})
                    mapping[folder_match2.group(1)]['types'].add(type_match.group(1))
                continue
            elif 'filename=' in tags_cell:
                continue
            else:
                continue

        folder = folder_match.group(1)
        if folder not in mapping:
            mapping[folder] = {'types': set(), 'tags': set()}

        # Extract individual tags from backtick-delimited list
        tags_found = re.findall(r'`([^`]+)`', tags_cell)
        for tag in tags_found:
            mapping[folder]['tags'].add(tag.lower())

    return mapping


# Patterns for junk file detection
JUNK_PATTERNS = [
    re.compile(r'^item\d+\.md$'),           # item1.md, item2.md, ...
    re.compile(r'^Empty_Document.*\.md$'),   # Empty_Document_xxx.md
    re.compile(r'^Untitled.*\.md$'),          # Untitled.md
    re.compile(r'^Extracted_Data.*\.md$'),    # Extracted_Data_N.md
]


def run_linter():
    schema_errors = []
    type_errors = []
    domain_errors = []
    staleness_warnings = []
    coverage_gaps = []
    moc_errors = []
    orphan_warnings = []
    duplicate_errors = []
    naming_errors = []
    tag_folder_errors = []
    tag_norm_errors = []
    taxonomy_errors = []
    uncategorized_overflow = []
    # New checks
    title_duplicate_errors = []
    merge_debris_warnings = []
    junk_file_errors = []
    crosslink_warnings = []
    content_duplicate_errors = []

    structural_errors_count = 0

    files_data = {}
    all_links = set()
    normalized_names = defaultdict(list)
    title_map = defaultdict(list)  # normalized title -> [relpath, ...]
    semantic_map = defaultdict(set)  # normalized string (title or alias) -> set of relpaths
    taxonomy_tags = extract_taxonomy_tags()
    tag_folder_mapping = extract_tag_folder_mapping()
    uncategorized_tags = defaultdict(list)

    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue

            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, WIKI_DIR).replace('\\', '/')
            folder = os.path.dirname(relpath)

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            fm, body = parse_frontmatter(content)
            links = extract_links(body)
            for link in links:
                all_links.add(link.split('|')[0].lower().replace(' ', '_'))

            tags = fm.get('tags', [])
            if not isinstance(tags, list):
                schema_errors.append(f"{relpath}: 'tags' must be a list")
                structural_errors_count += 1
                tags = []
            
            aliases = fm.get('aliases', [])
            if not isinstance(aliases, list):
                schema_errors.append(f"{relpath}: 'aliases' must be a list")
                structural_errors_count += 1

            files_data[relpath] = {
                'fm': fm,
                'body': body,
                'links': links,
                'folder': folder,
                'name': file,
                'tags': tags
            }

            # Check 9: Naming Convention
            # Check for spaces
            if ' ' in file:
                naming_errors.append(f"{relpath}: Filename contains spaces")
                structural_errors_count += 1

            # Check for forbidden characters (excluding hyphens and underscores which are allowed)
            basename_no_ext = file.replace('.md', '')
            for ch in basename_no_ext:
                if ch in FORBIDDEN_CHARS:
                    naming_errors.append(f"{relpath}: Filename contains forbidden character '{ch}'")
                    structural_errors_count += 1
                    break  # One error per file for forbidden chars

            # Duplicate detection normalization (skip _moc.md — expected in every folder)
            if file != '_moc.md':
                norm_name = re.sub(r'\(.*?\)', '', file).lower().replace('.md', '').replace(' ', '_').replace('-', '_').replace('.', '_')
                norm_name = re.sub(r'_+', '_', norm_name)
                normalized_names[norm_name].append(relpath)

            if file in SKIP_FILES:
                continue

            # Check 1: Schema Integrity
            missing_fields = [field for field in REQUIRED_FIELDS if field not in fm]
            if missing_fields:
                schema_errors.append(f"{relpath}: Missing fields {missing_fields}")
                structural_errors_count += 1

            # Check 2: Type Validation
            ftype = fm.get('type')
            if ftype:
                if ftype not in VALID_TYPES:
                    type_errors.append(f"{relpath}: Invalid type '{ftype}'")
                    structural_errors_count += 1
                elif ftype in TYPE_FIELDS:
                    missing_type_fields = [tf for tf in TYPE_FIELDS[ftype] if tf not in fm]
                    if missing_type_fields:
                        type_errors.append(f"{relpath}: Type '{ftype}' missing fields {missing_type_fields}")
                        structural_errors_count += 1
            else:
                type_errors.append(f"{relpath}: Missing type")
                structural_errors_count += 1

            # Check 3: Domain Placement (Level 1)
            if ftype == 'person' and not folder.startswith('people'):
                domain_errors.append(f"{relpath}: Person type should be in people/ (currently in {folder}/)")
                structural_errors_count += 1
            if ftype == 'tool' and not folder.startswith('tools'):
                domain_errors.append(f"{relpath}: Tool type should be in tools/ (currently in {folder}/)")
                structural_errors_count += 1
            if ftype == 'project' and not folder.startswith('projects'):
                domain_errors.append(f"{relpath}: Project type should be in projects/ (currently in {folder}/)")
                structural_errors_count += 1

            # Check 3.5: Directory Depth Limit (Rule 8)
            if len(relpath.split('/')) > 3:
                domain_errors.append(f"{relpath}: Directory depth exceeds 2 levels (Rule 8)")
                structural_errors_count += 1

            # Check 4: Staleness
            timestamp = fm.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, date) and not isinstance(timestamp, datetime):
                        dt = datetime.combine(timestamp, datetime.min.time())
                    elif isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.split('T')[0])
                    else:
                        dt = None
                    if dt and (datetime.now() - dt).days > 365:
                        staleness_warnings.append(f"{relpath}: Last updated {(datetime.now() - dt).days} days ago")
                except (ValueError, TypeError):
                    pass

            # Check 5: Coverage Gaps
            if not body.strip():
                coverage_gaps.append(f"{relpath}: Empty body content")
                structural_errors_count += 1  # Empty body is now structural
            elif len(body.split()) < 50:
                coverage_gaps.append(f"{relpath}: Too short (<50 words)")

            # Check 5.5: Non-English Language Detection (Rule 01.3)
            if body.strip():
                alpha_body = re.sub(r'[\W_]+', '', body)
                if alpha_body:
                    non_ascii = len([c for c in alpha_body if ord(c) > 127])
                    if non_ascii / len(alpha_body) > 0.1:
                        coverage_gaps.append(f"{relpath}: Contains high proportion of non-English characters (Rule 01.3)")
                        structural_errors_count += 1

            # Check 14: Title-based Semantic Duplicate Detection
            title = fm.get('title', '')
            if title:
                norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
                if norm_title:
                    title_map[norm_title].append(relpath)
                    semantic_map[norm_title].add(relpath)
            
            # Also add aliases to semantic map
            for al in aliases:
                norm_al = re.sub(r'[^a-z0-9]', '', str(al).lower())
                if norm_al:
                    semantic_map[norm_al].add(relpath)
            # Check 15: Merged Content Debris
            if '## Merged Content' in content or content.count('## Background') > 1 or content.count('## Role & Contributions') > 1:
                merge_debris_warnings.append(f"{relpath}: Contains duplicated sections from merge — needs consolidation")

            # Check 16: Junk/Phantom File Detection
            for pattern in JUNK_PATTERNS:
                if pattern.match(file):
                    junk_file_errors.append(f"{relpath}: Junk/placeholder file (matches pattern '{pattern.pattern}')")
                    structural_errors_count += 1
                    break

            # Check 17: Cross-link Poverty
            file_links = extract_links(body)
            if not file_links:
                crosslink_warnings.append(f"{relpath}: No wikilinks — isolated note")

            # Check 10: Tag→Folder Consistency
            expected_folder = None
            expected_domain = None

            # Tag-based routing
            for subfolder, rule in tag_folder_mapping.items():
                if 'tags' in rule:
                    for tag in tags:
                        if tag.lower() in rule['tags']:
                            expected_folder = subfolder
                            expected_domain = subfolder.split('/')[0]
                            break
                if expected_folder:
                    break

            if expected_folder:
                if folder.endswith('_uncategorized'):
                    current_domain = folder.split('/')[0]
                    if current_domain != expected_domain:
                        tag_folder_errors.append(f"{relpath}: Tags suggest domain {expected_domain}/ but is in {current_domain}/_uncategorized/")
                        structural_errors_count += 1
                elif folder != expected_folder:
                    tag_folder_errors.append(f"{relpath}: Tags suggest {expected_folder}/ but is in {folder}/")
                    structural_errors_count += 1

            # Check 11: Tag Normalization
            for tag in tags:
                if any(c.isupper() for c in tag):
                    tag_norm_errors.append(f"{relpath}: Uppercase tag '{tag}' → should be '{tag.lower()}'")
                    structural_errors_count += 1
                elif '/' in tag:
                    tag_norm_errors.append(f"{relpath}: Slash-prefixed tag '{tag}' → remove prefix")
                    structural_errors_count += 1
                elif tag.lower() in VALID_TYPES:
                    tag_norm_errors.append(f"{relpath}: Page type '{tag}' used as tag (Rule 8)")
                    structural_errors_count += 1

            # Check 12: Taxonomy Alignment
            if taxonomy_tags:
                for tag in tags:
                    normalized_tag = tag.lower().replace('/', '').strip()
                    if normalized_tag and normalized_tag not in taxonomy_tags:
                        taxonomy_errors.append(f"{relpath}: Tag '{tag}' not in taxonomy")
                        structural_errors_count += 1

            # Check 13: _uncategorized Overflow
            if '_uncategorized' in folder:
                for tag in tags:
                    uncategorized_tags[tag.lower()].append(relpath)

    # Check 6: MOC Sync — check all folders for _moc.md
    folders_with_files = defaultdict(list)
    for relpath, data in files_data.items():
        if data['name'] not in SKIP_FILES and data['name'] != '_moc.md':
            folders_with_files[data['folder']].append(relpath)

    for folder, folder_files in folders_with_files.items():
        if not folder or folder.startswith('_'):
            continue
        moc_path = f"{folder}/_moc.md"
        if moc_path not in files_data:
            moc_errors.append(f"{folder}/: Missing _moc.md ({len(folder_files)} files in folder)")
            structural_errors_count += 1
        else:
            # Check if all files are listed in MOC
            moc_links = set()
            for link in files_data[moc_path].get('links', []):
                moc_links.add(link.split('|')[0].lower().replace(' ', '_'))

            for fp in folder_files:
                fname = os.path.basename(fp).replace('.md', '').lower().replace(' ', '_')
                if fname not in moc_links:
                    moc_errors.append(f"{fp}: Not listed in {moc_path}")

            # Reverse check: MOC links pointing to non-existent files (dead links)
            all_basenames = set()
            for rp, d in files_data.items():
                all_basenames.add(d['name'].replace('.md', '').lower().replace(' ', '_'))
            for link in files_data[moc_path].get('links', []):
                link_target = link.split('|')[0].split('/')[-1].lower().replace(' ', '_')
                if link_target and link_target != '_moc' and link_target not in all_basenames:
                    moc_errors.append(f"{moc_path}: Dead link [[{link.split('|')[0]}]] — file does not exist")
                    structural_errors_count += 1

    # Check 7: Orphan Check
    for relpath, data in files_data.items():
        if data['name'] in SKIP_FILES or data['name'] == '_moc.md':
            continue
        base_name = data['name'].replace('.md', '').lower().replace(' ', '_')
        if base_name not in all_links:
            orphan_warnings.append(f"{relpath}: No internal links point to this file")

    # Check 8: Duplicate Detection (filename-based)
    for norm_name, paths in normalized_names.items():
        if len(paths) > 1:
            duplicate_errors.append(f"Normalized '{norm_name}' -> {', '.join(paths)}")
            structural_errors_count += 1

    # Check 14: Semantic Duplicate Detection (Title & Alias intersection)
    for norm_val, path_set in semantic_map.items():
        if len(path_set) > 1:
            # Exclude if already caught by filename duplicate detection
            already_caught = False
            for norm_name, name_paths in normalized_names.items():
                if len(name_paths) > 1 and set(name_paths) == path_set:
                    already_caught = True
                    break
            if not already_caught:
                title_duplicate_errors.append(f"Shared concept (Title/Alias) '{norm_val}' -> {', '.join(sorted(path_set))}")
                structural_errors_count += 1

    # Check 13: _uncategorized Overflow
    for tag, paths in uncategorized_tags.items():
        if len(paths) >= 3:
            uncategorized_overflow.append(f"Tag '{tag}' in {len(paths)} uncategorized files → candidate for new subfolder: {', '.join(paths[:5])}")
            structural_errors_count += 1

    # Calculate health — separate structural from advisory
    advisory_count = (len([c for c in coverage_gaps if 'Too short' in c])
                      + len(taxonomy_errors)
                      + len(merge_debris_warnings) + len(crosslink_warnings))
    if structural_errors_count == 0:
        health = "🟢 Green (0 structural errors)"
    elif structural_errors_count < 20:
        health = f"🟡 Yellow ({structural_errors_count} structural errors)"
    else:
        health = f"🔴 Red ({structural_errors_count} structural errors)"
    if advisory_count > 0:
        health += f" | {advisory_count} advisory warnings"

    # Build report
    sections = [
        ("1. Schema Integrity", schema_errors),
        ("2. Type Validation", type_errors),
        ("3. Domain Placement", domain_errors),
        ("4. Staleness", staleness_warnings),
        ("5. Coverage Gaps", coverage_gaps),
        ("6. MOC Sync", moc_errors),
        ("7. Orphan Check", orphan_warnings),
        ("8. Duplicate Detection (Filename)", duplicate_errors),
        ("9. Naming Convention", naming_errors),
        ("10. Tag→Folder Consistency", tag_folder_errors),
        ("11. Tag Normalization", tag_norm_errors),
        ("12. Taxonomy Alignment", taxonomy_errors),
        ("13. _uncategorized Overflow", uncategorized_overflow),
        ("14. Semantic Duplicate (Title/Alias)", title_duplicate_errors),
        ("15. Merge Debris", merge_debris_warnings),
        ("16. Junk/Phantom Files", junk_file_errors),
        ("17. Cross-link Poverty", crosslink_warnings),
        ("18. Content Similarity (TF-IDF)", content_duplicate_errors),
    ]



    # Check 18: Content Similarity (Semantic Duplication)
    file_list = list(files_data.items())
    n = len(file_list)
    for i in range(n):
        for j in range(i + 1, n):
            path1, data1 = file_list[i]
            path2, data2 = file_list[j]
            if data1['name'] in SKIP_FILES or data2['name'] in SKIP_FILES:
                continue
                
            name1 = data1['name'].replace('.md', '').lower()
            name2 = data2['name'].replace('.md', '').lower()
            
            # Content sim
            if len(data1.get('body', '').split()) > 30 and len(data2.get('body', '').split()) > 30:
                content_sim = cosine_similarity(data1.get('body', ''), data2.get('body', ''))
                if content_sim > 0.75:
                    content_duplicate_errors.append(f"{path1} <-> {path2} (Content Similarity: {content_sim:.2f})")
                    structural_errors_count += 1

    report = f"# Wiki Linter Report\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"## Overall Health\n\n**Status:** {health}\n\n"
    report += f"**Taxonomy tags loaded:** {len(taxonomy_tags)}\n"
    report += f"**Tag→Folder mappings loaded:** {sum(len(v.get('tags', set())) for v in tag_folder_mapping.values())} tags across {len(tag_folder_mapping)} subfolders\n\n"

    for title, errors in sections:
        report += f"## {title}\n"
        if errors:
            for err in errors:
                report += f"- {err}\n"
            report += f"\n**Total: {len(errors)} issues**\n"
        else:
            report += "- ✅ No issues\n"
        report += "\n"

    # Overall health table
    structural_checks = {"1. Schema Integrity", "2. Type Validation", "3. Domain Placement",
                         "6. MOC Sync", "8. Duplicate Detection (Filename)", "9. Naming Convention",
                         "10. Tag\u2192Folder Consistency", "11. Tag Normalization",
                         "14. Semantic Duplicate (Title/Alias)", "16. Junk/Phantom Files"}
    report += "## Overall Health Table\n\n"
    report += "| # | Check | Category | Status | Count |\n"
    report += "|---|-------|----------|--------|-------|\n"
    for title, errors in sections:
        cat = "Structural" if title in structural_checks else "Advisory"
        status = "PASS" if not errors else ("WARN" if len(errors) < 10 else "FAIL")
        icon = "✅" if not errors else ("⚠️" if len(errors) < 10 else "🔴")
        report += f"| {title} | {cat} | {icon} {status} | {len(errors)} |\n"

    report += f"\n## Next Steps\n"
    if structural_errors_count > 0:
        report += "- **Priority 1**: Fix structural errors (schema, naming, duplicates, domain placement) first.\n"
    if advisory_count > 0:
        report += "- **Priority 2**: Address advisory warnings (coverage gaps, taxonomy alignment, uncategorized overflow).\n"
    if structural_errors_count == 0 and advisory_count == 0:
        report += "- All checks passed. Wiki is fully healthy.\n"
    report += "- Run linter again after fixes to verify.\n"

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    health_display = health.encode('ascii', 'ignore').decode('ascii').strip()
    print(f"Report generated at {REPORT_FILE}")
    print(f"Taxonomy tags loaded: {len(taxonomy_tags)}")
    print(f"Tag-Folder mappings: {len(tag_folder_mapping)} subfolders")
    print(f"Overall: {health_display}")


if __name__ == '__main__':
    run_linter()
