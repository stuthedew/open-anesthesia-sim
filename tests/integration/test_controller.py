import dataclasses

import pytest

from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlInput
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    RecordedQuantity,
    RecordedSeries,
)
from anesthesia_sim.app.wash_in import is_wash_in
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.governing_equations import DELIVERED_AGENT_L, EXHAUSTED_AGENT_L
from anesthesia_sim.core.parameters import load_reference_adult_parameters
from anesthesia_sim.core.run_definition import RunDefinition, RunSegment
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

    Clamping produced a run whose every displayed value came from a dial
    position the caller never asked for, which is indistinguishable on
    screen from one they did.
    """

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        SimulationController(agent_id="isoflurane", delivered_partial_pressure_fraction=0.08)


def test_setting_a_delivered_concentration_above_the_agent_max_is_rejected() -> None:
    """Regression (PL-015): the setter path is bounded by the same guard.

    Before the fix only the UI slider bounded this value, so any non-UI
    caller could simulate 50% isoflurane on a 5% vaporizer.
    """

    controller = SimulationController(agent_id="isoflurane")

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        controller.set_delivered_partial_pressure_fraction(0.50)

    snapshot = controller.snapshot()

    assert snapshot.max_delivered_concentration_percent == 5.0
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.012)


def test_delivered_concentration_exactly_at_the_agent_max_is_accepted() -> None:
    """The boundary is inclusive: 5.0% is a real isoflurane dial position."""

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_partial_pressure_fraction(0.05)

    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.05)


def test_delivered_concentration_can_be_turned_off() -> None:
    """Zero is always deliverable: it is the vaporizer off, which is how
    washout begins.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.set_delivered_partial_pressure_fraction(0.0)

    assert controller.snapshot().delivered_partial_pressure_fraction == 0.0


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

    controller = SimulationController(
        agent_id="sevoflurane", delivered_partial_pressure_fraction=0.08
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
    """Circuit, flow, ventilation, and cardiac output carry over; the
    delivered concentration resets to the new agent's own 1 MAC instead
    (see test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac).
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=5.0,
        fresh_gas_flow_l_min=3.0,
        delivered_partial_pressure_fraction=0.03,
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
    assert snapshot.delivered_partial_pressure_fraction == pytest.approx(0.06)
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

        if isinstance(value, RunSegment):
            total += 1
        elif isinstance(value, tuple | list):
            total += sum(1 for item in value if isinstance(item, RunSegment))

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
    assert drawn(RecordedQuantity.CIRCUIT) == pytest.approx(
        snapshot.inspired_partial_pressure_fraction
    )
    assert drawn(RecordedQuantity.ALVEOLAR) == pytest.approx(
        snapshot.alveolar_partial_pressure_fraction
    )
    assert drawn(RecordedQuantity.FAT) == pytest.approx(snapshot.fat_partial_pressure_fraction)


def test_each_drawn_quantity_reads_the_state_of_the_compartment_it_names() -> None:
    """The same pairing, audited against the state vector the chart draws from.

    `COMPARTMENT_STATE_INDEX` is what `_build_history_sample` was once the
    chart evaluates the run definition instead of reading recorded samples
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
        RecordedQuantity.CIRCUIT: system.circuit.inspired_partial_pressure_fraction,
        RecordedQuantity.ALVEOLAR: system.alveoli.partial_pressure_fraction,
        RecordedQuantity.MIXED_VENOUS: system.patient.mixed_venous_partial_pressure_fraction,
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

    controller.set_fresh_gas_flow(3.0)
    controller.set_delivered_partial_pressure_fraction(0.06)

    after = controller.snapshot()

    assert after.elapsed_s == before.elapsed_s
    assert after.stored_agent_l == pytest.approx(before.stored_agent_l)
    assert after.fresh_gas_flow_l_min == 3.0
    assert after.delivered_partial_pressure_fraction == 0.06
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
        controller.set_delivered_partial_pressure_fraction(0.50)

    after = controller.snapshot()

    assert after.failure_reason is None
    assert after.is_running is True
    assert after.delivered_partial_pressure_fraction == before.delivered_partial_pressure_fraction


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
        blood_gas_partition_coefficient=original.blood_gas_partition_coefficient,
        tissue_gas_partition_coefficient=original.tissue_gas_partition_coefficient,
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
    controller.set_delivered_partial_pressure_fraction(0.03)
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
    controller.set_delivered_partial_pressure_fraction(0.03)
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

    controller.set_delivered_partial_pressure_fraction(0.03)

    (change,) = controller.snapshot().control_timeline
    assert change.new_value == pytest.approx(0.03)
    assert change.new_value == pytest.approx(
        controller.snapshot().delivered_partial_pressure_fraction
    )


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
        controller.set_delivered_partial_pressure_fraction(0.5)

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

    controller.set_delivered_partial_pressure_fraction(0.03)
    controller.set_delivered_partial_pressure_fraction(0.04)

    (change,) = controller.snapshot().control_timeline
    assert change.previous_value == pytest.approx(0.02)
    assert change.new_value == pytest.approx(0.04)
    assert change.elapsed_s == pytest.approx(1.0)


def test_a_change_undone_within_one_step_leaves_no_entry() -> None:
    """Returning to the step's own value means the model saw no change."""

    controller = SimulationController()

    controller.set_delivered_partial_pressure_fraction(0.03)
    controller.set_delivered_partial_pressure_fraction(0.02)

    assert controller.snapshot().control_timeline == ()


def test_the_same_control_changed_across_two_steps_records_both() -> None:
    """Each step the run was computed under is its own recorded setting."""

    controller = SimulationController()
    controller.start()

    controller.set_delivered_partial_pressure_fraction(0.03)
    _advance_for(controller, 1.0)
    controller.set_delivered_partial_pressure_fraction(0.04)

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


def _advance_through_halts(controller: SimulationController, duration_s: float) -> None:
    """Advance `duration_s`, resuming wherever a marked crossing halts the run.

    A marked run halts on the step that crosses one of its marks (`PL-CTD7`),
    which is an ordinary pause. A driver that did not resume would leave a
    marked run standing at its first crossing while an unmarked one ran on,
    so the two would differ by where the marks were rather than by anything
    the model computed. Unmarked runs never halt, so this is `_advance_for`
    for every caller that has no marks.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        if not controller.is_running:
            controller.start()

        controller.advance(MAXIMUM_SIMULATION_STEP_S)


def _run_with_two_changes(controller: SimulationController) -> None:
    """Drive 120 s through the controller, moving two controls on the way."""

    controller.start()
    _advance_through_halts(controller, duration_s=30.0)
    controller.set_delivered_partial_pressure_fraction(0.04)
    _advance_through_halts(controller, duration_s=30.0)
    controller.set_alveolar_ventilation(6.0)
    _advance_through_halts(controller, duration_s=60.0)


def test_a_setting_change_opens_a_segment_where_the_run_saw_it() -> None:
    """The run definition's segments and the timeline's entries describe one run.

    They are separate records on purpose - one is what the model integrated,
    the other is what a reader is shown - so what has to be checked is that
    they agree about when the run changed.
    """

    controller = SimulationController()
    _run_with_two_changes(controller)

    timeline = controller.snapshot().control_timeline
    openings = [segment.opening.instant_s for segment in controller.run_segments]

    assert [change.elapsed_s for change in timeline] == openings[1:]
    assert openings[0] == 0.0


def test_a_refused_setting_leaves_the_run_definition_describing_the_run() -> None:
    """A setting the core rejects never took effect, so it opens no segment.

    The same property the control timeline has, for the same reason: the core
    raises before anything is recorded, and the run it left untouched is the
    one both records describe.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    with pytest.raises(SimulationConfigurationError):
        controller.set_delivered_partial_pressure_fraction(0.5)

    assert len(controller.run_segments) == 1
    assert controller.snapshot().control_timeline == ()


def test_resetting_starts_the_run_definition_over() -> None:
    """`reset()` destroys the run, so nothing of its definition may survive it."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.reset()

    assert len(controller.run_segments) == 1
    assert controller.drawn_window(0.0, 0.0, 150).times_s == (0.0,)
    # The axis outlives the run it was showing, and is clipped to nothing.
    assert controller.drawn_window(0.0, 60.0, 150).times_s == (0.0,)


def test_changing_agent_starts_the_run_definition_over() -> None:
    """`set_agent` begins a new run, and a run definition is of one run only."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.set_agent("desflurane")

    assert len(controller.run_segments) == 1
    assert controller.drawn_window(0.0, 60.0, 150).times_s == (0.0,)


def test_a_paused_run_s_definition_stops_where_the_run_did() -> None:
    """Pausing stops the run, so it stops what the run definition will answer for."""

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


def test_an_axis_entirely_before_a_branch_s_fork_draws_nothing() -> None:
    """The other half of the same ordinary state, and the one a branch reaches.

    A branch holds no state before the instant it was forked at, and since
    `PL-ZMRT` its run definition refuses such an instant rather than answering
    from the nearest keyframe it happens to hold. So the window is clipped to
    the run's opening and comes back empty where the axis ends to the left of
    it - not raised out of the render loop, which is what clipping to a literal
    zero instead of to the opening would have caused on an ordinary frame.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    window = branch.drawn_window(0.0, fork_s / 2, 150)

    assert window.times_s == ()
    assert window.states == ()

    # And the trunk, on the same axis, draws it: the two differ because the
    # branch did not exist yet, not because the axis was rejected.
    assert trunk.drawn_window(0.0, fork_s / 2, 150).times_s != ()


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
    controller.set_delivered_partial_pressure_fraction(0.04)
    change_s = controller.snapshot().elapsed_s
    _advance_for(controller, duration_s=60.0)

    elapsed_s = controller.snapshot().elapsed_s

    for time_base in TIME_BASE_LADDER:
        window = controller.drawn_window(0.0, time_base.span_s, 150)

        assert change_s in window.times_s, (
            f"the dial change at {change_s} s is not drawn at the {time_base.span_s} s time base"
        )
        assert window.times_s[-1] == pytest.approx(min(time_base.span_s, elapsed_s))


# `PL-J2TD`: a fork resumes into a live run. The tests below hold the seam
# between a canonical keyframe state and a running system - what a branch opens
# at, what its clock reads, and what it refuses - end to end through the
# controller, because the two records a branch has to keep agreeing are only
# both present here.

COMPARTMENT_SNAPSHOT_FIELDS = (
    "inspired_partial_pressure_fraction",
    "alveolar_partial_pressure_fraction",
    "mixed_venous_partial_pressure_fraction",
    "vessel_rich_partial_pressure_fraction",
    "muscle_partial_pressure_fraction",
    "fat_partial_pressure_fraction",
)
"""The six compartment fractions a snapshot carries, named as the snapshot names them.

Written out rather than derived from `COMPARTMENT_QUANTITIES`, because that
tuple is keyed by the quantity the *chart* draws and one of its names differs
from the snapshot's: the circuit's drawn quantity is `circuit` while the field
is `inspired_partial_pressure_fraction`, since the state is named for the
clinical quantity and the container is still the circuit.
"""

BRANCH_AGREEMENT = 1e-14
"""How far a branch's live state may sit from its parent's, in fractions of 1 atm.

The two reach the same instant by different routes: the parent steps the whole
way from induction, while the branch is stood at a keyframe the canonical path
computed and steps only from there. `docs/MODEL.md` § "Closed-form agreement
test" is what governs that comparison, and stating the bound in fractions of
one atmosphere rather than relatively is its reasoning - a relative bound would
tighten without limit on the near-zero fat fraction of a 120 s run and say
nothing about a displayed digit.

Measured 2026-09-14 on the run below: the worst disagreement across all six
compartments is 2.7e-16, about one unit in the last place, and the two
cumulative accumulators agree to 1.6e-15 L. Pinned two orders above that so an
ordinary floating-point wobble does not fail the suite, and ten orders below
the 1e-4 that a two-decimal percent readout can show so a real divergence
still does.
"""


def _trunk_with_two_changes() -> SimulationController:
    """A 120 s sevoflurane run carrying two setting changes, so it holds three keyframes."""

    controller = SimulationController()
    _run_with_two_changes(controller)
    controller.pause()

    return controller


def test_a_fork_opens_at_a_keyframe_on_the_case_s_own_axis() -> None:
    """The item's own deliverable, in one test.

    A branch opens at a canonical keyframe state of another run, and both its
    clock and its definition stand at the instant it was forked from, because a
    branch is one patient's case under a second management and uptake is a
    function of time since induction. The two are asserted together because
    their agreement is the property `PL-ZMRT` bought: while the definition
    opened at a zero of its own, a branch carried two time frames and every
    reader had to know which one it was holding.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s

    branch = trunk.resumed_at(fork_s)

    # The clock is the case's: the branch stands at the fork instant, not at zero.
    assert branch.snapshot().elapsed_s == fork_s

    # And so is the definition, which opens *at* the keyframe it carries.
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

    # The opening does not move, and the reach follows the clock exactly: after
    # `PL-ZMRT` those are one quantity rather than two related by an offset, so
    # asserting their equality is asserting that no frame conversion is left.
    assert branch.run_segments[0].opening.instant_s == fork_s
    assert branch._run_definition.reached_s == branch.snapshot().elapsed_s


def test_a_branch_continues_the_case_s_step_count_so_the_envelope_is_the_case_s() -> None:
    """The 24 h supported run length is the patient's, not each branch's.

    `require_supported_run_length` reads a step count, so a branch restarting
    that count would be handed a fresh envelope - a fork taken late could then
    be advanced well past the span `docs/MODEL.md` § "Supported run length"
    declares, in the regime `core/supported_ranges.py` argues the omitted
    metabolism dominates, with every guard passing. Continuing the parent's
    count is what makes the envelope the case's, and it needs no second guard.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s

    branch = trunk.resumed_at(fork_s)

    assert branch._state.step_count == round(fork_s / MAXIMUM_SIMULATION_STEP_S)
    assert branch._state.simulation_step_s == MAXIMUM_SIMULATION_STEP_S
    assert branch.snapshot().elapsed_s == fork_s


def test_a_branch_reproduces_its_parent_at_every_instant_they_share() -> None:
    """`ROADMAP.md` item 12, element-wise rather than within a tolerance.

    The parent is advanced past the fork and the branch the same way, and
    every instant they share must agree entry for entry on the canonical path.
    The instants probed are the case's own - a whole number of steps times the
    step, which is the only way simulated time is ever formed here - and both
    runs are asked for each one directly. There is nothing to convert: since
    `PL-ZMRT` the branch's definition opens at the fork on that same axis, so
    parent and child form their intervals from the identical pair of floats.
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

    A definition opening at a zero of its own is the arrangement `PL-ZMRT`
    replaced, and it was not wrong so much as conditional: it reproduced the
    parent exactly *provided* every caller reached it by subtracting the fork
    instant, and silently did not when a caller named the branch's own elapsed
    time instead. The difference is real because the subtraction does not
    round-trip - with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
    9.999999974752427e-07 and not 1e-6 - so the two routes are exact solutions
    of the same equations composed in different orders, and `PL-Z3W6` requires
    sameness of the composition rather than of the solution.

    Measured on the run below, over the 601 case instants the branch and its
    parent share: the shipped branch, asked for the case's own instants, agrees
    with its parent at every one, while a definition opened at its own zero and
    asked for `steps * step` differs at **354 of them**. The second run is
    built here rather than obtained from the controller, because the controller
    can no longer produce one - which is the point.

    It fails honestly if the two ever coincide, which would mean the hazard had
    stopped existing and this test had stopped saying anything.
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
        fork_segment.settings, fork_segment.opening.state, opened_at_s=0.0
    )
    on_its_own_axis.advance_to(60.0)

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
    """The live path agrees too, which is the half a canonical comparison cannot see.

    The parent stepped from induction to 120 s; the branch was stood at the
    60 s keyframe and stepped from there. At the same case instant the two must
    describe one patient - which is the whole claim a comparison of two
    managements rests on, because everything before the fork has to be the same
    history rather than a reproduction of it.
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
    """The chart reads one time axis whichever run fills it.

    `drawn_window` takes the axis the caller has set and returns the instants
    it drew, and both are the case's time on a branch as on a trunk - there is
    no second frame for either to be in since `PL-ZMRT`. A window that came
    back measured from the fork would draw a correct trace at the wrong place
    on a labelled axis, which `CLAUDE.md`'s safety-critical standard counts as
    a presentation failure rather than a lesser kind.

    This passes a left edge below the branch's fork deliberately: it is what
    exercises the clamp in `drawn_window`, which clips to the run's own
    opening rather than to zero. Clipping to zero would ask the definition for
    an instant before the branch existed, which it refuses, so an ordinary
    frame on a branch would raise out of the render loop.
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
    """What one time frame buys the chart, which is why `PL-2R2C` needed no fix.

    `RunDefinition.evaluate_anchored` lays its grid on absolute multiples of
    the spacing measured in the definition's own frame - deliberately, because
    a grid anchored to the window instead makes every drawn point a new instant
    on every frame, which `PL-Q197` measured as what saturated the client. While
    a branch's definition opened at a zero of its own, that put its columns at
    `fork + m x spacing` against the trunk's `m x spacing`: on this 13-column
    120 s axis, with the fork deliberately off the grid at 55.3 s, 2 of the
    branch's 8 columns landed where the trunk also drew. A learner could not
    then read "at this instant the trunk was here and the branch was there" off
    matched points, and any difference trace or shared tooltip built on the
    assumption would be wrong rather than coarse.

    One frame makes them coincide with nothing added to the display path: both
    definitions are on the case's axis, so both grids are the same multiples.
    The fork instant itself is a column on the trunk because it is a setting
    change, and the branch's first column because it is where the branch opens.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=55.3)
    trunk.set_delivered_partial_pressure_fraction(0.04)
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

    # The fork is deliberately not a multiple of the 10 s spacing: where it is
    # one, the two grids coincide whatever frame the branch is in, and the test
    # would pass without saying anything.
    assert fork_s % ((stop_s - 0.0) / 12) != 0.0

    assert set(branch_columns) <= set(trunk_columns), (
        "the branch is drawn at instants the trunk never draws, so the two "
        "traces cannot be read against each other"
    )
    assert len(branch_columns) > 2

    # The axis reaches to the left of the fork; the branch's window is clipped
    # at its opening rather than refused, and starts exactly there.
    assert branch_columns[0] == fork_s
    assert branch_columns[-1] == trunk_columns[-1]


def test_a_control_moved_before_a_branch_steps_reopens_its_first_segment() -> None:
    """The learner's actual first act on a branch, which is to change something.

    `RunDefinition.record_change` replaces the open segment's settings in place
    where the run has not advanced past that segment's own opening, rather than
    recording a zero-length stretch nothing was ever computed under. That test
    is an equality between the run's reach and its first keyframe's instant,
    and on a branch both of those are now the fork instant where they used to
    be zero - so it is worth asserting rather than reading, since a version
    that seeded only one of the two would open a zero-length segment here and
    the run would still look right.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)

    assert len(branch.run_segments) == 1

    branch.set_delivered_partial_pressure_fraction(0.01)

    assert len(branch.run_segments) == 1
    assert branch.run_segments[0].opening.instant_s == fork_s
    assert branch.run_segments[0].opening.state == trunk.run_segments[-1].opening.state

    # And the new settings are the ones the run is then computed under.
    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.pause()

    assert branch.run_segments[0].settings.delivered_partial_pressure_fraction == 0.01
    assert len(branch.run_segments) == 1


