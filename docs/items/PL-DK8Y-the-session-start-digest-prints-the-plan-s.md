---
id: PL-DK8Y
title: The session-start digest prints 'The plan's numbering is behind the project' for every Wave.stale statement, which is false for the section-that-no-timeline-row-bears one
priority: P2
effort: S
status: done
classes: defect
feature: timeline-arrangement
milestone: v0.5.4
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-19
closed: 2026-09-22
pr: 894
verify: grep -q 'def test_the_digest_does_not_call_a_rowless_section_a_numbering_lag' subprojects/docket/tests/test_roadmap.py
---

**Problem.** The session-start digest prints 'The plan's numbering is behind the project' for every Wave.stale statement, which is false for the section-that-no-timeline-row-bears one

**Found 2026-09-19 closing `PL-LN3T`.** `format_digest` in
`subprojects/docket/src/docket/render.py` appends " The plan's numbering is
behind the project - check `wave`." whenever `plan.stale` is non-empty.
`Wave.stale` carries four statement kinds, and the sentence describes three of
them: a milestone row numbered at or below the version with no release of that
number recorded, the same row at exactly the version, and (since `PL-LN3T`) a
row the version table records as released whose section's own scope is still
open. The fourth is `release_train`'s own "the <label> section has no timeline
row, so the plan does not say where it comes", where nothing is behind
anything - the plan simply does not place the section.

`format_wave` already has the sentence that covers all four, and it is the
heading over the same statements: "The plan and the project disagree, so the
beat above rests on a stale plan". The digest has room for the short form of
it.

**Why it matters.** The digest is one line per session and is the only place
most sessions meet this; a reader told the numbering is behind goes and looks
at the timeline's numbers, which is the wrong file for this case. Predates
`PL-LN3T`: the row-less-section statement has been in `stale` since
`release_train` was written.

**Done when.** The digest's sentence is true of every statement `Wave.stale`
carries, and the assertion in
`subprojects/docket/tests/test_roadmap.py::test_a_milestone_row_the_version_has_passed_without_a_release_is_reported`
that pins the current wording moves with it.
