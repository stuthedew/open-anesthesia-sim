---
id: PL-HKTB
title: The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture
priority: P2
effort: S
status: needs-decision
classes: ux
feature: presentation-safety
touches: tools/contrast_check.py, src/anesthesia_sim/app/theme.py
added: 2026-09-08
---

**Problem.** The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture

**Why it matters.** Every other colour pair in this interface carries a declared
contrast requirement that `tools/contrast_check.py` enforces, and this one
carries none - so the question of whether it is legible has never been asked,
rather than having been asked and answered "exempt". WCAG 2.2 does not require
a minimum for purely decorative furniture, and a chart gridline plausibly is
that; a divider separating two regions of content plausibly is not, since it
carries structure a reader uses. At 1.31:1 it is far below the 3:1 that would
make it a non-text contrast pass, so if it is ever load-bearing it is failing.

The value of settling it is that the answer gets written down either way. A
recorded exemption is as good an outcome as a darker grey, and better than a
colour nobody has a requirement for - which is how this one has survived.

**Decision needed.** Whether the gridline and divider grey is darkened to meet
3:1 as a non-text contrast requirement, or recorded in `tools/contrast_check.py`
as exempt furniture with the reason. Note the two may separate: a gridline is a
stronger candidate for exemption than a divider, and there is no need to give
them one answer.

**Sequencing.** `PL-L9RD` re-expresses `app/theme.py` for Qt and makes the
interface pass's visual decisions once. This is one of those decisions, so it
lands there unless it is answered sooner - deciding it twice is the thing that
item exists to prevent.

**Done when.** The grey either meets a declared requirement in
`tools/contrast_check.py` or is recorded there as exempt with the reasoning, and
`make check` reports it under whichever it is.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and it has lost the
pass that was going to pick it up.** The measurement reproduces: `GRIDLINE` is
still `#D9E2EC` at `src/anesthesia_sim/app/theme.py:519`, serving both the chart
gridlines (`qt_chart.py:316`, `:346`) and the panel divider
(`simulation_view.py:365`), and `contrast_ratio("#D9E2EC", "#FFFFFF")` returns
1.3092 - 1.31:1 as recorded, and 1.22:1 against `BACKGROUND`.
`tools/contrast_check.py` still names it nowhere: no `GRIDLINE` requirement,
`KNOWN_SHORTFALLS` empty at `:724`, and the report line reads 24 of 24.

Two corrections. The question has in fact been *argued* once -
`theme.py:505-513` carries "**It carries no `REQUIREMENTS` entry, and that is a
judgment rather than an omission.** Measured 1.31:1 on `PANEL` …" since
`PL-2CS8` on 2026-09-08 - so the item is about recording that judgment where
`make check` reports it, not about asking an unasked question; `theme.py:518`
says "`PL-HKTB` carries it" in the same breath. And the sequencing this brief
rests on has lapsed: `PL-L9RD` closed 2026-09-16 without redeciding the
visuals, pushing that pass to `v0.7.x`, so no scheduled work will absorb this
decision and it now has to be taken on its own.
