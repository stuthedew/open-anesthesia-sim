import dataclasses

import pytest

from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.controller import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    CONTROL_INPUT_UNITS,
    ControlInput,
    RecordedQuantity,
    RecordedSeries,
    SimulationController,
)
from anesthesia_sim.app.wash_in import is_wash_in
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.parameters import load_reference_adult_parameters
from anesthesia_sim.core.run_score import ScoreSegment
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S


def _advance_for(controller: SimulationController, duration_s: float) -> None:
    """Advance a running controller to `duration_s` at the largest supported step.

    Simulated time comes from taking supported steps rather than from asking
    for one large one: `MAXIMUM_SIMULATION_STEP_S` is the declared
    control-resolution tolerance, and a step past it is refused.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        controller.advance(MAXIMUM_SIMULATION_STEP_S)


def test_default_controller_starts_with_sevoflurane() -> None:
    controller = SimulationController()

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "sevoflurane"
    assert snapshot.agent_display_name == "Sevoflurane"
    assert snapshot.max_delivered_concentration_percent == 8.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.02)


def test_default_controller_starts_each_agent_at_its_own_one_mac() -> None:
    """A freshly constructed controller starts at 1 MAC, the standard
    clinical starting point, not a fixed raw percentage.
    """

    assert SimulationController(
        agent_id="sevoflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.02)
    assert SimulationController(
        agent_id="isoflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.012)
    assert SimulationController(
        agent_id="desflurane"
    ).snapshot().delivered_concentration_fraction == pytest.approx(0.06)


def test_explicit_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): an explicitly requested fraction above a
    vaporizer's real maximum must fail, not be silently clamped.

    Clamping produced a run whose every displayed value came from a dial
    position the caller never asked for, which is indistinguishable on
    screen from one they did.
    """

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        SimulationController(agent_id="isoflurane", delivered_concentration_fraction=0.08)


def test_setting_a_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): the setter path is bounded by the same guard.

    Before the fix only the UI slider bounded this value, so any non-UI
    caller could simulate 50% isoflurane on a 5% vaporizer.
    """

    controller = SimulationController(agent_id="isoflurane")

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration(0.50)

    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.012)


def test_delivered_concentration_exactly_at_the_agent_max_is_accepted() -> None:
    """The boundary is inclusive: 5.0% is a real isoflurane dial position."""

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration(0.05)

    assert controller.snapshot().delivered_concentration_fraction == pytest.approx(0.05)


def test_delivered_concentration_can_be_turned_off() -> None:
    """Zero is always deliverable: it is the vaporizer off, which is how
    washout begins.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_concentration(0.0)

    assert controller.snapshot().delivered_concentration_fraction == 0.0


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
        alveolar_ventilation_l_min=3.0, cardiac_output_l_min=7.0
    ).snapshot()

    assert snapshot.alveolar_ventilation_l_min == pytest.approx(3.0)
    assert snapshot.cardiac_output_l_min == pytest.approx(7.0)


def test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac() -> None:
    """Switching agents must not carry over the old agent's raw percentage:
    the same percent means a different clinical depth per agent (e.g. 2%
    is 1 MAC of sevoflurane but only about a third of a MAC of desflurane).
    """

    controller = SimulationController(agent_id="sevoflurane", delivered_concentration_fraction=0.08)

    controller.set_agent("isoflurane")
    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.012)


def test_controller_can_be_constructed_for_a_different_agent() -> None:
    controller = SimulationController(agent_id="isoflurane")

    snapshot = controller.snapshot()

    assert snapshot.agent_id == "isoflurane"
    assert snapshot.agent_display_name == "Isoflurane"


