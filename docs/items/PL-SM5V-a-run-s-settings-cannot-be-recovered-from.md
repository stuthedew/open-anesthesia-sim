---
id: PL-SM5V
title: A run's settings cannot be recovered from RunSegment.settings: the L/min to L/s conversion does not round-trip for 7 of 101 cardiac outputs
priority: P2
effort: M
status: ready
classes: defect
feature: scenario-branching
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py, docs/MODEL.md
added: 2026-09-14
verify: grep -q 'def test_a_recorded_setting_round_trips_to_what_was_set' tests/unit/test_run_definition.py && uv run pytest tests/unit/test_run_definition.py
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

**Reproduced exactly, 2026-09-14.** Over the 101 cardiac outputs from 1.0 to
11.0 L/min at 0.1 L/min, `lpm / 60.0 * 60.0 != lpm` for **7**: 1.9, 3.8, 3.9,
7.6, 7.7 and two more. The first reads back `1.8999999999999997`. The count in
the title is right.

**Where it comes from.** `core/governing_equations.py:244-256` -
`UptakeEquationSettings` stores flows per second because `docs/MODEL.md` §
"Governing equations" requires it, "and the conversion from the user-facing
litres per minute happens once where this is constructed rather than inside an
equation". That is the right design and the loss is inherent to it: the L/min
the learner set is not among the settings, and multiplying back by 60 does not
always return it.

**Why it matters, and the sharper half is not the display.** No displayed value
is wrong: formatted to one decimal, `1.8999999999999997` prints `1.9`. Two other
things are affected, and both are real. First, `UptakeEquationSettings` is
"Frozen and compared by value, because `uptake_system.py` uses it as the key its
propagator is cached against" - so a settings object rebuilt from a recovered
L/min is *unequal* to the one built from the original entry, and a comparison
that should match does not. `PL-NC62` is where that surfaces as a user-visible
refusal with a misdiagnosed cause, which is why these two should be read
together. Second, `CLAUDE.md` asks that a displayed value be traceable to the
exact inputs that produced it; a run whose settings cannot be recovered as
entered is traceable only to one rounding of them.

**Why not `safety`, stated rather than assumed.** Nothing here produces a wrong
number a clinician could read. The failure is an equality that should hold and
does not, whose worst observed consequence is a refusal with a wrong
explanation - a defect, not a misleading clinical value.

**Done when.** A run's settings as the learner entered them are recoverable from
what the definition records - by keeping the entered L/min alongside the derived
per-second value, or by deriving both from one stored quantity - so that
rebuilding a settings object from a recorded segment yields one equal to the
original, for all 101 cardiac outputs above. `docs/MODEL.md` says which of the
two is the record and which is derived.
