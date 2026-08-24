---
id: PL-037
title: Check the branch is current against `main` before starting an item
priority: P1
effort: S
status: ready
classes: session-cost, infra
touches: .claude/skills/punch-list/SKILL.md, CLAUDE.md
added: 2026-08-24
---

**Problem.** Nothing in `CLAUDE.md` or the punch-list skill tells a session
to verify its branch against `main` before it starts work. A session that
picks up a branch whose pull request has already been merged stacks new
commits on merged history; one that starts from a stale base does the work
against code that has since moved.
**Why it matters.** Both cost a full rework cycle — the most expensive kind
of waste, since it is paid at the end of a session in merge conflicts rather
than at the start in one command. This actually happened: the session that
landed PL-032 was asked to check, found its own branch had been merged as
PR 19, and had to restart the branch from `main` before continuing.
**Where.** `.claude/skills/punch-list/SKILL.md` (a step before "Mode:
recommend what to work on" hands off, and in "Mode: hotfix"), possibly
`CLAUDE.md`'s "Punch list and work selection".
**First step.** Write the check as the three commands it actually takes:
`git fetch origin main`, `git rev-list --left-right --count origin/main...HEAD`,
and — when the branch is behind with nothing ahead — restart it from `main`
rather than merging into it.
**Done when.** The handoff a recommendation produces names the check, so a
fresh session runs it before its first edit rather than discovering the
problem at push time.