def test_set_agent_starts_fresh_preserving_flow_settings_but_not_concentration() -> None:
    """Circuit, flow, ventilation, and cardiac output carry over; the
    delivered concentration resets to the new agent's own 1 MAC instead
    (see test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=5.0,
        fresh_gas_flow_l_min=3.0,
        delivered_concentration_fraction=0.03,
        alveolar_ventilation_l_min=5.5,
        cardiac_output_l_min=6.0,
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
    assert snapshot.delivered_concentration_fraction == pytest.approx(0.06)
    assert snapshot.alveolar_ventilation_l_min == 5.5
    assert snapshot.cardiac_output_l_min == 6.0


def test_set_agent_rejects_unknown_agent_id() -> None:
    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError, match="unknown agent_id"):
        controller.set_agent("halothane")


def test_pause_blocks_advancement() -> None:
    controller = SimulationController()

    controller.advance(0.1)

    assert controller.snapshot().elapsed_s == 0.0


def test_start_advance_pause_sequence_is_deterministic() -> None:
    first = SimulationController()
    second = SimulationController()

    for controller in (first, second):
        controller.start()
        controller.advance(0.1)
        controller.advance(0.1)
        controller.pause()

    assert first.snapshot() == second.snapshot()


def _samples_a_snapshot_carries(controller: SimulationController) -> int:
    """Count the recorded samples reachable from one `snapshot()`.

    Walked over the fields rather than asserted against a named one,
    because the defect this guards is a *field* - any field - that carries
    the run. Naming one would go on passing after it was renamed or
    replaced by a second copy under another name.
    """

    snapshot = controller.snapshot()
    total = 0

    for field in dataclasses.fields(snapshot):
        value = getattr(snapshot, field.name)

        if isinstance(value, ScoreSegment):
            total += 1
        elif isinstance(value, tuple | list):
            total += sum(1 for item in value if isinstance(item, ScoreSegment))

    return total


def test_a_frame_reads_only_the_window_it_draws() -> None:
    """PL-0VM7: what crosses this boundary is the window, never the run.

    A frame's cost was proportional to how long the simulation had been
    running: `snapshot()` copied every sample ever recorded, five times a
    second, and the chart discarded all but the few hundred inside its
    axis. Timing is too flaky to assert, so the count of values crossing
    the boundary is asserted instead - it is the quantity the cost was
    proportional to, and it is exact.

    Stronger since `PL-2FM6` than it was written to be: the window is the
    states at the instants drawn, so it is bounded by the column budget
    outright rather than by the window's width in samples. Two runs an
    order of magnitude apart, read at the same axis, hand over the same
    number of states.
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
        # The window is the run's tail, and it ends on the instant the
        # readouts were built from.
        assert window.times_s[0] == pytest.approx(elapsed_s - window_s)
        assert window.times_s[-1] == pytest.approx(elapsed_s)

        drawn.append(len(window.times_s))

    # The run grew ten-fold; what one frame reads did not grow with it. The
    # single column of slack is the grid's phase rather than growth: columns
    # are multiples of the spacing measured from `t = 0`, so two windows of
    # equal width sitting at different points on that grid fit one more or
    # one fewer of them.
    assert abs(drawn[1] - drawn[0]) <= 1


def test_the_window_ends_on_the_sample_the_readouts_were_built_from() -> None:
    """The trace's right-hand end and the metrics beside it are one instant.

    Split across two reads by PL-0VM7, so the property that was previously
    structural - one snapshot carried both - is now asserted. A window
    ending one sample short of the readouts would draw a chart that
    disagreed with the numbers printed beside it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 12.0)

    snapshot = controller.snapshot()
    window = controller.drawn_window(snapshot.elapsed_s - 5.0, snapshot.elapsed_s, 150)

    def drawn(quantity: RecordedQuantity) -> float:
        return window.compartment_fractions(RecordedSeries(snapshot.agent_id, quantity))[-1]

    assert window.times_s[-1] == pytest.approx(snapshot.elapsed_s)
    assert drawn(RecordedQuantity.CIRCUIT) == pytest.approx(snapshot.circuit_concentration_fraction)
    assert drawn(RecordedQuantity.ALVEOLAR) == pytest.approx(
        snapshot.alveolar_concentration_fraction
    )
    assert drawn(RecordedQuantity.FAT) == pytest.approx(snapshot.fat_partial_pressure_fraction)


def test_each_drawn_quantity_reads_the_state_of_the_compartment_it_names() -> None:
    """The same pairing, audited against the state vector the chart draws from.

    `COMPARTMENT_STATE_INDEX` is what `_build_history_sample` was once the
    chart evaluates the score instead of reading recorded samples
    (`PL-2FM6`): a position in `governing_equations`' state order rather
    than a compartment accessor. It is the one place a trace could come to
    carry another compartment's values, and a swap here would reach a
    labelled curve drawn entirely from numbers the model really produced -
    which is why it is audited against the core rather than restated.

    The three tissue groups are the entries worth the audit: they are
    consecutive positions from `FIRST_TISSUE_FRACTION`, so this table
    assumes `PatientCompartmentsState.tissues`' order and would keep
    passing every other check if that order changed.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=60.0)

    system = controller._state.uptake_system
    state = system.state_vector()

    assert {
        quantity: state[COMPARTMENT_STATE_INDEX[quantity]] for quantity in COMPARTMENT_STATE_INDEX
    } == {
        RecordedQuantity.CIRCUIT: system.circuit.circuit_concentration_fraction,
        RecordedQuantity.ALVEOLAR: system.alveoli.concentration_fraction,
        RecordedQuantity.MIXED_VENOUS: system.patient.mixed_venous_fraction,
        RecordedQuantity.VESSEL_RICH: system.patient.vessel_rich.partial_pressure_fraction,
        RecordedQuantity.MUSCLE: system.patient.muscle.partial_pressure_fraction,
        RecordedQuantity.FAT: system.patient.fat.partial_pressure_fraction,
    }

    # Every compartment the interface draws has an entry, and the derived
    # ratio has none: it is a quotient of two of these rather than a state.
    assert set(COMPARTMENT_STATE_INDEX) == set(COMPARTMENT_QUANTITIES)
    assert RecordedQuantity.WASH_IN_RATIO not in COMPARTMENT_STATE_INDEX

    # ...and sixty seconds in they are far enough apart that a swap shows.
    drawn = [state[COMPARTMENT_STATE_INDEX[quantity]] for quantity in COMPARTMENT_QUANTITIES]
    assert len(set(drawn)) == len(drawn)
    assert drawn[0] > 100.0 * drawn[-1]


