"""The simulation controller, driven against real runs.

These tests cover the run definition and the drawn window it supplies.

`controller_support.py` holds what several of these files share.
"""

from collections.abc import Callable

import pytest

from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.controller import BranchedCase, RunSettings, RunStatus, SimulationController
from anesthesia_sim.app.run_series import RecordedQuantity, RecordedSeries
from anesthesia_sim.app.wash_in import is_wash_in
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationExecutionError
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from tests.integration.controller.controller_support import (
    COMPARTMENT_SNAPSHOT_FIELDS,
    _advance_for,
    _run_with_two_changes,
    _trunk_with_two_changes,
    _with_stale_tissue_flows,
    _with_the_tissue_fractions_put_back,
)

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
