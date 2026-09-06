---
id: PL-B9VL
title: Rename the wash-in validation module and its MODEL.md section now that both cover elimination too
priority: P2
effort: S
status: ready
classes: docs, refactor
feature: numerical-domain
touches: tests/reference/test_published_wash_in.py, docs/MODEL.md, src/anesthesia_sim/app/formatting.py, tests/unit/test_wash_in.py
added: 2026-09-06
verify: python3 tools/doc_check.py check && ! grep -q 'Published wash-in validation test' docs/MODEL.md
---

**Problem.** `tests/reference/test_published_wash_in.py` and `docs/MODEL.md`
§ "Published wash-in validation test" both now carry two comparisons in
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