def test_a_run_records_the_agent_it_is_a_run_of() -> None:
    """The substance a sample is keyed by is the agent the snapshot names.

    They are read together on every frame - the view addresses the run
    under `snapshot.agent_id` - so a run recorded under any other
    identifier would raise rather than draw, and `set_agent` has to leave
    the two agreeing.
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

        # Exactly the edge asked for, rather than the first sample at or
        # after it: a column is evaluated wherever it is wanted, so there
        # is no longer a cut that could land inside the drawn window.
        assert window.times_s[0] == pytest.approx(start_s)
        assert window.times_s[-1] == pytest.approx(elapsed_s)


def test_reset_pauses_and_clears_concentration_history() -> None:
    controller = SimulationController()
    controller.start()
    controller.advance(0.1)

    controller.reset()

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert snapshot.elapsed_s == 0.0
    assert snapshot.circuit_concentration_fraction == 0.0
    assert snapshot.alveolar_concentration_fraction == 0.0
    assert snapshot.stored_agent_l == 0.0

    window = controller.drawn_window(0.0, 0.0, 150)
    assert window.times_s == (0.0,)


def test_parameter_changes_do_not_reset_dynamic_state() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    before = controller.snapshot()

    controller.set_fresh_gas_flow(3.0)
    controller.set_delivered_concentration(0.06)

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.fresh_gas_flow_l_min == 3.0
    assert after.delivered_concentration_fraction == 0.06
    # The circuit volume is a fixed model parameter, so a settings change
    # must leave it exactly where the session was built with it (`PL-GYH2`).
    assert after.circuit_volume_l == before.circuit_volume_l


def test_the_circuit_volume_is_a_build_time_parameter_with_no_live_setter() -> None:
    """`PL-GYH2`: the app layer offers no route to the circuit volume.

    It is set once, from the value this controller is built with, and no
    interface control reaches it thereafter. The setter that used to sit on
    `SimulationController` was public and unbounded, so it let any caller of
    the app layer put the circuit outside the domain `docs/MODEL.md`
    verifies - for a control the interface has never offered. Asserted on
    the class rather than on an instance so that re-adding the method fails
    here whatever a run has done.

    `BreathingCircuit.set_circuit_volume` is deliberately untouched: it is
    how the parameter reaches the circuit at all, and it is where the
    conservation and capacity guards live (`PL-006`, `tests/unit/test_circuit.py`).
    """

    assert not hasattr(SimulationController, "set_circuit_volume")

    controller = SimulationController(circuit_volume_l=5.0)
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_fresh_gas_flow(3.0)

    assert controller.snapshot().circuit_volume_l == 5.0


def test_a_failed_session_is_not_the_same_state_as_a_pause() -> None:
    """`is_running` alone cannot carry the difference, so the reason does.

    A pause and a failure both stop the run, but only one of them leaves
    state a reader can trust. The snapshot has to say which it is.
    """

    controller = SimulationController()
    controller.start()
    controller.advance(0.1)

    paused = SimulationController()
    paused.start()
    paused.advance(0.1)
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
    controller.advance(0.1)
    controller.fail("SimulationNumericalError: boom")
    elapsed_at_failure = controller.snapshot().elapsed_s

    controller.advance(0.1)

    assert controller.snapshot().elapsed_s == elapsed_at_failure


def test_the_first_failure_reason_is_the_one_kept() -> None:
    """A later raise reacting to the same broken state must not mask it."""

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
    controller.advance(0.1)
    controller.fail("SimulationNumericalError: boom")

    controller.reset()

    assert controller.has_failed is False
    assert controller.snapshot().failure_reason is None
    assert controller.snapshot().elapsed_s == 0.0

    controller.start()
    controller.advance(0.1)

    assert controller.snapshot().is_running is True
    assert controller.snapshot().elapsed_s == pytest.approx(0.1)


def test_switching_agent_clears_a_failure() -> None:
    """Switching agents begins a new run, so nothing survives the old one."""

    controller = SimulationController()
    controller.start()
    controller.advance(0.1)
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
    controller.advance(0.1)
    before = controller.snapshot()

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_concentration(0.50)

    after = controller.snapshot()

    assert after.failure_reason is None
    assert after.is_running is True
    assert after.delivered_concentration_fraction == before.delivered_concentration_fraction


class _FatThatRefusesTheStep(TissueGroup):
    """A fat group that refuses the fraction the exact step hands it.

    Until `PL-GS5X` these tests reached a failing step through the model, on
    a patient file whose lungs one supported step of uptake could overdraw.
    The exact step closed that route for good rather than for these numbers:
    it is the solution of a system whose every off-diagonal entry is a
    transfer rate, so its propagator is entrywise nonnegative and no
    parameter set can make it carry a compartment out of range.

    What these tests are about is unchanged and still worth covering - that a
    numerical failure reaching the app boundary halts the run, leaves the
    chart history alone and leaves every displayed value bit-identical - so
    the failure is injected here instead. `tests/unit/
    test_uptake_system_failure.py` carries the same construction and the
    reasoning behind it; fat is the group armed because
    `_write_state_vector` writes it last.
    """

    def set_partial_pressure_fraction(self, partial_pressure_fraction: float) -> None:
        super().set_partial_pressure_fraction(-1.0)


def _controller_one_setting_from_a_failed_step() -> SimulationController:
    """A run 60 s in, whose next step a compartment refuses mid-write."""

    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    _advance_for(controller, duration_s=60.0)

    patient = controller._state.uptake_system.patient
    original = patient.fat
    patient.fat = _FatThatRefusesTheStep(
        name=original.name,
        volume_l=original.volume_l,
        perfusion_fraction=original.perfusion_fraction,
        blood_gas_partition_coefficient=(original.blood_gas_partition_coefficient),
        tissue_gas_partition_coefficient=(original.tissue_gas_partition_coefficient),
        blood_flow_l_min=original.blood_flow_l_min,
        agent_amount_l=original.agent_amount_l,
    )

    return controller


def test_a_failed_step_adds_nothing_to_the_chart_history() -> None:
    """PL-026 end to end, at the boundary the chart is actually drawn from.

    The item's complaint was about what a halted run displays, and the
    traces are drawn from the recorded history rather than from the
    compartments directly. A failed step must therefore leave the history
    exactly as long as it was, ending on the same sample: a history one
    entry longer would put a point on the chart that no completed step
    produced, at a simulation time that never happened.
    """

    controller = _controller_one_setting_from_a_failed_step()
    before_s = controller.snapshot().elapsed_s
    before = controller.drawn_window(0.0, before_s, 150)

    with pytest.raises(SimulationNumericalError):
        controller.advance(MAXIMUM_SIMULATION_STEP_S)

    after = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)

    assert controller.snapshot().elapsed_s == before_s
    assert after.times_s == before.times_s
    assert after.states == before.states


def test_a_failed_step_leaves_every_displayed_value_bit_identical() -> None:
    """The metrics beside the chart, held to the same standard.

    Every concentration the dashboard shows comes off this snapshot, so
    the rollback in `core/` is only worth having if it reaches here
    unchanged. `==` rather than `pytest.approx`, for the reason the core
    test gives: the claim is that nothing was written, not that what was
    written came back close.
    """

    controller = _controller_one_setting_from_a_failed_step()
    before = controller.snapshot()

    with pytest.raises(SimulationNumericalError):
        controller.advance(MAXIMUM_SIMULATION_STEP_S)

    after = controller.snapshot()

    assert after.circuit_concentration_fraction == before.circuit_concentration_fraction
    assert after.alveolar_concentration_fraction == before.alveolar_concentration_fraction
    assert after.mixed_venous_concentration_fraction == (before.mixed_venous_concentration_fraction)
    assert after.vessel_rich_partial_pressure_fraction == (
        before.vessel_rich_partial_pressure_fraction
    )
    assert after.muscle_partial_pressure_fraction == before.muscle_partial_pressure_fraction
    assert after.fat_partial_pressure_fraction == before.fat_partial_pressure_fraction

    # The mass-accounting panel too: it is a displayed value like any other,
    # and its totals are the two the validator accumulates during a step.
    assert after.delivered_agent_l == before.delivered_agent_l
    assert after.exhausted_agent_l == before.exhausted_agent_l
    assert after.stored_agent_l == before.stored_agent_l
    assert after.agent_accounting_passes_validation


def test_a_setting_change_is_recorded_with_the_time_it_took_effect() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)

    controller.set_fresh_gas_flow(3.0)

    (change,) = controller.snapshot().control_timeline
    assert change.control is ControlInput.FRESH_GAS_FLOW
    assert change.elapsed_s == pytest.approx(1.0)
    assert change.previous_value == pytest.approx(4.0)
    assert change.new_value == pytest.approx(3.0)
    assert change.unit == "L/min"


def test_every_control_records_under_its_own_stable_identifier() -> None:
    """The stored identifiers are the timeline's contract with future runs.

    They are asserted as literal strings rather than against the enum,
    because the enum is what a rename would move and these are what a
    recorded run would then no longer be readable under. PL-9SH6 and
    PL-3TLK rename two of the setters underneath them in v0.4.1.
    """

    controller = SimulationController()

    controller.set_fresh_gas_flow(3.0)
    controller.set_delivered_concentration(0.03)
    controller.set_alveolar_ventilation(5.0)
    controller.set_cardiac_output(4.0)

    assert [change.control.value for change in controller.snapshot().control_timeline] == [
        "fresh_gas_flow",
        "delivered",
        "alveolar_ventilation",
        "cardiac_output",
    ]


def test_every_recorded_control_carries_its_declared_unit() -> None:
    controller = SimulationController()

    controller.set_fresh_gas_flow(3.0)
    controller.set_delivered_concentration(0.03)
    controller.set_alveolar_ventilation(5.0)
    controller.set_cardiac_output(4.0)

    for change in controller.snapshot().control_timeline:
        assert change.unit == CONTROL_INPUT_UNITS[change.control]


def test_the_delivered_dial_is_recorded_as_the_fraction_the_core_holds() -> None:
    """Recording the interface's percent would break re-application.

    The timeline's claim is that re-applying it reproduces the run, and
    re-applying means calling the setter, which takes a fraction. A record
    of 3.0 where the model holds 0.03 would be a hundredfold error handed
    to whatever replays it.
    """

    controller = SimulationController()

    controller.set_delivered_concentration(0.03)

    (change,) = controller.snapshot().control_timeline
    assert change.new_value == pytest.approx(0.03)
    assert change.new_value == pytest.approx(controller.snapshot().delivered_concentration_fraction)


def test_a_setting_equal_to_the_one_in_place_records_nothing() -> None:
    """A slider re-entering a position it already holds is not a change."""

    controller = SimulationController()
    current = controller.snapshot().fresh_gas_flow_l_min

    controller.set_fresh_gas_flow(current)

    assert controller.snapshot().control_timeline == ()


def test_a_refused_setting_records_nothing() -> None:
    """It never took effect, so it is not part of the run.

    The guarantee is structural rather than incidental: the recorder runs
    after the core's setter returns, so a raise reaches the interface with
    the timeline untouched.
    """

    controller = SimulationController()

    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_concentration(0.5)

    assert controller.snapshot().control_timeline == ()
    assert not controller.has_failed


def test_changes_within_one_step_collapse_to_what_the_model_integrated() -> None:
    """Only the value standing when a step runs is ever integrated.

    A dial dragged from 2% through 3% to 4% between two steps is one change
    from 2% to 4% as far as the run is concerned, and a timeline that
    listed the intermediate value would describe a run that never happened.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)

    controller.set_delivered_concentration(0.03)
    controller.set_delivered_concentration(0.04)

    (change,) = controller.snapshot().control_timeline
    assert change.previous_value == pytest.approx(0.02)
    assert change.new_value == pytest.approx(0.04)
    assert change.elapsed_s == pytest.approx(1.0)


