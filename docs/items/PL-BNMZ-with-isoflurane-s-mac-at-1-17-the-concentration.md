---
id: PL-BNMZ
title: With isoflurane's MAC at 1.17%, the concentration chart's percent axis is labelled 0.585, 1.17, 1.755, 2.34, 2.925 and 3.51 %, three-decimal labels on gridlines that fall on no round percentage
status: untriaged
feature: chart-readout
touches: src/anesthesia_sim/app/chart_frame.py, docs/INTERFACE.md
added: 2026-11-22
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
