---
id: PL-LN3T
title: wave does not report a milestone row the version has released whose section's Required scope is still open, so a patch cut at a milestone's own number leaves the plan stepped past it once the hand-off has scrolled by
priority: P2
effort: S
status: done
classes: defect
feature: timeline-arrangement
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/README.md, ROADMAP.md, docs/items
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'def test_a_released_milestone_row_with_its_scope_still_open_is_reported' subprojects/docket/tests/test_roadmap.py
---

**Problem.** wave does not report a milestone row the version has released whose section's Required scope is still open, so a patch cut at a milestone's own number leaves the plan stepped past it once the hand-off has scrolled by

**Found 2026-09-19 closing `PL-2T03`**, as the residual of `PL-Y1L0`'s first
case. `ReleaseTrain.stale` reports a milestone row the version has *passed*
with no release of that number in the version table, and
`outstanding_roadmap_edits` states a number the cut has exactly *reached* at
the hand-off. A patch cut at a milestone's own number then writes that number
into the version table, so once the hand-off has scrolled by nothing
distinguishes the port shipped from the port skipped: the row reads as
released, its section drops out of the train's `ahead`, and the beat moves on.
The store knows the difference - the section's `Required scope` is still open -
and `wave` has the closed ids in hand.

**Why it matters.** The reversal of an owner's placement (`PL-RKWB`'s shape) is
what `PL-Y1L0` was filed on, and for this case it is now reported once, at the
cut, rather than on every run afterwards.

**Done when.** `wave` carries a released milestone row whose section's own
scope has open ids as a `stale` statement, and a test pins it. The fixtures in
`subprojects/docket/tests/test_roadmap.py` ship milestones by bumping the
version without closing scope ids, so either the statement's wording survives
being printed across them or the fixtures record their scope closed - that is
the design question, and it is small.

## The design question, answered 2026-09-19: neither

The brief offered two ways out - word the statement so it survives being
printed across the fixtures, or make the fixtures close their scope ids. The
condition that removes the choice is the one the statement was always about:
**the version table has to record the release.** `stale_milestones` fires on a
row numbered at or below the version with *no* row in the table, so the
complement is a row that *has* one, and the fixtures carry no version table at
all (`ROADMAP` and its variants state no `Versioning decision` section) - only
`RECORDED_PORT_ROADMAP` does. Nothing else in the suite changed, and the new
fixture is that one with the port's own number added.

It is the right condition for its own reason rather than for the fixtures'. The
recorded row is what makes the case *silent*: while the number is missing,
`stale_milestones` already reports the row and `outstanding_roadmap_edits`
already names both edits at the hand-off. Firing on both states would print two
statements about one row and re-report a case that is already covered.

**Open is `ScopeStatus.outstanding` and nothing wider.** An id the store does
not hold is `unknown_ids`, which withholds completeness rather than
establishing outstanding work - that field's own reasoning - so it cannot carry
this statement's claim.

**Where it landed.** `stale_scopes` in
`subprojects/docket/src/docket/roadmap.py`, called from `wave` rather than from
`release_train`, which reads no store; `ReleaseTrain` grows a `released` field
so the version table is parsed once, and `released_versions` states the
`COMPLETED` rule for both readers. `format_wave`'s existing stale block and
`cmd_wave`'s non-zero exit needed no change.

**Measured against the live file before and after:** `bin/docket wave` prints
no stale statement and exits 0, so this fires on nothing today. The two open
scoped milestones are unreleased, and every released section's own scope is
closed - v0.4.0 at 17 of 17, v0.4.26 at 28 of 28, and v0.1.0, v0.2.0, v0.2.8,
v0.3.0 and the v0.4.27 baseline recording no scope ids at all. Forced by
discarding three of v0.4.26's closures, the statement reads: `v0.4.26 — the
interface moves to Qt (timeline line 308, section line 1438) is numbered
v0.4.26, which the version table records as released while 3 of 28 ids in its
own Required scope are still open (...)`.

**Two residuals captured rather than folded in:** `PL-SZJ2` (the same fault in a
section's frozen list, which `ahead` hides for a released row - reproduced) and
`PL-DK8Y` (the digest's one-line summary of `stale` describes three of its four
statements). `PL-YS9F` already holds the other half of the hand-off statement,
so the wording of the reached-and-passed pair was left alone.
