---
id: PL-FX5C
title: PL-8B1K names two stale WORKING_NOTES citations but PL-006 already fixed the uptake_system.py one, so the item overstates what is left
priority: P3
effort: S
status: dropped
reason: PL-8B1K closes in the same branch as PL-X2XX, against the one instance that survived. There is no longer an overstated brief for a later session to read - the item records both instances and its closure records that PL-006 had already taken one of them.
classes: docs
feature: dev-tooling
touches: docs/items/PL-8B1K-two-citations-into-docs-working-notes-md-name.md
added: 2026-09-07
closed: 2026-09-07
---

**Problem.** PL-8B1K names two stale WORKING_NOTES citations but PL-006 already fixed the uptake_system.py one, so the item overstates what is left

`PL-8B1K` reads as two stale citations into `docs/WORKING_NOTES.md`. Only one
survives: `grep -n 'near-term to-dos' src/anesthesia_sim/core/uptake_system.py`
returns nothing as of 2026-09-07, because `PL-006` rewrote that module
docstring. The surviving instance is
`docs/items/PL-042-bound-the-splitting-error-across-the-settings.md:37`.

Its `verify:` command already reflects this - the `uptake_system.py` half
passes on the current tree - so the item is half-proven by a command written
before the work, which is the state the `verify:` rules warn about. Narrow the
brief to the one instance, or close the item against `PL-042` alone.

Found while working `PL-X2XX`, whose **Done when** asks that both instances be
among the errors the widened check reports; one of them cannot be.
