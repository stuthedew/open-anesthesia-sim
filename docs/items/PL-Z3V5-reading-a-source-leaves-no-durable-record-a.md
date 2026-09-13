---
id: PL-Z3V5
title: Reading a source leaves no durable record a later session can use: the extracted values, units and page locators are not written back to the public repository, so the same PDF is re-read per session
status: untriaged
feature: provenance
added: 2026-09-13
---

**Problem.** When a session reads an owner-supplied full text, what survives is
prose in the item that prompted the reading. The values taken, their units,
what was measured, in whom, and where in the document they sit are not recorded
anywhere a later session would look. So the next session needing the same
source re-reads it, and the session after that re-reads it again.

**Why it matters.** `PL-7Y27` closed by marking three vaporizer figures in
`docs/MODEL.md` "owner-attested rather than checkable" — the sources had been
supplied and read in full on 2026-09-06, and what neither the item nor the
document could supply was a later session's ability to check one. That is this
problem, already paid once and recorded as a limitation rather than as a gap to
close.

It also sets the cost of `PL-5NR5`. If reading writes nothing back, a private
corpus is consulted once per session forever; if it does, the corpus is
consulted once per source and the extraction serves every session after.
`CLAUDE.md` § "Prefer deterministic tooling over repeated model work" is the
same argument applied to literature: work moved out of the model is paid for
once, work left to it is re-derived at full context in every session.

**Why this half can live in the public repository.** Facts are not
copyrightable in the United States — *Feist Publications, Inc. v. Rural
Telephone Service Co.*, 499 U.S. 340 (1991), holding at 344–45 that "facts are
not copyrightable" and that copyright in a factual compilation is "thin",
protecting only original selection and arrangement. A note recording that a
named table reports a given coefficient, with the page it sits on, is therefore
publishable where the PDF is not. Short quotation for scholarly commentary is
separately supported by 17 U.S.C. § 107. What this does *not* license is
reproducing a table wholesale in its published arrangement, which is both the
riskier act and the unnecessary one.

This is what `docs/references/README.md` already does for citations — "the
citations were always the part designed to survive such a removal" — extended
from the citation to the numbers taken from it.

**The shape of an answer, not yet a decision.** One note per source under
`docs/references/`, written when the source is first read, recording for each
value taken: the quantity and its units, the locator (table, figure or page),
what was measured and in what population, and whether the project adopted it.
`docs/MODEL.md` § "Source hierarchy" already fixes the vocabulary for the last
of those, so the note records rather than invents it.

**Decision needed.** Whether reading an owner-supplied source obliges writing
an extraction note, and whether that obligation belongs in
`.claude/rules/citing-sources.md` beside the routes, or in
`docs/references/README.md` beside the redistribution rule. `PL-XJ5P` is
deciding the surrounding question and touches both files.

## Approved by the project owner, 2026-09-13

The obligation is approved in principle: reading an owner-supplied source writes
its numbers and locators back into the public repository. Not implemented here —
both candidate homes, `.claude/rules/citing-sources.md` and
`docs/references/README.md`, are in `PL-XJ5P`'s `touches` and `PL-XJ5P` is in
flight on `origin/claude/lucid-mendel-6kavwt`. It lands with that item's decision.

**A first target exists rather than a hypothetical one.** The corpus now holds
Yasuda et al. 1991, whose five-minute elimination vectors
`tests/reference/test_published_wash_in_and_elimination.py` already depends on.
An extraction note for that paper would record what the test file currently
asserts without a holdable source: the two vectors, their SDs, n = 7 volunteers,
the FA/FI values at 30 min, and the pages each sits on. That is the smallest
worked example of the convention and it is owed to a file already in `tests/`.
