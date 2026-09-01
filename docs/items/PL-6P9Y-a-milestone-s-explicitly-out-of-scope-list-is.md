---
id: PL-6P9Y
title: A milestone's Explicitly out of scope list is read as silence, so an id it names is unplaced where it could be reported out of scope
status: untriaged
added: 2026-09-01
---

**Problem.** `PL-HDY6` made a milestone section place an id only from the two
structures that record membership - its frozen list's entries, and its
`Required scope`. Every other mention is now silence. That is the right answer
for a mention the reader cannot interpret, but one of them is not a mention at
all: `### Explicitly out of scope for vX.Y.Z` is a heading whose whole meaning
is exclusion, and the ids under it are as decidable as the ids under `Required
scope`.

Measured 2026-09-01, one id sits there: v0.4.0's out-of-scope list names
`PL-Z7LY` (horizontal panning of the chart window). `Scope.placement` answers
`unplaced` for it, so `docket next` ranks it between in-scope and out-of-scope
work and prints no marking, where the roadmap has actually made a decision
about it.

**Why it matters.** Small, and an improvement to correct behaviour rather than
a defect in it - which is why this is queue work rather than a v0.2.8 gate
entry under that release's scope test. The value is that the section's own
decision reaches the ranking: an id a milestone has explicitly ruled out
should not be offered ahead of work nobody has ruled on.

**Where.** `subprojects/docket/src/docket/roadmap.py` - `_scope_ids` and the
subsection tracking in `parse_milestones`, then `Scope`, which today has three
answers and would need the anchor's own exclusions to be one of them rather
than folded into `out-of-scope` (whose reason string says "appears in
`<milestone>`'s section, which the current step has not reached", and that is
not what an exclusion means).

**Done when.** An id under a milestone's `Explicitly out of scope` heading is
reported as excluded by that milestone rather than as unplaced, with a reason
string that says so, and a test covers `PL-Z7LY`.