def test_a_branch_carries_the_case_s_delivered_and_exhausted_totals() -> None:
    """The litres a branch reports are the patient's, not the branch's own.

    A branch restarting them at zero would report a mass-balance readout that
    is correct about the branch and wrong about the patient, at the instant a
    learner is most likely to compare two managements by how much agent each
    used.
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

    The pre-branch history belongs to the trunk and is not reproduced here;
    what a branch carries forward is the *state* that history produced.
    """

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)

    assert branch.snapshot().control_timeline == ()
    assert trunk.snapshot().control_timeline != ()


def test_a_branch_inherits_its_parent_s_settings_at_the_fork() -> None:
    """Replayed from the recorded timeline, then checked against the segment.

    The check is the point: a branch that assembled a system matrix its parent
    never used would diverge from its first step, inside the tolerance that
    holds the two records together and reported by nothing.
    """

    trunk = _trunk_with_two_changes()

    for segment in trunk.run_segments:
        branch = trunk.resumed_at(segment.opening.instant_s)

        assert branch._state.uptake_system.equation_settings() == segment.settings


def test_a_branch_can_open_at_any_keyframe_the_run_holds() -> None:
    """Every recorded setting change is a branch point, and so is the run's start."""

    trunk = _trunk_with_two_changes()

    for segment in trunk.run_segments:
        branch = trunk.resumed_at(segment.opening.instant_s)

        assert branch.run_segments[0].opening.instant_s == segment.opening.instant_s
        assert branch.run_segments[0].opening.state == segment.opening.state