def test_a_change_undone_within_one_step_leaves_no_entry() -> None:
    """Returning to the step's own value means the model saw no change."""

    controller = SimulationController()

    controller.set_delivered_concentration(0.03)
    controller.set_delivered_concentration(0.02)

    assert controller.snapshot().control_timeline == ()


def test_the_same_control_changed_across_two_steps_records_both() -> None:
    """Each step the run was computed under is its own recorded setting."""

    controller = SimulationController()
    controller.start()

    controller.set_delivered_concentration(0.03)
    _advance_for(controller, 1.0)
    controller.set_delivered_concentration(0.04)

    first, second = controller.snapshot().control_timeline
    assert (first.previous_value, first.new_value) == pytest.approx((0.02, 0.03))
    assert (second.previous_value, second.new_value) == pytest.approx((0.03, 0.04))


def test_consecutive_changes_to_one_control_are_one_adjustment() -> None:
    """One drag of one slider reads as one act, however many steps it spans."""

    controller = SimulationController()
    controller.start()

    controller.set_fresh_gas_flow(3.0)
    _advance_for(controller, 1.0)
    controller.set_fresh_gas_flow(2.0)

    timeline = controller.snapshot().control_timeline
    assert {change.adjustment for change in timeline} == {1}


def test_a_declared_boundary_separates_two_drags_of_one_control() -> None:
    """Timing cannot separate them; the input boundary can.

    Two turns of the same dial arrive as a run of changes to one control,
    exactly as one turn does. Only the interface knows where the first
    gesture ended, and `begin_control_adjustment` is how it says so.
    """

    controller = SimulationController()
    controller.start()

    controller.set_fresh_gas_flow(3.0)
    _advance_for(controller, 60.0)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(2.0)

    first, second = controller.snapshot().control_timeline
    assert first.adjustment == 1
    assert second.adjustment == 2


