# Personalized LLM Knowledge Graph & Second Brain System

A fully autonomous, self-healing Personal Knowledge Base and Knowledge Graph engineered for research, software development, career strategy, and personal knowledge management. Powered by **AI Agents**, **Deterministic Python AST Processing Engines**, and **Obsidian Graph View**.

---

> [!NOTE]
> ### 🌐 Multi-Platform Compatibility & Adaptation Notice
> This repository was originally developed and optimized within the **Google Antigravity** environment (.agents/ architecture).
> If you are using **Claude (Claude Code, Claude Projects)**, **Codex / Cursor**, or other AI coding environments, this repository includes universal bridge adapters:
>
> 1. **Claude Code**: Works out of the box via [CLAUDE.md](CLAUDE.md) in the project root.
> 2. **Cursor / Windsurf**: Automatic rule enforcement via [.cursorrules](.cursorrules).
> 3. **Chat Data Extraction (scripts/extract_all_chats.py)**:
>    - Configure your local agent session folder in .env (AGENT_TRANSCRIPT_DIR=...).
>    - Or drop your exported conversations.json (from Claude.ai or ChatGPT data exports) directly into LLM_Wiki_Project/raw/imports/ for automated batch conversion into markdown.
> 4. **Single-Agent Fallback**: In environments without subagent swarm capabilities (invoke_subagent), all ingestion and linter tasks can be run deterministically via the CLI scripts under LLM_Wiki_Project/scripts/.

---

