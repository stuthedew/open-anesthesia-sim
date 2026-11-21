"""The readouts, the chart, the marks and a branch read the one state stored for each second.

`PL-MH9J` made every step store its state, and made each reader take a
second's state from that record. The expected states below come from a run
that this file steps in `core/` directly, with the same settings changed at
the same seconds. So no expected value is read from the controller that the
tests exercise.
"""

import itertools

from anesthesia_sim.app.bookmarks import MacTarget
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.formatting import mac_multiple
from anesthesia_sim.app.run_series import COMPARTMENT_STATE_INDEX, RecordedQuantity, RecordedSeries
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem
from tests.integration.controller.controller_support import COMPARTMENT_SNAPSHOT_FIELDS

AGENT = "sevoflurane"
RUN_S = 150
DIAL_CHANGE_S = 40
VENTILATION_CHANGE_S = 95
FLOW_CHANGE_S = 120

# The snapshot's field for each compartment, beside the position of that
# compartment's fraction in a stored state. The positions are written out from
# `docs/MODEL.md` § "State vector", in the order circuit, alveoli, mixed
# venous blood, vessel-rich group, muscle, fat.
SNAPSHOT_FIELD_POSITIONS = tuple(zip(COMPARTMENT_SNAPSHOT_FIELDS, range(6), strict=True))


def _states_stepped_in_core() -> list[tuple[float, ...]]:
    """Return the state of each second from 0 to `RUN_S`, stepped without a controller."""

    state = SimulationState(uptake_system=AgentUptakeSystem.for_agent(AGENT))
    states = [state.uptake_system.case_state()]

    for second in range(1, RUN_S + 1):
        states.append(state.advance().state)

        if second == DIAL_CHANGE_S:
            state.uptake_system.set_delivered_concentration_percent(Percent(4.0))
        elif second == VENTILATION_CHANGE_S:
            state.uptake_system.set_alveolar_ventilation(AlveolarVentilation(6.0))
        elif second == FLOW_CHANGE_S:
            state.uptake_system.set_fresh_gas_flow(FreshGasFlow(0.5))

    return states


def _change_settings_at(controller: SimulationController, second: int) -> None:
    if second == DIAL_CHANGE_S:
        controller.set_delivered_concentration_percent(Percent(4.0))
    elif second == VENTILATION_CHANGE_S:
        controller.set_alveolar_ventilation(AlveolarVentilation(6.0))
    elif second == FLOW_CHANGE_S:
        controller.set_fresh_gas_flow(FreshGasFlow(0.5))


def _drawn_states(
    controller: SimulationController, start_s: float, stop_s: float, columns: int
) -> dict[float, tuple[float, ...]]:
    """Return what one chart window draws: each drawn second and its six compartment values."""

    window = controller.drawn_window(start_s, stop_s, columns)
    traces = [
        window.compartment_fractions(RecordedSeries(AGENT, quantity))
        for quantity in COMPARTMENT_STATE_INDEX
    ]

    return {
        time_s: tuple(trace[column] for trace in traces)
        for column, time_s in enumerate(window.times_s)
    }


def test_the_readouts_and_the_chart_show_the_state_stored_for_each_second() -> None:
    """At every second of a run with three setting changes, both show the stepped state exactly.

    The comparison is exact. A readout that read a compartment back, or a
    chart point computed by formula, differs from the stored state in its
    last bits at some of these seconds.
    """

    expected = _states_stepped_in_core()
    controller = SimulationController(agent_id=AGENT)
    controller.start()

    for second in range(1, RUN_S + 1):
        controller.advance()

        snapshot = controller.snapshot()
        assert snapshot.elapsed_s == second

        for field, position in SNAPSHOT_FIELD_POSITIONS:
            assert getattr(snapshot, field) == expected[second][position], (second, field)

        # A window of one instant is the chart's newest point.
        assert _drawn_states(controller, second, second, 2) == {second: expected[second][:6]}

        _change_settings_at(controller, second)

    assert snapshot.delivered_agent_l == expected[RUN_S][6]
    assert snapshot.exhausted_agent_l == expected[RUN_S][7]


