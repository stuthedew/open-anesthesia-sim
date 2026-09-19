---
id: PL-J45M
title: _release_due's second arrangement is positional, so a gate-only milestone whose frozen list has cleared never reaches the release beat unless the project stands on its own timeline row
priority: P3
effort: M
status: done
classes: defect
feature: timeline-arrangement
milestone: v0.4.28
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-14
closed: 2026-09-19
pr: 690
verify: ! grep -q "supported = plan.beat != IMPLEMENT or plan.own_scope is not None" subprojects/docket/src/docket/release.py
---

**Problem.** _release_due's second arrangement is positional, so a gate-only milestone whose frozen list has cleared never reaches the release beat unless the project stands on its own timeline row

**Verified 2026-09-14, and it is already being worked around.**
`subprojects/docket/src/docket/release.py:545-551` names this item in a comment
and codes around it: `supported = plan.beat != IMPLEMENT or plan.own_scope is
not None`, written because `_release_due` "matches no arrangement, and one of
the shapes it falls through on is *finished* - a gate-only milestone whose
frozen list has cleared, reached from a step that is not its own row, which the
second arrangement misses because it compares positions". That comment landed
with `PL-6T4L` (`cda6bff`, `#571`); the arrangement matching it describes is
unchanged.

**Why it matters.** `implement` is `wave`'s fall-through, so it is returned both
when a milestone genuinely has work left *and* when `_release_due` simply could
not classify the arrangement. Two different states print the same beat, and
downstream code has to guess which it is - the `supported` line above is that
guess, and it is a good one, but it is a patch over a classifier that answers
"unfinished" when it means "unrecognised". A gate-only milestone whose frozen
list has cleared is *ready to release* and is told it is unfinished.

**Done when.** `_release_due` recognises a gate-only milestone whose frozen list
has cleared regardless of which row the project stands on, so `implement` is
returned only where there is work left rather than as a fall-through, and the
`supported` workaround at `release.py:551` is removed rather than left standing.

**Closed 2026-09-19 under `PL-2T03`.** `_release_due` reads the row order from
the release train, and its second arrangement releases a gate-only milestone
whose frozen list has cleared from whichever row the project stands on;
`implement` is returned only where the milestone's own scope counts open work,
and the `supported` workaround in `release.py` is deleted rather than left
standing. Pinned by
`test_a_gate_only_milestone_reached_from_another_row_is_a_release`,
`test_implement_is_never_a_fall_through` and
`test_a_finished_gate_only_milestone_is_offered_as_the_release_it_is`.
