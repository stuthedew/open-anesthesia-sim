import dataclasses
from collections.abc import Callable
from itertools import permutations

import pytest

from anesthesia_sim.app.bookmarks import BookmarkCrossing, MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlInput
from anesthesia_sim.app.controller import (
    BranchedCase,
    HereForkPoint,
    MarkForkPoint,
    RunSettings,
    RunStatus,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
    RESET_EXIT_TEXT,
    SUPPORTED_LIMIT_NOTICE_TEMPLATE,
    notice,
    transport,
)
from anesthesia_sim.app.formatting import (
    MAC_UNIT_SUFFIX,
    format_mac_multiple,
    format_supported_run_length,
)
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    RecordedQuantity,
    RecordedSeries,
)
from anesthesia_sim.app.wash_in import is_wash_in
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.concentration import (
    Fraction,
    MacMultiple,
    MacPercent,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
)
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.governing_equations import DELIVERED_AGENT_L, EXHAUSTED_AGENT_L, STATE_SIZE
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.run_definition import RunDefinition, RunSegment
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    maximum_step_count,
    require_supported_run_length,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.units import SECONDS_PER_MINUTE


def _advance_for(controller: SimulationController, duration_s: float) -> None:
    """Advance a running controller to `duration_s` at the largest supported step.

    The helper reaches the simulated time by taking many supported steps, not
    by asking for one large step. `MAXIMUM_SIMULATION_STEP_S` is the declared
    control-resolution tolerance, and the controller refuses a longer step.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))


def _with_stale_tissue_flows(controller: SimulationController, cardiac_output_l_min: float) -> None:
    """Make the tissue flows sum to `cardiac_output_l_min`, bypassing the tissues' guard.

    Each tissue's perfusion fraction is multiplied by `cardiac_output_l_min`
    divided by the patient's cardiac output. The new fraction is written
    directly, bypassing the tissue's own guard. The patient's cardiac output
    does not change. The settings record that opens the run's definition then
    rejects the tissue flows, because they no longer sum to the cardiac output.
    It rejects them at the next step and at Reset (`PL-M4M0`), and no setting
    repairs them. No guarded write can produce this record now. Every flow is
    computed from the cardiac output (`PL-HQF5`), and a fraction is written
    only once (`PL-Z0HN`). Before those changes, a tissue's `set_blood_flow`
    could produce the record, and a change of cardiac output repaired it.
    `_with_the_tissue_fractions_put_back` stands in for that repair.
    """

    patient = controller._state.uptake_system.patient
    scale = cardiac_output_l_min / patient.cardiac_output_l_min

    for tissue in patient.tissues:
        object.__setattr__(tissue, "perfusion_fraction", tissue.perfusion_fraction * scale)


def _with_the_tissue_fractions_put_back(controller: SimulationController) -> None:
    """Write back the reference adult's perfusion fractions, bypassing the tissues' guard.

    The fractions are typed in by hand from `data/patients/reference_adult.json`.
    Once they are back, the settings record no longer rejects the tissue flows.
    """

    for tissue, fraction in zip(
        controller._state.uptake_system.patient.tissues, (0.76, 0.18, 0.06), strict=True
    ):
        object.__setattr__(tissue, "perfusion_fraction", fraction)


def test_default_controller_starts_with_sevoflurane() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "sevoflurane"
    assert snapshot.agent_display_name == "Sevoflurane"
    assert snapshot.max_delivered_concentration_percent == 8.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.02)


def test_default_controller_starts_each_agent_at_its_own_one_mac() -> None:
    """A freshly constructed controller starts at 1 MAC, the standard
    clinical starting point, not a fixed raw percentage.
    """

    assert SimulationController(
        agent_id="sevoflurane"
    ).snapshot().delivered_partial_pressure_fraction == pytest.approx(0.02)
    assert SimulationController(
        agent_id="isoflurane"
    ).snapshot().delivered_partial_pressure_fraction == pytest.approx(0.012)
    assert SimulationController(
        agent_id="desflurane"
    ).snapshot().delivered_partial_pressure_fraction == pytest.approx(0.06)


def test_explicit_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): an explicitly requested fraction above a
    vaporizer's real maximum must fail, not be silently clamped.

    Clamping produced a run in which every displayed value came from a dial
    position the caller never asked for. On screen, that run looked exactly
    like a run at a position they had asked for.
    """

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        SimulationController(agent_id="isoflurane", delivered_concentration_percent=Percent(8.0))


def test_setting_a_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): the setter path is bounded by the same guard.

    Before the fix only the UI slider bounded this value, so any non-UI
    caller could simulate 50% isoflurane on a 5% vaporizer.
    """

    controller = SimulationController(agent_id="isoflurane")

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration_percent(Percent(50.0))

    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.012)


def test_delivered_concentration_exactly_at_the_agent_max_is_accepted() -> None:
    """The boundary is inclusive: 5.0% is a real isoflurane dial position."""

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration_percent(Percent(5.0))

    assert controller.snapshot().delivered_concentration_percent == 5.0


def test_delivered_concentration_can_be_turned_off() -> None:
    """Zero is always deliverable: it is the vaporizer off, which is how
    washout begins.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration_percent(Percent(0.0))

    assert controller.snapshot().delivered_concentration_percent == 0.0


def test_patient_defaults_come_from_the_data_file() -> None:
    """Regression (PL-017): the cited data-file defaults must reach the app.

    The controller previously hardcoded 4.0 L/min ventilation and 5.0
    L/min cardiac output, matching `reference_adult.json` by coincidence,
    so any correction to the cited values would silently not take effect.
    """

    original = uptake_system.load_reference_adult_parameters
    edited = dataclasses.replace(
        load_reference_adult_parameters(),
        default_alveolar_ventilation_l_min=5.5,
        default_cardiac_output_l_min=6.5,
    )
    uptake_system.load_reference_adult_parameters = lambda: edited

    try:
        snapshot = SimulationController().snapshot()
    finally:
        uptake_system.load_reference_adult_parameters = original

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(5.5)
    assert snapshot.cardiac_output_l_min == pytest.approx(6.5)


def test_patient_defaults_are_the_shipped_cited_values() -> None:
    """The app runs exactly what `reference_adult.json` declares."""

    patient_parameters = load_reference_adult_parameters()
    snapshot = SimulationController().snapshot()

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(
        patient_parameters.default_alveolar_ventilation_l_min
    )
    assert snapshot.cardiac_output_l_min == pytest.approx(
        patient_parameters.default_cardiac_output_l_min
    )


def test_explicit_patient_settings_still_override_the_data_file() -> None:
    """The constructor arguments remain explicit overrides."""

    snapshot = SimulationController(
        alveolar_ventilation_l_min=AlveolarVentilation(3.0), cardiac_output_l_min=CardiacOutput(7.0)
    ).snapshot()

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(3.0)
    assert snapshot.cardiac_output_l_min == pytest.approx(7.0)


def test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac() -> None:
    """Switching agents must not carry over the old agent's raw percentage:
    the same percent means a different clinical depth per agent (e.g. 2%
    is 1 MAC of sevoflurane but only about a third of a MAC of desflurane).
    """

    controller = SimulationController(
        agent_id="sevoflurane", delivered_concentration_percent=Percent(8.0)
    )

    controller.set_agent("isoflurane")
    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.012)


def test_controller_can_be_constructed_for_a_different_agent() -> None:
    controller = SimulationController(agent_id="isoflurane")

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "isoflurane"
    assert snapshot.agent_display_name == "Isoflurane"


def test_set_agent_starts_fresh_preserving_flow_settings_but_not_concentration() -> None:
    """The circuit volume, fresh gas flow, ventilation and cardiac output carry over.

    The delivered concentration does not. It resets to the new agent's own
    1 MAC instead (see
    test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=CompartmentVolume(5.0),
        fresh_gas_flow_l_min=FreshGasFlow(3.0),
        delivered_concentration_percent=Percent(3.0),
        alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        cardiac_output_l_min=CardiacOutput(6.0),
    )
    controller.start()
    _advance_for(controller, duration_s=30.0)

    assert controller.snapshot().stored_agent_l > 0.0

    controller.set_agent("desflurane")
    snapshot = controller.snapshot()

    assert snapshot.agent_id == "desflurane"
    assert snapshot.agent_display_name == "Desflurane"
    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.stored_agent_l == 0.0
    assert snapshot.agent_accounting_passes_validation is True

    assert snapshot.circuit_volume_l == 5.0
    assert snapshot.fresh_gas_flow_l_min == 3.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.06)
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0


_ORDERED_AGENT_PAIRS = tuple(permutations(AGENT_DATA_FILENAMES, 2))
"""Every switch a learner can make: each agent to each other agent, both ways."""


def _run_with_non_default_settings(agent_id: str) -> SimulationController:
    """A paused run of `agent_id` whose four carried-over settings are not the defaults.

    The data files give a 6.0 L circuit, 4.0 L/min of fresh gas, 4.0 L/min of
    alveolar ventilation and 5.0 L/min of cardiac output. Each value here
    differs from its default and from the other three. So a switch that drops
    a setting, or puts one setting's value in another's place, builds a run
    that differs from a fresh run with these settings.
    """

    return SimulationController(
        agent_id=agent_id,
        circuit_volume_l=CompartmentVolume(4.5),
        fresh_gas_flow_l_min=FreshGasFlow(2.5),
        alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        cardiac_output_l_min=CardiacOutput(6.5),
    )


def _switched_after_a_run_of(previous_agent_id: str, new_agent_id: str) -> SimulationController:
    """A run of `previous_agent_id` that has taken up agent, then switched to `new_agent_id`.

    Before the switch the run has taken 90 s of uptake into every compartment,
    with the dial moved to 1.5 times the previous agent's MAC at 60 s. So the
    compartments contain agent, the dial is not at its default, and the
    timeline contains a change. A switch that kept any of these would show
    the difference.
    """

    run = _run_with_non_default_settings(previous_agent_id)
    run.start()
    _advance_for(run, duration_s=60.0)
    run.set_delivered_concentration_percent(
        Percent(1.5 * load_agent_parameters(previous_agent_id).mac_percent)
    )
    _advance_for(run, duration_s=30.0)
    assert run.snapshot().stored_agent_l > 0.0

    run.set_agent(new_agent_id)

    return run


@pytest.mark.parametrize(("previous_agent_id", "new_agent_id"), _ORDERED_AGENT_PAIRS)
def test_an_agent_switch_runs_exactly_as_a_fresh_run_of_that_agent(
    previous_agent_id: str, new_agent_id: str
) -> None:
    """A switched run computes with the new agent alone (`PL-QJXS`).

    The expected run is built directly with the new agent and the same four
    settings, so the expected values do not come from the run under test.
    Every field of the snapshot is compared: the agent and its references, the
    settings, the six partial-pressure fractions, the delivered and exhausted
    amounts and the accounting. The equation settings and the opening state are
    compared before either run takes a step.

    A switch from sevoflurane to desflurane that kept sevoflurane's
    compartments passed every other test. Its run, labelled desflurane, showed
    an alveolar fraction of 2.95% (0.49 ×MAC) at 5 minutes, where a fresh
    desflurane run shows 3.59% (0.60 ×MAC).

    The comparison is exact, not within a tolerance. Both runs take the same
    steps from the same state, and the simulator is deterministic.
    """

    switched = _switched_after_a_run_of(previous_agent_id, new_agent_id)
    fresh = _run_with_non_default_settings(new_agent_id)

    assert switched.run_segments == fresh.run_segments
    assert switched.snapshot() == fresh.snapshot()

    for run in (switched, fresh):
        run.start()
        _advance_for(run, duration_s=300.0)

    assert fresh.snapshot().alveolar_partial_pressure_fraction > 0.0
    assert switched.snapshot() == fresh.snapshot()


@pytest.mark.parametrize(("previous_agent_id", "new_agent_id"), _ORDERED_AGENT_PAIRS)
def test_a_switched_run_branches_as_a_fresh_run_of_that_agent_does(
    previous_agent_id: str, new_agent_id: str
) -> None:
    """A branch of a switched run is the same as a branch of a fresh run (`PL-QJXS`).

    A branch rebuilds its agent and patient from the data files. Before it
    opens, `_branch_from` refuses a branch whose rebuilt settings differ from
    the settings of the run it comes from. So a switch that kept the previous
    agent's patient is refused here, and the error names the coefficient that
    differs. A correct switch gives the same branch that a fresh run of the
    new agent gives.
    """

    branches = []

    for run in (
        _switched_after_a_run_of(previous_agent_id, new_agent_id),
        _run_with_non_default_settings(new_agent_id),
    ):
        run.start()
        _advance_for(run, duration_s=120.0)
        run.pause()
        branch = run.resumed_at(CaseInstant(0.0))
        branch.start()
        _advance_for(branch, duration_s=60.0)
        branches.append(branch)

    switched_branch, fresh_branch = branches

    assert switched_branch.snapshot() == fresh_branch.snapshot()


def test_set_agent_rejects_unknown_agent_id() -> None:
    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError, match="unknown agent_id"):
        controller.set_agent("halothane")


def test_pause_blocks_advancement() -> None:
    controller = SimulationController()

    controller.advance(SimulationStep(0.1))

    assert controller.snapshot().elapsed_s == 0.0


def test_start_advance_pause_sequence_is_deterministic() -> None:
    first = SimulationController()
    second = SimulationController()

    for controller in (first, second):
        controller.start()
        controller.advance(SimulationStep(0.1))
        controller.advance(SimulationStep(0.1))
        controller.pause()

    assert first.snapshot() == second.snapshot()


def _samples_a_snapshot_carries(controller: SimulationController) -> int:
    """Count the recorded samples reachable from one `snapshot()`.

    The helper walks every field rather than checking one named field. The
    defect it guards against is a *field*, any field, that carries the run. A
    check of one named field would keep passing after that field was renamed,
    or after a second copy appeared under another name.
    """

    snapshot = controller.snapshot()
    total = 0

    for field in dataclasses.fields(snapshot):
        value = getattr(snapshot, field.name)

        if isinstance(value, RunSegment):
            total += 1
        elif isinstance(value, tuple | list):
            total += sum(1 for item in value if isinstance(item, RunSegment))

    return total


def test_a_frame_reads_only_the_window_it_draws() -> None:
    """PL-0VM7: only the drawn window crosses this boundary, never the whole run.

    A frame's cost used to be proportional to how long the simulation had
    been running. `snapshot()` copied every sample ever recorded, five times
    a second, and the chart discarded all but the few hundred inside its
    axis. Timing is too flaky to assert, so the test asserts the count of
    values that cross the boundary instead. The cost was proportional to that
    count, and the count is exact.

    Since `PL-2FM6`, the test is stronger than it was written to be. The
    window holds the states at the drawn instants, so the column budget
    bounds it directly, not the window's width in samples. Two runs whose
    lengths differ by an order of magnitude, read at the same axis, hand over
    the same number of states.
    """

    window_s = 30.0
    drawn: list[int] = []

    for run_s in (60.0, 600.0):
        controller = SimulationController()
        controller.start()
        _advance_for(controller, run_s)

        elapsed_s = controller.snapshot().elapsed_s
        window = controller.drawn_window(elapsed_s - window_s, elapsed_s, 150)

        assert _samples_a_snapshot_carries(controller) == 0, (
            "the snapshot is carrying recorded history again"
        )
        assert len(window.times_s) <= 150 + 2
        # The window is the end of the run, and it ends at the instant the
        # readouts were built from.
        assert window.times_s[0] == pytest.approx(elapsed_s - window_s)
        assert window.times_s[-1] == pytest.approx(elapsed_s)

        drawn.append(len(window.times_s))

    # The run grew ten-fold, but the amount one frame reads did not grow with
    # it. The one column of slack comes from where each window sits on the
    # grid, not from growth. Columns fall at multiples of the spacing measured
    # from `t = 0`. So two windows of equal width at different places on that
    # grid can hold one column more or one column fewer.
    assert abs(drawn[1] - drawn[0]) <= 1


def test_the_window_ends_on_the_sample_the_readouts_were_built_from() -> None:
    """The right-hand end of the trace and the metrics beside it show the same instant.

    PL-0VM7 split the trace and the metrics into two separate reads. Before
    that, one snapshot carried both, so they agreed by structure. Now the test
    asserts that they agree. A window that ended one sample before the
    readouts would draw a chart that disagreed with the numbers printed
    beside it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 12.0)

    snapshot = controller.snapshot()
    window = controller.drawn_window(snapshot.elapsed_s - 5.0, snapshot.elapsed_s, 150)

    def drawn(quantity: RecordedQuantity) -> float:
        return window.compartment_fractions(RecordedSeries(snapshot.agent_id, quantity))[-1]

    assert window.times_s[-1] == pytest.approx(snapshot.elapsed_s)
    assert drawn(RecordedQuantity.CIRCUIT) == pytest.approx(
        snapshot.inspired_partial_pressure_fraction
    )
    assert drawn(RecordedQuantity.ALVEOLAR) == pytest.approx(
        snapshot.alveolar_partial_pressure_fraction
    )
    assert drawn(RecordedQuantity.FAT) == pytest.approx(snapshot.fat_partial_pressure_fraction)


