---
name: lint
description: Triggers when the user uses `/lint`. Runs a comprehensive Two-Phase health check (Syntactic + Semantic) on the LLM Wiki.
---

# Wiki Linter

`/lint` executes a comprehensive Two-Phase (Syntactic + AI Semantic) sweep.

## Phase 1: Syntactic Audit
Run `python "LLM_Wiki_Project/scripts/run_linter.py"`. Read the generated `LLM_Wiki_Project/scripts/lint_report.md`.

## Phase 2: AI Semantic Sweep (Map-Reduce)
Spawn a `pro` subagent per subfolder with markdown files:
- **Role**: Domain Semantic Auditor
- **Prompt**: "Read all `.md` files in `{subfolder}`. Find hidden semantic duplicates that evade Python string-matching. Verify if tags match [taxonomy.md](../../../LLM_Wiki_Project/taxonomy.md). Return: [Duplicate Pair] - [Reason] - [Recommendation]."
Collect all subagent results.

## Output Artifact
Create `lint_audit.md` artifact containing:
- **Summary**: P1 (Green/Yellow/Red), P2 (Pass/Fail counts)
- **Phase 1 Issues**: From python report.
- **Phase 2 Issues**: True semantic duplicates and tag issues.
- **Next Steps**: Numbered repair list. Ask for user permission.

## Hard Rules
- Never delete files unilaterally. See [02_operations.md](../../rules/02_operations.md).
- Follow architectural rules in [01_architecture.md](../../rules/01_architecture.md).
