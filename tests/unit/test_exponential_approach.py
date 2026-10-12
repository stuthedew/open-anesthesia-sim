"""`core/exponential_approach.py`: the first-order approach every patient closed form takes.

Four properties, each measured failing in an arrangement the module refused
(its docstring carries the counts), each pinned here on the case that showed
it, and the interval held across drawn states as well. The compartments that
call it are walked in `tests/unit/test_compartment_primitives.py`.
"""

from decimal import Decimal, getcontext
from math import exp, expm1, inf, log, ulp

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from anesthesia_sim.core.exponential_approach import HALF_THE_GAP, exponential_approach

# A step long enough, against this time constant, for `1 - exp(-dt/tau)` to
# round to exactly 1.0: a full approach.
FULL_APPROACH_STEP_S = 60.0
FULL_APPROACH_TIME_CONSTANT_S = 1.0

# The time constant the share-of-the-gap test steps against, and the step at
# which the form switches anchor: ln 2 time constants, where `1 - exp(-dt/tau)`
# is a half - exactly, on glibc 2.39 (measured 2026-10-12), and within an ulp
# of it on any libm faithful to the last place, which is what is asserted.
TIME_CONSTANT_S = 100.0
SWITCH_STEP_S = log(2.0) * TIME_CONSTANT_S

# States and step lengths, in time constants, the result is held against the
# balance's solution taken to 40 digits. The first five are the states the
# other tests use; the last two are where a form switching anchor at three
# quarters of the gap, rather than a half, errs by 3.5 and 3.4 ulps at the two
# longest of the step lengths named with them (searched 2026-10-12 over
# 400,000 states of 1e-6 to 1,000 L): formed from the amount held there, its
# term is three times its result. Nothing below a normal double: past about
# 708 time constants the residual is subnormal and carries no precision.
ACCURACY_STATES = (
    pytest.param(0.0, 6.0, id="filling-from-empty"),
    pytest.param(6.0, 0.0, id="washing-out-to-empty"),
    pytest.param(6e-6, 6.0, id="filling-from-nearly-empty"),
    pytest.param(6.0, 6e-6, id="washing-out-to-nearly-empty"),
    pytest.param(1.98, 6.6000000000000005, id="vessel-rich-from-0.3"),
    pytest.param(2.865236619137837, 1.0263801144272433e-06, id="searched-washout"),
    pytest.param(199.0548618593574, 2.8869751106010743e-06, id="searched-muscle-washout"),
)
ACCURACY_LENGTHS_IN_TIME_CONSTANTS = (
    0.01,
    0.3,
    0.5,
    log(2.0),
    0.75,
    1.0,
    1.3173995853597509,
    1.343196842430155,
    2.0,
    5.0,
    20.0,
    40.0,
)
# Three ulps: the bound a form of four roundings owes under a libm faithful to
# the last place, and two under one correctly rounded. Measured 2026-10-12 on
# glibc 2.39, the worst case here is 1.6 ulps.
ACCURACY_BOUND_ULPS = 3

# Capacities two of the sevoflurane reference patient's tissue groups form, as
# `TissueGroup.capacity_l` forms them, and fractions they can be loaded to from
# which the full-approach sum formed from the amount held, `a + (c - a) * 1.0`,
# lands one ulp over `c`: `fl(c - a)` is exactly half an ulp of `c` high, and
# the sum rounds to even. The vessel-rich group, 6.0 L at a tissue:gas
# coefficient of 1.1, does from 9.6% of fractions drawn uniformly below a
# half; the muscle group, 33.0 L at 2.4, from 1.6% (200,000 draws each,
# measured 2026-10-12). A 6 L group at 1.0, the one
# `test_compartment_primitives.py` builds, never does, which is why the
# landing is pinned here on the reference patient's capacities.
OVERSHOOTING_STATES = (
    pytest.param(6.0 * 1.1, 0.3, id="vessel-rich-at-0.3"),
    pytest.param(6.0 * 1.1, 0.000561, id="vessel-rich-at-0.000561"),
    pytest.param(6.0 * 1.1, 0.002774, id="vessel-rich-at-0.002774"),
    pytest.param(33.0 * 2.4, 0.13237844585859004, id="muscle-at-0.132"),
    pytest.param(33.0 * 2.4, 0.07330126944954535, id="muscle-at-0.073"),
)

# Washouts from 6 L toward empty, in time constants, and the residual each
# leaves. The sum formed from the amount held, `6 + (0 - 6) * g`, carries the
# first to 2.1e-9 of itself and the second to 2.3e-4, rounding at the scale of
# the 6 L; from 37.43 time constants `g` rounds to 1.0 and the sum is exactly
# 0.0 (measured 2026-10-12).
WASHOUT_LENGTHS_IN_TIME_CONSTANTS = (20.0, 30.0, 40.0, 60.0)

