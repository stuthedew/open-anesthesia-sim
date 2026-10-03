---
id: PL-QVSN
title: plan.py's comment on the debt-gate step reason cites ROADMAP.md's cadence as shipping cleared gate work inside the gated milestone rather than the patch track, which PL-LPH9 reversed on 2026-09-27, so the comment's rationale now argues from a rule the roadmap no longer states
priority: P3
effort: S
status: done
classes: docs
feature: planning-cadence
milestone: v0.5.21
touches: subprojects/docket/src/docket/plan.py
added: 2026-09-27
closed: 2026-10-03
pr: 1284
payoff: the comment a maintainer checks before changing the debt-gate line argues from the rule the roadmap states now
verify: ! grep -qF 'has cleared gate work ship inside the milestone' subprojects/docket/src/docket/plan.py
---

**Problem.** plan.py's comment on the debt-gate step reason cites ROADMAP.md's cadence as shipping cleared gate work inside the gated milestone rather than the patch track, which PL-LPH9 reversed on 2026-09-27, so the comment's rationale now argues from a rule the roadmap no longer states

**Where, read 2026-09-27.** `subprojects/docket/src/docket/plan.py`, the
`if scope.clearing and scope.step_label:` branch that builds the "On the debt
gate recorded under ..." reason. Its comment says `ROADMAP.md` § "The cadence"
"has cleared gate work ship inside the milestone that recorded it rather than
in the patch track beneath it", and gives that as why the line must not say a
`v0.4.x` step clears the gate (`PL-TNB6`). `PL-LPH9` rewrote § "The cadence"
the same day to state the practice instead: a gate takes no version *of its
own*, and its work ships in patch releases on the preceding milestone's track
as it clears.

**What is and is not wrong.** The printed line still holds under the new
rule - the gate is recorded under the gated milestone and clears before that
milestone is implemented, whichever release carries each fix - so no output
changes. Only the comment's stated reason is stale: it argues from where gate
work ships, which is now the patch track, rather than from which milestone the
gate is recorded under, which is what the line actually names. Found by the
`PL-LPH9` build thread while sweeping for other statements of the old rule; not
fixed there because the file is outside that item's `touches`.

**Why it matters.** The comment is what a maintainer reads before changing that
line, and it argues from a rule `ROADMAP.md` no longer states; no output changes.

**Done when.** The comment argues from which milestone the gate is recorded
under, which is what the printed line names.

**Generator check.** An instance of `PL-G424`'s fact (a comment restating a
document's rule) in prose its 2026-09-19 decision left open (not a citation); found by `PL-LPH9`'s own sweep and filed
because `plan.py` was outside that item's `touches`. A one-off.

**Closed 2026-10-03.** The comment now argues from what the printed line
names: the milestone the gate is recorded under, and that the gate clears
before that milestone is implemented, "whichever release carries each fix".
It keeps `PL-TNB6`'s evidence that naming the step as clearing the gate handed
it the whole of Gate 1, of which 3 entries in 119 were its own, and no longer
restates where gate work ships, so a later change to § "The cadence" cannot
strand it the same way. No output changed.

Read and left: the comment opening the `IN_SCOPE` block above it (`PL-1J0P`)
and `Scope.step_label`'s docstring in `roadmap.py` both explain why the step can
differ from the anchor. Neither says where cleared gate work ships. The first
describes Gate 0's v0.3.0, the exception § "The cadence" still records, and
the second holds for every gate since `PL-LPH9`, so neither is this defect.
