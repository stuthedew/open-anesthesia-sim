---
id: PL-S0HP
title: With PL-571L's half-line top margin, re-measure whether a hover box with every trace fits a concentration plot at its least height, under the container's font and CI's
priority: P2
effort: S
status: done
classes: ux
feature: chart-readout
touches: tests/integration/test_qt_chart.py, docs/INTERFACE.md
added: 2026-11-22
closed: 2026-11-23
pr: 2274
tests: tests/integration/test_qt_chart.py::test_the_tallest_hover_box_fits_the_plot_at_its_least_height
---

**Problem.** With PL-571L's half-line top margin, re-measure whether a hover box with every trace fits a concentration plot at its least height, under the container's font and CI's

**Found on 2026-11-22** by the blind review of #2225, as an optional finding. PL-571L gives the plot a top margin of half a font line, so the top tick label is drawn whole. That margin comes out of the data area, and the plot's least height (`theme.CHART_LEAST_HEIGHT`, 160 px) did not grow with it.

**What was measured.** Offscreen, in the container's font, the concentration plot's data area at its least height is 113 px with the margin. PL-YJ7N measured it at about 120 px before, and measured a box reporting several traces at up to 113 px. The tallest box over the Induction dashboard's 222 test points was 53 px. So the tallest box PL-YJ7N measured now just fits, and a taller one, or CI's font (DejaVu Sans), could leave the box's bottom line clipped by the plot. That line is a value the learner is reading.

**Done when.** The tallest box the concentration plot can show (every trace of two compared runs) is measured against the data area at the least height, under both fonts. Where it does not fit, the least height grows by the margin, and the 1366 by 768 layouts are checked again.

**Generator check.** A one-off. `PL-571L` took height from the plot without a
test of the box at the least height, and this item adds that test.

**Done 2026-11-23.** Measured on `e75ec4d3` with the new test
`test_the_tallest_hover_box_fits_the_plot_at_its_least_height` in
`tests/integration/test_qt_chart.py`. The tallest box is the agent and all six
compartments, at the start of a run; two compared runs draw at most two
compartments each, so their box is shorter, and the test asserts that. At
`theme.CHART_LEAST_HEIGHT` the box is 113.0 px against a 113.1 px plot in the
container's font, and 106.0 px against 114.9 px in DejaVu Sans. It fits in
both, so the least height did not grow, and the 1366 by 768 layouts are
unchanged. The test runs in both fonts, so a change that cuts the box off
fails. With a 13-pixel font the box is 120.0 px and the plot 112.3 px, so the
box does not fit there; that is filed as `PL-HXSD`, and `docs/INTERFACE.md`
§ "When more than one trace is within reach" says so beside the new sentence.
Files checked: `docs/INTERFACE.md` § "When more than one trace is within
reach", `docs/VERIFICATION.md` (no hover
box height), `src/anesthesia_sim/app/theme.py` (the `CHART_LEAST_HEIGHT`
comment names no box).