# Drawn states: amounts in litres either side of one another, steps and time
# constants across the range the compartments form, the infinite time constant
# of zero flow among them.
AMOUNTS_L = st.floats(min_value=0.0, max_value=1e3, allow_nan=False, allow_infinity=False)
STEPS_S = st.floats(min_value=1e-3, max_value=1e6, allow_nan=False, allow_infinity=False)
TIME_CONSTANTS_S = st.one_of(
    st.floats(min_value=1e-6, max_value=1e30, allow_nan=False, allow_infinity=False), st.just(inf)
)


@pytest.mark.parametrize(
    "step_s",
    (SWITCH_STEP_S / 2.0, SWITCH_STEP_S, TIME_CONSTANT_S),
    ids=("formed-from-the-amount", "at-the-switch", "formed-from-the-equilibrium"),
)
@pytest.mark.parametrize(
    ("initial", "equilibrium"), ((0.0, 6.0), (6.0, 0.0), (1.98, 6.6000000000000005), (0.25, 0.25))
)
def test_either_form_closes_the_textbook_share_of_the_gap(
    initial: float, equilibrium: float, step_s: float
) -> None:
    """The arrangement changes the rounding and not the equation.

    Against `M_eq + (M - M_eq) exp(-dt/tau)`, the form `docs/MODEL.md`'s
    balance integrates to, at a step formed from the amount held, at the
    switch, and at one time constant, formed from the equilibrium.
    """

    textbook = equilibrium + (initial - equilibrium) * exp(-step_s / TIME_CONSTANT_S)

    assert exponential_approach(initial, equilibrium, step_s, TIME_CONSTANT_S) == pytest.approx(
        textbook, rel=1e-15
    )


@pytest.mark.parametrize(
    ("initial", "equilibrium"),
    ((0.0, 6.0), (6.0, 0.0), (1.98, 6.6000000000000005), (6e-6, 6.0), (6.0, 6e-6)),
)
def test_the_two_forms_agree_where_the_anchor_switches(initial: float, equilibrium: float) -> None:
    """At ln 2 time constants the gap closed is a half, and the two forms agree.

    The switch is the arrangement's one free choice, placed where the term
    each form adds is the same size, so that nothing jumps across it: the two
    forms agree there to within an ulp of the larger amount, and the result is
    one of them. The half is asserted to within an ulp rather than exactly,
    because exactly is a fact about one libm (`SWITCH_STEP_S`).
    """

    gap_closed = -expm1(-SWITCH_STEP_S / TIME_CONSTANT_S)
    remaining = exp(-SWITCH_STEP_S / TIME_CONSTANT_S)

    assert abs(gap_closed - HALF_THE_GAP) <= ulp(HALF_THE_GAP)
    assert abs(remaining - HALF_THE_GAP) <= ulp(HALF_THE_GAP)

    from_the_amount = initial + (equilibrium - initial) * gap_closed
    from_the_equilibrium = equilibrium + (initial - equilibrium) * remaining
    approached = exponential_approach(initial, equilibrium, SWITCH_STEP_S, TIME_CONSTANT_S)

    assert approached in (from_the_amount, from_the_equilibrium)
    assert abs(from_the_amount - from_the_equilibrium) <= ulp(max(initial, equilibrium))


@pytest.mark.parametrize("length_in_time_constants", ACCURACY_LENGTHS_IN_TIME_CONSTANTS)
@pytest.mark.parametrize(("initial", "equilibrium"), ACCURACY_STATES)
def test_the_result_is_within_three_ulps_of_the_balance_solution(
    initial: float, equilibrium: float, length_in_time_constants: float
) -> None:
    """Against the balance's solution taken to 40 digits, at every state and length named above.

    The four properties pinned above are exact facts at special points; this
    is the accuracy everywhere between them, which the switch at a half is
    what buys: a form switching at three quarters errs by 3.5 ulps at the
    searched states, carrying a term three times its result. The bound admits
    a switch anywhere up to a half, each of which is within it.
    """

    getcontext().prec = 40
    step_s = length_in_time_constants
    time_constant_s = 1.0
    reference = (
        Decimal(equilibrium) + (Decimal(initial) - Decimal(equilibrium)) * (-Decimal(step_s)).exp()
    )

    approached = exponential_approach(initial, equilibrium, step_s, time_constant_s)

    assert abs(Decimal(approached) - reference) <= ACCURACY_BOUND_ULPS * Decimal(
        ulp(float(reference))
    )


