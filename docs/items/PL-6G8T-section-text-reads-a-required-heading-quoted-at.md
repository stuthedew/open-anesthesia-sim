---
id: PL-6G8T
title: _section_text reads a required heading quoted at a line break as the section itself, so a wrapped quotation above an empty real heading masks the empty one
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-07
verify: grep -q 'def test_a_required_heading_quoted_mid_paragraph_is_not_the_section' subprojects/docket/tests/test_checks.py && uv run pytest -q subprojects/docket/tests/test_checks.py
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

**Measured 2026-09-26, for the project owner's decision.** `PL-GPJ7`'s Split named the route: a heading recognised only where a paragraph opens. Measured on the store first, as it asked, that rule refuses 63 headings that open no paragraph, 18 of them in 15 open items, and the README's own item-format example, which stacks its headings on consecutive lines, as do the test fixtures. **Recommended:** read every line that opens with a required heading's words, outside a fence, as that heading, and require text under each. A quotation can then no longer stand in for an empty heading below it, whatever the brief's layout, and no open item's reading changes. What it gives up: a quoted heading at a line start, with no real one anywhere, still reads as present, as it does today, and no open item has that shape. Put to the project owner 2026-09-26; the heading change waits for the answer, and the fence half of the same function landed with `PL-NQ3X`.

How each route builds, for the session that takes the answer. **Every heading** (recommended): `_section_text` reads the text under every `_heading` match in the fence-blanked copy and returns an empty string if any is empty, and `_stub_above_brief` asks of each empty one whether a `**Problem.**` heading follows it. **Paragraph rule**: `_heading` accepts a match only on the body's first line or under a blank one; the 18 headings, the README's item-format block and the docket test fixtures that stack headings (`BRIEF` in `test_checks.py`, `test_model.py` and `test_verify.py`, and bodies in `test_cli.py` and others) each get a blank line; and "brief is missing" names any line that opens with the heading inside a paragraph, since that reads as no heading at all.
