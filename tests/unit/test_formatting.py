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
    MAC_AXIS_STEP_LADDER_MAC,
    MAC_DISPLAY_DECIMALS,
    MAC_DISPLAY_RESOLUTION_MAC,
    MAC_UNIT_SUFFIX,
    MAX_MAC_AXIS_INTERVALS,
    format_delivered_label,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_subtitle,
    mac_axis_ticks,
    mac_multiple,
)
from anesthesia_sim.app_metadata import APP_VERSION
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters


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


def test_the_mac_resolution_is_derived_from_the_percent_resolution() -> None:
    """One stated resolution has to govern both display units.

    A MAC multiple is a percent divided by the agent's own `mac_percent`,
    so the percent resolution already fixes how finely the quotient is
    known. `docs/MODEL.md` § "Displayed precision" therefore *derives*
    `MAC_DISPLAY_DECIMALS` rather than choosing it: the finest power of
    ten that is nowhere finer than the percent resolution converted into
    MAC. Deriving it a second time independently would mean re-deriving
    two numbers whenever the first is re-measured, which is what
    `PL-X9KD` is about to do to the percent side.

    This re-runs that arithmetic against every shipped agent, so adding
    an agent, or changing the percent resolution, fails here rather than
    silently over-claiming on the display. The binding agent today is
    isoflurane: 0.01 percentage points of a 1.2% MAC is 0.0083 MAC, and
    0.01 is the finest power of ten at or above it.
    """

    coarsest_supported = max(
        CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / load_agent_parameters(agent_id).mac_percent
        for agent_id in AGENT_DATA_FILENAMES
    )

    assert MAC_DISPLAY_RESOLUTION_MAC >= coarsest_supported, (
        "the MAC readout resolves finer than the percent it is derived from"
    )
    assert MAC_DISPLAY_RESOLUTION_MAC / 10.0 < coarsest_supported, (
        "a finer power of ten would still not over-claim; the derivation has drifted"
    )
    assert MAC_DISPLAY_DECIMALS == 2
    assert MAC_DISPLAY_RESOLUTION_MAC == pytest.approx(0.01)


def test_no_mac_readout_claims_more_than_the_percent_beside_it() -> None:
    """The two units are read side by side, so neither may out-claim the other.

    The property is the one the derivation above exists to guarantee,
    stated in the terms a reader meets it in: for every shipped agent, one
    count of the MAC line is at least one count of the percent line above
    it. Where that failed, a reader could watch the MAC digit move while
    the percent digit stood still and conclude the model resolved
    something it does not.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        mac_percent = load_agent_parameters(agent_id).mac_percent
        one_mac_count_in_percentage_points = MAC_DISPLAY_RESOLUTION_MAC * mac_percent

        assert one_mac_count_in_percentage_points >= CONCENTRATION_DISPLAY_RESOLUTION_PERCENT, (
            f"{agent_id}: the MAC line resolves finer than the percent line"
        )


def test_one_mac_of_every_agent_reads_as_one() -> None:
    """The unit's defining case, on the three agents that ship.

    This is the whole reason for the second unit: the same clinical depth
    reads as the same number whichever agent is running, where the percent
    line reads 2.00%, 1.20% and 6.00% for the identical situation.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        mac_percent = load_agent_parameters(agent_id).mac_percent

        assert mac_multiple(mac_percent / 100.0, mac_percent) == pytest.approx(1.0)
        assert format_mac_multiple(mac_percent / 100.0, mac_percent) == "1.00 ×MAC"


def test_format_mac_multiple_carries_the_multiplication_sign() -> None:
    """`0.80 MAC` reads as a depth; `0.80 ×MAC` reads as a ratio.

    The sign is the display-side half of `docs/MODEL.md` § "MAC multiples
    as a display unit": on the four non-alveolar compartments the number
    is a partial-pressure ratio and asserts nothing about anesthetic
    depth, and the two readings are indistinguishable if the unit is
    written as a bare "MAC".
    """

    assert MAC_UNIT_SUFFIX == " ×MAC"
    assert format_mac_multiple(0.016, 2.0) == "0.80 ×MAC"
    assert format_mac_multiple(0.0, 2.0) == "0.00 ×MAC"
    assert format_mac_multiple(0.04, 2.0) == "2.00 ×MAC"


def test_format_mac_multiple_marks_a_value_below_the_resolution() -> None:
    """A filling compartment must not read as an empty one, in either unit.

    The below-resolution form matters more in MAC than in percent, not
    less: 0.01 MAC is 0.02 percentage points of sevoflurane and 0.06 of
    desflurane, so a compartment clears the MAC line's last digit later
    than it clears the percent readout beside it. `0.00 ×MAC` under a
    percent line already showing the compartment filling would be the two
    readouts contradicting each other.
    """

    expected = f"<{MAC_DISPLAY_RESOLUTION_MAC:.{MAC_DISPLAY_DECIMALS}f}{MAC_UNIT_SUFFIX}"

    # 0.015% of desflurane: above the percent resolution, below the MAC one.
    assert format_percent(0.00015) == "0.01%"
    assert format_mac_multiple(0.00015, 6.0) == expected
    assert format_mac_multiple(1e-9, 2.0) == expected


