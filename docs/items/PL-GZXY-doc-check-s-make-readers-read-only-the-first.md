---
id: PL-GZXY
title: doc_check's make readers read only the first clause of a fenced command line and take target: prereq ; recipe for a rule with no recipe, so cd sub && make nosuch names no target and an inline recipe reads as missing; latent
status: untriaged
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check's make readers read only the first clause of a fenced command line and take target: prereq ; recipe for a rule with no recipe, so cd sub && make nosuch names no target and an inline recipe reads as missing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`_make_mentions` (4683) reads `clauses[0]` of each fenced line, so `cd sub && make nosuch` and `true; make nosuch` name no target. `make_targets` (4625) reads `target: prereq ; recipe` (GNU make's inline recipe) as a target with no recipe, which `check_make_targets` would report as "declared but carries no recipe". Not members of `PL-R417`. Latent: no fence holds the form and the Makefile writes no inline recipe.