def test_an_instant_between_keyframes_is_refused_rather_than_approximated() -> None:
    """`docs/MODEL.md` § "The canonical evaluation rule", enforced at the seam.

    Opening between two keyframes would replace one propagation over an
    interval with two over its halves - a different rounding of the same exact
    solution - and `PL-Z3W6` requires element-wise reproduction rather than
    agreement within a tolerance. The refusal names the keyframes the run does
    hold, so a caller can pick one.
    """

    trunk = _trunk_with_two_changes()
    between_s = trunk.run_segments[-1].opening.instant_s + 5.0

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        trunk.resumed_at(between_s)


def test_an_instant_the_run_never_reached_is_refused() -> None:
    """A branch of a run that has not happened would be a prediction drawn as a run."""

    trunk = _trunk_with_two_changes()

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        trunk.resumed_at(trunk.snapshot().elapsed_s + 600.0)


def test_a_non_finite_fork_instant_is_refused() -> None:
    """Named separately from the keyframe refusal, which would be the wrong reason."""

    trunk = _trunk_with_two_changes()

    with pytest.raises(SimulationConfigurationError, match="finite instant"):
        trunk.resumed_at(float("inf"))


def test_a_branch_of_a_branch_is_refused_rather_than_silently_flattened() -> None:
    """`PL-TFX5`'s shape: one trunk with N branches, and sub-forks deliberately out.

    They multiply without bound and buy little over re-branching from the
    trunk, and that is the whole of the reason. It once also rested on a
    branch's keyframes being its definition's own, so that an instant handed
    to this on a branch meant something other than the same number handed to
    the trunk; `PL-ZMRT` retired that - every run's instants are the case's
    now - and `SimulationController.resumed_at` states the surviving reason
    alone. A guard defended by an argument that has stopped being true is one
    a later reader removes.
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
    """A branch's beginning is the fork; the case's induction is not a state it holds.

    Clearing to an empty system would stand the patient at no agent at a case
    time the model says they are loaded - a plausible state that never
    happened.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = trunk.resumed_at(fork_s)
    at_fork = branch.snapshot()

    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.set_fresh_gas_flow(1.0)
    branch.reset()

    after = branch.snapshot()

    assert after.elapsed_s == fork_s
    assert after.control_timeline == ()
    assert branch.run_segments[0].opening.state == trunk.run_segments[-1].opening.state

    for field in COMPARTMENT_SNAPSHOT_FIELDS:
        assert getattr(after, field) == getattr(at_fork, field)


