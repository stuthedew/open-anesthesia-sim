"""The simulation controller, driven against real runs.

These tests cover the preview of a dragged setting: the settings a run would
continue under if the dragged value were applied now, and the states it would
then pass through.

`controller_support.py` holds what several of these files share.
"""

import dataclasses
from collections.abc import Callable

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import PreviewOfAnotherCase, SettingPreview, SimulationController
from anesthesia_sim.app.run_series import RecordedQuantity, RecordedSeries
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import load_reference_adult_parameters
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from tests.integration.controller.controller_support import _advance_for

AGENT = "isoflurane"


def _isoflurane_run_off_its_defaults() -> SimulationController:
    """A paused 60 s isoflurane run on four settings that are not the data files' defaults.

    The data files give a 6.0 L circuit, 4.0 L/min of fresh gas, 4.0 L/min of
    alveolar ventilation and 5.0 L/min of cardiac output, and sevoflurane is
    the default agent. Each value here differs from its default and from the
    other three. So a preview that took any of them from the data files
    rather than from the run would predict another case.
    """

    run = SimulationController(
        agent_id=AGENT,
        circuit_volume_l=CompartmentVolume(4.5),
        fresh_gas_flow_l_min=FreshGasFlow(2.5),
        alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        cardiac_output_l_min=CardiacOutput(6.5),
    )
    run.start()
    _advance_for(run, duration_s=60)
    run.pause()

    return run


_APPLIED_SETTINGS: tuple[
    tuple[ControlInput, float, Callable[[SimulationController], None]], ...
] = (
    (ControlInput.FRESH_GAS_FLOW, 6.0, lambda run: run.set_fresh_gas_flow(FreshGasFlow(6.0))),
    (
        ControlInput.DELIVERED,
        3.0,
        lambda run: run.set_delivered_concentration_percent(Percent(3.0)),
    ),
    (
        ControlInput.ALVEOLAR_VENTILATION,
        7.0,
        lambda run: run.set_alveolar_ventilation(AlveolarVentilation(7.0)),
    ),
    (ControlInput.CARDIAC_OUTPUT, 3.5, lambda run: run.set_cardiac_output(CardiacOutput(3.5))),
)
"""Each control, a value to drag it to, and the setter that applies that value."""


@pytest.mark.parametrize(
    ("control", "value", "apply"),
    _APPLIED_SETTINGS,
    ids=[control.value for control, _, _ in _APPLIED_SETTINGS],
)
def test_a_preview_gives_the_settings_that_applying_its_value_would_give(
    control: ControlInput, value: float, apply: Callable[[SimulationController], None]
) -> None:
    """The settings a preview predicts under are the ones the run would step under once applied.

    A user dragging a slider sees the course the run would take at the
    dragged value. The expected settings come from a twin run with the same
    history, which really applies the value through its setter. A cardiac
    output preview must also change every tissue blood flow, as applying it
    does. The run being previewed keeps its own settings, because a preview
    applies nothing.
    """

    run = _isoflurane_run_off_its_defaults()
    twin = _isoflurane_run_off_its_defaults()
    segments_before = run.run_segments
    apply(twin)
    applied = twin.run_segments[-1].settings

    # The test is of a value that differs from the setting in force.
    assert applied != segments_before[-1].settings

    assert run.preview_settings(SettingPreview(control, value)) == applied
    assert run.run_segments == segments_before


