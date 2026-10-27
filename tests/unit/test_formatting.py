"""Unit tests for `app/formatting.py`, the interface's displayed values.

The functions in that module are the last step between a modeled number and
what a reader sees. They are therefore tested here directly, not only
through the dashboard. `docs/MODEL.md` § "Displayed precision" reasons about
that module, and each claim it makes should be checkable against the
function it describes without constructing a Flet interface.

The end-to-end path stays in `tests/unit/test_simulation_view.py`. That path
runs the real controller, a real step and the real formatter, and checks the
string on the panel. That file is where a displayed value can be read off
the control that shows it.
"""

import inspect
import math
from decimal import Decimal
from pathlib import Path
from typing import Any, get_type_hints

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from anesthesia_sim.app import formatting as formatting_module
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.formatting import (
    AGENT_AMOUNT_DISPLAY_PRECISION,
    CHART_AXIS_TOP_MAC,
    CHART_GRID_INTERVAL_MAC,
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    MAC_AXIS_STEP_LADDER_MAC,
    MAC_DISPLAY_DECIMALS,
    MAC_DISPLAY_RESOLUTION_MAC,
    MAC_UNIT_SUFFIX,
    MAX_MAC_AXIS_INTERVALS,
    AgentAmount,
    AgentAmountPrecision,
    AgentAmountUnit,
    agent_amount_display_precision,
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_agent_residual,
    format_agent_volume,
    format_branch_discard_warning,
    format_case_discard_warning,
    format_chart_time_label,
    format_delivered_label,
    format_elapsed,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_subtitle,
    format_supported_run_length,
    format_time_base,
    mac_awake_band_percent,
    mac_axis_ticks,
    mac_multiple,
)
from anesthesia_sim.app_metadata import APP_BUILD, APP_BUILD_VERSION, APP_VERSION
from anesthesia_sim.core.concentration import (
    Fraction,
    MacMultiple,
    MacPercent,
    Percent,
    fraction_from_percent,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_format_percent_uses_the_documented_display_resolution() -> None:
    """Pin the PL-040 decision to show every concentration to 0.01 percentage points.

    `docs/MODEL.md` § "Displayed precision" derives the resolution from the
    measured spread of the partition coefficients. This test exists so that a
    change to the resolution is made deliberately.
    `test_concentration_decimals_are_a_choice_within_a_recorded_band` is the
    other half. It says which direction of change requires re-deriving
    something.
    """

    assert CONCENTRATION_DISPLAY_DECIMALS == 2
    assert CONCENTRATION_DISPLAY_RESOLUTION_PERCENT == pytest.approx(0.01)

    assert format_percent(Fraction(0.0)) == "0.00%"
    assert format_percent(Fraction(1.0)) == "100.00%"
    assert format_percent(Fraction(0.0803456)) == "8.03%"
    assert format_percent(Fraction(0.02)) == "2.00%"


def test_concentration_decimals_are_a_choice_within_a_recorded_band() -> None:
    """Two decimals is the owner's pick inside a one-to-two decimal band.

    `docs/MODEL.md` § "Displayed precision" derives the band. The count of
    decimals inside the band is a presentation decision (`PL-88GQ`). The two
    halves fail differently on purpose, and that is the reason to pin the band
    separately from the value:

    - Moving to **one** decimal stays inside the band. That change is the
      project owner's to make, and it re-derives nothing in `core/`. What rules
      it out today is a teaching judgment, not a numerical limit: fat and
      muscle would show a flat `0.0%` for minutes to an hour.
    - Moving to **three** decimals leaves the band. It would claim a
      resolution finer than the measured spread of the partition coefficients
      that produced the number. That is false precision under `CLAUDE.md`'s
      safety standard.

    A session that reads only the constant cannot tell these two cases apart.
    That is why the band is asserted here rather than left in prose.
    """

    minimum_supported_decimals = 1
    maximum_supported_decimals = 2

    assert minimum_supported_decimals <= CONCENTRATION_DISPLAY_DECIMALS
    assert CONCENTRATION_DISPLAY_DECIMALS <= maximum_supported_decimals

    # `PL-X9KD` removed the dependency that ran from this count back into
    # `core/`. The loop below keeps `core/` from naming the constant again. It
    # is only a textual check. An import is the other way the dependency could
    # return, and `tools/import_boundary_check.py` rejects any import of
    # `anesthesia_sim.app` from `core/` in every form it can parse: absolute,
    # relative, or a dynamic import with a literal name (`PL-YXFF`). What is
    # left for this loop to catch is the identifier typed into `core/` by hand.
    # That could be in a comment, or in a second definition, which
    # `tools/literal_home_check.py` also rejects.
    #
    # This check would not have caught the defect that prompted it. What
    # `core/supported_ranges.py` actually said was that the ranges rested on
    # "every claim docs/MODEL.md makes about the last displayed digit". That
    # sentence states the reasoning without naming the constant. No check can
    # catch that phrasing without guessing at the judgment, and `CLAUDE.md`
    # says not to script the judgment. docs/MODEL.md § "Displayed precision"
    # states the reasoning in prose, and a reviewer is the guard.
    core_modules = (Path(__file__).resolve().parents[2] / "src" / "anesthesia_sim" / "core").rglob(
        "*.py"
    )
    for module in core_modules:
        assert "CONCENTRATION_DISPLAY_DECIMALS" not in module.read_text(), (
            f"{module.name} references the displayed decimal count. The display "
            f"must not bound the model: see docs/MODEL.md § 'Displayed precision'."
        )


def test_format_percent_rounds_rather_than_truncates() -> None:
    """The last displayed digit is the nearest one, not a truncation.

    Truncation would bias every reading downward by up to a full count of
    the last displayed digit. That would be a systematic error introduced by
    the display itself. It would also be the largest error anywhere between a
    slider and a pixel, now that the solver's own residual is nine orders of
    magnitude smaller than the readout. Exact ties are not asserted, because a
    decimal tie is not generally representable as a double.
    """

    assert format_percent(Fraction(0.021_39)) == "2.14%"
    assert format_percent(Fraction(0.021_31)) == "2.13%"


def test_format_percent_marks_a_value_below_the_resolution() -> None:
    """A filling compartment must not look like an empty one.

    Muscle and fat stay below 0.01% for the opening minutes of every run.
    Rounding them to `0.00%` would claim that the model has zero agent there
    when it does not. A positive value that rounds to zero is therefore shown
    as below the resolution instead.
    """

    assert format_percent(Fraction(1e-8)) == "<0.01%"
    assert format_percent(Fraction(4.0e-5)) == "<0.01%"

    # Exactly zero is the one value that may display as zero. It means that no
    # agent has reached the compartment, which the model does know.
    assert format_percent(Fraction(0.0)) == "0.00%"

    # Either side of the rounding threshold, at half the resolution.
    assert format_percent(Fraction(4.9e-5)) == "<0.01%"
    assert format_percent(Fraction(5.1e-5)) == "0.01%"


def _displayed_value(reading: str) -> float:
    """Return the percent that a reading from `format_percent` states, as a number.

    "<0.01%" says that the value is above zero and below the resolution. It is
    therefore treated as half the resolution, a number strictly between the two.
    """

    assert reading.endswith("%"), reading
    number = reading.removesuffix("%")

    if number.startswith("<"):
        assert float(number.removeprefix("<")) == CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
        return CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / 2.0

    return float(number)


#: One count of the last displayed digit, as a fraction: 0.01% is 1e-4.
_DISPLAY_COUNT_FRACTION = CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / 100.0


def _ulps_from(value: float, steps: int) -> float:
    """Return `value` moved by `steps` units in the last place, clamped to 0 to 1."""

    for _ in range(abs(steps)):
        value = math.nextafter(value, math.inf if steps > 0 else -math.inf)

    return min(max(value, 0.0), 1.0)


# Draw a fraction anywhere in 0 to 1, or within two units in the last place of
# a whole or half display count. The rounding threshold between two readings
# is at a half count, so a formatter that does not preserve order would show
# the fault there first.
_FRACTIONS = st.one_of(
    st.floats(min_value=0.0, max_value=1.0),
    st.builds(
        _ulps_from,
        st.integers(min_value=0, max_value=20_000).map(
            lambda half_counts: half_counts * _DISPLAY_COUNT_FRACTION / 2.0
        ),
        st.integers(min_value=-2, max_value=2),
    ),
)


@settings(derandomize=True, database=None, deadline=None, max_examples=2_000)
@given(_FRACTIONS, _FRACTIONS)
@example(0.0, 1e-12)
@example(4.9e-5, 5.1e-5)
@example(9.9e-5, 1.0)
def test_format_percent_preserves_order(first: float, second: float) -> None:
    """A higher fraction is never displayed as a lower percent.

    The dashboard shows six concentrations side by side, to be compared in
    order. `docs/MODEL.md` § "Displayed precision" relies on the display not
    reordering them. Rounding preserves order, but `format_percent` also has a
    below-resolution branch. The property is therefore checked on the shipped
    function rather than assumed (`PL-0M7K`). Each reading is parsed back to a
    number, and "<0.01%" is treated as strictly between 0 and 0.01. The
    fractions cover 0, the below-resolution branch, and both sides of every
    display-count boundary from 0% to 100%.
    """

    lower, higher = sorted((first, second))

    assert _displayed_value(format_percent(Fraction(lower))) <= _displayed_value(
        format_percent(Fraction(higher))
    )


@pytest.mark.parametrize("impossible", [-1e-8, -0.02, 1.0000000000000002])
def test_format_percent_refuses_an_impossible_fraction(impossible: float) -> None:
    """A fraction outside 0 to 1 cannot occur, and must not be disguised if it does.

    No `Fraction` can hold such a value. Reaching this point means that a
    caller which `mypy` does not check passed in a bare float, and something
    upstream is wrong. The below-resolution form would render a small negative
    value as an ordinary small positive reading. A value just past 1 because of
    rounding would display as `100.00%`. `CLAUDE.md` requires the obvious
    failure instead.

    Until `PL-4R3W`, a negative value was rendered with its sign. That item
    rejected the value by its range. Since `PL-1DP1`, such a value can only
    arrive as a bare float, and the bare float is rejected because it is not a
    `Fraction` at all, before its value is examined. That is the stronger
    check again.
    """

    with pytest.raises(TypeError, match="was not built as Fraction, it is float: build it as"):
        format_percent(impossible)  # type: ignore[arg-type]


def test_format_percent_states_the_below_resolution_form_from_the_constant() -> None:
    """The marker must say the resolution the readouts actually use.

    `<0.01%` is not a literal anywhere. It is rendered from
    `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` at
    `CONCENTRATION_DISPLAY_DECIMALS` decimals. A hardcoded marker would keep
    saying `<0.01%` after a resolution change. It would then tell a reader
    that the display resolves a digit finer or coarser than it does.
    """

    expected = f"<{CONCENTRATION_DISPLAY_RESOLUTION_PERCENT:.{CONCENTRATION_DISPLAY_DECIMALS}f}%"

    assert format_percent(Fraction(1e-9)) == expected


def test_format_subtitle_names_the_running_model_and_its_version() -> None:
    """The subtitle is the one line that ties a displayed value to what produced it.

    `CLAUDE.md` requires a clinically meaningful value to be traceable to
    the model and version behind it. This subtitle is where the interface
    states both. The test compares it with `APP_BUILD_VERSION` rather than
    with a literal, so that the test cannot pass with a stale version.
    """

    expected = f"Version {APP_BUILD_VERSION} — Sevoflurane patient model"
    assert format_subtitle("Sevoflurane") == expected
    assert (
        format_subtitle("Desflurane") == f"Version {APP_BUILD_VERSION} — Desflurane patient model"
    )


def test_the_subtitle_carries_the_build_identifier_when_there_is_one() -> None:
    """Between two releases every build shows the same version string.

    That made a merged fix look identical to the code it replaced when the
    project owner tried to confirm the fix by eye. The symptom was reported as
    still present, and the version on screen would have confirmed that wrong
    conclusion (`PL-QC38`, `PL-YKF8`). The subtitle now shows whatever
    `app_metadata.py` could establish about the running build. It shows the
    bare version when that is all there is.
    """

    subtitle = format_subtitle("Isoflurane")

    assert subtitle.startswith(f"Version {APP_VERSION}")
    if APP_BUILD is None:
        assert subtitle == f"Version {APP_VERSION} — Isoflurane patient model"
    else:
        assert subtitle == f"Version {APP_VERSION}+{APP_BUILD} — Isoflurane patient model"
        assert APP_BUILD.startswith("g")


def test_format_delivered_label_names_the_agent_being_delivered() -> None:
    """The vaporizer control must name the agent it is dialling.

    A delivered concentration is meaningless without its agent. 2% is a third
    of a MAC of desflurane and a full MAC of sevoflurane. The label therefore
    includes the agent's name rather than saying "Delivered agent".
    """

    assert format_delivered_label("Sevoflurane") == "Delivered sevoflurane"
    assert format_delivered_label("Isoflurane") == "Delivered isoflurane"


def test_the_mac_resolution_is_derived_from_the_percent_resolution() -> None:
    """One stated resolution has to govern both display units.

    A MAC multiple is a percent divided by the agent's own `mac_percent`.
    The percent resolution therefore already fixes how finely the quotient is
    known. For that reason `docs/MODEL.md` § "Displayed precision" *derives*
    `MAC_DISPLAY_DECIMALS` rather than choosing it. The MAC resolution is the
    finest power of ten that is nowhere finer than the percent resolution
    converted into MAC. Deriving it independently would mean re-deriving two
    numbers whenever the first is re-measured, and `PL-X9KD` is about to
    re-measure the percent side.

    This test repeats that arithmetic for every shipped agent. Adding an
    agent, or changing the percent resolution, therefore fails here rather
    than silently over-claiming on the display. The agent that sets the limit
    today is isoflurane: 0.01 percentage points of a 1.2% MAC is 0.0083 MAC,
    and 0.01 is the finest power of ten at or above that.
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

    This is the property that the derivation in the test above exists to
    guarantee, stated as a reader meets it. For every shipped agent, one count
    of the MAC line is at least one count of the percent line above it. If
    that failed, a reader could watch the MAC digit move while the percent
    digit stayed still. The reader could then conclude that the model resolves
    a difference that it does not.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        mac_percent = load_agent_parameters(agent_id).mac_percent
        one_mac_count_in_percentage_points = MAC_DISPLAY_RESOLUTION_MAC * mac_percent

        assert one_mac_count_in_percentage_points >= CONCENTRATION_DISPLAY_RESOLUTION_PERCENT, (
            f"{agent_id}: the MAC line resolves finer than the percent line"
        )


def test_one_mac_of_every_agent_reads_as_one() -> None:
    """Check the defining case of the MAC unit on the three agents that ship.

    This is the whole reason for the second unit. The same clinical depth
    shows as the same number whichever agent is running. The percent line
    shows 2.00%, 1.20% and 6.00% for the identical situation.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        mac_percent = load_agent_parameters(agent_id).mac_percent

        assert mac_multiple(fraction_from_percent(mac_percent), mac_percent) == pytest.approx(1.0)
        assert format_mac_multiple(fraction_from_percent(mac_percent), mac_percent) == "1.00 ×MAC"


def test_format_mac_multiple_carries_the_multiplication_sign() -> None:
    """`0.80 MAC` looks like a depth, and `0.80 ×MAC` looks like a ratio.

    The sign is the display side of `docs/MODEL.md` § "MAC multiples as a
    display unit". On the four non-alveolar compartments, the number is a
    partial-pressure ratio and claims nothing about anesthetic depth. The two
    meanings cannot be told apart if the unit is written as a bare "MAC".
    """

    assert MAC_UNIT_SUFFIX == " ×MAC"
    assert format_mac_multiple(Fraction(0.016), MacPercent(2.0)) == "0.80 ×MAC"
    assert format_mac_multiple(Fraction(0.0), MacPercent(2.0)) == "0.00 ×MAC"
    assert format_mac_multiple(Fraction(0.04), MacPercent(2.0)) == "2.00 ×MAC"


def test_format_mac_multiple_marks_a_value_below_the_resolution() -> None:
    """A filling compartment must not look like an empty one, in either unit.

    The below-resolution form matters more in MAC than in percent, not less.
    0.01 MAC is 0.02 percentage points of sevoflurane and 0.06 of desflurane.
    A compartment therefore reaches the MAC line's last digit later than it
    reaches the last digit of the percent readout beside it. If the MAC line
    showed `0.00 ×MAC` under a percent line that already shows the
    compartment filling, the two readouts would contradict each other.
    """

    expected = f"<{MAC_DISPLAY_RESOLUTION_MAC:.{MAC_DISPLAY_DECIMALS}f}{MAC_UNIT_SUFFIX}"

    # 0.015% of desflurane: above the percent resolution, below the MAC one.
    assert format_percent(Fraction(0.00015)) == "0.01%"
    assert format_mac_multiple(Fraction(0.00015), MacPercent(6.0)) == expected
    assert format_mac_multiple(Fraction(1e-9), MacPercent(2.0)) == expected


@pytest.mark.parametrize("impossible", [-0.02, -1e-9])
def test_format_mac_multiple_refuses_an_impossible_negative(impossible: float) -> None:
    """A negative value is an upstream defect and must not be shown as a value.

    The rule is the same as for `format_percent`, for the same reason. No
    `Fraction` can hold a negative value, so one that arrives here is rejected
    before it can be hidden in the plausible-looking below-resolution form.
    Since `PL-1DP1`, such a value can only arrive as a bare float, and it is
    rejected as one before its value is examined.
    """

    with pytest.raises(TypeError, match="was not built as Fraction, it is float: build it as"):
        format_mac_multiple(impossible, MacPercent(2.0))  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_mac", [0.0, -2.0, 2.0, Percent(2.0)])
def test_a_mac_not_built_as_one_refuses_to_produce_a_number(bad_mac: float) -> None:
    """`CLAUDE.md` requires an obvious failure over a plausible value.

    A zero or negative divisor cannot produce a meaningful multiple. Each
    formatter that divides by a MAC takes a `MacPercent`, which refuses zero
    when it is built. So a divisor that was not built as one is refused here,
    whatever its value. Before `PL-F9TC`, each formatter tested the sign
    itself, and a positive bare `float` passed. A `Percent` is refused too,
    because a dial setting is not a MAC.
    """

    refusal = "was not built as MacPercent"

    with pytest.raises(TypeError, match=refusal):
        mac_multiple(Fraction(0.02), bad_mac)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=refusal):
        format_mac_multiple(Fraction(0.02), bad_mac)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=refusal):
        mac_axis_ticks(8.0, bad_mac)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=refusal):
        chart_axis_top_percent(bad_mac)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=refusal):
        chart_grid_interval_percent(bad_mac)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=refusal):
        format_mac_reference("Sevoflurane", bad_mac)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=refusal):
        mac_awake_band_percent(
            fraction_of_mac=MacMultiple(0.34),
            standard_deviation_fraction_of_mac=MacMultiple(0.05),
            mac_percent=bad_mac,  # type: ignore[arg-type]
        )


