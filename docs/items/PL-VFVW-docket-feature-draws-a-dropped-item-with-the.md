---
id: PL-VFVW
title: docket feature draws a dropped item with the same empty checkbox as an open one, so counting the boxes disagrees with the 'N left' figure printed beside them
status: untriaged
added: 2026-09-05
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
