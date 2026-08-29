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

**References:**
- [<- Back to AGENTS.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/AGENTS.md)
- [01_architecture.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/01_architecture.md)
- [03_routing.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/03_routing.md)
