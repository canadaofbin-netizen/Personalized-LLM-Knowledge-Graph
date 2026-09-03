---
name: Wiki Architecture Rules
description: Rules for wiki directory structure and schema
trigger: always_on
---
# 01. Wiki Architecture & Schema

1. **Wiki Structure**: `LLM_Wiki_Project/` contains:
   - `raw/`: Sources and archive:
     - `assets/`: Ingestion queue (unprocessed raw files).
     - `imports/`: Raw imports and sync state logs.
     - `processed/`: Permanent archive of completed raw files.
   - `wiki/`: Generated markdown pages organized by domain (max depth: 2 levels). Every folder/subfolder must contain a `_moc.md`.
   - `templates/` & `scripts/`: System tools and templates.

2. **Page Frontmatter (Schema Integrity)**: Always read and strictly adhere to [schema.yaml](file:///LLM_Wiki_Project/schema.yaml) for valid types and required frontmatter fields.

3. **Language**: All generated files MUST be written in **English only**.

4. **Domain Routing**: Enforce type-to-domain mapping (e.g., `type: person` -> `wiki/people/`). Auto-create subfolders based on [taxonomy.md](file:///LLM_Wiki_Project/taxonomy.md) level-2 categories using the logic in [03_routing.md](file:///.agents/rules/03_routing.md). Tag hygiene: Do NOT use frontmatter `type` values as tags.

5. **Canonical Root Domains Whitelist**: `wiki/` contains ONLY 8 canonical root domain directories: `academic/`, `business/`, `career/`, `dev/`, `people/`, `personal/`, `projects/`, and `tools/`. Creating root directories outside this whitelist or naming folders with spaces (e.g. `personal projects/`, `computer science/`) is strictly forbidden.

