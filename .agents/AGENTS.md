# LLM Wiki Project Rules (Router)
*Note: Detailed rules are modularized. Add/edit rules only in `.agents/rules/`; do not add them here.*

## Core Rule Modules
- [**01. Wiki Architecture & Schema**](rules/01_architecture.md): Folder structures, YAML requirements, domains.
- [**02. Operations & Safety**](rules/02_operations.md): Core commands (`/ingest`, `/lint`, `/all`) & immutability.
- [**03. Routing Algorithm**](rules/03_routing.md): Q1-Q4 logic for tag-based folder auto-creation.
- [**04. Data Hygiene & Deduplication**](rules/04_data_hygiene.md): Normalization, duplicate prevention, MOC cascade cleanup.

## Skills (Actions)
- [**extract**](skills/extract/SKILL.md)
- [**extract_all**](skills/extract_all/SKILL.md): Proactive Knowledge Hunter (Harvests past chats & fills wiki coverage gaps).
- [**ingest**](skills/ingest/SKILL.md)
- [**lint**](skills/lint/SKILL.md)
- [**all**](skills/all/SKILL.md)
- [**query**](skills/query/SKILL.md)
- [**scrape_emails**](skills/scrape_emails/SKILL.md)
