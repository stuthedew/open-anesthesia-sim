---
id: PL-49D5
title: With ventilation stopped and the dial lowered, the F_A/F_I trace climbs toward 1 because the circuit washes out, and the plot draws that climb as wash-in ending at equilibrium
priority: P1
effort: S
status: ready
classes: defect, safety
feature: interface-design-review
touches: src/anesthesia_sim/app/wash_in.py, src/anesthesia_sim/app/dashboard_frame.py, docs/INTERFACE.md, tests/unit/test_wash_in.py, tests/unit/test_dashboard_frame.py
added: 2026-11-23
filed-pr: 2305
payoff: a learner who stops ventilation is not shown the F_A/F_I trace rising as if the alveoli were filling
---

**Problem.** Rule 2 in `src/anesthesia_sim/app/wash_in.py`'s module docstring calls every ratio at or below 1 "the uptake regime", and the plot draws it as the textbook wash-in curve. With alveolar ventilation at zero that is not so. In `tests/unit/test_dashboard_frame.py::test_a_ratio_above_one_with_ventilation_stopped_names_no_elimination`, ventilation stops at 600 s of 4% sevoflurane and the dial drops to 0.5%. The ratio then climbs toward 1 because fresh gas washes the circuit out, not because the alveoli fill, and the plot draws that climb as wash-in ending on the equilibrium line.

**Found by** the first blind review pass of `PL-7PBB` on 2026-11-23, as an optional finding outside that item's change.

[superseded 2026-11-27: decided by the triage pass; see **Decided 2026-11-27** below] **What to decide.** Whether the plot should stop drawing, or caption, a ratio below 1 while alveolar ventilation is zero, and what the caption names. The number itself is the true quotient; the question is whether drawing it on the wash-in curve teaches a wash-in that is not happening.

**Why it matters.** A learner who stops ventilation and lowers the dial sees the trace rise to the equilibrium line and can read it as the alveoli filling, when no agent moves between the circuit and the lungs. With the dial left alone the same holds: during apnoea the ratio moves only because blood takes agent from the alveoli, and the plot draws that movement on the wash-in curve. `CLAUDE.md`'s safety-critical standard counts a misleading graph as a defect.

**Reproduced 2026-11-27.** On `main` at `f653c1eb`, `read_wash_in` in `src/anesthesia_sim/app/wash_in.py` takes only the alveolar and inspired fractions, so a column with alveolar ventilation at zero and a ratio at or below 1 is classed as wash-in and drawn.

**Decided 2026-11-27 (triage).** While alveolar ventilation is zero, a column is outside the plot's domain. Nothing is drawn there, and the caption names the condition: ventilation is stopped, so the ratio is not a wash-in fraction. Three reasons, each already stated in this repository:

1. The model moves agent between the circuit and the alveoli only through the term $`V_A(F_I - F_A)`$ in `build_system_matrix` (`src/anesthesia_sim/core/governing_equations.py`), as `PL-7PBB` recorded. At $`V_A = 0`$ nothing the ratio does is uptake from the circuit. A dial change with ventilation running is different in kind: the ratio is still set by uptake, which is why `docs/INTERFACE.md` keeps drawing it there and adds the control marks.
2. `wash_in.py`'s module docstring refuses a caption beside a trace that is still drawing, as two displays disagreeing about the same instant. So a caption alone is not enough.
3. The safety-critical standard prefers a visible gap to a plausible-looking curve.

It extends the mechanism that `PL-P3ZL` and `PL-7PBB` chose, naming the condition and not a cause, so it was taken here rather than put to the owner. A PubMed search on 2026-11-27 for the alveolar-to-inspired ratio with ventilation and uptake found nothing that bears on drawing the ratio during apnoea.

**Done when.** A test stops ventilation during a run, with the dial lowered and with it unchanged, and shows that no point of the wash-in plot is drawn while alveolar ventilation is zero and that the caption names the stopped ventilation. `docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" and rule 2 in `wash_in.py` state the new boundary, and the approved interface strings record the caption.

**Generator check.** The same fault as `PL-7PBB`, one rule further on: both treat "ratio at or below 1" as uptake without asking whether ventilation is running. `PL-7PBB`'s blind review found this item before that fix shipped (#2305), so it does not show the fix failed. Two items are not a generator.
