"""Unit tests for `app/wash_in.py`, the F_A/F_I ratio and its domain.

`docs/MODEL.md` § "F_A/F_I as a displayed ratio" reasons about this module,
so the claims it makes are checked here against the functions that make
them, without constructing a Flet interface. The end-to-end path - real
controller, real steps, the trace and the sentence beside it - is in
`tests/unit/test_simulation_view.py`.

The published values these tests compare against are the ones
`docs/MODEL.md` § "Published wash-in and elimination validation test" already cites; this
file does not restate the citation, it only shows that the displayed ratio
is the same quantity that test validates.
"""

import pytest

from anesthesia_sim.app.formatting import CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
from anesthesia_sim.app.wash_in import (
    WASH_IN_DENOMINATOR_FLOOR_FRACTION,
    WASH_IN_EQUILIBRIUM_RATIO,
    WashInDomain,
    is_wash_in,
    read_wash_in,
    wash_in_ratio,
)


def test_the_ratio_is_the_plain_quotient_of_the_two_fractions() -> None:
    """No scaling, no percent, no rounding: one fraction over the other."""

    assert wash_in_ratio(0.0147, 0.0173) == pytest.approx(0.0147 / 0.0173)
    assert wash_in_ratio(0.0, 0.02) == 0.0
    assert wash_in_ratio(0.02, 0.02) == 1.0


def test_the_denominator_floor_is_the_displayed_resolution() -> None:
    """Derived, not chosen beside it.

    A second independently chosen constant would let the two drift, so
    that a ratio could be formed from an inspired concentration the
    interface itself renders as `0.00%`.
    """

    assert WASH_IN_DENOMINATOR_FLOOR_FRACTION == pytest.approx(
        CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / 100.0
    )


def test_no_ratio_is_formed_from_an_empty_circuit() -> None:
    """The 0/0 at the start of every run must not reach the chart.

    `CLAUDE.md` prefers an obvious absence to a plausible-looking number,
    and there is no defensible number here: nothing has been inspired, so
    there is nothing for the alveolar fraction to be a fraction *of*.
    """

    assert wash_in_ratio(0.0, 0.0) is None
    assert read_wash_in(0.0, 0.0).domain is WashInDomain.NO_INSPIRED_AGENT
    assert read_wash_in(0.0, 0.0).plotted_ratio is None


def test_no_ratio_is_formed_below_the_denominator_floor() -> None:
    """The floor is a floor, not a guard against exact zero alone."""

    just_under = WASH_IN_DENOMINATOR_FLOOR_FRACTION * 0.99

    assert wash_in_ratio(just_under / 2.0, just_under) is None
    assert read_wash_in(0.0, just_under).domain is WashInDomain.NO_INSPIRED_AGENT

    # At the floor exactly, the quotient is a number again.
    assert wash_in_ratio(
        WASH_IN_DENOMINATOR_FLOOR_FRACTION / 2.0, WASH_IN_DENOMINATOR_FLOOR_FRACTION
    ) == pytest.approx(0.5)


def test_the_trace_stops_where_alveolar_exceeds_inspired() -> None:
    """Above 1 the run is eliminating agent, and this is not a wash-in.

    The arithmetic still gives a number, and that number is meaningful -
    it is just not a wash-in fraction, so it must not be drawn on a curve
    whose whole claim is that it is the textbook wash-in graph. It is
    excluded rather than clamped: a value pinned to 1.0 would draw a
    completed wash-in that the run never reached.
    """

    reading = read_wash_in(0.0090, 0.0030)

    assert reading.domain is WashInDomain.ELIMINATION
    assert reading.plotted_ratio is None
    # The quotient itself is still available, and is not clamped.
    assert wash_in_ratio(0.0090, 0.0030) == pytest.approx(3.0)


def test_equilibrium_is_inside_the_domain() -> None:
    """F_A = F_I is the wash-in curve's asymptote, not its exclusion."""

    reading = read_wash_in(0.02, 0.02)

    assert reading.domain is WashInDomain.WASH_IN
    assert reading.plotted_ratio == WASH_IN_EQUILIBRIUM_RATIO


def test_the_domain_predicate_and_the_reading_share_one_boundary() -> None:
    """One comparison, in one place.

    The chart classifies a sample with `is_wash_in` and the caption with
    `read_wash_in`, so a second copy of `<= 1` in either would be a
    boundary that could move in one and not the other.
    """

    assert is_wash_in(WASH_IN_EQUILIBRIUM_RATIO)
    assert is_wash_in(0.0)
    assert not is_wash_in(WASH_IN_EQUILIBRIUM_RATIO * 1.0001)

    for alveolar, inspired in ((0.0, 0.02), (0.017, 0.02), (0.02, 0.02), (0.021, 0.02)):
        ratio = wash_in_ratio(alveolar, inspired)

        assert ratio is not None
        assert is_wash_in(ratio) == (
            read_wash_in(alveolar, inspired).domain is WashInDomain.WASH_IN
        )


@pytest.mark.parametrize(
    ("alveolar", "inspired", "expected"),
    [
        (0.0, 0.0, WashInDomain.NO_INSPIRED_AGENT),
        (0.0, 0.02, WashInDomain.WASH_IN),
        (0.017, 0.02, WashInDomain.WASH_IN),
        (0.02, 0.02, WashInDomain.WASH_IN),
        (0.021, 0.02, WashInDomain.ELIMINATION),
    ],
)
def test_the_domain_and_the_plotted_value_always_agree(
    alveolar: float, inspired: float, expected: WashInDomain
) -> None:
    """One call answers both, so a caption cannot contradict a trace.

    The interface reads the sentence beside the plot from the domain and
    the trace from the value, and a reader seeing "no agent has reached
    the circuit yet" beside a drawn curve would have no way to tell which
    of the two was lying.
    """

    reading = read_wash_in(alveolar, inspired)

    assert reading.domain is expected
    assert (reading.plotted_ratio is not None) == (expected is WashInDomain.WASH_IN)