def test_changing_a_different_control_starts_a_new_adjustment() -> None:
    controller = SimulationController()

    controller.set_fresh_gas_flow(3.0)
    controller.set_cardiac_output(4.0)

    first, second = controller.snapshot().control_timeline
    assert first.adjustment == 1
    assert second.adjustment == 2


def test_reset_clears_the_control_timeline_with_the_run() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, 1.0)
    controller.set_fresh_gas_flow(3.0)

    controller.reset()

    assert controller.snapshot().control_timeline == ()


def test_reset_restarts_adjustment_numbering() -> None:
    """A run's adjustments are numbered from its own beginning.

    Carrying the count across a reset would make the first adjustment of a
    fresh run read as the fourth of something the reader cannot see.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(3.0)
    controller.set_cardiac_output(4.0)

    controller.reset()
    controller.set_fresh_gas_flow(2.0)

    (change,) = controller.snapshot().control_timeline
    assert change.adjustment == 1


def test_changing_agent_clears_the_control_timeline() -> None:
    """A new agent is a new run, and the old run's inputs are not its own."""

    controller = SimulationController()
    controller.set_fresh_gas_flow(3.0)

    controller.set_agent("isoflurane")

    assert controller.snapshot().control_timeline == ()


def test_the_constructor_overrides_are_not_recorded_as_changes() -> None:
    """Initial conditions are what the run starts from, not inputs to it."""

    controller = SimulationController(fresh_gas_flow_l_min=3.0, cardiac_output_l_min=4.0)

    assert controller.snapshot().control_timeline == ()


