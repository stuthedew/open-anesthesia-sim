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

`tissue.py`, `blood.py` and `circuit.py` each branch on an exact zero flow
once, in `time_constant_s`, which returns `inf`, and no closed form branches
at all. Three sites with one reason, where there were five with two: measured
2026-09-13, re-measured 2026-10-12 with the patient compartments' closed forms
rewritten (`PL-XWFP`), and re-run by
`tests/unit/test_compartment_primitives.py` so that removing a guard, or
writing a branch or the old form back, is a failing test rather than a
plausible simplification:

- **The three `time_constant_s` guards are required.** Python raises
  `ZeroDivisionError` on `V/0.0` rather than returning `inf`, so the branch is
  the only route to the `inf` that `docs/MODEL.md` states for an unperfused
  compartment.
- **No closed form needs a guard, and none has one.** Each is written
  `i + (e - i) * (1 - exp(-dt/tau))`, anchored at what the compartment holds,
  with the last factor taken by `expm1`, so at zero flow it is
  `i + (e - i) * 0.0`, which is `i` exactly, and the change each reports is
  exactly zero. `BreathingCircuit.advance_fresh_gas()` has been written so on
  its fraction since `PL-YT8N`, with the factor taken from the gas the step
  admits. Written `d + (i - d) * exp(-dt/tau)` until then, it was `i` only
  while the two were within a factor of two of each other, and a guard bought
  the exact no-op: without it a 6 L circuit loaded to a fraction of 1e-6 under
  a 100% dial came back holding 6.000000000172534e-06 L where it held 6e-06
  (measured 2026-10-05). The guard had once stopped a `nan` too, from an
  exhaust carrying `tau * (1 - exp(-dt/tau))`, which is `inf * 0.0` where the
  time constant overflows (`PL-B26Y`); nothing in the closed form holds a time
  constant now.
- **`TissueGroup` and `VenousBloodCompartment` are written so on the amount
  they store, through `exponential_approach.py`, since `PL-XWFP`.** Each kept
  a guard until then because its form was written on the fraction and wrote
  the amount back as `capacity_l * next_fraction`, a round trip that moved 220
  of 200,000 random capacity and amount pairs by up to 4e-15 L; the branch was
  why an unperfused tissue reported a change of exactly zero rather than of
  one unit in the last place, which is `docs/MODEL.md`'s `dM_i/dt = 0` held
  exactly. Anchored at the amount held there is no round trip, and the no-op
  is the closed form's own.

**The test is an equality because there is no band of nearly-zero flows to
catch.** Walked from zero upwards - the smallest denormal, 1e-300 and 1e-30
L/min - each compartment stores exactly what its zero-flow result stores, bit
for bit: the flows are real, and the agent they move over a step is below the
resolution of what the compartment holds. The two patient compartments report
exactly no agent moved there; the circuit reports the agent such a flow
delivers and exhausts, 1.7e-33 L over 0.1 s at 1e-30 L/min, within one
rounding of zero. The smallest denormal is one of the flows at which the
circuit's time constant overflows to `inf` - every flow below about 2e-306
L/min, for a 6 L circuit - which its closed form no longer forms (`PL-B26Y`,
`PL-YT8N`). Each compartment first moves where its own gap term stops
rounding to zero against what it holds: the circuit and the tissue group at
1e-18 L/min, where each moves 8.5e-22 L, and the venous pool at 1e-19 L/min,
where it moves 1.1e-22 L (measured over 0.1 s from a fraction of 1e-6 driven
by 1.0; 2026-10-11 for the circuit, 2026-10-12 for the two patient
compartments). An epsilon would not remove a discontinuity - it would
introduce one, freezing flows the model says still move (`PL-79YX`).
"""
