# LLM Wiki Project

A Personal Knowledge Base system managed by an AI Agent (Antigravity).
It automatically extracts knowledge from various sources such as conversations, Google Drive documents, and PDFs, and integrates it into a structured markdown wiki for viewing in Obsidian.

---

## Folder Structure

```
LLM_Wiki_Project/
│
├── raw/                          # Raw sources (Immutable)
│   ├── assets/                   # Output from /extract (Extracted knowledge markdown)
│   └── imports/                  # Drive file snapshots + .extract_log.json
│
├── wiki/                         # Official Wiki (Managed by LLM)
│   ├── index.md                  # Catalog & Entry point
│   ├── log.md                    # Operation logs (Auto-filled)
│   ├── overview.md               # High-level synthesis
│   ├── academic/                 # Research, papers, lectures, theories
│   │   ├── _uncategorized/       # Uncategorized (Auto-promoted to subfolder at 3+ files)
│   │   └── *(Subfolders are auto-created by taxonomy.md)*
│   ├── business/                 # Strategy, marketing, finance, management
│   ├── dev/                      # Programming, frameworks, architecture
│   ├── projects/                 # Projects, internships, coursework
│   ├── people/                   # People profiles
│   ├── tools/                    # Software, tools
│   ├── languages/                # Language learning
│   └── personal/                 # Personal notes, goals, reflections
│
├── templates/                    # Page creation templates (9 types)
│   ├── Concept.md                # Concepts, theories, methodologies
│   ├── Entity.md                 # Organizations, products, institutions
│   ├── Person.md                 # People
│   ├── Tool.md                   # Software, tools
│   ├── Project.md                # Projects
│   ├── Summary.md                # Document summaries
│   ├── Log.md                    # Chronological logs
│   ├── MOC.md                    # Map of Content (Navigation)
│   └── Overview.md               # High-level synthesis
│
├── scripts/                      # Automation scripts
│   ├── reduce.py                 # Ingest Reduce phase (Merge Map results)
│   ├── generate_mocs.py          # Batch MOC generator
│   ├── run_linter.py             # 13-step wiki health check
│   ├── normalize_tags.py         # Tag normalization
│   ├── rename_and_merge.py       # Filename correction and duplicate merge
│   └── migrate_folders.py        # Domain folder migration
│
├── schema.yaml                   # Wiki schema (Required properties and types - SSOT)
└── taxonomy.md                   # Tag taxonomy (Single Source of Truth)
```

---

## Commands

All commands are defined as individual `SKILL.md` files in the `.agents/skills/` folder.

### `/all` — End-to-End Pipeline

Executes the entire knowledge pipeline **fully automatically** with a single command.

```
/all              → Harvest all past chats, research web gaps, and ingest into wiki
```

**Pipeline Flow:**

```
Extract_All ──→ Ingest ──→ MOC ──→ Lint
   (1)           (2)       (3)      (4)
```

| Stage | Role | Output |
|:-----:|:-----|:-----|
| 1. Extract_All | Harvest past chats & actively research gaps | `raw/assets/*.md` |
| 2. Ingest | Convert knowledge into wiki pages | `wiki/**/*.md` |
| 3. MOC | Generate Map of Content per folder | `wiki/**/_moc.md` |
| 4. Lint | 2-Phase (Syntactic+Semantic) health check | Report + Auto-fix |

---

### `/extract_all` — The Proactive Knowledge Hunter

A massive, fully-automated knowledge gathering pipeline that runs before ingestion.

```
/extract_all      → Scans all past Antigravity chats + Researches web for Wiki gaps
```

**Core Features:**
- **Pan-Conversation Harvester**: Iterates through all past `brain/*/transcript.jsonl` files and extracts historical `USER_INPUT` and `PLANNER_RESPONSE` data.
- **Proactive Gap Filler (Map-Reduce)**: Identifies files with <50 words from the lint report, spawns subagents, and actively crawls the Web, Google Drive, and Outlook to synthesize missing information.

---

### `/extract` — Knowledge Extraction

Extracts raw knowledge from external sources and saves it as markdown in `raw/assets/`.

```
/extract              → Extract from current conversation logs (Mode 1)
/extract [file_path]  → Extract from a single file (Mode 2)
/extract [folder_path]→ Batch extract unprocessed files in a folder (Mode 3)
```

**Core Principles:**
- **Extract preserves, Ingest summarizes.** In this stage, capture the raw text exactly without summarizing.
- **Incremental Extraction** via `.extract_log.json`: If a file was already extracted, only extract the changed parts (Diff).
- Uses the **Map-Reduce Subagent** pattern for batch processing.

---

### `/ingest` — Wiki Integration (7 Steps)

