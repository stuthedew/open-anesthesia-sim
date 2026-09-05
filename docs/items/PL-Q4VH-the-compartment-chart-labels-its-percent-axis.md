---
id: PL-Q4VH
title: The compartment chart labels its percent axis at a different interval from the gridlines it rules
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-04
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_percent_axis_labels_the_values_it_rules' tests/unit/test_simulation_view.py
---

**Problem.** The compartment chart labels its percent axis at a different
interval from the gridlines it rules

**Observed 2026-09-04, while landing `PL-ZRSP` (the F_A/F_I trace).** The
compartment chart rules horizontal gridlines every 2 percentage points
(`horizontal_grid_lines=fch.ChartGridLines(interval=2, ...)` in
`app/simulation_view.py`) but leaves the left axis to label itself, which it
does at every 1. The ruling and the labelling therefore describe two different
scales on one axis. It is milder than it sounds today - a label happens to sit
at every gridline as well as between them - so a value read off a gridline is
still read against a correct label. It becomes wrong the moment either
interval changes, and it is the same defect the wash-in axis had in its first
draft: rules at 0.25 and labels at 0.2, where the chart *did* leave gridlines
unlabelled. That one is fixed by giving the axis explicit `labels` and a
`label_spacing` equal to the gridline interval, which is the fix here too.

**Why it matters.** `CLAUDE.md`'s safety-critical standard counts a plot whose
axis can be misread as a defect rather than a cosmetic issue: a reader taking a
concentration off the nearest rule is taking it off a scale nobody stated.

**Done when.** The compartment chart's percent axis is labelled at exactly the
values it rules, and a test holds the two together so they cannot drift.

**Rendered evidence, 2026-09-05 (while landing `PL-SSBP`).** Driving the real
app in a browser shows a second symptom of the same root cause: leaving the
axis to label itself also leaves `label_size` at its 22 px default, which is
narrower than the labels the axis chooses. Every half-percent label wraps onto
two lines, so the axis reads `6`, `5.`, `5`, `5`, `4.`, `5` down its length
rather than `6`, `5.5`, `5`, `4.5`. It is not a regression - the same wrapping
is on `origin/main` - and the fix is the one this item already names: explicit
`labels`, `label_spacing` equal to the gridline interval, and a `label_size`
wide enough for what those labels say. Screenshots are not kept; re-run the
app to see it.