def test_each_drawn_quantity_reads_the_state_of_the_compartment_it_names() -> None:
    """Audit the same pairing against the state vector that the chart draws from.

    `COMPARTMENT_STATE_INDEX` took over the pairing that `_build_history_sample`
    held, once the chart began evaluating the run definition instead of
    reading recorded samples (`PL-2FM6`). Each entry is a position in
    `governing_equations`' state order, not a compartment accessor. This table
    is the one place where a trace could come to carry another compartment's
    values. A swap here would put a curve under the wrong label, drawn
    entirely from numbers the model really produced. That is why the test
    checks the table against the core rather than restating it.

    The three tissue groups are the entries most worth the audit. They sit at
    consecutive positions starting from `FIRST_TISSUE_FRACTION`, so the table
    assumes the order of `PatientCompartmentsState.tissues`. If that order
    changed, the table would keep passing every other check.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=60.0)

    system = controller._state.uptake_system
    state = system.state_vector()

    assert {
        quantity: state[COMPARTMENT_STATE_INDEX[quantity]] for quantity in COMPARTMENT_STATE_INDEX
    } == {
        RecordedQuantity.CIRCUIT: system.circuit.inspired_partial_pressure_fraction,
        RecordedQuantity.ALVEOLAR: system.alveoli.partial_pressure_fraction,
        RecordedQuantity.MIXED_VENOUS: system.patient.mixed_venous_partial_pressure_fraction,
        RecordedQuantity.VESSEL_RICH: system.patient.vessel_rich.partial_pressure_fraction,
        RecordedQuantity.MUSCLE: system.patient.muscle.partial_pressure_fraction,
        RecordedQuantity.FAT: system.patient.fat.partial_pressure_fraction,
    }

    # Every compartment the interface draws has an entry. The derived ratio
    # has none, because it is the quotient of two of these, not a state.
    assert set(COMPARTMENT_STATE_INDEX) == set(COMPARTMENT_QUANTITIES)
    assert RecordedQuantity.WASH_IN_RATIO not in COMPARTMENT_STATE_INDEX

    # Sixty seconds into the run, the values are far enough apart that a
    # swap would show.
    drawn = [state[COMPARTMENT_STATE_INDEX[quantity]] for quantity in COMPARTMENT_QUANTITIES]
    assert len(set(drawn)) == len(drawn)
    assert drawn[0] > 100.0 * drawn[-1]


def test_a_run_records_the_agent_it_is_a_run_of() -> None:
    """The substance that keys a sample is the agent that the snapshot names.

    The view reads the two together on every frame, because it looks the run
    up under `snapshot.agent_id`. A run recorded under any other identifier
    would raise an error instead of drawing. So `set_agent` must leave the
    two in agreement.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    _advance_for(controller, duration_s=1.0)

    assert controller.drawn_window(0.0, 1.0, 150).substance_id == "isoflurane"

    controller.set_agent("desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert controller.drawn_window(0.0, 0.0, 150).substance_id == "desflurane"


def test_the_window_starts_at_the_time_asked_for_and_never_after_it() -> None:
    """A cut inside the drawn window would truncate the trace silently.

    The caller passes the left edge of the axis it is about to draw, so a
    window beginning after that time would show a run that started later
    than it did, with nothing on the chart to say so. Every sample at or
    after the requested time must be present, and the offset must locate
    the first of them within the run.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 20.0)

    elapsed_s = controller.snapshot().elapsed_s

    for start_s in (0.0, 0.05, 7.3, 19.9, 20.0):
        window = controller.drawn_window(start_s, elapsed_s, 150)

        # The window starts exactly at the requested edge, not at the first
        # sample at or after it. A column is evaluated wherever it is needed,
        # so no cut can land inside the drawn window any more.
        assert window.times_s[0] == pytest.approx(start_s)
        assert window.times_s[-1] == pytest.approx(elapsed_s)


def test_reset_pauses_and_clears_concentration_history() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))

    controller.reset()

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.inspired_partial_pressure_fraction == 0.0
    assert snapshot.alveolar_partial_pressure_fraction == 0.0
    assert snapshot.stored_agent_l == 0.0

    window = controller.drawn_window(0.0, 0.0, 150)
    assert window.times_s == (0.0,)


def test_parameter_changes_do_not_reset_dynamic_state() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    before = controller.snapshot()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_delivered_concentration_percent(Percent(6.0))

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.fresh_gas_flow_l_min == 3.0
    assert after.delivered_concentration_percent == 6.0
    # The circuit volume is a fixed model parameter, so a settings change
    # must leave it at exactly the value the session was built with (`PL-GYH2`).
    assert after.circuit_volume_l == before.circuit_volume_l


def test_the_circuit_volume_is_a_build_time_parameter_with_no_live_setter() -> None:
    """`PL-GYH2`: the app layer offers no way to change the circuit volume.

    The volume is set once, from the value this controller is built with, and
    no interface control can change it after that. The setter that used to be
    on `SimulationController` was public and had no bounds. Any caller of the
    app layer could use it to put the circuit outside the domain that
    `docs/MODEL.md` verifies, through a control the interface has never
    offered. The test asserts on the class rather than on an instance, so
    re-adding the method fails here whatever a run has done.

    `BreathingCircuit.set_circuit_volume` is deliberately left in place. It is
    how the parameter reaches the circuit at all, and it is where the
    conservation and capacity guards live (`PL-006`, `tests/unit/test_circuit.py`).
    """

    assert not hasattr(SimulationController, "set_circuit_volume")

    controller = SimulationController(circuit_volume_l=CompartmentVolume(5.0))
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    assert controller.snapshot().circuit_volume_l == 5.0


def test_a_failed_session_is_not_the_same_state_as_a_pause() -> None:
    """`is_running` alone cannot show the difference, so the failure reason does.

    A pause and a failure both stop the run, but only a pause leaves a state
    that a reader can trust. The snapshot has to say which one happened.
    """

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))

    paused = SimulationController()
    paused.start()
    paused.advance(SimulationStep(0.1))
    paused.pause()

    controller.fail("SimulationNumericalError: the step could not be completed")

    assert controller.snapshot().is_running is False
    assert controller.has_failed is True
    assert controller.snapshot().failure_reason == (
        "SimulationNumericalError: the step could not be completed"
    )

    assert paused.snapshot().is_running is False
    assert paused.has_failed is False
    assert paused.snapshot().failure_reason is None


def test_a_failed_session_cannot_be_resumed() -> None:
    """Resuming would extend a run from a step that never completed."""

    controller = SimulationController()
    controller.start()
    controller.fail("SimulationNumericalError: boom")

    with pytest.raises(SimulationExecutionError, match="cannot resume a failed simulation"):
        controller.start()

    assert controller.snapshot().is_running is False


def test_a_failed_session_does_not_advance() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.fail("SimulationNumericalError: boom")
    elapsed_at_failure = controller.snapshot().elapsed_s

    controller.advance(SimulationStep(0.1))

    assert controller.snapshot().elapsed_s == elapsed_at_failure


_STOPS: dict[str, Callable[[SimulationController], None]] = {
    "on a failure": lambda controller: controller.fail("SimulationNumericalError: boom"),
    "at the supported run length": lambda controller: controller.halt_at_supported_limit(
        "reached 86400 s of simulated time"
    ),
}
_SETTERS: dict[ControlInput, Callable[[SimulationController], None]] = {
    ControlInput.FRESH_GAS_FLOW: lambda controller: controller.set_fresh_gas_flow(
        FreshGasFlow(6.0)
    ),
    ControlInput.DELIVERED: lambda controller: controller.set_delivered_concentration_percent(
        Percent(3.0)
    ),
    ControlInput.ALVEOLAR_VENTILATION: lambda controller: controller.set_alveolar_ventilation(
        AlveolarVentilation(5.0)
    ),
    ControlInput.CARDIAC_OUTPUT: lambda controller: controller.set_cardiac_output(
        CardiacOutput(10.0)
    ),
}


# The name each refusal gives its setting, written out so a change to a label fails here.
_NAMED: dict[ControlInput, str] = {
    ControlInput.FRESH_GAS_FLOW: "fresh gas flow",
    ControlInput.DELIVERED: "delivered agent",
    ControlInput.ALVEOLAR_VENTILATION: "alveolar ventilation",
    ControlInput.CARDIAC_OUTPUT: "cardiac output",
}


@pytest.mark.parametrize("stop", list(_STOPS))
@pytest.mark.parametrize("control", list(ControlInput))
def test_a_stopped_run_refuses_every_setting_and_records_nothing(
    stop: str, control: ControlInput
) -> None:
    """No step runs after a stop, so a new setting would sit beside values it never produced.

    Until `PL-3B34` each setter applied the value and recorded a change at the
    stop instant. The dial then showed a setting that no step ran under, and
    the record claimed a change that never acted on the patient. Each setter
    now refuses before it applies anything. The expected settings come from a
    run built and stepped the same way that never stopped. The test runs once
    for each `ControlInput`, so a control added without a setter here, or
    without the refusal, fails it.
    """

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    _STOPS[stop](controller)
    never_stopped = SimulationController()
    never_stopped.start()
    never_stopped.advance(SimulationStep(0.1))

    with pytest.raises(
        SimulationConfigurationError,
        match=f"^the {_NAMED[control]} setting cannot be changed on a stopped run, because every",
    ):
        _SETTERS[control](controller)

    settings, expected = controller.settings(), never_stopped.settings()
    assert controller.record().control_timeline == ()
    assert settings.fresh_gas_flow_l_min == expected.fresh_gas_flow_l_min
    assert settings.delivered_concentration_percent == expected.delivered_concentration_percent
    assert settings.alveolar_ventilation_l_min == expected.alveolar_ventilation_l_min
    assert settings.cardiac_output_l_min == expected.cardiac_output_l_min


def test_the_first_failure_reason_is_the_one_kept() -> None:
    """A later error raised by the same broken state must not hide the first reason."""

    controller = SimulationController()
    controller.start()
    controller.fail("SimulationNumericalError: the step could not be completed")
    controller.fail("AttributeError: NoneType has no attribute 'value'")

    assert controller.snapshot().failure_reason == (
        "SimulationNumericalError: the step could not be completed"
    )


def test_reset_clears_a_failure_and_restores_a_startable_session() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.fail("SimulationNumericalError: boom")

    controller.reset()

    assert controller.has_failed is False
    assert controller.snapshot().failure_reason is None
    assert controller.snapshot().elapsed_s == 0.0

    controller.start()
    controller.advance(SimulationStep(0.1))

    assert controller.snapshot().is_running is True
    assert controller.snapshot().elapsed_s == pytest.approx(0.1)


def test_switching_agent_clears_a_failure() -> None:
    """Switching agents begins a new run, so nothing survives the old one."""

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.fail("SimulationNumericalError: boom")

    controller.set_agent("desflurane")

    assert controller.has_failed is False
    assert controller.snapshot().failure_reason is None
    assert controller.snapshot().agent_id == "desflurane"

    controller.start()

    assert controller.snapshot().is_running is True


def test_a_refused_setting_does_not_fail_the_session() -> None:
    """A rejected value changes nothing, so the run stays trustworthy."""

    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    controller.advance(SimulationStep(0.1))
    before = controller.snapshot()

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration_percent(Percent(50.0))

    after = controller.snapshot()

    assert after.failure_reason is None
    assert after.is_running is True
    assert after.delivered_concentration_percent == before.delivered_concentration_percent


class _FatThatRefusesTheStep(TissueGroup):
    """A fat group that rejects the fraction that the exact step gives it.

    Until `PL-GS5X`, these tests reached a failing step through the model
    itself. They used a patient file in which one supported step of uptake
    could draw more agent from the lungs than the lungs held. The exact step
    closed that route for good, not only for those numbers. The exact step is
    the solution of a system in which every off-diagonal entry is a transfer
    rate. So its propagator is nonnegative in every entry, and no parameter
    set can make it carry a compartment out of range.

    What these tests check has not changed and is still worth covering. A
    numerical failure that reaches the app boundary must halt the run, leave
    the chart history alone and leave every displayed value bit-identical.
    So the failure is injected here instead. `tests/unit/
    test_uptake_system_failure.py` uses the same construction and explains
    the reasoning behind it. Fat is the group that is armed, because
    `_write_state_vector` writes it last.
    """

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        super().set_partial_pressure_fraction(
            Fraction(-1.0, name=f"{self.name} partial_pressure_fraction")
        )


def _controller_one_setting_from_a_failed_step() -> SimulationController:
    """A run 60 s in, whose next step a compartment rejects partway through the write."""

    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    _advance_for(controller, duration_s=60.0)

    patient = controller._state.uptake_system.patient
    original = patient.fat
    patient.fat = _FatThatRefusesTheStep(
        name=original.name,
        volume_l=original.volume_l,
        perfusion_fraction=original.perfusion_fraction,
        blood_gas_partition_coefficient=original.blood_gas_partition_coefficient,
        tissue_gas_partition_coefficient=original.tissue_gas_partition_coefficient,
        agent_amount_l=original.agent_amount_l,
    )

    return controller


def test_a_failed_step_adds_nothing_to_the_chart_history() -> None:
    """PL-026 end to end, at the boundary that the chart is actually drawn from.

    The item's complaint was about what a halted run displays, and the traces
    are drawn from the recorded history rather than from the compartments
    directly. A failed step must therefore leave the history exactly as long
    as it was, ending on the same sample. A history one entry longer would put
    a point on the chart that no completed step produced, at a simulation
    time that never happened.
    """

    controller = _controller_one_setting_from_a_failed_step()
    before_s = controller.snapshot().elapsed_s
    before = controller.drawn_window(0.0, before_s, 150)

    with pytest.raises(SimulationNumericalError):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    after = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)

    assert controller.snapshot().elapsed_s == before_s
    assert after.times_s == before.times_s
    assert after.states == before.states


def test_a_failed_step_leaves_every_displayed_value_bit_identical() -> None:
    """Hold the metrics beside the chart to the same standard.

    Every concentration the dashboard shows comes from this snapshot, so the
    rollback in `core/` is only worth having if its result arrives here
    unchanged. The test uses `==` rather than `pytest.approx`, for the reason
    the core test gives: the claim is that nothing was written, not that what
    was written came back close.
    """

    controller = _controller_one_setting_from_a_failed_step()
    before = controller.snapshot()

    with pytest.raises(SimulationNumericalError):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    after = controller.snapshot()

    assert after.inspired_partial_pressure_fraction == before.inspired_partial_pressure_fraction
    assert after.alveolar_partial_pressure_fraction == before.alveolar_partial_pressure_fraction
    assert after.mixed_venous_partial_pressure_fraction == (
        before.mixed_venous_partial_pressure_fraction
    )
    assert after.vessel_rich_partial_pressure_fraction == (
        before.vessel_rich_partial_pressure_fraction
    )
    assert after.muscle_partial_pressure_fraction == before.muscle_partial_pressure_fraction
    assert after.fat_partial_pressure_fraction == before.fat_partial_pressure_fraction

    # The mass-accounting panel is checked too. It is a displayed value like
    # any other, and its totals are the two that the validator accumulates
    # during a step.
    assert after.delivered_agent_l == before.delivered_agent_l
    assert after.exhausted_agent_l == before.exhausted_agent_l
    assert after.stored_agent_l == before.stored_agent_l
    assert after.agent_accounting_passes_validation


def test_a_setting_change_is_recorded_with_the_time_it_took_effect() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    (change,) = controller.snapshot().control_timeline
    assert change.control is ControlInput.FRESH_GAS_FLOW
    assert change.elapsed_s == pytest.approx(1.0)
    assert change.previous_value == pytest.approx(4.0)
    assert change.new_value == pytest.approx(3.0)
    assert change.unit == "L/min"


def test_every_control_records_under_its_own_stable_identifier() -> None:
    """The stored identifiers are the timeline's contract with future runs.

    The test asserts them as literal strings, not against the enum. A rename
    would change the enum, and a recorded run stored under the old strings
    could then no longer be read. PL-9SH6 and PL-3TLK rename two of the
    setters underneath them in v0.4.1.
    """

    controller = SimulationController()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_alveolar_ventilation(AlveolarVentilation(5.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    assert [change.control.value for change in controller.snapshot().control_timeline] == [
        "fresh_gas_flow",
        "delivered",
        "alveolar_ventilation",
        "cardiac_output",
    ]


def test_every_recorded_control_carries_its_declared_unit() -> None:
    controller = SimulationController()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_alveolar_ventilation(AlveolarVentilation(5.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    for change in controller.snapshot().control_timeline:
        assert change.unit == CONTROL_INPUT_UNITS[change.control]


def test_the_delivered_dial_is_recorded_as_the_percent_the_core_holds() -> None:
    """Recording the model's fraction would break re-application.

    The timeline claims that re-applying it reproduces the run. Re-applying
    means calling the setter, which takes the percent the dial was set to
    (`PL-NJPB`). A record of 0.03 where the circuit stores 3.0 would hand a
    hundredfold error to whatever replays it.
    """

    controller = SimulationController()

    controller.set_delivered_concentration_percent(Percent(3.0))

    (change,) = controller.snapshot().control_timeline
    assert change.new_value == 3.0
    assert change.new_value == controller.snapshot().delivered_concentration_percent


def test_the_control_timeline_records_the_vaporizer_percent_as_dialled() -> None:
    """The recorded change and the run segment both give back the dial exactly.

    `PL-NJPB`. Both records used to store the fraction, which is the dial's
    percent divided by a hundred. At some dial positions, that fraction times
    a hundred does not equal the percent it came from: 0.9% read back as
    0.9000000000000001. The first assertion shows that 0.9 is such a
    position. Both recorded values are then compared with it by equality,
    not within a tolerance.
    """

    assert percent_from_fraction(fraction_from_percent(Percent(0.9))) != 0.9

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=1.0)

    controller.set_delivered_concentration_percent(Percent(0.9))

    (change,) = controller.snapshot().control_timeline
    assert change.control is ControlInput.DELIVERED
    assert change.new_value == 0.9
    assert controller.run_segments[-1].settings.delivered_concentration_percent == 0.9


def test_a_setting_equal_to_the_one_in_place_records_nothing() -> None:
    """A slider set again to the position it is already at is not a change."""

    controller = SimulationController()
    current = controller.snapshot().fresh_gas_flow_l_min

    controller.set_fresh_gas_flow(FreshGasFlow(current))

    assert controller.snapshot().control_timeline == ()


def test_a_refused_setting_records_nothing() -> None:
    """A refused setting never took effect, so it is not part of the run.

    The guarantee comes from the structure, not from chance. The recorder runs
    after the core's setter returns, so an error raised by the setter reaches
    the interface with the timeline untouched.
    """

    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_concentration_percent(Percent(50.0))

    assert controller.snapshot().control_timeline == ()
    assert not controller.has_failed


def test_changes_within_one_step_collapse_to_what_the_model_integrated() -> None:
    """Only the value in place when a step runs is ever integrated.

    A dial dragged from 2% through 3% to 4% between two steps is one change
    from 2% to 4% as far as the run is concerned, and a timeline that
    listed the intermediate value would describe a run that never happened.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)

    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_delivered_concentration_percent(Percent(4.0))

    (change,) = controller.snapshot().control_timeline
    assert change.previous_value == pytest.approx(2.0)
    assert change.new_value == pytest.approx(4.0)
    assert change.elapsed_s == pytest.approx(1.0)


def test_a_change_undone_within_one_step_leaves_no_entry() -> None:
    """Returning to the step's own value means the model saw no change."""

    controller = SimulationController()

    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_delivered_concentration_percent(Percent(2.0))

    assert controller.snapshot().control_timeline == ()


def test_the_same_control_changed_across_two_steps_records_both() -> None:
    """A setting is recorded for each step that the run was computed under."""

    controller = SimulationController()
    controller.start()

    controller.set_delivered_concentration_percent(Percent(3.0))
    _advance_for(controller, 1.0)
    controller.set_delivered_concentration_percent(Percent(4.0))

    first, second = controller.snapshot().control_timeline
    assert (first.previous_value, first.new_value) == pytest.approx((2.0, 3.0))
    assert (second.previous_value, second.new_value) == pytest.approx((3.0, 4.0))


def test_consecutive_changes_to_one_control_are_one_adjustment() -> None:
    """One drag of one slider counts as one adjustment, however many steps it spans."""

    controller = SimulationController()
    controller.start()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance_for(controller, 1.0)
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    timeline = controller.snapshot().control_timeline
    assert {change.adjustment for change in timeline} == {1}


def test_a_declared_boundary_separates_two_drags_of_one_control() -> None:
    """Timing cannot separate two drags, but the input boundary can.

    Two turns of the same dial arrive as a run of changes to one control,
    exactly as one turn does. Only the interface knows where the first
    gesture ended, and `begin_control_adjustment` is how it says so.
    """

    controller = SimulationController()
    controller.start()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance_for(controller, 60.0)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    first, second = controller.snapshot().control_timeline
    assert first.adjustment == 1
    assert second.adjustment == 2


def test_changing_a_different_control_starts_a_new_adjustment() -> None:
    controller = SimulationController()

    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    first, second = controller.snapshot().control_timeline
    assert first.adjustment == 1
    assert second.adjustment == 2


def test_reset_clears_the_control_timeline_with_the_run() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    controller.reset()

    assert controller.snapshot().control_timeline == ()


def test_reset_restarts_adjustment_numbering() -> None:
    """A run's adjustments are numbered from its own beginning.

    Carrying the count across a reset would make the first adjustment of a
    fresh run appear as the fourth of something the reader cannot see.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.set_cardiac_output(CardiacOutput(4.0))

    controller.reset()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    (change,) = controller.snapshot().control_timeline
    assert change.adjustment == 1


def test_changing_agent_clears_the_control_timeline() -> None:
    """A new agent is a new run, and the old run's inputs are not its own."""

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))

    controller.set_agent("isoflurane")

    assert controller.snapshot().control_timeline == ()


def test_the_constructor_overrides_are_not_recorded_as_changes() -> None:
    """Initial conditions are what the run starts from, not inputs to it."""

    controller = SimulationController(
        fresh_gas_flow_l_min=FreshGasFlow(3.0), cardiac_output_l_min=CardiacOutput(4.0)
    )

    assert controller.snapshot().control_timeline == ()


def test_a_recorded_change_is_stamped_with_the_instant_it_took_effect() -> None:
    """The mark belongs at the instant the run changed, and it is drawn there.

    The chart draws its control mark as a line at `elapsed_s`. Since
    `PL-2FM6`, that instant is also a column of the drawn window. So the mark
    and the kink in the trace beneath it fall at the same instant by
    construction, not because two reads happen to agree.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 2.0)

    controller.set_cardiac_output(CardiacOutput(4.0))

    (change,) = controller.snapshot().control_timeline
    elapsed_s = controller.snapshot().elapsed_s

    assert change.elapsed_s == pytest.approx(elapsed_s)
    _advance_for(controller, 2.0)
    window = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)
    assert change.elapsed_s in window.times_s


def test_a_run_nobody_has_touched_holds_nothing_to_discard() -> None:
    """Check the state of a new session, which is also the state `reset()` returns to.

    `SimulationSnapshot.has_recorded_run` lets the interface tell an agent
    change that would destroy a run from a harmless one. So the tests pin both
    of its values rather than leaving them to a caller's interpretation.
    """

    controller = SimulationController()

    assert controller.snapshot().has_recorded_run is False


def test_an_advanced_run_holds_something_to_discard() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    assert controller.snapshot().has_recorded_run is True


def test_a_setting_changed_before_the_run_starts_is_something_to_discard() -> None:
    """Elapsed time alone would miss this one.

    A vaporizer turned before Start is a recorded input at zero simulated
    time, and it is part of the case that a reader set up. A check that read
    only the clock would call this run empty and discard it without asking.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    snapshot = controller.snapshot()
    assert snapshot.elapsed_s == 0.0
    assert snapshot.control_timeline != ()
    assert snapshot.has_recorded_run is True


def test_reset_returns_a_run_to_holding_nothing_to_discard() -> None:
    """Reset is the way to make an agent change cost nothing.

    This matters. A reader who wants a different agent and does not want to
    keep their case is told to use Reset. So Reset must really clear both
    halves of the predicate.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    controller.reset()

    assert controller.snapshot().has_recorded_run is False


def test_set_agent_leaves_a_new_run_holding_nothing_to_discard() -> None:
    """Right after a confirmed switch, the new run must not count as something to discard.

    Otherwise a learner who confirmed a new case and then opened the selector
    again would be asked about a case with nothing in it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_agent("desflurane")

    assert controller.snapshot().has_recorded_run is False


def test_a_fresh_branch_holds_nothing_to_destroy() -> None:
    """`PL-7TBQ`: a new branch is built at its fork, and being built there is not a learner's act.

    The branch uses the case's clock, so its elapsed time is past zero as soon
    as it exists. Counted from zero, it held a run to lose before the learner
    had done anything to it. Counted from where it began, it holds nothing.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = BranchedCase(trunk).fork_at(fork_s)

    snapshot = branch.snapshot()

    # The premise: the clock is past zero and nothing has been recorded.
    assert snapshot.elapsed_s == snapshot.began_at_s == branch.began_at_s == fork_s
    assert snapshot.elapsed_s > 0.0
    assert snapshot.control_timeline == ()
    assert trunk.snapshot().began_at_s == 0.0

    assert snapshot.has_recorded_run is False


def test_a_fresh_branch_taken_at_a_bookmark_holds_nothing_to_destroy() -> None:
    """Check the other way to fork, at the step on which the trunk halted."""

    marked = _trunk_halted_on_a_bookmark()
    branch = BranchedCase(marked).fork_here()

    snapshot = branch.snapshot()

    assert snapshot.elapsed_s == snapshot.began_at_s == marked.snapshot().elapsed_s
    assert snapshot.has_recorded_run is False


def test_a_branch_advanced_one_step_past_its_fork_holds_something_to_destroy() -> None:
    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.start()
    branch.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert branch.snapshot().has_recorded_run is True


def test_a_setting_changed_on_a_fresh_branch_is_something_to_destroy() -> None:
    """Check the timeline half on a branch: a change made at the fork is the learner's act."""

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))

    snapshot = branch.snapshot()

    assert snapshot.elapsed_s == snapshot.began_at_s
    assert snapshot.has_recorded_run is True


def test_resetting_a_branch_returns_it_to_holding_nothing_to_destroy() -> None:
    """The case `PL-7TBQ` measured: a branch advanced, changed and reset still had a run to lose.

    A branch's reset returns it to its fork rather than to zero. So a reset
    branch is a fresh branch, and it must count as one.
    """

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.start()
    _advance_for(branch, duration_s=5.0)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    branch.reset()

    assert branch.snapshot().has_recorded_run is False


# --- Stopping at the supported run length (PL-Y5WR) --------------------------


def test_stopping_at_the_supported_run_length_is_not_a_failure() -> None:
    """Three stopped states, and the snapshot has to tell them apart.

    A pause, a failure and reaching the supported run length all leave
    `is_running` false. Only a failure means that something on screen cannot
    be trusted. The interface reads these two fields to decide what to say.
    So if a run that stopped correctly reported a `failure_reason`, the
    interface would show "simulation error" over a sound model
    (`docs/MODEL.md`, "Supported run length").
    """

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert controller.has_reached_supported_limit is True
    assert snapshot.supported_limit_reason == "reached 86400 s of simulated time"
    assert controller.has_failed is False
    assert snapshot.failure_reason is None


def test_a_session_at_the_supported_run_length_cannot_be_resumed() -> None:
    """The core would refuse Start on its first tick.

    The controller raises an error rather than quietly declining, for the
    same reason a failed session does. A Start that silently does nothing is
    a control that pretends to work. The message says which of the two
    stopped states the session is in, so a caller that reports the refusal
    does not have to guess.
    """

    controller = SimulationController()
    controller.start()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        controller.start()

    assert controller.snapshot().is_running is False