Reads extracted files from `raw/assets/` and converts them into structured wiki pages.

| Step | Name | Description |
|:----:|:-----|:-----|
| 1 | Source Analysis | Read raw files, extract concepts/entities/people |
| 2 | Type Classification | Classify into one of 11 types |
| 3 | Domain Routing | 2-level folder routing based on `taxonomy.md` |
| 4 | Page Routing | Duplicate check → Merge or Create new |
| 5 | Frontmatter & Tagging | YAML Frontmatter + Tag assignment |
| 6 | Cross-linking | Connect related pages with `[[wikilinks]]` |
| 7 | MOC Update | Update `_moc.md` indexes |

**Batch Processing Architecture (Map-Reduce):**

```
┌─ Mapper 1 ─→ Temp Draft ─┐
├─ Mapper 2 ─→ Temp Draft ─┤
├─ Mapper 3 ─→ Temp Draft ─┼──→ Reducer ──→ wiki/
├─ ...                     │    (Merge)     (Official Ingest)
└─ Mapper N ─→ Temp Draft ─┘
```

- **Map**: N subagents analyze files in parallel and create drafts in a temp folder.
- **Reduce**: Main agent uses `scripts/reduce.py` to collect drafts, merge duplicates, and officially ingest them into `wiki/`.
- **MOC Generation**: After Reduce completes, `scripts/generate_mocs.py` is executed to batch generate `_moc.md` for all folders.

---

### `/lint` — Two-Phase Wiki Health Check

Ensures a flawless wiki state by performing both powerful syntactic checks via Python and semantic checks via AI.

**Phase 1: Syntactic Audit (Python)**
Runs `scripts/run_linter.py` to perform an **18-step structural check**.
- Schema integrity, Type/Domain matching, Folder depth limit (max 2 levels)
- Strict duplicate detection and filename validation (including period `.` circumvention)
- Prevents structural overflow from Q4 routing
- Detects non-English characters (Enforces Rule 01.3)

**Phase 2: Semantic Audit (AI Subagents)**
The main agent invokes subagents to read the context of documents and verify Type accuracy, detect semantic duplicates, and validate Aliases 100% according to rules `01~04.md`.

---

### `/query` — Wiki Search

Answers questions using **only** the knowledge inside the `wiki/` folder.

```
/query What is Reinforcement Learning?
/query [domain:academic] [tag:eeg] BCI concepts summary
```

---

### `/ask` — General Conversation

A free-form Q&A mode completely unrelated to the wiki.

---

## Core Rules

### File Naming
- **Underscore_Title_Case**: `Between_Subjects_Design.md`
- Hyphens allowed in compound words: `Brain-Computer_Interface.md`
- Forbidden characters (including periods): `( ) [ ] { } # % & * | \ / : " < > ? — .`

### Tags
- Lowercase, hyphen-separated: `brain-computer-interface`, `forced-choice`
- MUST be selected from `taxonomy.md` (Add new tags to taxonomy before using)
- Do NOT use type values (`concept`, `source`, etc.) as tags

### YAML Frontmatter (Required)
```yaml
---
type: concept          # One of 11 valid types
title: "Page Title"
description: "Description"
tags: [tag-a, tag-b]
timestamp: 2026-08-11
sources: [raw/assets/source.md]
---
```

### Folder Depth
- **Maximum 2 Levels**: `academic/statistics/` (O)
- 3+ levels must be managed by tags: `academic/statistics/inferential/` (X)

### Data Safety
- Raw data (`raw/`) is **immutable**.
- Do NOT delete/move files without explicit user permission.

---

## Incremental Extraction System (.extract_log.json)

A log-based system to prevent duplicate work when repeatedly extracting from external sources like Google Drive.

```
1. Check Document ID → Look up record in .extract_log.json
2. No record → Full Extract + Save snapshot
3. Record exists → Compare snapshot with current content (Diff)
   3a. Identical → Skip (update last_checked timestamp only)
   3b. Modified → Extract ONLY the changed parts (Incremental Extract)
```

---

## MOC (Map of Content)

Each folder's `_moc.md` serves as its **Navigation Hub**.

- Lists all wiki pages in the folder grouped by type (Concept, Entity, Tool, etc.)
- Includes links to subfolders
- Batch generated/updated via `scripts/generate_mocs.py`
- Runs automatically after Ingest Reduce completes (executed sequentially to prevent conflicts)

---

## External Integrations

### Google Drive MCP
- `listFolder`: Traverse folders
- `getGoogleDocContent`: Read Google Docs content
- `getGoogleSheetContent`: Read Google Sheets content
- `getGoogleSlidesContent`: Read Google Slides content
