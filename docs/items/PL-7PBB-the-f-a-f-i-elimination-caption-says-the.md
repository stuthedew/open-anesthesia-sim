---
id: PL-7PBB
title: The F_A/F_I elimination caption says the patient is returning agent while ventilation is stopped, when no agent moves between the lungs and the circuit
priority: P1
effort: S
status: ready
classes: defect, safety
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/wash_in.py, docs/INTERFACE.md
added: 2026-11-23
filed-pr: 2294
payoff: a learner who stops ventilation is not told the patient is eliminating agent
---

**Problem.** The caption above the F_A/F_I plot reads "Past equilibrium: alveolar exceeds inspired — the patient is returning agent, which is elimination and not wash-in." (`WASH_IN_ELIMINATION_TEXT` in `src/anesthesia_sim/app/dashboard_frame.py`) whenever F_A/F_I is above 1. The ratio rises above 1 in two different situations. With ventilation running after the vaporizer is closed, the lungs give agent back to the circuit, and the sentence is true. With alveolar ventilation at 0, the model moves no agent between the alveoli and the circuit: the circuit's row in `build_system_matrix` (`src/anesthesia_sim/core/governing_equations.py`) is `dF_I/dt = (V_F/V_C)(F_D - F_I) - (V_A/V_C)(F_I - F_A)`, whose second term is then zero. Fresh gas washes the circuit out while the alveoli keep their agent, so F_A rises above F_I although the patient returns nothing and eliminates nothing. The caption then tells a learner who has stopped ventilation that the patient is eliminating agent. Rule 2 in `src/anesthesia_sim/app/wash_in.py`'s module docstring and in `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" gives the same cause for every ratio above 1: "the tissues are returning agent faster than it is delivered".

The blind review of `PL-P3ZL` found it on 2026-11-23. `PL-P3ZL` fixed the same fault in the other caption of the pair, which said that no agent had reached the circuit during a washout, by naming the condition and not a cause. Its research is in that item.

**What to do.** Make the caption and both rule 2 texts true in both situations, by naming the condition (the alveolar concentration is above the inspired, so the ratio is above 1 and is not a wash-in fraction) rather than a cause, as `PL-P3ZL` did. Update the approved interface strings. Add a test that reaches a ratio above 1 with ventilation stopped through a run, as `.claude/rules/test-oracles.md` rule 2 asks.

**Why it matters.** A learner who stops ventilation and reads that the patient is eliminating agent learns the opposite of the model: with no alveolar ventilation, nothing leaves the lungs. That is a wrong clinical statement beside a displayed value, so the safety-critical standard applies.

**Done when.** A test reaches a ratio above 1 with ventilation stopped through a run, and shows that the caption and both rule 2 texts name the condition (alveolar above inspired, so the ratio is not a wash-in fraction) and say nothing false about where agent goes. The approved interface strings record the new caption.

**Generator check.** The same fault as `PL-P3ZL` in the other caption of the pair, found by its review: a caption that names a cause where only the condition is known. One-off; `PL-P3ZL` closed with this item filed during its work.

**Reproduced 2026-11-23.** `WASH_IN_ELIMINATION_TEXT` in `src/anesthesia_sim/app/dashboard_frame.py` and rule 2 in `src/anesthesia_sim/app/wash_in.py` still give the cause "returning agent".
