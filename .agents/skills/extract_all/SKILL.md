---
name: extract_all
description: End-to-end Proactive Knowledge Hunter. Harvests all past conversations and actively researches missing information to fill wiki coverage gaps.
---

# `/extract_all` — The Proactive Knowledge Hunter

This skill orchestrates a massive extraction and proactive research pipeline to gather maximum knowledge before handing off to `/ingest`.

## Stage 1: Pan-Conversation Harvester (Local Extract)
Extracts knowledge from ALL historical Antigravity conversations.
**Command**: `python "LLM_Wiki_Project/scripts/extract_all_chats.py"`
- **Behavior**: Scans `~/.gemini/antigravity/brain/*/` (or configured platform log directory) for `transcript.jsonl` files.
- **Filtering**: Captures `USER_INPUT` and `PLANNER_RESPONSE` (skips raw tool outputs to save tokens).
- **Incremental**: Uses `LLM_Wiki_Project/raw/imports/.extract_all_log.json` to skip previously processed transcripts.
- **Output**: Dumps chunked markdown files (e.g., `archive_chat_chunk_X.md`) into `raw/assets/`.

## Stage 1.5: Google Drive Proactive Scanner
Proactively discovers and extracts knowledge from user-authored documents across the entire Google Drive.
- **Pipeline**:
  1. **Folder Scan**: Use Drive MCP `listFolder` to recursively list top-level and key workspace folders. Record folder names, file names, types (`application/vnd.google-apps.document`, `application/pdf`, etc.), and modification dates.
  2. **Relevance Filter**: AI evaluates each file name and folder context against known wiki projects (cross-reference `wiki/projects/_moc.md`). **INCLUDE**: User-authored docs related to ongoing projects, research designs, study overviews, survey instruments, meeting notes, collaboration materials, and personal plans. **EXCLUDE**: Published papers, textbooks, downloaded course slides, media files, and any document the user did not author. The goal is to capture the user's **actions and artifacts**, not external reference material.
  3. **Content Extraction**: For relevant files, use Drive MCP `downloadFile` (export Google Docs as `text/plain`, Sheets as `text/csv`) to read contents. Extract substantive knowledge into markdown files in `raw/assets/`.
  4. **Incremental**: Track scanned files in `LLM_Wiki_Project/raw/imports/.drive_scan_log.json` (`{"fileId": "...", "name": "...", "last_scanned": "...", "content_hash": "..."}`). Skip unchanged files on subsequent runs.
- **Spawn Strategy**: Use Map-Reduce subagents — one subagent per top-level Drive folder to parallelize scanning.

## Stage 2: Proactive Gap Filler (Map-Reduce Research)
After harvesting local chats, the agent proactively hunts for missing information on the web.
1. **Identify Gaps**: Read `LLM_Wiki_Project/reports/lint_report.md` (specifically the "Coverage Gaps" section).
2. **Spawn Hunters**: For each entity < 50 words (e.g., a Company or Person), spawn a `pro` subagent.
   - **Role**: Proactive Research Hunter
   - **Prompt**: "Research [Entity Name] using the `search_web` tool. If it's a person, find their affiliation and research focus. If it's a company, find their 2027 internship roles and tech stack. Synthesize into a markdown file and save it to `./LLM_Wiki_Project/raw/assets/web_extract_[Entity].md`."

## Stage 3: Auto-Ingest Handoff
Once Stage 1 and Stage 2 are complete and all new knowledge files are in `raw/assets/`:
- Inform the user of the number of files generated.
- Suggest running `/all` or `/ingest` to seamlessly merge the massive influx of data into the Obsidian graph.

## Hard Rules
- **Taxonomy**: Cross-reference `taxonomy.md` to use canonical tags.
- **Safety**: Do not delete any existing wiki files during extraction. Follow operations rules.
