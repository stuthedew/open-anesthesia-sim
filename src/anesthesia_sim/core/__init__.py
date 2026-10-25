"""This package holds the PK/PD compartments and the validated agent and patient parameters.

It is pure scientific and simulation code. It does not depend on Flet
or on any other UI framework, and nothing in it renders a user interface or
reads from one.

## A compartment's `advance()` is not how a run advances

A run advances one state vector. `governing_equations.py` assembles every
balance that `docs/MODEL.md` states into one system matrix.
`matrix_exponential.py` propagates that matrix exactly, and
`AgentUptakeSystem.advance()` is the only entry point to that propagation.

The compartments still carry `advance()` methods. Each one is that
compartment's own closed-form solution against a *constant stated input*: a
held arterial fraction for `TissueGroup`, a held tissue-return fraction for
`VenousBloodCompartment`, and a held vaporizer dial for `BreathingCircuit`.
Such a method is exact at any step size, and that is what separates it from a
sub-step of an operator split. Exactness is a property to check rather than a
claim. `tests/unit/test_compartment_primitives.py` compares one 60 s step with
six hundred 0.1 s steps for each of the three methods.

`alveolar.py` states the rule that such a method must not break: nothing
outside the governing equations may move agent between two modelled
compartments. Solving one compartment against a boundary input does not break
that rule. Composing several such solutions does. `PatientCompartments.advance()`
broke it. It stepped the three tissue groups and then mixed their end-of-step
return into venous blood, which is the first-order split that `PL-GS5X`
replaced. It was measured on 2026-09-13 on the sevoflurane reference patient at
an arterial fraction of 0.08. Its mixed venous fraction after 60 s was 0.018770
in one step and 0.014969 in six hundred steps. The two results were 25% apart,
the method had no documented error bound, and it had no production caller. It
was deleted rather than documented. A plausible number that solves no equation
the simulator runs is the case for which `CLAUDE.md` reserves "prefer an
obvious failure" (`PL-74R0`).

## Zero flow is tested with `== 0.0`, never against a tolerance

`tissue.py`, `blood.py` and `circuit.py` each branch on an exact zero flow in
one place only: `time_constant_s`, which returns `inf`. No closed form branches
on flow at all. That makes three branch sites with one reason, where there used
to be five sites with two reasons. Which guards are needed was measured on
2026-09-13. It was measured again on 2026-10-12, after the patient
compartments' closed forms were rewritten (`PL-XWFP`).
`tests/unit/test_compartment_primitives.py` re-runs the measurement, so
removing a guard, or writing the old closed form back, fails a test rather than
passing as a plausible simplification. A zero-flow branch added back to a
closed form is not caught, but it is only redundant. It returns what the closed
form already returns, bit for bit, at every flow that the suite walks through
(measured 2026-10-12):

- **The three `time_constant_s` guards are required.** Python raises
  `ZeroDivisionError` on `V/0.0` rather than returning `inf`, so the branch is
  the only route to the `inf` that `docs/MODEL.md` states for an unperfused
  compartment.
- **No closed form needs a guard, and none has one.** Each closed form is
  `i + (e - i) * (1 - exp(-dt/tau))`. It is anchored at what the compartment
  holds, and its last factor is computed with `expm1`. At zero flow the form is
  `i + (e - i) * 0.0`, which is exactly `i`, so the change each compartment
  reports is exactly zero. `BreathingCircuit.advance_fresh_gas()` has used this
  form on its fraction since `PL-YT8N`, with the factor computed from the gas
  that the step admits. The two patient compartments use it on their amount for
  any step that closes up to half the gap, which includes a step at zero flow.
  For a longer step they use the form anchored at the equilibrium
  (`core/exponential_approach.py`, `PL-XWFP`). Before `PL-YT8N`, the circuit's
  form was written `d + (i - d) * exp(-dt/tau)`. At zero flow that form
  returned exactly `i` only while the starting fraction and the driving
  fraction were within a factor of two of each other, so a guard was needed to
  make a zero-flow step an exact no-op. Without the guard, a 6 L circuit loaded
  to a fraction of 1e-6 under a 100% dial came back holding
  6.000000000172534e-06 L where it had held 6e-06 L (measured 2026-10-05). The
  guard had once also stopped a `nan`. The exhaust term then contained
  `tau * (1 - exp(-dt/tau))`, which is `inf * 0.0` where the time constant
  overflows (`PL-B26Y`). Nothing in the closed form contains a time constant now.
- **Since `PL-XWFP`, `TissueGroup` and `VenousBloodCompartment` apply the form
  to the amount they store, through `exponential_approach.py`.** Each kept a
  guard until then. Its form was written on the fraction, and it wrote the
  amount back as `capacity_l * next_fraction`. That round trip returns some
  amounts one ulp away from where they started. For example,
  0.40250137443750783 L comes back as 0.4025013744375079 L, both through a
  capacity of 6.0 L and through one of 0.7943 L (measured 2026-10-12).
  `tests/unit/test_compartment_primitives.py` checks four such amounts. The
  guard was the reason that an unperfused tissue reported a change of exactly
  zero rather than a change of one unit in the last place. A change of exactly
  zero meets `docs/MODEL.md`'s `dM_i/dt = 0` exactly. A form anchored at the
  amount held makes no round trip, so the closed form gives the exact no-op by
  itself.

**The test is an equality because there is no band of nearly-zero flows to
catch.** The suite walks upward from zero through the smallest denormal,
1e-300 and 1e-30 L/min. At each of these flows, every compartment stores
exactly what its zero-flow result stores, bit for bit. The flows are real, but
the agent they move over a step is smaller than the resolution of the amount
the compartment holds. At these flows the two patient compartments report that
exactly no agent moved. The circuit reports the agent that such a flow delivers
and exhausts, which is 1.7e-33 L over 0.1 s at 1e-30 L/min, within one rounding
of zero. The smallest denormal is one of the flows at which the circuit's time
constant overflows to `inf`. For a 6 L circuit, that happens at every flow less
than about 2e-306 L/min. The circuit's closed form no longer computes that time
constant (`PL-B26Y`, `PL-YT8N`). Each compartment first moves agent at the flow
where its own gap term stops rounding to zero against the amount it holds. For
the circuit that flow is 3.8e-19 L/min, and for the tissue group it is 3.9e-19,
where each moves 8.5e-22 L. For the venous pool it is 4.9e-20 L/min, where it
moves 1.1e-22 L. The walk's grid takes one and three times each power of ten.
On that grid, the circuit and the tissue group first move at 1e-18 L/min and
the venous pool at 1e-19 (bisected over 0.1 s from a fraction of 1e-6 driven by
1.0, 2026-10-12). An epsilon would not remove a discontinuity. It would
introduce one, by freezing flows that the model says still move (`PL-79YX`).
"""
