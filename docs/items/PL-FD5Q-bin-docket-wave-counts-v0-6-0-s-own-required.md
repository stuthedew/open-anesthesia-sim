---
id: PL-FD5Q
title: bin/docket wave counts v0.6.0's own Required-scope items among the open items outside the gate that its blocked entries wait on: 5 of the 10 it names (PL-1FT6, PL-2KXB, PL-R1WQ, PL-W9P6, PL-WV9K) are work the milestone itself clears, so the beat overstates what the gate waits on outside the milestone
priority: P3
effort: S
status: done
classes: defect
milestone: v0.5.9
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
closed: 2026-09-23
pr: 970
payoff: the session-start Beat line reports how much the gate really waits on outside the milestone - five items today, not ten
verify: grep -q 'def test_outside_items_leave_out_what_required_scope_names' subprojects/docket/tests/test_roadmap.py
---

**Problem.** bin/docket wave counts v0.6.0's own Required-scope items among the open items outside the gate that its blocked entries wait on: 5 of the 10 it names (PL-1FT6, PL-2KXB, PL-R1WQ, PL-W9P6, PL-WV9K) are work the milestone itself clears, so the beat overstates what the gate waits on outside the milestone

**Reproduced at triage, 2026-09-23.** `bin/docket wave` lists ten items under
"what they wait on", and five of them - PL-1FT6, PL-2KXB, PL-R1WQ, PL-W9P6,
PL-WV9K - appear in v0.6.0's `### Required scope`; the gate line and the
digest's Beat both print "10 open items outside it".

**Why it matters.** The Beat line is the plan statement every session start
reads, and it says the gate waits on ten items outside the milestone when half
of them are the milestone's own required work, so the dependency looks twice as
external as it is.

**Done when.** `GateStatus.outside_items` leaves out, or counts separately, the
blockers v0.6.0's Required scope names - by the same Required-scope reading
`self_cleared` uses for the gate's own entries - so `wave` and the Beat report
the true split, pinned in `test_roadmap.py`.

**Generator check.** A re-entry of `PL-J6HP` (gate facts read once in
`docket.roadmap`, closed 2026-09-23 in `#937`): one question - which work the
milestone clears itself - is answered from Required scope for the gate's entries
and not asked for what those entries wait on. Filed at 19:19 on 2026-09-22
(-0500), before the head closed at 20:40, so not a post-close instance; but the
head's `spent` verdict does not hold at this site.

**Not `PL-WD5Z`'s mechanism (2026-09-23), so it is off that head's
`root-cause-of:`.** `PL-WD5Z`'s decision round found this is a reader defect:
`outside_items` never subtracts Required scope, which is already a structured
slot. It does not come from a disposition written into prose, and moving
dispositions onto the item leaves it standing. It is fixed in `PL-WD5Z`'s
branch as its own commit led by this id, because both changes rewrite
`docket.roadmap`'s gate readers and landing them apart would conflict.
