# LLM Wiki Project Rules (Router)
*Note: Detailed rules are modularized. Add/edit rules only in `.agents/rules/`; do not add them here.*

## Agent Customizations Index

### Rules (`.agents/rules/`)
- [Rule: 01. Wiki Architecture & Schema](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/01_architecture.md) - Folder structures, YAML requirements, domains, and English-only policy.
- [Rule: 02. Operations & Safety](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/02_operations.md) - Core commands (`/ingest`, `/lint`, `/all`), GitHub sync, and adaptive chunk bundling.
- [Rule: 03. Routing Algorithm](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/03_routing.md) - Q1-Q4 logic for tag-based folder auto-creation and type overrides.
- [Rule: 04. Data Hygiene & Deduplication](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/rules/04_data_hygiene.md) - File naming standards, Unicode normalization, duplicate prevention, and cascade cleanup.

### Skills (`.agents/skills/`)
- [Skill: extract](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract/SKILL.md) - Extracts knowledge from conversations, Drive files, or Gemini exports.
- [Skill: extract_all](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/extract_all/SKILL.md) - Proactive Knowledge Hunter (Harvests past chats & fills wiki coverage gaps).
- [Skill: ingest](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/ingest/SKILL.md) - Compiles raw sources into structured, interlinked markdown wiki pages with domain routing and MOC updates.
- [Skill: lint](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/lint/SKILL.md) - Runs comprehensive Two-Phase health checks (Syntactic + Semantic) on the LLM Wiki.
- [Skill: all](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/all/SKILL.md) - End-to-end knowledge pipeline running Scrape → Extract → Ingest → MOC → Lint.
- [Skill: query](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/query/SKILL.md) - Retrieves and synthesizes information exclusively from the local wiki.
- [Skill: scrape_emails](file:///g:/My%20Drive/Kyubin_Yun_Workspace/06_Obsidian_System/01_Obsidian_Vault/03_General/.agents/skills/scrape_emails/SKILL.md) - Scrapes emails from Outlook OWA and outputs raw JSON for ingestion.
