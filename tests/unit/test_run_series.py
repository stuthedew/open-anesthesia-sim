"""Tests of the drawn window that `app/run_series.py` hands the chart, run without a GUI."""

import re
from math import inf

import pytest

from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import SettingPreview, SimulationController
from anesthesia_sim.app.run_series import DrawnWindow, RecordedQuantity, RecordedSeries
from anesthesia_sim.app.wash_in import wash_in_ratio
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import ALVEOLAR_FRACTION, INSPIRED_FRACTION
from anesthesia_sim.core.supported_ranges import AlveolarVentilation


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


def _taking_up_sevoflurane(seconds: int) -> SimulationController:
    """Return a run that has taken up 4% sevoflurane for `seconds` at the default settings."""

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(4.0))
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

    expected = [
        wash_in_ratio(state[ALVEOLAR_FRACTION], state[INSPIRED_FRACTION]) for state in window.states
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

    controller = _taking_up_sevoflurane(60)
    running = controller.snapshot().alveolar_ventilation_l_min
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

    controller = _taking_up_sevoflurane(300)
    running = controller.snapshot().alveolar_ventilation_l_min
    window = controller.preview_window(
        SettingPreview(ControlInput.ALVEOLAR_VENTILATION, 0.0), 0.0, 900.0, 30
    )
    quotients = window.wash_in_quotients("sevoflurane")

    assert window.times_s[0] == 300
    assert window.alveolar_ventilations_l_min == (running,) + (0.0,) * (len(window.times_s) - 1)
    assert quotients[0] is not None
    assert quotients[1:] == [None] * (len(window.times_s) - 1)
