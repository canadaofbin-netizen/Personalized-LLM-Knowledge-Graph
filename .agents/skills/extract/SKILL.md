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
   - Finally, run the Google Drive Proactive Scan (Mode 4) automatically.
2. **`/extract [file/URL]`**: Single file (Drive MCP or local). Check `.extract_log.json` for diffs.
3. **`/extract [folder]`**: Specifically target a folder to scan for unprocessed files. Use Map-Reduce Subagents for parallel extraction.
4. **`/extract drive`** (or auto-triggered by Mode 1): **Google Drive Proactive Scanner**.
   - **Purpose**: Proactively discover user-authored documents (Google Docs, Sheets, PDFs) across the entire Google Drive that contain actionable knowledge about ongoing projects, research, or personal activities.
   - **Pipeline**:
     1. **Folder Scan**: Use Drive MCP `listFolder` to recursively list top-level and key workspace folders. Record folder names, file names, types, and modification dates.
     2. **Relevance Filter**: AI evaluates each file name and folder context to determine relevance. **INCLUDE**: User-authored documents clearly related to ongoing projects, research designs, study overviews, meeting notes, personal plans, and collaboration materials. **EXCLUDE**: Raw academic papers/PDFs not authored by the user, third-party course materials, system/config files, and media files (images, videos).
     3. **Content Extraction**: For files that pass the relevance filter, use Drive MCP `downloadFile` (export Google Docs as `text/plain`, Sheets as `text/csv`) to read their contents. Extract substantive knowledge into markdown files in `raw/assets/`.
     4. **Incremental**: Track scanned files in `LLM_Wiki_Project/raw/imports/.drive_scan_log.json` (`{"fileId": "...", "name": "...", "last_scanned": "...", "content_hash": "..."}`). Skip unchanged files on subsequent runs.
   - **Judgment Heuristic (What to Extract)**:
     - Documents the user personally created or edited (e.g., study designs, survey instruments, project overviews, collaboration notes).
     - Files related to known wiki projects (cross-reference `wiki/projects/_moc.md` for project names).
     - Recently modified files (within the last 30 days) in work-related folders.
   - **What NOT to Extract**: Published papers, textbooks, downloaded course slides, or any document the user did not author. The goal is to capture the user's **actions and artifacts**, not external reference material.

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
When extracting from email JSON (e.g., `outlook_emails.json`), do NOT use the standard output format. Instead, run the official Python script:
`python LLM_Wiki_Project/scripts/extract_emails.py`
This script automatically parses the JSON and generates valid markdown files with all required schema fields (`title`, `description`, `tags: [email-contact]`, `timestamp`, `sources`, etc.) in `raw/assets/emails/`. Do NOT summarize or condense email body text manually.

## Hard Rules
- **Taxonomy**: Cross-reference [taxonomy.md](../../../LLM_Wiki_Project/taxonomy.md) to use canonical tags.
- **Safety**: Follow [02_operations.md](../../rules/02_operations.md) for data immutability.
- **No Hallucinations/Pre-training**: Extract only what is in the source.
- **Incremental**: Overwrite snapshots in `raw/imports/`, but NEVER delete them.
