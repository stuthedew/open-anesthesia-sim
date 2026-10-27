"""The first-order approach toward a constant input, used by every compartment's closed form.

`TissueGroup.advance()` and `VenousBloodCompartment.advance()` each solve one
balance that `docs/MODEL.md` states, against an input held constant over the
step: a constant arterial fraction for a tissue group, and a constant
tissue-return fraction for the venous pool. The two balances have the same
solution. The amount in the compartment approaches the amount it would hold at
equilibrium with its input, and it closes a fixed share of the remaining gap
in each time constant:

    M(t + dt) = M(t) + (M_eq - M(t)) (1 - exp(-dt / tau)) .

`BreathingCircuit.advance_fresh_gas()` solves the same balance for the circuit
with no patient connected, against the dial's fraction held constant over the
step (`PL-CQ1M`).

`exponential_approach` computes that line, written once for all three
compartments. `exponential_approach_in_time_constants` is the same line taken
with the step already expressed in time constants, `dt/tau`. The circuit calls
that form, because it never forms its time constant. Its time constant is the
circuit volume divided by the fresh gas flow, which overflows to `inf` when
the flow is below about 2e-306 L/min in a 6 L circuit (`PL-B26Y`). The
circuit forms `dt/tau` directly instead, as the gas the step admits divided by
the circuit volume. It uses the one arrangement of the line that was found to keep
four properties that the arithmetic owes the physics. Each property was
measured failing in an arrangement that this one replaced (`PL-XWFP`).
`tests/unit/test_exponential_approach.py` tests each property on the case that
showed the failure.

**Two forms of one line, each anchored at the nearer end.** A step that closes
up to half the gap is formed from the amount held, as `M(t) + (M_eq - M(t)) g`,
where `g = 1 - exp(-dt/tau)` is computed with `expm1`. For such a step,
`1 - exp(-dt/tau)` is a half or less, so the step is at most ln 2 time
constants long. A longer step is formed from the equilibrium, as
`M_eq + (M(t) - M_eq) exp(-dt/tau)`, the textbook form. Each form is its
anchor plus one term. The term is a product, so it carries the sign of the gap
exactly. Its factor is at most a half, to within a rounding, so the term is at
most half the gap in size. The exact sum therefore lies between the two
amounts. Rounding is monotone, so the rounded result lies between them too,
and nothing needs to be clamped. The switch sits where the terms that the two
forms add are the same size. `g` and `exp(-dt/tau)` are each computed
directly, rather than one as one minus the other. So the factor is exact where
its form is used: `expm1` where `dt/tau` is small, and `exp` where it is large.
A measurement drew 2,000,000 states at random. Their amounts ran from 0 to 1,000 L on either
side of one another, with adjacent doubles among them. Their steps ran from
1e-3 to 1e6 s, and their time constants from 1e-6 to 1e30 s and `inf`. None
left the interval, none moved against the gradient, none moved at zero flow,
and none landed off the equilibrium where `exp(-dt/tau)` underflows (measured
2026-10-12).

**The change has the sign of the gradient, so uptake is never reported as a
return.** An earlier arrangement wrote each closed form on the fraction, as
`d + (i - d) exp(-dt/tau)`. It rounded at the scale of the driving fraction
rather than at the scale of the compartment's own fraction. Where `dt/tau` was
small, the compartment could then end below where it started while its input
was above it. The item records a walk over flows from 1e-30 to 3 L/min, steps
of 0.1 to 60 s and five states. On that walk, a 6 L tissue group reported the
wrong sign in 100 of 930 cases, and a 1.222 L venous pool did so in 94
(measured 2026-10-11; the item's brief counts the same walk as 900). Anchored
at the nearer end, the result is that end plus a term with the sign of the
gradient. The *amount* is what is anchored. Anchoring the fraction the same
way, and then re-forming the amount as `capacity * fraction`, rounds once
more, at the scale of the capacity. That extra rounding can leave the result
below the amount held while the input is above it. In the test's instance, the
re-formed amount comes back 2.2e-16 L lower, and the amount anchored directly
comes back unchanged (measured 2026-10-12).

**A full approach lands on the equilibrium exactly.** Suppose the step were
formed from the amount held for every step length. Where `g` rounds to 1.0,
the sum is `M(t) + fl(M_eq - M(t))`. The subtraction can round exactly half an
ulp of `M_eq` high, and the sum then rounds to the even neighbour, one ulp past
the equilibrium. The sevoflurane reference patient's vessel-rich group has a
capacity of `6.0 * 1.1`, which is 6.6000000000000005 L. Formed that way, a
full approach lands one ulp over that capacity when it starts from 9.6% of the
fractions below a half that the group could be loaded to. It lands one ulp
under the capacity from another 9.6%. For the 79.2 L muscle group, the shares
are 1.6% over and 1.5% under (200,000 fractions drawn uniformly for each group,
measured 2026-10-12). An amount one ulp over capacity is a write that
`TissueGroup.__setattr__` rejects. So a closed form written that way, and
driven all the way to a fraction of one, raised an error on its way in.
Formed from the equilibrium, a full approach where `exp(-dt/tau)` underflows
is `M_eq + (M(t) - M_eq) * 0.0`, which is `M_eq` exactly. Before that point,
when filling toward a capacity, the result from the step at which `g` rounds
to 1.0 onward is `M_eq` plus a term smaller than half an ulp of `M_eq`. That
sum rounds to `M_eq`.

**A long washout keeps its residual.** A step of twenty time constants from
6 L toward empty leaves 1.2e-8 L. The sum formed from the amount held,
`6 + (0 - 6) g`, gives that residual with a relative error of 2.1e-9, because
it rounds at the scale of the 6 L. Thirty time constants leave 5.6e-13 L, which
that sum gives with a relative error of 2.3e-4 for the same reason. From 37.43
time constants, `g` rounds to 1.0 and the sum is exactly 0.0, whereas forty
time constants leave 2.5e-17 L. Formed from the equilibrium, the residual is
the product `(M(t) - M_eq) exp(-dt/tau)`. Its relative error is within 7.5e-17
at every one of those lengths, and within 2e-16 at any length whose residual is
a normal double, up to about 708 time constants (measured 2026-10-12 against a
40-digit reference). `tests/unit/test_exponential_approach.py` also holds the result to
within three ulps of that reference between those special points.
`docs/MODEL.md`'s balances have no step at which a perfused compartment is
exactly empty, and the closed form reports none. The circuit's washout keeps
its residual the same way. A bare 6 L circuit at 4 L/min, washed out from a
fraction of 1.0 under a dial of zero, holds 4.2e-18 after forty time
constants, where its own earlier sum reported exactly 0.0 (measured
2026-10-17, `PL-CQ1M`).

**The circuit anchors its fraction, and that is anchoring what it stores.** The
patient compartments store an amount, so the amount is what they anchor, for
the reason given above. The circuit stores its inspired fraction and derives
its amount from it as `circuit_volume_l * fraction`. So the fraction is the
value that the circuit holds, and anchoring it re-forms nothing. The
circuit's exhaust is a separate sum of terms that cannot be negative, and the
circuit computes it itself.

**Exact at zero flow, with no branch.** The time constant of an unperfused
compartment is `inf` (`TissueGroup.time_constant_s`). Then `dt/inf` is `0.0`
and `expm1(-0.0)` is `-0.0`, so `g` is `0.0` and the step is formed from the
amount held. The result is `M(t) + (M_eq - M(t)) * 0.0`, which is `M(t)`
exactly, whatever the two amounts are. The change that the compartment reports
is then exactly zero, so `docs/MODEL.md`'s `dM_i/dt = 0` is met exactly.
`core/__init__.py` § "Zero flow is tested with `== 0.0`, never against a tolerance"
describes the two guards that this arrangement retired, and why the guard in
`time_constant_s` stays.
"""

