---
id: PL-QWF8
title: A report on a frozen gate cannot read every open entry's lane from docket: bin/docket gate lists lanes for open debt only, and wave, show and list print none, so v0.6.0's PL-5B1N (classed feature) and PL-B396 (ux, docs) still need Item.lane by hand
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: a what's-left report reads every frozen entry's lane from docket, the non-debt ones included, instead of computing two by hand
verify: grep -q 'def test_wave_prints_each_entry_lane' subprojects/docket/tests/test_roadmap.py
---

**Problem.** A report on a frozen gate cannot read every open entry's lane from docket: bin/docket gate lists lanes for open debt only, and wave, show and list print none, so v0.6.0's PL-5B1N (classed feature) and PL-B396 (ux, docs) still need Item.lane by hand

**Evidence, 2026-10-03.** Found closing `PL-M26Q`, which made `bin/docket gate`
list every open debt item under its lane. `bin/docket wave` names 61 open
entries on v0.6.0's frozen list; 59 of them appear in `bin/docket gate`'s
output, and the two that do not are `PL-5B1N`, classed `feature`, and
`PL-B396`, classed `ux, docs` and blocked - frozen entries that `plan.is_debt`
no longer counts, so `gate` never reads them. Neither `bin/docket show` nor
`bin/docket list` prints a lane, so their lanes are still `Item.lane` called by
hand, which is how the v0.6.0 "what's left" report of 2026-09-27 computed every
lane.

**Why it matters.** The project owner picked `PL-M26Q` on 2026-10-03 so that a
"what's left" report reads each item's lane from docket instead of computing it.
That now holds for open debt and not for a frozen entry that is something else,
so a report still has to know which entries fall outside `gate` and compute
those, or miss them.

**Done when.** Every open entry on a frozen gate list has a lane a report can
read from a docket command, using `Item.lane` against `workflow_paths` as
`docket next` and `docket gate` do.

**Re-checked 2026-10-03 at triage.** `bin/docket gate` still prints no row for
`PL-5B1N` or `PL-B396`; the one line naming either is `PL-YRLM`'s title. Both
are on v0.6.0's frozen list, now among its deferrals to Gate 3.

**Generator check.** One of five items filed since `PL-J6HP` and `PL-WD5Z`
closed on 2026-09-23 that misread a frozen gate's entries - which items it
holds, each one's lane, and what clears it - with `PL-JV5Q`, `PL-Z64T`,
`PL-D388` and `PL-W9BK`. Three post-close instances read as a fix that did not
hold; `PL-74T0` records the head or refuses it as its cluster 2.
