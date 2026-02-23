---
name: memory-management
description: Activate when managing Claude persistent memory, deciding what to save
  or remove from MEMORY.md, organizing deep storage files, or optimizing context
  window usage across sessions.
---

# Memory Management (Context Keeper)

You are a memory management specialist who maintains Claude's persistent knowledge base across sessions. You decide what information to store, where to store it, and when to prune, ensuring fast context loading and accurate recall.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Memory Architecture

```
CLAUDE.md (project root)
  Read every session, project-level instructions
~/.claude/projects/.../MEMORY.md (auto-memory)
  Hot cache: key facts, status, patterns
memory/*.md (deep storage)
  Detailed specs, full breakdowns, design docs
agents/skills/*/SKILL.md (domain knowledge)
  Auto-activated by topic, not manually loaded
```

## Hot Cache Rules (MEMORY.md)

| Rule | Guideline |
|------|-----------|
| Max lines | Keep under 200 lines total |
| Structure | Use headers, tables, and bullet points (scannable) |
| Update frequency | Every session that changes project state |
| Content type | Facts, decisions, status, patterns, warnings |
| No code blocks | Save code examples in deep storage instead |
| No duplication | If it exists in CLAUDE.md, don't repeat in MEMORY.md |
| Date stamp | Mark significant entries with date |

## Deep Storage Files

| File | Path | Content |
|------|------|---------|
| Task Tree | `memory/task_tree.md` | Full hierarchical task breakdown |
| Backlog | `memory/backlog.md` | Prioritized future work items |
| Rich Menu Design | `memory/rich_menu_design.md` | Rich menu specs and dimensions |
| Plugin Patterns | `memory/plugin_patterns.md` | Anthropic plugin architecture notes |

## What to Save

| Save | Example |
|------|---------|
| Completion status changes | "Wallet System: 100% complete" |
| New patterns discovered | "auth='none' requires with_user(SUPERUSER_ID)" |
| Critical bug fixes | "Cart add bug: template vs variant ID mismatch" |
| Architecture decisions | "Single LINE OA for all roles with dynamic switching" |
| External integrations | "Rich menu IDs, API endpoints, test user IDs" |
| Known issues | "OWL components disabled, needs Odoo 18 rewrite" |

## What NOT to Save

| Don't Save | Reason |
|------------|--------|
| Full code implementations | Too large, read from source files |
| Temporary debugging info | Irrelevant next session |
| Speculative plans not decided | Creates confusion |
| Information already in CLAUDE.md | Duplication wastes context |
| Step-by-step command history | Not useful for future sessions |
| File contents verbatim | Use file paths instead |

## Memory Update Protocol

1. At session start: read MEMORY.md and CLAUDE.md (auto-loaded)
2. During work: note significant changes mentally
3. Before session end: update MEMORY.md with new facts
4. If MEMORY.md > 200 lines: move detail to `memory/*.md`, keep summary
5. If a deep storage file > 500 lines: split into sub-files

## Cross-References

- [task-management](../task-management/SKILL.md) for task-related memory
- [platform-admin](../platform-admin/SKILL.md) for architecture decisions to remember
- [daily-briefing](../daily-briefing/SKILL.md) for session start context loading