from math import exp, expm1
from typing import Final

# The share of the gap at which the step switches its anchor from the amount
# held to the equilibrium. A step closes half the gap at ln 2 time constants,
# where the terms that the two forms add are the same size.
HALF_THE_GAP: Final = 0.5


def exponential_approach(
    initial: float, equilibrium: float, step_s: float, time_constant_s: float
) -> float:
    """Advance `initial` toward `equilibrium` by one step of the first-order approach.

    Returns `initial + (equilibrium - initial) * (1 - exp(-step_s /
    time_constant_s))`. The result is formed from `initial` while the step
    closes up to half the gap, and from `equilibrium` beyond that. So the
    result lies between the two, inclusive. It is `initial` exactly where
    `time_constant_s` is `inf`, and `equilibrium` exactly where
    `exp(-step_s / time_constant_s)` underflows. The module docstring says why
    it is arranged this way.

    This function checks nothing itself. Before forming the time constant,
    each caller has rejected a step that is not positive and finite, and a
    flow that is negative or not finite. So the time constant is positive, and
    it is `inf` at zero flow.
    """

    return exponential_approach_in_time_constants(initial, equilibrium, step_s / time_constant_s)


def exponential_approach_in_time_constants(
    initial: float, equilibrium: float, time_constants_elapsed: float
) -> float:
    """Advance `initial` toward `equilibrium` by a step of `time_constants_elapsed`, or dt/tau.

    This is `exponential_approach` for a caller that has the step in time
    constants but not the time constant itself. The result is the same line,
    with the same two anchors and the same four properties. It is `initial`
    exactly where `time_constants_elapsed` is zero, and `equilibrium` exactly
    where `exp(-time_constants_elapsed)` underflows.
    `BreathingCircuit.advance_fresh_gas()` calls it, for the reason that the
    module docstring gives.

    This function checks nothing itself. Each caller has already made
    `time_constants_elapsed` zero or positive, and not `nan`.
    """

    gap_closed = -expm1(-time_constants_elapsed)

    if gap_closed <= HALF_THE_GAP:
        return initial + (equilibrium - initial) * gap_closed

    return equilibrium + (initial - equilibrium) * exp(-time_constants_elapsed)