def test_the_first_supported_limit_reason_is_the_one_kept() -> None:
    """A later tick that reaches the same boundary must not overwrite the first reason."""

    controller = SimulationController()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")
    controller.halt_at_supported_limit("reached 86400 s again")

    assert controller.snapshot().supported_limit_reason == "reached 86400 s of simulated time"


def test_reset_clears_the_supported_limit_and_restores_a_startable_session() -> None:
    """Reset is the only way out of this state, so it must really work."""

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    controller.reset()

    assert controller.has_reached_supported_limit is False
    assert controller.snapshot().supported_limit_reason is None

    controller.start()

    assert controller.snapshot().is_running is True


def test_switching_agent_clears_the_supported_limit() -> None:
    """A new agent is a new run, and a new run has no run length behind it."""

    controller = SimulationController()
    controller.start()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    controller.set_agent("isoflurane")

    assert controller.has_reached_supported_limit is False
    assert controller.snapshot().supported_limit_reason is None


# `PL-T691`: the controller stores the run in two forms, as its settings over
# time and as recorded samples. The two must describe the same run. The tests
# below check the closed form against the recorded path that it is meant to
# replace. They work end to end through the controller's own setters, not
# against the core directly. `PL-2FM6` removes the recorded half. Until it
# lands, this agreement is the strongest check available, because a
# divergence in either path fails it.

CLOSED_FORM_AGREEMENT = 1e-13
"""How far the closed form may differ from the recorded run, as a fraction of 1 atm.

The disagreement was measured on 2026-09-07 over the 120 s run below. That run has
1 201 samples of six compartments each, and the largest fraction it reaches
is 0.0205. The worst disagreement is 6.7e-16, which is about three units in
the last place of the values being compared. The tolerance is set two orders
of magnitude above that, so an ordinary floating-point wobble does not fail
the suite. It is also nine orders of magnitude below the 1e-4 that a
two-decimal percent readout can show, so a real divergence still fails it.
"""


def _advance_through_halts(controller: SimulationController, duration_s: float) -> None:
    """Advance `duration_s`, resuming wherever a marked crossing halts the run.

    A marked run halts on the step that crosses one of its marks (`PL-CTD7`),
    and the halt is an ordinary pause. A driver that did not resume would
    leave a marked run stopped at its first crossing while an unmarked run
    went on. The two runs would then differ because of where the marks were,
    not because of anything the model computed. Unmarked runs never halt, so
    for a caller with no marks this helper behaves exactly like `_advance_for`.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        if not controller.is_running:
            controller.start()

        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))


def _run_with_two_changes(controller: SimulationController) -> None:
    """Drive 120 s through the controller, moving two controls on the way."""

    controller.start()
    _advance_through_halts(controller, duration_s=30.0)
    controller.set_delivered_concentration_percent(Percent(4.0))
    _advance_through_halts(controller, duration_s=30.0)
    controller.set_alveolar_ventilation(AlveolarVentilation(6.0))
    _advance_through_halts(controller, duration_s=60.0)


def test_a_setting_change_opens_a_segment_where_the_run_saw_it() -> None:
    """The run definition's segments and the timeline's entries describe one run.

    They are separate records on purpose. One is what the model integrated,
    and the other is what a reader is shown. So the test checks that they
    agree about when the run changed.
    """

    controller = SimulationController()
    _run_with_two_changes(controller)

    timeline = controller.snapshot().control_timeline
    openings = [segment.opening.instant_s for segment in controller.run_segments]

    assert [change.elapsed_s for change in timeline] == openings[1:]
    assert openings[0] == 0.0


def test_a_refused_setting_leaves_the_run_definition_describing_the_run() -> None:
    """A setting the core rejects never took effect, so it opens no segment.

    The control timeline has the same property, for the same reason. The core
    raises an error before anything is recorded, and both records describe
    the run that it left untouched.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_concentration_percent(Percent(50.0))

    assert len(controller.run_segments) == 1
    assert controller.snapshot().control_timeline == ()


def test_resetting_starts_the_run_definition_over() -> None:
    """`reset()` destroys the run, so nothing of its definition may survive it."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.reset()

    assert len(controller.run_segments) == 1
    assert controller.drawn_window(0.0, 0.0, 150).times_s == (0.0,)
    # The axis outlives the run it was showing, so the window is clipped to
    # nothing but the instant at zero.
    assert controller.drawn_window(0.0, 60.0, 150).times_s == (0.0,)


def test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was() -> None:
    """`reset()` refuses before it clears anything, so a refused Reset is not a half reset.

    The settings record that opens a run's definition is built from the
    compartments. It rejects tissue flows that no longer sum to the cardiac
    output. Before `PL-M4M0`, the record was read after the state had been
    cleared, and the refusal left the run half reset. The compartments and
    the clock were at zero, but the old definition and timeline were kept, no
    failure was recorded, and the run was still marked as running. Now the
    record is read first, and the refusal leaves everything as it was. The
    run keeps going, on its own state and definition. The interface decides
    what the refusal means (`RunView._handle_reset`).
    """

    controller = SimulationController()
    _run_with_two_changes(controller)
    before = controller.snapshot()
    segments = controller.run_segments
    _with_stale_tissue_flows(controller, 6.0)

    with pytest.raises(
        SimulationConfigurationError, match="the venous balance returns what the tissues receive"
    ):
        controller.reset()

    after = controller.snapshot()

    assert before.is_running is True
    assert after.is_running is True
    assert controller.has_failed is False
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert after.control_timeline == before.control_timeline
    assert len(after.control_timeline) == 2
    assert controller.run_segments == segments
    assert len(segments) == 3
    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(after, field) == getattr(before, field)


@pytest.mark.parametrize(
    ("change", "setting"),
    [
        (
            lambda controller: controller.set_fresh_gas_flow(FreshGasFlow(3.0)),
            "fresh_gas_flow_l_min",
        ),
        (
            lambda controller: controller.set_delivered_concentration_percent(Percent(3.0)),
            "delivered_concentration_percent",
        ),
        (
            lambda controller: controller.set_alveolar_ventilation(AlveolarVentilation(8.0)),
            "alveolar_ventilation_l_min",
        ),
    ],
    ids=["fresh-gas-flow", "delivered-concentration", "alveolar-ventilation"],
)
def test_a_setting_the_record_refuses_leaves_the_run_on_its_previous_setting(
    change: Callable[[SimulationController], None], setting: str
) -> None:
    """A setting that its compartment accepted and the settings record refused is written back.

    A compartment checks only its own value, but the settings record checks
    the fields against each other. On a run whose tissue flows no longer sum
    to the cardiac output, the record refuses every setting, and it does so
    after the setter has written the new value. Before `PL-VCP4`, the
    compartment kept the new value and the dial showed it. The open segment
    of the run's definition and the timeline kept the old value, and the
    banner said that the simulation was unchanged and still running its
    previous setting. Now the previous value is written back before the
    error is raised, so the banner is right.

    Until `PL-HQF5`, a cardiac output change repaired the mismatch, because
    it set every compartment's flow from the new output. Now the only way to
    produce the mismatch is a perfusion fraction written directly, bypassing
    its guard, and no cardiac output repairs that. So the cardiac output is
    refused and written back too. Its write-back leaves every tissue flow
    where it was. It could not do that while a changed fraction moved the
    flows that the write-back set (`PL-Z0HN`). Once the fractions are put
    back, the cardiac output and then the setting are accepted.
    """

    controller = SimulationController()
    _run_with_two_changes(controller)
    _with_stale_tissue_flows(controller, 6.0)
    before = controller.snapshot()
    segments = controller.run_segments

    with pytest.raises(
        SimulationConfigurationError,
        match="perfused at 6.0 L/min in total but cardiac output is 5.0 L/min",
    ):
        change(controller)

    after = controller.snapshot()

    assert getattr(after, setting) == getattr(before, setting)
    assert getattr(segments[-1].settings, setting) == getattr(before, setting)
    assert controller.run_segments == segments
    assert after.control_timeline == before.control_timeline
    assert after.is_running is True
    assert controller.has_failed is False

    patient = controller._state.uptake_system.patient
    flows_before = [
        tissue.blood_flow_l_min_at(patient.cardiac_output_l_min) for tissue in patient.tissues
    ]

    with pytest.raises(
        SimulationConfigurationError,
        match="perfused at 7.2 L/min in total but cardiac output is 6.0 L/min",
    ):
        controller.set_cardiac_output(CardiacOutput(6.0))

    assert controller.snapshot().cardiac_output_l_min == before.cardiac_output_l_min == 5.0
    assert [
        tissue.blood_flow_l_min_at(patient.cardiac_output_l_min) for tissue in patient.tissues
    ] == flows_before
    assert controller.run_segments == segments
    assert controller.snapshot().control_timeline == before.control_timeline

    _with_the_tissue_fractions_put_back(controller)
    controller.set_cardiac_output(CardiacOutput(6.0))
    change(controller)

    repaired = controller.snapshot()

    assert repaired.cardiac_output_l_min == 6.0
    assert getattr(repaired, setting) != getattr(before, setting)
    assert getattr(controller.run_segments[-1].settings, setting) == getattr(repaired, setting)
    assert len(repaired.control_timeline) == len(before.control_timeline) + 2


_WRITES_PAST_THE_CONTROLLER: tuple[
    tuple[str, Callable[[uptake_system.AgentUptakeSystem], None]], ...
] = (
    ("cardiac-output", lambda system: system.set_cardiac_output(CardiacOutput(6.0))),
    ("fresh-gas-flow", lambda system: system.circuit.set_fresh_gas_flow(FreshGasFlow(6.0))),
    (
        "alveolar-ventilation",
        lambda system: system.alveoli.set_alveolar_ventilation(AlveolarVentilation(6.0)),
    ),
    ("delivered", lambda system: system.circuit.set_delivered_concentration_percent(Percent(3.0))),
)


@pytest.mark.parametrize(
    "write",
    [write for _, write in _WRITES_PAST_THE_CONTROLLER],
    ids=[name for name, _ in _WRITES_PAST_THE_CONTROLLER],
)
def test_a_setting_written_onto_the_core_past_the_controller_refuses_the_next_step(
    write: Callable[[uptake_system.AgentUptakeSystem], None],
) -> None:
    """A setting the run definition never recorded stops the run before it is stepped (`PL-XRN8`).

    The readouts come from the steps, and the chart comes from the run
    definition. A step at a setting that the definition does not contain would
    make them describe two different runs. So the controller refuses the step
    instead. Each write here calls a core setter that the interface never
    calls, with a value other than the reference default.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    system = controller._state.uptake_system
    recorded = controller.run_segments
    state_before = system.state_vector()
    elapsed_before = controller.snapshot().elapsed_s

    write(system)

    assert system.equation_settings() != recorded[-1].settings

    with pytest.raises(SimulationExecutionError, match="without SimulationController recording it"):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert system.state_vector() == state_before
    assert controller.snapshot().elapsed_s == elapsed_before == 10.0
    assert controller.run_segments == recorded


def test_reset_after_a_setting_written_past_the_controller_runs_at_that_setting() -> None:
    """Reset starts a new run from the core's current settings, so it steps again (`PL-XRN8`).

    The expected trajectory is a fresh controller built at the same cardiac
    output, rather than anything read from the controller under test.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller._state.uptake_system.set_cardiac_output(CardiacOutput(6.0))

    with pytest.raises(SimulationExecutionError):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    controller.reset()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    fresh = SimulationController(cardiac_output_l_min=CardiacOutput(6.0))
    fresh.start()
    _advance_for(fresh, duration_s=10.0)

    assert controller.run_segments[0].settings.cardiac_output_l_min == 6.0
    assert controller._state.uptake_system.state_vector() == (
        fresh._state.uptake_system.state_vector()
    )


def test_a_setting_written_onto_a_branch_s_core_past_its_controller_refuses_its_next_step() -> None:
    """A branch records its own settings at its fork and enforces them on its core (`PL-XRN8`)."""

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=10.0)
    trunk.pause()
    branch = BranchedCase(trunk).fork_here()
    branch.start()
    _advance_for(branch, duration_s=10.0)

    branch._state.uptake_system.set_cardiac_output(CardiacOutput(6.0))

    with pytest.raises(SimulationExecutionError, match="without SimulationController recording it"):
        branch.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    trunk.start()
    _advance_for(trunk, duration_s=10.0)

    assert trunk.snapshot().elapsed_s == 20.0


def test_changing_agent_starts_the_run_definition_over() -> None:
    """`set_agent` begins a new run, and a run definition describes only one run."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.set_agent("desflurane")

    assert len(controller.run_segments) == 1
    assert controller.drawn_window(0.0, 60.0, 150).times_s == (0.0,)


def test_a_paused_run_s_definition_stops_where_the_run_did() -> None:
    """Pausing stops the run, so the run definition returns no values past the pause."""

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.pause()
    _advance_for(controller, duration_s=10.0)

    elapsed_s = controller.snapshot().elapsed_s

    # The axis may extend past a paused run. The trace stops where the run
    # stopped and is not extended into a prediction.
    window = controller.drawn_window(0.0, elapsed_s + MAXIMUM_SIMULATION_STEP_S, 150)

    assert window.times_s[-1] == pytest.approx(elapsed_s)


def test_the_drawn_window_is_clipped_to_the_run_not_to_the_axis() -> None:
    """The axis extends past the run by design, but the trace must not.

    `following_window` keeps empty axis to the right of the newest instant.
    `fitted_window` returns the chosen rung's full width however short the
    run is. Both do this so that a trace's slope means the same thing at every
    moment. So the drawn range ends where the run ends, and `times_s` shows
    that, rather than being padded to the axis.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=60.0)

    window = controller.drawn_window(0.0, 900.0, 150)

    assert window.times_s[0] == 0.0
    assert window.times_s[-1] == pytest.approx(controller.snapshot().elapsed_s)
    assert window.times_s[-1] < 900.0


def test_the_drawn_window_places_a_column_on_every_control_change() -> None:
    """A dial change inside the window is an instant the chart actually plots.

    This is `PL-4RBD`'s guarantee, now provided by the structure. The columns
    are evaluated rather than selected, so the change is a column itself, not
    a sample that the decimation had to be persuaded to keep.
    """

    controller = SimulationController()
    _run_with_two_changes(controller)

    window = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)
    changes = {change.elapsed_s for change in controller.snapshot().control_timeline}

    assert changes
    assert changes <= set(window.times_s)


def test_a_drawn_window_refuses_another_substance() -> None:
    """A trace drawn from another agent's values misstates the run."""

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    window = controller.drawn_window(0.0, 10.0, 150)

    with pytest.raises(SimulationConfigurationError, match="a run is of one agent"):
        window.compartment_fractions(RecordedSeries("desflurane", RecordedQuantity.CIRCUIT))

    with pytest.raises(SimulationConfigurationError, match="a run is of one agent"):
        window.wash_in_quotients("desflurane")


def test_a_drawn_window_refuses_the_derived_ratio_as_a_compartment() -> None:
    """F_A/F_I is a quotient of two states, so the window does not treat it as a state."""

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    window = controller.drawn_window(0.0, 10.0, 150)
    agent_id = controller.snapshot().agent_id

    with pytest.raises(SimulationConfigurationError, match="not a compartment state"):
        window.compartment_fractions(RecordedSeries(agent_id, RecordedQuantity.WASH_IN_RATIO))


def _read_the_alveolar_quotient_as(monkeypatch: pytest.MonkeyPatch, quotient: float) -> None:
    """Make every alveolar compartment return `quotient` as its partial-pressure fraction.

    This is the one way left to get a quotient outside 0 to 1. No supported
    setting produces one (`core/concentration.py`). Since `PL-544D`, an
    amount larger than the capacity is refused when it is written. So the
    helper replaces the quotient that every alveolar compartment returns, for
    the snapshot and the stepper alike, rather than producing it through the
    stored amount.
    """

    monkeypatch.setattr(
        AlveolarCompartment, "partial_pressure_fraction", property(lambda compartment: quotient)
    )


def test_a_snapshot_whose_quotient_is_refused_names_the_compartment_and_the_status_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`snapshot()` builds each compartment's fraction under its name, and `status()` builds none.

    The compartments store amounts, and a quotient computed from one carries
    no proof that it is in range. So the snapshot builds the `Fraction` and
    rejects a quotient greater than 1. The test reaches such a quotient by
    replacing the quotient that the alveolar compartment returns. No supported
    setting produces one (`core/concentration.py`), and since `PL-544D` a
    write beyond the capacity is refused. The refusal names the compartment
    as a step would (`run_series.COMPARTMENT_FRACTION_NAMES`). `status()`,
    which the interface uses to report the halt, still returns a result for
    the same run. A snapshot is a `RunStatus` too, so code that reads one can
    read either (`PL-7DJK`).
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=5.0)

    assert isinstance(controller.snapshot(), RunStatus)

    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^alveolar partial_pressure_fraction of 1\.0000001 is outside 0 to 1",
    ):
        controller.snapshot()

    assert controller.status() == RunStatus(
        is_running=True, supported_limit_reason=None, failure_reason=None, rejected_accounting=None
    )

    controller.fail("SimulationConfigurationError: alveolar partial_pressure_fraction refused")

    assert controller.status() == RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason="SimulationConfigurationError: alveolar partial_pressure_fraction refused",
        rejected_accounting=None,
    )


def test_settings_are_read_of_a_run_whose_snapshot_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """`settings()` returns the run's settings even when the run's `snapshot()` refuses.

    A `RunSettings` is built from the agent and the four settings that the
    compartments store. Each setting is a checked type, built when it was
    set, and no compartment value is used. So a dial dragged into a halt can
    still be set from what the run stores (`PL-85LJ`). A snapshot is a
    `RunSettings` too, so code that reads one can read either.

    The test sets each of the four settings to a value that differs from the
    others and from its default, and expects back what it set. The shipped
    fresh gas flow and alveolar ventilation are both 4.0 L/min, so with those
    left equal a `settings()` that built the ventilation from the fresh gas
    flow passed every test (`PL-5V5F`).
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=5.0)
    controller.set_fresh_gas_flow(FreshGasFlow(6.0))
    controller.set_delivered_concentration_percent(Percent(3.0))
    controller.set_alveolar_ventilation(AlveolarVentilation(5.5))
    controller.set_cardiac_output(CardiacOutput(6.5))
    snapshot = controller.snapshot()

    assert isinstance(snapshot, RunSettings)

    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    with pytest.raises(SimulationConfigurationError):
        controller.snapshot()

    settings = controller.settings()

    assert settings.fresh_gas_flow_l_min == 6.0
    assert settings.delivered_concentration_percent == 3.0
    assert settings.alveolar_ventilation_l_min == 5.5
    assert settings.cardiac_output_l_min == 6.5
    assert settings == RunSettings(
        is_running=True,
        supported_limit_reason=None,
        failure_reason=None,
        rejected_accounting=None,
        agent_id=snapshot.agent_id,
        agent_display_name=snapshot.agent_display_name,
        max_delivered_concentration_percent=snapshot.max_delivered_concentration_percent,
        agent_mac_percent=snapshot.agent_mac_percent,
        fresh_gas_flow_l_min=snapshot.fresh_gas_flow_l_min,
        accepted_fresh_gas_flow_range_l_min=snapshot.accepted_fresh_gas_flow_range_l_min,
        delivered_concentration_percent=snapshot.delivered_concentration_percent,
        alveolar_ventilation_l_min=snapshot.alveolar_ventilation_l_min,
        cardiac_output_l_min=snapshot.cardiac_output_l_min,
    )


def test_set_agent_on_a_run_whose_snapshot_refuses_raises_before_it_changes_anything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`set_agent` carries the settings over from the snapshot, so the refusal is `set_agent`'s.

    The snapshot is read before the run is paused. So the refusal leaves the
    run as it was: running, on its own agent, with nothing failed. A refused
    setting behaves the same way everywhere else. `agent_id` still returns a
    result, read from the settings record and not from any compartment. The
    interface puts the selector back to that agent (`PL-V2HC`).
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=5.0)
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^alveolar partial_pressure_fraction of 1\.0000001 is outside 0 to 1",
    ):
        controller.set_agent("desflurane")

    assert controller.agent_id == "sevoflurane"
    assert controller.status() == RunStatus(
        is_running=True, supported_limit_reason=None, failure_reason=None, rejected_accounting=None
    )


def test_wash_in_is_formed_per_drawn_column() -> None:
    """The ratio is a property of the instant plotted, not of a recorded sample.

    Every drawn instant gets a quotient. A run that has just started contains
    both the opening stretch, which has no quotient at all, and the wash-in
    that follows it. So the boundary between them falls on a column that the
    chart plots, not on a sample that the chart might not have selected.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=120.0)

    window = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)
    quotients = window.wash_in_quotients(controller.snapshot().agent_id)

    assert len(quotients) == len(window.times_s)
    # The opening stretch has no quotient: no agent has reached the circuit.
    assert quotients[0] is None
    assert any(quotient is not None for quotient in quotients)
    # Every quotient that exists is inside the uptake regime for this run.
    assert all(is_wash_in(quotient) for quotient in quotients if quotient is not None)


def test_an_axis_entirely_ahead_of_the_run_draws_nothing() -> None:
    """A window that lies wholly after the run's current end is empty rather than an error.

    This is an ordinary state at the very start of a run. An empty window
    draws nothing, which is correct, and drawing nothing is not the same as
    drawing a zero.
    """

    controller = SimulationController()
    controller.start()

    window = controller.drawn_window(60.0, 960.0, 150)

    assert window.times_s == ()
    assert window.states == ()


def test_an_axis_entirely_before_a_branch_s_fork_draws_nothing() -> None:
    """The other half of the same ordinary state, the half that a branch meets.

    A branch has no state before the instant it was forked at. Since
    `PL-ZMRT`, its run definition refuses such an instant rather than
    returning a value from the nearest keyframe it happens to have. So the
    window is clipped to the run's opening, and it comes back empty when the
    axis ends to the left of the opening. It does not raise an error out of
    the render loop. Clipping to a literal zero instead of to the opening
    would have raised that error on an ordinary frame.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    window = branch.drawn_window(0.0, fork_s / 2, 150)

    assert window.times_s == ()
    assert window.states == ()

    # The trunk draws something on the same axis. The two differ because the
    # branch did not exist yet, not because the axis was rejected.
    assert trunk.drawn_window(0.0, fork_s / 2, 150).times_s != ()


def test_a_control_change_is_drawn_at_every_time_base_the_reader_can_select() -> None:
    """`PL-4RBD`: a dial change that leaves the trace rising is still a drawn point.

    The defect this test closes came from selecting recorded extremes. When
    the dial was turned down, the kink was a local maximum and was drawn.
    When the dial was turned up mid-rise, the trace kept rising and the kink
    fell inside a bucket. The polyline then went straight through the one
    instant a reader was looking for. Re-measured on 2026-09-08 at the shipped
    time bases, the error reached 0.65 pp on the alveolar trace at the 12 h
    base, which is 0.32 MAC.

    Evaluating columns removes the defect at every width, not only at the
    widths somebody remembered to check. That is why the test walks the whole
    ladder of time bases. The change is a column because it is an event, not
    because the spacing happened to land on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=60.0)
    # The dial is turned *up* mid-rise, the case that a selection of extremes
    # could not capture.
    controller.set_delivered_concentration_percent(Percent(4.0))
    change_s = controller.snapshot().elapsed_s
    _advance_for(controller, duration_s=60.0)

    elapsed_s = controller.snapshot().elapsed_s

    for time_base in TIME_BASE_LADDER:
        window = controller.drawn_window(0.0, time_base.span_s, 150)

        assert change_s in window.times_s, (
            f"the dial change at {change_s} s is not drawn at the {time_base.span_s} s time base"
        )
        assert window.times_s[-1] == pytest.approx(min(time_base.span_s, elapsed_s))


