---
name: Wiki Architecture Rules
description: Rules for wiki directory structure and schema
trigger: always_on
---
# 01. Wiki Architecture & Schema

1. **Wiki Structure**: `LLM_Wiki_Project/` contains:
   - `raw/`: Immutable sources (`assets/` and `imports/`).
   - `wiki/`: Generated markdown pages organized by domain (max depth: 2 levels). Every folder/subfolder must contain a `_moc.md`.
   - `templates/` & `scripts/`: System tools and templates.

2. **Page Frontmatter (Schema Integrity)**: Always read and strictly adhere to [schema.yaml](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/schema.yaml) for valid types and required frontmatter fields.

3. **Language**: All generated files MUST be written in **English only**.

4. **Domain Routing**: Enforce type-to-domain mapping (e.g., `type: person` -> `wiki/people/`). Auto-create subfolders based on [taxonomy.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/taxonomy.md) level-2 categories using the logic in [03_routing.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/03_routing.md). Tag hygiene: Do NOT use frontmatter `type` values as tags.
