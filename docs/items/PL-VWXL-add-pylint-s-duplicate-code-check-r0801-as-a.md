---
id: PL-VWXL
title: Add pylint's duplicate-code check (R0801) as a ratchet over src/, tools/ and subprojects/docket/, with a baseline that can only shrink
priority: P3
effort: S
status: ready
classes: refactor, infra
feature: one-source-of-truth
touches: Makefile, pyproject.toml
blocked-by: v0.6.0, PL-K88Z
deferred-from: v0.6.0 - placed on ROADMAP.md's v0.6.x one-source-of-truth row, built after v0.6.0 ships (project owner, 2026-10-19, ratified, PL-2LB5)
added: 2026-10-19
payoff: copied logic fails make check instead of drifting apart
verify: grep -q 'duplicate-code' Makefile
---

**Problem.** Add pylint's duplicate-code check (R0801) as a ratchet over src/, tools/ and subprojects/docket/, with a baseline that can only shrink

**Why it matters.** Step 5 of `PL-2LB5` (the one-source-of-truth design round). Copied logic is the third shape of a second copy. pylint already ships a duplicate-code checker, so this adds a ratchet over an existing tool rather than a new one.

**Done when.** `make check` runs pylint `R0801` over `src/`, `tools/` and `subprojects/docket/`, fails on a duplicate block not in its baseline, and the baseline is at zero.

**Generator check.** Not a re-entry: it is a step of `PL-2LB5` (the one-source-of-truth design round), which widens the closed `PL-4S6C` at the project owner's ask, and no open generator head names this shape.