# `PL-J2TD`: a fork resumes into a live run. The tests below check the seam
# between a canonical keyframe state and a running system: the state a branch
# opens at, what its clock reads, and what it refuses. They work end to end
# through the controller, because only the controller holds both of the
# records that a branch must keep in agreement.

COMPARTMENT_SNAPSHOT_FIELDS = (
    "inspired_partial_pressure_fraction",
    "alveolar_partial_pressure_fraction",
    "mixed_venous_partial_pressure_fraction",
    "vessel_rich_partial_pressure_fraction",
    "muscle_partial_pressure_fraction",
    "fat_partial_pressure_fraction",
)
"""The six compartment fractions a snapshot carries, named as the snapshot names them.

The names are written out rather than derived from `COMPARTMENT_QUANTITIES`.
That tuple is keyed by the quantity the *chart* draws, and one of its names
differs from the snapshot's. The circuit's drawn quantity is `circuit`, while
the snapshot field is `inspired_partial_pressure_fraction`. The state is named
for the clinical quantity, but the container is still the circuit.
"""

BRANCH_AGREEMENT = 1e-14
"""How far a branch's live state may differ from its parent's, in fractions of 1 atm.

The two reach the same instant by different routes. The parent steps the whole
way from induction. The branch is placed at a keyframe that the canonical path
computed, and steps only from there. `docs/MODEL.md` § "Closed-form agreement
test" governs that comparison. It also gives the reason for stating the bound
in fractions of one atmosphere rather than as a relative bound. A relative
bound would tighten without limit on the near-zero fat fraction of a 120 s
run, and it would say nothing about a displayed digit.

Measured on 2026-09-14 on the run below, the worst disagreement across all six
compartments is 2.7e-16, about one unit in the last place. The two cumulative
accumulators agree to 1.6e-15 L. The bound is set two orders of magnitude
above that, so an ordinary floating-point wobble does not fail the suite. It
is also ten orders of magnitude below the 1e-4 that a two-decimal percent
readout can show, so a real divergence still fails it.
"""


def _trunk_with_two_changes() -> SimulationController:
    """A 120 s sevoflurane run with two setting changes, so it has three keyframes."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.pause()

    return controller


def test_a_fork_opens_at_a_keyframe_on_the_case_s_own_axis() -> None:
    """The item's own deliverable, in one test.

    A branch opens at a canonical keyframe state of another run. Both its
    clock and its definition start at the instant it was forked from. That is
    because a branch is one patient's case under a second management, and
    uptake is a function of time since induction. The test asserts the clock
    and the definition together, because their agreement is what `PL-ZMRT`
    delivered. While the definition opened at a zero of its own, a branch
    carried two time frames, and every reader had to know which one it was
    using.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s

    branch = trunk.resumed_at(fork_s)

    # The branch uses the case's clock: it starts at the fork instant, not at zero.
    assert branch.snapshot().elapsed_s == fork_s

    # The definition uses the case's clock too, and opens *at* the keyframe it carries.
    assert branch.run_segments[0].opening.instant_s == fork_s
    assert branch.run_segments[0].opening.state == trunk.run_segments[-1].opening.state

    # And the state that arrived is the parent's keyframe, element for element.
    for entry in COMPARTMENT_STATE_INDEX.values():
        assert (
            branch.run_segments[0].opening.state[entry]
            == (trunk.run_segments[-1].opening.state[entry])
        )

    # It is a live run: it advances by the path every run takes.
    branch.start()
    _advance_for(branch, duration_s=10.0)

    assert branch.snapshot().elapsed_s == fork_s + 10.0

    # The opening does not move, and the reach follows the clock exactly. Since
    # `PL-ZMRT`, the reach and the clock are one quantity, not two related by
    # an offset. So asserting that they are equal asserts that no frame
    # conversion is left.
    assert branch.run_segments[0].opening.instant_s == fork_s
    assert branch._run_definition.reached_s == branch.snapshot().elapsed_s


def test_a_branch_continues_the_case_s_step_count_so_the_envelope_is_the_case_s() -> None:
    """The 24 h supported run length belongs to the patient, not to each branch.

    `require_supported_run_length` reads a step count, so a branch that
    restarted the count would get a fresh 24 h envelope. A fork taken late
    could then be advanced well past the span that `docs/MODEL.md` § "Supported
    run length" declares, with every guard passing. The model is not claimed to
    represent a patient for a run that long. As `core/supported_ranges.py`
    argues, the model omits metabolism and its fat flow is uncertain, so how
    far the slow part of the trace can stray from a patient grows as a run
    goes on. When the branch
    continues the parent's count, the whole case has one envelope, and no
    second guard is needed.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s

    branch = trunk.resumed_at(fork_s)

    assert branch._state.step_count == round(fork_s / MAXIMUM_SIMULATION_STEP_S)
    assert branch._state.simulation_step_s == MAXIMUM_SIMULATION_STEP_S
    assert branch.snapshot().elapsed_s == fork_s


def test_a_branch_reproduces_its_parent_at_every_instant_they_share() -> None:
    """`ROADMAP.md` item 12, element-wise rather than within a tolerance.

    The parent and the branch are both advanced past the fork in the same way.
    At every instant they share, they must agree entry for entry on the
    canonical path. The instants probed are the case's own: a whole number of
    steps times the step, which is the only way simulated time is ever formed
    here. Both runs are asked for each instant directly. There is nothing to
    convert. Since `PL-ZMRT`, the branch's definition opens at the fork on
    that same axis, so parent and child form their intervals from the
    identical pair of floats.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    trunk.start()
    _advance_for(trunk, duration_s=20.0)
    trunk.pause()

    branch.start()
    _advance_for(branch, duration_s=20.0)
    branch.pause()

    trunk_definition = trunk._run_definition
    branch_definition = branch._run_definition
    fork_steps = round(fork_s / MAXIMUM_SIMULATION_STEP_S)

    for steps_past_fork in range(0, 201):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S

        assert branch_definition.state_at(case_s) == trunk_definition.state_at(case_s), (
            f"the branch and its parent differ at {case_s} s"
        )


def test_a_branch_on_its_own_axis_would_not_reproduce_its_parent() -> None:
    """Why the branch opens at the fork, measured at this seam rather than quoted.

    `PL-ZMRT` replaced the arrangement in which a definition opened at a zero
    of its own. That arrangement was not so much wrong as conditional. It
    reproduced the parent exactly *provided* every caller reached it by
    subtracting the fork instant. It silently failed when a caller named the
    branch's own elapsed time instead. The difference is real because the
    subtraction does not round-trip. With a fork at 900 s,
    `(900.0 + 1e-6) - 900.0` is 9.999999974752427e-07 and not 1e-6. So the
    two routes are exact solutions of the same equations composed in
    different orders, and `PL-Z3W6` requires the composition to be the same,
    not only the solution.

    Measured on the run below, the branch and its parent share 601 case
    instants. Asked for the case's own instants, the shipped branch agrees
    with its parent at every one. A definition opened at its own zero and
    asked for `steps * step` differs at **354 of them**. The test builds the
    second run itself rather than getting it from the controller, because the
    controller can no longer produce one, which is the point.

    The test fails openly if the two ever coincide. That would mean the hazard
    no longer existed and the test no longer showed anything.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()

    branch.start()
    _advance_for(branch, duration_s=60.0)
    branch.pause()

    trunk_definition = trunk._run_definition
    branch_definition = branch._run_definition
    fork_segment = trunk.run_segments[-1]
    # The rejected arrangement, which nothing in `src/` builds any more: the
    # same keyframe under the same settings, opened at a zero of its own.
    on_its_own_axis = RunDefinition(
        fork_segment.settings, fork_segment.opening.state, opened_at_s=CaseInstant(0.0)
    )
    on_its_own_axis.advance_to(CaseInstant(60.0))

    fork_steps = round(fork_s / MAXIMUM_SIMULATION_STEP_S)
    shipped_differs = 0
    own_axis_differs = 0

    for steps_past_fork in range(0, 601):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S
        parent_state = trunk_definition.state_at(case_s)

        shipped_differs += branch_definition.state_at(case_s) != parent_state
        own_axis_differs += (
            on_its_own_axis.state_at(steps_past_fork * MAXIMUM_SIMULATION_STEP_S) != parent_state
        )

    assert shipped_differs == 0, (
        "a branch opening at the fork is asked for the case's own instants and must be exact"
    )
    assert own_axis_differs > 0, (
        "a branch on its own axis now agrees everywhere, so the hazard this test "
        "exists to describe has stopped existing"
    )


def test_a_branch_steps_to_where_its_parent_stepped() -> None:
    """The live path agrees too, and a canonical comparison cannot see that half.

    The parent stepped from induction to 120 s. The branch was placed at the
    60 s keyframe and stepped from there. At the same case instant, the two
    must describe one patient. Any comparison of two managements rests on that
    claim, because everything before the fork has to be the same history, not
    a reproduction of it.
    """

    trunk = _trunk_with_two_changes()
    at_end = trunk.snapshot()
    fork_s = trunk.run_segments[-1].opening.instant_s

    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=at_end.elapsed_s - fork_s)

    resumed = branch.snapshot()

    assert resumed.elapsed_s == at_end.elapsed_s, "the two must be compared at one case instant"

    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert abs(getattr(at_end, field) - getattr(resumed, field)) < BRANCH_AGREEMENT, (
            f"{field} diverged across the fork"
        )

    assert abs(at_end.delivered_agent_l - resumed.delivered_agent_l) < BRANCH_AGREEMENT
    assert abs(at_end.exhausted_agent_l - resumed.exhausted_agent_l) < BRANCH_AGREEMENT


def test_a_branch_s_drawn_window_is_on_the_case_s_axis() -> None:
    """The chart uses one time axis, whichever run fills it.

    `drawn_window` takes the axis the caller has set and returns the instants
    it drew. On a branch, as on a trunk, both are in the case's time. Since
    `PL-ZMRT`, there is no second time frame for either to be in. A window
    measured from the fork would draw a correct trace at the wrong place on a
    labelled axis. `CLAUDE.md`'s safety-critical standard counts that as a
    presentation failure, not as a lesser kind of error.

    The test deliberately passes a left edge earlier than the branch's fork.
    That exercises the clamp in `drawn_window`, which clips to the run's own
    opening rather than to zero. Clipping to zero would ask the definition for
    an instant before the branch existed. The definition refuses such an
    instant, so an ordinary frame on a branch would raise an error out of the
    render loop.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10.0)

    window = branch.drawn_window(0.0, fork_s + 10.0, 150)

    assert window.times_s[0] == fork_s, "a branch draws nothing before the fork"
    assert window.times_s[-1] == fork_s + 10.0
    assert all(time_s >= fork_s for time_s in window.times_s)


def test_a_trunk_s_drawn_window_spans_the_axis_it_was_asked_for() -> None:
    """A trunk opens at the case's zero, so the whole axis is inside its run."""

    trunk = _trunk_with_two_changes()
    snapshot = trunk.snapshot()

    window = trunk.drawn_window(0.0, snapshot.elapsed_s, 150)

    assert trunk.run_segments[0].opening.instant_s == 0.0
    assert window.times_s[0] == 0.0
    assert window.times_s[-1] == snapshot.elapsed_s


def test_a_branch_is_drawn_on_the_same_columns_as_the_run_it_forked_from() -> None:
    """One shared time frame aligns the chart's columns, so `PL-2R2C` needed no fix.

    `RunDefinition.evaluate_anchored` lays its grid on absolute multiples of
    the spacing, measured in the definition's own frame. This is deliberate. A
    grid anchored to the window instead makes every drawn point a new instant
    on every frame, and `PL-Q197` measured that as the cause of the saturated
    client. While a branch's definition opened at a zero of its own, its
    columns fell at `fork + m x spacing`, against the trunk's `m x spacing`.
    On this 13-column 120 s axis, with the fork deliberately off the grid at
    55.3 s, 2 of the branch's 8 columns landed where the trunk also drew. A
    learner then could not read "at this instant the trunk was here and the
    branch was there" from matched points. Any difference trace or shared
    tooltip built on that assumption would be wrong, not merely coarse.

    One time frame makes the columns coincide, with nothing added to the
    display path. Both definitions are on the case's axis, so both grids use
    the same multiples. The fork instant itself is a column on the trunk
    because it is a setting change. It is the branch's first column because
    it is where the branch opens.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=55.3)
    trunk.set_delivered_concentration_percent(Percent(4.0))
    _advance_for(trunk, duration_s=64.7)
    trunk.pause()

    fork_s = trunk.run_segments[-1].opening.instant_s
    stop_s = trunk.snapshot().elapsed_s
    branch = trunk.resumed_at(fork_s)

    branch.start()
    _advance_for(branch, duration_s=stop_s - fork_s)
    branch.pause()

    trunk_columns = trunk.drawn_window(0.0, stop_s, 13).times_s
    branch_columns = branch.drawn_window(0.0, stop_s, 13).times_s

    # The fork is deliberately not a multiple of the 10 s spacing. If it were,
    # the two grids would coincide whatever frame the branch was in, and the
    # test would pass without showing anything.
    assert fork_s % ((stop_s - 0.0) / 12) != 0.0

    assert set(branch_columns) <= set(trunk_columns), (
        "the branch is drawn at instants the trunk never draws, so the two "
        "traces cannot be read against each other"
    )
    assert len(branch_columns) > 2

    # The axis extends to the left of the fork. The branch's window is clipped
    # at its opening rather than refused, and it starts exactly there.
    assert branch_columns[0] == fork_s
    assert branch_columns[-1] == trunk_columns[-1]


def test_a_control_moved_before_a_branch_steps_reopens_its_first_segment() -> None:
    """The learner's actual first act on a branch, which is to change something.

    When the run has not advanced past the open segment's own opening,
    `RunDefinition.record_change` replaces that segment's settings in place.
    It does not record a zero-length stretch that nothing was ever computed
    under. The check it makes is an equality between the run's reach and its
    first keyframe's instant. On a branch, both of those are now the fork
    instant, where they used to be zero. So the behaviour is worth asserting
    rather than assuming from the code. A version that initialised only one
    of the two would open a zero-length segment here, and the run would still
    look right.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    assert len(branch.run_segments) == 1

    branch.set_delivered_concentration_percent(Percent(1.0))

    assert len(branch.run_segments) == 1
    assert branch.run_segments[0].opening.instant_s == fork_s
    assert branch.run_segments[0].opening.state == trunk.run_segments[-1].opening.state

    # And the new settings are the ones the run is then computed under.
    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.pause()

    assert branch.run_segments[0].settings.delivered_concentration_percent == 1.0
    assert len(branch.run_segments) == 1


def test_a_branch_carries_the_case_s_delivered_and_exhausted_totals() -> None:
    """The litres a branch reports are the patient's, not the branch's own.

    A branch that restarted them at zero would show a mass-balance readout
    that is correct for the branch and wrong for the patient. It would do so
    at the moment a learner is most likely to compare two managements by how
    much agent each used.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    at_fork = branch.snapshot()

    assert at_fork.delivered_agent_l > 0.0
    assert at_fork.agent_accounting_passes_validation
    assert at_fork.delivered_agent_l == trunk.run_segments[-1].opening.state[DELIVERED_AGENT_L]
    assert at_fork.exhausted_agent_l == trunk.run_segments[-1].opening.state[EXHAUSTED_AGENT_L]


def test_a_branch_opens_with_its_own_empty_control_timeline() -> None:
    """A branch records the acts its own learner makes, not its parent's.

    The history before the fork belongs to the trunk and is not reproduced
    here. What a branch carries forward is the *state* that history produced.
    """

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert branch.snapshot().control_timeline == ()
    assert trunk.snapshot().control_timeline != ()


def test_a_branch_inherits_its_parent_s_settings_at_the_fork() -> None:
    """The settings are replayed from the recorded timeline, then checked against the segment.

    The check is the point. A branch that assembled a system matrix its parent
    never used would diverge from its first step. The divergence would stay
    inside the tolerance that keeps the two records in agreement, and nothing
    would report it.
    """

    trunk = _trunk_with_two_changes()

    for segment in trunk.run_segments:
        branch = trunk.resumed_at(segment.opening.instant_s)

        assert branch._state.uptake_system.equation_settings() == segment.settings


def test_a_settings_mismatch_names_the_setting_that_differs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression (`PL-NC62`): the refusal states what differs, never a cause.

    A branch re-reads the agent's data file when it is rebuilt. So a file
    edited between the trunk and the branch fails the settings check, even
    though the control timeline is not at fault. Whatever had differed, the
    refusal used to say that the timeline did not reproduce its own segments.
    That sent its reader to the one part that was working.
    """

    trunk = _trunk_with_two_changes()
    before = trunk.snapshot()
    on_file = load_agent_parameters(before.agent_id)
    edited = dataclasses.replace(
        on_file,
        blood_gas_partition_coefficient=PartitionCoefficient(
            on_file.blood_gas_partition_coefficient + 0.05
        ),
    )
    monkeypatch.setattr(uptake_system, "load_agent_parameters", lambda agent_id: edited)

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert (
        f"blood_gas_partition_coefficient is {on_file.blood_gas_partition_coefficient!r} "
        f"in this run and {edited.blood_gas_partition_coefficient!r} on the branch"
    ) in str(refusal.value)
    assert "timeline" not in str(refusal.value)
    assert trunk.snapshot() == before


def test_a_patient_mismatch_names_the_tissue_group_it_is_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Three tissue groups share each field name, so the message names the group too."""

    trunk = _trunk_with_two_changes()
    on_file = load_reference_adult_parameters()
    edited = dataclasses.replace(
        on_file, muscle_volume_l=CompartmentVolume(on_file.muscle_volume_l + 1.0)
    )
    monkeypatch.setattr(uptake_system, "load_reference_adult_parameters", lambda: edited)

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert (
        f"muscle volume_l is {on_file.muscle_volume_l!r} in this run and "
        f"{edited.muscle_volume_l!r} on the branch"
    ) in str(refusal.value)


def test_a_branch_rebuilt_under_another_mac_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """`PL-NC62`'s second gap: an agent reference that no equation reads is checked too.

    Every MAC multiple on screen is a concentration divided by the MAC, and a
    branch re-reads the MAC from the agent's file. A branch rebuilt under a
    different MAC would show one concentration as a different multiple from
    its parent's, while every equation setting agreed. So the settings check
    alone let it through.
    """

    trunk = _trunk_with_two_changes()
    on_file = load_agent_parameters(trunk.snapshot().agent_id)
    edited = dataclasses.replace(on_file, mac_percent=MacPercent(on_file.mac_percent + 0.1))
    monkeypatch.setattr(
        "anesthesia_sim.app.controller.load_agent_parameters", lambda agent_id: edited
    )

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert (
        f"agent_mac_percent is {on_file.mac_percent!r} in this run and "
        f"{edited.mac_percent!r} on the branch"
    ) in str(refusal.value)


def test_a_vaporizer_maximum_edited_before_a_branch_is_named_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A vaporizer maximum edited between a trunk and its branch is named once, as one difference.

    The equation settings carry the circuit's vaporizer maximum (`PL-BBMG`).
    The controller used to keep a second copy, read from the same file, and
    compared that copy as a displayed reference. So the one edit appeared twice
    in the message that refused the branch, and sent its reader looking for a
    second edit (`PL-1MGB`).
    """

    trunk = _trunk_with_two_changes()
    on_file = load_agent_parameters(trunk.snapshot().agent_id)
    edited = dataclasses.replace(
        on_file,
        max_delivered_concentration_percent=Percent(
            on_file.max_delivered_concentration_percent + 1.0
        ),
    )
    monkeypatch.setattr(uptake_system, "load_agent_parameters", lambda agent_id: edited)
    monkeypatch.setattr(
        "anesthesia_sim.app.controller.load_agent_parameters", lambda agent_id: edited
    )

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    named = (
        f"max_delivered_concentration_percent is "
        f"{on_file.max_delivered_concentration_percent!r} in this run and "
        f"{edited.max_delivered_concentration_percent!r} on the branch"
    )

    assert str(refusal.value).count(named) == 1


def test_a_branch_can_open_at_any_keyframe_the_run_holds() -> None:
    """Every recorded setting change is a branch point, and so is the run's start."""

    trunk = _trunk_with_two_changes()

    for segment in trunk.run_segments:
        branch = trunk.resumed_at(segment.opening.instant_s)

        assert branch.run_segments[0].opening.instant_s == segment.opening.instant_s
        assert branch.run_segments[0].opening.state == segment.opening.state


def test_resumed_at_refuses_an_instant_no_setting_changed_at_and_names_the_other_doors() -> None:
    """The refusal gives the method's scope as its reason, not an arithmetic limit (`PL-54V0`).

    `resumed_at` opens at the run's opening or at a recorded setting change.
    An instant between two of them can still be reproduced: `resumed_at_mark`
    and `resumed_here` both fork there and reproduce the run element-wise.
    Such an instant belongs to another method, so the message says which one.
    It also names the keyframes this run does have, so a caller can pick one.
    The reason the message used to give was that opening there "would restart
    from two propagations where the run took one". That is true only of a
    construction that no fork method uses. A reader who believed it would
    reach for the refused fix of recording a keyframe there.
    """

    trunk = _trunk_with_two_changes()
    between_s = trunk.run_segments[-1].opening.instant_s + 5.0

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe") as refusal:
        trunk.resumed_at(CaseInstant(between_s))

    message = str(refusal.value)
    openings = [segment.opening.instant_s for segment in trunk.run_segments]

    assert str(openings) in message
    assert "resumed_at_mark" in message
    assert "resumed_here" in message
    assert "two propagations" not in message


