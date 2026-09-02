---
name: Wiki Data Hygiene Rules
description: Rules for file naming, duplicate prevention, and cascade deletion
trigger: always_on
---
# 04. Data Hygiene and Deduplication

1. **File Naming Standard:** All files MUST use `Underscore_Separated_Title_Case` (e.g., `Author_Year_Reading_Notes.md`, `Brain-Computer_Interface.md`). No exceptions. Forbidden characters: `()[]{}#%&*|\/:"<>?—.` Tags MUST be lowercase, hyphen-separated.

2. **Duplicate Prevention & Normalization:** Search and MERGE into existing pages instead of creating duplicates. Normalization sequence for comparison:
1) Remove extensions and parenthetical suffixes.
2) Apply Unicode NFKD decomposition and strip diacritics (ASCII-only).
3) Strip all non-alphanumeric characters except spaces, hyphens, and underscores.
4) Convert spaces, hyphens, and periods to `_`.
5) Collapse consecutive underscores (`re.sub(r'_+', '_', name)`).
6) Strip leading and trailing underscores (`.strip('_')`).
7) Lowercase.
Ignore `_moc.md`. Flag duplicates in `wiki/log.md`.

3. **Cascade Cleanup:** Upon deleting ANY file, you MUST: 1) Remove/update all `[[wikilinks]]` referencing it in `_moc.md` and other wiki pages. 2) Log the deletion in `wiki/log.md`.

4. **Move Cascade:** Upon MOVING any file to a new location, you MUST: 1) Update all `[[wikilinks]]` that use explicit paths (e.g., `[[old_path/Page]]` → `[[new_path/Page]]`). 2) Update the source and destination `_moc.md` files. 3) Log the move in `wiki/log.md`.

5. **Source Citation Standard & Ghost Link Prevention:** Raw source files (`email_*.md`, `chat_extract_*.md`, `web_history_*.md`, `archive_chat_*.md`, `drive_doc_*.md`, etc.) MUST NEVER be enclosed in `[[wikilinks]]`. Always cite them as plain text strings in YAML frontmatter (`sources: [email_123_processed.md]`) or under body `## Sources` as `- email_123_processed.md`. Wikilinks (`[[...]]`) are strictly reserved for actual existing wiki knowledge pages inside `wiki/`.

6. **Single Frontmatter & Deduplicated Merging:** Every markdown note MUST contain exactly ONE YAML frontmatter block at lines 1–N. Never inject secondary YAML headers into the markdown body during merges. When merging new information, always strip incoming frontmatters, deduplicate repetitive paragraphs, and merge list fields (`tags`, `aliases`, `sources`) as set unions.

**References:**
- [<- Back to AGENTS.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/AGENTS.md)
- [01_architecture.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/01_architecture.md)
- [03_routing.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/03_routing.md)

