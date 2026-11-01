"""Tests of the drawn window that `app/run_series.py` hands the chart, run without a GUI."""

import re
from math import inf

import pytest

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.run_series import DrawnWindow, RecordedQuantity, RecordedSeries
from anesthesia_sim.core.exceptions import SimulationConfigurationError


def test_a_window_refusing_the_wash_in_ratio_names_a_method_that_forms_it() -> None:
    """The error message names a method that `DrawnWindow` really has (`PL-756M`).

    The message used to name `wash_in_readings`, which no module defines. So a
    reader looking for where F_A/F_I is computed was sent to code that does not
    exist. The test does not take the expected name from a copy of the message.
    Instead, it checks each method that the message names against the class itself.
    """

    window = DrawnWindow("sevoflurane", (), ())

    with pytest.raises(SimulationConfigurationError) as refusal:
        window.compartment_fractions(RecordedSeries("sevoflurane", RecordedQuantity.WASH_IN_RATIO))

    message = str(refusal.value)
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
        DrawnWindow(window.substance_id, times_s, window.states)