def test_an_instant_the_run_never_reached_is_refused() -> None:
    """A branch of a run that has not happened would be a prediction drawn as a run."""

    trunk = _trunk_with_two_changes()

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        trunk.resumed_at(CaseInstant(trunk.snapshot().elapsed_s + 600.0))


def test_a_non_finite_fork_instant_cannot_be_built() -> None:
    """This refusal is separate from the keyframe refusal, which would give the wrong reason.

    Since `PL-CN5S`, a non-finite instant is refused when the instant is
    built, so no run is ever asked to branch at one.
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(float("inf"))


@pytest.mark.parametrize("instant_s", [0.0, float("inf")])
def test_a_fork_instant_not_built_as_a_case_instant_is_refused(instant_s: float) -> None:
    """The instant is refused whatever its value, before the keyframes are searched (`PL-CN5S`).

    A bare `0.0` is refused even though the trunk has a keyframe there,
    because nothing has checked it. The refusal says so. It does not say that
    the run has no keyframe there, which would be the wrong reason. `fork_at`
    forwards to this method, so it refuses the same way.
    """

    trunk = _trunk_with_two_changes()

    with pytest.raises(TypeError, match="instant_s of .* was not built as CaseInstant"):
        trunk.resumed_at(instant_s)  # type: ignore[arg-type]


def test_a_failed_frame_refuses_every_fork_until_the_trunk_starts_over() -> None:
    """A trunk whose frame failed offers no fork point and refuses every fork (`PL-T2Q2`).

    The failed-frame record belongs to the run, as a failure does. So a reset
    clears it, and the fresh run offers its opening again. A failure alone
    does not cause a refusal: a trunk whose own step failed keeps its
    keyframes.
    """

    trunk = _trunk_with_two_changes()
    case = BranchedCase(trunk)
    keyframes = case.fork_points_s
    assert len(keyframes) == 3

    trunk.fail("SimulationNumericalError: a step failed")

    assert case.fork_points_s == keyframes
    assert trunk.fork_refusal is None

    trunk.record_failed_frame("RuntimeError: this frame could not be assembled")

    assert case.fork_points_s == ()
    assert case.mark_fork_points == ()
    assert trunk.fork_refusal is not None
    assert "this frame could not be assembled" in trunk.fork_refusal

    with pytest.raises(
        SimulationConfigurationError, match="the dashboard this run is drawn in failed"
    ):
        case.fork_at(keyframes[0])

    trunk.reset()

    assert trunk.fork_refusal is None
    assert case.fork_points_s == (CaseInstant(0.0),)


def test_a_branch_of_a_branch_is_refused_rather_than_silently_flattened() -> None:
    """`PL-TFX5`'s shape: one trunk with N branches, and sub-forks deliberately excluded.

    Sub-forks multiply without bound and give little that re-branching from
    the trunk does not. That is the whole reason. The rule once also rested on
    a branch's keyframes belonging to its own definition. An instant passed to
    this method on a branch then meant something different from the same
    number passed to the trunk. `PL-ZMRT` retired that, because every run's
    instants are now the case's. `SimulationController.resumed_at` states only
    the reason that remains. A later reader removes a guard whose argument has
    stopped being true.
    """

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_at(branch.snapshot().elapsed_s)


def test_forking_leaves_the_trunk_untouched() -> None:
    """The trunk survives the fork, which is what separates branching from truncating."""

    trunk = _trunk_with_two_changes()
    before = trunk.snapshot()
    segments_before = trunk.run_segments

    trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert trunk.snapshot() == before
    assert trunk.run_segments == segments_before


def test_a_branch_starts_paused() -> None:
    """Opening a branch is not starting it: the learner decides when it runs."""

    trunk = _trunk_with_two_changes()
    trunk.start()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert branch.is_running is False


def test_resetting_a_branch_returns_it_to_its_fork_rather_than_to_zero() -> None:
    """A branch begins at the fork, and the case's induction is not a state it has.

    Clearing to an empty system would put the patient at no agent, at a case
    time when the model says they are loaded with agent. That is a plausible
    state that never happened.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)
    at_fork = branch.snapshot()

    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    branch.reset()

    after = branch.snapshot()

    assert after.elapsed_s == fork_s
    assert after.control_timeline == ()
    assert branch.run_segments[0].opening.state == trunk.run_segments[-1].opening.state

    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(after, field) == getattr(at_fork, field)


def test_a_branch_reset_the_core_refuses_leaves_the_branch_exactly_as_it_was() -> None:
    """A branch's reset reads the same record first, so a refused reset leaves the branch as it was.

    `_open_at` takes the branch back to its fork and records the settings in
    force at the fork. Before `PL-M4M0`, it read those settings itself, after
    the state had already been moved back to the fork. So a refusal left the
    branch at the fork under its old definition, with nothing recorded.
    `reset()` now reads the record before anything moves and passes it in.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    before = branch.snapshot()
    segments = branch.run_segments
    _with_stale_tissue_flows(branch, 6.0)

    with pytest.raises(
        SimulationConfigurationError, match="the venous balance returns what the tissues receive"
    ):
        branch.reset()

    after = branch.snapshot()

    assert after.is_running is True
    assert branch.has_failed is False
    assert after.elapsed_s == before.elapsed_s > fork_s
    assert after.control_timeline == before.control_timeline
    assert len(after.control_timeline) == 1
    assert branch.run_segments == segments
    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(after, field) == getattr(before, field)


def test_a_branch_is_the_agent_and_patient_its_parent_was() -> None:
    """`PL-TFX5`: a branch that could change either would be a second case."""

    trunk = SimulationController(agent_id="desflurane", cardiac_output_l_min=CardiacOutput(3.8))
    _run_with_two_changes(trunk)
    trunk.pause()

    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    at_fork = branch.snapshot()

    assert at_fork.agent_id == "desflurane"
    assert at_fork.cardiac_output_l_min == trunk.snapshot().cardiac_output_l_min
    assert at_fork.circuit_volume_l == trunk.snapshot().circuit_volume_l


"""`PL-TFX5`: a case is one trunk and the branches taken from it, kept flat.

`SimulationController.resumed_at` cannot enforce this clause on its own. It
makes one branch and returns it detached. So two calls produce two
controllers that each know the instant they opened at, and neither knows the
other exists. `BranchedCase` makes them one case, and it builds the flat shape
into the structure. The trunk is the only run it will fork, so a sub-fork is
not an operation it ever has to refuse.
"""


def test_a_case_forks_at_every_instant_the_trunk_offers() -> None:
    """`PL-TFX5`'s first clause: any recorded control event is a branch point.

    `fork_points_s` is the run's keyframes: its opening and every setting
    change that the model was actually stepped under. So the test asserts that
    the list agrees with the timeline, as well as that each point forks. A
    list of fork points that quietly left one out would still pass a test that
    only walked the list.
    """

    case = BranchedCase(_trunk_with_two_changes())
    timeline = case.trunk.snapshot().control_timeline

    assert case.fork_points_s == (0.0, *(change.elapsed_s for change in timeline))

    for elapsed_s in case.fork_points_s:
        branch = case.fork_at(elapsed_s)

        assert branch.run_segments[0].opening.instant_s == elapsed_s
        assert branch.snapshot().elapsed_s == elapsed_s

    assert len(case.branches) == len(case.fork_points_s)
    assert case.runs == (case.trunk, *case.branches)


def test_a_case_holds_two_branches_taken_at_one_decision_point() -> None:
    """The comparison the milestone is named for, so a fork point can be used more than once.

    Coasting against holding, from the same instant: two branches at one fork
    point are the normal case, not a duplicate to reject. Once taken, they
    must be managed separately.
    """

    case = BranchedCase(_trunk_with_two_changes())
    fork_s = case.fork_points_s[-1]

    coasting = case.fork_at(fork_s)
    holding = case.fork_at(fork_s)

    assert case.branches == (coasting, holding)
    assert coasting is not holding

    coasting.set_fresh_gas_flow(FreshGasFlow(0.5))
    holding.set_fresh_gas_flow(FreshGasFlow(6.0))

    assert coasting.snapshot().fresh_gas_flow_l_min == 0.5
    assert holding.snapshot().fresh_gas_flow_l_min == 6.0


def test_forking_a_case_repeatedly_leaves_the_trunk_where_it_was() -> None:
    """`PL-TFX5`'s third clause, against the whole of `fork_points_s`.

    The trunk's survival is what separates a comparison from an undo. The test
    checks it after every branch has been advanced and re-dialled, because a
    branch that shared a compartment with its parent would show nothing until
    something moved.
    """

    case = BranchedCase(_trunk_with_two_changes())
    before = case.trunk.snapshot()
    segments_before = case.trunk.run_segments

    for elapsed_s in case.fork_points_s:
        branch = case.fork_at(elapsed_s)
        branch.set_cardiac_output(CardiacOutput(2.5))
        branch.start()
        _advance_for(branch, duration_s=30.0)
        branch.pause()

    assert case.trunk.snapshot() == before
    assert case.trunk.run_segments == segments_before
    assert case.trunk.run_segments[0].opening.instant_s == 0.0
    assert case.trunk.opened_from is None


def test_a_case_cannot_be_rooted_in_a_branch() -> None:
    """`PL-TFX5`'s fourth clause, as an interface that cannot express a sub-fork.

    `resumed_at` refuses a branch of a branch and keeps doing so. That is the
    guard for a caller that holds two controllers. This test covers the other
    half. A case built on a branch would offer `fork_at` over a second
    generation, so the case is refused when it is built, not at the fork.
    """

    trunk = _trunk_with_two_changes()
    branch = BranchedCase(trunk).fork_at(trunk.run_segments[-1].opening.instant_s)

    with pytest.raises(SimulationConfigurationError, match="branches of branches are excluded"):
        BranchedCase(branch)


def test_a_case_refuses_a_fork_at_an_instant_the_trunk_holds_no_keyframe_for() -> None:
    """The refusal passes through the case unchanged rather than being softened by it."""

    case = BranchedCase(_trunk_with_two_changes())
    between_s = (case.fork_points_s[-2] + case.fork_points_s[-1]) / 2.0

    assert between_s not in case.fork_points_s

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        case.fork_at(CaseInstant(between_s))

    assert case.branches == ()


def test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork() -> None:
    """`PL-TFX5`'s last clause, against a patient value that moves during the run.

    Cardiac output is the one patient quantity that a control can change. So
    it is the only one that tells "the branch carries its parent's patient"
    apart from "the branch rebuilds the same reference patient from the same
    data file". A run that never changes it checks the second claim while
    appearing to check the first, because `_setting_at` then falls through to
    the value in force now. So this test changes it mid-run and forks *before*
    the change. The branch must carry the value the case was computed under at
    the fork, which is no longer the trunk's current value.
    """

    trunk = SimulationController(agent_id="isoflurane", cardiac_output_l_min=CardiacOutput(4.2))
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.set_cardiac_output(CardiacOutput(6.5))
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()

    case = BranchedCase(trunk)
    before_s, after_s = case.fork_points_s

    assert trunk.snapshot().cardiac_output_l_min == 6.5

    at_earlier_fork = case.fork_at(before_s).snapshot()
    at_later_fork = case.fork_at(after_s).snapshot()

    assert at_earlier_fork.cardiac_output_l_min == 4.2
    assert at_later_fork.cardiac_output_l_min == 6.5

    for at_fork in (at_earlier_fork, at_later_fork):
        assert at_fork.agent_id == "isoflurane"
        assert at_fork.circuit_volume_l == trunk.snapshot().circuit_volume_l


def test_a_branch_cannot_change_its_agent_out_from_under_the_case() -> None:
    """`PL-TFX5`: a branch that could re-choose its agent is a second case.

    `set_agent` begins a new run, and `_build_state` clears `opened_from` along
    with everything else. Without this refusal, a branch would silently become
    a trunk. `reset()` would stop returning it to its fork, `resumed_at` would
    accept it, and the case it was taken from would go on listing it. The
    trunk is unaffected: changing the case's agent still starts an explicit
    new case, as it always did.
    """

    trunk = _trunk_with_two_changes()
    case = BranchedCase(trunk)
    branch = case.fork_at(case.fork_points_s[-1])

    with pytest.raises(SimulationConfigurationError, match="carries the agent of the case"):
        branch.set_agent("desflurane")

    assert branch.snapshot().agent_id == trunk.snapshot().agent_id
    assert branch.opened_from is not None

    trunk.set_agent("desflurane")

    assert trunk.snapshot().agent_id == "desflurane"


def test_every_recorded_control_event_is_an_instant_the_run_can_be_forked_at() -> None:
    """`PL-TFX5`'s first clause, against the case that used to break it.

    The clause "A run can be forked at any recorded control event" ties two
    records together. They collapse redundant changes by different rules, so
    the clause is true only while those rules agree.
    `RunDefinition.record_change` compares the whole settings against the
    previous stretch, and its result does not depend on order. The control
    timeline compares one entry, and it used to compare only the newest one.

    What separated the two records was two dials nudged and both put back in
    **interleaved** order: F up, C up, F back, C back. Each move's predecessor
    was the other control, so no collapse happened. Four entries remained at
    an instant at which the run never changed, while the definition correctly
    had no keyframe there. The nested order collapsed to nothing. So the
    defect depended on order, and a test that moved two controls once each
    could not see it. A learner meets it while paused, when `advance()` does
    nothing and every control they touch carries the same instant.

    The test asserts the property rather than the repair. Every time stamp the
    reader is shown is an instant at which the run has a keyframe, and
    `resumed_at` accepts each one.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=30.0)

    opening = trunk.snapshot()
    trunk.pause()

    trunk.set_fresh_gas_flow(FreshGasFlow(opening.fresh_gas_flow_l_min + 1.0))
    trunk.set_cardiac_output(CardiacOutput(opening.cardiac_output_l_min + 1.0))
    trunk.set_fresh_gas_flow(opening.fresh_gas_flow_l_min)
    trunk.set_cardiac_output(opening.cardiac_output_l_min)

    timeline = trunk.snapshot().control_timeline
    openings = [segment.opening.instant_s for segment in trunk.run_segments]

    # Nothing the model saw has changed, so neither record shows a change.
    assert [change.elapsed_s for change in timeline] == openings[1:]
    assert openings == [0.0]

    # Now the general property, on a run that does change. Every time stamp a
    # reader is shown is a fork point, which is what the clause promises.
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.set_alveolar_ventilation(AlveolarVentilation(6.0))
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()

    case = BranchedCase(trunk)

    for change in trunk.snapshot().control_timeline:
        assert change.elapsed_s in case.fork_points_s
        assert case.fork_at(change.elapsed_s).run_segments[0].opening.instant_s == (
            change.elapsed_s
        )


# --------------------------------------------------------------- bookmarks
#
# `tests/unit/test_bookmarks.py` covers what a mark rejects. This section
# covers the controller's half. It checks that the collections reach a reader
# through the snapshot. It also checks what happens to them at the three
# points where a run starts over: `reset`, `set_agent` and a fork. Each of
# those three is a decision rather than a consequence, so each has a test
# that says which way it went and why (`PL-LPLD`).


def test_a_fresh_run_is_marked_at_nothing() -> None:
    assert SimulationController().snapshot().bookmarks.is_empty


def test_a_mark_reaches_a_reader_through_the_snapshot() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "intubation"))
    controller.add_mac_target(MacTarget(RecordedQuantity.VESSEL_RICH, MacMultiple(0.8), "wash-in"))

    marks = controller.snapshot().bookmarks

    assert [bookmark.label for bookmark in marks.time_bookmarks] == ["intubation"]
    assert [target.label for target in marks.mac_targets] == ["wash-in"]


def test_the_two_collections_are_added_to_and_removed_from_independently() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0)))
    controller.add_mac_target(MacTarget(RecordedQuantity.FAT, MacMultiple(0.5)))
    controller.remove_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    marks = controller.snapshot().bookmarks

    assert marks.time_bookmarks == ()
    assert len(marks.mac_targets) == 1


def test_a_snapshot_taken_before_a_mark_was_added_does_not_acquire_it() -> None:
    # The snapshot is a read-only view of one instant. A panel that keeps a
    # snapshot from an earlier tick must not come to describe a later run.
    controller = SimulationController()
    before = controller.snapshot()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    assert before.bookmarks.is_empty
    assert not controller.snapshot().bookmarks.is_empty


def test_a_marked_instant_cannot_be_marked_twice_through_the_controller() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "and again"))

    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_resetting_a_run_keeps_its_marks() -> None:
    # A reset is for running the same case again, and it is the same case the
    # learner was asking about. So the marks stay with the settings rather
    # than with the state.
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0)))
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.reset()

    assert controller.snapshot().bookmarks.time_bookmarks == (TimeBookmark(CaseInstant(600.0)),)


def test_changing_agent_keeps_the_marks_although_it_destroys_the_run() -> None:
    # A MAC target is a multiple of whichever agent is running, so 0.8 x MAC
    # stays 0.8 x MAC of the new agent rather than becoming the old agent's
    # absolute concentration under a new divisor. A learner who changes agent
    # wants to see the same multiple reached at a different time.
    controller = SimulationController()
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.8))
    controller.add_mac_target(target)
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_agent("desflurane")

    after = controller.snapshot()

    assert after.agent_id == "desflurane"
    assert after.control_timeline == ()
    assert after.bookmarks.mac_targets == (target,)


def _run_to_halt(
    controller: SimulationController, reading_of: Callable[[SimulationSnapshot], Fraction]
) -> tuple[float, SimulationSnapshot]:
    """Advance one step at a time until a mark halts the run.

    Returns the reading on the step before the halt, in multiples of MAC, and
    the halted snapshot.
    """

    mac_fraction = float(fraction_from_percent(controller.snapshot().agent_mac_percent))
    before = float(reading_of(controller.snapshot())) / mac_fraction
    for _ in range(round(60.0 / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
        snapshot = controller.snapshot()
        if snapshot.bookmark_halt is not None:
            return before, snapshot
        before = float(reading_of(snapshot)) / mac_fraction
    raise AssertionError("no mark halted the run within 60 s")


def _sevoflurane_at_8_percent_and_10_l_min() -> SimulationController:
    controller = SimulationController()
    controller.set_agent("sevoflurane")
    controller.set_fresh_gas_flow(FreshGasFlow(10.0))
    controller.set_delivered_concentration_percent(Percent(8.0))
    return controller


def test_a_circuit_target_halts_within_one_step_of_its_mark_and_can_show_one_count_past() -> None:
    """The simulation halts within one simulation step of the mark, as `docs/MODEL.md` now says.

    A mark is the target value that the learner sets for a reading. The simulation halts when
    the reading crosses it. § "Halting on a marked crossing" used to say that the value
    displayed beside a halt is the value the learner marked (`PL-M8F6`). The specification
    now gives this case as its first example. With 8% sevoflurane at 10 L/min, a 0.10 ×MAC
    circuit target halts showing 0.11 ×MAC, one display count past its mark.
    """

    controller = _sevoflurane_at_8_percent_and_10_l_min()
    mark = MacMultiple(0.10)
    controller.add_mac_target(MacTarget(RecordedQuantity.CIRCUIT, mark))
    controller.start()

    before, halted = _run_to_halt(
        controller, lambda snapshot: snapshot.inspired_partial_pressure_fraction
    )

    # The halting step is the one that crossed: the reading before it was
    # below the mark, and its own reading is at or past it.
    mac_fraction = float(fraction_from_percent(halted.agent_mac_percent))
    assert before < mark <= float(halted.inspired_partial_pressure_fraction) / mac_fraction
    assert format_mac_multiple(
        halted.inspired_partial_pressure_fraction, halted.agent_mac_percent
    ) == (f"0.11{MAC_UNIT_SUFFIX}")


def test_an_alveolar_target_can_halt_two_counts_past_its_mark_when_ventilation_resumes() -> None:
    """In one simulation step, a reading can move more than one display count past its mark.

    A display count is one unit of the last digit shown. This test is the second example in
    `docs/MODEL.md` § "Halting on a marked crossing". After 120 s with no alveolar
    ventilation, the circuit has filled but the alveolar reading is still zero. When
    ventilation is restored to 12 L/min, the alveolar reading rises fast enough that a
    0.10 ×MAC alveolar target halts showing 0.12 ×MAC.
    """

    controller = _sevoflurane_at_8_percent_and_10_l_min()
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.start()
    for _ in range(round(120.0 / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    assert controller.snapshot().alveolar_partial_pressure_fraction == 0.0
    mark = MacMultiple(0.10)
    controller.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, mark))
    controller.set_alveolar_ventilation(AlveolarVentilation(12.0))

    before, halted = _run_to_halt(
        controller, lambda snapshot: snapshot.alveolar_partial_pressure_fraction
    )

    mac_fraction = float(fraction_from_percent(halted.agent_mac_percent))
    assert before < mark <= float(halted.alveolar_partial_pressure_fraction) / mac_fraction
    assert format_mac_multiple(
        halted.alveolar_partial_pressure_fraction, halted.agent_mac_percent
    ) == (f"0.12{MAC_UNIT_SUFFIX}")


def test_a_branch_opens_carrying_the_marks_of_the_case_it_continues() -> None:
    # Marks behave the opposite way to the control timeline, for the opposite
    # reason. The timeline records what was done to a run, and a mark is a
    # question about what is still to come. A comparison is two managements
    # answering one question. A learner made to re-enter the marks could
    # compare two branches at two different heights, with nothing to show it.
    trunk = _trunk_with_two_changes()
    target = MacTarget(RecordedQuantity.MUSCLE, MacMultiple(0.3))
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.0), "the decision point"))
    trunk.add_mac_target(target)

    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    marks = branch.snapshot().bookmarks

    assert marks.time_bookmarks == (TimeBookmark(CaseInstant(45.0), "the decision point"),)
    assert marks.mac_targets == (target,)
    # The timeline still starts empty, because it is the half that does not
    # carry over.
    assert branch.snapshot().control_timeline == ()


def test_marking_a_branch_does_not_mark_the_trunk_it_came_from() -> None:
    # Marks are inherited at the fork and not shared afterwards. The two runs
    # are two managements, and a mark added to one is a question asked of that
    # one.
    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.add_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    assert trunk.snapshot().bookmarks.is_empty
    assert len(branch.snapshot().bookmarks.time_bookmarks) == 1


