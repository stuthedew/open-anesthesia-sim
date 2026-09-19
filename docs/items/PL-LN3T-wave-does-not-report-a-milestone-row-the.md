---
id: PL-LN3T
title: wave does not report a milestone row the version has released whose section's Required scope is still open, so a patch cut at a milestone's own number leaves the plan stepped past it once the hand-off has scrolled by
status: untriaged
feature: timeline-arrangement
added: 2026-09-19
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
