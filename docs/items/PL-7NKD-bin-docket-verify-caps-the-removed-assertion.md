---
id: PL-7NKD
title: bin/docket verify caps the removed-assertion evidence at five lines with nothing saying so, so a count of six prints five and the reader cannot tell which line is missing
status: untriaged
feature: verify-assertion-evidence
added: 2026-09-20
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
