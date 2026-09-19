---
id: PL-4PC5
title: bin/docket wave counts ids cited in a Required scope section's prose as scope entries, so v0.5.0 reads 21 ids with 11 closed against the section's own stated eighteen with 8 closed
priority: P2
effort: M
status: done
classes: defect
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-14
closed: 2026-09-19
verify: uv run pytest subprojects/docket/tests/test_roadmap.py && grep -q 'def test_an_id_a_scope_entry_names_only_in_prose_is_not_claimed' subprojects/docket/tests/test_roadmap.py
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

**Still reproduces 2026-09-14, with the numbers moved.** `ROADMAP.md`'s
`### Required scope` opens "Nineteen items, in the order the dependencies
allow"; `bin/docket wave` reports `Scope: the Required scope of v0.5.0 (25 ids),
17 closed, 8 open`. At capture it was 21 against eighteen. The gap has widened
rather than closed, which is what an id cited in prose does: every re-brief that
mentions another item adds one.

**Why it matters.** `bin/docket wave` is what the `docket` skill tells a session
to read before the queue, and `ROADMAP.md` states `Required scope` as the test
for what a milestone contains. A session is therefore told a milestone is
larger than the document says it is, with no way to see which six ids are the
difference - and the same over-count feeds the closed/open split that decides
whether the gate reads as clear.

**`PL-C4RS` is the same disagreement from the document's side** - whether the
group headings and the stated count agree - and the two have to land agreeing
with each other. This one is the tool: `scope_status` reads
`section.own_scope_ids`, which is populated from more than the list.

**Done when.** `bin/docket wave` counts only the ids a `Required scope` section
*lists* as entries, not ids its prose cites in passing, so the reported count
matches the section's own - 19 against 19 on v0.5.0 today - and
`tests/unit/` covers a section whose prose cites an id it does not list.

---

**Done 2026-09-19, by `PL-HWW1`'s declaration rule.** `Required scope` is now
read from each entry's `(queue item ...)` slot rather than in full, so an id
cited in an entry's prose places nothing. v0.5.0's section parses at **20 ids
from 20 entries** against its own stated "Twenty items" - the two numbers this
item was filed to reconcile - and the six ids the narrowing drops there
(`PL-011`, `PL-5328`, `PL-ZMRT`, `PL-2R2C`, `PL-HLD5`, `PL-GVXP`) are all
closed, so no open item changed placement. The other direction this item asked
to be measured rather than assumed was measured: v0.4.0 drops 4 citations,
v0.6.0 drops 2, the two frozen gate lists are read by their entries' heads and
were never affected.

**`verify:` re-pointed 2026-09-19, with the work.** The old command was `... &&
bin/docket wave | grep -q 'Scope.*(19 ids)'`, and it could not pass on any
tree: `PL-KD98` had since withheld the `Scope` line from `wave` while a gate is
open, which is the beat the project is on, so the string it greps for is absent
whatever the parser says. The count had also moved from 19 to 20 as the section
grew. The replacement pins the test that states this item's own defect - a
prose citation is not a member - and `touches` now names the file that test
lives in, so the discriminating clause reads a path this item declares.
