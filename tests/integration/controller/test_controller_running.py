"""The simulation controller, driven against real runs.

These tests cover pausing, the drawn window, resetting, and a failed step.

`controller_support.py` holds what several of these files share.
"""

import dataclasses
from collections.abc import Callable

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    RecordedQuantity,
    RecordedSeries,
)
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.run_definition import RunSegment
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from tests.integration.controller.controller_support import _advance_for


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
    run that was built and stepped the same way but never stopped. The test
    runs once for each `ControlInput`, so a control added without a setter
    here, or without the refusal, fails it.
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
        match=f"^the {_NAMED[control]} setting cannot be changed on a stopped run, because no step",
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