def test_a_branch_is_the_agent_and_patient_its_parent_was() -> None:
    """`PL-TFX5`: a branch that could change either would be a second case."""

    trunk = SimulationController(agent_id="desflurane", cardiac_output_l_min=3.8)
    _run_with_two_changes(trunk)
    trunk.pause()

    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    at_fork = branch.snapshot()

    assert at_fork.agent_id == "desflurane"
    assert at_fork.cardiac_output_l_min == trunk.snapshot().cardiac_output_l_min
    assert at_fork.circuit_volume_l == trunk.snapshot().circuit_volume_l


"""`PL-TFX5`: a case is one trunk and the branches taken from it, held flat.

The clause `SimulationController.resumed_at` cannot carry on its own. It makes
one branch and hands it back detached, so two calls produce two controllers
that each know the instant they opened at and none of which knows the others
exist. `BranchedCase` is what makes them one case, and what makes the flat
shape structural: the trunk is the only run it will fork, so a sub-fork is not
an operation to decline.
"""


def test_a_case_forks_at_every_instant_the_trunk_offers() -> None:
    """`PL-TFX5`'s first clause: any recorded control event is a branch point.

    `fork_points_s` is the run's keyframes, which are its opening and every
    setting change the model was actually stepped under - so this asserts the
    two agree as well as that each one forks, because a fork point list that
    quietly omitted one would still pass a test that only walked the list.
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
    """The comparison the milestone is named for, so nothing makes a point unique.

    Coast against hold, from the same instant: two branches at one fork point
    are the normal case rather than a duplicate to reject, and they must be
    separately managed once taken.
    """

    case = BranchedCase(_trunk_with_two_changes())
    fork_s = case.fork_points_s[-1]

    coasting = case.fork_at(fork_s)
    holding = case.fork_at(fork_s)

    assert case.branches == (coasting, holding)
    assert coasting is not holding

    coasting.set_fresh_gas_flow(0.5)
    holding.set_fresh_gas_flow(6.0)

    assert coasting.snapshot().fresh_gas_flow_l_min == 0.5
    assert holding.snapshot().fresh_gas_flow_l_min == 6.0


def test_forking_a_case_repeatedly_leaves_the_trunk_where_it_was() -> None:
    """`PL-TFX5`'s third clause, against the whole of `fork_points_s`.

    The trunk surviving is what separates a comparison from an undo. It is
    checked after every branch has been advanced and re-dialled, because a
    branch sharing a compartment with its parent would show nothing until
    something moved.
    """

    case = BranchedCase(_trunk_with_two_changes())
    before = case.trunk.snapshot()
    segments_before = case.trunk.run_segments

    for elapsed_s in case.fork_points_s:
        branch = case.fork_at(elapsed_s)
        branch.set_cardiac_output(2.5)
        branch.start()
        _advance_for(branch, duration_s=30.0)
        branch.pause()

    assert case.trunk.snapshot() == before
    assert case.trunk.run_segments == segments_before
    assert case.trunk.run_segments[0].opening.instant_s == 0.0
    assert case.trunk.opened_from is None


def test_a_case_cannot_be_rooted_in_a_branch() -> None:
    """`PL-TFX5`'s fourth clause, as an interface that cannot state a sub-fork.

    `resumed_at` refuses a branch of a branch and keeps doing so - that is the
    guard for a caller holding two controllers. This is the other half: a case
    built on a branch would offer `fork_at` over a second generation, so it is
    refused at construction rather than at the fork.
    """

    trunk = _trunk_with_two_changes()
    branch = BranchedCase(trunk).fork_at(trunk.run_segments[-1].opening.instant_s)

    with pytest.raises(SimulationConfigurationError, match="branches of branches are excluded"):
        BranchedCase(branch)


def test_a_case_refuses_a_fork_at_an_instant_the_trunk_holds_no_keyframe_for() -> None:
    """The refusal reaches through the case rather than being softened by it."""

    case = BranchedCase(_trunk_with_two_changes())
    between_s = (case.fork_points_s[-2] + case.fork_points_s[-1]) / 2.0

    assert between_s not in case.fork_points_s

    with pytest.raises(SimulationConfigurationError, match="holds no keyframe"):
        case.fork_at(between_s)

    assert case.branches == ()


def test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork() -> None:
    """`PL-TFX5`'s last clause, against a patient value that moves during the run.

    Cardiac output is the one patient quantity a control can move, so it is
    the only one that distinguishes "the branch carries its parent's patient"
    from "the branch rebuilds the same reference patient from the same data
    file". A run that never moves it asserts the second while reading like the
    first, because `_setting_at` then falls through to the value in force now.
    So this moves it mid-run and forks *before* the move: the branch must carry
    the value the case was computed under at the fork, which is no longer the
    value the trunk is standing at.
    """

    trunk = SimulationController(agent_id="isoflurane", cardiac_output_l_min=4.2)
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.set_cardiac_output(6.5)
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

    `set_agent` begins a new run, and `_build_state` clears `opened_from` with
    everything else - so without this refusal a branch becomes a trunk in
    silence, `reset()` stops returning it to its fork, `resumed_at` accepts it,
    and the case it was taken from goes on listing it. The trunk is unaffected:
    changing the case's agent is still the explicit new case it always was.
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

    "A run can be forked at any recorded control event" binds two records that
    collapse redundant changes by different rules, so it holds only while those
    rules agree. `RunDefinition.record_change` compares whole settings against
    the previous stretch and is order-independent; the control timeline
    compares one entry, and used to compare only the newest one.

    Two dials nudged and both put back **interleaved** - F up, C up, F back, C
    back - is what separated them: each move's predecessor was the other
    control, so no collapse fired, and four entries stood at an instant the run
    never changed at while the definition correctly held no keyframe there. The
    nested order collapsed to nothing, so the defect was order-dependent and
    invisible to a test that moved two controls once each. A learner reaches it
    while paused, where `advance()` is a no-op and every control they touch
    carries one instant.

    Asserted as the property rather than as the repair: every stamp the reader
    is shown is an instant the run holds a keyframe for, and `resumed_at`
    accepts each one.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=30.0)

    opening = trunk.snapshot()
    trunk.pause()

    trunk.set_fresh_gas_flow(opening.fresh_gas_flow_l_min + 1.0)
    trunk.set_cardiac_output(opening.cardiac_output_l_min + 1.0)
    trunk.set_fresh_gas_flow(opening.fresh_gas_flow_l_min)
    trunk.set_cardiac_output(opening.cardiac_output_l_min)

    timeline = trunk.snapshot().control_timeline
    openings = [segment.opening.instant_s for segment in trunk.run_segments]

    # Nothing the model saw differs, so neither record has anything to say.
    assert [change.elapsed_s for change in timeline] == openings[1:]
    assert openings == [0.0]

    # And the general property, on a run that does change: every stamp a reader
    # is shown is a fork point, which is what the clause promises.
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.set_alveolar_ventilation(6.0)
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
# `tests/unit/test_bookmarks.py` holds what a mark refuses. What is here is
# the controller's half: that the collections reach a reader through the
# snapshot, and what happens to them at the three points a run starts over -
# `reset`, `set_agent` and a fork. Each of those three is a decision rather
# than a consequence, so each has a test saying which way it went and why
# (`PL-LPLD`).


def test_a_fresh_run_is_marked_at_nothing() -> None:
    assert SimulationController().snapshot().bookmarks.is_empty


def test_a_mark_reaches_a_reader_through_the_snapshot() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(600.0, "intubation"))
    controller.add_mac_target(MacTarget(RecordedQuantity.VESSEL_RICH, MacMultiple(0.8), "wash-in"))

    marks = controller.snapshot().bookmarks

    assert [bookmark.label for bookmark in marks.time_bookmarks] == ["intubation"]
    assert [target.label for target in marks.mac_targets] == ["wash-in"]


def test_the_two_collections_are_added_to_and_removed_from_independently() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(600.0))
    controller.add_mac_target(MacTarget(RecordedQuantity.FAT, MacMultiple(0.5)))
    controller.remove_time_bookmark(TimeBookmark(600.0))

    marks = controller.snapshot().bookmarks

    assert marks.time_bookmarks == ()
    assert len(marks.mac_targets) == 1


def test_a_snapshot_taken_before_a_mark_was_added_does_not_acquire_it() -> None:
    # The snapshot is a read-only view of one instant, so a panel holding one
    # from an earlier tick must not come to describe a later run.
    controller = SimulationController()
    before = controller.snapshot()
    controller.add_time_bookmark(TimeBookmark(600.0))

    assert before.bookmarks.is_empty
    assert not controller.snapshot().bookmarks.is_empty


def test_a_marked_instant_cannot_be_marked_twice_through_the_controller() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(600.0))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        controller.add_time_bookmark(TimeBookmark(600.0, "and again"))

    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_resetting_a_run_keeps_its_marks() -> None:
    # A reset is for taking the same case again, and it is the same case the
    # learner was asking about - so the marks go with the settings rather than
    # with the state.
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(600.0))
    controller.start()
    _advance_for(controller, duration_s=30.0)
    controller.reset()

    assert controller.snapshot().bookmarks.time_bookmarks == (TimeBookmark(600.0),)


def test_changing_agent_keeps_the_marks_although_it_destroys_the_run() -> None:
    # A MAC target is a multiple of whichever agent is running, so 0.8 x MAC
    # stays 0.8 x MAC of the new agent rather than becoming the old agent's
    # absolute concentration under a new divisor. Reaching the same multiple at
    # a different time is what a learner changing agent is there to see.
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


def test_a_branch_opens_carrying_the_marks_of_the_case_it_continues() -> None:
    # The opposite of the control timeline, and for the opposite reason: the
    # timeline is the record of what was done to a run, and a mark is a
    # question about what is still to come. A comparison is two managements
    # answering one question, so a learner made to re-enter the marks could
    # compare two branches at two different heights with nothing saying so.
    trunk = _trunk_with_two_changes()
    target = MacTarget(RecordedQuantity.MUSCLE, MacMultiple(0.3))
    trunk.add_time_bookmark(TimeBookmark(45.0, "the decision point"))
    trunk.add_mac_target(target)

    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    marks = branch.snapshot().bookmarks

    assert marks.time_bookmarks == (TimeBookmark(45.0, "the decision point"),)
    assert marks.mac_targets == (target,)
    # And the timeline still starts empty, which is the half that does not
    # come across.
    assert branch.snapshot().control_timeline == ()


def test_marking_a_branch_does_not_mark_the_trunk_it_came_from() -> None:
    # Inherited at the fork and not shared afterwards: the two runs are two
    # managements, and a mark added to one is a question asked of that one.
    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.add_time_bookmark(TimeBookmark(600.0))

    assert trunk.snapshot().bookmarks.is_empty
    assert len(branch.snapshot().bookmarks.time_bookmarks) == 1


def test_a_mark_changes_nothing_the_run_computes() -> None:
    # The property that lets a mark be carried across a fork at all, and the
    # one `PL-B8MK` measured the alternative against: recording a keyframe
    # where a run halts moves the trunk's own later answers, and holding a mark
    # in a collection beside the run moves nothing. Element-wise rather than
    # within a tolerance, because that is the claim.
    #
    # It survives `PL-CTD7` unchanged, and the claim is now the stronger one:
    # the marked run below is *stopped twice* on the way through, at 45 s and
    # where the alveolar compartment crosses 0.8 ×MAC, and still computes the
    # same trajectory element-wise. A halt costs the run no simulated time and
    # moves no state - it only declines to take the next step until asked.
    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(45.0))
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
