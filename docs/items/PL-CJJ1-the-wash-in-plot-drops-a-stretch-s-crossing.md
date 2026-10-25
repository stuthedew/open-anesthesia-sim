---
id: PL-CJJ1
title: The wash-in plot drops a stretch's crossing column whenever its ratio exceeds the 1.05 terminus ceiling, which is common at wide time bases because columns there are many seconds apart, so the trace stops in clear space below equilibrium with no terminus dot, the clipped-looking ending the extension exists to prevent
priority: P2
effort: S
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_frame.py, tests/integration/test_qt_chart.py
added: 2026-10-25
payoff: a finished wash-in no longer looks like a cut-off trace at wide time bases
verify: grep -q 'def test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium' tests/unit/test_chart_frame.py
---

**Problem.** `wash_in_stretches` (`src/anesthesia_sim/app/chart_frame.py`) extends a stretch by one crossing column only if that column's ratio is at most `WASH_IN_TERMINUS_CEILING = 1.05`. The ceiling was justified by the 1.00235 that one 0.1 s step reaches. Drawn columns are now spaced by the time base, up to minutes apart, so the first column past equilibrium is often well above 1.05. Reproduced on main: 60 min at the default dial, then dial 0 for 20 min. Under "Fit run" (2 h) the stretch ends at 0.98 with no terminus; on the 4 h base it ends at 0.87 with no terminus. After 10 min of wash-in, the 4 h base ends at 0.97 with no terminus.

**Why it matters.** A learner sees the curve stop short of the equilibrium line. That looks like a cut-off trace rather than a finished wash-in. The docstring now admits that columns can land on a later state, but the behaviour is unchanged. The only Qt test checks the 5-minute-after case that ends with a terminus. A fix could interpolate the crossing onto the line, or mark the ending some other way.

**Done when.** At every time base, a wash-in stretch that reached equilibrium ends on the equilibrium line or with a mark that says it ended there, never in clear space below it. `tests/unit/test_chart_frame.py` has `test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium`, which reproduces the 60-minute run on the 4 h base.

**Found by.** `PL-TBQS` reviewer replay on #578, findings r03 F3, r04 F3 and r05 F3, and `PL-ZWXD` entry 1. Checked against main on 2026-10-25 with `assemble_chart_frame` on a `SimulationController` run (`scripts/c_terminus.py`).
