---
id: PL-ZB82
title: docket check could flag an open item whose verify: discriminating clause reads a path its touches omit, using verify.command_paths: a fifth instance (PL-DHJ7) turned up after PL-LBW5's four were repaired by hand
priority: P3
effort: S
status: ready
classes: infra
feature: verify-command-health
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-30
payoff: a verify command a neighbour's work could flip is caught when it is written, not after the replay blames the wrong item
verify: grep -q 'def test_a_verify_reading_a_path_its_touches_omit_is_reported' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check could flag an open item whose verify: discriminating clause reads a path its touches omit, using verify.command_paths: a fifth instance (PL-DHJ7) turned up after PL-LBW5's four were repaired by hand

**Why it matters.** A `verify:` clause reading a path its item does not declare can be flipped by a neighbour's work, so the replay blames the wrong item and `bin/docket concurrent` answers wrongly (`PL-3DXV`, `PL-LBW5`). It is decidable from `verify.command_paths` and the item's `touches`, the case `CLAUDE.md` puts in code.

**Done when.** `docket check` advises on an open item whose `verify:` discriminating clause reads a path its `touches` does not declare, naming the path, with a test.

**Read 2026-10-01.** `PL-DHJ7`'s command now reads `tests/unit/test_doc_check.py`, which its `touches` declare, so this pass found no open instance; the case for the check is the five that arrived.

**Generator check.** The fact is `PL-1P5V`'s and `PL-6TP8`'s - what a `verify:` command's exit status proves about its own item's work - read at the `touches` boundary. `PL-LBW5`'s four and `PL-DHJ7`'s were fields inside items, not filed items, so they are no head's re-filings; not a new generator.
