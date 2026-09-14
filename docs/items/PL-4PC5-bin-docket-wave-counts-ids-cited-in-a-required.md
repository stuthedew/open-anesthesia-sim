---
id: PL-4PC5
title: bin/docket wave counts ids cited in a Required scope section's prose as scope entries, so v0.5.0 reads 21 ids with 11 closed against the section's own stated eighteen with 8 closed
status: untriaged
added: 2026-09-14
---

**Problem.** bin/docket wave counts ids cited in a Required scope section's prose as scope entries, so v0.5.0 reads 21 ids with 11 closed against the section's own stated eighteen with 8 closed

**Found 2026-09-14, mapping v0.5.0's open Required scope after Gate 1 cleared.**

**The count and where the extra ids come from.** `bin/docket wave` reported
`the Required scope of v0.5.0 (21 ids), 11 closed, 10 open`. The section states
its own size in its first line - "Eighteen items, in the order the dependencies
allow" - and has eighteen `- **...**` entries. The three extra ids are cited
*inside* those entries' prose rather than being entries of their own:

| Id | Where it is cited | What it is |
| --- | --- | --- |
| `PL-011` | inside the `PL-2FM6` entry | the dropped retention item whose debt that entry pays |
| `PL-HLD5` | inside the `PL-8PSW` entry | the channel-assignment reversal that entry records |
| `PL-GVXP` | inside the `PL-8PSW` entry | the 1.01:1 contrast measurement that forced it |

All three happen to be closed or dropped, so they inflate both sides: 8 of 18
real entries closed reads as 11 of 21. Nothing is currently *mis-offered* -
`docket next` would have to meet an open one - but the progress figure a
session reports to the project owner is wrong, and the beat line carries it.

**It reproduced immediately, on this session's own edit.** `PL-5328` corrected
the `PL-RD3B` entry's stale noun and recorded the provenance the way this
document does everywhere else - "**Re-briefed 2026-09-14** (`PL-5328`)". The
count moved to `22 ids, 12 closed` on the next run. So the defect is not a
historical accident in three old entries: **following the roadmap's own
citation idiom creates a new false scope entry every time**, which is what
makes this worth fixing in the parser rather than by editing the prose.

**Why the prose is not the fix.** Citing the id that changed an entry is how
this file is written throughout, and it is load-bearing provenance -
`.claude/rules/expert-review.md` requires that a future reviewer be able to
determine why a decision exists. Stripping the ids to satisfy the parser would
trade a real property for a count.

**Where.** `subprojects/docket/src/docket/roadmap.py`. The `Scope` reader
should count an id only where it *leads* a `Required scope` entry - the
`- **...**` bullet's own `(queue item PL-XXXX)` position - not anywhere in the
section's text. `docket next`'s placement line reads the same structure, so
both move together. The skill already states the intended rule - "Placement is
read from the frozen list a milestone records and its `Required scope`, never
from a mention elsewhere in the section" - so this is the implementation
disagreeing with the documented behaviour rather than an undecided question.

**Check the other direction too.** The Qt port's Required scope and the two frozen
gate lists are read by the same code; whether they carry the same inflation is
a measurement this item should take rather than assume.

**Not a count to correct in `ROADMAP.md`.** The section deliberately does not
record how many of its entries are closed, for the reason the v0.4.0 section
gives: a count written into a document goes stale the next time an item
closes. The fix belongs in the reader.
