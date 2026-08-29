---
name: Wiki Operations and Safety Rules
description: Rules for commands, syncing, and data safety
trigger: always_on
---
# 02. Operations and Safety

1. **Operations (Commands)**: Wiki operations map to skills in `.agents/skills/`:
   - [**/ingest**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/ingest/SKILL.md): **CRITICAL**: Use Map-Reduce Subagents for batch ingestion. Dispatch one subagent per file for extraction/synthesis; avoid sequential processing.
   - [**/query**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/query/SKILL.md): Strictly queries the Knowledge Base.
   - [**/lint**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/lint/SKILL.md): Runs comprehensive Two-Phase checks.
   - [**/extract**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract/SKILL.md): Args: `none`=live chat, `file/URL`=Drive file, `folder path`=scan/extract all.
   - [**/all**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/all/SKILL.md): End-to-end pipeline (Extract → Ingest → MOC → Lint).
   
2. **Sync & External Integrations**:
   - Sync via Google Drive (No Git).

3. **Data Safety**:
   - Assume source data is immutable (default to copy/merge). **Never** execute destructive commands (`rm`, `del`) without explicit, unambiguous user permission.
