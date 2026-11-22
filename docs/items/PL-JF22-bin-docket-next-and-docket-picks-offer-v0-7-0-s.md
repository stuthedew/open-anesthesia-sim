---
id: PL-JF22
title: bin/docket next and docket picks offer v0.7.0's Required-scope items while Gate 3's second group is still open, though ROADMAP.md § The cadence beat 3 clears the gate before implementation begins (the likely route by which PL-6590's slip happened)
priority: P2
effort: S
status: ready
classes: defect
feature: planning-cadence
touches: subprojects/docket/src/docket/picks.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests
deferred-from: v0.7.0 - present at the freeze, deferred on a stated reason: the fault shows only while a gate is being cleared, and v0.7.0 is past that beat (bin/docket wave, 2026-11-22: no entry this gate can clear, all 19 Required-scope ids closed), so a fix protects nothing on this gate and first applies at Gate 4
added: 2026-11-11
payoff: From Gate 4 on, the work picker stops handing out milestone features while the gate is still being cleared, so the rule the owner kept on 2026-11-11 is the one sessions follow.
---

**Problem.** bin/docket next and docket picks offer v0.7.0's Required-scope items while Gate 3's second group is still open, though ROADMAP.md § The cadence beat 3 clears the gate before implementation begins (the likely route by which PL-6590's slip happened).

**Evidence, 2026-11-11.** `bin/docket next product` ranks `PL-RJN9` second.
`PL-RJN9` is v0.7.0 Required-scope entry 13, so it is milestone implementation,
and Gate 3 still has 36 entries open. `docket picks` prints a "Build, from the
milestone's Required scope" block during the clear beat. That block only
appends "the roadmap clears the gate first" (`render.py`, the `build_waits`
branch). `PL-KFTM`, a Required-scope item, was built and closed on 2026-11-01
while the gate was open. No record shows which command its session picked it
from, so the route is likely rather than shown.

**Why it matters.** `PL-6590` (does the debt gate have to clear before a
milestone's features are built?) recommends keeping the rule so it applies
again from Gate 4. While the tools offer Required-scope work by band during the
clear beat, `next` ranks a build item by its band among the gate's entries,
so a P1 build item comes ahead of every P2 and P3 gate entry. The rule will be
skipped again the same way.

**Done when.** `next` and `docket picks` stop offering a milestone's
Required-scope item while the beat is `clear`, or offer it only as off-gate
work that `ROADMAP.md` § "The cadence" beat 3 holds back. The project owner
kept the rule on 2026-11-11 (ratified, over rewriting it as "debt and features
are worked side by side"), in the `PL-6590` decision, so it applies again from
Gate 4 and the tools must say the same thing.

Found while reviewing `PL-6590`'s recommendation, 2026-11-11.

**Checked 2026-11-22**, at `d4e8200c`. The fault cannot be run today, because
`bin/docket wave --no-fetch` reports the beat as "release v0.7.0": Gate 3 holds
no entry it can clear, and all 19 Required-scope ids have closed. Read in the
code instead, it is still there. `subprojects/docket/src/docket/picks.py` line
326 sets `build_waits=plan.beat == CLEAR`, and `render.py` (lines 3655 to 3662)
uses it only to append "the roadmap clears the gate first" to a build block it
prints either way. `PLACEMENT_ORDER` in `plan.py` (line 495) ranks the
milestone's own Required scope below the gate's entries and unplaced work, but
`next` still offers it once those run short. Both were the same at the Gate 3
freeze (`0947408`).

**Generator check.** The fact is what work the current beat of the cadence
allows: whether a milestone's build may start while its gate is open. The
picker reads the beat and only annotates the offer. One-off: no other item
misreads this fact, and no head's `misread:` states it.