def test_a_recorded_change_is_stamped_with_the_instant_it_took_effect() -> None:
    """The mark belongs at the instant the run changed, and it is drawn there.

    The chart rules its control mark at `elapsed_s`, and `PL-2FM6` makes
    that instant a column of the drawn window as well - so the mark and the
    kink in the trace beneath it are the same instant by construction
    rather than by two reads agreeing.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, 2.0)

    controller.set_cardiac_output(4.0)

    (change,) = controller.snapshot().control_timeline
    elapsed_s = controller.snapshot().elapsed_s

    assert change.elapsed_s == pytest.approx(elapsed_s)
    _advance_for(controller, 2.0)
    window = controller.drawn_window(0.0, controller.snapshot().elapsed_s, 150)
    assert change.elapsed_s in window.times_s


def test_a_run_nobody_has_touched_holds_nothing_to_discard() -> None:
    """The state a fresh session leaves, and the state `reset()` returns to.

    `SimulationSnapshot.has_recorded_run` is what lets the interface tell a
    destructive agent change from a harmless one, so the two ends of it are
    pinned rather than left to a caller's reading.
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
    time, and it is part of the case a reader set up; a check reading only
    the clock would call this run empty and discard it without asking.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(2.0)

    snapshot = controller.snapshot()
    assert snapshot.elapsed_s == 0.0
    assert snapshot.control_timeline != ()
    assert snapshot.has_recorded_run is True


