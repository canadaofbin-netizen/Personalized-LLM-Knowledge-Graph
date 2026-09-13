"""
reduce.py — Ingest Reduce Phase
Collects proposed wiki pages from mapper subagent scratch directories,
performs duplicate detection, and creates/merges pages into the wiki.

Usage:
  python reduce.py [scratch_dir_1] [scratch_dir_2] ...
  
If no directories are specified, scans ALL subdirectories under the default
scratch/map_results/ path in the calling agent's artifact directory.
"""

import os
import re
import sys
import yaml
from datetime import datetime

WIKI_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "wiki"
)
LOG_FILE = os.path.join(WIKI_ROOT, "log.md")

DOMAINS = [
    "academic",
    "business",
    "career",
    "dev",
    "people",
    "personal",
    "projects",
    "tools",
]


def append_to_log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        date_str = datetime.now().strftime("%Y-%m-%d")
        f.write(f"\n- **{date_str}**: {msg}")
    pass


def normalize_name(name):
    n = name.lower().replace("_", "").replace("-", "").replace(" ", "").replace(".", "")
    return n


def find_existing_file(basename):
    norm_base = normalize_name(basename)
    for root, _, files in os.walk(WIKI_ROOT):
        for f in files:
            if normalize_name(f) == norm_base:
                return os.path.join(root, f)
    return None


def extract_sections(body):
    """Split markdown body into {heading: content} dict.
    Recognizes H1, H2, and H3 headings.
    """
    sections = {}
    current_heading = "__intro__"
    current_lines = []
    for line in body.split("\n"):
        if re.match(r"^#{1,3}\s+", line):
            if current_lines:
                text = "\n".join(current_lines).strip()
                if current_heading in sections:
                    sections[current_heading] += "\n" + text
                else:
                    sections[current_heading] = text
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        text = "\n".join(current_lines).strip()
        if current_heading in sections:
            sections[current_heading] += "\n" + text
        else:
            sections[current_heading] = text
    return sections


