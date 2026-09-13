---
id: PL-VFVW
title: docket feature draws a dropped item with the same empty checkbox as an open one, so counting the boxes disagrees with the 'N left' figure printed beside them
priority: P3
effort: S
status: done
classes: defect, ux
milestone: v0.4.21
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-05
closed: 2026-09-13
pr: 542
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_feature_draws_a_dropped_entry_distinctly_from_an_open_one' subprojects/docket/tests/test_cli.py
---

**Problem.** `bin/docket feature teachable-case` printed `18/28 done (9 left)`
above a list in which **ten** entries carried an empty `[ ]`. The tenth is
`PL-TJJY`, which is `dropped` — closed, resolved, and correctly excluded from
the count, but drawn identically to the nine that are genuinely open.

**Why it matters.** The count and the boxes are two renderings of one fact and
they disagree where a reader can see both at once, which is the same defect
class the lane line was fixed for (`subprojects/docket/README.md`, "two lines
in one block ranked by different rules contradict each other"). A reader
counting boxes to sanity-check the number gets the wrong answer and has no way
to tell which of the two is lying.

**Where.** `subprojects/docket/src/docket/render.py`, the feature listing's
checkbox: it tests `status == "done"` where the count tests `is_open`, and
`dropped` is in neither.

**Done when.** A dropped entry is visually distinct from an open one - `[-]`,
or the id struck through, or a trailing `(dropped)` - and counting the marks
reproduces the figure printed above them.

**Worked.** The checkbox was in `subprojects/docket/src/docket/cli.py`
(`cmd_feature`), not in `render.py` as **Where.** above says - and
`cmd_milestone` carried the identical line, counting by the same two rules
and drawing the same box. Both now call `render.progress_mark`, which owns
the three marks: `[x]` for the `done` numerator, `[ ]` for what `is_open`
counts as left, `[-]` for a `dropped` entry that is in neither. Counting
reproduces both figures and the line total is the denominator.