def test_mac_axis_ticks_land_on_round_mac_values_inside_the_plotted_range() -> None:
    """The axis exists so a reader can find 1 MAC, not so it can find 2%.

    Each tick is returned as the percent position it occupies, because the
    chart plots percent and the MAC axis is a relabelling of that same
    coordinate rather than a second set of points. A tick above the top of
    the range would be drawn outside the plotted area.
    """

    ticks = mac_axis_ticks(8.0, MacPercent(2.0))

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

    The three vaporizer maxima span 5% to 18%, which is 3.0 to 4.2 MAC. That
    range is narrow enough that the ladder gives all three agents a half-MAC
    step. The second unit exists for comparison across agents, and the shared
    step is what makes that comparison readable. A gridline that a reader
    learns under sevoflurane means the same thing under desflurane.
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

    `MAX_MAC_AXIS_INTERVALS` is the maximum number of intervals, and the
    ladder supplies the steps. A fixed step would put sixty labels on a wide
    axis. That axis would be unreadable rather than precise.
    """

    for max_percent, expected_step in (
        (1.0, 0.25),
        (8.0, 0.5),
        (18.0, 1.0),
        (25.0, 2.0),
        (45.0, 5.0),
    ):
        ticks = mac_axis_ticks(max_percent, MacPercent(2.0))
        labels = [float(label) for _, label in ticks]

        assert len(ticks) - 1 <= MAX_MAC_AXIS_INTERVALS
        assert round(labels[1] - labels[0], 6) == expected_step
        assert expected_step in MAC_AXIS_STEP_LADDER_MAC


def test_the_mac_axis_is_unlabelled_rather_than_invented_for_an_empty_range() -> None:
    """No plotted range means no scale to label, and none is guessed."""

    assert mac_axis_ticks(0.0, MacPercent(2.0)) == ()
    assert mac_axis_ticks(-1.0, MacPercent(2.0)) == ()


def test_format_mac_reference_states_the_divisor_the_readouts_used() -> None:
    """The display names the one free parameter of the second unit.

    `CLAUDE.md` requires a clinically meaningful displayed value to be
    traceable to the transformation that produced it. A MAC multiple has
    exactly one transformation, the division by MAC. Naming the divisor beside
    the axis lets a reader who disagrees with it see that they disagree. They
    can then convert back.
    """

    assert format_mac_reference("Sevoflurane", MacPercent(2.0)) == "1 MAC sevoflurane = 2.0%"
    assert format_mac_reference("Desflurane", MacPercent(6.0)) == "1 MAC desflurane = 6.0%"

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        reference = format_mac_reference(agent.display_name, agent.mac_percent)

        assert agent.display_name.lower() in reference
        assert f"{agent.mac_percent:.1f}%" in reference


def test_the_mac_awake_band_is_the_stored_fraction_scaled_by_the_stored_mac() -> None:
    """The band's height is a fraction times a divisor, and nothing else.

    The test checks every shipped agent rather than one literal. The property
    that matters is that *that agent's* two values place the band. The
    expected edges are calculated here independently from the data files
    rather than restated. A corrected value in a data file therefore moves the
    assertion with it, instead of failing against a stale literal.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        mac_awake = agent.mac_awake

        lower, upper = mac_awake_band_percent(
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
            mac_percent=agent.mac_percent,
        )

        deviation_percent = mac_awake.standard_deviation_fraction_of_mac * agent.mac_percent
        centre_percent = mac_awake.fraction_of_mac * agent.mac_percent

        assert lower == pytest.approx(centre_percent - deviation_percent)
        assert upper == pytest.approx(centre_percent + deviation_percent)
        assert 0.0 < lower < upper < agent.mac_percent


