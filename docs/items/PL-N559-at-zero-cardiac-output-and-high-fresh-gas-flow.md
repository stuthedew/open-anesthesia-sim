---
id: PL-N559
title: At zero cardiac output and high fresh gas flow, the exact propagator settles with the alveolar fraction a few units in the last place above the inspired fraction and the dial, so read_wash_in classes the steady state as elimination and the wash-in plot tells the learner the patient is returning agent while nothing changed
priority: P1
effort: M
status: ready
classes: defect, science, ux, safety
feature: replay-findings
touches: src/anesthesia_sim/core/matrix_exponential.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/app/wash_in.py, tests/unit/test_wash_in.py, docs/MODEL.md
added: 2026-10-25
payoff: the wash-in plot no longer tells a learner the patient is returning agent when nothing has changed
verify: grep -q 'def test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination' tests/unit/test_wash_in.py
---

**Problem.** Zero cardiac output is a supported input (PL-629Z). With no uptake, F_A should approach F_I from below and never pass it. Reproduced on main: isoflurane at its default dial, cardiac output 0 and fresh gas 10 L/min, stepped at 0.1 s. F_A first exceeds F_I at 2064.8 s, and it ends at 0.012000000000000071 against F_I 0.01199999999999981 and F_D 0.012. `is_wash_in` (`src/anesthesia_sim/app/wash_in.py`) compares the ratio to 1.0 with no tolerance, so `read_wash_in` returns ELIMINATION.

**Why it matters.** The trace stops at the equilibrium line and the caption `WASH_IN_ELIMINATION_TEXT` in `dashboard_frame.py` says "the patient is returning agent, which is elimination". That is false: the dial is unchanged and nothing is being eliminated. The reviewer found this in 16 of 54 zero-output combinations. The fix needs a decision: give the propagator an exact fixed point at F_D, or give the domain rule a tolerance derived from rounding. Either needs a test against a closed form.

**Done when.** At zero cardiac output and high fresh gas flow, the steady state is read as wash-in at equilibrium, not elimination, through an exact fixed point in the propagator or a tolerance derived from rounding, and `docs/MODEL.md` records which. `tests/unit/test_wash_in.py` has `test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination`, checked against the closed form.

**Found by.** `PL-TBQS` reviewer replay on #376, finding r01 F1. Checked against main on 2026-10-25 with `scripts/c_core376.py P`.
