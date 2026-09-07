---
id: PL-FX5C
title: PL-8B1K names two stale WORKING_NOTES citations but PL-006 already fixed the uptake_system.py one, so the item overstates what is left
status: untriaged
added: 2026-09-07
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