def test_a_mark_changes_nothing_the_run_computes() -> None:
    # This property is what lets a mark be carried across a fork at all.
    # `PL-B8MK` measured the alternative against it. Recording a keyframe where
    # a run halts changes the trunk's own later results. Keeping a mark in a
    # collection beside the run changes nothing. The comparison is element-wise
    # rather than within a tolerance, because that is the claim.
    #
    # The test still applies unchanged after `PL-CTD7`, and the claim is now
    # stronger. The marked run below is *stopped twice* on the way: at 45 s,
    # and where the alveolar compartment crosses 0.8 ×MAC. It still computes
    # the same trajectory element-wise. A halt costs the run no simulated time
    # and changes no state. It only declines to take the next step until asked.
    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(45.0)))
    marked.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.8)))
    unmarked = SimulationController()

    for controller in (marked, unmarked):
        _run_with_two_changes(controller)
        controller.pause()

    assert marked.snapshot().elapsed_s == unmarked.snapshot().elapsed_s

    for quantity in COMPARTMENT_QUANTITIES:
        position = COMPARTMENT_STATE_INDEX[quantity]
        window = marked.drawn_window(0.0, marked.snapshot().elapsed_s, 50)
        same = unmarked.drawn_window(0.0, unmarked.snapshot().elapsed_s, 50)

        assert [state.values[position] for state in window.states] == [
            state.values[position] for state in same.states
        ]


def _advance_until_halted(controller: SimulationController, limit_s: float) -> None:
    """Step a running controller until a mark halts it, or raise if no mark does.

    A bookmark fork is taken at the halt. A test that silently ran past the
    halt would fork at whatever instant it happened to stop at, and it would
    assert nothing about the case it was meant to test.
    """

    for _ in range(round(limit_s / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

        if controller.snapshot().bookmark_halt is not None:
            return

    raise AssertionError(f"no mark halted this run within {limit_s} s of stepping")


def _trunk_halted_on_a_bookmark() -> SimulationController:
    """A run stopped where a mark lies between two of its keyframes.

    The run has one setting change, at 30 s, so it has keyframes at 0 s and
    30 s and nowhere else. The mark is at 45.3 s, which is neither of them.
    That is the ordinary case, not a contrived one. On the 120 s run that the
    other fork tests use, 3 of the 1 201 instants a halt could land on are
    keyframes.
    """

    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(45.3), "the decision point"))
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_delivered_concentration_percent(Percent(4.0))
    _advance_until_halted(controller, limit_s=60.0)

    return controller


def _the_same_case_never_marked(steps: int) -> SimulationController:
    """`_trunk_halted_on_a_bookmark`'s case without the mark, run the same distance.

    The run is driven by step count rather than by duration. The marked run
    stops partway through a step budget. A second run told to advance "45.3 s"
    would take a different number of steps, and so it would stop at a
    different float.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_delivered_concentration_percent(Percent(4.0))

    for _ in range(steps - controller._state.step_count):
        controller.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    return controller


def test_a_branch_taken_at_a_bookmark_reproduces_its_parent_without_changing_it() -> None:
    """`PL-B8MK`'s deliverable, and both halves of it.

    A design this project refused could satisfy either half alone. Recording a
    keyframe where the run halts makes the branch exact against the trunk it
    forked from. But it also changes that trunk's own later results: 48 of 54
    elements differed from the same case built unmarked, so marking a run
    would change it. Doing nothing at all leaves the trunk untouched but
    refuses the fork. So the two halves are asserted together. The branch
    reproduces its parent element-wise from the fork onwards, *and* the trunk
    is, element for element, the case it would have been if nobody had marked
    it.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_steps = marked._state.step_count

    # The premise: the trunk has no keyframe at the fork instant, so the
    # refused route would have had to record one there.
    assert fork_s not in [segment.opening.instant_s for segment in marked.run_segments]

    branch = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=30.0)
    marked.pause()

    branch.start()
    _advance_for(branch, duration_s=30.0)
    branch.pause()

    unmarked = _the_same_case_never_marked(steps=marked._state.step_count)
    unmarked.pause()

    # The trunk is the case it would have been without the mark: the same
    # keyframes, at the same instants, with the same states. A keyframe
    # recorded where the run halted would show up here as a third opening
    # that the unmarked run does not have.
    assert marked._state.step_count == unmarked._state.step_count
    assert marked.snapshot().elapsed_s == unmarked.snapshot().elapsed_s
    assert [segment.opening.instant_s for segment in marked.run_segments] == [
        segment.opening.instant_s for segment in unmarked.run_segments
    ]
    assert [segment.opening.state for segment in marked.run_segments] == [
        segment.opening.state for segment in unmarked.run_segments
    ]

    for steps in range(0, marked._state.step_count + 1):
        case_s = steps * MAXIMUM_SIMULATION_STEP_S

        assert marked._run_definition.state_at(case_s) == unmarked._run_definition.state_at(
            case_s
        ), f"marking the run moved what it says at {case_s} s"

    # And the branch reproduces the parent it forked from, element for element,
    # at every instant the two share.
    for steps_past_fork in range(0, 301):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S

        assert branch._run_definition.state_at(case_s) == marked._run_definition.state_at(case_s), (
            f"the branch and its parent differ at {case_s} s"
        )


def test_a_bookmark_fork_opens_its_definition_at_the_keyframe_before_it() -> None:
    """The route this project chose, stated as the structure it produces.

    The branch's clock and live system are at the bookmark. Its run definition
    opens at the keyframe *at or before* that instant, with that keyframe's
    own state. Every instant after the fork is then one propagation from the
    same keyframe that the trunk propagates from. `docs/MODEL.md` § "What this
    requires of a branch" relaxes the second of its two conditions to exactly
    that.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s

    branch = marked.resumed_here()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch.opened_from is not None
    assert branch.opened_from.fork.instant_s == fork_s

    # The definition opens earlier, at the trunk's own keyframe rather than at
    # the fork, and nothing was recorded on the trunk to make one there.
    assert branch.run_segments[0].opening.instant_s == 30.0
    assert branch.run_segments[0].opening.instant_s < fork_s
    assert branch.run_segments[0].opening.state == marked.run_segments[-1].opening.state
    assert [segment.opening.instant_s for segment in marked.run_segments] == [0.0, 30.0]


def test_a_branch_taken_at_a_bookmark_is_not_drawn_before_its_fork() -> None:
    """The window is clipped at the fork, not at the definition's opening.

    The definition can return values for the stretch between the keyframe it
    opens at and the fork, because that stretch belongs to the parent. The
    branch did not live through it. Drawing it would show the trunk's
    trajectory under the branch's identity. Those are the right numbers in the
    wrong patient context, and `CLAUDE.md`'s safety-critical standard counts
    that as a failure in its own right.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    # An axis that ends inside the interval that the definition covers, and
    # that the branch never lived through, draws nothing at all.
    assert 30.0 < fork_s - 5.0 < fork_s
    window = branch.drawn_window(0.0, fork_s - 5.0, 150)

    assert window.times_s == ()
    assert window.states == ()

    # An axis reaching the fork draws from the fork, not from the keyframe.
    spanning = branch.drawn_window(0.0, fork_s, 150)

    assert spanning.times_s == (fork_s,)

    # On the same axis, the trunk draws the stretch that the branch does not.
    # The two differ because the branch did not exist yet.
    assert marked.drawn_window(0.0, fork_s - 5.0, 150).times_s != ()


WORST_SHARED_COLUMN_DIVERGENCE = 1e-13
"""Bound the difference between the trunk's and the branch's drawn values at a shared column.

The trunk is the parent run, and the branch is the run forked from one of its bookmarks. A
column is one of the sampled points that the plot draws.

The divergence was measured at or below 2.8e-15 on the case below. The bound is about 36 times
that, roughly one and a half orders of magnitude. That margin keeps an ordinary floating-point
wobble from failing the suite. The bound is also nine orders of magnitude below 1e-4, the
smallest difference that the display resolves according to `docs/MODEL.md` § "Displayed
precision". That gap is the point of the measurement: the two runs differ by far less than the
display can show.
"""


def test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share() -> None:
    """`PL-Z3W6`: a branch agrees with its parent at every sampled point a learner sees.

    "Every sampled point" has a second meaning, and it is the one the release is
    for: the columns that the chart draws. A learner does not compare two runs at
    whole steps of the solver. They compare them at the vertices of two overlaid
    traces. A divergence before the fork would make it impossible to attribute a
    difference after the fork to the one setting that was changed.

    Three things are asserted, and they are three different claims:

    - **The branch adds exactly one column that the trunk does not draw, and that
      column is the fork.** A fork at a control event adds none, because a control
      event is a column on every run that has one. A bookmark's instant is not a
      column on the trunk, so the branch draws it as the left end of its own clipped
      range. That vertex marks where the two stop being one run.
    - **Evaluated by the canonical rule, they agree element for element at every
      column they share.** This is the guarantee, checked at the drawn instants
      rather than at the solver's steps: 0 of 2 259 elements differ over 251 shared
      columns.
    - **The drawn values at those columns do not agree exactly.** 2 000 of the same
      2 259 elements differ, the worst by 5.3e-16. This was measured on 2026-10-26,
      after `PL-T5NJ` put the columns on whole hundredths of a second. Before that,
      1 909 of 2 160 elements over 240 columns differed, the worst by 2.7e-15. The
      values differ because `evaluate_anchored` chains one propagator across
      consecutive columns and breaks the chain at a bound. So
      the trunk chains through the fork, while the branch restarts there. Without
      this third claim, a display path that had quietly become the canonical one
      would satisfy the first two. `docs/MODEL.md` § "The canonical evaluation
      rule" would then be enforcing a separation that no longer existed.

    The third claim is why the second is worth asserting at all. A reader who
    subtracts one drawn trace from the other sees a few units in the last place
    here, where two identical runs should show zero. The canonical agreement is
    what shows that the case did not disagree with itself.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=30.0)
    marked.pause()

    branch.start()
    _advance_for(branch, duration_s=30.0)
    branch.pause()

    span_s = marked.snapshot().elapsed_s
    trunk_window = marked.drawn_window(0.0, span_s, 601)
    branch_window = branch.drawn_window(0.0, span_s, 601)
    shared = sorted(set(trunk_window.times_s) & set(branch_window.times_s))

    assert tuple(sorted(set(branch_window.times_s) - set(trunk_window.times_s))) == (fork_s,)
    assert len(shared) == 251

    trunk_drawn = dict(zip(trunk_window.times_s, trunk_window.states, strict=True))
    branch_drawn = dict(zip(branch_window.times_s, branch_window.states, strict=True))
    elements = drawn_differing = 0

    for elapsed_s in shared:
        assert branch._run_definition.state_at(elapsed_s) == marked._run_definition.state_at(
            elapsed_s
        ), f"the branch and its parent differ at the column drawn at {elapsed_s} s"

        for entry in range(STATE_SIZE):
            elements += 1
            trunk_value = trunk_drawn[elapsed_s].values[entry]
            branch_value = branch_drawn[elapsed_s].values[entry]
            drawn_differing += trunk_value != branch_value

            assert abs(trunk_value - branch_value) < WORST_SHARED_COLUMN_DIVERGENCE, (
                f"the two drawn columns at {elapsed_s} s diverged further than measured"
            )

    assert elements == 251 * STATE_SIZE
    assert drawn_differing > 0, (
        "the drawn values at every shared column agreed bit for bit, so the display path "
        "has become the canonical one and the separation docs/MODEL.md enforces no longer "
        "costs or buys anything"
    )


def test_a_paused_trunk_branches_where_it_stands() -> None:
    """`PL-Y2SL`'s deliverable: paused anywhere, the learner can branch right there.

    The trunk is paused at 120 s, which is neither a keyframe nor a mark.
    Before this item, no fork method reached such an instant, so a learner had
    to mark it first. The branch uses the bookmark fork's construction, with
    the clock giving the fork instant. The branch starts at the clock, and its
    definition opens at the keyframe where the trunk's current stretch opens.
    It reproduces the trunk element-wise from the fork on, and the trunk stays
    the case it was. The method takes no instant, so there is no instant to
    get wrong.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.snapshot().elapsed_s
    fork_steps = trunk._state.step_count
    keyframes = [
        (segment.opening.instant_s, segment.opening.state) for segment in trunk.run_segments
    ]

    # The premise: nothing is recorded where the trunk is paused.
    assert fork_s not in [instant_s for instant_s, _ in keyframes]
    assert trunk.snapshot().bookmark_halt is None
    assert trunk.here_fork_point == HereForkPoint(fork_s, stopped_on_mark=False)

    branch = trunk.resumed_here()

    assert branch.began_at_s == branch.snapshot().elapsed_s == fork_s
    assert branch._state.step_count == fork_steps
    assert branch.opened_from is not None
    assert branch.opened_from.fork.state == trunk._run_definition.state_at(fork_s)
    assert branch.opened_from.crossing is None
    assert branch.run_segments[0].opening.instant_s == trunk.run_segments[-1].opening.instant_s
    assert [
        (segment.opening.instant_s, segment.opening.state) for segment in trunk.run_segments
    ] == keyframes

    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()

    branch.start()
    _advance_for(branch, duration_s=30.0)
    branch.pause()

    for steps_past_fork in range(0, 301):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S

        assert branch._run_definition.state_at(case_s) == trunk._run_definition.state_at(case_s), (
            f"the branch and the trunk it was paused at differ at {case_s} s"
        )


def test_resuming_past_a_bookmark_turns_its_fork_into_the_paused_point() -> None:
    """A step uses up the halt, nothing is offered while the run goes, and a pause offers again.

    A running run's position moves with each step, so an instant read from it
    is gone before it can be taken. The fork method refuses it rather than
    fork a step or a tick later than the label said. Once paused again, the
    run offers the place where it then is, which is no longer on the mark.
    """

    marked = _trunk_halted_on_a_bookmark()
    halted_s = marked.snapshot().elapsed_s

    assert marked.here_fork_point == HereForkPoint(halted_s, stopped_on_mark=True)

    marked.start()
    marked.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert marked.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="is going"):
        marked.resumed_here()

    marked.pause()
    paused_s = marked.snapshot().elapsed_s

    assert paused_s > halted_s
    assert marked.here_fork_point == HereForkPoint(paused_s, stopped_on_mark=False)
    assert marked.resumed_here().began_at_s == paused_s


def test_a_failed_run_offers_no_place_to_branch_where_it_stands() -> None:
    """A failure is not a pause, so a failed run's position is neither offered nor taken.

    `RunStatus.failure_reason` keeps a failure from being presented as a
    pause. A branch there would resume a run that `fail` says is not resumed.
    The run can still be branched at the keyframes it passed before the
    failure, as the refusal says.
    """

    trunk = _trunk_with_two_changes()
    trunk.fail("a step raised")

    assert trunk.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="not a pause") as refusal:
        trunk.resumed_here()

    assert "a step raised" in str(refusal.value)
    assert "resumed_at" in str(refusal.value)
    assert trunk.resumed_at(trunk.run_segments[-1].opening.instant_s).began_at_s == (
        trunk.run_segments[-1].opening.instant_s
    )


def test_a_run_at_its_opening_offers_no_place_to_branch_where_it_stands() -> None:
    """Nothing is recorded at the opening, and `resumed_at` already opens a branch there."""

    trunk = SimulationController()

    assert trunk.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="opening"):
        trunk.resumed_here()

    assert trunk.resumed_at(CaseInstant(0.0)).began_at_s == 0.0


def test_a_mark_added_inside_the_halting_step_reads_passed_on_the_branch() -> None:
    """A mark the halting step crossed shows as passed on the branch, however late (`PL-2N43`).

    A 45.35 s mark halts the run at the end of the step that reaches it, at
    45.4 s. A 45.33 s mark added while the run is stopped there lies inside
    that same step. The halt's record names only what was marked when the run
    stopped. So a branch started from that record opened just past a mark it
    had no record of. It showed the mark as before the branch, while the trunk
    and `resumed_at_mark` showed it as passed. When the step's crossing is
    computed from the current marks, it names both.
    """

    trunk = SimulationController()
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.35), "the decision point"))
    trunk.start()
    _advance_until_halted(trunk, limit_s=60.0)
    added = TimeBookmark(CaseInstant(45.33), "added while standing")
    trunk.add_time_bookmark(added)

    assert trunk.snapshot().elapsed_s == 454 * MAXIMUM_SIMULATION_STEP_S

    branch = trunk.resumed_here()

    assert branch.snapshot().bookmark_standings.of_time_bookmark(added) is MarkStanding.PASSED
    assert trunk.snapshot().bookmark_standings.of_time_bookmark(added) is MarkStanding.PASSED
    assert trunk.resumed_at_mark(added).opened_from == branch.opened_from


def test_an_instant_between_keyframes_is_refused_even_where_the_run_stands_on_it() -> None:
    """`resumed_at` keeps its keyframe rule unchanged, halt or no halt.

    `PL-B8MK` added a second fork method rather than widening this one, and
    `PL-Z3W6` did not widen it either. Every instant at which a run can be
    halted is already reachable through `resumed_here`. A marked instant that
    the run has gone past is reachable too, through `resumed_at_mark`
    (`PL-W4XQ`). That is a third method, and it leaves this method's scope
    unchanged.
    """

    marked = _trunk_halted_on_a_bookmark()

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        marked.resumed_at(marked.snapshot().elapsed_s)


def test_resetting_a_branch_taken_at_a_bookmark_returns_it_to_the_bookmark() -> None:
    """A branch's beginning is its fork, and a bookmark fork is no exception."""

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._run_definition.state_at(fork_s)
    branch = marked.resumed_here()

    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch._run_definition.state_at(fork_s) == fork_state


def test_a_branch_reset_under_new_settings_is_drawn_from_where_it_stands() -> None:
    """`reset()` preserves settings, and the definition has to follow.

    A branch reset after its learner has dialled something new is at the fork
    state under the new settings. A definition still opening at the parent's
    earlier keyframe would propagate that keyframe forward under settings the
    parent never used. It would draw the branch from a state the branch is not
    in. The readouts would then say one thing and the trace another, about one
    run.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._run_definition.state_at(fork_s)
    branch = marked.resumed_here()

    branch.set_delivered_concentration_percent(Percent(6.0))
    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch._run_definition.state_at(fork_s) == fork_state


def test_a_branch_of_a_bookmark_fork_is_refused_rather_than_silently_flattened() -> None:
    """The flat shape applies to every branch, whichever fork method made it."""

    marked = _trunk_halted_on_a_bookmark()
    branch = marked.resumed_here()
    branch.add_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_at(branch.run_segments[0].opening.instant_s)


def test_a_case_forks_at_the_bookmark_its_trunk_is_standing_on() -> None:
    """The case-level fork method keeps the branch rather than returning it detached."""

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    case = BranchedCase(marked)

    branch = case.fork_here()

    assert case.branches == (branch,)
    assert case.runs == (marked, branch)
    assert branch.opened_from is not None
    assert branch.opened_from.fork.instant_s == fork_s
    # The trunk stays where it was, still stopped at its halt.
    assert marked.snapshot().elapsed_s == fork_s
    assert marked.snapshot().bookmark_halt is not None


def test_a_mark_between_a_bookmark_branch_s_definition_and_its_fork_is_unreachable() -> None:
    """The standings are taken from where the branch *began*, not where its definition opens.

    A bookmark branch's definition opens at the keyframe at or before the
    fork, and the stretch between them belongs to the parent. A mark in that
    stretch can never be reached going forward, so the row must say so. Until
    `PL-B8MK`, the definition's own opening was the same number as the fork
    for every branch. Using it here instead would tell a learner to wait for
    something that no step can reach.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(40.0), "passed on the way"))
    marked.add_time_bookmark(TimeBookmark(CaseInstant(45.3), "the decision point"))
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)

    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    # The premise: the definition reaches back past the mark, and the branch
    # does not.
    assert branch.run_segments[0].opening.instant_s < 40.0 < fork_s
    assert branch.began_at_s == fork_s

    standings = branch.snapshot().bookmark_standings

    assert standings.of_time_bookmark(TimeBookmark(CaseInstant(40.0), "passed on the way")) is (
        MarkStanding.BEFORE_THIS_BRANCH
    )


# ------------------------------------------- a mark the run is at or behind
#
# These are `PL-3K9B`'s seven measured cases. They run end to end rather than
# being asserted against `BookmarkSet.standings` directly, because the defect
# was never in that function. It was in what the controller passed to it.
# Each case makes the same claim. `STILL_RUNNING` says the run can still reach
# the mark, and in none of these cases could any step ever make that true.


def test_a_branch_forked_at_a_mark_on_the_step_grid_reads_it_as_passed() -> None:
    """Case A, and the common one: every whole second is on the 0.1 s grid.

    The branch's first `before_s` is the fork itself, and `before_s` only
    increases. Because `crossed_between` uses a strict `<`, no step the branch
    ever takes can cross this instant. The test steps well past it to show
    that.
    """

    marked = SimulationController()
    on_the_grid = TimeBookmark(CaseInstant(30.0), "induction complete")
    marked.add_time_bookmark(on_the_grid)
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)

    assert marked.snapshot().elapsed_s == 30.0

    branch = marked.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=60.0)

    assert branch.snapshot().bookmark_standings.of_time_bookmark(on_the_grid) is (
        MarkStanding.PASSED
    )


def test_one_act_off_the_step_grid_reads_the_same_as_on_it() -> None:
    """Case B, and the whole of what it is about.

    A halt lands on the step that crossed the mark. So an instant that is not
    a multiple of the step in binary is halted a few parts in 1e16 past
    itself, and both rows display as `45.3s`. Two branches taken by the
    identical act must not give a reader two different accounts of it because
    of that.
    """

    on_the_grid = TimeBookmark(CaseInstant(30.0))
    off_the_grid = TimeBookmark(CaseInstant(45.3))
    standings = []

    for mark in (on_the_grid, off_the_grid):
        marked = SimulationController()
        marked.add_time_bookmark(mark)
        marked.start()
        _advance_until_halted(marked, limit_s=60.0)
        branch = marked.resumed_here()
        standings.append(branch.snapshot().bookmark_standings.of_time_bookmark(mark))

    assert marked.snapshot().elapsed_s > 45.3, "the premise: the halt lands past the mark"
    assert standings == [MarkStanding.PASSED, MarkStanding.PASSED]


