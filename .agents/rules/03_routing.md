---
name: Wiki Routing Decision Tree
description: Subfolder routing decision algorithm for placing new files
trigger: always_on
---
# 03. Routing Algorithm (for `/ingest`)

## Priority 0: Type Override
If the file's `type` field has a canonical domain mapping, route there **before** evaluating tags:
- `person` → `wiki/people/`
- `tool` → `wiki/tools/`
- `project` → `wiki/projects/`
- `log` → `wiki/{domain}/` (use the `domain` field)
- `email` → `wiki/{domain}/` (use the `domain` field)
- `moc` → `wiki/{domain}/` (use the `domain` field)

For ambiguous types (`concept`, `entity`, `summary`, `overview`, `reading_note`, `collection`, `lecture_note`), proceed to tag-based evaluation below.

## Tag-Based Routing (Steps 1–4)
Evaluate sequentially for new files against [taxonomy.md](../../LLM_Wiki_Project/taxonomy.md):
1. **Exact Match**: Tag matches a Tag→Folder entry in `taxonomy.md` → Route to folder.
2. **Parent Match**: Tag's parent in `taxonomy.md` maps to existing subfolder → Route.
3. **Shared Parents**: Tag shares 2+ parent tags with existing subfolder → Route.
4. **Auto-Create / Fallback**: If `_uncategorized/` reaches 3+ files with the same tag AND tag maps to a broad Level-2 category:
   - **Depth Guard**: Before creating `wiki/{domain}/{new_topic}/`, verify the resulting path depth ≤ 2 levels below `wiki/`. If it would create a 3rd level, route to the parent subfolder instead.
   - Create `wiki/{domain}/{new_topic}/` & local `_moc.md`
   - Append to `taxonomy.md`
   - Move matching files from `_uncategorized/`
   - Log to `wiki/log.md`
   - *Else*: Keep in `_uncategorized/` and log.

**References:**
- [<- Back to AGENTS.md](../AGENTS.md)
- [01_architecture.md](01_architecture.md)