def test_a_chart_window_draws_stored_states_at_its_columns_its_ends_and_each_setting_change() -> (
    None
):
    """A window wider than its columns reads whole seconds, and no value between two of them.

    Any other second it draws is one at which a compartment is above or below
    both columns beside it. The tests of the overpressure run below check
    those seconds.
    """

    expected = _states_stepped_in_core()
    controller = SimulationController(agent_id=AGENT)
    controller.start()

    for second in range(1, RUN_S + 1):
        controller.advance()
        _change_settings_at(controller, second)

    # An axis from 3.5 s to 148.5 s in 11 columns has a spacing of 14.5 s,
    # which is rounded down to 14 s. The columns fall on multiples of 14 s
    # from the case's zero. The ends move inward to whole seconds.
    columns = sorted(
        {4, 148, *range(14, 148, 14), DIAL_CHANGE_S, VENTILATION_CHANGE_S, FLOW_CHANGE_S}
    )
    drawn = _drawn_states(controller, 3.5, 148.5, 11)

    assert set(columns) <= set(drawn)

    for second, values in drawn.items():
        assert values == expected[int(second)][:6], second

    for second in set(drawn) - set(columns):
        left_s = max(column for column in columns if column < second)
        right_s = min(column for column in columns if column > second)

        assert any(
            expected[int(second)][position]
            > max(expected[left_s][position], expected[right_s][position])
            or expected[int(second)][position]
            < min(expected[left_s][position], expected[right_s][position])
            for position in range(6)
        ), second


def test_a_run_halts_on_the_second_whose_stored_state_first_reaches_a_marked_height() -> None:
    """A target set at the readout's own value for second 60 halts the run on second 60.

    The vessel-rich group is still rising at 60 s, so second 59 is below the
    height. The halted trunk and a branch opened where it stands show the
    state stored for second 60, and both name the target as reached.
    """

    expected = _states_stepped_in_core()
    vessel_rich = COMPARTMENT_STATE_INDEX[RecordedQuantity.VESSEL_RICH]
    controller = SimulationController(agent_id=AGENT)
    mac_percent = controller.snapshot().agent_mac_percent
    height = mac_multiple(
        Fraction(expected[60][vessel_rich], name="vessel_rich partial_pressure_fraction"),
        mac_percent,
    )
    target = MacTarget(RecordedQuantity.VESSEL_RICH, height)
    controller.add_mac_target(target)
    controller.start()

    for second in range(1, RUN_S + 1):
        controller.advance()

        if not controller.is_running:
            break

        _change_settings_at(controller, second)

    assert expected[59][vessel_rich] < expected[60][vessel_rich]
    assert controller.snapshot().elapsed_s == 60

    halt = controller.snapshot().bookmark_halt
    assert halt is not None
    assert halt.mac_targets == (target,)

    branch = controller.resumed_here()
    branch_snapshot = branch.snapshot()
    branch_halt = branch_snapshot.bookmark_halt

    assert branch_halt is not None
    assert branch_halt.mac_targets == (target,)

    for field, position in SNAPSHOT_FIELD_POSITIONS:
        assert getattr(branch_snapshot, field) == expected[60][position], field

    assert _drawn_states(branch, 60, 60, 2) == {60: expected[60][:6]}


def test_a_branch_stores_its_parents_state_at_the_fork_and_steps_on_from_it() -> None:
    """A branch taken at a setting change, with no setting moved, repeats its parent's fractions.

    The parent's later states are the expected values, stepped in `core/`.
    """

    expected = _states_stepped_in_core()
    controller = SimulationController(agent_id=AGENT)
    controller.start()

    for second in range(1, RUN_S + 1):
        controller.advance()
        _change_settings_at(controller, second)

    branch = controller.resumed_at(CaseInstant(VENTILATION_CHANGE_S))

    assert _drawn_states(branch, 0.0, float(VENTILATION_CHANGE_S), 2) == {
        VENTILATION_CHANGE_S: expected[VENTILATION_CHANGE_S][:6]
    }

    branch.start()

    for second in range(VENTILATION_CHANGE_S + 1, FLOW_CHANGE_S + 1):
        branch.advance()

        snapshot = branch.snapshot()

        for field, position in SNAPSHOT_FIELD_POSITIONS:
            assert getattr(snapshot, field) == expected[second][position], (second, field)


