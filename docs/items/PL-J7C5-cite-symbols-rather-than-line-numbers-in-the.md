---
id: PL-J7C5
title: Cite symbols rather than line numbers in the contrast table's reasons
status: untriaged
added: 2026-09-02
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