def intelligent_merge(existing_content, new_content):
    """Merge new content into existing page by section and frontmatter without duplicating."""
    # 1. Parse existing frontmatter and body
    existing_fm = {}
    existing_body = existing_content
    if existing_content.strip().startswith("---"):
        parts = existing_content.split("---", 2)
        if len(parts) >= 3:
            try:
                existing_fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                existing_fm = {}
            existing_body = parts[2]

    # 2. Parse new frontmatter and body
    new_fm = {}
    new_body = new_content
    if new_content.strip().startswith("---"):
        parts = new_content.split("---", 2)
        if len(parts) >= 3:
            try:
                new_fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                new_fm = {}
            new_body = parts[2]

    # Strip any stray embedded frontmatter blocks in new_body
    new_body = re.sub(r"^---.*?---\s*", "", new_body.strip(), flags=re.DOTALL)

    # 3. Merge frontmatter fields cleanly
    merged_fm = dict(existing_fm)
    for field in ["tags", "aliases", "sources"]:
        ex_list = merged_fm.get(field, []) or []
        nw_list = new_fm.get(field, []) or []
        combined = []
        seen = set()
        for item in ex_list + nw_list:
            clean_item = str(item).strip()
            # Strip [[ ]] if someone passed wikilink
            if clean_item.startswith("[[") and clean_item.endswith("]]"):
                clean_item = clean_item[2:-2].strip()
            if clean_item and clean_item.lower() not in seen:
                seen.add(clean_item.lower())
                combined.append(clean_item)
        merged_fm[field] = combined

    # 4. Merge body sections with deduplication
    existing_sections = extract_sections(existing_body)
    new_sections = extract_sections(new_body)

    for heading, new_text in new_sections.items():
        if heading in existing_sections:
            ex_text = existing_sections[heading]
            # Paragraph level deduplication
            ex_paras = {re.sub(r"\s+", " ", p).lower().strip() for p in ex_text.split("\n\n") if p.strip()}
            new_paras_to_add = []
            for p in new_text.split("\n\n"):
                norm_p = re.sub(r"\s+", " ", p).lower().strip()
                if norm_p and norm_p not in ex_paras:
                    ex_paras.add(norm_p)
                    new_paras_to_add.append(p.strip())
            if new_paras_to_add:
                existing_sections[heading] += "\n\n" + "\n\n".join(new_paras_to_add)
        else:
            # Avoid duplicate H1 if another H1 exists
            if heading.startswith("# ") and any(h.startswith("# ") for h in existing_sections.keys()):
                heading = "## " + heading[2:]
            existing_sections[heading] = new_text

    # 5. Rebuild clean markdown
    rebuilt_body = ""
    if "__intro__" in existing_sections:
        intro_text = existing_sections.pop("__intro__").strip()
        if intro_text:
            rebuilt_body += intro_text + "\n\n"
    for heading, text in existing_sections.items():
        text_str = text.strip()
        if text_str:
            rebuilt_body += f"{heading}\n{text_str}\n\n"

    fm_yaml = yaml.dump(merged_fm, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{fm_yaml}\n---\n\n{rebuilt_body.rstrip()}\n"


def process_file(filepath):
    filename = os.path.basename(filepath)

    # Handle MERGE_ prefix from upgraded ingest_mapper
    is_merge_target = filename.startswith("MERGE_")
    if is_merge_target:
        filename = filename[6:]  # Strip "MERGE_" prefix

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse frontmatter to inspect domain, type, tags
    fm = {}
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                fm = {}

    # Priority 0: Type Override (Rule 03)
    ftype = str(fm.get("type", "")).lower()
    type_domain_map = {
        "person": "people",
        "tool": "tools",
        "project": "projects",
    }

    domain = "personal"  # default fallback
    if ftype in type_domain_map:
        domain = type_domain_map[ftype]
    elif fm.get("domain") and str(fm.get("domain")).lower() in DOMAINS:
        domain = str(fm.get("domain")).lower()

    subdomain = None
    actual_filename = filename

    name_parts = filename.split("_")
    # If filename starts with a recognized canonical domain
    if name_parts[0].lower() in DOMAINS:
        if ftype not in type_domain_map and not fm.get("domain"):
            domain = name_parts[0].lower()

        # Check if second part matches an actual existing subfolder under wiki/{domain}/
        if len(name_parts) > 2:
            candidate_sub = name_parts[1].lower()
            subfolder_path = os.path.join(WIKI_ROOT, domain, candidate_sub)
            if os.path.isdir(subfolder_path):
                subdomain = candidate_sub
                actual_filename = "_".join(name_parts[2:])
            else:
                actual_filename = "_".join(name_parts[1:])
        else:
            actual_filename = "_".join(name_parts[1:])

    if not actual_filename.endswith(".md"):
        actual_filename += ".md"

    # Check for duplicates
    existing_path = find_existing_file(actual_filename)
    if existing_path:
        # Intelligent merge instead of naive append
        with open(existing_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
        merged = intelligent_merge(existing_content, content)
        with open(existing_path, "w", encoding="utf-8") as f:
            f.write(merged)
        append_to_log(f"Merged `{actual_filename}` into existing file: `{os.path.relpath(existing_path, WIKI_ROOT)}`")
    else:
        # Create new page
        if subdomain:
            target_dir = os.path.join(WIKI_ROOT, domain, subdomain)
        else:
            target_dir = os.path.join(WIKI_ROOT, domain)

        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, actual_filename)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        append_to_log(f"Created new page: `{os.path.relpath(target_path, WIKI_ROOT)}`")


def main():
    source_dirs = sys.argv[1:] if len(sys.argv) > 1 else []

    if not source_dirs:
        print("Usage: python reduce.py <dir1> [dir2] ...")
        print("No directories specified. Nothing to do.")
        return

    print("Starting Reduce phase...")
    file_count = 0
    for sdir in source_dirs:
        if os.path.exists(sdir):
            for root, _, files in os.walk(sdir):
                for f in files:
                    if f.endswith(".md"):
                        process_file(os.path.join(root, f))
                        file_count += 1
        else:
            print(f"Warning: Directory not found: {sdir}")

    print(f"Reduce phase completed. Processed {file_count} files.")


if __name__ == "__main__":
    main()
