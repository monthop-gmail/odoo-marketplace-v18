# /update

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Sync tasks, triage new items, and update completion status across the project.

## Usage

```
/update                           # Full sync and triage
/update --tasks                   # Review task list only
/update --memory                  # Update MEMORY.md only
/update --backlog                 # Triage backlog items
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                     UPDATE                            │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Review current task list from memory              │
│  ✓ Triage new items and assign priorities            │
│  ✓ Update completion percentages                     │
│  ✓ Identify blocked or stale items                   │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when codebase accessible)             │
│  + Scan codebase for actual completion status        │
│  + Count models, views, endpoints, tests             │
│  + Compare against task tree expectations            │
│  + Update MEMORY.md with verified numbers            │
│  + Update backlog.md with triage results             │
└─────────────────────────────────────────────────────┘
```

## Update Workflow

1. **Read Current State** — Load MEMORY.md, task_tree.md, backlog.md
2. **Scan Codebase** — Count actual artifacts (models, controllers, views, tests)
3. **Compare** — Match actual vs expected for each component
4. **Triage** — Classify new/changed items as priority/normal/deferred
5. **Write Back** — Update memory files with verified status

## Triage Matrix

| Signal | Priority | Action |
|--------|----------|--------|
| New critical bug | P1 | Add to top of backlog |
| Security gap found | P1 | Add to top of backlog |
| Feature incomplete | P2 | Update completion % |
| Test missing | P3 | Add to backlog |
| Documentation gap | P4 | Add to backlog |
| Optimization opportunity | P4 | Add to backlog |

## Key Files

| File | Purpose | Updated By |
|------|---------|-----------|
| `memory/MEMORY.md` | Project status and context | /update --memory |
| `memory/task_tree.md` | Full task breakdown | /update --tasks |
| `memory/backlog.md` | Prioritized backlog | /update --backlog |

## Output

```markdown
## Update Summary

**Date:** [date]
**Scope:** [full/tasks/memory/backlog]

### Changes Detected
| Component | Previous | Current | Delta |
|-----------|----------|---------|-------|
| Models | [n] | [n] | [+/-n] |
| Controllers | [n] | [n] | [+/-n] |
| Endpoints | [n] | [n] | [+/-n] |
| Tests | [n] | [n] | [+/-n] |

### Triage Results
| Item | Priority | Status |
|------|----------|--------|
| [description] | [P1-P4] | [new/updated/deferred] |

### Files Updated
- [file path] — [what changed]
```

## Next Steps

- Want me to start working on the top priority item?
- Should I update the task tree with new estimates?
- Want to see the full backlog sorted by priority?

## Related Skills

- Uses [productivity](../skills/) for task management logic
- Cross-references all domain skills for completeness checks
