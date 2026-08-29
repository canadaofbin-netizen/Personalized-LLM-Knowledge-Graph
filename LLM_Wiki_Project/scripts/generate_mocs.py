"""
generate_mocs.py — MOC (Map of Content) Generator
Scans all directories under wiki/ and generates _moc.md files
that serve as navigation hubs for each folder.

Usage:
  python generate_mocs.py
"""

import os
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from datetime import datetime

WIKI_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "wiki"
)


def extract_frontmatter(filepath):
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            if HAS_YAML:
                return yaml.safe_load(match.group(1)) or {}
            else:
                # Simple fallback parser
                fm = {}
                for line in match.group(1).split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        fm[key] = val
                return fm
    except Exception:
        pass
    return {}


def get_pages_in_dir(dirpath):
    """Get all .md files in a directory (not recursive, excluding _moc.md)."""
    pages = []
    if not os.path.isdir(dirpath):
        return pages
    for f in sorted(os.listdir(dirpath)):
        if f.endswith(".md") and f != "_moc.md" and not f.startswith("."):
            full = os.path.join(dirpath, f)
            if os.path.isfile(full):
                fm = extract_frontmatter(full)
                title = fm.get("title", f.replace(".md", "").replace("_", " "))
                if isinstance(title, str):
                    title = title.strip('"').strip("'")
                page_type = fm.get("type", "unknown")
                description = fm.get("description", "")
                if isinstance(description, str):
                    description = description.strip('"').strip("'")
                pages.append({
                    "filename": f,
                    "title": title,
                    "type": page_type,
                    "description": description
                })
    return pages


def get_subdirs(dirpath):
    """Get immediate subdirectories."""
    subdirs = []
    if not os.path.isdir(dirpath):
        return subdirs
    for d in sorted(os.listdir(dirpath)):
        full = os.path.join(dirpath, d)
        if os.path.isdir(full) and not d.startswith("."):
            subdirs.append(d)
    return subdirs


def generate_moc(dirpath, domain_name):
    """Generate a _moc.md for the given directory."""
    pages = get_pages_in_dir(dirpath)
    subdirs = get_subdirs(dirpath)

    timestamp = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append("---")
    lines.append("type: moc")
    lines.append(f'title: "{domain_name} Map of Content"')
    lines.append(f'aliases: ["{domain_name} MOC", "{domain_name} Map of Content"]')
    lines.append(f'description: "Navigation hub for {domain_name} domain pages."')
    lines.append(f"tags: [{domain_name.lower().replace(' ', '-')}]")
    lines.append(f"timestamp: {timestamp}")
    lines.append("sources: []")
    lines.append(f"domain: {domain_name.lower().replace(' ', '-')}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {domain_name} Map of Content")
    lines.append("")

    # List subfolders first
    if subdirs:
        lines.append("## Subfolders")
        lines.append("")
        for sd in subdirs:
            lines.append(f"- [[{sd}/_moc|{sd.replace('_', ' ').title()}]]")
        lines.append("")

    # Group pages by type
    type_groups = {}
    for p in pages:
        t = p["type"]
        if t not in type_groups:
            type_groups[t] = []
        type_groups[t].append(p)

    type_order = [
        "concept", "entity", "summary", "reading_note", "collection",
        "project", "person", "tool", "log", "unknown"
    ]
    type_labels = {
        "concept": "Concepts",
        "entity": "Entities",
        "summary": "Summaries",
        "reading_note": "Reading Notes",
        "collection": "Collections",
        "project": "Projects",
        "person": "People",
        "tool": "Tools",
        "log": "Logs",
        "unknown": "Other"
    }

    for t in type_order:
        if t in type_groups:
            label = type_labels.get(t, t.title())
            lines.append(f"## {label}")
            lines.append("")
            for p in type_groups[t]:
                fname = p["filename"].replace(".md", "")
                desc = f" — {p['description']}" if p["description"] else ""
                lines.append(f"- [[{fname}]]{desc}")
            lines.append("")

    # Handle any types not in the order list
    for t, group in type_groups.items():
        if t not in type_order:
            lines.append(f"## {t.title()}")
            lines.append("")
            for p in group:
                fname = p["filename"].replace(".md", "")
                lines.append(f"- [[{fname}]]")
            lines.append("")

    moc_path = os.path.join(dirpath, "_moc.md")
    with open(moc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return moc_path


def main():
    created = []

    for root, dirs, files in os.walk(WIKI_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        md_files = [f for f in files if f.endswith(".md") and f != "_moc.md"]
        if md_files or dirs:
            rel = os.path.relpath(root, WIKI_ROOT).replace("\\", "/")
            if rel == ".":
                domain_name = "Wiki"
            else:
                domain_name = os.path.basename(root).replace("_", " ").title()

            moc_path = generate_moc(root, domain_name)
            print(f"Created MOC: {os.path.relpath(moc_path, WIKI_ROOT)}")
            created.append(moc_path)

    print(f"\nTotal MOCs created/updated: {len(created)}")


if __name__ == "__main__":
    main()
