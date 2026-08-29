---
name: ingest
description: Compiles raw sources into structured, interlinked markdown wiki pages with domain routing and MOC updates.
---

# Wiki Ingestor

Read unprocessed files from `LLM_Wiki_Project/raw/` and integrate them into `LLM_Wiki_Project/wiki/`.

## Ingest Pipeline (7 Steps)

1. **Source Analysis**: Read files. **CRITICAL**: Use Map-Reduce Subagents for batch ingestion (one subagent per file). Handle `_incremental.md` files by merging/updating instead of full recreation.
2. **Type Classification**: Classify items based on [schema.yaml](../../../LLM_Wiki_Project/schema.yaml) (e.g., concept, entity, person).
   - **Email Synthesis Rule**: When reading raw emails from `raw/assets/emails/`, do NOT move the email files into the wiki. Instead, synthesize the substantive knowledge within them (e.g., people, tools, concepts, projects) and create new, dedicated wiki notes for those specific entities. **FILTERING**: Strictly ignore and skip all promotional, marketing, or spam emails. Only extract knowledge from meaningful human conversations (e.g., discussions with professors/colleagues) or highly important notices.
3. **Domain Routing**: Route strictly according to [01_architecture.md](../../rules/01_architecture.md) and [03_routing.md](../../rules/03_routing.md).
4. **Page Creation & Deduplication**: Adhere to naming and duplicate prevention rules in [04_data_hygiene.md](../../rules/04_data_hygiene.md). Check local `_moc.md` before creating. Merge if exists. Skip if < 2 substantive sentences. Ensure `aliases` field exists for entities/people.
5. **Frontmatter & Tagging**: Apply valid YAML from [schema.yaml](../../../LLM_Wiki_Project/schema.yaml). Select tags exclusively from [taxonomy.md](../../../LLM_Wiki_Project/taxonomy.md) (lowercase, hyphen-separated).
6. **Cross-linking**: Aggressively link `[[Page_Name]]`. Include a `## Sources` section at the bottom linking to `[[original_filename_processed.md]]`. (e.g., if the raw file is `email_123.md`, write `[[email_123_processed.md]]` because it will be renamed at the end of the pipeline).
7. **MOC Update**: Add wikilinks to relevant `_moc.md` files (cluster by Type in Domain MOCs, alphabetical in Subfolder MOCs).

## Finalization
- Rename ingested raw files (append `_processed`). **CRITICAL**: After renaming, update the `snapshot_path` field in `LLM_Wiki_Project/raw/imports/.extract_log.json` to reflect the new filename. This prevents the incremental extraction system from breaking.
- Update `wiki/index.md` if needed.
- Log actions to `wiki/log.md`.

## Hard Rules
- **No Hallucinations**: Write ONLY facts supported by `raw/` documents.
- **Never Delete Knowledge**: Merge safely.
- **Respect Rules**: Follow [AGENTS.md](../../AGENTS.md) and its sub-rules meticulously.