## Table of Contents
1. [System Overview & Architecture Philosophy](#1-system-overview--architecture-philosophy)
2. [Canonical 8 Root Domains Architecture](#2-canonical-8-root-domains-architecture)
3. [End-to-End Pipeline & Data Lifecycle](#3-end-to-end-pipeline--data-lifecycle)
4. [Command Skills Specification (7 Skills)](#4-command-skills-specification-7-skills)
5. [The 22-Check Deterministic Linter Catalog](#5-the-22-check-deterministic-linter-catalog)
6. [Obsidian Graph View & UI Configuration](#6-obsidian-graph-view--ui-configuration)
7. [Directory Tree & System Structure](#7-directory-tree--system-structure)
8. [CLI Execution Guide & Maintenance Workflows](#8-cli-execution-guide--maintenance-workflows)
9. [Quick Start & Customization Guide](#9-quick-start--customization-guide)
10. [License & Attribution](#10-license--attribution)

---

## 1. System Overview & Architecture Philosophy

The **Personalized LLM Knowledge Graph** is a production-grade personal knowledge management (PKM) system that continuously transforms unstructured chats, cloud documents, academic literature, and email communications into a structured, bidirectional knowledge graph.

`
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      PERSONALIZED LLM KNOWLEDGE GRAPH                            │
│                                                                                  │
│   [Raw Sources]            [AI Agent Swarm]              [Knowledge Graph]       │
│  • Agent Chat Logs       • Ingest Mappers (1:N, 1:1)   • 8 Canonical Domains     │
│  • Google Drive Docs     • Knowledge Gap Hunters       • Dynamic Maps of Content │
│  • Outlook Emails        • AST Reducer Engine          • Bidirectional Wikilinks │
│  • Web Crawl History     • 22-Check Python Linter      • Obsidian Visual Graph   │
└──────────────────────────────────────────────────────────────────────────────────┘
`

### Core Engineering Directives
1. **English-Only Standardization (Rule 01.3)**:
   - All knowledge base notes must be written in professional technical English. Raw conversation transcripts in other languages are translated and synthesized into structured technical prose upon ingestion.
2. **Deterministic Routing & Flat Hierarchy (Rule 01.1 & 01.5)**:
   - File placement is determined by canonical type overrides and Level-2 taxonomy categories. Folder nesting is strictly capped at a maximum depth of 2 levels below wiki/ (e.g., wiki/academic/machine-learning/). Creating directories outside the 8 canonical domains or with spaces is strictly prohibited.
3. **Ghost Node Eradication (Rule 04.5)**:
   - Obsidian's Graph View generates unresolved grey "ghost" nodes whenever target files do not exist or when raw source filenames are enclosed in wikilinks. Raw assets (e.g., email_*.md, chat_extract_*.md) must **never** be linked via [[...]]. They are cited as plain text strings in frontmatter sources: lists and body ## Sources sections.
4. **Dual-Layer Hygiene & Prevention Architecture**:
   - **Layer A (AI Prompt Rules)**: Strict behavioral directives in .agents/rules/, CLAUDE.md, and .cursorrules that enforce single frontmatter blocks, entity grounding anchors, and plaintext citations at generation time.
   - **Layer B (Deterministic AST Python Engine)**: educe.py and un_linter.py parse YAML abstract syntax trees, merge set-union properties, and hash paragraphs to eliminate duplicates before committing.

---

## 2. Canonical 8 Root Domains Architecture

The knowledge base is organized into exactly eight canonical root directories under wiki/. Creating unapproved root directories or naming folders with spaces is blocked by the system linter.

| Domain | Scope & Knowledge Focus | Subfolder Structure | Representative Examples |
| :--- | :--- | :--- | :--- |
| **cademic/** | Research papers, scientific theories, mathematics, study modules. | eeg/, machine-learning/, psychology/, 
euroscience/ | Brain_Computer_Interface.md, Deep_Learning_Architectures.md, Cognitive_Psychology.md |
| **usiness/** | Organizational behavior, management strategy, enterprise AI, market dossiers. | strategy/, inance/, case-studies/ | Enterprise_AI_Strategy.md, Organizational_Behavior.md, Market_Analysis.md |
| **career/** | Master resumes/CVs, target companies, interview prep, skill matrices. | *(Top-level flat)* | Master_Resume_Dossier.md, Target_Companies_Dossier.md, Technical_Interview_Preparation.md |
| **dev/** | Software engineering, data pipelines, web scrapers, DevOps & MLOps. | i/, pipelines/, rameworks/ | Data_Pipeline_Architecture.md, Playwright_Web_Scraper.md, API_Design_Patterns.md |
| **people/** | Academic collaborators, mentors, authors, industry leaders (	ype: person). | *(Top-level flat)* | Alan_Turing.md, Claude_Shannon.md, Research_Advisor.md |
| **personal/** | Personal reflections, learning milestones, productivity workflows, administration. | *(Top-level flat)* | Yearly_Goals_And_Reflections.md, Certification_Study_Guide.md |
| **projects/** | Active engineering and academic research initiatives (	ype: project). | coursework/, internships/, personal-projects/, esearch/ | Knowledge_Graph_Pipeline.md, Open_Source_Contribution.md |
| **	ools/** | Software platforms, hardware instruments, developer utilities (	ype: tool). | *(Top-level flat)* | Obsidian_Second_Brain_Architecture.md, Playwright_Browser_Automation.md |

---

## 3. End-to-End Pipeline & Data Lifecycle

`mermaid
flowchart TD
    subgraph S1 [Sources Layer]
        C1[Agent Chat Logs]
        C2[Google Drive Docs / Sheets]
        C3[Outlook OWA Webmail]
        C4[Web Research History]
    end

    subgraph S2 [Extraction Layer]
        E1["/extract_all (Chat Harvester)"]
        E2["/scrape_emails (Playwright Scraper)"]
        E3["/extract (Drive & Chat Diff)"]
    end

    subgraph S3 [Ingestion & Merge Layer]
        M1[Adaptive Map Dispatch]
        M2[1:1 Dedicated Subagent >=15KB]
        M3["1:N Bundled Subagents <15KB"]
        R1["scripts/reduce.py (AST Reducer)"]
    end

    subgraph S4 [Storage & Navigation Layer]
        W1[("wiki/ (8 Canonical Domains)")]
        MC["scripts/generate_mocs.py (MOCs)"]
        AR[("raw/processed/ (Archive)")]
    end

    subgraph S5 [Quality Assurance Layer]
        L1["scripts/run_linter.py (22 Checks)"]
        L2[reports/lint_report.md]
        OB[Obsidian Graph View & Filters]
    end

    C1 & C4 --> E1
    C3 --> E2
    C2 --> E3

    E1 & E2 & E3 -->|Raw Markdown| M1
    M1 --> M2 & M3
    M2 & M3 -->|Draft Markdown| R1

    R1 -->|Single Frontmatter & Paragraph Dedup| W1
    R1 -->|Move Completed Raw| AR
    W1 --> MC
    W1 --> L1
    L1 --> L2
    W1 --> OB
`

### Data Lifecycle Transitions
1. **Raw Ingestion Queue (aw/assets/)**:
   - Newly extracted files (chat_extract_*.md, email_*.md, drive_doc_*.md) land here. Files remain here only while awaiting ingestion.
2. **Knowledge Base (wiki/)**:
   - The permanent repository of structured knowledge. Every page adheres strictly to schema.yaml and contains bidirectional wikilinks to related concepts.
3. **Permanent Archive (aw/processed/)**:
   - Upon successful ingestion and reduction by educe.py, raw source files are cleanly archived into aw/processed/ to guarantee idempotency and prevent duplicate processing.
4. **Incremental Logs (aw/imports/)**:
   - Maintains diff tracking logs: .extract_all_log.json (indexed chat IDs), .drive_scan_log.json (Google Drive file checksums), and .extract_emails_log.json (scraped email message IDs).

---

## 4. Command Skills Specification (7 Skills)

All operations are modularized as standard agent skills in .agents/skills/:

### 1. /extract — Incremental Knowledge Extraction
- **Trigger**: /extract [optional: file_path | folder_path]
- **Purpose**: Extracts structured technical information from live conversation contexts, Google Drive files, or local documents without premature summarization.
- **Output**: Writes immutable markdown source files to aw/assets/.

### 2. /extract_all — Proactive Knowledge Hunter
- **Trigger**: /extract_all
- **Purpose**: Mass-harvests historical conversations across AI sessions and fills knowledge coverage gaps in the wiki.
- **Workflow**:
  1. Scans transcript logs from configured agent directory (or exported conversations.json).
  2. Compares conversation IDs against .extract_all_log.json to process only new sessions.
  3. Inspects eports/lint_report.md for entities flagged as "Too short (<50 words)".
  4. Dispatches web research subagents with the **Entity Grounding Anchor Protocol** ("[Entity Name]" "[Affiliation]" "[Field]") to harvest missing details without identity conflation.

### 3. /scrape_emails — Automated Outlook Scraper
- **Trigger**: /scrape_emails
- **Purpose**: Automates headless Chromium via Playwright (scripts/outlook_scraper/) to scrape emails from Outlook Web Access (OWA).
- **Newsletter Blacklist**: Automatically detects and tags automated system emails (
o-reply@*, notifications, marketing newsletters) as 	ags: [email-newsletter] to prevent spam from contaminating the graph.
- **Output**: Writes aw/imports/outlook_emails.json, converted to markdown in aw/assets/emails/ via scripts/extract_emails.py.

### 4. /ingest — Adaptive Map-Reduce Ingestion Engine
- **Trigger**: /ingest
- **Purpose**: Compiles raw markdown files from aw/assets/ into structured, interlinked wiki pages with taxonomy routing.
- **Adaptive Dispatch Algorithm**:
  - **Large Files (≥15KB or ≥200 lines)**: 1:1 dedicated subagent for deep synthesis.
  - **Small Files (<15KB)**: Bundled up to 10 files per subagent (max 50KB total payload).
  - **Concurrency Safeguard**: Capped at 15 parallel subagents to prevent API rate limits.
- **AST Reducer (scripts/reduce.py)**:
  - Parses YAML frontmatter into a dictionary using pyyaml.
  - Performs set union operations on 	ags, liases, and sources.
  - Strips incoming secondary frontmatter headers to maintain strict 1-block integrity.
  - Compares normalized 15+ word paragraphs across sections to eliminate duplicate text injection.

### 5. /lint — Two-Phase Comprehensive Health Check
- **Trigger**: /lint
- **Phase 1: Deterministic Syntactic Audit**: Executes scripts/run_linter.py across 22 structural and advisory checks.
- **Phase 2: AI Semantic Sweep**: Dispatches subagents to inspect subfolders for semantic duplicates that evade lexical string matching.
- **Output**: Generates eports/lint_report.md with overall health status (🟢 Green, 🟡 Yellow, or 🔴 Red).

### 6. /query — Grounded Local Knowledge Retrieval
- **Trigger**: /query [question] or /query [domain:academic] [tag:ml] [question]
- **Purpose**: Answers technical and research inquiries strictly using verified knowledge contained inside wiki/. Prohibits ungrounded hallucinations.

### 7. /all — End-to-End Autonomous Pipeline
- **Trigger**: /all
- **Purpose**: Executes the complete pipeline in a single automated pass:
  \text{Scrape Emails} \longrightarrow \text{Extract All} \longrightarrow \text{Ingest (Map-Reduce)} \longrightarrow \text{Generate MOCs} \longrightarrow \text{Run Linter}

---

## 5. The 22-Check Deterministic Linter Catalog

The custom Python linter (scripts/run_linter.py) executes 22 rigorous deterministic checks. The wiki must achieve **0 Structural Errors** to be certified as **🟢 Green Status**.

| # | Check Name | Classification | Failure Condition & Enforcement Rule |
| :---: | :--- | :---: | :--- |
| **1** | **Schema Integrity** | **Structural** | Missing any mandatory field (	ype, 	itle, description, 	ags, 	imestamp, sources) from schema.yaml. |
| **2** | **Type Validation** | **Structural** | Note 	ype is not one of the valid types or misses type-specific required fields. |
| **3** | **Domain Placement** | **Structural** | Physical folder path does not match the YAML frontmatter domain: attribute. |
| **4** | **Staleness Check** | **Advisory** | Note has not been updated in over 90 days. |
| **5** | **Coverage Gaps** | **Advisory** | Note body has fewer than 50 words or contains non-English characters. |
| **6** | **MOC Sync** | **Structural** | Note is not indexed in its folder's local _moc.md file. |
| **7** | **Orphan Check** | **Advisory** | Note has zero incoming wikilinks from other pages or MOCs. |
| **8** | **Duplicate Filenames** | **Structural** | Two or more files share identical normalized names (stripped of hyphens, underscores, case). |
| **9** | **Naming Convention** | **Structural** | Filename violates Underscore_Separated_Title_Case or contains spaces or illegal characters ()[]{}#%&*|\/:"<>?—.. |
| **10** | **Tag→Folder Consistency** | **Structural** | Note tags conflict with designated subfolder mapping rules in 	axonomy.md. |
| **11** | **Tag Normalization** | **Structural** | Tag contains uppercase letters, underscores, spaces, or illegal characters (must be lowercase hyphen-separated). |
| **12** | **Taxonomy Alignment** | **Advisory** | Note contains tags not registered in 	axonomy.md. |
| **13** | **_uncategorized Overflow** | **Advisory** | An _uncategorized/ folder accumulates 3 or more files sharing the same tag (triggers auto-folder creation). |
| **14** | **Semantic Title/Alias Dups** | **Structural** | Two distinct files declare identical titles or overlapping YAML liases. |
| **15** | **Merge Debris** | **Advisory** | Note body contains uncleaned merge markers (e.g., ## Merged Content, ## Additional Sources). |
| **16** | **Junk / Phantom Files** | **Structural** | Temporary scraper or editor debris exists (e.g., item1.md, Untitled.md, Empty_Document_*.md). |
| **17** | **Cross-link Poverty** | **Advisory** | Note contains zero outgoing [[wikilinks]] to other concepts in the vault. |
| **18** | **Content Similarity (TF-IDF)** | **Advisory** | Two notes exhibit \(\ge 88\%\) cosine similarity based on word-frequency vectorization. |
| **19** | **Broken Outgoing Links** | **Structural** | Wikilinks target non-existent files/aliases or include .md extensions (root cause of Obsidian ghost nodes). |
| **20** | **Multi-YAML Frontmatter** | **Structural** | Note contains more than one YAML header block (---...---) embedded within the markdown body. |
| **21** | **Repetitive Paragraphs** | **Advisory** | Identical normalized paragraphs of \(\ge 15\) words occur multiple times within the same file. |
| **22** | **Canonical Root Domains** | **Structural** | Root directory under wiki/ does not belong to the 8 canonical domains or contains spaces. |

---

## 6. Obsidian Graph View & UI Configuration

### Exclusion Filters (.obsidian/app.json)
The following patterns are excluded from Obsidian's quick switcher, search index, and graph visualization:
`json
{
  "userIgnoreFilters": [
    "raw/*",
    "templates/*",
    "reports/*",
    "scripts/*",
    ".agents/*"
  ]
}
`

### Graph Physics & Color Palette (.obsidian/graph.json)
- **Ghost Node Suppression**: "hideUnresolved": true is enforced so that uncreated links do not render as hollow grey nodes.
- **Color Mapping by Schema Type**:
  - concept: #60A5FA (Blue)
  - person: #F472B6 (Pink)
  - project: #34D399 (Emerald Green)
  - 	ool: #FBBF24 (Amber Yellow)
  - cademic: #A78BFA (Purple)
  - usiness: #FB923C (Orange)
  - overview: #F87171 (Coral Red)
  - moc: #9CA3AF (Slate Grey)

---

## 7. Directory Tree & System Structure

`
Personalized-LLM-Knowledge-Graph/
├── .agents/                                # Agent Directives & Modular Prompts
│   ├── AGENTS.md                           # Central Agent Customizations Index & Router
│   ├── rules/                              # Modular Behavioral Directives
│   │   ├── 01_architecture.md              # 8 Domains, Schema & English-Only Rules
│   │   ├── 02_operations.md                # Operations, Subagent Dispatch & Safety
│   │   ├── 03_routing.md                   # Deterministic Tag-to-Folder Routing (Q1-Q4)
│   │   └── 04_data_hygiene.md              # Naming, Normalization, Ghost Link Rules
│   └── skills/                             # Executable Agent Skills
│       ├── all/SKILL.md                    # End-to-end full pipeline
│       ├── extract/SKILL.md                # Single/batch source extractor
│       ├── extract_all/SKILL.md            # Pan-conversation knowledge hunter
│       ├── ingest/SKILL.md                 # Adaptive map-reduce ingest skill
│       ├── lint/SKILL.md                   # Two-phase health check & 22-check catalog
│       ├── query/SKILL.md                  # Grounded wiki question-answering
│       └── scrape_emails/SKILL.md          # Playwright Outlook email scraper
│
├── CLAUDE.md                               # Universal adapter for Claude Code
├── .cursorrules                            # Universal adapter for Cursor / Windsurf
├── .env.example                            # Configuration template for platforms & keys
│
├── LLM_Wiki_Project/
│   ├── raw/                                # Raw Source Data Layer (Immutable)
│   │   ├── assets/                         # Ingestion Queue (Extracted markdown)
│   │   ├── imports/                        # Scraped JSON & Incremental Diff Logs
│   │   └── processed/                      # Permanent Archive of Completed Raw Files
│   │
│   ├── wiki/                               # The Official Knowledge Graph
│   │   ├── _moc.md                         # Master Vault Map of Content
│   │   ├── index.md                        # Domain Catalog & Entry Point
│   │   ├── overview.md                     # High-level synthesis
│   │   ├── log.md                          # Operation Log
│   │   ├── academic/                       # Research, Science, Lectures
│   │   ├── business/                       # Strategy, Management, Market Analysis
│   │   ├── career/                         # Resumes, Target Companies, Interview Prep
│   │   ├── dev/                            # Software Engineering, AI, Data Pipelines
│   │   ├── people/                         # Collaborators, Mentors, Authors
│   │   ├── personal/                       # Personal Reflections, Goals, Study Notes
│   │   ├── projects/                       # Active Initiatives & Research Projects
│   │   └── tools/                          # Software & Hardware Tools
│   │
│   ├── scripts/                            # Automation Engines & Deterministic Scripts
│   │   ├── run_linter.py                   # 22-Check Deterministic Wiki Linter
│   │   ├── generate_mocs.py                # Batch Map of Content (MOC) Generator
│   │   ├── reduce.py                       # AST YAML & Paragraph-Dedup Merge Reducer
│   │   ├── extract_emails.py               # JSON to Markdown Email Converter
│   │   ├── extract_all_chats.py            # Multi-Platform Chat Harvester
│   │   └── outlook_scraper/                # Headless Playwright Browser Scraper
│   │
│   ├── reports/                            # Linter Reports & Health Audits
│   │   └── lint_report.md                  # Detailed Report Generated by run_linter.py
│   │
│   ├── schema.yaml                         # Strict SSOT YAML Schema Specification
│   ├── taxonomy.md                         # Controlled Tag Vocabulary & Routing Map
│   └── templates/                          # Reusable Markdown Note Templates
└── README.md                               # Project Documentation
`

---

## 8. CLI Execution Guide & Maintenance Workflows

All maintenance commands can be executed directly from PowerShell or Bash:

### 1. Run Complete Quality Assurance (22 Checks)
`ash
python LLM_Wiki_Project/scripts/run_linter.py
`
*Outputs detailed diagnostic breakdown to eports/lint_report.md and displays health status in terminal.*

### 2. Batch Regenerate All Maps of Content (MOCs)
`ash
python LLM_Wiki_Project/scripts/generate_mocs.py
`

### 3. Harvest Agent Conversations & Exported Chats
`ash
python LLM_Wiki_Project/scripts/extract_all_chats.py
`

### 4. Git Synchronization Protocol
`ash
git status -s
git add -A
git commit -m "feat(wiki): ingest new notes and synchronize MOCs"
git push origin develop
`

---

## 9. Quick Start & Customization Guide

1. **Clone the Repository**:
   `ash
   git clone https://github.com/canadaofbin-netizen/Personalized-LLM-Knowledge-Graph.git
   cd Personalized-LLM-Knowledge-Graph
   `

2. **Set Up Python Dependencies**:
   `ash
   pip install pyyaml playwright
   playwright install chromium
   `

3. **Configure Environment (.env)**:
   `ash
   cp .env.example .env
   # Edit .env to specify your AGENT_PLATFORM (antigravity, claude_code, etc.)
   `

4. **Open in Obsidian**:
   - Open Obsidian > "Open folder as vault" > Select the repository root.
   - Graph View colors and ignore filters in .obsidian/ are automatically loaded.

5. **Start Adding Knowledge**:
   - Drop documents into LLM_Wiki_Project/raw/assets/ and tell your AI assistant:
     `
     /ingest
     `
   - Verify vault health at any time:
     `
     /lint
     `

---

## 10. License & Attribution
- **Engine**: Google Antigravity & Multi-Platform LLM Agents
- **Repository**: [https://github.com/canadaofbin-netizen/Personalized-LLM-Knowledge-Graph](https://github.com/canadaofbin-netizen/Personalized-LLM-Knowledge-Graph)
- **License**: MIT License. Open source for personal and research use.