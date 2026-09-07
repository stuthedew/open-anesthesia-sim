---
id: PL-6G8T
title: _section_text reads a required heading quoted at a line break as the section itself, so a wrapped quotation above an empty real heading masks the empty one
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-07
---

**Problem.** _section_text reads a required heading quoted at a line break as the section itself, so a wrapped quotation above an empty real heading masks the empty one

**Why it matters.** `_section_text` judges the *first* line matching a required
marker, and a paragraph wrapped so that a quoted heading starts a line matches
it. `PL-JL2M` is the live instance: line 30 is the tail of a sentence quoting
`docket triage`'s own message, and it is what the checker reads as that item's
`**Done when.**` section rather than the real one at line 58.

It gives the right answer there, because both are non-empty and the check only
asks whether there is text. The hole is the ordering it cannot see: a wrapped
quotation *above* a genuinely empty real heading makes the empty section read
as filled, so `docket check` passes an item that has no closing condition. The
direction matters - this can only ever hide a gap, never invent one - which is
why it survived undetected while the opposite failure (`PL-D188`) was loud.

**Where.** `subprojects/docket/src/docket/checks.py`, `_section_text`. The
narrow fix is to require the marker to be followed by its closing `.**` and
end the line, or to ignore a match inside an indented or quoted block; the
first is cheap and the second is more faithful. Either needs a test for the
elaborated-heading case `**Why it matters, and why it is not new.**`, which
must keep matching.

**Done when.** A body whose only text under a required heading is a quotation
of that heading appearing earlier in a wrapped sentence is reported as empty.
