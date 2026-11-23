---
id: PL-P3ZL
title: After the vaporizer is turned off, the F_A/F_I caption says no agent has reached the circuit yet
status: untriaged
feature: interface-design-review
added: 2026-11-23
filed-pr: 2281
---

**Problem.** The line above the F_A/F_I plot says "Not defined: no agent has reached the circuit yet." (`WASH_IN_NOT_DEFINED_TEXT` in `src/anesthesia_sim/app/dashboard_frame.py`) whenever the inspired fraction is below 0.01%, the floor `read_wash_in` in `src/anesthesia_sim/app/wash_in.py` divides by. `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" names only the start of a run and a run whose vaporizer is never opened as the cases below that floor. A run can also reach it after agent was given: with the vaporizer turned off, the inspired fraction falls below 0.01% during washout. `tests/integration/controller/test_controller_preview_crossings.py` builds such a run (8% sevoflurane for 30 s, then apnoea at 0.5 L/min with the vaporizer off), and its inspired fraction falls below the floor in its second hour. The caption then tells a learner that no agent ever reached the circuit while the patient still holds agent, and while the plot may report earlier wash-in stretches in the same line ("(2 earlier stretch(es) not drawn)").

The blind review of `PL-00Y5` found it on 2026-11-23, in a new test that pinned that contradictory line. The test was changed to leave the no-agent state out, so nothing now pins the wording this item changes, except `test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit` in `tests/unit/test_dashboard_frame.py`, which checks the start of a run, where the sentence is true.

**What to do.** Make the line true in both cases. One way is a wording that does not claim a history, such as one that says the inspired concentration is below the 0.01% the ratio is divided by. Another is a separate state for a run that has had agent in its circuit, which needs a fact the single reading does not hold. Research how a monitor or a teaching display labels a ratio whose denominator is too small, record the sources here, and choose. Update `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" and the approved interface strings with it. Add a test that reaches the washout case through a run, as `.claude/rules/test-oracles.md` rule 2 asks.