def test_a_trunk_and_its_branch_agree_about_the_height_that_separated_them() -> None:
    """Case C, the worst of the seven by consequence.

    The branch's whole identity is *the management taken at this height*.
    Suppose a panel showed the trunk's row as reached and the branch's row as
    still running. The two runs would then disagree about the one instant that
    they share by construction. A target has no clock time to compare against,
    so this is the case that the seeded crossing is carried for.
    """

    marked = SimulationController()
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.4), "the decision point")
    marked.add_mac_target(target)
    marked.start()
    _advance_until_halted(marked, limit_s=400.0)

    # A height stops the run as an instant does, and the offered fork point
    # says so in the same way.
    assert marked.here_fork_point == HereForkPoint(
        marked.snapshot().elapsed_s, stopped_on_mark=True
    )

    branch = marked.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=300.0)

    assert marked.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED
    assert branch.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_mark_added_behind_a_running_trunk_is_not_called_still_reachable() -> None:
    """Case D, with no branch in it at all.

    A learner marks an instant the case has just run past when something
    interesting has already happened, and nothing refuses that. The instant
    can never enter the halt set, because the clock is already past it. So the
    halt set cannot decide the mark's standing.
    """

    run = SimulationController()
    run.start()
    _advance_for(run, duration_s=60.0)

    behind_the_clock = TimeBookmark(CaseInstant(30.0), "when the pressure dropped")
    run.add_time_bookmark(behind_the_clock)

    assert run.snapshot().bookmark_standings.of_time_bookmark(behind_the_clock) is (
        MarkStanding.PASSED
    )

    _advance_for(run, duration_s=120.0)

    assert run.snapshot().bookmark_standings.of_time_bookmark(behind_the_clock) is (
        MarkStanding.PASSED
    )


def test_a_branch_taken_at_a_control_event_agrees_with_its_trunk_about_a_mark_there() -> None:
    """Case E, at the fork method that predates bookmark forks entirely.

    The trunk halted on the mark, and a setting was then changed there, so the
    halt is a keyframe too. Like `resumed_here`, `resumed_at` asks the step
    that ends at the keyframe what it crossed. So the branch opens at the
    halt's crossing rather than at no crossing (`PL-1ZQ4`, case 3).
    """

    marked = SimulationController()
    at_the_keyframe = TimeBookmark(CaseInstant(30.0), "the decision point")
    marked.add_time_bookmark(at_the_keyframe)
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)
    marked.set_fresh_gas_flow(FreshGasFlow(3.0))

    branch = marked.resumed_at(CaseInstant(30.0))

    assert branch.opened_from is not None
    assert branch.opened_from.crossing == BookmarkCrossing(CaseInstant(30.0), (at_the_keyframe,))
    assert branch.opened_from == marked.resumed_here().opened_from
    assert marked.snapshot().bookmark_standings.of_time_bookmark(at_the_keyframe) is (
        MarkStanding.PASSED
    )
    assert branch.snapshot().bookmark_standings.of_time_bookmark(at_the_keyframe) is (
        MarkStanding.PASSED
    )


def test_a_mark_removed_and_re_added_at_a_branch_s_fork_instant_still_reads_passed() -> None:
    """Case F: `_forget_unmarked` drops the run's record of the mark, and the clock still decides.

    Removing a mark clears the run's record of it, which is right, because the
    row is gone. An equal mark added afterwards is a new question about the
    same instant, and the run's clock is still at that instant.
    """

    marked = SimulationController()
    at_the_fork = TimeBookmark(CaseInstant(30.0))
    marked.add_time_bookmark(at_the_fork)
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)

    branch = marked.resumed_here()
    branch.remove_time_bookmark(at_the_fork)
    re_added = TimeBookmark(CaseInstant(30.0), "asked again")
    branch.add_time_bookmark(re_added)

    assert branch.snapshot().bookmark_standings.of_time_bookmark(re_added) is MarkStanding.PASSED


def test_resetting_a_branch_leaves_it_standing_on_the_crossing_it_opened_at() -> None:
    """Case G: the crossing a branch opened at must survive a reset, or the defect returns.

    A branch's reset returns it to its fork, which is the crossing it opens
    at. So the halt it is stopped at, and what it has crossed, are part of
    where it is, not of what an earlier run did. `_open_at` is the path for
    both a reset and a fork, which is why the two end in identical states.
    """

    marked = SimulationController()
    at_the_fork = TimeBookmark(CaseInstant(30.0))
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.15))
    marked.add_time_bookmark(at_the_fork)
    marked.add_mac_target(target)
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)

    branch = marked.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=30.0)
    branch.reset()
    after = branch.snapshot()

    assert after.elapsed_s == branch.began_at_s
    assert after.bookmark_halt is not None
    assert after.bookmark_standings.of_time_bookmark(at_the_fork) is MarkStanding.PASSED


def test_a_mark_unmarked_on_a_branch_does_not_come_back_with_its_reset() -> None:
    """The crossing a branch is stopped at is filtered by what is marked *now*, not by what was.

    A halt that names a row the panel no longer draws is the stale state that
    `_forget_unmarked` exists to prevent. A reset that starts again from the
    fork is the one place where that state could have come back.
    """

    marked = SimulationController()
    at_the_fork = TimeBookmark(CaseInstant(30.0))
    marked.add_time_bookmark(at_the_fork)
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)

    branch = marked.resumed_here()
    branch.remove_time_bookmark(at_the_fork)
    branch.reset()

    assert branch.snapshot().bookmark_halt is None


def test_a_control_moved_before_a_bookmark_branch_steps_opens_a_segment_at_the_fork() -> None:
    """The bookmark analogue of reopening a branch's first segment in place.

    A branch forked at a control event opens its definition at the fork. So a
    dial turned before it steps rewrites that one segment, and the branch
    still has one segment. A bookmark branch has already reached past its
    definition's opening. So the change opens a second segment at the fork
    instead, carrying the fork's own state. That keeps the branch from
    propagating its parent's keyframe forward under settings the parent never
    used. The branch's two records still agree: the control timeline's time
    stamps are exactly the segment openings after the first.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._run_definition.state_at(fork_s)
    branch = marked.resumed_here()

    branch.set_alveolar_ventilation(AlveolarVentilation(6.0))

    assert [segment.opening.instant_s for segment in branch.run_segments] == [30.0, fork_s]
    assert branch.run_segments[1].opening.state == fork_state
    assert [change.elapsed_s for change in branch.snapshot().control_timeline] == [
        segment.opening.instant_s for segment in branch.run_segments
    ][1:]
    # And it is still drawn from the fork rather than from the earlier keyframe.
    assert branch.drawn_window(0.0, fork_s, 150).times_s == (fork_s,)


def test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork() -> None:
    """`PL-2R2C`'s comparison property, and the one instant a bookmark fork adds to it.

    A branch is drawn on the trunk's own columns so the two traces can be read
    against each other. A fork at a control event adds nothing, because a
    control event is already a drawn instant on both. A bookmark's instant is
    not, so the branch draws its own first point there and the trunk does not.
    That is one vertex, at the instant the two runs stop being the same run,
    with the value both runs have there. The test pins this rather than
    leaving it implicit, so a later change that adds more such columns fails
    here rather than coming as a surprise.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=30.0)
    branch.start()
    _advance_for(branch, duration_s=30.0)

    trunk_columns = set(marked.drawn_window(0.0, 120.0, 150).times_s)
    branch_columns = set(branch.drawn_window(0.0, 120.0, 150).times_s)

    assert branch_columns - trunk_columns == {fork_s}


def test_a_case_refuses_a_fork_where_its_trunk_stands_while_the_trunk_is_going() -> None:
    """The refusal passes through `BranchedCase` as the keyframe refusal does, and the offer too."""

    trunk = _trunk_with_two_changes()
    case = BranchedCase(trunk)

    assert case.here_fork_point == HereForkPoint(trunk.snapshot().elapsed_s, stopped_on_mark=False)

    trunk.start()

    assert case.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="is going"):
        case.fork_here()

    assert case.branches == ()


def test_a_bookmark_halt_is_not_one_of_the_fork_points_the_case_offers() -> None:
    """The two fork methods stay separate, which keeps the list of fork points stable.

    `fork_points_s` is the trunk's keyframes, and a halt records none. So the
    list does not change its members as the run halts and resumes. A caller
    holding an instant from the list cannot ask for a fork at a mark that the
    run has since stepped past.
    """

    marked = _trunk_halted_on_a_bookmark()
    case = BranchedCase(marked)
    fork_s = marked.snapshot().elapsed_s

    assert case.fork_points_s == (0.0, 30.0)
    assert fork_s not in case.fork_points_s

    # The halt can still be forked, by the other fork method.
    assert case.fork_here().began_at_s == fork_s


def test_two_branches_may_be_taken_at_one_bookmark() -> None:
    """The comparison the milestone is named for: one decision point, two managements.

    A learner marks the instant they want to decide at, the run stops there,
    and both managements are taken from that one state. Nothing about a
    bookmark fork makes it unique, exactly as nothing about a control-event
    fork does.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    case = BranchedCase(marked)

    first = case.fork_here()
    second = case.fork_here()

    assert first is not second
    assert case.branches == (first, second)
    assert first.began_at_s == second.began_at_s == fork_s
    assert first.run_segments[0].opening.state == second.run_segments[0].opening.state
    # The trunk is still stopped at its halt. It was read twice and written
    # neither time.
    assert marked.snapshot().elapsed_s == fork_s
    assert marked.snapshot().bookmark_halt is not None


def test_a_branch_standing_on_its_own_halt_cannot_be_forked_either() -> None:
    """The flat shape still applies to the newer fork method, with the same message."""

    marked = _trunk_halted_on_a_bookmark()
    branch = marked.resumed_here()
    branch.add_time_bookmark(TimeBookmark(CaseInstant(branch.began_at_s + 5.0)))
    branch.start()
    _advance_until_halted(branch, limit_s=30.0)

    assert branch.snapshot().bookmark_halt is not None

    assert branch.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_here()


def test_a_setting_changed_while_halted_makes_the_bookmark_fork_a_keyframe_fork() -> None:
    """Where the two fork methods meet, and the arithmetic does not notice.

    A halt is an ordinary pause, and the setters apply unconditionally. So a
    learner may stop on a mark and dial something before branching. That
    opens a segment at the halt instant, which makes the fork a keyframe after
    all. The definition opens *at* the fork, and the two options that
    `_open_at` chooses between are the same keyframe. The test pins this
    because it is the one path where a bookmark fork and a control-event fork
    are the same fork. A later change that treated the halt as a special case
    would have to keep them the same.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(45.3), "the decision point"))
    marked.start()
    _advance_until_halted(marked, limit_s=60.0)

    fork_s = marked.snapshot().elapsed_s
    marked.set_delivered_concentration_percent(Percent(4.0))

    assert [segment.opening.instant_s for segment in marked.run_segments] == [0.0, fork_s]
    assert marked.snapshot().bookmark_halt is not None

    branch = marked.resumed_here()

    assert branch.run_segments[0].opening.instant_s == branch.began_at_s == fork_s
    assert branch.run_segments[0].opening.state == marked._run_definition.state_at(fork_s)

    marked.start()
    _advance_for(marked, duration_s=30.0)
    branch.start()
    _advance_for(branch, duration_s=30.0)

    fork_steps = round(fork_s / MAXIMUM_SIMULATION_STEP_S)

    for steps_past_fork in range(0, 301):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S

        assert branch._run_definition.state_at(case_s) == marked._run_definition.state_at(case_s)


def test_two_reversible_acts_in_either_order_leave_one_branch() -> None:
    """Where a branch's definition opens cannot depend on the order of a dial and a reset.

    "Dial, dial back, reset" and "dial, reset, dial back" end at one branch:
    the same settings, the same live state, the same snapshot. Suppose the
    reset decided where the definition opens from the settings in place at
    that moment. The second sequence would then open at the fork rather than
    at the parent's keyframe. It would restart from two propagations where the
    parent took one, and quietly stop reproducing the parent in 40 of 45
    elements, with nothing on screen to show it. Instead, `_open_at` records
    the dialled settings as a change at the fork, and `record_change`'s own
    collapse rule notices the dial-back.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    original = marked.snapshot().cardiac_output_l_min

    untouched = marked.resumed_here()
    dialled_back_first = marked.resumed_here()
    reset_first = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=60.0)
    marked.pause()

    dialled_back_first.set_cardiac_output(CardiacOutput(4.0))
    dialled_back_first.set_cardiac_output(CardiacOutput(original))
    dialled_back_first.reset()

    reset_first.set_cardiac_output(CardiacOutput(4.0))
    reset_first.reset()
    reset_first.set_cardiac_output(CardiacOutput(original))

    for branch in (untouched, dialled_back_first, reset_first):
        assert branch.snapshot().cardiac_output_l_min == original
        assert branch.run_segments[0].opening.instant_s == 30.0
        assert len(branch.run_segments) == 1

        branch.start()
        _advance_for(branch, duration_s=60.0)
        branch.pause()

    fork_steps = round(fork_s / MAXIMUM_SIMULATION_STEP_S)

    for steps_past_fork in range(0, 601):
        case_s = (fork_steps + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S
        expected = marked._run_definition.state_at(case_s)

        for name, branch in (
            ("untouched", untouched),
            ("dialled back before the reset", dialled_back_first),
            ("dialled back after the reset", reset_first),
        ):
            assert branch._run_definition.state_at(case_s) == expected, (
                f"the branch {name} differs from its parent at {case_s} s"
            )


def test_a_branch_reset_under_new_settings_records_them_at_its_fork() -> None:
    """Check the structure that the reset leaves, which is why the order does not matter.

    The parent's stretch, with its keyframe and its settings, stays the
    parent's. What the learner has dialled is a change the branch made at its
    own beginning. The keyframe that opens with that change is the fork's own
    state, so the trace starts where the readouts say the branch is.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._run_definition.state_at(fork_s)
    branch = marked.resumed_here()

    branch.set_cardiac_output(CardiacOutput(4.0))
    branch.reset()

    assert [segment.opening.instant_s for segment in branch.run_segments] == [30.0, fork_s]
    assert branch.run_segments[0].settings == marked.run_segments[-1].settings
    assert branch.run_segments[1].opening.state == fork_state
    assert branch._run_definition.state_at(fork_s) == fork_state
    assert branch.drawn_window(0.0, fork_s, 150).times_s == (fork_s,)


# --- A mark the run has passed, returned to (PL-W4XQ) -------------------------
#
# This is the act the owner described a time bookmark for: paused at 3 h, mark
# 1 h and go back to it. Neither of the other fork methods reaches it.
# `resumed_at` opens only at a keyframe, and `resumed_here` only where the run
# is stopped. So `resumed_at_mark` is a third method, built from the halt
# fork's construction. The cases scale the owner's hours down to seconds.
# Nothing in the fork depends on the scale, and the suite pays for every step
# it takes.


def _trunk_paused_past_a_change(past_s: float = 180.0) -> SimulationController:
    """The item's case at a minute's scale: a setting change at 30 s, then on to `past_s`.

    The run has keyframes at 0 s and 30 s and nowhere else. So the trunk has
    no keyframe at an instant past 30 s that a learner marks, and no step
    crossed that instant while it was marked. Both earlier fork methods refuse
    that case.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_fresh_gas_flow(FreshGasFlow(1.0))
    _advance_for(controller, duration_s=past_s - 30.0)
    controller.pause()

    return controller


def test_a_mark_set_behind_the_clock_can_be_returned_to() -> None:
    """`PL-W4XQ`'s deliverable: an instant marked after the run passed it, and returned to.

    When the item was filed, both fork methods refused it. The trunk has no
    keyframe there, and no step ever crossed a mark set after the clock had
    gone by. The branch opens where a halt would have stopped the run, from
    the trunk's canonical state there. It reproduces the trunk element-wise
    from that instant on, and it leaves the trunk exactly the case it was.
    """

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(60.0), "what if")
    trunk.add_time_bookmark(mark)
    keyframes = [
        (segment.opening.instant_s, segment.opening.state) for segment in trunk.run_segments
    ]

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        trunk.resumed_at(CaseInstant(60.0))

    # The paused trunk's own position is a separate fork point, and it is not the mark.
    here = trunk.here_fork_point

    assert here is not None
    assert here.fork_s == trunk.snapshot().elapsed_s != 60.0

    branch = trunk.resumed_at_mark(mark)

    assert branch.began_at_s == branch.snapshot().elapsed_s == 60.0
    assert branch.opened_from is not None
    assert branch.opened_from.fork.state == trunk._run_definition.state_at(CaseInstant(60.0))
    assert branch.snapshot().bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED
    # The branch's definition opens at the trunk's own keyframe before the mark,
    # and nothing was recorded on the trunk to make one where it was marked.
    assert branch.run_segments[0].opening.instant_s == 30.0
    assert [
        (segment.opening.instant_s, segment.opening.state) for segment in trunk.run_segments
    ] == keyframes
    assert trunk.snapshot().elapsed_s == 180.0

    branch.start()
    _advance_for(branch, duration_s=60.0)
    branch.pause()

    for steps_past_fork in range(0, 601):
        case_s = (600 + steps_past_fork) * MAXIMUM_SIMULATION_STEP_S

        assert branch._run_definition.state_at(case_s) == trunk._run_definition.state_at(case_s), (
            f"the branch and the trunk it returned to differ at {case_s} s"
        )


def test_a_mark_set_behind_the_clock_forks_where_its_halt_would_have() -> None:
    """Marking late changes when the mark was set, and nothing about the branch.

    The same case is run twice. In the first run, the mark is set before the
    clock reaches 45.3 s, so the run halts there and is forked at the halt. In
    the second, the mark is set only after the clock has passed it. No step
    crosses it, and the fork comes through `resumed_at_mark`. The two branches
    open at the same step, 45.300000000000004 s, which is the end of the step
    that reached the typed 45.3. They open from the same state, inside the
    same stretch, at the same crossing.
    """

    at_the_halt = _trunk_halted_on_a_bookmark().resumed_here()

    late = SimulationController()
    late.start()
    _advance_for(late, duration_s=30.0)
    late.set_delivered_concentration_percent(Percent(4.0))
    _advance_for(late, duration_s=60.0)
    late.pause()
    late.add_time_bookmark(TimeBookmark(CaseInstant(45.3), "the decision point"))

    behind_the_clock = late.resumed_at_mark(TimeBookmark(CaseInstant(45.3)))

    assert behind_the_clock.began_at_s == 453 * MAXIMUM_SIMULATION_STEP_S
    assert behind_the_clock.began_at_s != 45.3
    assert behind_the_clock.opened_from is not None
    assert behind_the_clock.opened_from == at_the_halt.opened_from


def test_a_mark_the_run_halted_on_is_returned_to_alike_before_and_after_it_steps_on() -> None:
    """A step uses up the halt, but not the mark that the run stopped at.

    While the trunk is at the halt, both fork methods give the same branch.
    Once the trunk steps on, `resumed_here` opens where the trunk then is, as
    it should. The mark still gives the branch that the halt gave.
    """

    marked = _trunk_halted_on_a_bookmark()
    mark = TimeBookmark(CaseInstant(45.3))
    at_the_halt = marked.resumed_here()

    assert marked.resumed_at_mark(mark).opened_from == at_the_halt.opened_from

    marked.start()
    _advance_for(marked, duration_s=30.0)
    marked.pause()

    assert marked.resumed_here().began_at_s == marked.snapshot().elapsed_s > mark.instant_s
    assert marked.resumed_at_mark(mark).opened_from == at_the_halt.opened_from


@pytest.mark.parametrize(("typed_s", "steps"), [(45.3, 453), (45.35, 454)])
def test_a_branch_returned_to_a_mark_off_the_step_grid_reads_it_as_passed(
    typed_s: float, steps: int
) -> None:
    """A branch at a mark a few parts in 1e16 off the grid, or inside a step, opens just past it.

    That puts the mark before the branch's own beginning. The clock alone
    would call the mark `BEFORE_THIS_BRANCH`, meaning unreachable. That is the
    wrong answer for the one mark the branch was taken at. The crossing at
    which the branch opens is what shows that the mark and the fork are one
    event (`PL-3K9B`, case B), and a reset keeps that crossing.
    """

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(typed_s))
    trunk.add_time_bookmark(mark)

    branch = trunk.resumed_at_mark(mark)

    assert branch.began_at_s == steps * MAXIMUM_SIMULATION_STEP_S
    assert branch.began_at_s > typed_s, "the premise: the branch opens after its own mark"
    assert branch.snapshot().bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED

    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.reset()

    assert branch.snapshot().elapsed_s == steps * MAXIMUM_SIMULATION_STEP_S
    assert branch.snapshot().bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED


def test_a_height_crossed_on_the_step_that_reached_a_passed_mark_is_stood_on_too() -> None:
    """The crossing is reconstructed by the rule that halts a run, so it names every mark crossed.

    One run finds the step on which a height is crossed, by halting there. A
    second, identical run marks that instant and that height only after its
    clock is well past both, so no step halted on either. Returning to the
    instant opens the branch at a crossing that names both, as a halt there
    would have.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.4), "the decision point")
    finder = SimulationController()
    finder.add_mac_target(target)
    finder.start()
    _advance_until_halted(finder, limit_s=400.0)
    crossed_at_s = finder.snapshot().elapsed_s

    late = SimulationController()
    late.start()

    for _ in range(finder._state.step_count + 600):
        late.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    late.pause()
    instant = TimeBookmark(CaseInstant(crossed_at_s))
    late.add_time_bookmark(instant)
    late.add_mac_target(target)

    branch = late.resumed_at_mark(instant)

    assert branch.opened_from is not None
    assert branch.opened_from.crossing == BookmarkCrossing(crossed_at_s, (instant,), (target,))
    assert branch.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_mark_added_after_the_step_that_crossed_it_reads_alike_on_every_run() -> None:
    """One result per mark, whichever run is asked and whichever order the mark and branch came in.

    These are the three cases that `PL-1ZQ4` reproduced. Each is built on the
    step on which a 0.3 xMAC alveolar target is crossed. A finder run halts
    there to identify that step. Each case asks that one step about marks
    added after it was taken:

    1. A trunk paused on the step, with the target added afterwards, showed
       the target as still running, while a branch opened there showed it as
       reached. They still disagreed 300 s later.
    2. A trunk halted on the step by a time mark. Marks added before
       `fork_here` showed as passed and reached on the branch. Marks added to
       both runs after `fork_here` showed as before this branch and still
       running.
    3. The same halt with a setting changed on it, so the halt is a keyframe
       too. `fork_at` there opened at no crossing, while `fork_here` opened at
       the halt's crossing.

    Every run here is stopped on that step or opened on it, so each mark
    inside the step counts as crossed by it: the late time mark as passed, and
    the target as reached (`docs/MODEL.md` § "Halting on a marked crossing").
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3))
    finder = SimulationController()
    finder.add_mac_target(target)
    finder.start()
    _advance_until_halted(finder, limit_s=400.0)
    crossing_steps = finder._state.step_count
    crossed_at_s = finder.snapshot().elapsed_s
    # Both lie inside the crossing step, which ends at `crossed_at_s`: the
    # first halts the run there, and the second is added after the halt.
    halting = TimeBookmark(CaseInstant(crossed_at_s - 0.05), "halts the run")
    late = TimeBookmark(CaseInstant(crossed_at_s - 0.07), "added late")

    def standings(run: SimulationController) -> tuple[MarkStanding, ...]:
        answers = run.snapshot().bookmark_standings

        return tuple(answers.of_time_bookmark(mark) for mark in (halting, late)) + (
            answers.of_mac_target(target),
        )

    def halted_on_the_step() -> SimulationController:
        run = SimulationController()
        run.add_time_bookmark(halting)
        run.start()
        _advance_until_halted(run, limit_s=400.0)
        assert run.snapshot().elapsed_s == crossed_at_s, "the premise: the halt is the step's"

        return run

    def add_late_marks(*runs: SimulationController) -> None:
        for run in runs:
            run.add_time_bookmark(late)
            run.add_mac_target(target)

    reached = (MarkStanding.PASSED, MarkStanding.PASSED, MarkStanding.REACHED)

    # Case 1: a plain pause, with the target added afterwards. The time marks
    # are added with it, so every run is asked about the same three marks.
    paused = SimulationController()
    paused.start()

    for _ in range(crossing_steps):
        paused.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    paused.pause()
    paused.add_time_bookmark(halting)
    add_late_marks(paused)
    from_the_pause = BranchedCase(paused).fork_here()

    assert standings(paused) == standings(from_the_pause) == reached

    for run in (paused, from_the_pause):
        run.start()
        _advance_for(run, duration_s=300.0)
        run.pause()

    assert paused.snapshot().elapsed_s == from_the_pause.snapshot().elapsed_s
    assert standings(paused) == standings(from_the_pause) == reached

    # Case 2: one trunk gets the late marks before it is branched. The other is branched
    # first, and then both runs get the marks.
    marked_first = halted_on_the_step()
    add_late_marks(marked_first)
    branched_after_marking = BranchedCase(marked_first).fork_here()

    branched_first = halted_on_the_step()
    branched_before_marking = BranchedCase(branched_first).fork_here()
    add_late_marks(branched_first, branched_before_marking)

    assert standings(marked_first) == standings(branched_after_marking) == reached
    assert standings(branched_first) == standings(branched_before_marking) == reached

    # Case 3: a setting change makes the halt a keyframe, then both fork methods are used.
    changed_on_the_halt = halted_on_the_step()
    changed_on_the_halt.set_fresh_gas_flow(FreshGasFlow(3.0))
    add_late_marks(changed_on_the_halt)
    case = BranchedCase(changed_on_the_halt)
    at_the_keyframe = case.fork_at(CaseInstant(crossed_at_s))
    where_it_stands = case.fork_here()

    assert at_the_keyframe.opened_from is not None
    assert at_the_keyframe.opened_from.crossing == BookmarkCrossing(
        CaseInstant(crossed_at_s), (halting, late), (target,)
    )
    assert at_the_keyframe.opened_from == where_it_stands.opened_from
    assert standings(changed_on_the_halt) == reached
    assert standings(at_the_keyframe) == standings(where_it_stands) == reached


def test_a_mark_at_the_case_s_opening_returns_to_induction_with_no_crossing() -> None:
    """No step reaches it, because the run is at it from the start, so the fork is the opening.

    The branch is the one that `resumed_at` gives at the opening keyframe, and
    the clock alone shows the mark as passed there.
    """

    trunk = _trunk_paused_past_a_change()
    at_induction = TimeBookmark(CaseInstant(0.0), "induction")
    trunk.add_time_bookmark(at_induction)

    returned = trunk.resumed_at_mark(at_induction)

    assert returned.opened_from is not None
    assert returned.opened_from.crossing is None
    assert returned.opened_from == trunk.resumed_at(CaseInstant(0.0)).opened_from
    assert returned.snapshot().bookmark_standings.of_time_bookmark(at_induction) is (
        MarkStanding.PASSED
    )


def test_a_mark_is_returned_to_by_its_instant_whatever_label_the_caller_holds() -> None:
    """The mark is matched as removal matches it, and the crossing carries the run's own copy."""

    trunk = _trunk_paused_past_a_change()
    held = TimeBookmark(CaseInstant(60.0), "what if")
    trunk.add_time_bookmark(held)

    branch = trunk.resumed_at_mark(TimeBookmark(CaseInstant(60.0)))

    assert branch.opened_from is not None
    assert branch.opened_from.crossing is not None
    assert branch.opened_from.crossing.time_bookmarks == (held,)


