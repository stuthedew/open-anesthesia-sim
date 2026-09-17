---
id: PL-C7XV
title: docs/WORKING_NOTES.md's UI-structure thread says 'What was decided that day: the placement above' where the sentence above now carries two placements, so the 2026-09-16 v0.7.x move reads as a 2026-09-08 decision
priority: P3
effort: S
status: ready
classes: docs
feature: interface-pass-narrative
touches: docs/WORKING_NOTES.md
added: 2026-09-16
verify: python3 tools/doc_check.py check && ! grep -qF 'the placement above' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md's UI-structure thread says 'What was decided that day: the placement above' where the sentence above now carries two placements, so the 2026-09-16 v0.7.x move reads as a 2026-09-08 decision

**Found while closing `PL-D1RT`** (the stale `v0.5.x — the interface pass`
citations), whose sweep is what created the residue.

The thread § "Shelved, then resumed: UI structure/form mockups" now reads:

> … with the interface-pass row of "The timeline" giving it a position -
> written `v0.5.x` and sitting between v0.5.0 and v0.6.0 then, and `v0.7.x`
> sitting after item 34's two releases since 2026-09-16 (`PL-PHKP`). What was
> decided that day: the placement above, and that the structural half of an
> overhaul is not polish …

"That day" is 2026-09-08, when the project owner asked for the pass and placed
it. The sentence it points back to now carries **two** placements, because
`PL-PHKP` (move the interface pass after v0.7.0) folded the 2026-09-16 move
into the same clause. So "the placement above" no longer names one thing, and
the nearest reading attributes a 2026-09-16 decision to a 2026-09-08
conversation.

**Why it is worth an item rather than a passing fix.** `CLAUDE.md`'s
provenance rule turns on who decided what and when, and its own ratified/
specified distinction is read off exactly these attributions - a decision the
owner *specified* takes a compelling argument to reopen, one they *ratified*
takes ordinary evidence. A sentence that hands a session's recommendation to
the owner's own 2026-09-08 framing raises the bar to reopen it.

**Done when** the thread names one placement per decision date, so that the
2026-09-08 sentence claims only what was decided on 2026-09-08.

**Why it matters.** `docs/WORKING_NOTES.md` is where a later session goes to find
out what was decided and by whom, and this sentence now attributes a 2026-09-16
move to a 2026-09-08 conversation with the project owner. Misattributed
provenance is worse than none: `CLAUDE.md` distinguishes a decision the owner
*specified* from one they *ratified* precisely because the two have different
bars to reopen, and a reader cannot apply that rule to a decision whose date is
wrong.

**Done when** the thread names the 2026-09-08 decision and the 2026-09-16 move
separately, each with its date, so "what was decided that day" resolves to one
placement. The `verify:` command pins the ambiguous clause being gone rather than
any particular replacement wording.