def test_a_preview_of_a_run_whose_patient_file_changed_is_refused_naming_each_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A preview rebuilt with a patient other than the run's is refused, and names each difference.

    The preview rebuilds the run from its settings and re-reads the patient
    from the data file. Here the file is edited after the run was built, so
    the rebuilt patient's muscle and fat volumes differ from the run's. A
    preview drawn anyway would show the course of another patient as if it
    were this one's. The refusal's message is for the user holding the dial,
    and names the dial (`PL-412F`). Its note names each value that differs
    once, with both of its values, so a developer can find the edit. Each
    entry names the preview, which opens no branch (`PL-VYN4`).
    """

    run = _isoflurane_run_off_its_defaults()
    on_file = load_reference_adult_parameters()
    edited = dataclasses.replace(
        on_file,
        muscle_volume_l=CompartmentVolume(on_file.muscle_volume_l + 1.0),
        fat_volume_l=CompartmentVolume(on_file.fat_volume_l + 2.0),
    )
    monkeypatch.setattr(uptake_system, "load_reference_adult_parameters", lambda: edited)

    with pytest.raises(PreviewOfAnotherCase) as refusal:
        run.preview_settings(SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0))

    assert str(refusal.value) == (
        "the fresh gas flow preview would not start from the values this run holds, so "
        "it would predict a different case. The simulator's data may have changed since "
        "this run began, or the simulator may have a fault. Reopen the simulator and run "
        "the case again to preview a setting. If this notice comes back, the cause is a "
        "fault in the simulator"
    )
    (note,) = refusal.value.__notes__
    reason, _, named = note.partition(": ")
    differences = named.split("; ")

    assert reason == (
        "a preview would be drawn from values this run does not hold, "
        "so it would predict a different case"
    )
    assert differences == [
        f"muscle volume_l is {on_file.muscle_volume_l!r} in this run and "
        f"{edited.muscle_volume_l!r} in the preview",
        f"fat volume_l is {on_file.fat_volume_l!r} in this run and "
        f"{edited.fat_volume_l!r} in the preview",
    ]


def test_a_preview_on_an_axis_whose_columns_are_a_second_apart_is_drawn_at_every_second() -> None:
    """A prediction is drawn on the run's own grid, so a one-second grid draws every second.

    The axis runs from 0 s to 120 s in 150 columns, so its columns would be
    less than a second apart and are drawn one second apart. The run has
    reached 60 s, so the prediction starts there and ends at the axis's right
    edge. The run, once it got there, would be drawn at each of those seconds,
    and the prediction is drawn by the same rule so that the two meet
    (`drawn_window`).
    """

    run = _isoflurane_run_off_its_defaults()

    window = run.preview_window(SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0), 0.0, 120.0, 150)

    assert window.times_s == tuple(range(60, 121))


def test_a_run_on_an_axis_of_zero_width_is_drawn_at_that_one_second() -> None:
    """An axis of zero width is one instant, and the run is drawn there alone (`PL-WZDM`).

    At 30 s the run holds a state, so that one second is drawn. At 30.5 s it
    holds none, because a run stands only on whole seconds, so nothing is.
    """

    run = _isoflurane_run_off_its_defaults()

    assert run.drawn_window(30.0, 30.0, 150).times_s == (30,)
    assert run.drawn_window(30.5, 30.5, 150).times_s == ()


def test_a_preview_toward_an_axis_of_zero_width_is_drawn_at_every_second_up_to_it() -> None:
    """A prediction toward an axis of zero width is drawn one second apart (`PL-WZDM`).

    The run has reached 60 s and the axis is the one instant 70 s. Its grid
    spacing is one second, so the prediction is drawn at each second from the
    reach to 70 s, as the run would be drawn there.
    """

    run = _isoflurane_run_off_its_defaults()

    window = run.preview_window(SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0), 70.0, 70.0, 150)

    assert window.times_s == tuple(range(60, 71))


def test_a_preview_on_an_axis_that_ends_at_the_reach_is_an_empty_window_of_the_run_s_agent() -> (
    None
):
    """A prediction with no second to draw is empty, and is still bound to the run's agent.

    The run has reached 60 s and the axis ends there, so nothing lies ahead
    to predict. The empty window is read like any other, so asking it for
    the run's own agent's trace gives no points rather than a refusal.
    """

    run = _isoflurane_run_off_its_defaults()

    window = run.preview_window(SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0), 0.0, 60.0, 150)

    assert window.times_s == ()
    assert window.substance_id == AGENT
    assert window.compartment_fractions(RecordedSeries(AGENT, RecordedQuantity.ALVEOLAR)) == []
