---
name: query
description: Retrieves and synthesizes information exclusively from the local wiki to answer user questions, with optional domain/subdomain/type/tag filtering.
---

# Wiki Query

Search `LLM_Wiki_Project/wiki/` to answer questions based **only** on the compiled markdown pages.

## Query Syntax & Filters
- `/query {question}`: Search all pages.
- `/query [domain] {question}`: Restrict to `wiki/{domain}/`
- `/query [domain/subdomain] {question}`: Restrict to `wiki/{domain}/{subdomain}/`
- `/query [type:X] {question}`: Filter by frontmatter `type` (see [schema.yaml](../../../LLM_Wiki_Project/schema.yaml)).
- `/query [tag:X] {question}`: Filter by frontmatter `tags` (see [taxonomy.md](../../../LLM_Wiki_Project/taxonomy.md)).

## Query Pipeline
1. **Information Retrieval**: Parse filters. Check relevant `_moc.md` files first, then read candidate pages.
2. **Synthesis**: Synthesize knowledge across multiple pages.
3. **Citations & Linking**: Every factual claim MUST be backed by an inline citation using `[[Page_Name]]`.

## Hard Rules
- **Wiki First**: Do NOT use pre-trained knowledge. If not found, explicitly state "There is no relevant information in the wiki." and suggest `/ingest`.
- **Respect Filters**: Do NOT search outside the specified scope.
- **Reference**: Follow [01_architecture.md](../../rules/01_architecture.md).
