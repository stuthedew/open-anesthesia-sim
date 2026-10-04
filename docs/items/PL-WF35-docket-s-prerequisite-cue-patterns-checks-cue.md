---
id: PL-WF35
title: docket's prerequisite cue patterns - checks._cue_pattern, PROSE_DEPENDENCY, CLOSED_DEPENDENCY and the continuation - refuse a line break between cue and id, so a waits-on clause wrapped before its id is never read, and PL-KZ99's dependency on an item done since 2026-09-17 raises no advisory; live
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's prerequisite cue patterns - checks._cue_pattern, PROSE_DEPENDENCY, CLOSED_DEPENDENCY and the continuation - refuse a line break between cue and id, so a waits-on clause wrapped before its id is never read, and PL-KZ99's dependency on an item done since 2026-09-17 raises no advisory; live

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.7: a clause continues across a soft line break. The window `[^.\n;:()\"|—]{0,40}?` refuses `\n`, so `PROSE_DEPENDENCY` over "**Depends on.** This item is blocked on" wrapped onto "`PL-GHJK`, which is still open." finds nothing, where the same text on one line finds `PL-GHJK`; the continuation pattern misses "Blocked on `PL-GHJK` and on" wrapped onto "`PL-MNPQ`". Read by `_undeclared_prerequisites` and `_ended_waits` through `_prerequisite_matches`.

**Live:** `docs/items/PL-KZ99-store-each-agent-s-molar-mass-and-liquid.md`:58-59 reads "the same block on" over "`PL-S6WW`", and `_ended_waits` names nothing; joined, it reports that `PL-S6WW` is done. Re-reading the 298 open items with each statement's soft breaks joined adds three advisories: that one, true, and two false ones on `PL-BYMX`, whose lines 58-59 narrate `PL-W7H9`'s blockers - the third item's edge the docstring already names as a blind spot.

The docstring (checks.py:3106-3109) records the wrapped case as deliberately unread, on a 2026-09-23 count of four passages, two of them negations; `NEGATED_CUE` now reads a negation across a break, so that half of the count no longer holds, and nothing declines the wrap at run time. Whether to read it (one true and two false advisories today) or decline it by name is the fix's call.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