def test_the_mac_awake_band_uses_the_fraction_rather_than_a_published_percent() -> None:
    """Pin the denominator trap as arithmetic.

    Desflurane's published MAC-awake of 2.60% is 36% of a MAC of about 7.25%,
    which is Rampil's figure for ages 18-30. This project stores Rampil's
    figure for ages 31-65, which is 6.0%. Importing the *percent* would place
    the band at 2.60%, where the fraction places it at 2.16%. That is 20% too
    high. A falling trace crosses a reference drawn too high too soon, so the
    chart would teach an earlier wake-up than the literature supports.
    `docs/MODEL.md` § "MAC-awake as a chart reference" gives the reasoning.

    This trap is why the fraction is the stored form, rather than a schema
    preference. The test therefore treats the wrong band as a value that the
    interface must not be able to produce.

    The band is also compared with an independent measurement. That
    measurement is the non-jaundiced control arm of Song et al. 2005, in the
    population that the 31-65 year divisor describes. The comparison is
    coarse. Its tolerance is Song's standard deviation, so it fails only when
    the stored fraction is more than about 11% too low or 12% too high, that
    is, outside 0.320-0.403 of MAC.
    `test_mac_awake_matches_its_adopted_primary_source` in
    `tests/unit/test_parameters.py` pins the fraction exactly (`PL-H1JH`).
    """

    desflurane = load_agent_parameters("desflurane")
    mac_awake = desflurane.mac_awake

    lower, upper = mac_awake_band_percent(
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=desflurane.mac_percent,
    )
    centre = (lower + upper) / 2.0

    assert centre == pytest.approx(2.16)
    # Song et al. 2005 (PMID 15731594), Abstract, read through PubMed on
    # 2026-10-17: the control group's MAC-awake was "2.17 +/- 0.25%" (mean +/-
    # SD). The centre lies within one of Song's standard deviations of that
    # mean. The bound is not the display's resolution. The difference between
    # 2.16 and 2.17 falls exactly on that resolution in decimal arithmetic, and
    # only float rounding let a strict `<` pass there.
    assert abs(centre - 2.17) <= 0.25
    # The stored fraction must not reproduce Chortkoff's absolute percent,
    # because that percent belongs to a different population's MAC.
    assert centre != pytest.approx(2.60)
    # Also rule out the mistake of dividing that absolute percent by the
    # stored MAC.
    assert mac_awake.fraction_of_mac != pytest.approx(2.60 / desflurane.mac_percent, abs=1e-3)


@pytest.mark.parametrize(
    ("agent_id", "band_percent", "reference_line"),
    [
        # 0.34 +/- 0.05 times 2.0%
        (
            "sevoflurane",
            (0.58, 0.78),
            "MAC-awake sevoflurane = 0.34 ×MAC (0.68%), band ±1 SD 0.58–0.78%",
        ),
        # 0.31 +/- 0.05 times 1.2%
        (
            "isoflurane",
            (0.312, 0.432),
            "MAC-awake isoflurane = 0.31 ×MAC (0.37%), band ±1 SD 0.31–0.43%",
        ),
        # 0.36 +/- 0.063 times 6.0%
        (
            "desflurane",
            (1.782, 2.538),
            "MAC-awake desflurane = 0.36 ×MAC (2.16%), band ±1 SD 1.78–2.54%",
        ),
    ],
    ids=["sevoflurane", "isoflurane", "desflurane"],
)
def test_each_shipped_mac_awake_band_lands_at_its_published_values(
    agent_id: str, band_percent: tuple[float, float], reference_line: str
) -> None:
    """Check a run's MAC-awake band and its line of text against literals.

    The run is built from the shipped data file. Each edge was worked out by
    hand as the published mean minus or plus one standard deviation, times
    the MAC that the display divides by. The fractions are Katoh et al.'s and
    Chortkoff et al.'s, and `test_mac_awake_matches_its_adopted_primary_source`
    in `tests/unit/test_parameters.py` gives their locators. The MACs are De
    Wolf et al.'s. The other band tests in this file compute their expected
    band from the loaded file. None of them can therefore detect a value that
    was wrong when it was stored (`PL-H1JH`).
    """

    snapshot = SimulationController(agent_id=agent_id).snapshot()
    mac_awake = snapshot.agent_mac_awake
    band = mac_awake_band_percent(
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=snapshot.agent_mac_percent,
    )
    line = format_mac_awake_reference(
        snapshot.agent_display_name,
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=snapshot.agent_mac_percent,
    )

    assert band == pytest.approx(band_percent)
    assert line == reference_line


