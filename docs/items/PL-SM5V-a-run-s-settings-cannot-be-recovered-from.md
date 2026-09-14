---
id: PL-SM5V
title: A run's settings cannot be recovered from RunSegment.settings: the L/min to L/s conversion does not round-trip for 7 of 101 cardiac outputs
status: untriaged
added: 2026-09-14
---

**Problem.** A run's settings cannot be recovered from RunSegment.settings: the L/min to L/s conversion does not round-trip for 7 of 101 cardiac outputs

**Where it was found.** `PL-J2TD`'s fork seam, which has to build a branch's
system carrying its parent's settings. The obvious source is the
`RunSegment` the branch opens from, since that is what carries the settings a
stretch of the run was computed under - and it is the wrong one.

**The measurement.** `AgentUptakeSystem.equation_settings()` converts each flow
to litres per second, because that is the unit `docs/MODEL.md`'s governing
equations are written in, while the compartments hold litres per minute.
Multiplying back by sixty does not recover the original: over the supported
0 to 10 L/min cardiac-output range on a 0.1 L/min grid, **7 of 101 values**
produce a different `UptakeEquationSettings`, the first at 1.9 L/min. The
divergence is in the three per-tissue blood flows rather than in cardiac output
itself, because `PatientCompartments._update_blood_flows` derives each as
`cardiac_output_l_min * perfusion_fraction` *before* the conversion, so the
child's flows are `(Q_l_s * 60) * fraction / 60` against the parent's
`Q * fraction / 60`.

**Why it matters.** A branch built that way assembles a system matrix one unit
in the last place from its parent's, so its live path and its own run
definition solve slightly different equations from the first step - inside the
tolerance `docs/MODEL.md` § "Closed-form agreement test" holds the two records
together with, and therefore reported by nothing. The same round trip also
makes a displayed flow read 7.699999999999999 L/min on one branch and 7.7 on
the other.

**What holds it today, and what does not.** `tests/unit/test_resume_at.py`'s
`_like()` helper takes the settings off the parent's compartments in L/min and
asserts the two settings objects compare equal, so the test suite uses the
right source and says why. Nothing stops production code from using the wrong
one: `RunSegment.settings` is public, `SimulationController.run_segments` hands
it out, and the multiplication looks obviously correct.

**Options.** Either make the recovery honest - carry the compartments' L/min
values alongside, or derive the tissue flows from the converted cardiac output
on both sides so the two agree by construction - or make it impossible, by
documenting on `RunSegment` that its settings are for assembling a matrix and
never for configuring a system. The second is cheaper and is probably right;
the first is what a save/load format (planned item 9) will need, because a
reloaded run has no parent compartments to read.
