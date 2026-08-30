---
id: PL-TG60
title: Stop printing six decimals of an exhaust integral good to three
priority: P3
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, tests/unit/test_simulation_view.py
added: 2026-08-30
verify: uv run pytest tests/unit/test_simulation_view.py -k agent_amounts_precision
---

**Problem.** The agent-accounting panel renders litres at `:.6f`
(`app/simulation_view.py:719-728`), but the exhausted amount it prints is not
accurate to six decimals. `core/circuit.py:148-152` integrates the
*fresh-gas-only sub-step* trajectory over the step, not the true F_C(t) that
`docs/MODEL.md:456` defines the exhaust integral against — the circuit's
concentration also changes within the step through the alveolar exchange, and
that part is not in the integral. Measured over 3600 s: sevoflurane at the
defaults reports 3.991854 L against a true 3.991974 L, and desflurane at the
envelope corner is 1.306 mL out. The last three or four printed digits carry no
information.

**Why it matters.** False precision is one of the failure modes `CLAUDE.md`
names outright: six decimals asserts a resolution the model does not have, and
this panel is the one a user consults to decide whether the run is trustworthy.
A reader who sees the sixth digit change and believes it is measuring something
draws a conclusion from noise. `docs/MODEL.md`'s "Displayed precision" section
justifies the resolution of the six concentration readouts and says nothing
about this panel, so the number that most overstates itself is the one outside
the rule.

**Where.** `app/simulation_view.py:719-728`; `core/circuit.py:146-152`;
`docs/MODEL.md:454-458` (the exhaust integral) and its "Displayed precision"
section.

**Approach.** Extend "Displayed precision" to cover the accounting panel, derive
a justified number of decimals from the sub-step integration error above, and
format to it. Two related things belong in the same pass:

- The residual and absolute-error fields alongside are printed at `:.3e`, which
  is appropriate for a quantity whose whole purpose is its order of magnitude —
  keep that, and say in the document why the two formats differ.
- These are litres of equivalent agent **gas**, which is not the unit anyone
  consumes agent in. Label the unit unambiguously here. This is directly
  relevant to planned-milestone item 28 (agent cost), which builds on this
  number and would otherwise inherit both the unit ambiguity and the false
  precision.

Fixing the integral itself is a separate, larger question and is not this item;
the defect here is displaying more digits than the integral supports.

**Done when.** `docs/MODEL.md`'s "Displayed precision" governs the accounting
panel with the sub-step integration error recorded as the reason, the panel
prints only digits that error supports, the gas-volume unit is unambiguous in
the label, and a test pins the format.
