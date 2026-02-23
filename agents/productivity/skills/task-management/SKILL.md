---
name: task-management
description: Activate when tracking tasks, priorities, backlogs, or work breakdown
  for the marketplace platform. Covers task sources, priority framework, current priorities,
  and epic-to-subtask decomposition.
---

# Task Management (Project Coordinator)

You are a project coordinator who tracks all work items, priorities, and progress for the marketplace platform. You maintain task trees, manage backlogs, and ensure work is broken down into actionable units.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Task Sources

| Source | Path | Content | Update Frequency |
|--------|------|---------|-----------------|
| Task Tree | `memory/task_tree.md` | Full hierarchical breakdown | Per work session |
| Backlog | `memory/backlog.md` | Prioritized future work | Weekly |
| MEMORY.md | `~/.claude/.../MEMORY.md` | Completion status, known issues | Per session |
| CLAUDE.md | Project root `CLAUDE.md` | Phase roadmap, architecture | Rarely |
| GitHub Issues | `gh issue list` | External bug reports, features | As filed |

## Priority Framework

| Level | Label | Definition | Response Time |
|-------|-------|-----------|---------------|
| P0 | Critical | System down, data loss, security breach | Immediate |
| P1 | High | Feature broken, blocking other work | Same day |
| P2 | Medium | Enhancement, non-blocking bug | This sprint |
| P3 | Low | Nice to have, tech debt, cleanup | Next sprint |

## Current Priorities

| Priority | Task | Plugin | Status |
|----------|------|--------|--------|
| P1 | Fix security (row-level rules + seller permissions) | seller-engine | Pending |
| P2 | Promotion LIFF App (models + API + frontend) | liff-apps | 5% stub |
| P2 | Support LIFF App (models + API + frontend) | liff-apps | 5% stub |
| P2 | OWL components rewrite (Odoo 18 OWL 2.x) | commerce | Pending |
| P2 | Add core_marketplace tests | data | 0% |
| P3 | Admin rich menu redesign | line-platform | Pending |
| P3 | Phase 3: Affiliate, AI moderation, Ranking, Boost | All | Planned |

## Task Breakdown Pattern

```
Epic (Phase-level goal)
  Feature (User-facing capability)
    Task (Implementable unit, 1-4 hours)
      Subtask (Single file change or function)
```

### Example Breakdown

```
Epic: Promotion LIFF App
  Feature: Promotion Models
    Task: Create promotion.campaign model
    Task: Create promotion.coupon model
    Task: Add security rules + access CSV
  Feature: Promotion API
    Task: GET /promotions (list active)
    Task: POST /promotions (create campaign)
    Task: POST /promotions/apply (apply coupon)
  Feature: Promotion LIFF UI
    Task: Campaign list page
    Task: Create campaign form
    Task: Coupon distribution page
```

## Task Status Values

| Status | Meaning |
|--------|---------|
| Planned | In backlog, not started |
| Pending | Ready to start, dependencies met |
| In Progress | Actively being worked on |
| Review | Code complete, awaiting review |
| Complete | Merged and verified |
| Blocked | Waiting on dependency or decision |

## Cross-References

- [platform-admin](../platform-admin/SKILL.md) for priority decisions
- [memory-management](../memory-management/SKILL.md) for persisting task state
- [daily-briefing](../daily-briefing/SKILL.md) for surfacing priority items
