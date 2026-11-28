"""Tests of the drawn window that `app/run_series.py` hands the chart, run without a GUI."""

import re
from math import inf

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import BranchedCase, SettingPreview, SimulationController
from anesthesia_sim.app.run_series import (
    COMPARTMENT_NAMES,
    COMPARTMENT_QUANTITIES,
    DrawnWindow,
    RecordedQuantity,
    RecordedSeries,
)
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import ALVEOLAR_FRACTION, INSPIRED_FRACTION
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant

#: An alveolar ventilation that differs from the reference patient's default,
#: so that a test which sets it can tell its own setting from the default.
SET_VENTILATION_L_MIN = 3.0


def test_a_window_refusing_the_wash_in_ratio_names_a_method_that_forms_it() -> None:
    """The error message names a method that `DrawnWindow` really has (`PL-756M`).

    The message used to name `wash_in_readings`, which no module defines. So a
    reader looking for where F_A/F_I is computed was sent to code that does not
    exist. The test does not take the expected name from a copy of the message.
    Instead, it checks each method that the message names against the class itself.
    """

    window = DrawnWindow("sevoflurane", (), (), ())

    with pytest.raises(SimulationConfigurationError) as refusal:
        window.compartment_fractions(RecordedSeries("sevoflurane", RecordedQuantity.WASH_IN_RATIO))

    message = str(refusal.value)
    # regex: the message is prose, and only a backticked identifier can name a
    # method, so backticked text that is not an identifier is left out.
    named = re.findall(r"`(\w+)`", message)

    assert named, f"the refusal names no method: {message!r}"
    assert all(callable(getattr(DrawnWindow, name, None)) for name in named), message
    assert message.endswith(f"`{named[-1]}` is what forms it"), message


@pytest.mark.parametrize("instant_s", [float("nan"), inf, -inf], ids=["nan", "inf", "-inf"])
def test_a_window_refuses_an_instant_that_is_not_finite(instant_s: float) -> None:
    """Every drawn instant is finite, so the chart may skip pyqtgraph's own scan (`PL-TCNT`).

    `app/qt_chart.py` draws every curve with `skipFiniteCheck`, and pyqtgraph
    leaves the result undefined for a non-finite coordinate. Every drawn
    instant passes through the window, for a run and for a preview alike.
    So the window is where such an instant is rejected.
    """

    window = SimulationController().drawn_window(0.0, 0.0, 2)
    times_s = (instant_s, *window.times_s[1:])

    with pytest.raises(
        SimulationConfigurationError,
        match=rf"^a drawn window holds the instant {instant_s} s, which is not finite",
    ):
        DrawnWindow(window.substance_id, times_s, window.states, window.alveolar_ventilations_l_min)


