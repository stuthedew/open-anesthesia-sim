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

import math

import pytest

from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.formatting import CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
from anesthesia_sim.app.wash_in import (
    WASH_IN_DENOMINATOR_FLOOR_FRACTION,
    WASH_IN_EQUILIBRIUM_RATIO,
    WASH_IN_ROUNDING_ALLOWANCE,
    WashInDomain,
    is_wash_in,
    read_wash_in,
    wash_in_ratio,
)
from anesthesia_sim.core.governing_equations import ALVEOLAR_FRACTION, INSPIRED_FRACTION
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    CardiacOutput,
    FreshGasFlow,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

#: The limit is one hour of `SIMULATION_STEP_S` steps. Each run below reaches its fixed
#: point in about 21 000 steps, so a run that has not reached it within the limit has failed.
ZERO_OUTPUT_STEP_LIMIT = 36_000

#: The largest share of the agent in the fast pool that a run may lose while it is held at the
#: edge of `WASH_IN_ROUNDING_ALLOWANCE` for the longest supported run length. This is the
#: clinical requirement on the allowance (`PL-N559`, project owner, 2026-10-26).
HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL = 0.01

#: The smallest allowed ratio of `WASH_IN_ROUNDING_ALLOWANCE` to the rounding at a settled state.
#: Below this ratio, a later tightening of the allowance would bring back the false elimination
#: caption.
ROUNDING_MARGIN = 1_000

#: How close each settled fraction must be to the closed form, relative. The
#: measured distance is about 2e-14 (`PL-N559`, 2026-10-26).
ZERO_OUTPUT_CLOSED_FORM_TOLERANCE = 1e-12


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


@pytest.mark.parametrize("agent", ["sevoflurane", "isoflurane", "desflurane"])
def test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination(agent: str) -> None:
    """At zero cardiac output, the settled run is treated as wash-in at equilibrium (`PL-N559`).

    With no blood flow there is no uptake. The closed form then has the circuit and the alveoli
    both settle at the delivered fraction, so $`F_A/F_I`$ is exactly 1. The stepped run settles
    onto a floating-point fixed point instead, within rounding of that value. Isoflurane at the
    fastest fresh gas flow settles with $`F_A`$ above $`F_I`$, which the rule once treated as
    elimination.

    The test does not depend on how long a run may last. It steps until one more step changes
    neither fraction. From then on every step returns the same state, so the reading at the
    fixed point is the reading for the rest of any run, however long the run limit becomes.
    """

    system = AgentUptakeSystem.for_agent(agent)
    system.set_cardiac_output(CardiacOutput(0.0))
    system.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN))
    step = SIMULATION_STEP_S

    previous = system.state_vector()
    for _ in range(ZERO_OUTPUT_STEP_LIMIT):
        system.advance(step)
        state = system.state_vector()
        settled = (state[INSPIRED_FRACTION], state[ALVEOLAR_FRACTION])
        if settled == (previous[INSPIRED_FRACTION], previous[ALVEOLAR_FRACTION]):
            break
        previous = state
    else:
        pytest.fail(f"{agent} did not reach a fixed point in {ZERO_OUTPUT_STEP_LIMIT} steps")

    delivered = float(system.circuit.delivered_partial_pressure_fraction)
    inspired = state[INSPIRED_FRACTION]
    alveolar = state[ALVEOLAR_FRACTION]

    assert math.isclose(inspired, delivered, rel_tol=ZERO_OUTPUT_CLOSED_FORM_TOLERANCE)
    assert math.isclose(alveolar, delivered, rel_tol=ZERO_OUTPUT_CLOSED_FORM_TOLERANCE)
    reading = read_wash_in(alveolar, inspired)
    assert reading.domain is WashInDomain.WASH_IN
    assert reading.plotted_ratio == alveolar / inspired
    if agent == "isoflurane":
        assert alveolar > inspired, "the case that the rule once read as elimination"
    overshoot = abs(alveolar / inspired - WASH_IN_EQUILIBRIUM_RATIO)
    assert overshoot * ROUNDING_MARGIN <= WASH_IN_ROUNDING_ALLOWANCE, (
        f"WASH_IN_ROUNDING_ALLOWANCE ({WASH_IN_ROUNDING_ALLOWANCE:g}) is less than "
        f"{ROUNDING_MARGIN} times the rounding at {agent}'s settled state ({overshoot:.2g}). "
        "Either the allowance was tightened too far, or a change to the solver now rounds "
        "worse. Too small an allowance brings back PL-N559: at zero cardiac output the wash-in "
        "plot says the patient is returning agent when nothing has changed. See "
        'docs/MODEL.md § "F_A/F_I as a displayed ratio".'
    )


