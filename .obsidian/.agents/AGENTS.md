# LLM Wiki Project Rules (Router)
*Note: Detailed rules are modularized. Add/edit rules only in `.agents/rules/`; do not add them here.*

## Core Rule Modules
- [**01. Wiki Architecture & Schema**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/01_architecture.md): Folder structures, YAML requirements, domains.
- [**02. Operations & Safety**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/02_operations.md): Core commands (`/ingest`, `/lint`, `/all`) & immutability.
- [**03. Routing Algorithm**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/03_routing.md): Q1-Q4 logic for tag-based folder auto-creation.
- [**04. Data Hygiene & Deduplication**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/04_data_hygiene.md): Normalization, duplicate prevention, MOC cascade cleanup.

## Skills (Actions)
- [**extract**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract/SKILL.md)
- [**extract_all**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract_all/SKILL.md): Proactive Knowledge Hunter (Harvests past chats & fills wiki coverage gaps).
- [**ingest**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/ingest/SKILL.md)
- [**lint**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/lint/SKILL.md)
- [**all**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/all/SKILL.md)
- [**query**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/query/SKILL.md)
- [**scrape_emails**](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/scrape_emails/SKILL.md)