def test_the_mac_awake_band_refuses_inputs_it_cannot_place_honestly() -> None:
    """The band raises an obvious failure rather than drawing a plausible-looking band.

    A non-positive divisor has no meaningful multiple. A lower edge at or
    below zero is not a concentration. `_MacAwakePayload` already makes both
    impossible from a shipped data file. If either arrives here, something
    upstream is wrong, and the band must not be drawn anyway.
    """

    with pytest.raises(TypeError, match="MacPercent"):
        mac_awake_band_percent(
            fraction_of_mac=0.34,
            standard_deviation_fraction_of_mac=0.05,
            mac_percent=0.0,  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="lower edge"):
        mac_awake_band_percent(
            fraction_of_mac=0.05,
            standard_deviation_fraction_of_mac=0.05,
            mac_percent=MacPercent(2.0),
        )


def test_each_display_refusal_a_halt_can_show_is_pinned_whole() -> None:
    """Pin the whole sentence that the "Simulation stopped" banner shows for each display refusal.

    A frame that cannot be drawn halts the run and prints the refusal. The
    tests above match only a phrase of each refusal. Such a match still
    passes when the value that the refusal names is missing (`PL-79PK`). A
    zero MAC is no longer among these refusals. A `MacPercent` refuses it
    when the agent is read, before any run starts (`PL-F9TC`).
    """

    with pytest.raises(ValueError) as no_band:
        mac_awake_band_percent(
            fraction_of_mac=0.05,
            standard_deviation_fraction_of_mac=0.05,
            mac_percent=MacPercent(2.0),
        )

    with pytest.raises(ValueError) as no_time:
        format_elapsed(-1.0)

    assert str(no_band.value) == (
        "the MAC-awake band's lower edge must be strictly positive, got 0.05 - 0.05"
    )
    assert str(no_time.value) == "duration must be finite and non-negative, got -1.0"


def test_the_mac_awake_band_arguments_are_keyword_only() -> None:
    """The signature rejects a transposition that the type system cannot catch.

    The mean and its standard deviation are two dimensionless numbers of the
    same magnitude and the same type. If they were positional, swapping them
    would draw a band centred on the spread rather than the mean, with no
    error anywhere.
    """

    with pytest.raises(TypeError):
        mac_awake_band_percent(0.34, 0.05, 2.0)  # type: ignore[call-arg]


def test_a_concentration_fraction_reaching_the_mac_awake_band_is_refused_by_mypy_alone() -> None:
    """Show the swap that `MacMultiple` exists to reject, and what it costs if it happens.

    A fraction of an atmosphere and a ratio to MAC are both small
    dimensionless numbers of the same magnitude. Neither looks wrong in place
    of the other. Sevoflurane's band is 0.34 +/- 0.05 MAC against a MAC of
    2.0%, which is 0.58-0.78%. That is the range a falling alveolar trace has
    to cross for arousal. A circuit fraction at the vaporizer's own 8% maximum,
    passed instead, clears every runtime guard, because 0.08 - 0.05 is still
    positive. It draws the same band at 0.06-0.26%. That
    band is *below* the awakening concentration, so a trace crosses it late
    or not at all, and nothing on the screen says so.

    The directive below is therefore the whole of the safeguard. The two
    assertions are what a reader needs in order to believe that (`PL-BQ46`).
    """

    correct = mac_awake_band_percent(
        fraction_of_mac=MacMultiple(0.34),
        standard_deviation_fraction_of_mac=MacMultiple(0.05),
        mac_percent=MacPercent(2.0),
    )
    swapped = mac_awake_band_percent(
        fraction_of_mac=Fraction(0.08),  # type: ignore[arg-type]
        standard_deviation_fraction_of_mac=MacMultiple(0.05),
        mac_percent=MacPercent(2.0),
    )

    assert correct == pytest.approx((0.58, 0.78))
    assert swapped == pytest.approx((0.06, 0.26))


def test_a_mac_multiple_reaching_a_concentration_parameter_is_refused_too() -> None:
    """The swap in the other direction is rejected too: it would corrupt a readout, not a reference.

    `mac_multiple()` returns a ratio to MAC. The two readouts beside each
    other show the same compartment in the two units. Sevoflurane at 0.34 MAC
    is an alveolar fraction of 0.0068. Rendering the multiple as though it
    were the fraction prints the percent of 0.34 next to "0.34" of MAC. The
    two readouts of one compartment would then disagree by the factor of 50
    between them.

    `mypy` rejects the call, which the directive asserts. Since `PL-1DP1`, the
    formatter also rejects it at run time. There a `MacMultiple` is a bare
    `float`, not built as a `Fraction`. Until then, the formatter printed it
    as the fraction it is not.
    """

    fraction = Fraction(0.0068)
    multiple = mac_multiple(fraction, MacPercent(2.0))

    assert format_percent(fraction) == f"{0.68:.{CONCENTRATION_DISPLAY_DECIMALS}f}%"
    assert multiple == pytest.approx(0.34)

    with pytest.raises(
        TypeError, match=f"^fraction of {multiple!r} was not built as Fraction, it is float"
    ):
        format_percent(multiple)  # type: ignore[arg-type]


def test_every_mac_divisor_here_is_typed_as_a_percent() -> None:
    """Every `mac_percent` this module takes is a `MacPercent`, never a bare `float`.

    Sevoflurane's 1 MAC is 2.0% of an atmosphere, and 0.02 as a fraction.
    Given the fraction, every function named below runs without complaint,
    because the divisor is still positive. The chart's ceiling lands at 0.06%
    instead of 6%, and 1 MAC displays as 100.00 ×MAC. A `Fraction` is a
    `float`, so only a parameter typed `Percent` rejects one. A parameter
    typed `float` breaks no caller, so `mypy` never asks for it to change.
    Six of these eight were `float` until `PL-W3Q5`. The test reads the types
    from the signatures rather than from a list, so a function added with a
    bare `float` divisor fails here too. Since `PL-F9TC`, the type is
    `MacPercent`, a `Percent` checked to be above zero.
    """

    divisors = {
        name: get_type_hints(function)["mac_percent"]
        for name, function in inspect.getmembers(formatting_module, inspect.isfunction)
        if function.__module__ == formatting_module.__name__
        and "mac_percent" in inspect.signature(function).parameters
    }

    assert set(divisors) >= {
        "chart_axis_top_percent",
        "chart_grid_interval_percent",
        "format_mac_awake_reference",
        "format_mac_multiple",
        "format_mac_reference",
        "mac_awake_band_percent",
        "mac_axis_ticks",
        "mac_multiple",
    }
    assert {name: hint for name, hint in divisors.items() if hint is not MacPercent} == {}


def test_format_mac_awake_reference_names_both_free_parameters() -> None:
    """The band has two free parameters, so both are on the display.

    A MAC multiple has one divisor, and `format_mac_reference` names it. The
    band is a published fraction *applied to* that divisor. A reader therefore
    has two values to be able to disagree with. The line states the fraction,
    the percent it lands at, and the edges of the band.
    """

    reference = format_mac_awake_reference(
        "Sevoflurane",
        fraction_of_mac=0.34,
        standard_deviation_fraction_of_mac=0.05,
        mac_percent=MacPercent(2.0),
    )

    assert reference == "MAC-awake sevoflurane = 0.34 \u00d7MAC (0.68%), band ±1 SD 0.58–0.78%"

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        mac_awake = agent.mac_awake
        rendered = format_mac_awake_reference(
            agent.display_name,
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
            mac_percent=agent.mac_percent,
        )
        lower, upper = mac_awake_band_percent(
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
            mac_percent=agent.mac_percent,
        )

        assert agent.display_name.lower() in rendered
        assert f"{mac_awake.fraction_of_mac:.{MAC_DISPLAY_DECIMALS}f}{MAC_UNIT_SUFFIX}" in rendered
        assert f"{lower:.{CONCENTRATION_DISPLAY_DECIMALS}f}" in rendered
        assert f"{upper:.{CONCENTRATION_DISPLAY_DECIMALS}f}" in rendered
        # The line must name the endpoint. MAC-awake is responsiveness to
        # command. MAC is immobility in response to incision. The two look alike unless
        # the line says which one it means.
        assert "MAC-awake" in rendered