OVERPRESSURE_S = 120
OVERPRESSURE_RUN_S = 600
# A window from 0 to 600 s in five columns has a column every 150 s. The chart
# also draws the second of the dial change, so these are the seconds it drew
# before it searched each stretch for a peak (`PL-BLZJ`).
OVERPRESSURE_COLUMNS_S = (0, OVERPRESSURE_S, 150, 300, 450, OVERPRESSURE_RUN_S)


def _overpressure_stepped_in_core() -> list[tuple[float, ...]]:
    """Return each second's state of 8% sevoflurane for 120 s and 1% after, stepped in core."""

    state = SimulationState(uptake_system=AgentUptakeSystem.for_agent(AGENT))
    state.uptake_system.set_delivered_concentration_percent(Percent(8.0))
    states = [state.uptake_system.case_state()]

    for second in range(1, OVERPRESSURE_RUN_S + 1):
        states.append(state.advance().state)

        if second == OVERPRESSURE_S:
            state.uptake_system.set_delivered_concentration_percent(Percent(1.0))

    return states


def _overpressure_in_the_controller() -> SimulationController:
    controller = SimulationController(agent_id=AGENT)
    controller.set_delivered_concentration_percent(Percent(8.0))
    controller.start()

    for second in range(1, OVERPRESSURE_RUN_S + 1):
        controller.advance()

        if second == OVERPRESSURE_S:
            controller.set_delivered_concentration_percent(Percent(1.0))

    return controller


def test_a_peak_between_two_chart_columns_is_drawn_at_its_stored_value() -> None:
    """After an overpressure the alveolar fraction peaks between two columns, and is drawn there.

    The alveoli keep filling for a few seconds after the dial is lowered at
    120 s, so the alveolar fraction peaks after the change and before the
    next column at 150 s. A chart that drew only its columns and the change
    would show the alveolar trace about 0.05 percentage points below that
    peak. The peak's second and height are found here in a run stepped in
    `core/`.
    """

    expected = _overpressure_stepped_in_core()
    alveolar = COMPARTMENT_STATE_INDEX[RecordedQuantity.ALVEOLAR]
    peak_s = max(range(len(expected)), key=lambda second: expected[second][alveolar])

    # The test is of a peak that no column draws.
    assert OVERPRESSURE_S < peak_s < 150
    assert expected[peak_s][alveolar] - expected[OVERPRESSURE_S][alveolar] > 0.0004

    drawn = _drawn_states(_overpressure_in_the_controller(), 0.0, float(OVERPRESSURE_RUN_S), 5)

    assert peak_s in drawn
    assert drawn[peak_s] == expected[peak_s][:6]
    assert max(values[1] for values in drawn.values()) == expected[peak_s][alveolar]


def test_every_compartments_highest_and_lowest_value_in_each_column_is_drawn() -> None:
    """Between two columns, the drawn points reach as high and as low as the run did.

    Each stretch between two columns is compared with every second of a run
    stepped in `core/`. For each compartment, the highest and the lowest of
    the points drawn in the stretch equal the highest and the lowest stored
    values in it. The chart adds at most two points to a stretch for each
    compartment.
    """

    expected = _overpressure_stepped_in_core()
    drawn = _drawn_states(_overpressure_in_the_controller(), 0.0, float(OVERPRESSURE_RUN_S), 5)

    assert set(OVERPRESSURE_COLUMNS_S) <= set(drawn)
    assert len(drawn) <= len(OVERPRESSURE_COLUMNS_S) + 2 * 6 * (len(OVERPRESSURE_COLUMNS_S) - 1)

    for left_s, right_s in itertools.pairwise(OVERPRESSURE_COLUMNS_S):
        stored = expected[left_s : right_s + 1]
        points = [values for second, values in drawn.items() if left_s <= second <= right_s]

        for position in range(6):
            assert max(point[position] for point in points) == max(
                state[position] for state in stored
            ), (left_s, position)
            assert min(point[position] for point in points) == min(
                state[position] for state in stored
            ), (left_s, position)


def test_a_window_with_a_column_on_every_second_draws_no_other_point() -> None:
    drawn = _drawn_states(_overpressure_in_the_controller(), 100.0, 160.0, 61)

    assert sorted(drawn) == list(range(100, 161))
