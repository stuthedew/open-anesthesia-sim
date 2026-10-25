"""Unit tests for `app/wash_in.py`, which computes the F_A/F_I ratio and decides its domain.

`docs/MODEL.md` § "F_A/F_I as a displayed ratio" makes claims about this
module. These tests check each claim against the function that implements
it, without building a Flet interface. The end-to-end path is tested in
`tests/unit/test_simulation_view.py`: a real controller, real steps, the
trace, and the sentence beside the trace.

The published values that these tests compare against are the ones that
`docs/MODEL.md` § "Published wash-in and elimination validation test" already cites.
This file does not restate the citation. It only shows that the displayed
ratio is the same quantity that the published test validates.
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
    """The ratio is one fraction divided by the other, with no scaling, percent or rounding."""

    assert wash_in_ratio(0.0147, 0.0173) == pytest.approx(0.0147 / 0.0173)
    assert wash_in_ratio(0.0, 0.02) == 0.0
    assert wash_in_ratio(0.02, 0.02) == 1.0


def test_the_denominator_floor_is_the_displayed_resolution() -> None:
    """The denominator floor is derived from the display resolution, not chosen separately.

    The floor is the smallest inspired fraction from which a ratio is
    formed. If it were a second constant chosen independently, the two
    constants could drift apart. A ratio could then be formed from an
    inspired concentration that the interface itself shows as `0.00%`.
    """

    assert WASH_IN_DENOMINATOR_FLOOR_FRACTION == pytest.approx(
        CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / 100.0
    )


def test_no_ratio_is_formed_from_an_empty_circuit() -> None:
    """The 0/0 at the start of every run must not reach the chart.

    `CLAUDE.md` prefers an obvious absence to a plausible-looking number.
    No number is defensible here. Nothing has been inspired, so there is
    nothing for the alveolar fraction to be a fraction *of*.
    """

    assert wash_in_ratio(0.0, 0.0) is None
    assert read_wash_in(0.0, 0.0).domain is WashInDomain.NO_INSPIRED_AGENT
    assert read_wash_in(0.0, 0.0).plotted_ratio is None


def test_no_ratio_is_formed_below_the_denominator_floor() -> None:
    """The floor rejects every denominator less than it, not only an exact zero."""

    just_under = WASH_IN_DENOMINATOR_FLOOR_FRACTION * 0.99

    assert wash_in_ratio(just_under / 2.0, just_under) is None
    assert read_wash_in(0.0, just_under).domain is WashInDomain.NO_INSPIRED_AGENT

    # When the denominator equals the floor exactly, the quotient is a number again.
    assert wash_in_ratio(
        WASH_IN_DENOMINATOR_FLOOR_FRACTION / 2.0, WASH_IN_DENOMINATOR_FLOOR_FRACTION
    ) == pytest.approx(0.5)


def test_the_trace_stops_where_alveolar_exceeds_inspired() -> None:
    """When F_A/F_I is above 1, the run is eliminating agent, not washing it in.

    The arithmetic still gives a meaningful number, but that number is not
    a wash-in fraction. It must not be drawn on a curve that claims to be
    the textbook wash-in graph. The value is left out rather than clamped,
    because a value pinned to 1.0 would draw a completed wash-in that the
    run never reached.
    """

    reading = read_wash_in(0.0090, 0.0030)

    assert reading.domain is WashInDomain.ELIMINATION
    assert reading.plotted_ratio is None
    # The quotient itself is still available, and is not clamped.
    assert wash_in_ratio(0.0090, 0.0030) == pytest.approx(3.0)


def test_equilibrium_is_inside_the_domain() -> None:
    """F_A = F_I is the asymptote of the wash-in curve, so it is inside the domain."""

    reading = read_wash_in(0.02, 0.02)

    assert reading.domain is WashInDomain.WASH_IN
    assert reading.plotted_ratio == WASH_IN_EQUILIBRIUM_RATIO


def test_the_domain_predicate_and_the_reading_share_one_boundary() -> None:
    """The domain boundary is one comparison, made in one place.

    The chart classifies a sample with `is_wash_in`, and the caption
    classifies it with `read_wash_in`. A second copy of `<= 1` in either
    function would be a boundary that could change in one function and
    not in the other.
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
    """One call returns both, so a caption cannot contradict a trace.

    The interface takes the sentence beside the plot from the domain, and
    it takes the trace from the value. A reader who saw "no agent has
    reached the circuit yet" beside a drawn curve could not tell which of
    the two was wrong.
    """

    reading = read_wash_in(alveolar, inspired)

    assert reading.domain is expected
    assert (reading.plotted_ratio is not None) == (expected is WashInDomain.WASH_IN)
