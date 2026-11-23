---
id: PL-CJJ1
title: The wash-in plot drops a stretch's crossing column whenever its ratio exceeds the 1.05 terminus ceiling, which is common at wide time bases because columns there are many seconds apart, so the trace stops in clear space below equilibrium with no terminus dot, the clipped-looking ending the extension exists to prevent
priority: P2
effort: S
status: done
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_frame.py, tests/integration/test_qt_chart.py
added: 2026-10-25
closed: 2026-11-23
pr: 2265
payoff: a finished wash-in no longer looks like a cut-off trace at wide time bases
tests: tests/unit/test_chart_frame.py::test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium, tests/unit/test_chart_time_base.py::test_the_second_a_wash_in_stretch_leaves_the_domain_is_drawn
---

**Problem.** `wash_in_stretches` (`src/anesthesia_sim/app/chart_frame.py`) extends a stretch by one crossing column only if that column's ratio is at most `WASH_IN_TERMINUS_CEILING = 1.05`. The ceiling was justified by the 1.00235 that one 0.1 s step reaches. Drawn columns are now spaced by the time base, up to minutes apart, so the first column past equilibrium is often well above 1.05. Reproduced on main: 60 min at the default dial, then dial 0 for 20 min. Under "Fit run" (2 h) the stretch ends at 0.98 with no terminus; on the 4 h base it ends at 0.87 with no terminus. After 10 min of wash-in, the 4 h base ends at 0.97 with no terminus.

**Why it matters.** A learner sees the curve stop short of the equilibrium line. That looks like a cut-off trace rather than a finished wash-in. The docstring now admits that columns can land on a later state, but the behaviour is unchanged. The only Qt test checks the 5-minute-after case that ends with a terminus. A fix could interpolate the crossing onto the line, or mark the ending some other way.

**Done when.** At every time base, a wash-in stretch that reached equilibrium ends on the equilibrium line or with a mark that says it ended there, never in clear space below it. `tests/unit/test_chart_frame.py` has `test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium`, which reproduces the 60-minute run on the 4 h base.

**Found by.** `PL-TBQS` reviewer replay on #578, findings r03 F3, r04 F3 and r05 F3, and `PL-ZWXD` entry 1. Checked against main on 2026-10-25 with `assemble_chart_frame` on a `SimulationController` run (`scripts/c_terminus.py`).

**Checked 2026-11-21**, by `PL-5FMC` (the check of `docs/INTERFACE.md` against the code), at `2452b9b4e`. One of the three examples above no longer reproduces. A 10-minute wash-in followed by the dial at 0, drawn on a 4-hour time base at 900 px, ends its stretch at a ratio of 0.97 with no terminus dot. The other two examples were not rerun. Rerun all three before building, and say in the brief which still fail.

**Checked 2026-11-22** against `d4e8200`: still applies in the code. `WASH_IN_TERMINUS_CEILING` is still 1.05 in `src/anesthesia_sim/app/chart_frame.py`. `wash_in_stretches` still leaves out a crossing column above the ceiling, so the stretch ends where it would without one. Since #2180 the docstring gives the largest one-step crossing as 1.0281 at the 1 s step, not 1.00235, but it adds that a drawn column can land on a later state, so the brief's fault remains. No test named in `verify:` exists. The note of 2026-11-21 above reports a 0.97 ending with no terminus, which is this fault and not a fix. The other two examples were not run again here.

**Done 2026-11-23.** The three examples were run again on main first. At 900 px they no longer end below the line, but the same run fails at wide time bases and narrow plots: 17 of 66 pairs of time base and plot width from 300 px to 1 600 px, and 23 of 162 stretches in a wider sweep. The fix draws the stored second at which the ratio crosses equilibrium, so the stretch's last point is a real state on the far side of the line. Nothing is interpolated. `chart_time_base.wash_in_crossing_seconds` chooses those seconds and `controller._with_extremes` adds them to each drawn and predicted window. After the fix, no pair and no stretch in either sweep ends below the line. `test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium` reproduces the brief's run on the 4 h and 12 h bases, and fails without the controller change. Documents checked: `docs/INTERFACE.md` (§ "What the chart draws", updated), `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/ARCHITECTURE.md` (neither describes the drawn columns' choice), and the docstrings of `wash_in_stretches` and `_with_extremes` (updated).
