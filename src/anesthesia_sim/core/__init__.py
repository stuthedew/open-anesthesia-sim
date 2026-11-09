"""This package holds the PK/PD compartments and the validated agent and patient parameters.

It is pure scientific and simulation code. It does not depend on Qt
or on any other UI framework, and nothing in it renders a user interface or
reads from one.

## A compartment's `advance()` is not how a run advances

A run advances one state vector. One module assembles every balance that
`docs/MODEL.md` states into a single system matrix (`governing_equations.py`),
and another propagates that matrix exactly (`matrix_exponential.py`). The only
entry point to that propagation is `AgentUptakeSystem.advance()`.

The compartments also have `advance()` methods of their own. Each one is that
compartment's closed-form solution against a stated, constant input: a held
arterial fraction for `TissueGroup`, a held tissue-return fraction for
`VenousBloodCompartment`, and a held vaporizer dial for `BreathingCircuit`.
Such a method is exact at any step size, which is what separates it from one
sub-step of a scheme that steps the compartments one after another. A test
checks that exactness for each of the three methods by comparing one 60 s step
with six hundred 0.1 s steps (`tests/unit/test_compartment_primitives.py`).

Such a method must not break the rule that `alveolar.py` states: nothing
outside the governing equations may move agent between two modelled
compartments. Solving one compartment against a boundary input does not break
that rule, but composing several such solutions does. A former method,
`PatientCompartments.advance()`, broke it. It stepped the three tissue groups
and then mixed their end-of-step return into venous blood. That
one-after-another stepping is the first-order split that `PL-GS5X` replaced.
On the sevoflurane reference patient at an arterial fraction of 0.08, the
method's mixed venous fraction after 60 s was 0.018770 in one step and 0.014969
in six hundred steps (simulated 2026-09-13). The two results were 25% apart,
the method had no documented error bound, and nothing in production called it.
It was deleted rather than documented, because the project's rules reserve
"prefer an obvious failure" for a plausible number that solves no equation the
simulator runs (`CLAUDE.md`, `PL-74R0`).

## Zero flow is tested with `== 0.0`, never against a tolerance

In each of `tissue.py`, `blood.py` and `circuit.py`, the only zero-flow guard
is a branch in `time_constant_s` that returns `inf` at an exact zero flow. No
closed form branches on flow at all. That makes three guards with one reason,
where there used to be five with two reasons. Which zero-flow guards are needed
was found by running the code on 2026-09-13, and again on 2026-10-12 after the
patient compartments' closed forms were rewritten (`PL-XWFP`). The runs are
repeated in `tests/unit/test_compartment_primitives.py`, so removing a guard,
or writing the old closed form back, fails a test rather than passing as a
plausible simplification. A zero-flow guard added back to a closed form is not
caught, but it is only redundant. It returns what the closed form already
returns, bit for bit, at every flow that the test suite walks through (checked
2026-10-12).

- **The three `time_constant_s` guards are required.** Python raises
  `ZeroDivisionError` on `V/0.0` rather than returning `inf`, so the guard is
  the only route to the `inf` that `docs/MODEL.md` states for an unperfused
  compartment.
- **No closed form needs a guard, and none has one.** Each closed form is
  `i + (e - i) * (1 - exp(-dt/tau))`. It is anchored at `i`, what the
  compartment holds, and its last factor is computed with `expm1`. At zero
  flow the form is `i + (e - i) * 0.0`, which is exactly `i`, so the change
  each compartment reports is exactly zero. All three compartments get this
  form from a shared module (`core/exponential_approach.py`) and use it for any
  step that closes up to half the gap `e - i`, which includes a step at zero
  flow. For a longer step they take the form anchored at the equilibrium
  (`PL-XWFP`). The two patient compartments apply it to the amount they store.
  The method `BreathingCircuit.advance_fresh_gas()` applies it to the fraction
  that the circuit stores, and computes the step's length in time constants,
  `dt/tau`, from the gas that the step admits (`PL-YT8N`, `PL-CQ1M`).
- **The circuit's earlier form needed a guard to make a zero-flow step an
  exact no-op.** That form was `d + (i - d) * exp(-dt/tau)` for every step
  (until `PL-YT8N`). At zero flow it returned exactly `i` only while the
  starting fraction and the driving fraction were within a factor of two of
  each other, so a guard was needed to make a zero-flow step an exact no-op.
  Without the guard, a 6 L circuit loaded to a fraction of 1e-6 under a 100%
  dial came back holding 6.000000000172534e-06 L where it had held 6e-06 L
  (computed 2026-10-05). At one time the guard also stopped a `nan` from the
  exhaust term, which then contained `tau * (1 - exp(-dt/tau))`. That product
  is `inf * 0.0` where the time constant overflows (`PL-B26Y`). Nothing in the
  closed form contains a time constant now.
- **The patient compartments' earlier form, applied to the fraction, needed a
  guard at zero flow.** Until `PL-XWFP`, each kept a guard, applied its form to
  the fraction, and wrote the amount back as `capacity_l * next_fraction`. That
  round trip returns some amounts one unit in the last place away from where
  they started. For example, 0.40250137443750783 L comes back as
  0.4025013744375079 L, both through a capacity of 6.0 L and through one of
  0.7943 L (computed 2026-10-12). Four such amounts are checked in
  `tests/unit/test_compartment_primitives.py`. The guard made an unperfused
  tissue report a change of exactly zero rather than one unit in the last
  place, and zero meets `docs/MODEL.md`'s `dM_i/dt = 0` exactly. A form
  anchored at the amount held makes no round trip, so the closed form gives the
  exact no-op by itself.

**Zero flow is compared exactly because there is no band of nearly-zero flows
to catch.** The test suite walks upward from zero through the smallest
denormal, 1e-300 and 1e-30 L/min. These flows are not zero, but the agent they
move over a step is smaller than the resolution of the amount the compartment
holds. At each of them, every compartment stores exactly what its zero-flow
result stores, bit for bit, and the two patient compartments report that
exactly no agent moved. The circuit reports the agent that such a flow
delivers and exhausts, which is 1.7e-33 L over 0.1 s at 1e-30 L/min, within
one rounding of zero. The smallest denormal is one of the flows at which the
circuit's time constant overflows to `inf`. For a 6 L circuit, that happens at
every flow less than about 2e-306 L/min. Nothing in the circuit's closed form
computes that time constant (`PL-B26Y`, `PL-YT8N`).

A tolerance would not remove a discontinuity. It would introduce one, by
freezing flows that the model says still move (`PL-79YX`). Each compartment
first moves agent at the flow where its own gap term stops rounding to zero
against the amount it holds. For the circuit that flow is 3.8e-19 L/min, and
for the tissue group it is 3.9e-19 L/min, where each moves 8.5e-22 L. For the
venous blood compartment it is 4.9e-20 L/min, where it moves 1.1e-22 L. The
test suite's walk uses a grid of one and three times each power of ten. On that
grid, the circuit and the tissue group first move at 1e-18 L/min and the venous
blood compartment at 1e-19 L/min (bisected over 0.1 s from a fraction of 1e-6
driven by 1.0, 2026-10-12).
"""
