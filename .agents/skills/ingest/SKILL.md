---
name: ingest
description: Compiles raw sources into structured, interlinked markdown wiki pages with domain routing and MOC updates.
---

# Wiki Ingestor

Read unprocessed files from `LLM_Wiki_Project/raw/` and integrate them into `LLM_Wiki_Project/wiki/`.

## Ingest Pipeline (7 Steps)

1. **Source Analysis (Adaptive Dispatch)**: Inspect unprocessed raw files from `raw/assets/` and determine batch allocations:
   - **Large Files (≥15 KB or ≥200 lines)**: Dispatch 1 dedicated subagent per file (1:1 mapping) for deep synthesis.
   - **Small Files (<15 KB and <200 lines)**: Bundle up to 10 files (max 50 KB total per bundle) per subagent (1:N mapping).
   - **Concurrency Guard**: Strictly limit concurrent subagent invocations to a maximum of 15 per batch to prevent `429 RESOURCE_EXHAUSTED` errors. Wait for the batch to complete before launching the next. Handle `_incremental.md` files by merging/updating instead of full recreation.
2. **Type Classification**: Classify items based on [schema.yaml](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/schema.yaml) (e.g., concept, entity, person).
   - **Email Synthesis Rule**: When reading raw emails from `raw/assets/emails/`, do NOT move the email files into the wiki. Instead, synthesize the substantive knowledge within them (e.g., people, tools, concepts, projects) and create new, dedicated wiki notes for those specific entities. **FILTERING**: Strictly ignore and skip all promotional, marketing, or spam emails. Only extract knowledge from meaningful human conversations (e.g., discussions with professors/colleagues) or highly important notices.
3. **Domain Routing**: Route strictly according to [01_architecture.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/01_architecture.md) and [03_routing.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/03_routing.md).
4. **Page Creation & Deduplicated Merging**: Adhere to naming and duplicate prevention rules in [04_data_hygiene.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/04_data_hygiene.md). Check local `_moc.md` before creating. When merging into existing notes, strip the incoming file's frontmatter, deduplicate repeated paragraphs, and NEVER inject a secondary YAML block into the body. Skip if < 2 substantive sentences. Ensure `aliases` field exists for entities/people.
5. **Frontmatter & Tagging**: Apply valid YAML from [schema.yaml](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/schema.yaml). Select tags exclusively from [taxonomy.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/LLM_Wiki_Project/taxonomy.md) (lowercase, hyphen-separated).
6. **Cross-linking & Sources**: Aggressively link valid wiki concepts using `[[Page_Name]]`. Include a `## Sources` section at the bottom citing source filenames as PLAIN TEXT (`- original_filename.md`). NEVER enclose raw filenames or `.md` extensions in `[[wikilinks]]` (prevents ghost nodes).
7. **MOC Update**: Add wikilinks to relevant `_moc.md` files (cluster by Type in Domain MOCs, alphabetical in Subfolder MOCs).

## Finalization
- Move ingested raw files to `LLM_Wiki_Project/raw/processed/`. Do not rename with `_processed` in-place; cleanly relocate them to the archive folder to keep the active queue empty. **CRITICAL**: After moving, update the `snapshot_path` field in `LLM_Wiki_Project/raw/imports/.extract_log.json` to reflect the new path. This prevents the incremental extraction system from breaking.
- Update `wiki/index.md` if needed.
- Log actions to `wiki/log.md`.

## Hard Rules
- **No Hallucinations**: Write ONLY facts supported by `raw/` documents.
- **Never Delete Knowledge**: Merge safely.
- **Respect Rules**: Follow [AGENTS.md](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/AGENTS.md) and its sub-rules meticulously.
