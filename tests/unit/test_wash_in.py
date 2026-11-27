"""Unit tests for `app/wash_in.py`, which computes the F_A/F_I ratio and decides its domain.

`docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" makes claims about this
module. These tests check each claim against the function that implements
it, without building the Qt interface. The end-to-end path is tested in
`tests/integration/simulation_view/`: a real controller, real steps,
the trace, and the sentence beside the trace.

These tests compare against the published values that
`docs/VERIFICATION.md` § "Published wash-in and elimination validation test" cites.
They show only that the displayed ratio is the same quantity that the
published test validates.
"""

import ast
import math
from pathlib import Path

import pytest

import anesthesia_sim
from anesthesia_sim.app.formatting import CONCENTRATION_DISPLAY_RESOLUTION_PERCENT, format_percent
from anesthesia_sim.app.wash_in import (
    WASH_IN_DENOMINATOR_FLOOR_FRACTION,
    WASH_IN_EQUILIBRIUM_RATIO,
    WashInDomain,
    WashInReading,
    _smallest_fraction_shown_as_one_display_step,
    is_ventilated,
    is_wash_in,
    read_wash_in,
    read_wash_in_with_ventilation,
    wash_in_ratio,
)
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.governing_equations import ALVEOLAR_FRACTION, INSPIRED_FRACTION
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.rounding import WASH_IN_ROUNDING_ALLOWANCE
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    FreshGasFlow,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

#: The limit is one hour of one-second steps. Each run below reaches its fixed point
#: in about 2 250 steps at the fastest fresh gas flow and in about 3 250 steps at
#: `FRESH_GAS_FLOW_THAT_SETTLES_ABOVE_L_MIN`, so a run that has not reached it within the limit
#: has failed.
ZERO_OUTPUT_STEP_LIMIT = 3_600

#: A fresh gas flow, in L/min, at which isoflurane at zero cardiac output settles with $`F_A`$
#: above $`F_I`$. That is the case that the rule once treated as elimination (`PL-N559`). Which
#: side of 1 a run settles on is a property of the rounding, and it changes with the step. At
#: the one-second step the quotient settles 4.7e-15 above 1 at this flow, and below 1 for every
#: agent at the fastest flow (measured 2026-11-21, `PL-SZ6G`).
FRESH_GAS_FLOW_THAT_SETTLES_ABOVE_L_MIN = 6.0

#: The largest share of the agent in the fast pool that a run may lose while it is held at the
#: edge of `WASH_IN_ROUNDING_ALLOWANCE` for the longest supported run length. This is the
#: clinical requirement on the allowance (`PL-N559`, project owner, 2026-10-26).
HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL = 0.01

#: The smallest allowed ratio of `WASH_IN_ROUNDING_ALLOWANCE` to the rounding at a settled state.
#: Below this ratio, a later tightening of the allowance would bring back the false elimination
#: caption.
ROUNDING_MARGIN = 1_000

#: How close each settled fraction must be to the closed form, relative. This is a numerical
#: limit on the rounding of the stepped run. The measured distance is at most 7.5e-14 at the
#: one-second step (`PL-SZ6G`, 2026-11-21).
ZERO_OUTPUT_CLOSED_FORM_TOLERANCE = 1e-12


def test_the_ratio_is_the_plain_quotient_of_the_two_fractions() -> None:
    """The ratio is one fraction divided by the other, with no scaling, percent or rounding."""

    assert wash_in_ratio(0.0147, 0.0173) == pytest.approx(0.0147 / 0.0173)
    assert wash_in_ratio(0.0, 0.02) == 0.0
    assert wash_in_ratio(0.02, 0.02) == 1.0


def test_the_denominator_floor_is_where_the_readout_first_shows_one_step() -> None:
    """The floor is the smallest inspired fraction that the readout shows as `0.01%`.

    The expected strings are the readout's forms that `docs/INTERFACE.md`
    § "Displayed precision" specifies: two decimals, and `<0.01%` for a
    positive value that rounds to zero. If the floor were a second constant
    chosen apart from the readout, the two could drift apart. A ratio could
    then be formed from an inspired concentration that the readout shows as
    `<0.01%`, or refused for one it shows as `0.01%` (`PL-FSXD`).
    """

    just_below = Fraction(math.nextafter(WASH_IN_DENOMINATOR_FLOOR_FRACTION, 0.0))

    assert format_percent(WASH_IN_DENOMINATOR_FLOOR_FRACTION) == "0.01%"
    assert format_percent(just_below) == "<0.01%"
    # The readout rounds to the nearest hundredth of a percent, so the floor is half a step.
    assert WASH_IN_DENOMINATOR_FLOOR_FRACTION == pytest.approx(
        CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / 100.0 / 2.0
    )


