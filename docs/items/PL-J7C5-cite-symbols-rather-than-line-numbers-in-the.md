---
id: PL-J7C5
title: Cite symbols rather than line numbers in the contrast table's reasons
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-02
verify: uv run pytest tests/unit/test_contrast_check.py && ! grep -qE '[.]py:[0-9]' tools/contrast_check.py
---

**Problem.** Each `Requirement` in `tools/contrast_check.py`'s `REQUIREMENTS`
table names where its colour pair appears by file and line —
`(simulation_view.py:532, :556, :595)`. Nothing checks those numbers, and any
edit above them moves what they point at. Found while working PL-8M05: the
`INK`/`PANEL` and `MUTED`/`PANEL` entries were pointing about ninety lines off
their subjects, having drifted across several unrelated changes, and the drift
was invisible until someone followed one.

**Why it matters.** `.claude/rules/ui-color.md` makes the requirement table
the specification for what gets checked, and the reason string is how a
reviewer confirms the pair named is the pair on screen. A citation that points
at unrelated code costs that reviewer the lookup and, worse, can be read as
saying the pair appears somewhere it does not. Refreshing them by hand is the
same work again after the next edit.

**Where.** `tools/contrast_check.py`, the `reason` field of each `Requirement`
in `REQUIREMENTS`.

**Approach.** Cite the symbol instead — `_build_metric_panel`,
`_build_chart_panel`, `_build_metric_value` — which does not move when lines
above it do. `tools/doc_check.py` already decides the dangling-citation
question for paths and could be extended to assert each cited symbol still
exists in the cited module, which turns a drifting comment into a checked one
for a few lines of standard library. Whether that extension is worth building,
or whether symbol names alone are enough, is the judgment in this item.

**Done when.** No reason string in `REQUIREMENTS` names a line number, and
either the symbols it names are checked by `make check` or the item records
why they are not.

**The same drift is in `docs/items/`, with fresh evidence** (recorded
2026-09-02 while working `PL-VG7G`). `PL-YMY7` cited "lines 402, 472-486,
529-539, 572, 621, 650, 724, 795, 1162-1168" of `app/simulation_view.py` on
2026-08-25. Re-measured 2026-09-02 they were eleven statements at entirely
different lines, and `PL-8M05` moved them again the same day - twice stale
inside nine days, in an item whose whole finding *is* which lines those are.

So the scope worth considering is not only the requirement table: item bodies
cite line numbers routinely, nothing checks them, and a reader who trusts one
is sent to unrelated code. The approach above covers both without changing -
`tools/doc_check.py` already decides the dangling-citation question for paths
across the documentation tree, and asserting that a cited symbol still exists
in the cited module is the same kind of question asked of a different token.
Worth deciding as one mechanism rather than two, and worth noting that item
files are the larger surface.
