---
id: PL-9LXK
title: Nothing checks a prose claim about the tier or adoption of a stored value's source, though PL-1JDD made both machine-readable and three such claims went stale within a day
status: untriaged
added: 2026-09-07
---

**Problem.** Nothing checks a prose claim about the tier or adoption of a stored value's source, though PL-1JDD made both machine-readable and three such claims went stale within a day

**What is decidable here.** Since `PL-1JDD` every `sources` entry declares
`tier` and `adopted`, so a prose claim of the form "all twelve partition
coefficients are the Gas Man set", "all eleven physiologic parameters are the
Gas Man default patient", or "of the 29 rows, 26 are tier 3" is answerable by
reading the data files. `tools/doc_check.py` already has the mechanism one
field over: `PROSE_MARKER_RE` reads a `<!-- provenance: ... -->` marker and
holds the figure beside it to the value in the named JSON file. A marker
asserting a tier or an adoption count is the same design, and would fail the
same way - loudly, at `make check`, naming the file and the line.

**What must not be scripted.** Whether a citation declared `primary` really is
a primary measurement of the quantity, which `check_source_tiers` already
refuses to guess at for the reason `CLAUDE.md` gives; and whether the *rule*
stated in prose matches the practice, which is the judgment `PL-J302` exists
to have made rather than automated. The line is between counting declared
fields and reading a paper.

**The gate this has to pass before it is built.** `CLAUDE.md` asks whether the
work genuinely recurs. The evidence for is that three such claims went stale
inside a single day - the seven data-file restatements `PL-FJGY` swept,
`PL-J302`, and `PL-7KDC` - each found by a session reading the files rather
than by anything that runs. The evidence against is that a marker only checks
the claims somebody remembers to mark, so the next unmarked sentence drifts
exactly as these did, and an unmarked claim is the common case. Decide that
first: if the answer is that marking is what the author will not do, the item
is a different one - a check that reads the *counts* out of the data and
prints them, so a session updating the paragraph has the true numbers in front
of it without having to trust prose.

**Found.** `PL-X19T` (align the tier-3 absolute in the instruction files with
the practice), 2026-09-07, after two stale-count findings in one pass.
