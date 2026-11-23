---
id: PL-7PBB
title: The F_A/F_I elimination caption says the patient is returning agent while ventilation is stopped, when no agent moves between the lungs and the circuit
priority: P1
effort: S
status: done
classes: defect, safety
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/wash_in.py, docs/INTERFACE.md
added: 2026-11-23
closed: 2026-11-23
pr: 2305
filed-pr: 2294
payoff: a learner who stops ventilation is not told the patient is eliminating agent
tests: tests/unit/test_dashboard_frame.py::test_a_ratio_above_one_with_ventilation_stopped_names_no_elimination
---

**Problem.** The caption above the F_A/F_I plot reads "Past equilibrium: alveolar exceeds inspired — the patient is returning agent, which is elimination and not wash-in." (`WASH_IN_ELIMINATION_TEXT` in `src/anesthesia_sim/app/dashboard_frame.py`) whenever F_A/F_I is above 1. The ratio rises above 1 in two different situations. With ventilation running after the vaporizer is closed, the lungs give agent back to the circuit, and the sentence is true. With alveolar ventilation at 0, the model moves no agent between the alveoli and the circuit: the circuit's row in `build_system_matrix` (`src/anesthesia_sim/core/governing_equations.py`) is `dF_I/dt = (V_F/V_C)(F_D - F_I) - (V_A/V_C)(F_I - F_A)`, whose second term is then zero. Fresh gas washes the circuit out while the alveoli keep their agent, so F_A rises above F_I although the patient returns nothing and eliminates nothing. The caption then tells a learner who has stopped ventilation that the patient is eliminating agent. Rule 2 in `src/anesthesia_sim/app/wash_in.py`'s module docstring and in `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" gives the same cause for every ratio above 1: "the tissues are returning agent faster than it is delivered".

The blind review of `PL-P3ZL` found it on 2026-11-23. `PL-P3ZL` fixed the same fault in the other caption of the pair, which said that no agent had reached the circuit during a washout, by naming the condition and not a cause. Its research is in that item.

**What to do.** Make the caption and both rule 2 texts true in both situations, by naming the condition (the alveolar concentration is above the inspired, so the ratio is above 1 and is not a wash-in fraction) rather than a cause, as `PL-P3ZL` did. Update the approved interface strings. Add a test that reaches a ratio above 1 with ventilation stopped through a run, as `.claude/rules/test-oracles.md` rule 2 asks.

**Why it matters.** A learner who stops ventilation and reads that the patient is eliminating agent learns the opposite of the model: with no alveolar ventilation, nothing leaves the lungs. That is a wrong clinical statement beside a displayed value, so the safety-critical standard applies.

**Done when.** A test reaches a ratio above 1 with ventilation stopped through a run, and shows that the caption and both rule 2 texts name the condition (alveolar above inspired, so the ratio is not a wash-in fraction) and say nothing false about where agent goes. The approved interface strings record the new caption.

**Generator check.** The same fault as `PL-P3ZL` in the other caption of the pair, found by its review: a caption that names a cause where only the condition is known. One-off; `PL-P3ZL` closed with this item filed during its work.

**Reproduced 2026-11-23.** `WASH_IN_ELIMINATION_TEXT` in `src/anesthesia_sim/app/dashboard_frame.py` and rule 2 in `src/anesthesia_sim/app/wash_in.py` still give the cause "returning agent".

**Done 2026-11-23.** The caption above 1 is now "Past equilibrium: alveolar exceeds inspired, so the ratio is not a wash-in fraction." (`WASH_IN_ELIMINATION_TEXT` in `app/dashboard_frame.py`). It names the condition and no cause, as `PL-P3ZL` did for the other caption on the same research (the NN/g error-message guidelines and the Philips IntelliVue MP20/MP30 instructions for use, recorded in `PL-P3ZL`), under the owner's answer there to research best practice and follow it. Rule 2 in `app/wash_in.py`'s module docstring and in `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" now says that with ventilation running the patient is returning agent to the circuit, and that with alveolar ventilation at zero no agent moves between the lungs and the circuit and the ratio passes 1 only because fresh gas washes the circuit out. `tests/unit/test_dashboard_frame.py::test_a_ratio_above_one_with_ventilation_stopped_names_no_elimination` runs 4% sevoflurane for 600 s, stops ventilation, turns the dial to 0.5% and at 900 s finds the alveolar concentration above the inspired, no plotted ratio, and the new caption. The approved interface strings hold no point that reaches this caption, so they did not change; `PL-4G79` covers strings shown only after a setting change. Documents checked: `docs/INTERFACE.md` (rule 2 and the caption paragraph; the 1 + 2.2e-14 history paragraph describes the old wording as past and still holds), `docs/MODEL.md`, `docs/VERIFICATION.md` and `README.md` (none quotes the caption).