def test_the_rounding_allowance_is_the_only_slack_above_equilibrium() -> None:
    """A quotient past the allowance is still elimination, and the boundary is inclusive."""

    assert is_wash_in(WASH_IN_EQUILIBRIUM_RATIO + WASH_IN_ROUNDING_ALLOWANCE)
    assert not is_wash_in(
        math.nextafter(WASH_IN_EQUILIBRIUM_RATIO + WASH_IN_ROUNDING_ALLOWANCE, math.inf)
    )


def _fast_pool_capacity_l(agent: str) -> float:
    """Return the litres of vapour that the fast pool holds for each unit of gas fraction.

    The fast pool is the alveolar gas, the venous blood and the vessel-rich group, which holds
    the brain. Each compartment adds its volume times its partition coefficient against gas.
    Muscle and fat are left out. That makes the fast pool the smallest store that a hidden loss
    could deplete, so the bound is conservative.
    """

    agent_parameters = load_agent_parameters(agent)
    patient = load_reference_adult_parameters()
    return (
        float(patient.alveolar_gas_volume_l)
        + float(patient.venous_pool_volume_l)
        * float(agent_parameters.blood_gas_partition_coefficient)
        + float(patient.vessel_rich_volume_l)
        * float(agent_parameters.vessel_rich_tissue_gas_partition_coefficient)
    )


@pytest.mark.parametrize("agent", sorted(AGENT_DATA_FILENAMES))
def test_the_rounding_allowance_hides_no_clinical_change_over_a_whole_run(agent: str) -> None:
    """A run held at the edge of the allowance loses less than 1% of the fast pool (`PL-N559`).

    A quotient of 1 + `WASH_IN_ROUNDING_ALLOWANCE` is drawn as equilibrium. If the run were
    really eliminating at that edge, agent would leave at alveolar ventilation times $`F_I`$
    times the allowance. The fast pool holds its capacity times $`F_I`$, so the loss as a share
    of the fast pool does not depend on the concentration. The test takes the fastest supported
    ventilation and the longest supported run, so it covers every run the simulator allows. It
    is meant to fail when either limit grows or a less soluble agent ships, and its message says
    what to do then.
    """

    run_length_min = MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_MINUTE
    capacity_l = _fast_pool_capacity_l(agent)
    hidden_loss_fraction = (
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN * WASH_IN_ROUNDING_ALLOWANCE * run_length_min
    ) / capacity_l
    largest_allowance = (
        HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL
        * capacity_l
        / (MAXIMUM_ALVEOLAR_VENTILATION_L_MIN * run_length_min)
    )

    assert hidden_loss_fraction < HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL, (
        "This test failed as designed. It guards WASH_IN_ROUNDING_ALLOWANCE in "
        "src/anesthesia_sim/app/wash_in.py (PL-N559). The wash-in plot treats a ratio up to "
        f"1 + {WASH_IN_ROUNDING_ALLOWANCE:g} as equilibrium, and that is only safe while a "
        "whole run at that edge loses less than "
        f"{HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL:.0%} of the agent in the fast pool. "
        f"For {agent} it would now lose {hidden_loss_fraction:.2%}.\n"
        "The inputs it read:\n"
        f"  run-length limit MAXIMUM_ELAPSED_SIMULATION_TIME_S = "
        f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s ({run_length_min / 60:g} h)\n"
        f"  ventilation limit MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = "
        f"{MAXIMUM_ALVEOLAR_VENTILATION_L_MIN:g} L/min\n"
        f"  {agent}'s fast pool = {capacity_l:.3g} L of vapour per unit fraction\n"
        "One of these grew since the allowance was set, or a less soluble agent was added. "
        "What to do: lower WASH_IN_ROUNDING_ALLOWANCE to at most "
        f"{largest_allowance:.2g} (a round value below it, such as half), and update its "
        'reasoning there and in docs/MODEL.md § "F_A/F_I as a displayed ratio". '
        "test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination then checks that "
        "the new value is still far enough above the rounding."
    )