def test_reset_returns_a_run_to_holding_nothing_to_discard() -> None:
    """Reset is the way to make an agent change cost nothing.

    Not incidental: it is what a reader who wants a different agent and does
    not want their case is told to do, so it has to actually clear both
    halves of the predicate.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_fresh_gas_flow(2.0)
    controller.reset()

    assert controller.snapshot().has_recorded_run is False


def test_set_agent_leaves_a_new_run_holding_nothing_to_discard() -> None:
    """A switch that has just been paid for must not immediately re-arm.

    Confirming a new case and then re-opening the selector would otherwise
    ask about a case with nothing in it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_agent("desflurane")

    assert controller.snapshot().has_recorded_run is False


# --- Stopping at the supported run length (PL-Y5WR) --------------------------


def test_stopping_at_the_supported_run_length_is_not_a_failure() -> None:
    """Three stopped states, and the snapshot has to tell them apart.

    A pause, a failure and the supported run length all leave `is_running`
    false, and only the middle one means anything on screen is untrustworthy.
    The interface reads these two fields to decide what to say, so a run that
    stopped correctly reporting `failure_reason` would put "simulation error"
    over a sound model (`docs/MODEL.md`, "Supported run length").
    """

    controller = SimulationController()
    controller.start()
    controller.advance(0.1)
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert controller.has_reached_supported_limit is True
    assert snapshot.supported_limit_reason == "reached 86400 s of simulated time"
    assert controller.has_failed is False
    assert snapshot.failure_reason is None


def test_a_session_at_the_supported_run_length_cannot_be_resumed() -> None:
    """Start would be refused by the core on its first tick.

    Raising rather than quietly declining, for the reason a failed session
    does: a Start that silently does nothing is a control presenting itself
    as working. The message says which of the two states it is, so the
    refusal a caller reports is not a guess.
    """

    controller = SimulationController()
    controller.start()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        controller.start()

    assert controller.snapshot().is_running is False


def test_the_first_supported_limit_reason_is_the_one_kept() -> None:
    """A later tick reaching the same boundary must not overwrite it."""

    controller = SimulationController()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")
    controller.halt_at_supported_limit("reached 86400 s again")

    assert controller.snapshot().supported_limit_reason == "reached 86400 s of simulated time"


def test_reset_clears_the_supported_limit_and_restores_a_startable_session() -> None:
    """Reset is the only way out, so it has to actually be one."""

    controller = SimulationController()
    controller.start()
    controller.advance(0.1)
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


# `PL-T691`: the controller holds the run as its settings over time as well as
# as recorded samples, and the two must describe the same run. The tests below
# hold the closed form to the recorded path it is meant to replace, end to end
# through the controller's own setters rather than against the core directly.
# `PL-2FM6` is what removes the recorded half; until it lands, this agreement
# is the strongest check available, because a divergence in either path fails
# it.

CLOSED_FORM_AGREEMENT = 1e-13
"""How far the closed form may sit from the recorded run, as a fraction of 1 atm.

Measured 2026-09-07 over the 120 s run below - 1 201 samples, six
compartments each, largest fraction reached 0.0205 - the worst disagreement
is 6.7e-16, which is about three units in the last place of the values being
compared. Pinned two orders above that so an ordinary floating-point wobble
does not fail the suite, and nine orders below the 1e-4 a two-decimal percent
readout can show so a real divergence still does.
"""


def _run_with_two_changes(controller: SimulationController) -> None:
    """Drive 120 s through the controller, moving two controls on the way."""

    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.set_delivered_concentration(0.04)
    _advance_for(controller, duration_s=30.0)
    controller.set_alveolar_ventilation(6.0)
    _advance_for(controller, duration_s=60.0)


def test_a_setting_change_opens_a_segment_where_the_run_saw_it() -> None:
    """The score's segments and the timeline's entries describe one run.

    They are separate records on purpose - one is what the model integrated,
    the other is what a reader is shown - so what has to be checked is that
    they agree about when the run changed.
    """

    controller = SimulationController()
    _run_with_two_changes(controller)

    timeline = controller.snapshot().control_timeline
    openings = [segment.opening.elapsed_s for segment in controller.score_segments]

    assert [change.elapsed_s for change in timeline] == openings[1:]
    assert openings[0] == 0.0


