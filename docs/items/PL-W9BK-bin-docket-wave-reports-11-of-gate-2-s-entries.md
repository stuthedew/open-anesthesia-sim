---
id: PL-W9BK
title: bin/docket wave reports 11 of Gate 2's entries as blocked outside the gate when everything they wait on is v0.6.0's own Required scope, so it prints 3 cleared by the milestone where the frozen list's own group, which doc_check holds to Required scope, says 14
priority: P3
effort: S
status: ready
classes: defect, infra
feature: gate-prerequisites
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21) and not safety or science; a report fix that changes what wave prints, not what the gate is asked to clear, so nothing in v0.6.0 waits on it
added: 2026-10-03
payoff: bin/docket wave's 'blocked outside the gate' lists only entries that wait on work outside the milestone, so a reader stops reading 11 of v0.6.0's own entries as stuck
verify: grep -q 'def test_an_entry_waiting_only_on_its_milestones_own_scope_is_cleared_by_it' subprojects/docket/tests/test_roadmap.py
recurrences: 2026-10-04 PL-MFVV withdrawn 2026-10-04 PL-MFVV
---

**Problem.** bin/docket wave reports 11 of Gate 2's entries as blocked outside the gate when everything they wait on is v0.6.0's own Required scope, so it prints 3 cleared by the milestone where the frozen list's own group, which doc_check holds to Required scope, says 14

**Why it matters.** Measured 2026-10-03 on `origin/main` at `e93af565`:
`bin/docket wave` lists 17 entries as "blocked outside the gate" and 3 as
"cleared by the milestone itself". Eleven of the 17 - `PL-9LNF`, `PL-NWTM`,
`PL-50PZ`, `PL-7Z84`, `PL-904Y`, `PL-G5SX`, `PL-K285`, `PL-L8RN`, `PL-TH35`,
`PL-W54S` and `PL-JSY5` - are named in v0.6.0's Required scope, and so is
every open item they wait on at any depth: `PL-1FT6`, `PL-W9P6`, `PL-WV9K`,
`PL-R1WQ` and `PL-2KXB`, read from `roadmap.gate_status`'s own transitive
`prerequisites`. The frozen list files all 14 under "Cleared by v0.6.0 itself",
and `tools/doc_check.py`'s `check_self_cleared_group` holds that group to
Required scope (`PL-J6HP`). So the roadmap and the checker say the milestone
clears 14, and wave says 3.

Readers take wave's word. The coordinator's count on 2026-10-03 reported 18
entries blocked outside, and the project owner asked why gate entries keep
ending up blocked by work outside the gate. The first v0.6.0 report thread
(2026-09-27) had to correct for the 11 by hand. Eleven entries that wait only
on the milestone's own build also hide the ones that do not: `PL-D388`'s
`PL-VV6N` sat among them.

**Where.** `subprojects/docket/src/docket/roadmap.py`, `gate_status`.
`blocked_outside` is computed first and wins over `self_cleared`. The
`GateStatus.self_cleared` comment gives the reason: an entry that is milestone
work and waits on work off the list "is not something the milestone can simply
clear". That holds when the work is outside the milestone. It does not hold for
the milestone's own Required scope, which implementing the milestone closes.
`PL-FD5Q` already drew that line for the blockers - `GateStatus.outside_items`
subtracts `own_scope_ids` and `scope_items` reports them apart - and did not
carry it to the entries waiting on them.

**Not a change to what the gate is asked for.** Both buckets are already left
out of `clearable`, so `is_clear` and the beat do not move. Only the bucket
these 11 are printed in changes.

**Generator check.** A re-entry of `PL-FD5Q`, closed 2026-09-23, which is
within 30 days. It is the same reader defect at a sibling site: `PL-FD5Q` took
Required scope out of the blockers wave reports, and not out of the entries
waiting on them. It is not counted toward `PL-WD5Z`'s fact. That head's own
decision took `PL-FD5Q` off its members as a reader defect that moving the
disposition onto the item does not fix, and this one is the same kind. One-off
otherwise.

**Done when.** An open entry whose every open id is in `own_scope_ids`, and
whose every open prerequisite off the list (the `_prerequisites_outside` walk)
is in `own_scope_ids` too, is `self_cleared` rather than `blocked_outside`. An
entry waiting on any id outside both stays blocked outside. A regression test
pins both directions. On the store measured above, wave would then read 14
cleared by the milestone itself and 6 blocked outside the gate: the 5 Gate 3
deferrals and `PL-VV6N`.
