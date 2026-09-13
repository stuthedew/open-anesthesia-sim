---
id: PL-TP5M
title: PL-ZBRB's advisory names blocked-by to work around a checker that did not read it, and PL-KBD0's check now does
status: untriaged
added: 2026-09-13
---

**Problem.** PL-ZBRB's advisory names blocked-by to work around a checker that did not read it, and PL-KBD0's check now does

**Why it matters.** `PL-ZBRB`'s advisory reports an undeclared prose
prerequisite, and its message names both `status: blocked` and `blocked-by`
because, at the time, nothing read the second field - `plan.py` filtered on
status alone and `concurrency.py` was the only consumer of the edge. Its own
docstring says so. `PL-KBD0` closed that gap: `_ready_with_an_open_blocker` now
errors on a `ready` item declaring an open blocker, so a reader who acts on
`PL-ZBRB` and stops one field early is caught by a check rather than by a
sentence.

The message is therefore doing work a checker now does, and a reader who
follows it can be told the same thing twice in one run - once as an advisory
about the prose, once as an error about the field.

**Not urgent, and deliberately not folded into `PL-KBD0`.** Narrowing an
advisory's wording is a judgment about what a reader needs to be told, not a
consequence of the check landing, and `PL-KBD0` was already deciding one
question about how far a check should reach.

**Where.** `subprojects/docket/src/docket/checks.py`, `PL-ZBRB`'s advisory
message and its docstring's note about naming both fields.

**Decision needed.** Whether the advisory should now name only `blocked-by` -
leaving the status contradiction to the check that reads it - or keep naming
both because the two fire in different situations and a reader meeting the
advisory may not be about to trip the error. Check what the two messages
actually read like together on one item before deciding; it may be that they
compose fine and the honest answer is to change nothing but the docstring's
note.
