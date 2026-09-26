---
id: PL-C7XV
title: docs/WORKING_NOTES.md's UI-structure thread says 'What was decided that day: the placement above' where the sentence above now carries two placements, so the 2026-09-16 v0.7.x move reads as a 2026-09-08 decision
priority: P3
effort: S
status: done
classes: docs
feature: interface-pass-narrative
touches: docs/WORKING_NOTES.md
added: 2026-09-16
closed: 2026-09-26
pr: 1134
verify: ! grep -qF 'the placement above' docs/WORKING_NOTES.md && python3 tools/doc_check.py check
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

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
One placement per dated entry. The 2026-09-16 move gets its own dated sentence
rather than being written over the earlier one, which is the specific edit
clause 4 forbids - a dated statement edited to carry a later fact reads as a
record of something that was never recorded.

**Done 2026-09-26, as a rider on `PL-V1Y7`**, which had to edit this sentence
anyway: break-out came off the timeline that day and the row it names became
`v0.6.x`. The 2026-09-08 paragraph now says "What was decided that day: that
position, written `v0.5.x` and sitting between v0.5.0 and v0.6.0, and that the
structural half of an overhaul is not polish", and the two later moves follow
the 2026-09-14 paragraph as their own dated sentences - 2026-09-16's, ratified
on `PL-PHKP`, and 2026-09-26's under `PL-V1Y7` - as `PL-4FBP`'s table disposed.
