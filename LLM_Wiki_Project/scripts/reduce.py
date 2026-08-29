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
from datetime import datetime

WIKI_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "wiki"
)
LOG_FILE = os.path.join(WIKI_ROOT, "log.md")

DOMAINS = ["academic", "business", "dev", "projects", "people", "tools", "languages", "personal"]


def append_to_log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        date_str = datetime.now().strftime("%Y-%m-%d")
        f.write(f"\n- **{date_str}**: {msg}")
    print(msg)


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
    If a heading appears multiple times, appends to the existing one.
    """
    sections = {}
    current_heading = "__intro__"
    current_lines = []
    for line in body.split("\n"):
        if line.startswith("## "):
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
    """Merge new content into existing page by section, not by appending."""
    # Parse existing frontmatter and body
    existing_fm_str = ""
    existing_body = existing_content
    if existing_content.startswith("---"):
        parts = existing_content.split("---", 2)
        if len(parts) >= 3:
            existing_fm_str = f"---{parts[1]}---"
            existing_body = parts[2]

    # Strip frontmatter from new content
    new_body = re.sub(r"^---.*?---\n?", "", new_content, flags=re.DOTALL).strip()

    existing_sections = extract_sections(existing_body)
    new_sections = extract_sections(new_body)

    # Merge: for each new section, append new bullet points to existing section
    for heading, new_text in new_sections.items():
        if heading in existing_sections:
            # Append only genuinely new lines (avoid exact duplicates)
            existing_lines = set(existing_sections[heading].split("\n"))
            new_lines = []
            for line in new_text.split("\n"):
                if line.strip() and line not in existing_lines:
                    new_lines.append(line)
            if new_lines:
                existing_sections[heading] += "\n" + "\n".join(new_lines)
        else:
            # New section entirely — add it
            existing_sections[heading] = new_text

    # Rebuild body
    rebuilt_body = ""
    # Put intro first
    if "__intro__" in existing_sections:
        rebuilt_body += existing_sections.pop("__intro__") + "\n\n"
    for heading, text in existing_sections.items():
        rebuilt_body += f"{heading}\n{text}\n\n"

    return f"{existing_fm_str}\n{rebuilt_body.rstrip()}\n"


def process_file(filepath):
    filename = os.path.basename(filepath)

    # Handle MERGE_ prefix from upgraded ingest_mapper
    is_merge_target = filename.startswith("MERGE_")
    if is_merge_target:
        filename = filename[6:]  # Strip "MERGE_" prefix

    parts = filename.split("_")

    domain = "personal"  # default
    subdomain = None
    actual_filename = filename

    # Try to parse domain prefix
    if parts[0].lower() in [d.lower() for d in DOMAINS]:
        domain = parts[0].lower()
        # Try to parse subdomain (heuristic: second part is lowercase and short)
        if len(parts) > 2 and parts[1].islower() and len(parts[1]) < 20:
            subdomain = parts[1]
            actual_filename = "_".join(parts[2:])
        else:
            actual_filename = "_".join(parts[1:])

    if not actual_filename.endswith(".md"):
        actual_filename += ".md"

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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