def test_a_mark_still_ahead_of_the_clock_cannot_be_returned_to() -> None:
    """The case has no state there yet, and a fork there would be a prediction drawn as a run."""

    trunk = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600.0))
    trunk.add_time_bookmark(ahead)

    with pytest.raises(SimulationConfigurationError, match="short of the mark at 600.0 s"):
        trunk.resumed_at_mark(ahead)

    assert trunk.mark_fork_points == ()


def test_an_instant_nobody_marked_cannot_be_returned_to_as_a_mark() -> None:
    """The method takes a mark the run has, so the learner must mark the instant first."""

    trunk = _trunk_paused_past_a_change()

    with pytest.raises(SimulationConfigurationError, match="no time bookmark stands at 60.0 s"):
        trunk.resumed_at_mark(TimeBookmark(CaseInstant(60.0)))


def test_a_branch_cannot_be_returned_to_a_mark_it_has_passed() -> None:
    """The flat shape still applies to the third fork method, with the same message."""

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(60.0))
    trunk.add_time_bookmark(mark)
    branch = trunk.resumed_at_mark(mark)
    branch.start()
    _advance_for(branch, duration_s=30.0)
    branch.pause()
    later = TimeBookmark(CaseInstant(75.0))
    branch.add_time_bookmark(later)

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_at_mark(later)


def test_the_marks_a_trunk_can_be_returned_to_are_the_ones_its_standings_call_passed() -> None:
    """The marks come earliest first, each with the step instant a branch opens at, none ahead."""

    trunk = _trunk_paused_past_a_change()
    later = TimeBookmark(CaseInstant(120.0), "added first")
    ahead = TimeBookmark(CaseInstant(600.0))
    off_grid = TimeBookmark(CaseInstant(45.3))

    for mark in (later, ahead, off_grid):
        trunk.add_time_bookmark(mark)

    snapshot = trunk.snapshot()

    assert trunk.mark_fork_points == (
        MarkForkPoint(off_grid, CaseInstant(453 * MAXIMUM_SIMULATION_STEP_S)),
        MarkForkPoint(later, CaseInstant(1200 * MAXIMUM_SIMULATION_STEP_S)),
    )
    assert {point.bookmark for point in trunk.mark_fork_points} == {
        mark
        for mark in snapshot.bookmarks.time_bookmarks
        if snapshot.bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED
    }


def test_a_trunk_that_has_not_stepped_can_be_returned_only_to_a_mark_at_its_opening() -> None:
    """With no step taken, no mark can be reached, and the run is still at its opening."""

    trunk = SimulationController()
    at_induction = TimeBookmark(CaseInstant(0.0))
    ahead = TimeBookmark(CaseInstant(30.0))
    trunk.add_time_bookmark(at_induction)
    trunk.add_time_bookmark(ahead)

    assert trunk.mark_fork_points == (MarkForkPoint(at_induction, CaseInstant(0.0)),)
    assert trunk.resumed_at_mark(at_induction).began_at_s == 0.0

    with pytest.raises(SimulationConfigurationError, match="short of the mark at 30.0 s"):
        trunk.resumed_at_mark(ahead)


def test_a_case_keeps_a_branch_returned_to_a_mark_its_trunk_has_passed() -> None:
    """The case-level method keeps the branch and adds no instant to `fork_points_s`."""

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(60.0))
    trunk.add_time_bookmark(mark)
    case = BranchedCase(trunk)

    assert case.mark_fork_points == trunk.mark_fork_points

    branch = case.fork_at_mark(mark)

    assert case.branches == (branch,)
    assert branch.began_at_s == 60.0
    assert case.fork_points_s == (0.0, 30.0)
    assert trunk.snapshot().elapsed_s == 180.0


def test_a_case_refuses_a_mark_its_trunk_has_not_reached_and_keeps_nothing() -> None:
    """The refusal passes through `BranchedCase`, as the other two fork methods' refusals do."""

    trunk = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600.0))
    trunk.add_time_bookmark(ahead)
    case = BranchedCase(trunk)

    with pytest.raises(SimulationConfigurationError, match="short of the mark"):
        case.fork_at_mark(ahead)

    assert case.branches == ()


# --- Standing on the supported run length with no step refused (PL-5291) ------
#
# The core refuses the step *from* the last supported count. So a run that
# stops only when a step is refused looks like an ordinary pause on every route
# that brings it to 24:00:00 without a refused step. Those routes are a trunk
# halted there on a mark, a branch forked there, and a branch reset onto such
# a fork. Each of these offered Start, showed no limit notice, and told a
# learner that an unreached mark was still ahead of a run that could not step.
# Every assertion below is checked end to end, from the controller's snapshot
# through the pure dashboard functions that a frame is built from. They use
# the shipped 0.1 s step, because that is the step whose last supported count
# lands exactly on 24 hours (`PL-8H2R`).
#
# Stepping a run to 24 hours takes about 30 s. So the two runs that do it are
# built once per pytest run and shared between xdist workers. Nothing below
# changes what another test reads from them. A fork leaves its parent
# untouched, and the one dial moved on a stopped run is refused (`PL-3B34`).

#: A height the fat group cannot reach at 1 MAC delivered. The mark stays
#: unreached on every run below, so its standing is what the tests check.
_UNREACHABLE_TARGET = MacTarget(RecordedQuantity.FAT, MacMultiple(3.0), "never")


def _step_onto_the_supported_run_length(controller: SimulationController) -> None:
    """Take exactly the supported number of 0.1 s steps, and no refused one.

    `maximum_step_count` is the largest step count the run may reach. The core
    refuses the step after it, and this helper never takes that step.
    """

    controller.start()
    step = SimulationStep(MAXIMUM_SIMULATION_STEP_S)

    for _ in range(maximum_step_count(step)):
        controller.advance(step)


def _stepped_onto_the_limit() -> SimulationController:
    """An unmarked trunk that took the last supported step and was never refused one."""

    controller = SimulationController()
    _step_onto_the_supported_run_length(controller)

    return controller


def _halted_on_a_mark_at_the_limit() -> SimulationController:
    """A trunk halted by a time mark on 24:00:00, carrying a mark it never reached."""

    controller = SimulationController()
    controller.add_time_bookmark(
        TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S), "the end")
    )
    controller.add_mac_target(_UNREACHABLE_TARGET)
    _step_onto_the_supported_run_length(controller)

    return controller


@pytest.fixture(scope="module")
def trunk_stepped_onto_the_limit(
    computed_once: Callable[[str, Callable[[], SimulationController]], SimulationController],
) -> SimulationController:
    """An unmarked trunk that took the last supported step and was never refused one."""

    return computed_once("controller trunk stepped onto the limit", _stepped_onto_the_limit)


@pytest.fixture(scope="module")
def trunk_halted_on_a_mark_at_the_limit(
    computed_once: Callable[[str, Callable[[], SimulationController]], SimulationController],
) -> SimulationController:
    """A trunk halted by a time mark on 24:00:00, carrying a mark it never reached."""

    return computed_once(
        "controller trunk halted on a mark at the limit", _halted_on_a_mark_at_the_limit
    )


#: The two runs above, each with the number of simulated minutes it steps
#: through. `tests/conftest.py` schedules every test that reads one of them
#: back to back, at the start of one xdist worker's first slice (`PL-K5VM`).
#: Each run is built once per pytest run. A worker that `worksteal` gives one
#: of these tests reads the run through `computed_once` rather than building
#: it again (`PL-ZWQS`).
MODULE_FIXTURE_MINUTES = {
    fixture.name: MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_MINUTE
    for fixture in (trunk_stepped_onto_the_limit, trunk_halted_on_a_mark_at_the_limit)
}


def _the_reason_the_refused_step_would_give(run: SimulationController) -> str:
    """The message with which the core refuses this run's next step, taken from the core."""

    with pytest.raises(SimulationDomainLimitError) as refusal:
        require_supported_run_length(
            run._state.step_count, SimulationStep(MAXIMUM_SIMULATION_STEP_S)
        )

    return str(refusal.value)


def _assert_reads_as_stopped_at_the_supported_run_length(run: SimulationController) -> None:
    """Check `PL-5291`'s completion condition: every reader says the run is at the limit.

    The snapshot carries the reason the refused step would give. Start is
    refused and not offered. The banner names the limit. A mark the run never
    reached shows as "not reached within the supported run length", not as
    still ahead. None of them shows a failure.
    """

    snapshot = run.snapshot()

    assert snapshot.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert snapshot.is_running is False
    assert run.has_reached_supported_limit is True
    assert snapshot.supported_limit_reason == _the_reason_the_refused_step_would_give(run)
    assert run.has_failed is False
    assert snapshot.failure_reason is None

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        run.start()

    assert run.snapshot().is_running is False
    assert transport(snapshot).start_enabled is False
    assert notice(snapshot, None) == SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(
        run_length=format_supported_run_length(), exit=RESET_EXIT_TEXT
    )

    if _UNREACHABLE_TARGET in snapshot.bookmarks.mac_targets:
        standing = snapshot.bookmark_standings.of_mac_target(_UNREACHABLE_TARGET)

        assert standing is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_run_standing_on_the_supported_run_length_reads_as_stopped_from_the_arriving_step(
    trunk_stepped_onto_the_limit: SimulationController,
) -> None:
    """The run halts on the step that arrives at the limit, not one refused tick later.

    No step was refused: the run took exactly the supported count of steps and
    stopped there. Because the limit is read from the state, this stop is the
    same stop that the refusal used to produce. Halting on arrival keeps the
    snapshot's contract, which is that `is_running` is false wherever a limit
    reason is set. It does so without a flag that only a refusal could set.
    """

    trunk = trunk_stepped_onto_the_limit

    assert trunk._state.step_count == maximum_step_count(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    _assert_reads_as_stopped_at_the_supported_run_length(trunk)

    # A further tick does nothing, as it does on a paused run. Nothing is
    # raised, and the clock stays exactly where the last supported step left it.
    trunk.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert trunk.snapshot().elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_a_trunk_halted_on_a_mark_at_the_supported_run_length_reads_as_stopped_there(
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """The first row of `PL-5291`'s table: a trunk halted on a mark at 24:00:00.

    That trunk showed "Paused" and offered Start.
    """

    trunk = trunk_halted_on_a_mark_at_the_limit
    snapshot = trunk.snapshot()

    assert snapshot.bookmark_halt is not None
    assert snapshot.bookmark_standings.of_time_bookmark(
        TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S), "the end")
    ) is (MarkStanding.PASSED)
    _assert_reads_as_stopped_at_the_supported_run_length(trunk)


def test_a_branch_forked_at_a_halt_on_the_supported_run_length_reads_as_stopped_there(
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """The route the item is named for: a branch built at 24:00:00.

    `_open_at` builds the state at the parent's step count and never asks
    whether there is room for another step. Nothing refuses a step until Start
    is pressed. A branch is a new controller, so a flag on the parent would
    not have reached it either. The limit has to be read from the branch's own
    state. The branch is taken through `resumed_at_mark`, because the trunk's
    position at the limit is not offered as a place to branch (`PL-Y2SL`).
    """

    branch = trunk_halted_on_a_mark_at_the_limit.resumed_at_mark(
        TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    )

    assert branch.opened_from is not None
    _assert_reads_as_stopped_at_the_supported_run_length(branch)


def test_no_dial_makes_a_keyframe_on_the_supported_run_length_to_branch_at(
    trunk_stepped_onto_the_limit: SimulationController,
) -> None:
    """A dial moved on the stopped trunk is refused, so no branch opens at a keyframe on 24:00:00.

    Until `PL-3B34`, a dial moved after the run stopped was recorded at
    24:00:00. That made a keyframe there, and `resumed_at` opened a branch on
    it that could never step. The stopped run now refuses the dial, so the
    trunk keeps its one stretch from 0 s, and `resumed_at` rejects the limit as
    an instant with no keyframe. A mark on the limit is the one fork left
    there, and `test_a_branch_forked_at_a_halt_on_the_supported_run_length_reads_as_stopped_there`
    covers it.
    """

    trunk = trunk_stepped_onto_the_limit

    with pytest.raises(
        SimulationConfigurationError,
        match="^the fresh gas flow setting cannot be changed on a stopped run",
    ):
        trunk.set_fresh_gas_flow(FreshGasFlow(6.0))

    assert [segment.opening.instant_s for segment in trunk.run_segments] == [0.0]

    with pytest.raises(SimulationConfigurationError, match="keyframe"):
        trunk.resumed_at(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))

    _assert_reads_as_stopped_at_the_supported_run_length(trunk)


def test_a_branch_reset_onto_a_fork_on_the_supported_run_length_reads_as_stopped_there(
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """Reset returns a branch to its fork, and a fork on the limit has no span left.

    This is the last row of `PL-5291`'s table. Reset clears the recorded
    reason, as it must for a trunk going back to zero. A branch going back to
    a fork at 24:00:00 then showed as paused again, with Start offered again.
    Now the limit is read from the state, so the branch is at the limit, and a
    reset leaves it there.
    """

    branch = trunk_halted_on_a_mark_at_the_limit.resumed_at_mark(
        TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    )
    branch.reset()

    _assert_reads_as_stopped_at_the_supported_run_length(branch)


def test_a_run_at_the_supported_run_length_offers_no_place_to_branch_where_it_stands(
    trunk_stepped_onto_the_limit: SimulationController,
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """A stop at the limit is not a pause, so the run's position is neither offered nor taken.

    No step is left to take there, so a branch opened where the run is stopped
    could never be run. While the case allows only one comparison, only the trunk's
    Reset, which discards the case, would take that branch off the chart
    (`PL-Y2SL`). Both ways of arriving there are refused alike: stepping onto
    the limit, and halting on a mark at it. The refusal names the fork methods
    that still work there.
    """

    for trunk in (trunk_stepped_onto_the_limit, trunk_halted_on_a_mark_at_the_limit):
        assert trunk.here_fork_point is None
        assert BranchedCase(trunk).here_fork_point is None

        with pytest.raises(SimulationConfigurationError, match="supported run length") as refusal:
            trunk.resumed_here()

        assert "resumed_at_mark" in str(refusal.value)


# --- Each branch refusal a learner can read, pinned whole (PL-79PK) -----------
#
# `SimulationView` shows the message for a refused branch, and for a refused
# agent change, word for word in the "Setting refused" banner. The tests above
# match one phrase of each message, so they pass even when the instant, the
# reason or the advice is wrong. Each expected sentence below is typed by hand
# from the run the test builds. The two-change trunk changes a setting at 30 s
# and 60 s and stops at 120 s. The paused-past-a-change trunk changes one
# setting at 30 s and stops at 180 s.


def test_a_branch_s_agent_change_refusal_is_pinned_whole() -> None:
    trunk = _trunk_with_two_changes()
    branch = BranchedCase(trunk).fork_at(CaseInstant(60.0))

    with pytest.raises(SimulationConfigurationError) as refusal:
        branch.set_agent("desflurane")

    assert str(refusal.value) == (
        "this run is a branch opened at 60.0 s, and a branch carries the agent of the case "
        "it continues; changing agent begins a new case, so change it on the run this "
        "branch came from or start a new one"
    )


def test_a_branch_at_no_keyframe_refusal_is_pinned_whole() -> None:
    trunk = _trunk_with_two_changes()

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(CaseInstant(65.0))

    assert str(refusal.value) == (
        "this run holds no keyframe at 65.0 s, and resumed_at opens at one: the run's "
        "opening or a recorded setting change, which this run holds at [0.0, 30.0, 60.0] s. "
        "A marked instant is branched at with resumed_at_mark once the run has passed it, "
        "and the instant a paused run stands at with resumed_here"
    )


def test_each_refusal_to_branch_where_a_run_stands_is_pinned_whole() -> None:
    going = _trunk_with_two_changes()
    going.start()
    failed = _trunk_with_two_changes()
    failed.fail("a step raised")
    opening = SimulationController()
    refusals = {}

    for name, trunk in (("going", going), ("failed", failed), ("opening", opening)):
        with pytest.raises(SimulationConfigurationError) as refusal:
            trunk.resumed_here()

        refusals[name] = str(refusal.value)

    assert refusals == {
        "going": (
            "this run is going, so where it stands moves with every step and an instant read "
            "off it is gone before it can be branched at; pause it, and resumed_here branches "
            "where it then stands"
        ),
        "failed": (
            "this run stopped at 120.0 s on a failure, not a pause (a step raised), so where "
            "it stands is not a place to branch; a setting change or a mark it passed before "
            "is still branched at with resumed_at or resumed_at_mark"
        ),
        "opening": (
            "this run stands at its opening and has recorded nothing to branch from; "
            "resumed_at opens a branch at the opening"
        ),
    }


def test_the_refusal_to_branch_at_the_supported_run_length_is_pinned_whole(
    trunk_stepped_onto_the_limit: SimulationController,
) -> None:
    """86,400 s is the supported run length `docs/MODEL.md` § "Supported run length" states."""

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk_stepped_onto_the_limit.resumed_here()

    assert str(refusal.value) == (
        "this run stands at 86400.0 s, the supported run length, where no step is left to "
        "take, so a branch opened where it stands could not be run; a setting change or a "
        "mark it passed before is still branched at with resumed_at or resumed_at_mark"
    )


def test_each_refusal_to_branch_at_a_mark_is_pinned_whole() -> None:
    trunk = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600.0))
    trunk.add_time_bookmark(ahead)

    with pytest.raises(SimulationConfigurationError) as short_of_it:
        trunk.resumed_at_mark(ahead)

    with pytest.raises(SimulationConfigurationError) as unmarked:
        trunk.resumed_at_mark(TimeBookmark(CaseInstant(60.0)))

    assert str(short_of_it.value) == (
        "this run's clock stands at 180.0 s, short of the mark at 600.0 s, so the case "
        "holds no state there to branch from: a mark is branched at once the run has "
        "passed it, or, standing on the step that crosses it, with resumed_here"
    )
    assert str(unmarked.value) == "no time bookmark stands at 60.0 s, so there is no mark there"
