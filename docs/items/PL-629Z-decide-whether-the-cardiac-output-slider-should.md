---
id: PL-629Z
title: Decide whether the cardiac-output slider should reach zero
priority: P1
effort: S
status: done
classes: safety, docs
feature: numerical-domain
milestone: v0.2.7
touches: docs/MODEL.md, src/anesthesia_sim/app/simulation_view.py, tests/reference/test_coupled_dynamics.py
added: 2026-08-30
closed: 2026-08-30
commit: a0b3ab1
pr: 68
verify: uv run pytest tests/reference/test_coupled_dynamics.py -k envelope_limits
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

---

**Decided 2026-08-30: zero cardiac output is a supported input.** Recorded in
`docs/MODEL.md` § "Supported input ranges", with the reasons — the equations
stay well posed and "Required tests" already specifies the behavior; zero is
the endpoint of a continuous axis and a floor above it would be an arbitrary
boundary inside the valid domain; and the low end of the axis is where the
teaching is. That last one is the operative reason and it is measured, not
asserted: reducing cardiac output accelerates alveolar wash-in, and in this
model \(F_A/F_I\) at five minutes for sevoflurane at 1 MAC is 0.41 at
10 L/min, 0.49 at 5, 0.58 at 2.5, 0.70 at 1, and 0.86 at zero. Zero is that
demonstration's clearest case.

The same section records what the setting does *not* claim — it is a
statement about agent transport, not a model of circulatory arrest,
cardiopulmonary bypass, or ECMO, all three of which "Known limitations"
already excludes.

**The bound stands unchanged.** This item's second concern — that
`SPLITTING_ERROR_BOUND_PER_STEP_SECOND` was set 22% above a number produced
by a setting nobody would defend — is answered by the decision rather than by
a re-measurement: the setting is defended, so 2.29e-3 s^-1 is a coefficient
inside the supported domain and the bound over it is the right one.

**One enforcement gap closed with it.** `test_envelope_limits_match_the_interface`
checked only the slider maxima, so flooring cardiac output above zero would
have removed the bound's own worst case from the reachable domain without
failing anything — PL-042's defect at the other end of the axis. The four
floors are now named constants in `app/simulation_view.py` (separately, so
each stays an independent decision) and all seven limits are checked.
