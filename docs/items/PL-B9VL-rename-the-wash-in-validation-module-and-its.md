---
id: PL-B9VL
title: Rename the wash-in validation module and its MODEL.md section now that both cover elimination too
priority: P2
effort: S
status: done
closed: 2026-09-13
classes: docs, refactor
feature: numerical-domain
touches: tests/reference/test_published_wash_in_and_elimination.py, docs/MODEL.md, docs/WORKING_NOTES.md, README.md, ROADMAP.md, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_wash_in.py, docs/items/
added: 2026-09-06
verify: python3 tools/doc_check.py check && ! grep -q 'Published wash-in and elimination validation test' docs/MODEL.md
---

**Problem.** `tests/reference/test_published_wash_in_and_elimination.py` and `docs/MODEL.md`
§ "Published wash-in and elimination validation test" both now carry two comparisons in
opposite directions: `F_A/F_I` at 30 minutes of wash-in, and `F_A/F_A0` at five
minutes of elimination. Both names describe only the first. The module docstring
and the section both say so in their opening lines, which is the stopgap rather
than the fix.

**Why it matters.** A reader looking for what this repository checks about
washout has no reason to open a file named for wash-in, so the one gate in that
direction is the hardest one to find. It is documentation staleness of the kind
`CLAUDE.md` treats as a safety issue rather than tidiness.

**Where.** The heading is cited from five places, and `tools/doc_check.py`
checks that cited section headings resolve, so the rename and its citations move
together or the check fails:

- `docs/MODEL.md` line ~1737 (the heading itself)
- `docs/MODEL.md` § "Supported input ranges"
- `docs/MODEL.md` § "F_A/F_I as a displayed ratio"
- `docs/MODEL.md` § "Release gate"
- `src/anesthesia_sim/app/formatting.py`
- `tests/unit/test_wash_in.py`

**Done when.** The module file and the section heading name both directions,
every citation above resolves, and `make check` passes.

**Closed 2026-09-13.** The module is
`tests/reference/test_published_wash_in_and_elimination.py` and the section is
§ "Published wash-in and elimination validation test". "Elimination" rather
than "washout" because that is the word the module docstring, the section body
and the Yasuda abstracts already use for $`F_A/F_{A0}`$; introducing a second
term for one quantity is the defect this item is about.

The count in **Where** was low. It named five citation sites; there are
**twenty-one files**, because the module *path* is cited as widely as the
section heading is - `README.md`, `ROADMAP.md`, `docs/WORKING_NOTES.md` and
`src/anesthesia_sim/core/supported_ranges.py` all carry one, and fourteen item
files do. `tools/doc_check.py` checks the queue and source docstrings as well
as the documentation, so every one of them had to move together or the check
fails; that is the mechanism the item predicted, operating over a wider surface
than it counted.

One citation survived the mechanical sweep and `doc_check` caught it:
`docs/MODEL.md:4519` wrapped the quoted heading across a line break, so no
single-line pattern matched it. That is `PL-6G8T`'s wrapped-quotation shape
arriving in a different check, and it is the argument for the check existing.

The section's own stopgap paragraph went with the rename. It read "although its
heading names only the first - the name is kept because five other passages
cite it, and a citation that no longer resolves is a worse defect than a
heading that under-describes", which is a true statement about the old name and
a misleading one about this heading.
