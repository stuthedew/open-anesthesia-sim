---
id: PL-BNMZ
title: With isoflurane's MAC at 1.17%, the concentration chart's percent axis is labelled 0.585, 1.17, 1.755, 2.34, 2.925 and 3.51 %, three-decimal labels on gridlines that fall on no round percentage
priority: P2
effort: S
status: done
classes: ux, safety
feature: chart-readout
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/qt_chart.py, docs/INTERFACE.md, tests/unit/test_chart_frame.py, tests/integration/test_qt_chart.py
added: 2026-11-22
closed: 2026-11-22
pr: 2270
tests: tests/unit/test_chart_frame.py::test_each_axis_is_labelled_at_round_values_of_its_own_unit, tests/integration/test_qt_chart.py::test_the_mac_axis_labels_every_gridline_and_the_percent_axis_is_round
---

**Problem.** The concentration chart draws a gridline every half MAC
(`CHART_GRID_INTERVAL_MAC` in `app/formatting.py`) up to 3 MAC, and
`chart_frame.percent_axis_ticks` labels each gridline on the percent axis with
its exact value. With the MAC at age 40 that `PL-LBVN` stores, the labels are,
computed on branch `work/pl-lbvn-replay` on 2026-11-22:

- sevoflurane (1.80%): 0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4
- isoflurane (1.17%): 0, 0.585, 1.17, 1.755, 2.34, 2.925, 3.51
- desflurane (6.6%): 0, 3.3, 6.6, 9.9, 13.2, 16.5, 19.8

At the old 1.2% MAC, isoflurane's labels were 0.6, 1.2, 1.8 and so on.

**What a learner sees.** On an isoflurane run, the percent axis carries
three-decimal labels, 0.585, 1.755 and 2.925, beside readouts that show two
decimals. The labels imply a precision the readouts do not claim, and they are
awkward to read a trace against: a learner who wants to know when the alveolar
trace passes 1% or 2% has no gridline there and must interpolate between odd
numbers. The MAC axis on the other side is unaffected, because it is labelled
in round MAC multiples, which is its purpose.

**What a fix has to weigh.** The present rule puts the gridlines on round MAC
values so that both axes name the same rules. Moving the percent labels to
round percentages would give the percent axis its own rules, or unlabelled
gridlines. `docs/INTERFACE.md` § "MAC multiples as a display unit" states the
current rule, in its paragraphs on the 3 ×MAC ceiling and the half-MAC gridline, and the `percent_axis_ticks`
docstring already mentions a half-MAC of 0.575% as a label it would print
whole. This is a display decision for the project owner, with the
false-precision standard in `CLAUDE.md` on one side and one ruler for both
axes on the other.

Found while replaying `PL-LBVN` (the MAC at age 40); not fixed there.

**Why it matters.** Three-decimal axis labels beside two-decimal readouts imply
a precision the model does not claim, which `CLAUDE.md`'s false-precision
standard refuses, and they leave a learner no gridline at 1% or 2% to read a
trace against.

**Done when.** The percent axis is labelled at round percentages for every
agent and every chart top, with no more decimals than the step needs, and
`docs/INTERFACE.md` states the rule.

**Generator check.** A one-off: the half-MAC gridline labelled exactly was
right while every MAC was a round number, and `PL-LBVN`'s age-40 MAC of 1.17%
exposed it. No other item misreads the fact that a percent label is a value
the learner reads against the readouts.


**Done 2026-11-22**, in `PL-K1VH`'s pull request. The question was put to the coordinator with the research below, and it answered that the research gives a clear answer and the labelling is the session's to decide (coordinator, 2026-11-22 23:40Z). The left axis is now labelled at round percentages, at the finest of 1, 2 and 5 times a power of ten that gives no more intervals than the MAC axis (`percent_axis_ticks`, `PERCENT_AXIS_STEP_LADDER` in `app/chart_frame.py`). The gridlines stand at the MAC axis's labels. At 3 MAC: sevoflurane 0-5%, isoflurane 0-3%, desflurane 0, 5, 10, 15%. The tick marks are the axis's own, in the axis grey that the existing exemption for the axis lines covers, since the labels carry the scale.

Sources, all read 2026-11-22: Datawrapper, "Dual-axis charts: a guide" (https://www.datawrapper.de/blog/dual-axis-charts-guide), raw page: "the safest use case for dual-axis charts: Showing the same measure in two units, like °C and °F"; Datawrapper, "Dual-axis charts" (https://www.datawrapper.de/blog/dual-axis-charts), raw page: "By default, the two vertical grids have independent tick intervals"; Talbot, Lin and Hanrahan, "An Extension of Wilkinson's Algorithm for Positioning Tick Labels on Axes", IEEE InfoVis 2010, full text (https://www.tableau.com/sites/default/files/2023-01/infovis2010-talbot-tickmarks.pdf), section 2: nice numbers are much easier to work with in mental estimation (their ref 6, Reys et al. 1982), and Heckbert's Q = {1, 2, 5}. Isenberg et al. 2011 was found but not read (the link returned a home page); it is about broken-scale charts, not two units.