@pytest.mark.parametrize(("capacity_l", "loaded_fraction"), OVERSHOOTING_STATES)
def test_a_full_approach_lands_on_the_equilibrium_exactly(
    capacity_l: float, loaded_fraction: float
) -> None:
    """Where the sum formed from the amount held lands an ulp over, the result is the equilibrium.

    The first assertions are the measurement that makes the form taken from
    the equilibrium load-bearing rather than cosmetic: at these states the
    gap factor is exactly 1.0 and `a + (c - a) * 1.0` is one ulp of `c`
    above `c`. Past the capacity, that is a write `TissueGroup.__setattr__`
    refuses, so formed from the amount throughout, a tissue driven to a
    fraction of one from these states raised from its own closed form.
    """

    loaded_amount_l = capacity_l * loaded_fraction
    gap_closed = -expm1(-FULL_APPROACH_STEP_S / FULL_APPROACH_TIME_CONSTANT_S)
    from_the_amount_l = loaded_amount_l + (capacity_l - loaded_amount_l) * gap_closed

    assert gap_closed == 1.0
    assert from_the_amount_l == capacity_l + ulp(capacity_l)

    approached_l = exponential_approach(
        loaded_amount_l, capacity_l, FULL_APPROACH_STEP_S, FULL_APPROACH_TIME_CONSTANT_S
    )

    assert approached_l == capacity_l


@pytest.mark.parametrize("length_in_time_constants", WASHOUT_LENGTHS_IN_TIME_CONSTANTS)
def test_a_long_washout_keeps_its_residual(length_in_time_constants: float) -> None:
    """Formed from the equilibrium, the residual is a product and keeps its own precision.

    The first assertion is the measurement that makes that form load-bearing
    at long steps: formed from the 6 L held, the same step carries the
    residual to no better than a part in 1e9, and from 37.43 time constants
    reports exactly 0.0. The reference is the balance's solution taken to 28
    digits.
    """

    held_amount_l = 6.0
    time_constant_s = 1.0
    step_s = length_in_time_constants * time_constant_s
    residual_reference_l = Decimal(held_amount_l) * (-Decimal(step_s)).exp()
    from_the_amount_l = held_amount_l + (0.0 - held_amount_l) * -expm1(-step_s / time_constant_s)

    assert abs(Decimal(from_the_amount_l) - residual_reference_l) > residual_reference_l * Decimal(
        1e-9
    )

    approached_l = exponential_approach(held_amount_l, 0.0, step_s, time_constant_s)

    assert abs(Decimal(approached_l) - residual_reference_l) < residual_reference_l * Decimal(1e-15)


def test_a_short_step_closes_its_share_of_the_gap_exactly() -> None:
    """`1 - exp(-dt/tau)` taken by `expm1` is exact where taken as written it is zero.

    A step of 1e-20 time constants from empty toward 1 L closes 1e-20 L, bit
    for bit; `1.0 - exp(-1e-20)` is 0.0, and a form taking its factor so
    moves nothing at all.
    """

    assert 1.0 - exp(-1e-20) == 0.0
    assert exponential_approach(0.0, 1.0, 1e-20, 1.0) == 1e-20


def test_the_change_is_anchored_at_the_amount_rather_than_at_the_fraction() -> None:
    """Anchoring the fraction and re-forming the amount rounds once more, and can flip the sign.

    The instance: a 6 L capacity holding 1.8134844858482426 L, driven to a
    fraction of one over 1 s against a time constant of 2.76e29 s, so the gap
    factor is 3.6e-30 and leaves the fraction unchanged. Re-formed, the
    amount is `6.0 * (1.8134844858482426 / 6.0)`, one ulp below what was
    held: a return of 2.2e-16 L reported under a gradient driving agent in
    (measured 2026-10-12).
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

    `dt/inf` is `0.0`, `expm1(-0.0)` is `-0.0`, the step is formed from the
    amount held, and `initial + gap * 0.0` is `initial`. The first pair is
    the primitives walk's own state: a compartment far below the input
    driving it, where `d + (i - d)` rounds and the forms anchored at the
    driving fraction needed a branch.
    """

    assert exponential_approach(initial, equilibrium, 60.0, inf) == initial


@settings(derandomize=True, database=None, deadline=None, max_examples=500)
@given(initial=AMOUNTS_L, equilibrium=AMOUNTS_L, step_s=STEPS_S, time_constant_s=TIME_CONSTANTS_S)
def test_the_result_lies_between_the_start_and_the_equilibrium(
    initial: float, equilibrium: float, step_s: float, time_constant_s: float
) -> None:
    """Drawn states: the result never crosses either end, so the change has the gradient's sign.

    Where `exp(-dt/tau)` underflows the step is a full approach, and lands on
    the equilibrium exactly.
    """

    approached = exponential_approach(initial, equilibrium, step_s, time_constant_s)

    assert min(initial, equilibrium) <= approached <= max(initial, equilibrium)

    if equilibrium == initial:
        assert approached == initial

    if exp(-step_s / time_constant_s) == 0.0:
        assert approached == equilibrium
