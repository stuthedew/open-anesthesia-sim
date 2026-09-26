---
id: PL-7NKD
title: bin/docket verify caps the removed-assertion evidence at five lines with nothing saying so, so a count of six prints five and the reader cannot tell which line is missing
priority: P3
effort: S
status: done
classes: defect, infra
feature: verify-assertion-evidence
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-20
closed: 2026-09-25
payoff: a reader asked to account for every removed assertion can see every one of them, instead of reading a count of six above five lines
verify: grep -q 'def test_the_removed_assertion_evidence_names_the_lines_it_omits' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify caps the removed-assertion evidence at five lines with nothing saying so, so a count of six prints five and the reader cannot tell which line is missing

**Found 2026-09-20 on `PL-0RZ0`'s branch**, beside `PL-087W`.

`verify.py` builds the evidence as `tuple(dropped[:5])` while `detail` is
`f"{len(dropped)} line(s)"`, so a branch with six dropped assertions prints
`6 line(s)` above five of them and names neither the cap nor the line it left
out. Reading the missing one back took a `git show` per commit.

**Why it matters.** This project's own rule for a bounded display is that the
bound is shown rather than hidden - `docs/MODEL.md` § "The control-input
timeline", "Bounds are displayed, not silent", which is why
`ChartFrame.undrawn_compartments` and `undrawn_control_marks` exist. A refusal
block is exactly where that applies: the reader is being asked to account for
each line, and one of them is not on the page.

**The cheapest fix is a line saying so**, in the shape the store already uses
elsewhere - `... and 1 more` - rather than raising the cap, which trades one
unreadable block for another. The same `[:5]` is on `suppressed` at the check
above it and on the `folded` tuple beside it; whichever way this goes, the
three want to agree.

**Where.** `subprojects/docket/src/docket/verify.py`, the `Check` construction
for `no existing assertion removed` and the `no suppression added` check above
it.

**Done when.** A refusal block whose evidence is capped says so in the shape
the store already uses - `... and N more` - so the count above the block and
the lines under it can be reconciled by a reader, with the `suppressed` and
`folded` caps beside it agreeing; and a test under
`subprojects/docket/tests/test_verify.py` drives a branch with six dropped
assertions and holds that the block accounts for all six.

**The code moved under the brief, and the finding holds.** `verify.py` no
longer spells the cap `tuple(dropped[:5])`. Read 2026-09-20 it is
`tuple(line for line in dropped if line not in named)[:5]`, with `folded[:5]`
beside it and `detail = f"{len(dropped)} line(s)"` above - so the count and the
evidence still come from different places and the block still names neither the
cap nor the line it left out. `suppressed[:5]`, on the `no suppression added`
check, is the sibling the fix should bring into agreement, and the
`replaced[:3]` and `swapped[:3]` caps are a third shape to decide about rather
than assume.

**Worked.** The code had moved again since the note above: `PL-4W2L`'s
statement-altitude reading already ends a function's list with `and N more
that left` or `that arrived`, and its function list with `and N more
function(s)`, so on a file the parser reads six dropped assertions were already
accounted for. Two lists still stopped at five in silence: the lines of a file
read line by line, under `no existing assertion removed`, and `no suppression
added`'s. Both now go through one helper, `_capped`, which prints the first
`SHOWN_FUNCTIONS` and then `and N more line(s)`, so the two agree by
construction; I widened that constant's comment to say it also caps a check
that reads lines. The `folded` list is no longer capped at all, since
`declared_lines` prints every fold, and the `replaced[:3]` and `swapped[:3]`
caps no longer exist, so neither had anything to agree with. The test is
parametrized over both readings: the `parsed` case pins behaviour that already
held and has no other test, while `line_by_line` and the separate
`test_the_suppression_evidence_names_the_lines_it_omits` fail with the helper
reverted.
