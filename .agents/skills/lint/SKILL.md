---
name: lint
description: Triggers when the user uses `/lint`. Runs a comprehensive Two-Phase health check (Syntactic + Semantic) on the LLM Wiki.
---

# Wiki Linter

`/lint` executes a comprehensive Two-Phase (Syntactic + AI Semantic) sweep.

## Phase 1: Syntactic Audit (22 Deterministic Checks)
Run `python "LLM_Wiki_Project/scripts/run_linter.py"`. Read the generated `LLM_Wiki_Project/reports/lint_report.md`.

### Structural Checks (13 Total — Must be 0 for 🟢 Green Status)
1. **Schema Integrity**: Validates presence of all mandatory frontmatter fields defined in [schema.yaml](file:///LLM_Wiki_Project/schema.yaml).
2. **Type Validation**: Verifies that the note `type` belongs exclusively to canonical schema types.
3. **Domain Placement**: Verifies that directory location matches the YAML `domain` field.
4. **MOC Sync (Check 6)**: Verifies that every markdown page is linked in its local `_moc.md`.
5. **Duplicate Detection - Filename (Check 8)**: Catches normalized filename collisions across the vault.
6. **Naming Convention (Check 9)**: Enforces `Underscore_Separated_Title_Case` and forbids spaces or illegal characters `()[]{}#%&*|\/:"<>?—.`.
7. **Tag→Folder Consistency (Check 10)**: Verifies that tags map deterministically to designated subfolders.
8. **Tag Normalization (Check 11)**: Enforces lowercase, hyphen-separated tags with no spaces or uppercase characters.
9. **Semantic Duplicate - Title/Alias (Check 14)**: Catches duplicate concept definitions across titles and YAML `aliases`.
10. **Junk/Phantom Files (Check 16)**: Detects temporary or scraper debris (e.g., `item1.md`, `Untitled.md`, `Empty_Document_*.md`).
11. **Broken Outgoing Links (Check 19)**: Verifies all `[[wikilinks]]` resolve to existing wiki notes or aliases; strictly forbids `.md` extensions in wikilinks to eradicate Obsidian ghost nodes.
12. **Multi-YAML Frontmatter Guard (Check 20)**: Enforces exactly ONE YAML block at lines 1–N; flags embedded secondary YAML headers in markdown bodies.
13. **Canonical Root Domain Whitelist (Check 22)**: Restricts root folders under `wiki/` strictly to the 8 canonical domains (`academic/`, `business/`, `career/`, `dev/`, `people/`, `personal/`, `projects/`, `tools/`).

### Advisory Checks (9 Total — Content Quality & Maintenance Warnings)
1. **Staleness (Check 4)**: Flags notes with no updates in >90 days.
2. **Coverage Gaps (Check 5)**: Identifies shallow notes (<50 words) and non-English text violating Rule 01.3.
3. **Orphan Check (Check 7)**: Identifies notes with zero incoming internal links.
4. **Taxonomy Alignment (Check 12)**: Identifies tags not registered in [taxonomy.md](file:///LLM_Wiki_Project/taxonomy.md).
5. **_uncategorized Overflow (Check 13)**: Alerts when an `_uncategorized/` folder accumulates 3+ files sharing a common tag.
6. **Merge Debris (Check 15)**: Detects uncleaned merge headers (e.g., `## Merged from`, `## Additional Sources`).
7. **Cross-link Poverty (Check 17)**: Flags isolated notes lacking outgoing wikilinks.
8. **Content Similarity - TF-IDF (Check 18)**: Detects near-duplicate documents with \(\ge 88\%\) lexical cosine similarity.
9. **Repetitive Paragraphs (Check 21)**: Detects copy-paste bloat where paragraphs (\(\ge 15\) words) are duplicated within the same file.

## Phase 2: AI Semantic Sweep (Map-Reduce)
Spawn a `pro` subagent per subfolder with markdown files. **Concurrency Limit**: Batch subagent invocations to a maximum of 15 at a time to prevent `429 RESOURCE_EXHAUSTED` errors.
- **Role**: Domain Semantic Auditor
- **Prompt**: "Read all `.md` files in `{subfolder}`. Find hidden semantic duplicates that evade Python string-matching. Verify if tags match [taxonomy.md](file:///LLM_Wiki_Project/taxonomy.md). Return: [Duplicate Pair] - [Reason] - [Recommendation]."
Collect all subagent results.

## Output Artifact
Create `lint_audit.md` artifact containing:
- **Summary**: P1 (Green/Yellow/Red), P2 (Pass/Fail counts)
- **Phase 1 Issues**: From python report.
- **Phase 2 Issues**: True semantic duplicates and tag issues.
- **Next Steps**: Numbered repair list. Ask for user permission.

## Hard Rules
- Never delete files unilaterally. See [02_operations.md](file:///.agents/rules/02_operations.md).
- Follow architectural rules in [01_architecture.md](file:///.agents/rules/01_architecture.md).
