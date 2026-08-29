---
name: all
description: End-to-end knowledge pipeline. Runs Scrape → Extract → Ingest → MOC → Lint in a single fully-automated pass.
---

# `/all` — End-to-End Pipeline

Execute Scrape → Extract → Ingest → MOC → Lint without user confirmation. See [extract_all/SKILL.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract_all/SKILL.md) for invocation arguments.

## Pipeline Stages

1. **Stage 1: SCRAPE_EMAILS**: Run `python LLM_Wiki_Project/scripts/outlook_scraper/outlook_scraper.py --scrape --incremental` to fetch new emails to `raw/imports/outlook_emails.json`. (If an Auth or 2FA error occurs, log it and SKIP to Stage 2 without halting the pipeline).
2. **Stage 2: EXTRACT**:
   - **Auto-Route**: Run `python LLM_Wiki_Project/scripts/auto_route_raw.py` FIRST to ensure any manually dropped files in `raw/` are safely moved to `raw/imports/`.
   - **Extract Chats & Web**: Run logic from [extract_all/SKILL.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract_all/SKILL.md) to harvest past conversations and proactive web gaps (uses previous run's lint report).
   - **Extract Files**: Run logic from [extract/SKILL.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract/SKILL.md) to convert unprocessed imports (including `outlook_emails.json`) to markdown in `raw/assets/`.
3. **Stage 3: INGEST**: Run logic from [ingest/SKILL.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/ingest/SKILL.md). Map Phase reads and classifies raw files via subagents to scratch directory. Reduce Phase sequentially checks duplicates and merges into `wiki/`.
4. **Stage 4: MOC**: Run `LLM_Wiki_Project/scripts/generate_mocs.py` sequentially after Ingest.
5. **Stage 5: LINT**: Run the full `/lint` skill (Phase 1: `LLM_Wiki_Project/scripts/run_linter.py` + Phase 2: AI Semantic Sweep via Map-Reduce subagents). Auto-fix Naming Convention, Tag Normalization, and Missing Frontmatter. DO NOT auto-fix Domain Placement, Duplicates, or Type Validation.

## Output
Generate `walkthrough.md` artifact summarizing extraction counts, ingested pages, MOC updates, lint status, and applied auto-fixes.

## Hard Rules
- **No User Interruption**.
- **Map-Reduce for Batch**: Always use subagents for Extract/Ingest batches. Reduce is strictly sequential.
- **Incremental**: Never re-extract unchanged content. Never delete knowledge on merge.
- **Reference**: Cross-reference [taxonomy.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/taxonomy.md) for tags.

## Error Handling
- **Stage Gate**: After each pipeline stage, verify output integrity. If any subagent reports failure or produces 0 output files when input was non-empty, **HALT** the pipeline immediately and report the error. Do NOT proceed to the next stage.
- **Malformed Data Guard**: Before Ingest, validate that all extracted files have valid YAML frontmatter. Skip files with parse errors and log them to `wiki/log.md`.