@pytest.mark.parametrize(
    ("mac_percent", "expected_top", "expected_interval"),
    [
        (2.0, 6.0, 1.0),  # sevoflurane
        (1.2, 3.6, 0.6),  # isoflurane
        (6.0, 18.0, 3.0),  # desflurane
    ],
)
def test_the_chart_ceiling_and_rules_are_the_agent_s_mac_scaled(
    mac_percent: float, expected_top: float, expected_interval: float
) -> None:
    """Each expected value is calculated independently as the constant times the agent's 1 MAC.

    Desflurane's 18.0 deserves a second look. It is also that agent's
    vaporizer dial maximum. The number is therefore unchanged from the rule
    that PL-CC23 replaced, but the reason for it is entirely different. The
    match is a coincidence of 18 % / 6 % = 3.00, not agreement between the
    two rules.
    """

    assert chart_axis_top_percent(MacPercent(mac_percent)) == pytest.approx(expected_top)
    assert chart_grid_interval_percent(MacPercent(mac_percent)) == pytest.approx(expected_interval)


def test_the_chart_axis_spans_the_same_mac_range_whatever_the_agent() -> None:
    """Check, in MAC, the invariant that the axis exists to keep.

    Measured in MAC, the ceiling is one number for every agent. That is what
    gives two agents' wash-in curves the same shape for the same case. The
    test states this as a property over a range of 1 MAC values rather than
    over the three shipped agents. It therefore constrains the *rule* rather
    than today's data files.
    """

    for mac_percent in (0.5, 1.2, 2.0, 6.0, 12.0):
        assert chart_axis_top_percent(MacPercent(mac_percent)) / mac_percent == pytest.approx(
            CHART_AXIS_TOP_MAC
        )
        assert chart_grid_interval_percent(MacPercent(mac_percent)) / mac_percent == pytest.approx(
            CHART_GRID_INTERVAL_MAC
        )


def test_the_chart_ceiling_leaves_one_mac_inside_the_plot_with_room_to_overpressure() -> None:
    """Check the two constraints that chose 3 rather than 2 or 4.

    1 MAC must sit inside the plot rather than on its frame. The 2-3x MAC
    range in which overpressure induction works must also be on the plot. A
    ceiling of 2 would put the 1 MAC line at half height, with no room above
    it for the technique. The assertions below stop the constant from
    drifting back toward either edge.
    """

    assert CHART_AXIS_TOP_MAC >= 3.0, "overpressure at 2-3x MAC must stay on the plot"
    assert 1.0 / CHART_AXIS_TOP_MAC <= 0.34, "1 MAC must not sit near the top of the frame"
    # The gridlines have to divide the ceiling exactly. Otherwise the topmost
    # gap is a different size from the rest and looks like a scale change.
    assert (CHART_AXIS_TOP_MAC / CHART_GRID_INTERVAL_MAC) % 1 == pytest.approx(0.0)


@pytest.mark.parametrize("bad_mac_percent", [0.0, -1.0, -0.001])
def test_the_chart_axis_refuses_a_non_positive_mac(bad_mac_percent: float) -> None:
    """An axis of zero or negative height would place every trace somewhere meaningless.

    Failing is the required behavior. A chart drawn against such an axis
    would still render, and a reader could still read a number off every
    value on it. The axis takes a `MacPercent`, so such a MAC is rejected when
    the `MacPercent` is built, before an axis can be computed from it
    (`PL-F9TC`). The axis itself rejects a bare `float`, as
    `test_a_mac_not_built_as_one_refuses_to_produce_a_number` shows.
    """

    with pytest.raises(SimulationConfigurationError, match="mac_percent of"):
        chart_axis_top_percent(MacPercent(bad_mac_percent))


def test_the_discard_warning_states_the_time_at_the_clock_s_own_resolution() -> None:
    """The warning uses the clock's one rendering of simulated time, not a second one.

    A warning quoting "1 min" beside a clock showing "1m" would leave a
    reader converting between two displayed forms of the same quantity. They
    would be doing that at the moment they decide whether to destroy the case.
    `format_elapsed` exists to prevent that failure.

    The test asserts the literal as well as the call, so that the two cannot
    agree by both being wrong. `format_elapsed` moved from `1234.5 s` to the
    compound form under `PL-Q4M4` and `PL-CZFY`. A test written only against
    the function would have followed that change silently.
    """

    warning = format_case_discard_warning("Sevoflurane", 1234.5, 3)

    assert format_elapsed(1234.5) in warning
    assert "20m34.5s" in warning


def test_the_discard_warning_names_the_agent_being_left() -> None:
    """The agent is named in sentence case, because the warning is prose and not a label.

    The agent's name makes the warning about *this* case rather than about
    cases in general. It is also the cue that a reader compares with the
    header badge before answering.
    """

    assert "The current sevoflurane case" in format_case_discard_warning("Sevoflurane", 60.0, 1)
    assert "The current desflurane case" in format_case_discard_warning("Desflurane", 60.0, 1)


@pytest.mark.parametrize(
    ("control_change_count", "expected"),
    [
        (0, "0 recorded control changes"),
        (1, "1 recorded control change"),
        (2, "2 recorded control changes"),
        (47, "47 recorded control changes"),
    ],
)
def test_the_discard_warning_counts_control_changes_in_agreeing_grammar(
    control_change_count: int, expected: str
) -> None:
    """A count and its noun have to agree, including at one.

    This is not decoration. The sentence is read once, under time pressure, by
    someone about to lose the run it describes. "1 recorded control changes"
    is the kind of flaw that makes a reader read the one clause that matters
    a second time.
    """

    assert expected in format_case_discard_warning("Sevoflurane", 60.0, control_change_count)


def test_the_branch_discard_warning_states_both_instants_the_clock_showed() -> None:
    """`PL-W5WX`: a branch's time is two instants on the case's clock, not a duration.

    The literal is written from `format_elapsed`'s stated grammar, such as
    `1m` and `5m30.5s`, rather than from a call. A change to the clock's form
    therefore fails here instead of being followed silently.
    """

    assert format_branch_discard_warning("Run 2", 60.0, 330.5, 2) == (
        "Run 2 — branched at 1m and run to 5m30.5s, 2 recorded control changes — will be "
        "discarded along with its chart history. This cannot be undone."
    )


@pytest.mark.parametrize("elapsed_s", [60.0, None])
def test_the_branch_discard_warning_states_no_second_instant_it_cannot_stand_behind(
    elapsed_s: float | None,
) -> None:
    """Show only the fork time for a branch not run past its fork, or whose time is unknown.

    "Run to 1m" beside "branched at 1m" says nothing. An instant that could
    not be read must not be printed as though it were known.
    """

    assert format_branch_discard_warning("Run 2", 60.0, elapsed_s, 1) == (
        "Run 2 — branched at 1m, 1 recorded control change — will be discarded along with "
        "its chart history. This cannot be undone."
    )


@pytest.mark.parametrize(
    ("agent", "elapsed_s", "control_change_count", "expected"),
    [
        (
            "Sevoflurane",
            60.0,
            1,
            "The current sevoflurane case — 1m of simulated time, 1 recorded control "
            "change — will be discarded along with its chart history. This cannot be undone.",
        ),
        (
            "Desflurane",
            3725.0,
            0,
            "The current desflurane case — 1h2m5s of simulated time, 0 recorded control "
            "changes — will be discarded along with its chart history. This cannot be undone.",
        ),
        (
            "Isoflurane",
            1234.5,
            2,
            "The current isoflurane case — 20m34.5s of simulated time, 2 recorded control "
            "changes — will be discarded along with its chart history. This cannot be undone.",
        ),
    ],
)
def test_the_case_discard_warning_is_pinned_whole(
    agent: str, elapsed_s: float, control_change_count: int, expected: str
) -> None:
    """Pin the whole sentence, so that a wrong plural cannot pass as a substring.

    The grammar test above asserts `expected in warning`, and "1 recorded
    control change" is a substring of "1 recorded control changes". So a
    warning that dropped its singular form passed the whole suite (`PL-79PK`).
    Each expected sentence here is typed out, with the clock reading worked
    out by hand: 3725 s is 1 h 2 min 5 s, and 1234.5 s is 20 min 34.5 s.
    """

    assert format_case_discard_warning(agent, elapsed_s, control_change_count) == expected


def test_the_discard_warning_says_the_loss_is_final() -> None:
    """Finality is the one thing a reader cannot recover from misunderstanding.

    There is no undo and no saved state behind this dialog. The sentence has
    to say so, rather than leaving a reader to take "discarded" as reversible.
    """

    warning = format_case_discard_warning("Sevoflurane", 60.0, 1)

    assert "discarded" in warning
    assert "cannot be undone" in warning


def test_the_playback_rate_is_stated_at_every_rate_including_real_time() -> None:
    """A rate is a mode, and the label's absence must never be the signal.

    Rendering nothing at 1x would make "no label" mean real time. A reader
    would have to be taught that convention. `PL-SN2C` requires the
    multiplier beside the clock at all times for exactly that reason.
    """

    assert format_playback_rate(1) == "1\u00d7 real time"
    assert format_playback_rate(60) == "60\u00d7 real time"


