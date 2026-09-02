---
name: Wiki Operations and Safety Rules
description: Rules for commands, syncing, and data safety
trigger: always_on
---
# 02. Operations and Safety

1. **Operations (Commands)**: Wiki operations map to skills in `.agents/skills/`:
   - [**/ingest**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/ingest/SKILL.md): **CRITICAL**: Use Map-Reduce Subagents for batch ingestion. Adaptive dispatch: Large files (≥15KB or ≥200 lines) receive 1 dedicated subagent (1:1); Small files (<15KB) are bundled up to 10 files (max 50KB total) per subagent (1:N). Concurrency strictly capped at 15 subagents.
   - [**/query**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/query/SKILL.md): Strictly queries the Knowledge Base.
   - [**/lint**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/lint/SKILL.md): Runs comprehensive Two-Phase checks (22 Deterministic checks: 13 Structural + 9 Advisory, followed by Map-Reduce AI Semantic sweep).
   - [**/extract**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract/SKILL.md): Args: `none`=live chat, `file/URL`=Drive file, `folder path`=scan/extract all.
   - [**/all**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/all/SKILL.md): End-to-end pipeline (Extract → Ingest → MOC → Lint).
   
2. **Sync & External Integrations**:
   - Sync via GitHub repository: `https://github.com/canadaofbin-netizen/LLM-WIKI---personalized`. (Previously Google Drive).


3. **Data Safety**:
   - Assume source data is immutable (default to copy/merge). **Never** execute destructive commands (`rm`, `del`) without explicit, unambiguous user permission.
