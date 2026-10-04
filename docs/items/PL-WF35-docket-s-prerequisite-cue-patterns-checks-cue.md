---
id: PL-WF35
title: docket's prerequisite cue patterns - checks._cue_pattern, PROSE_DEPENDENCY, CLOSED_DEPENDENCY and the continuation - refuse a line break between cue and id, so a waits-on clause wrapped before its id is never read, and PL-KZ99's dependency on an item done since 2026-09-17 raises no advisory; live
priority: P2
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests, tests/unit, docs/items/PL-KZ99-store-each-agent-s-molar-mass-and-liquid.md, docs/items/PL-BYMX-bin-docket-stranded-compares-branches-by-item.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1358
payoff: a wait wrapped before its id is read like one on a single line, so a brief still waiting on finished work, or naming an undeclared prerequisite, is advised on wherever its line breaks
verify: grep -qF '"prerequisite cues, ' tests/unit/test_doc_check.py
---

**Problem.** docket's prerequisite cue patterns - checks._cue_pattern, PROSE_DEPENDENCY, CLOSED_DEPENDENCY and the continuation - refuse a line break between cue and id, so a waits-on clause wrapped before its id is never read, and PL-KZ99's dependency on an item done since 2026-09-17 raises no advisory; live

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.7: a clause continues across a soft line break. The window `[^.\n;:()\"|—]{0,40}?` refuses `\n`, so `PROSE_DEPENDENCY` over "**Depends on.** This item is blocked on" wrapped onto "`PL-GHJK`, which is still open." finds nothing, where the same text on one line finds `PL-GHJK`; the continuation pattern misses "Blocked on `PL-GHJK` and on" wrapped onto "`PL-MNPQ`". Read by `_undeclared_prerequisites` and `_ended_waits` through `_prerequisite_matches`.

**Live:** `docs/items/PL-KZ99-store-each-agent-s-molar-mass-and-liquid.md`:58-59 reads "the same block on" over "`PL-S6WW`", and `_ended_waits` names nothing; joined, it reports that `PL-S6WW` is done. Re-reading the 298 open items with each statement's soft breaks joined adds three advisories: that one, true, and two false ones on `PL-BYMX`, whose lines 58-59 narrate `PL-W7H9`'s blockers - the third item's edge the docstring already names as a blind spot.

The docstring (checks.py:3106-3109) records the wrapped case as deliberately unread, on a 2026-09-23 count of four passages, two of them negations; `NEGATED_CUE` now reads a negation across a break, so that half of the count no longer holds, and nothing declines the wrap at run time. Whether to read it (one true and two false advisories today) or decline it by name is the fix's call.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `_prerequisite_matches` over "**Depends on.** This item is blocked on" wrapped onto "`PL-GHJK`, which is still open." returns nothing, where the one-line form returns `PL-GHJK`; and `bin/docket check` raises no advisory on `PL-KZ99`, whose lines 58-59 read "the same block on" over "`PL-S6WW`", done since 2026-09-17.

**Why it matters.** `docket next` never opens a brief, so these advisories are the only thing holding a dependency stated in prose to `blocked-by` and to the state of the item it names; the item format wraps at 80 columns, so a cue landing at a line's end is ordinary, and each one wrapped there is a wait nobody is told has ended or was never declared.

**Decided at triage: read the wrap.** The two false advisories it adds on `PL-BYMX` are a third item's edge narrated, the blind spot the docstring already names for a cue on one line, so the wrap brings no new class of false reading; and `NEGATED_CUE` already reads its half across a break. Declining it by name would put a refusal on every wrapped cue in the store for the sake of two narrations.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** The cue patterns read a cue and its id across a soft break, never across a blank line or a block's start; the docstring's blind-spot paragraph says so; the advisories that reading adds on the tree are resolved in the briefs they name, `PL-KZ99`'s true one and `PL-BYMX`'s two false ones; and `prerequisite cues, ...` cases in `CONTINUED_STATEMENTS` pin it.