def test_the_playback_rate_uses_the_multiplication_sign_the_readouts_use() -> None:
    """One typographic convention for a multiple, across the whole display.

    The MAC readouts already write a multiple with U+00D7. A rate written
    with a lowercase "x" beside them would look like a different kind of
    quantity.
    """

    assert "\u00d7" in format_playback_rate(60)
    assert "x" not in format_playback_rate(60)


def test_the_playback_rate_is_not_a_second_reading_of_the_clock() -> None:
    """The playback rate names a pace, so it must not carry a unit of simulated time.

    A second string ending in "s" beside `format_elapsed` invites a reader
    to take it as another elapsed time. That would be the confusion between
    modeled state and context, arriving through a label rather than through
    a number.
    """

    rate = format_playback_rate(60)

    assert not rate.endswith(" s")
    assert rate != format_elapsed(60.0)


@pytest.mark.parametrize(
    ("elapsed_s", "expected"),
    [
        (0.0, "0"),
        (15.0, "15s"),
        (45.0, "45s"),
        (60.0, "1m"),
        (90.0, "1m30s"),
        (180.0, "3m"),
        (900.0, "15m"),
        (3_600.0, "1h"),
        (5_400.0, "1h30m"),
        (43_200.0, "12h"),
        (86_400.0, "24h"),
    ],
)
def test_a_time_axis_tick_carries_its_own_unit(elapsed_s: float, expected: str) -> None:
    """A time-axis label must never lose its unit.

    The chart's horizontal axis spans anything from a minute to half a day.
    A bare number would mean seconds on one time base and hours on another,
    while looking identical on both. A reader who missed the caption would
    have nothing in the label to correct them. Reading a twelve-hour axis as
    twelve minutes inverts every rate on the plot.
    """

    assert format_chart_time_label(elapsed_s) == expected


def test_the_run_s_start_is_labelled_without_a_unit() -> None:
    """`0s` would invite reading the whole axis as seconds."""

    assert format_chart_time_label(0.0) == "0"


def test_a_time_axis_tick_shows_a_fraction_of_a_second_only_when_there_is_one() -> None:
    """A trailing `.0` on every label is noise, but a dropped tenth is a wrong time.

    Every tick that `app/chart_time_base.py` places falls on a whole second,
    so the ladder never produces a fraction. Rounding a fraction away
    silently, though, is how a label comes to name a time that the chart is
    not drawing.
    """

    assert format_chart_time_label(90.5) == "1m30.5s"
    assert format_chart_time_label(30.0) == "30s"


@pytest.mark.parametrize("elapsed_s", [-1.0, float("nan"), float("inf")])
def test_a_time_axis_tick_refuses_a_time_that_is_not_one(elapsed_s: float) -> None:
    """An axis label is a displayed value, so an impossible one fails loudly."""

    with pytest.raises(ValueError, match="finite and non-negative"):
        format_chart_time_label(elapsed_s)


@pytest.mark.parametrize(
    ("span_s", "expected"),
    [
        (60.0, "1 minute"),
        (900.0, "15 minutes"),
        (1_800.0, "30 minutes"),
        (3_600.0, "1 hour"),
        (7_200.0, "2 hours"),
        (43_200.0, "12 hours"),
        (86_400.0, "24 hours"),
        (5_400.0, "1 hour 30 minutes"),
    ],
)
def test_a_time_base_is_named_in_words_the_reader_chooses_from(
    span_s: float, expected: str
) -> None:
    """The selector's entries and the axis caption use the same words.

    The name is spelled out rather than written in `format_chart_time_label`'s
    compact form. A reader picks it from a list and reads it back, and it does
    not compete for width as a tick label does. The two forms stay consistent
    about the quantity: `15 minutes` in the caption sits over an axis whose
    last tick shows `15m`.
    """

    assert format_time_base(span_s) == expected


def test_a_time_base_name_agrees_with_its_own_count() -> None:
    """ "1 hours" is the kind of flaw that makes a reader read a line twice."""

    assert format_time_base(3_600.0) == "1 hour"
    assert format_time_base(60.0) == "1 minute"


def test_the_supported_run_length_is_stated_from_the_model_s_own_constant() -> None:
    """The interface may not state a limit the model does not enforce.

    The stated limit is derived rather than written out, so the two cannot
    drift apart. Suppose a change to `MAXIMUM_ELAPSED_SIMULATION_TIME_S` left a
    hardcoded "24 hours" in the banner. The banner would then tell a reader
    that the run stopped somewhere it did not. That is the
    correct-number-wrong-label failure, which `CLAUDE.md` treats as a safety
    defect rather than a typo.
    """

    assert format_supported_run_length() == (f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} hours")


def test_the_subtitle_declares_an_unidentified_build_instead_of_naming_one(
    monkeypatch: Any,
) -> None:
    """`PL-KCWD`: a provenance field must not show a non-answer that looks like a version.

    `app_metadata.py` falls back to `UNKNOWN_VERSION` where installed-package
    metadata is missing. That policy is right, because failing visibly is
    better than crashing on launch. The objection was to where the visible
    failure appeared. Substituted into this sentence, it read "Version
    unknown". This subtitle is the interface's only link between a displayed
    number and the model that produced it, so a reader was given an answer
    where there was none. `CLAUDE.md` requires a displayed value to be
    traceable to the exact version behind it. A build that cannot offer that
    has to say so. An unidentified build is precisely the one whose numbers
    must not later be quoted as having come from a known version.
    """

    monkeypatch.setattr(formatting_module, "APP_VERSION_IS_KNOWN", False)

    subtitle = format_subtitle("Sevoflurane")

    assert subtitle == (
        "Version unavailable (this build is not traceable) — Sevoflurane patient model"
    )
    assert "unknown" not in subtitle
    assert subtitle.endswith("Sevoflurane patient model")


def test_an_identified_build_still_names_its_version() -> None:
    """The other half of `PL-KCWD`: the ordinary path is unchanged."""

    assert format_subtitle("Sevoflurane") == (
        f"Version {APP_BUILD_VERSION} — Sevoflurane patient model"
    )


@pytest.mark.parametrize(
    "elapsed_s",
    [0.1, 20.0, 59.9, 60.0, 90.0, 3600.0, 5400.0, 86_399.9, MAXIMUM_ELAPSED_SIMULATION_TIME_S],
)
def test_the_clock_and_the_axis_state_one_quantity_one_way(elapsed_s: float) -> None:
    """`PL-Q4M4`: the display, not the reader, must do the unit conversion.

    `PL-SSBP` gave the chart a time base that spans a case, so its axis shows
    `1h30m`. The clock above it used to show `5400.0 s`. That was one quantity
    in two formats on one screen. Locating a control mark on a twelve-hour
    axis meant dividing by 3600 by hand. The test checks the whole range
    rather than one value. The two forms have to agree at every boundary where
    a component appears or disappears, and that is exactly where two
    independent implementations would drift apart.
    """

    assert format_elapsed(elapsed_s) == format_chart_time_label(elapsed_s)


def test_the_origin_is_the_one_place_the_two_forms_differ() -> None:
    """The axis origin is a bare `0`, and the clock says `0s`.

    This difference is deliberate, and it is the only one. On the axis, `0s`
    invites reading the whole axis as seconds, and the origin needs no unit
    to be understood. On the clock, a bare `0` beside six percent readings
    has nothing to say what it counts.
    """

    assert format_chart_time_label(0.0) == "0"
    assert format_elapsed(0.0) == "0s"


def test_the_clock_reads_the_supported_limit_the_way_the_limit_is_stated() -> None:
    """`PL-CZFY`: `86400.0 s` was false precision on a boundary declared in hours.

    `PL-Y5WR` declared the 24-hour envelope, so `86400.0 s` was the clock's
    top reading. A reader had to divide by 3600 to know where they were in the
    case. `format_supported_run_length` had already declined to reuse the old
    form for exactly this reason. Now the two agree about the quantity and
    differ only in register.

    That agreement holds for a limit of whole hours, and every limit declared
    so far has been one. At any other limit, the clock's `24h30m` and the
    sentence's `24.5 hours` would differ in more than register. This test
    then fails, so that someone reviews the pairing rather than shipping it.
    """

    hours = MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600

    assert format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S) == f"{hours:g}h"
    assert format_supported_run_length() == f"{hours:g} hours"


def test_the_clock_still_resolves_the_step_the_simulation_advances_by() -> None:
    """The compound form keeps the tenth of a second, which is what made one form possible.

    `format_elapsed`'s docstring used to argue that the clock and the axis
    could not share a form because "a compound duration form would round the
    stamp away". That was false of the compound form that shipped, and these
    assertions keep it false. A recorded control change has to resolve the
    `0.1 s` step at which it was taken.
    """

    assert format_elapsed(0.1) == "0.1s"
    assert format_elapsed(5400.1) == "1h30m0.1s"
    assert format_elapsed(86_399.9) == "23h59m59.9s"


