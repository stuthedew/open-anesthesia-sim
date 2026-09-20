---
id: PL-82B0
title: doc_check's _declined_ids reads only the first Declined to Gate subsection, so a second one silently orphans the first's dispositions
priority: P2
effort: S
status: done
classes: defect
feature: gate-list-integrity
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-13
closed: 2026-09-20
pr: 774
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_second_declined_subsection_is_read' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _declined_ids reads only the first Declined to Gate subsection, so a second one silently orphans the first's dispositions
**Why it matters.** Verified 2026-09-13: `_declined_ids` takes the *first*
`### Declined to Gate ...` heading at or after the gate line - a bare
`next(...)`, with no accumulation - and `ROADMAP.md` holds exactly one such
subsection today, at line 2004. So the defect is latent rather than live, and
latent is the shape that costs most here: the second subsection will be written
by somebody recording a deferral, who has no reason to suspect that writing it
makes the first one's ids stop being excluded from the gate's counts. A gate
count that is quietly wrong is read as the project's own statement of what it
owes, and `bin/docket wave` prints it in every session digest.

**Done when.** `_declined_ids` reads every `### Declined to Gate ...`
subsection between the gate heading and the section that ends it, a test in
`tests/unit/test_doc_check.py` pins the two-subsection case, and the docstring
states the rule it now implements.
