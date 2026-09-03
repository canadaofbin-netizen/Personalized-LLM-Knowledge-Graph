# CLAUDE.md — Claude Code Project Guidelines

This repository implements an autonomous, self-healing Personal Knowledge Graph and Wiki System.
Detailed modular rules are maintained in .agents/rules/ and .agents/skills/. When operating in this repository, strictly adhere to the following architecture and protocols.

---

## 1. Core Architecture & 8 Canonical Domains
All compiled knowledge pages reside in LLM_Wiki_Project/wiki/ organized under strictly 8 canonical domains:
- **cademic/**: Research papers, study notes, lectures, scientific concepts.
- **usiness/**: Strategy, finance, management, corporate dossiers.
- **career/**: Resume/CV dossiers, interview prep, company targets, portfolio.
- **dev/**: Programming, software architecture, AI pipelines, dev tools.
- **people/**: Profiles of collaborators, researchers, mentors (	ype: person).
- **personal/**: Personal reflections, goals, study notes, administration.
- **projects/**: Active initiatives and research projects (	ype: project).
- **	ools/**: Hardware and software utilities (	ype: tool).

*Rule*: Directory nesting is strictly capped at a maximum of 2 levels below wiki/ (e.g. wiki/academic/neuroscience/). Every directory must contain a local _moc.md.

---

## 2. Formatting & Data Hygiene Protocols
1. **File Naming Standard**: All wiki files MUST use Underscore_Separated_Title_Case.md (e.g., Machine_Learning_Fundamentals.md). No spaces or illegal characters: `()[]{}#%&*|\/:"<>?—.`.
2. **Language**: All generated files must be written in **professional English only**.
3. **Single YAML Frontmatter**: Exactly one YAML frontmatter block at lines 1–N. Never inject secondary YAML headers into the markdown body.
4. **Ghost Link Prevention**: Raw source files (email_*.md, chat_extract_*.md, outlook_emails.json, etc.) must **NEVER** be wrapped in [[wikilinks]]. Always cite them as plain text strings in sources: [filename.md] or under ## Sources as - filename.md. Wikilinks [[...]] are strictly reserved for actual wiki notes.
5. **Schema SSOT**: Adhere to LLM_Wiki_Project/schema.yaml for mandatory frontmatter fields (	ype, 	itle, description, 	ags, 	imestamp, sources).
6. **Controlled Tags**: Select tags exclusively from LLM_Wiki_Project/taxonomy.md. Tags must be lowercase, hyphen-separated.

---

## 3. Operations & Automation Scripts
- **Deterministic Quality Check**:
  `ash
  python LLM_Wiki_Project/scripts/run_linter.py
  `
- **Rebuild Navigation Hubs (MOCs)**:
  `ash
  python LLM_Wiki_Project/scripts/generate_mocs.py
  `
- **Historical Chat Harvester**:
  `ash
  python LLM_Wiki_Project/scripts/extract_all_chats.py
  `
- **Email Extraction**:
  `ash
  python LLM_Wiki_Project/scripts/extract_emails.py
  `

---

## 4. Multi-Platform Adaptation Notice
This project was originally developed within the Google Antigravity environment. When running with Claude Code:
- Use standard bash commands to execute the Python scripts in LLM_Wiki_Project/scripts/.
- If you have exported conversations (conversations.json from Claude.ai or ChatGPT), drop them into LLM_Wiki_Project/raw/imports/ and run extract_all_chats.py.