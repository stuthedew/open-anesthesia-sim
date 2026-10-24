---
id: PL-SH0W
title: Give each configuration fact (Python version, paths, commands, timeouts) one home across pyproject.toml, .github/workflows/, the Makefile, docket.toml and the docs, held by a check
priority: P3
effort: S
status: ready
classes: infra
feature: one-source-of-truth
touches: pyproject.toml, Makefile, .github/workflows/
blocked-by: v0.6.0, PL-K88Z
added: 2026-10-19
payoff: a configuration fact changed in one file cannot leave another running the old value
verify: grep -q 'config_home_check' Makefile
---

**Problem.** Give each configuration fact (Python version, paths, commands, timeouts) one home across pyproject.toml, .github/workflows/, the Makefile, docket.toml and the docs, held by a check

**Why it matters.** Step 6 of `PL-2LB5` (the one-source-of-truth design round). A configuration fact restated across files drifts silently: one copy changes and the others keep running the old value.

**Done when.** Each configuration fact the inventory (`PL-K88Z`) finds in more than one file has one home that the others read, or a check that fails when a copy differs from its home.

**Generator check.** Not a re-entry: it is a step of `PL-2LB5` (the one-source-of-truth design round), which widens the closed `PL-4S6C` at the project owner's ask, and no open generator head names this shape.
