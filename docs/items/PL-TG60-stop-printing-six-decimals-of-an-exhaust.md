---
id: PL-TG60
title: Stop printing six decimals of an exhaust integral good to three
priority: P3
effort: S
status: done
classes: defect, ux
feature: presentation-safety
milestone: v0.4.26
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_formatting.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-08-30
closed: 2026-09-15
pr: 588
verify: uv run pytest tests/unit/test_formatting.py && grep -q 'def test_agent_amounts_precision' tests/unit/test_formatting.py
---

> **This fix rides the Qt port, not Flet.** `ROADMAP.md` § "Completed: v0.4.26 -
> the interface moves to Qt" names this item under "Fixes this port carries":
> the defect lives in code that milestone rewrites from scratch, so fixing it
> on Flet means writing the same lines twice. Project owner, 2026-09-10.

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

**What v0.4.1 does to this (added 2026-09-03).** **Re-measure before deciding anything.**
This item's quantitative basis is the split: `BreathingCircuit.advance_fresh_gas`
(`core/circuit.py:209-214`) integrates the *fresh-gas-only* sub-step trajectory
analytically, which is what makes the exhaust integral good to about three
decimals rather than six. Under a coupled propagator the exhaust integral has no
sub-step trajectory to integrate and must be recomputed - `PL-GS5X`'s brief
leaves that open, and `AgentSimulationValidator.record_external_agent_transfer`
depends on the answer. The integral could become materially more accurate, in
which case the right decimal count is a different number, or it could be
computed a way that changes the argument entirely. Six decimals on a value good
to three is still wrong today; how many are right is not answerable until the
exact step lands.

**Basis changed by `PL-GS5X`, 2026-09-06 — re-read before working.** This
item's quantitative argument was that the exhausted-agent integral is good to
about three decimals because `BreathingCircuit.advance_fresh_gas` integrates
the *fresh-gas-only* sub-step trajectory analytically, which is not the
trajectory the coupled system takes.

That is no longer how the integral is formed. Exhausted agent is now a state of
the system matrix, with $`dM_{exhausted}/dt = \dot V_F F_I`$ as its row, so the
propagator integrates it along the same coupled trajectory it produces for
everything else — exactly, not approximately. `docs/MODEL.md` § "Selected
method (as implemented)" carries why it is a state rather than a side
calculation.

So the "six decimals of a number good to three" framing is void. The measured
residual is now 1.0e-12 L to 1.3e-11 L over an hour depending on the agent
(recorded in the same section), which is a different and much smaller number
than this item assumed — but the *displayed* question it raises is untouched:
six decimals of an exhaust total is still more precision than a reader can use,
whatever the value is good to. Re-measure and re-argue on the new figure.

**Deferred to the Qt port, 2026-09-13 (`PL-D143`, project owner).** `status:
blocked`, `blocked-by: PL-25KS` - the dashboard port, which rewrites the agent-accounting panel this defect is in. `bin/docket next` therefore stops
offering work that cannot be done until that port lands. The owner's 2026-09-10
note above is the decision; this only makes the queue agree with it.

It is blocked on the **item** rather than on the port's version because the two mean
different things in this store: `blocked-by: <version>` says an item is waiting
for a milestone to be *scoped*, and `docket check` promotes it back to `ready`
the moment that section carries its four subsections - which the port's already
does, so the version form raised "ready to promote" on every run. The port item
is the edge that is actually true.

**Closed 2026-09-15, with `PL-25KS`, on a measurement.** Perturbing one
stored coefficient by one published SD, as § "Displayed precision" does for
the readouts, moves the exhaust total by 0.016-0.042 L at 3600 s and by
0.18-0.23 L at the 24 h supported limit (sevoflurane 0.024 and 0.19 L,
isoflurane 0.016 and 0.18 L, desflurane 0.042 and 0.23 L; blood:gas
dominant; 1 MAC, the reference adult's flows). One count of 0.1 L sits
between a quarter of an SD and six SDs across the whole span, the band the
readouts' own derivation admits; 0.01 L falls to a fiftieth of an SD by
24 h. So the panel prints one decimal through
`formatting.format_agent_volume` (`AGENT_VOLUME_DISPLAY_DECIMALS`, with the
below-resolution form `<0.1 L`), keeps the residual lines in scientific
notation, and states the unit as the specification states it, "Litres of
equivalent pure agent gas". `docs/MODEL.md` § "Displayed precision" carries
the derivation and withdraws the sentence that had justified six decimals
(the residual is visible only on the lines that print it in scientific
notation). `test_agent_amounts_precision` pins the form.
