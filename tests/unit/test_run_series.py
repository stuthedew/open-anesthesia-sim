"""Tests of the drawn window that `app/run_series.py` hands the chart, run without a GUI."""

import re

import pytest

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
