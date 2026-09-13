---
id: PL-Z0G0
title: doc_check candidates attributes a hit to the alphabetically first matching term, so a line matched through render.py prints as (render)
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.15
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-05
closed: 2026-09-13
pr: 506
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_candidate_line_is_labelled_with_the_most_specific_term' tests/unit/test_doc_check.py
---

**Problem.** `format_candidates` records one entry per documentation line -
`hits.setdefault((doc, number), token)` - so the line keeps whichever term
reached it first, and terms are walked in sorted order. A changed
`render.py` contributes both `render` and `render.py`, `render` sorts first,
and a line reading ``- PL-WFJ9 (S) `render.py` reads ...`` is therefore
printed as `(render)`.

**Observed 2026-09-05** while closing `PL-B2NS`, on `PL-YHD3`'s diff:
`ROADMAP.md:659` and `ROADMAP.md:775` are both about `render.py` and both
print `(render)`.

**Why it matters.** Small. The line is a genuine candidate either way and the
reader opens it regardless; the label just points at the less specific of the
two reasons it was chosen. It matters slightly more since `PL-B2NS`, because
the label now also tells the reader whether the term was one the tool narrowed
to code context.

**Where.** `tools/doc_check.py`, `format_candidates`.

**Done when.** A line matched by more than one of a file's terms is labelled
with the most specific one - longest term wins, or the distinctive term wins
over the ordinary-word one.
