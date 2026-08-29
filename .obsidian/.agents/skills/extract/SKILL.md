---
name: extract
description: Extracts knowledge from conversations, Drive files, or Gemini exports and saves to raw/ for ingestion.
---

# Knowledge Extractor

**CRITICAL PHILOSOPHY: Extract preserves, Ingest summarizes.**
Capture ALL substantive knowledge verbatim. Do NOT condense or restructure.

## Modes

1. **`/extract`**: Default comprehensive mode. 
   - First, extract the current conversation (`<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl`). Focus on `USER_INPUT` and `PLANNER_RESPONSE`.
   - Then, automatically scan and extract all unprocessed files located in the `raw/` directory (acting as `/extract [folder]`).
2. **`/extract [file/URL]`**: Single file (Drive MCP or local). Check `.extract_log.json` for diffs.
3. **`/extract [folder]`**: Specifically target a folder to scan for unprocessed files. Use Map-Reduce Subagents for parallel extraction.

## Pre-processing (Auto-Routing)
- **CRITICAL STEP**: Before starting ANY extraction mode that involves files (including the default `/extract` and Modes 2 & 3), always run the auto-routing script to ensure any files the user dropped directly into `raw/` are moved to `raw/imports/`:
  `python "LLM_Wiki_Project/scripts/auto_route_raw.py"`
## Filters
- **INCLUDE**: Concepts, definitions, formulas, methodologies, code, user insights, corrections, and generated artifacts.
- **EXCLUDE**: Meta-discussions, system configs, generic coding help, and UI/infrastructure details (unless it is the studied domain).

## Incremental Extraction (Modes 2 & 3)
Check `LLM_Wiki_Project/raw/imports/.extract_log.json`. If unchanged, skip. If changed, extract ONLY modified sections using Incremental Output Format. Update `.extract_log.json` with a single-line JSON entry (`{"title": "...", "last_extracted": "...", "snapshot_path": "...", "extract_count": 1, "content_hash": "..."}`).

## Output Format
Save to `raw/assets/`. Use `# Knowledge Extract — {Date}`, metadata block (`> Source`, `> Domain`, `> Taxonomy categories`), followed by `## Topic`, `### Key Concepts Covered`, `### Full Content`, `### Open Questions`, and `### Sources`.

### Email Data Format (Strict Knowledge Synthesis)
When extracting from email JSON (e.g., `outlook_emails.json`), do NOT use the standard output format. Instead, output the precise email as a markdown file structured for Obsidian Dataview, and save it to `raw/assets/emails/`:
1. Include a YAML frontmatter block containing:
   - `type: email`
   - `sender: "[Sender Name or Email]"`
   - `date: "[Date from scraped_at or email text]"`
   - `folder: "[Original Folder]"`
   - `topics: [list of topics]`
   - `sentiment: "[positive/negative/neutral]"`
2. Follow the YAML block with `# [Subject or Preview snippet]` and the verbatim `full_body` text of the email. Do NOT summarize or condense email body text.

## Hard Rules
- **Taxonomy**: Cross-reference [taxonomy.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/taxonomy.md) to use canonical tags.
- **Safety**: Follow [02_operations.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/02_operations.md) for data immutability.
- **No Hallucinations/Pre-training**: Extract only what is in the source.
- **Incremental**: Overwrite snapshots in `raw/imports/`, but NEVER delete them.
