"""`core/exponential_approach.py`: the first-order approach every patient closed form takes.

Three properties, each measured failing in an arrangement the module refused
(its docstring carries the counts), each pinned here on the case that showed
it, and the bound held across drawn states as well. The compartments that
call it are walked in `tests/unit/test_compartment_primitives.py`.
"""

from math import exp, expm1, inf, ulp

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from anesthesia_sim.core.exponential_approach import exponential_approach

# A step long enough, against this time constant, for `1 - exp(-dt/tau)` to
# round to exactly 1.0: a full approach.
FULL_APPROACH_STEP_S = 60.0
FULL_APPROACH_TIME_CONSTANT_S = 1.0

# Capacities two of the sevoflurane reference patient's tissue groups form, as
# `TissueGroup.capacity_l` forms them, and fractions they can be loaded to from
# which the unbounded far-end sum `a + (c - a)` lands one ulp over `c`:
# `fl(c - a)` is exactly half an ulp of `c` high, and the sum rounds to even.
# The vessel-rich group, 6.0 L at a tissue:gas coefficient of 1.1, does from
# 9.6% of fractions drawn uniformly below a half; the muscle group, 33.0 L at
# 2.4, from 1.6% (200,000 draws each, measured 2026-10-12). A 6 L group at
# 1.0, the one `test_compartment_primitives.py` builds, never does, which is
# why the bound is pinned here on the reference patient's capacities.
OVERSHOOTING_STATES = (
    pytest.param(6.0 * 1.1, 0.3, id="vessel-rich-at-0.3"),
    pytest.param(6.0 * 1.1, 0.000561, id="vessel-rich-at-0.000561"),
    pytest.param(6.0 * 1.1, 0.002774, id="vessel-rich-at-0.002774"),
    pytest.param(33.0 * 2.4, 0.13237844585859004, id="muscle-at-0.132"),
    pytest.param(33.0 * 2.4, 0.07330126944954535, id="muscle-at-0.073"),
)

# Drawn states: amounts in litres either side of one another, steps and time
# constants across the range the compartments form, the infinite time constant
# of zero flow among them.
AMOUNTS_L = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
STEPS_S = st.floats(min_value=1e-3, max_value=1e6, allow_nan=False, allow_infinity=False)
TIME_CONSTANTS_S = st.one_of(
    st.floats(min_value=1e-6, max_value=1e30, allow_nan=False, allow_infinity=False), st.just(inf)
)


@pytest.mark.parametrize(
    ("initial", "equilibrium"), ((0.0, 6.0), (6.0, 0.0), (1.98, 6.6000000000000005), (0.25, 0.25))
)
def test_one_time_constant_closes_the_textbook_share_of_the_gap(
    initial: float, equilibrium: float
) -> None:
    """The arrangement changes the rounding and not the equation.

    Against `M_eq + (M - M_eq) exp(-dt/tau)`, the form `docs/MODEL.md`'s
    balance integrates to, at one time constant.
    """

    textbook = equilibrium + (initial - equilibrium) * exp(-1.0)

    assert exponential_approach(initial, equilibrium, 100.0, 100.0) == pytest.approx(
        textbook, rel=1e-15
    )


@pytest.mark.parametrize(("capacity_l", "loaded_fraction"), OVERSHOOTING_STATES)
def test_a_full_approach_lands_on_the_equilibrium_exactly(
    capacity_l: float, loaded_fraction: float
) -> None:
    """Where the unbounded sum rounds an ulp past the equilibrium, the result is the equilibrium.

    The first assertions are the measurement that makes the bound load-bearing
    rather than cosmetic: at these states the gap factor is exactly 1.0 and
    `a + (c - a) * 1.0` is one ulp of `c` above `c`. Past the capacity, that
    is a write `TissueGroup.__setattr__` refuses, so unbounded, a tissue
    driven to a fraction of one from these states raised from its own closed
    form.
    """

    loaded_amount_l = capacity_l * loaded_fraction
    gap_closed = -expm1(-FULL_APPROACH_STEP_S / FULL_APPROACH_TIME_CONSTANT_S)
    unbounded_l = loaded_amount_l + (capacity_l - loaded_amount_l) * gap_closed

    assert gap_closed == 1.0
    assert unbounded_l == capacity_l + ulp(capacity_l)

    approached_l = exponential_approach(
        loaded_amount_l, capacity_l, FULL_APPROACH_STEP_S, FULL_APPROACH_TIME_CONSTANT_S
    )

    assert approached_l == capacity_l


def test_the_change_is_anchored_at_the_amount_rather_than_at_the_fraction() -> None:
    """Anchoring the fraction and re-forming the amount rounds once more, and can flip the sign.

    The instance: a 6 L capacity holding 1.8134844858482426 L, driven to a
    fraction of one over 1 s against a time constant of 2.76e29 s, so the gap
    factor is 3.6e-30 and leaves the fraction unchanged. Re-formed, the
    amount is `6.0 * (1.8134844858482426 / 6.0)`, one ulp below what was
    held: a return of 2.2e-16 L reported under a gradient driving agent in.
    1,650 of 300,000 random states did the same (measured 2026-10-12).
    """

    capacity_l = 6.0
    held_amount_l = 1.8134844858482426
    step_s = 1.0
    time_constant_s = 2.758981710292717e29
    gap_closed = -expm1(-step_s / time_constant_s)
    held_fraction = held_amount_l / capacity_l
    re_formed_amount_l = capacity_l * (held_fraction + (1.0 - held_fraction) * gap_closed)

    assert re_formed_amount_l - held_amount_l < 0.0

    approached_l = exponential_approach(held_amount_l, capacity_l, step_s, time_constant_s)

    assert approached_l - held_amount_l >= 0.0


@pytest.mark.parametrize(
    ("initial", "equilibrium"),
    ((6e-6, 6.0), (6.0, 6e-6), (0.0, 0.7943), (0.7943, 0.0), (0.25, 0.25)),
)
def test_at_zero_flow_the_result_is_the_start_exactly(initial: float, equilibrium: float) -> None:
    """An infinite time constant closes no part of the gap, bit for bit, with no branch.

    `dt/inf` is `0.0`, `expm1(-0.0)` is `-0.0`, and `initial + gap * 0.0` is
    `initial`. The first pair is the primitives walk's own state: a
    compartment far below the input driving it, where `d + (i - d)` rounds
    and the forms anchored at the driving fraction needed a branch.
    """

    assert exponential_approach(initial, equilibrium, 60.0, inf) == initial


@settings(derandomize=True, database=None, deadline=None, max_examples=500)
@given(initial=AMOUNTS_L, equilibrium=AMOUNTS_L, step_s=STEPS_S, time_constant_s=TIME_CONSTANTS_S)
def test_the_result_lies_between_the_start_and_the_equilibrium(
    initial: float, equilibrium: float, step_s: float, time_constant_s: float
) -> None:
    """Drawn states: the result never crosses either end, so the change has the gradient's sign."""

    approached = exponential_approach(initial, equilibrium, step_s, time_constant_s)

    assert min(initial, equilibrium) <= approached <= max(initial, equilibrium)

    if equilibrium == initial:
        assert approached == initial