def test_the_search_for_the_floor_ends_on_the_readout_boundary() -> None:
    """Running the search again gives the floor, and the readout's boundary lies just below it.

    The floor is computed once, when `app/wash_in.py` is imported. This test
    calls the search itself, so a change to the search fails here and not
    only through a constant that was computed before the change ran.
    """

    found = _smallest_fraction_shown_as_one_display_step()

    assert found == WASH_IN_DENOMINATOR_FLOOR_FRACTION
    assert format_percent(found) == "0.01%"
    assert format_percent(Fraction(math.nextafter(found, 0.0))) == "<0.01%"


def test_each_inspired_value_the_readout_shows_gives_a_ratio_always_or_never() -> None:
    """Two inspired fractions that the readout shows alike are both divided by, or neither is.

    A floor of 0.01% fails here. The readout shows an inspired fraction from
    0.005% up to 0.01% as `0.01%`, and that floor would give it no ratio
    while a larger fraction, also shown as `0.01%`, got one. The grid runs in steps of
    0.00001% from zero to 0.03%, so it crosses three readout steps, and it
    adds the floor and its neighbour below. The two readout forms with no
    number, `0.00%` and `<0.01%`, must give no ratio, and `0.01%` must give
    one.
    """

    grid = [step * 1e-7 for step in range(3_001)]
    grid += [WASH_IN_DENOMINATOR_FLOOR_FRACTION]
    grid += [math.nextafter(WASH_IN_DENOMINATOR_FLOOR_FRACTION, 0.0)]
    divided_by: dict[str, set[bool]] = {}

    for inspired in grid:
        shown = format_percent(Fraction(inspired))
        divided_by.setdefault(shown, set()).add(wash_in_ratio(0.0, inspired) is not None)

    assert {shown: answers for shown, answers in divided_by.items() if len(answers) > 1} == {}
    assert divided_by["0.00%"] == {False}
    assert divided_by["<0.01%"] == {False}
    assert divided_by["0.01%"] == {True}
    assert divided_by["0.03%"] == {True}


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


def test_zero_ventilation_is_stopped_and_any_flow_above_it_is_not() -> None:
    """Rule 3 compares zero exactly, as every zero-flow test in this model does.

    The smallest positive float is not zero, so a step at that ventilation is
    ventilated. Its agent exchange is below what the fractions resolve, but
    no band of nearly-zero ventilations is set apart, for the reason
    `core/__init__.py` gives for every flow.
    """

    assert not is_ventilated(AlveolarVentilation(0.0))
    assert is_ventilated(AlveolarVentilation(math.ulp(0.0)))
    assert is_ventilated(AlveolarVentilation(5.0))


@pytest.mark.parametrize(
    ("alveolar", "inspired"), [(0.005, 0.01), (0.02, 0.01)], ids=["below-one", "above-one"]
)
def test_a_state_reached_at_zero_ventilation_is_not_a_wash_in_fraction(
    alveolar: float, inspired: float
) -> None:
    """With ventilation stopped, no ratio is a wash-in fraction, whichever side of 1 (`PL-49D5`).

    No agent moves between the circuit and the alveoli, so a ratio of 0.5
    is not half-way through a wash-in, and a ratio of 2 is not elimination.
    """

    reading = read_wash_in_with_ventilation(alveolar, inspired, AlveolarVentilation(0.0))

    assert reading == WashInReading(WashInDomain.VENTILATION_STOPPED, None)


def test_the_denominator_rule_is_applied_before_the_ventilation_rule() -> None:
    """With no inspired agent to divide by, the reading says that, ventilated or not."""

    reading = read_wash_in_with_ventilation(0.002, 0.00004, AlveolarVentilation(0.0))

    assert reading == WashInReading(WashInDomain.NO_INSPIRED_AGENT, None)


