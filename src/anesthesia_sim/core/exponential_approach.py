"""The first-order approach to a held input that a patient compartment's closed form takes.

`TissueGroup.advance()` and `VenousBloodCompartment.advance()` each solve one
balance `docs/MODEL.md` states against a constant stated input - a held
arterial fraction, a held tissue-return fraction - and the two balances have
one solution: the amount held approaches the amount the compartment would hold
at equilibrium with its input, closing a fixed share of the gap per time
constant,

    M(t + dt) = M(t) + (M_eq - M(t)) (1 - exp(-dt / tau)) .

`exponential_approach` is that line, written once for both compartments, in
the one arrangement of it found to hold four properties the arithmetic owes
the physics. Each was measured failing in an arrangement this one replaced
(`PL-XWFP`), and `tests/unit/test_exponential_approach.py` pins each on the
case that showed it.

**Two forms of one line, each anchored at the nearer end.** A step closing up
to half the gap - `1 - exp(-dt/tau)` of a half or less, which is a step of up
to ln 2 time constants - is formed from the amount held, `M(t) + (M_eq -
M(t)) g`, with `g = 1 - exp(-dt/tau)` taken by `expm1`; a longer step is
formed from the equilibrium, `M_eq + (M(t) - M_eq) exp(-dt/tau)`, the
textbook form. Either is its anchor plus one term. The term is a product, so
it carries the gap's sign exactly, and its factor is at most a half, within a
rounding, so it is at most half the gap in size: the exact sum lies between
the two amounts, and rounding is monotone, so the result does too, with
nothing clamped. The switch sits where the term either form adds is the same
size, and `g` and `exp(-dt/tau)` are each taken directly rather than one as
one minus the other, so the factor is exact where its form is used: `expm1`
where `dt/tau` is small, `exp` where it is large. 2,000,000 drawn states -
amounts from 0 to 1,000 L either side of one another, adjacent doubles among
them, steps of 1e-3 to 1e6 s, time constants of 1e-6 to 1e30 s and `inf` -
left the interval in none, moved against the gradient in none, moved at zero
flow in none, and landed off the equilibrium where `exp(-dt/tau)` underflows
in none (measured 2026-10-12).

**The change has the gradient's sign, so uptake is never reported as a
return.** Written on the fraction as `d + (i - d) exp(-dt/tau)`, each closed
form rounded at the scale of the driving fraction rather than of the
compartment's own, and where `dt/tau` was small the compartment could land
below where it started while its input was above it. On the walk the item
records - flows from 1e-30 to 3 L/min, steps of 0.1 to 60 s, five states - a
6 L tissue group reported the wrong sign in 100 of 930 cases and a 1.222 L
venous pool in 94 (measured 2026-10-11; the item's brief counts the same walk
as 900). Anchored at the nearer end, the result is that end plus a term of the
gradient's sign. The *amount* is what is anchored: anchoring the fraction the
same way and re-forming the amount as `capacity * fraction` rounds once more,
at the capacity's scale, and can land below the amount held while the input
is above it: the test's instance comes back 2.2e-16 L lower re-formed, and
unchanged anchored at the amount (measured 2026-10-12).

**A full approach lands on the equilibrium exactly.** Formed from the amount
held throughout, where `g` rounds to 1.0 the sum is `M(t) + fl(M_eq - M(t))`,
the subtraction can round exactly half an ulp of `M_eq` high, and the sum then
rounds to the even neighbour, one ulp past the equilibrium. The sevoflurane
reference patient's vessel-rich group has a capacity of `6.0 * 1.1`, which is
6.6000000000000005 L, and from 9.6% of the fractions below a half it could be
loaded to, a full approach so formed lands an ulp over that capacity, and an
ulp under it from 9.6% more; its 79.2 L muscle group does from 1.6% and 1.5%
(200,000 fractions drawn uniformly each, measured 2026-10-12). An ulp over
capacity is a write
`TissueGroup.__setattr__` refuses, so a closed form so written and driven all
the way to a fraction of one raised on its way in. Formed from the
equilibrium, a full approach is `M_eq + (M(t) - M_eq) * 0.0` where
`exp(-dt/tau)` underflows, which is `M_eq` exactly, and before that, filling
toward a capacity, `M_eq` plus a term below half its ulp from the step at
which `g` rounds to 1.0, which rounds to `M_eq`.

**A long washout keeps its residual.** A step of twenty time constants from
6 L toward empty leaves 1.2e-8 L, which the sum formed from the amount held,
`6 + (0 - 6) g`, carries to 2.1e-9 of itself, since it rounds at the scale of
the 6 L; thirty leave 5.6e-13 L, carried to 2.3e-4 of itself; from 37.43 time
constants `g` rounds to 1.0 and the sum is exactly 0.0, where forty leave
2.5e-17 L. Formed from the equilibrium, the residual is the product `(M(t) -
M_eq) exp(-dt/tau)`, within 7.5e-17 of itself at every one of those lengths
and within 2e-16 at any length whose residual is a normal double, up to about
708 time constants (measured 2026-10-12 against a 40-digit reference).
`tests/unit/test_exponential_approach.py` holds the result to three ulps of
that reference between the special points as well. `docs/MODEL.md`'s
balances have no step at which a perfused compartment is exactly empty, and
the closed form reports none.

**Exact at zero flow, with no branch.** The time constant of an unperfused
compartment is `inf` (`TissueGroup.time_constant_s`), `dt/inf` is `0.0`,
`expm1(-0.0)` is `-0.0`, so `g` is `0.0`, the step is formed from the amount
held, and the result is `M(t) + (M_eq - M(t)) * 0.0`, which is `M(t)` exactly
whatever the two amounts are; the change the compartment reports is then
exactly zero, `docs/MODEL.md`'s `dM_i/dt = 0` held exactly. `core/__init__.py`
§ "Zero flow is tested with `== 0.0`, never against a tolerance" is the
account of the two guards this retired, and of why the one in
`time_constant_s` stays.
"""

from math import exp, expm1
from typing import Final

# The share of the gap a step closes at which the form switches anchor, from
# the amount held to the equilibrium: a half, reached at ln 2 time constants,
# where the term either form adds is the same size.
HALF_THE_GAP: Final = 0.5


def exponential_approach(
    initial: float, equilibrium: float, step_s: float, time_constant_s: float
) -> float:
    """Advance `initial` toward `equilibrium` by one step of the first-order approach.

    Returns `initial + (equilibrium - initial) * (1 - exp(-step_s /
    time_constant_s))`, formed from `initial` while the step closes up to half
    the gap and from `equilibrium` beyond that, so that the result lies
    between the two inclusive, is `initial` exactly where `time_constant_s` is
    `inf`, and is `equilibrium` exactly where `exp(-step_s / time_constant_s)`
    underflows. The module docstring says why it is arranged so.

    Checks nothing itself: each caller has refused a step that is not positive
    and finite, and a flow that is negative or not finite, before forming the
    time constant, which is positive, and `inf` at zero flow.
    """

    gap_closed = -expm1(-step_s / time_constant_s)

    if gap_closed <= HALF_THE_GAP:
        return initial + (equilibrium - initial) * gap_closed

    return equilibrium + (initial - equilibrium) * exp(-step_s / time_constant_s)