def test_format_mac_multiple_leaves_an_impossible_negative_visible() -> None:
    """A negative is an upstream defect and must stay legible as one.

    Same rule as `format_percent`, for the same reason: the compartment
    guards make a negative unreachable, so one arriving here must not be
    absorbed into the plausible-looking below-resolution form.
    """

    assert format_mac_multiple(-0.02, 2.0).startswith("-")
    assert not format_mac_multiple(-1e-9, 2.0).startswith("<")


def test_a_non_positive_mac_refuses_to_produce_a_number() -> None:
    """`CLAUDE.md` requires an obvious failure over a plausible value.

    A zero or negative divisor cannot produce a meaningful multiple. The
    loader's `PositivePercent` makes one unreachable from a shipped data
    file, so one arriving here means something upstream is wrong and the
    display must not carry on regardless.
    """

    for bad_mac in (0.0, -2.0):
        with pytest.raises(ValueError, match="strictly positive"):
            mac_multiple(0.02, bad_mac)

        with pytest.raises(ValueError, match="strictly positive"):
            format_mac_multiple(0.02, bad_mac)

        with pytest.raises(ValueError, match="strictly positive"):
            mac_axis_ticks(8.0, bad_mac)


def test_mac_axis_ticks_land_on_round_mac_values_inside_the_plotted_range() -> None:
    """The axis exists so a reader can find 1 MAC, not so it can find 2%.

    Each tick is returned as the percent position it occupies, because the
    chart plots percent and the MAC axis is a relabelling of that same
    coordinate rather than a second set of points. A tick above the top of
    the range would be drawn outside the plotted area.
    """

    ticks = mac_axis_ticks(8.0, 2.0)

    assert [label for _, label in ticks] == [
        "0.0",
        "0.5",
        "1.0",
        "1.5",
        "2.0",
        "2.5",
        "3.0",
        "3.5",
        "4.0",
    ]
    assert [percent for percent, _ in ticks] == pytest.approx(
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    )

    for percent, label in ticks:
        assert 0.0 <= percent <= 8.0
        assert percent == pytest.approx(float(label) * 2.0)


def test_every_shipped_agent_gets_the_same_mac_axis_spacing() -> None:
    """One mental scale has to survive an agent change.

    The three vaporizer maxima span 5% to 18%, which is 3.0 to 4.2 MAC —
    close enough that the ladder gives all three a half-MAC step. That is
    what makes the cross-agent comparison the second unit exists for
    actually readable: the gridline a reader learns under sevoflurane
    means the same thing under desflurane.
    """

    spacings = set()

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        ticks = mac_axis_ticks(agent.max_delivered_concentration_percent, agent.mac_percent)
        labels = [float(label) for _, label in ticks]

        assert labels[0] == 0.0
        assert len(labels) >= 2
        spacings.add(round(labels[1] - labels[0], 6))

    assert spacings == {0.5}


def test_the_mac_axis_coarsens_rather_than_crowding_a_wide_range() -> None:
    """The spacing is a function of the range, not a constant.

    `MAX_MAC_AXIS_INTERVALS` is the ceiling; the ladder supplies the
    steps. A fixed step would put sixty labels on a wide axis, which is
    an unreadable axis rather than a precise one.
    """

    for max_percent, expected_step in (
        (1.0, 0.25),
        (8.0, 0.5),
        (18.0, 1.0),
        (25.0, 2.0),
        (45.0, 5.0),
    ):
        ticks = mac_axis_ticks(max_percent, 2.0)
        labels = [float(label) for _, label in ticks]

        assert len(ticks) - 1 <= MAX_MAC_AXIS_INTERVALS
        assert round(labels[1] - labels[0], 6) == expected_step
        assert expected_step in MAC_AXIS_STEP_LADDER_MAC


def test_the_mac_axis_is_unlabelled_rather_than_invented_for_an_empty_range() -> None:
    """No plotted range means no scale to label, and none is guessed."""

    assert mac_axis_ticks(0.0, 2.0) == ()
    assert mac_axis_ticks(-1.0, 2.0) == ()


def test_format_mac_reference_states_the_divisor_the_readouts_used() -> None:
    """The one free parameter of the second unit, named on the display.

    `CLAUDE.md` requires a clinically meaningful displayed value to be
    traceable to the transformation that produced it. A MAC multiple has
    exactly one, so naming it beside the axis is what lets a reader who
    disagrees with the divisor see that they disagree — and convert back.
    """

    assert format_mac_reference("Sevoflurane", 2.0) == "1 MAC sevoflurane = 2.0%"
    assert format_mac_reference("Desflurane", 6.0) == "1 MAC desflurane = 6.0%"

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        reference = format_mac_reference(agent.display_name, agent.mac_percent)

        assert agent.display_name.lower() in reference
        assert f"{agent.mac_percent:.1f}%" in reference
