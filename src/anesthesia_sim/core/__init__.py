"""Pure scientific/simulation core: PK/PD compartments and validated agent
and patient parameters. Independent of Flet or any other UI framework;
nothing in this package renders or reads from a user interface.

## A compartment's `advance()` is not how a run advances

A run advances one state vector. `governing_equations.py` assembles every
balance `docs/MODEL.md` states as one system matrix, `matrix_exponential.py`
propagates it exactly, and `AgentUptakeSystem.advance()` is the only entry
point to that.

The `advance()` methods the compartments still carry are each that
compartment's own closed form against a *constant stated input* - a held
arterial fraction for `TissueGroup`, a held tissue-return fraction for
`VenousBloodCompartment`, a held vaporizer dial for `BreathingCircuit`. Being
exact at any step size is what separates such a method from a sub-step of an
operator split, and it is a property to check rather than a claim:
`tests/unit/test_compartment_primitives.py` holds one 60 s step against six
hundred 0.1 s steps for each of them.

`alveolar.py` states the line such a method has to stay on the right side of -
nothing outside the governing equations may move agent between two modelled
compartments. Solving one compartment against a boundary input does not;
composing several of them does. `PatientCompartments.advance()` did: it
stepped the three tissue groups and then mixed their end-of-step return into
venous blood, which is the first-order split `PL-GS5X` replaced. Measured
2026-09-13 on the sevoflurane reference patient at an arterial fraction of
0.08, its mixed venous fraction after 60 s was 0.018770 in one step against
0.014969 in six hundred - 25% apart, with no documented error bound and no
production caller. It was deleted rather than documented: a plausible number
solving no equation the simulator runs is what `CLAUDE.md` reserves "prefer an
obvious failure" for (`PL-74R0`).

## Zero flow is tested with `== 0.0`, never against a tolerance

`circuit.py`, `tissue.py` and `blood.py` each branch on an exact zero flow
twice - once in `time_constant_s`, which returns `inf`, and once in the closed
form above, which leaves the compartment unchanged. Six sites, and they do not
share one reason. Measured 2026-09-13, and re-run by
`tests/unit/test_compartment_primitives.py` so that removing one is a failing
test rather than a plausible simplification:

- **The three `time_constant_s` guards are required.** Python raises
  `ZeroDivisionError` on `V/0.0` rather than returning `inf`, so the branch is
  the only route to the `inf` that `docs/MODEL.md` states for an unperfused
  compartment.
- **`BreathingCircuit.advance_fresh_gas()`'s guard is required.** Its
  exhausted-agent integral carries the factor `tau * (1 - exp(-dt/tau))`,
  which at `tau = inf` is `inf * 0.0` and therefore `nan` - for every circuit
  state, including one already sitting at the dial. Without the branch the
  circuit would report a `nan` exhaust to the mass-balance check.
- **The two amount-storing guards buy an exact no-op.** `TissueGroup` and
  `VenousBloodCompartment` would come out of the general path with the right
  *fraction* - `exp(-dt/inf)` is exactly `1.0`, and the fraction update is bit
  exact across 200,000 random pairs - but they write the amount back as
  `capacity_l * next_fraction`, and that round trip is not: 220 of 200,000
  random capacity and amount pairs move, by up to 4e-15 L. The branch is why
  an unperfused tissue reports a change of exactly zero rather than of one
  unit in the last place, which is `docs/MODEL.md`'s `dM_i/dt = 0` held
  exactly.

**The test is an equality because there is no band of nearly-zero flows to
catch.** Walked from zero upwards, the branch agrees with the general path bit
for bit at the smallest denormal, at 1e-300 and at 1e-30; the first divergence
is at a flow of 1e-12 L/min, where a real flow moves a real 1e-15 L of agent.
An epsilon would not remove a discontinuity - it would introduce one, freezing
flows the model says still move (`PL-79YX`).
"""