def test_the_widest_reachable_clock_string_is_what_the_reserved_width_assumes() -> None:
    """The clock's reserved width is measured from this string, in the rendering font.

    The compound form changes length as components appear and disappear. The
    readout therefore reserves a width, rather than letting its panel move on
    every render tick. `dashboard_frame.WIDEST_READOUT_VALUE` is this string,
    and `qt_widgets.MetricPanel` measures it in the font it draws with
    (`PL-3355`). The Flet build used a fixed pixel guess,
    `theme.ELAPSED_VALUE_WIDTH`, which was retired with that port
    (`PL-25KS`). This test keeps the premise true if either the form or the
    envelope changes.

    The test therefore checks the premise rather than a string (`PL-T5J5`).
    No hour of the span may display wider than the reading from which the
    reserved width is measured. An hour's widest reading is its last tenth.
    There the minutes and the seconds both have two digits and the tenth is
    shown. That instant therefore represents the whole hour, at whatever
    limit the model declares.
    """

    widest = max(
        (
            format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S - tenth / 10.0)
            for tenth in range(1, 11)
        ),
        key=len,
    )
    last_tenth_of_each_hour = (
        format_elapsed(hour * 3600.0 + 3599.9)
        for hour in range(int(MAXIMUM_ELAPSED_SIMULATION_TIME_S // 3600))
    )

    assert all(len(reading) <= len(widest) for reading in last_tenth_of_each_hour)


@pytest.mark.parametrize("bad_elapsed_s", [-0.1, float("nan"), float("inf")])
def test_the_clock_refuses_a_time_that_cannot_have_elapsed(bad_elapsed_s: float) -> None:
    """The clock raises on an impossible time, which the old one-decimal form did not.

    `f"{-1.0:.1f} s"` renders `-1.0 s` without complaint. Simulated time
    cannot run backwards, so a negative value is a fault upstream. `CLAUDE.md`
    prefers an obvious failure to a plausible-looking displayed number.
    """

    with pytest.raises(ValueError, match="finite and non-negative"):
        format_elapsed(bad_elapsed_s)


_RUN_TOTALS = (AgentAmount.DELIVERED, AgentAmount.EXHAUSTED, AgentAmount.STORED)


def test_agent_amounts_precision() -> None:
    """Pin the `PL-TG60` decision: one decimal of a litre, and the below-resolution form.

    The Flet panel printed six decimals of an exhaust total whose parameter
    uncertainty is 0.016-0.23 L across the supported span. One count of 0.1 L
    lies inside the band that `docs/MODEL.md` § "Displayed precision" derives
    for the concentration readouts, and 0.01 L does not. The three totals
    share the count, so the accounting panel shows them on one scale. A
    positive amount that rounds to zero is shown as below the resolution,
    rather than as zero, which would suggest an empty circuit.
    """

    for total in _RUN_TOTALS:
        litres = agent_amount_display_precision(total, AgentAmountUnit.LITRES_OF_VAPOUR)
        assert (litres.decimals, litres.finest_decimals) == (1, 1)

    assert format_agent_volume(3.991974) == "4.0 L"
    assert format_agent_volume(0.012345) == "<0.1 L"
    assert format_agent_volume(0.0) == "0.0 L"


def test_the_exhausted_total_in_millilitres_of_liquid_claims_no_more_than_in_litres() -> None:
    """Derive the exhausted total's liquid precision from its litre one, for every agent.

    The exhausted total carries the partition coefficients' uncertainty, so
    in liquid it must not claim a finer resolution than in litres of vapour
    (`PL-0S0V`). So the liquid count is the finest power of ten that
    is no finer than one step of the litre display. That step is 0.1 L of
    vapour, converted into liquid. This test does that conversion from each
    agent's stored molar mass and density, not from the formatter. At the
    20 °C reference, 0.1 L of vapour is about 0.55 mL of sevoflurane, 0.51 mL
    of isoflurane and 0.48 mL of desflurane liquid. So 1 mL is the finest
    power of ten at or above all three, and 0.1 mL would claim five times the
    resolution that the litre display claims for the same amount.

    The parameter spread gives the same answer. One published SD of a
    partition coefficient moves the exhaust total at 24 h by 0.19 L of
    sevoflurane vapour, 0.18 L of isoflurane and 0.23 L of desflurane
    (`PL-TG60`). Converted with each agent's own ratio of vapour to liquid,
    those are 1.04, 0.92 and 1.10 mL of liquid. One step of 1 mL is then
    about one SD, and 0.1 mL would be a tenth of one.
    """

    litres = agent_amount_display_precision(AgentAmount.EXHAUSTED, AgentAmountUnit.LITRES_OF_VAPOUR)
    liquid = agent_amount_display_precision(
        AgentAmount.EXHAUSTED, AgentAmountUnit.MILLILITRES_OF_LIQUID
    )
    one_litre_count_in_ml_of_liquid = {
        agent_id: litres.resolution
        * 1000.0
        / load_agent_parameters(agent_id).vapour_volume_per_liquid_volume
        for agent_id in AGENT_DATA_FILENAMES
    }
    coarsest_supported_ml = max(one_litre_count_in_ml_of_liquid.values())

    # 100 mL of vapour over the 182.8 mL of vapour each mL of liquid gives.
    assert one_litre_count_in_ml_of_liquid["sevoflurane"] == pytest.approx(0.547, abs=0.001)
    assert liquid.resolution >= coarsest_supported_ml, (
        "the liquid figure resolves finer than the same amount in litres of vapour"
    )
    assert liquid.resolution / 10.0 < coarsest_supported_ml, (
        "a finer power of ten would still not over-claim; the derivation has drifted"
    )
    assert (liquid.decimals, liquid.finest_decimals) == (0, 0)


def test_the_delivered_total_in_millilitres_of_liquid_is_shown_to_a_tenth() -> None:
    """Pin the owner's ruling for the delivered total, and the density limit behind it.

    The delivered agent is the dial times the flow times the time, so no
    partition coefficient makes it uncertain. The conversion to liquid is
    exact at the model's 20 °C reference, so its one uncertainty in liquid is
    the measured density's. So the delivered total is shown to 0.1 mL (project
    owner, 2026-10-27, ratified, over whole millilitres, `PL-0S0V`). That also
    lets a reader multiply the two figures beside a cost by eye.

    The limit is computed here from each agent's stored density and its SD,
    not from the formatter. One SD of the density moves the liquid figure by
    0.1 mL once it holds about 190 mL of sevoflurane, 250 mL of isoflurane or
    366 mL of desflurane. Those are 0.1 x 1.5203 / 0.0008, 0.1 x 1.5019 / 0.0006
    and 0.1 x 1.4651 / 0.0004, from Laster, Fang and Eger's densities as
    `docs/MODEL.md` § "Agent amount" tabulates them. At Gas Man's Exercise 14-1,
    39.4 mL of isoflurane, one SD is 0.016 mL, well inside half a step.
    """

    liquid = agent_amount_display_precision(
        AgentAmount.DELIVERED, AgentAmountUnit.MILLILITRES_OF_LIQUID
    )
    litres = agent_amount_display_precision(AgentAmount.DELIVERED, AgentAmountUnit.LITRES_OF_VAPOUR)
    one_sd_reaches_a_step_at_ml = {
        agent_id: liquid.resolution
        * load_agent_parameters(agent_id).liquid_density.g_ml
        / load_agent_parameters(agent_id).liquid_density.standard_deviation_g_ml
        for agent_id in AGENT_DATA_FILENAMES
    }
    isoflurane = load_agent_parameters("isoflurane").liquid_density

    assert (liquid.decimals, liquid.finest_decimals) == (1, 1)
    assert (litres.decimals, litres.finest_decimals) == (1, 1)
    assert one_sd_reaches_a_step_at_ml == pytest.approx(
        {"sevoflurane": 190.0, "isoflurane": 250.3, "desflurane": 366.3}, abs=0.1
    )
    assert 39.4 * isoflurane.standard_deviation_g_ml / isoflurane.g_ml == pytest.approx(
        0.016, abs=0.001
    )


def test_a_precision_finer_than_its_derived_band_is_refused() -> None:
    """A finer count is refused when the precision is built, never clamped.

    The derived count is an upper bound only (`PL-0S0V`). Showing fewer
    decimals than the derivation admits claims nothing false. Showing more
    would claim a resolution that the model does not support. Clamping a
    finer request to the bound would let a caller believe it got the
    precision it asked for, so the request fails instead. The bound comes
    from the derivation for the amount and unit, so no caller can pass a
    looser one.
    """

    coarser = AgentAmountPrecision(AgentAmount.DELIVERED, AgentAmountUnit.LITRES_OF_VAPOUR, 0)
    assert coarser.resolution == 1.0
    assert coarser.finest_decimals == 1

    with pytest.raises(ValueError, match="2 decimals is finer than the 1"):
        AgentAmountPrecision(AgentAmount.STORED, AgentAmountUnit.LITRES_OF_VAPOUR, 2)
    with pytest.raises(ValueError, match="1 decimals is finer than the 0"):
        AgentAmountPrecision(AgentAmount.EXHAUSTED, AgentAmountUnit.MILLILITRES_OF_LIQUID, 1)
    with pytest.raises(ValueError, match="2 decimals is finer than the 1"):
        AgentAmountPrecision(AgentAmount.DELIVERED, AgentAmountUnit.MILLILITRES_OF_LIQUID, 2)

    for bad_count in (-1, 1.0, True):
        with pytest.raises(ValueError, match="whole number of decimals of 0 or more"):
            AgentAmountPrecision(
                AgentAmount.DELIVERED,
                AgentAmountUnit.LITRES_OF_VAPOUR,
                bad_count,  # type: ignore[arg-type]
            )

    for precision in AGENT_AMOUNT_DISPLAY_PRECISION.values():
        assert precision.decimals <= precision.finest_decimals


def test_a_unit_with_no_derived_precision_is_refused() -> None:
    """An amount in a unit with no derivation fails loudly.

    It is never formatted at a default precision (`PL-0S0V`). A compartment's
    amount has no entry in any unit until `PL-2881` derives one. The table must
    not lend it the litre precision of the run totals. At 0.1 L, venous blood
    and the alveoli would show below resolution for a whole hour. The stored
    total has no liquid entry, because a store converted to liquid comes out
    5.8% too high (`docs/MODEL.md` § "Known limitations"). At 17 mL of liquid,
    that error is already one whole step of 1 mL.
    """

    refused = [(AgentAmount.COMPARTMENT, unit) for unit in AgentAmountUnit] + [
        (AgentAmount.STORED, AgentAmountUnit.MILLILITRES_OF_LIQUID),
        (AgentAmount.DELIVERED, AgentAmountUnit.MILLILITRES_OF_VAPOUR),
    ]

    for amount, unit in refused:
        message = f"No displayed precision is derived for a {amount.value} in {unit.value}"
        with pytest.raises(ValueError, match=message):
            agent_amount_display_precision(amount, unit)
        with pytest.raises(ValueError, match=message):
            AgentAmountPrecision(amount, unit, 0)

        assert (amount, unit) not in AGENT_AMOUNT_DISPLAY_PRECISION


def test_format_agent_volume_rounds_rather_than_truncates() -> None:
    """The last displayed digit is the nearest one, as for every other readout."""

    assert format_agent_volume(3.96) == "4.0 L"
    assert format_agent_volume(3.94) == "3.9 L"


def test_format_agent_volume_marks_a_value_below_the_resolution() -> None:
    """In the first minute of a run, the exhaust is real and less than a tenth of a litre."""

    assert format_agent_volume(1e-8) == "<0.1 L"
    assert format_agent_volume(0.04) == "<0.1 L"
    # Either side of the rounding threshold, at half the resolution.
    assert format_agent_volume(0.049) == "<0.1 L"
    assert format_agent_volume(0.051) == "0.1 L"


def test_format_agent_volume_states_the_below_resolution_form_from_the_constant() -> None:
    """The marker says the resolution the panel actually uses, never a literal."""

    litres = AGENT_AMOUNT_DISPLAY_PRECISION[
        (AgentAmount.DELIVERED, AgentAmountUnit.LITRES_OF_VAPOUR)
    ]
    expected = f"<{litres.resolution:.{litres.decimals}f} L"

    assert format_agent_volume(1e-9) == expected


def test_format_agent_volume_leaves_an_impossible_negative_visible() -> None:
    """A negative amount cannot occur, and must not be disguised if it does.

    The below-resolution form would render it as an ordinary small positive
    reading. `CLAUDE.md` requires the obvious failure instead, as
    `format_percent` does for a negative fraction.
    """

    assert format_agent_volume(-1e-8) == "-0.0 L"
    assert format_agent_volume(-2.0) == "-2.0 L"


def test_format_agent_residual_prints_the_power_of_ten_it_lies_below() -> None:
    """The two residual lines exist to show an order of magnitude (`PL-TG60`) and print only it."""

    assert format_agent_residual(1.5e-13) == "<1e-12 L"
    assert format_agent_residual(5.601e-14) == "<1e-13 L"
    assert format_agent_residual(3.289e-15) == "<1e-14 L"
    assert format_agent_residual(0.5) == "<1e+00 L"
    assert format_agent_residual(12.0) == "<1e+02 L"


def test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws() -> None:
    """Regression for `PL-3PJZ`: a passing check looks the same before and after a correct change.

    `PL-2MD9` changed the propagator's result in the last bits. The same
    branch sample showed `5.601e-14 L` on the v0.5.21 tag and `5.609e-14 L` on
    v0.5.22. Elsewhere, the residual moved by up to 5.9 times inside one
    decade. Four significant digits printed that rounding as if it were a
    reading.
    """

    assert format_agent_residual(5.601e-14) == format_agent_residual(5.609e-14)
    assert format_agent_residual(1.1e-14) == format_agent_residual(9.4e-14)


def test_format_agent_residual_drops_the_sign_the_rounding_chose() -> None:
    """A passing residual's sign is only the direction of its rounding, so both signs look alike.

    The signed value is still on screen where it means something. A check
    that fails halts the run, and the failure notice prints the value to six
    figures.
    """

    assert format_agent_residual(-3.289e-15) == "<1e-14 L"
    assert format_agent_residual(-3.289e-15) == format_agent_residual(3.289e-15)


@pytest.mark.parametrize("power", range(-17, 3))
def test_format_agent_residual_bound_is_strict_and_tight_at_every_power_of_ten(power: int) -> None:
    """The printed decade is exact for the float's own value, either side of each power of ten.

    `math.log10` would place the float written `1e-16`, which is exactly
    9.99...e-17, in the decade above. The bound must be the decade that the
    float actually lies in.
    """

    nearest = float(f"1e{power}")

    for litres in (math.nextafter(nearest, 0.0), nearest, math.nextafter(nearest, math.inf)):
        rendered = format_agent_residual(litres)
        exponent = int(rendered.removeprefix("<1e").removesuffix(" L"))

        assert Decimal(litres) < Decimal(10) ** exponent, rendered
        assert Decimal(litres) >= Decimal(10) ** (exponent - 1), rendered

    assert format_agent_residual(1e-16) == "<1e-16 L"


def test_format_agent_residual_reads_zero_as_zero() -> None:
    """Exactly zero, as before a run starts, is exact and needs no bound."""

    assert format_agent_residual(0.0) == "0 L"
    assert format_agent_residual(-0.0) == "0 L"


@pytest.mark.parametrize("litres", [math.nan, math.inf, -math.inf])
def test_format_agent_residual_leaves_a_non_finite_value_visible(litres: float) -> None:
    """The accounting check cannot produce a non-finite value, but one would be shown unbounded."""

    assert format_agent_residual(litres) == f"{litres} L"


def test_the_model_keeps_precision_the_display_throws_away() -> None:
    """The 0.01% resolution is a property of the display alone.

    `docs/MODEL.md` § "Displayed precision" argues at length for two decimal
    places. A reader could reasonably take that as a statement about the
    model, but it is not one. Every compartment state and every integration
    step keeps full binary64 precision throughout, and the rounding happens
    once, in the formatter. Two runs whose only difference is four orders of
    magnitude smaller than the display resolution must therefore reach
    different states. If anything in the pipeline rounded to what the display
    shows, the two states would be identical and this test would fail.
    """

    step_s = 0.1
    below_resolution = 1e-6  # percentage points, i.e. a fraction of 1e-8

    def run_at(delivered_concentration_percent: float) -> tuple[float, str]:
        controller = SimulationController()
        controller.set_delivered_concentration_percent(Percent(delivered_concentration_percent))
        controller.start()

        for _ in range(round(120.0 / step_s)):
            controller.advance(SimulationStep(step_s))

        snapshot = controller.snapshot()

        return snapshot.alveolar_partial_pressure_fraction, format_percent(
            snapshot.alveolar_partial_pressure_fraction
        )

    baseline_fraction, baseline_displayed = run_at(2.0)
    perturbed_fraction, perturbed_displayed = run_at(2.0 + below_resolution)

    assert baseline_fraction != perturbed_fraction, (
        "a change four orders of magnitude below the display resolution left "
        "the alveolar state bit-identical; something in the model or the "
        "snapshot is rounding to what the display shows"
    )
    assert 0.0 < abs(perturbed_fraction - baseline_fraction) < 1e-6
    assert baseline_displayed == perturbed_displayed, (
        "the two runs should be indistinguishable on the display and distinct "
        "in the model; if they differ on the display this test is no longer "
        "measuring what it claims"
    )