def _taking_up_sevoflurane(
    seconds: int, alveolar_ventilation_l_min: float | None = None
) -> SimulationController:
    """Return a run that has taken up 4% sevoflurane for `seconds`.

    The alveolar ventilation is the default unless `alveolar_ventilation_l_min`
    is given. The other settings are the defaults.
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(4.0))
    if alveolar_ventilation_l_min is not None:
        controller.set_alveolar_ventilation(AlveolarVentilation(alveolar_ventilation_l_min))
    controller.start()

    while controller.snapshot().elapsed_s < seconds:
        controller.advance()

    return controller


def test_a_window_refuses_a_ventilation_count_that_differs_from_its_instants() -> None:
    """Each drawn instant carries the ventilation of the step that reached it, and only one."""

    window = _taking_up_sevoflurane(60).drawn_window(0.0, 60.0, 4)

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^a drawn window has {len(window.times_s)} instants and "
            rf"{len(window.times_s) - 1} alveolar ventilations; each instant needs "
        ),
    ):
        DrawnWindow(
            window.substance_id,
            window.times_s,
            window.states,
            window.alveolar_ventilations_l_min[1:],
        )


def test_a_state_reached_at_zero_ventilation_gives_no_quotient() -> None:
    """The F_A/F_I plot draws nothing at a state a step at zero ventilation reached (`PL-49D5`).

    The expected quotients are divided here from the window's own fractions,
    and the column left without one is the one this test set to zero.
    """

    # The window starts after agent has reached the circuit, so every
    # ventilated column has a quotient.
    window = _taking_up_sevoflurane(120).drawn_window(30.0, 120.0, 4)
    ventilations = list(window.alveolar_ventilations_l_min)
    ventilations[2] = AlveolarVentilation(0.0)
    stopped = DrawnWindow(window.substance_id, window.times_s, window.states, tuple(ventilations))

    expected: list[float | None] = [
        state[ALVEOLAR_FRACTION] / state[INSPIRED_FRACTION] for state in window.states
    ]
    expected[2] = None

    assert all(ratio is not None for index, ratio in enumerate(expected) if index != 2)
    assert stopped.wash_in_quotients("sevoflurane") == expected


def test_each_column_carries_the_ventilation_of_the_step_that_reached_it() -> None:
    """At the second ventilation stops, the state was reached with ventilation running.

    The run takes up sevoflurane at the default ventilation to 60 s, runs at
    zero ventilation to 90 s, and at 5 L/min to 120 s. The expected values are
    the settings this test made, second by second.
    """

    running = SET_VENTILATION_L_MIN
    controller = _taking_up_sevoflurane(60, running)
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))

    while controller.snapshot().elapsed_s < 90:
        controller.advance()

    controller.set_alveolar_ventilation(AlveolarVentilation(5.0))

    while controller.snapshot().elapsed_s < 120:
        controller.advance()

    window = controller.drawn_window(0.0, 120.0, 120)
    expected = tuple(
        running if second <= 60 else 0.0 if second <= 90 else 5.0 for second in range(121)
    )

    assert window.times_s == tuple(range(121))
    assert window.alveolar_ventilations_l_min == expected
    assert controller.snapshot().reaching_alveolar_ventilation_l_min == 5.0


def test_a_preview_of_zero_ventilation_gives_no_quotient_after_the_reach() -> None:
    """A predicted state that a step at zero ventilation would reach has no ratio to draw.

    The first column is the run's own state at its reach, which the run
    reached with ventilation running, so it keeps its quotient.
    """

    running = SET_VENTILATION_L_MIN
    controller = _taking_up_sevoflurane(300, running)
    window = controller.preview_window(
        SettingPreview(ControlInput.ALVEOLAR_VENTILATION, 0.0), 0.0, 900.0, 30
    )
    quotients = window.wash_in_quotients("sevoflurane")

    assert window.times_s[0] == 300
    assert window.alveolar_ventilations_l_min == (running,) + (0.0,) * (len(window.times_s) - 1)
    assert quotients[0] is not None
    assert quotients[1:] == [None] * (len(window.times_s) - 1)


def _stopped_from(stop_s: int, reach_s: int) -> SimulationController:
    """Return a run at the set ventilation to `stop_s`, then at zero ventilation to `reach_s`."""

    controller = _taking_up_sevoflurane(stop_s, SET_VENTILATION_L_MIN)
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))

    while controller.snapshot().elapsed_s < reach_s:
        controller.advance()

    return controller


def test_a_preview_that_restores_ventilation_draws_no_ratio_at_a_reach_reached_in_apnoea() -> None:
    """The reach keeps the ventilation that reached it, whatever the preview sets.

    The run stops ventilating at 300 s and reaches 360 s in apnoea. A preview of
    ventilation restored to the set value starts at that reach, so its first
    second has no ratio and every later second has one. The grid is one second
    wide, so the second after the reach is drawn too.
    """

    controller = _stopped_from(300, 360)
    window = controller.preview_window(
        SettingPreview(ControlInput.ALVEOLAR_VENTILATION, SET_VENTILATION_L_MIN), 360.0, 420.0, 60
    )
    quotients = window.wash_in_quotients("sevoflurane")

    assert window.times_s == tuple(range(360, 421))
    assert window.alveolar_ventilations_l_min == (0.0,) + (SET_VENTILATION_L_MIN,) * 60
    assert quotients[0] is None
    assert None not in quotients[1:]


def test_a_preview_after_ventilation_stops_at_the_reach_keeps_the_reach_s_ratio() -> None:
    """Stopping ventilation at the second the run has reached does not change how it was reached.

    The run reaches 300 s ventilated, and ventilation is then set to zero
    without a step. The state at 300 s was reached with ventilation running,
    so the preview's first second keeps its ratio, and the predicted seconds
    after it have none.
    """

    controller = _taking_up_sevoflurane(300, SET_VENTILATION_L_MIN)
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    window = controller.preview_window(
        SettingPreview(ControlInput.ALVEOLAR_VENTILATION, 0.0), 300.0, 360.0, 60
    )
    quotients = window.wash_in_quotients("sevoflurane")

    assert window.times_s == tuple(range(300, 361))
    assert window.alveolar_ventilations_l_min == (SET_VENTILATION_L_MIN,) + (0.0,) * 60
    assert quotients[0] is not None
    assert quotients[1:] == [None] * 60


def test_a_branch_keeps_the_ventilation_that_reached_its_fork() -> None:
    """A branch draws its fork's ratio by the ventilation the trunk reached that second with.

    The trunk stops ventilating at 600 s and reaches 700 s in apnoea. A branch
    opened at 650 s, in apnoea, has no ratio at its fork. A branch opened at
    600 s keeps the ratio there, because the trunk reached 600 s ventilated,
    even after the branch sets zero ventilation at its fork.
    """

    case = BranchedCase(_stopped_from(600, 700))
    in_apnoea = case.fork_at(CaseInstant(650))
    at_the_stop = case.fork_at(CaseInstant(600))
    at_the_stop.set_alveolar_ventilation(AlveolarVentilation(0.0))

    assert in_apnoea.drawn_window(650.0, 650.0, 2).wash_in_quotients("sevoflurane") == [None]
    assert at_the_stop.drawn_window(600.0, 600.0, 2).wash_in_quotients("sevoflurane") != [None]
    assert in_apnoea.snapshot().reaching_alveolar_ventilation_l_min == 0.0
    assert at_the_stop.snapshot().reaching_alveolar_ventilation_l_min == SET_VENTILATION_L_MIN


def test_a_coarse_preview_draws_the_restored_ratio_from_its_first_ventilated_second() -> None:
    """The search for a trace's lowest point forms no ratio at a reach reached in apnoea.

    The run reaches 360 s in apnoea, and the preview restores ventilation. The
    restored ratio is lowest at 361 s, the first second a ventilated step
    reaches, and rises after it. The chart's columns are a minute apart, so
    361 s is drawn only because it is the trace's lowest point. A search that
    formed a ratio at the apnoeic reach would take that ratio as the trace's
    first value and drop 361 s, so the trace would start later and higher.
    """

    controller = _stopped_from(300, 360)
    window = controller.preview_window(
        SettingPreview(ControlInput.ALVEOLAR_VENTILATION, SET_VENTILATION_L_MIN), 0.0, 3600.0, 60
    )
    quotients = window.wash_in_quotients("sevoflurane")
    first_restored = quotients[1]

    assert window.times_s[:2] == (360, 361)
    assert quotients[0] is None
    assert first_restored is not None
    assert all(ratio is not None and ratio > first_restored for ratio in quotients[2:])


def test_every_compartment_has_one_on_screen_name_in_the_order_the_interface_lists_them() -> None:
    """`PL-5867`: the legend, the mark editor and a refused mark's notice read one name each."""

    assert tuple(COMPARTMENT_NAMES) == COMPARTMENT_QUANTITIES
