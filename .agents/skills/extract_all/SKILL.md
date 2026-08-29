---
name: extract_all
description: End-to-end Proactive Knowledge Hunter. Harvests all past conversations and actively researches missing information to fill wiki coverage gaps.
---

# `/extract_all` — The Proactive Knowledge Hunter

This skill orchestrates a massive extraction and proactive research pipeline to gather maximum knowledge before handing off to `/ingest`.

## Stage 1: Pan-Conversation Harvester
Extracts knowledge from ALL historical Antigravity conversations.
**Command**: `python "LLM_Wiki_Project/scripts/extract_all_chats.py"`
- **Behavior**: Scans `C:/Users/yunky/.gemini/antigravity/brain/*/` for `transcript.jsonl` files.
- **Filtering**: Captures `USER_INPUT` and `PLANNER_RESPONSE` (skips raw tool outputs to save tokens).
- **Incremental**: Uses `LLM_Wiki_Project/raw/imports/.extract_all_log.json` to skip previously processed transcripts.
- **Output**: Dumps chunked markdown files (e.g., `archive_chat_chunk_X.md`) into `raw/assets/`.

## Stage 2: Proactive Gap Filler (Map-Reduce Research)
After harvesting local chats, the agent proactively hunts for missing information on the web.
1. **Identify Gaps**: Read `LLM_Wiki_Project/reports/lint_report.md` (specifically the "Coverage Gaps" section).
2. **Spawn Hunters**: For each entity < 50 words (e.g., a Company or Person), spawn a `pro` subagent.
   - **Role**: Proactive Research Hunter
   - **Prompt**: "Research [Entity Name] using the `search_web` tool. If it's a person, find their affiliation and research focus. If it's a company, find their 2027 internship roles and tech stack. Synthesize into a markdown file and save it to `g:/My Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/raw/assets/web_extract_[Entity].md`."

## Stage 3: Auto-Ingest Handoff
Once Stage 1 and Stage 2 are complete and all new knowledge files are in `raw/assets/`:
- Inform the user of the number of files generated.
- Suggest running `/all` or `/ingest` to seamlessly merge the massive influx of data into the Obsidian graph.

## Hard Rules
- **Taxonomy**: Cross-reference `taxonomy.md` to use canonical tags.
- **Safety**: Do not delete any existing wiki files during extraction. Follow operations rules.
