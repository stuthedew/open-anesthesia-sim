---
id: PL-629Z
title: Decide whether the cardiac-output slider should reach zero
status: untriaged
added: 2026-08-30
---

**Problem.** `simulation_view`'s cardiac-output slider has `min=0`, so a user
can hold cardiac output at 0 L/min indefinitely and the model will integrate
it. Found while measuring PL-SLHS's splitting-error domain: the worst
trajectory the four sliders can reach — and therefore the measurement
`SPLITTING_ERROR_BOUND_PER_STEP_SECOND` is now set from — depends on that
setting. Loading the circuit and alveoli to the vaporizer maximum with no
perfusion, then restoring perfusion, gives 2.29e-3 s^-1 against 1.52e-3 s^-1
for the same manoeuvre at a physiological cardiac output.

**Why it matters.** Two separate things, and the second is the reason to
decide rather than leave it.

Zero cardiac output is not a physiological state a simulation of uptake and
distribution has anything to say about: it is circulatory arrest, and every
compartment equation the model carries assumes flow. Offering it on a slider
with no marking presents an unmodelled state as an ordinary setting.

And it costs the release gate its clinical meaning. The bound is now set 22%
above a number produced by a setting nobody would defend, so a real
regression at defensible settings has more headroom before it fails than the
gate's narrow margin suggests. Flooring the slider (or refusing the setting)
would let the bound follow the ventilator-start trajectory instead, which is
a manoeuvre a user performs.

The same question applies to alveolar ventilation, which also reaches zero —
but there the answer is likely different: apnoea is a real, teachable state
that the model does represent, and the ventilator-start trajectory depends on
it.

**Where.** `src/anesthesia_sim/app/simulation_view.py` (the slider's `min`),
`src/anesthesia_sim/core/patient.py` (`set_cardiac_output`'s validation), and
`tests/reference/test_coupled_dynamics.py`'s
`_unperfused_load_then_dial_off`, whose docstring says why it is there and
would have to be revisited.

**Done when.** The decision is recorded in `docs/MODEL.md` — either that zero
cardiac output is a supported input and why, or that it is refused and where.
If it is refused, the splitting-error domain is re-swept without it, the
bound reset from that measurement, and `docs/MODEL.md`'s coefficient table
and "Displayed precision" section revised together with it.
