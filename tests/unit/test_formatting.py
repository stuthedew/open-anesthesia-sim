"""Unit tests for `app/formatting.py`, the interface's displayed values.

These are the last transformation between a modeled number and what a
reader sees, so they are tested here directly rather than only through the
dashboard: `docs/MODEL.md` § "Displayed precision" reasons about this
module, and a claim it makes should be checkable against the function it
describes without constructing a Flet interface.

The end-to-end path - real controller, real step, real formatter, the
string on the panel - stays in `tests/unit/test_simulation_view.py`, which
is where a displayed value can be read off the control that carries it.
"""

import pytest

from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    format_delivered_label,
    format_percent,
    format_subtitle,
)
from anesthesia_sim.app_metadata import APP_VERSION


def test_format_percent_uses_the_documented_display_resolution() -> None:
    """Pin the PL-040 decision: 0.01 percentage points, uniformly.

    The resolution is justified in `docs/MODEL.md` § "Displayed precision"
    against the measured splitting error, so a change here is a change to a
    safety-critical claim about what the model can support — not a
    formatting preference. This test exists to make that change deliberate.
    """

    assert CONCENTRATION_DISPLAY_DECIMALS == 2
    assert CONCENTRATION_DISPLAY_RESOLUTION_PERCENT == pytest.approx(0.01)

    assert format_percent(0.0) == "0.00%"
    assert format_percent(1.0) == "100.00%"
    assert format_percent(0.0803456) == "8.03%"
    assert format_percent(0.02) == "2.00%"


def test_format_percent_rounds_rather_than_truncates() -> None:
    """The last displayed digit is the nearest one, not a truncation.

    Truncation would bias every reading downward by up to a full count of
    the uncertain digit, on top of the solver error the resolution is
    already chosen to sit above. Exact ties are not asserted: a decimal
    tie is not generally representable as a double, and the model's own
    error is many orders of magnitude larger than that distinction.
    """

    assert format_percent(0.021_39) == "2.14%"
    assert format_percent(0.021_31) == "2.13%"


def test_format_percent_marks_a_value_below_the_resolution() -> None:
    """A filling compartment must not read as an empty one.

    Muscle and fat sit under 0.01% for the opening minutes of every run.
    Rounding them to `0.00%` would assert the model holds zero there when
    it does not, so a positive value that rounds to zero is shown as below
    the resolution instead.
    """

    assert format_percent(1e-8) == "<0.01%"
    assert format_percent(4.0e-5) == "<0.01%"

    # Exactly zero is the one value that may read as zero: nothing has
    # reached the compartment, which is a fact the model does hold.
    assert format_percent(0.0) == "0.00%"

    # Either side of the rounding threshold, at half the resolution.
    assert format_percent(4.9e-5) == "<0.01%"
    assert format_percent(5.1e-5) == "0.01%"


def test_format_percent_leaves_an_impossible_negative_visible() -> None:
    """A negative fraction cannot occur, and must not be disguised if it does.

    The compartment guards reject a negative amount, so reaching here means
    something upstream is wrong. The below-resolution form would render that
    as an ordinary small positive reading; `CLAUDE.md` requires the obvious
    failure instead.
    """

    assert format_percent(-1e-8) == "-0.00%"
    assert format_percent(-0.02) == "-2.00%"


def test_format_percent_states_the_below_resolution_form_from_the_constant() -> None:
    """The marker must say the resolution the readouts actually use.

    `<0.01%` is not a literal anywhere; it is rendered from
    `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` at
    `CONCENTRATION_DISPLAY_DECIMALS`. A hardcoded marker would keep saying
    `<0.01%` after a resolution change, telling a reader the display
    resolves a digit finer or coarser than it does.
    """

    expected = f"<{CONCENTRATION_DISPLAY_RESOLUTION_PERCENT:.{CONCENTRATION_DISPLAY_DECIMALS}f}%"

    assert format_percent(1e-9) == expected


def test_format_subtitle_names_the_running_model_and_its_version() -> None:
    """The one line tying a displayed value to what produced it.

    `CLAUDE.md` requires a clinically meaningful value to be traceable to
    the model and version behind it, and this subtitle is where the
    interface says both. It is asserted against `APP_VERSION` rather than
    against a literal so that the test cannot pass a stale version.
    """

    assert format_subtitle("Sevoflurane") == f"Version {APP_VERSION} — Sevoflurane patient model"
    assert format_subtitle("Desflurane") == f"Version {APP_VERSION} — Desflurane patient model"


def test_format_delivered_label_names_the_agent_being_delivered() -> None:
    """The vaporizer control must name the agent it is dialling.

    A delivered concentration is meaningless without its agent — 2% is
    a third of a MAC of desflurane and a full MAC of sevoflurane — so the
    label carries the name rather than reading "Delivered agent".
    """

    assert format_delivered_label("Sevoflurane") == "Delivered sevoflurane"
    assert format_delivered_label("Isoflurane") == "Delivered isoflurane"
