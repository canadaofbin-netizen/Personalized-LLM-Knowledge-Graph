# Knowledge Taxonomy

All tags during ingestion MUST be selected from this list.
If a new tag is needed, append it under the most appropriate parent category.
If no parent category fits, create a new top-level domain.

Domains correspond 1:1 with wiki/ folder structure.
When a new domain is added here, a matching wiki/{domain}/ folder and _moc.md must also be created.

Tags MUST be lowercase, hyphen-separated. No uppercase, no slashes, no domain prefixes.

---

## academic
- research, statistics, psychology, neuroscience, linguistics, philosophy, mathematics, physics, biology, chemistry, economics, sociology, history, literature

*(Note: As you ingest files with new tags, add them here. If a tag gathers 3+ files in `_uncategorized`, auto-create its subfolder and update this mapping.)*

## business
- strategy, marketing, finance, management

## dev
- programming, frameworks, architecture

## projects
- internships, coursework, research-projects, personal-projects

## people
- (Use role or affiliation tags as needed, e.g., professor, researcher, ceo)
- professor, researcher, student

## tools
- (Use software category tags as needed, e.g., ide, database, design)
- ide, database, browser

## languages
- (Use specific language tags as needed, e.g., english, python)
- english, korean, python, javascript

## personal
- goals, reflections, administration

## wiki
- wiki-management, index, log, moc

---

## broad-categories
(Used as fallback tags to satisfy linter Check 12 if a file only has highly specific tags but no recognized domain/subdomain tag)
- academic
- business
- dev
- projects
- people
- tools
- languages
- personal
- wiki
