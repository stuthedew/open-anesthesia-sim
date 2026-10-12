"""The first-order approach to a held input that a patient compartment's closed form takes.

`TissueGroup.advance()` and `VenousBloodCompartment.advance()` each solve one
balance `docs/MODEL.md` states against a constant stated input - a held
arterial fraction, a held tissue-return fraction - and the two balances have
one solution: the amount held approaches the amount the compartment would hold
at equilibrium with its input, closing a fixed share of the gap per time
constant,

    M(t + dt) = M(t) + (M_eq - M(t)) (1 - exp(-dt / tau)) .

`exponential_approach` is that line, written once for both compartments, in
the one arrangement of it found to hold three properties the arithmetic owes
the physics. Each was measured failing in an arrangement this one replaced
(`PL-XWFP`), and `tests/unit/test_exponential_approach.py` pins each on the
case that showed it.

**Anchored at the amount held, so the change has the gradient's sign.**
Written `M_eq + (M(t) - M_eq) exp(-dt/tau)`, the textbook form, the result
rounds at the scale of the equilibrium rather than of the amount held, and
where `dt/tau` is small the compartment can land below where it started while
its input is above it: uptake reported as a return, which the physics forbids.
On the walk the item records - flows from 1e-30 to 3 L/min, steps of 0.1 to
60 s, five states - a 6 L tissue group reported the wrong sign in 100 of 900
cases and a 1.222 L venous pool in 94 (measured 2026-10-11). Anchored at
`M(t)`, with `1 - exp(-dt/tau)` taken by `expm1` so that it is exact where it
is small, the result is `M(t)` plus one term carrying the gradient's sign, and
it rounds at the scale of `M(t)`. The *amount* is what is anchored: anchoring
the fraction the same way and re-forming the amount as `capacity * fraction`
rounds once more, at the capacity's scale, and 1,650 of 300,000 random states
came back with the wrong sign that way (measured 2026-10-12).

**Bounded at the equilibrium, so a full approach lands on it exactly.** Where
`1 - exp(-dt/tau)` rounds to 1.0 the sum is `M(t) + fl(M_eq - M(t))`, and the
subtraction can round exactly half an ulp of `M_eq` high; the sum then rounds
to the even neighbour, one ulp past the equilibrium. The sevoflurane
reference patient's vessel-rich group has a capacity of `6.0 * 1.1`, which is
6.6000000000000005 L, and from 9.6% of the fractions below a half it could
be loaded to, a full approach lands an ulp over that capacity; its 79.2 L
muscle group does from 1.6% (200,000 fractions drawn uniformly each, measured
2026-10-12). An ulp over capacity is a write
`TissueGroup.__setattr__` refuses, so unbounded, a closed form driven all the
way to a fraction of one raises on its way in. Bounded, the result lies
between `M(t)` and `M_eq` inclusive, in either direction, and nothing else
changes: the bound binds only where the sum has crossed.

**Exact at zero flow, with no branch.** The time constant of an unperfused
compartment is `inf` (`TissueGroup.time_constant_s`), `dt/inf` is `0.0`,
`expm1(-0.0)` is `-0.0`, and the result is `M(t) + (M_eq - M(t)) * 0.0`,
which is `M(t)` exactly whatever the two amounts are; the change the
compartment reports is then exactly zero, `docs/MODEL.md`'s `dM_i/dt = 0`
held exactly. `core/__init__.py` § "Zero flow is tested with `== 0.0`, never
against a tolerance" is the account of the two guards this retired, and of
why the one in `time_constant_s` stays.
"""

from math import expm1


def exponential_approach(
    initial: float, equilibrium: float, step_s: float, time_constant_s: float
) -> float:
    """Advance `initial` toward `equilibrium` by one step of the first-order approach.

    Returns `initial + (equilibrium - initial) * (1 - exp(-step_s /
    time_constant_s))`, never past `equilibrium`: the result lies between the
    two inclusive, and is `initial` exactly where `time_constant_s` is `inf`.
    The module docstring says why it is arranged so.

    Checks nothing itself: each caller has refused a step that is not positive
    and finite, and a flow that is negative or not finite, before forming the
    time constant, which is positive, and `inf` at zero flow.
    """

    gap_closed = -expm1(-step_s / time_constant_s)
    approached = initial + (equilibrium - initial) * gap_closed

    if equilibrium >= initial:
        return min(approached, equilibrium)

    return max(approached, equilibrium)