def test_a_refused_setting_leaves_the_score_describing_the_run() -> None:
    """A setting the core rejects never took effect, so it opens no segment.

    The same property the control timeline has, for the same reason: the core
    raises before anything is recorded, and the run it left untouched is the
    one both records describe.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_concentration(0.5)

    assert len(controller.score_segments) == 1
    assert controller.snapshot().control_timeline == ()


def test_resetting_starts_the_score_over() -> None:
    """`reset()` destroys the run, so nothing of its score may survive it."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.reset()

    assert len(controller.score_segments) == 1
    assert controller.drawn_window(0.0, 0.0, 150).times_s == (0.0,)
    # The axis outlives the run it was showing, and is clipped to nothing.
    assert controller.drawn_window(0.0, 60.0, 150).times_s == (0.0,)


def test_changing_agent_starts_the_score_over() -> None:
    """`set_agent` begins a new run, and a score is of one run only."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.set_agent("desflurane")

    assert len(controller.score_segments) == 1
    assert controller.drawn_window(0.0, 60.0, 150).times_s == (0.0,)


def test_a_paused_run_s_score_stops_where_the_run_did() -> None:
    """Pausing stops the run, so it stops what the score will answer for."""

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.pause()
    _advance_for(controller, duration_s=10.0)

    elapsed_s = controller.snapshot().elapsed_s

    # The axis may reach past a paused run; the trace stops where the run
    # did rather than being extended into a prediction.
    window = controller.drawn_window(0.0, elapsed_s + MAXIMUM_SIMULATION_STEP_S, 150)

    assert window.times_s[-1] == pytest.approx(elapsed_s)


def test_the_drawn_window_is_clipped_to_the_run_not_to_the_axis() -> None:
    """The axis reaches past the run by design; the trace must not.

    `following_window` keeps empty axis to the right of the newest instant
    and `fitted_window` returns the chosen rung's full width however short
    the run, both so a trace's slope means the same thing at every moment.
    So the drawn range ends where the run does, and says so in `times_s`
    rather than being padded to the axis.
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

    `PL-4RBD`'s guarantee, delivered structurally: the columns are evaluated
    rather than selected, so the event is a column instead of a sample the
    decimation had to be persuaded to keep.
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
    """F_A/F_I is a quotient of two states, so it is not read as one."""

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    window = controller.drawn_window(0.0, 10.0, 150)
    agent_id = controller.snapshot().agent_id

    with pytest.raises(SimulationConfigurationError, match="not a compartment state"):
        window.compartment_fractions(RecordedSeries(agent_id, RecordedQuantity.WASH_IN_RATIO))


def test_wash_in_is_formed_per_drawn_column() -> None:
    """The ratio is a property of the instant plotted, not of a recorded sample.

    Every drawn instant gets a quotient, and a run that has just started
    carries both the opening stretch with no quotient at all and the wash-in
    that follows it - so the boundary between them falls on a column the
    chart plots rather than on a sample it might not have selected.
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
    """A window before the run began is empty rather than an error.

    It is an ordinary state at the very start of a run, and an empty window
    draws nothing - which is correct, and is not the same as drawing a zero.
    """

    controller = SimulationController()
    controller.start()

    window = controller.drawn_window(60.0, 960.0, 150)

    assert window.times_s == ()
    assert window.states == ()


def test_a_control_change_is_drawn_at_every_time_base_the_reader_can_select() -> None:
    """`PL-4RBD`: a dial change that leaves the trace rising is still a drawn point.

    The defect this closes was a property of selecting recorded extremes:
    turned down, the kink was a local maximum and was drawn; turned up
    mid-rise the trace kept rising, the kink was interior to a bucket, and
    the polyline went straight through the one instant a reader was looking
    for. Re-measured 2026-09-08 at the shipped time bases, that reached
    0.65 pp on the alveolar trace at the 12 h base - 0.32 MAC.

    Evaluating columns removes it at every width rather than at the widths
    somebody remembered to check, which is why this walks the whole ladder:
    the event is a column because it is an event, not because the spacing
    happened to land on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=60.0)
    # Turned *up* mid-rise: the case a selection of extremes could not reach.
    controller.set_delivered_concentration(0.04)
    change_s = controller.snapshot().elapsed_s
    _advance_for(controller, duration_s=60.0)

    elapsed_s = controller.snapshot().elapsed_s

    for time_base in TIME_BASE_LADDER:
        window = controller.drawn_window(0.0, time_base.span_s, 150)

        assert change_s in window.times_s, (
            f"the dial change at {change_s} s is not drawn at the {time_base.span_s} s time base"
        )
        assert window.times_s[-1] == pytest.approx(min(time_base.span_s, elapsed_s))