@pytest.mark.parametrize(
    ("alveolar", "inspired", "expected"),
    [
        (0.005, 0.01, WashInReading(WashInDomain.WASH_IN, 0.5)),
        (0.02, 0.01, WashInReading(WashInDomain.ELIMINATION, None)),
        (0.002, 0.00004, WashInReading(WashInDomain.NO_INSPIRED_AGENT, None)),
    ],
    ids=["wash-in", "above-one", "no-inspired-agent"],
)
def test_a_ventilated_state_is_read_by_the_first_two_rules(
    alveolar: float, inspired: float, expected: WashInReading
) -> None:
    """With ventilation running, the reading is the one rules 1 and 2 give."""

    assert read_wash_in_with_ventilation(alveolar, inspired, AlveolarVentilation(5.0)) == expected
    assert read_wash_in(alveolar, inspired) == expected


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
    it takes the trace from the value. A reader who saw "Not defined"
    beside a drawn curve could not tell which of the two was wrong.
    """

    reading = read_wash_in(alveolar, inspired)

    assert reading.domain is expected
    assert (reading.plotted_ratio is not None) == (expected is WashInDomain.WASH_IN)


@pytest.mark.parametrize(
    ("agent", "fresh_gas_flow_l_min"),
    [
        ("sevoflurane", MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        ("isoflurane", MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        ("desflurane", MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        ("isoflurane", FRESH_GAS_FLOW_THAT_SETTLES_ABOVE_L_MIN),
    ],
)
def test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination(
    agent: str, fresh_gas_flow_l_min: float
) -> None:
    """At zero cardiac output, the settled run is treated as wash-in at equilibrium (`PL-N559`).

    With no blood flow there is no uptake. The closed form then has the circuit and the alveoli
    both settle at the delivered fraction, so $`F_A/F_I`$ is exactly 1. The stepped run settles
    onto a floating-point fixed point instead, within rounding of that value. Each agent is run
    at the fastest fresh gas flow, where the fixed point is furthest from 1. Isoflurane is also
    run at `FRESH_GAS_FLOW_THAT_SETTLES_ABOVE_L_MIN`, where it settles with $`F_A`$ above
    $`F_I`$, which the rule once treated as elimination.

    The test does not depend on how long a run may last. It steps until one more step changes
    neither fraction. From then on every step returns the same state, so the reading at the
    fixed point is the reading for the rest of any run, however long the run limit becomes.
    """

    system = AgentUptakeSystem.for_agent(agent)
    system.set_cardiac_output(CardiacOutput(0.0))
    system.set_fresh_gas_flow(FreshGasFlow(fresh_gas_flow_l_min))

    previous = system.state_vector()
    for _ in range(ZERO_OUTPUT_STEP_LIMIT):
        system.advance()
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
    if fresh_gas_flow_l_min == FRESH_GAS_FLOW_THAT_SETTLES_ABOVE_L_MIN:
        assert alveolar > inspired, "the case that the rule once read as elimination"
    overshoot = abs(alveolar / inspired - WASH_IN_EQUILIBRIUM_RATIO)
    assert overshoot * ROUNDING_MARGIN <= WASH_IN_ROUNDING_ALLOWANCE, (
        "Raise WASH_IN_ROUNDING_ALLOWANCE in src/anesthesia_sim/app/wash_in.py to at least "
        f"{overshoot * ROUNDING_MARGIN:.1g}, or undo the solver change that made rounding worse.\n"
        f"Why: {agent}'s settled state at zero cardiac output rounds to {overshoot:.2g} above "
        f"1, and the allowance must be at least {ROUNDING_MARGIN} times that. Below it, the "
        "wash-in plot shows elimination when nothing is changing (PL-N559)."
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
    suggested_allowance = 10.0 ** math.floor(math.log10(largest_allowance))

    assert hidden_loss_fraction < HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL, (
        "Lower WASH_IN_ROUNDING_ALLOWANCE in src/anesthesia_sim/app/wash_in.py to "
        f"{suggested_allowance:.0e} (anything up to {largest_allowance:.2g} passes), and "
        'update its note in docs/INTERFACE.md § "F_A/F_I as a displayed ratio".\n'
        f"Why: a {run_length_min / 60:g} h run at {MAXIMUM_ALVEOLAR_VENTILATION_L_MIN:g} L/min "
        f"alveolar ventilation could hide a loss of {hidden_loss_fraction:.1%} of the {agent} from "
        f"the wash-in plot, and the limit is {HIDDEN_LOSS_LIMIT_FRACTION_OF_FAST_POOL:.0%}. "
        "A longer run-length limit, a higher ventilation limit or a less soluble agent "
        "causes this (PL-N559)."
    )


def test_only_the_full_reader_calls_the_reader_without_ventilation() -> None:
    """No module in `src/` reads the plotted ratio through `read_wash_in`, which skips rule 3.

    `read_wash_in` cannot apply the rule that a state reached at zero alveolar
    ventilation has no ratio, because it is not given the ventilation. A
    display path that called it would draw a ratio through an apnoea
    (`PL-ZZLW`). So every call of it under `src/` must be the one inside
    `read_wash_in_with_ventilation`.
    """

    package = Path(anesthesia_sim.__file__).parent
    callers: list[str] = []

    for path in sorted(package.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
                continue

            for node in ast.walk(function):
                called = isinstance(node, ast.Call) and (
                    (isinstance(node.func, ast.Name) and node.func.id == "read_wash_in")
                    or (isinstance(node.func, ast.Attribute) and node.func.attr == "read_wash_in")
                )

                if called:
                    callers.append(f"{path.relative_to(package)}::{function.name}")

    assert callers == ["app/wash_in.py::read_wash_in_with_ventilation"]
