"""What the recorded control-input timeline becomes on screen."""

from anesthesia_sim.app.control_timeline import (
    CONTROL_INPUT_LABELS,
    format_adjustment,
    format_control_value,
    group_adjustments,
)
from anesthesia_sim.app.controller import CONTROL_INPUT_UNITS, ControlChange, ControlInput


def _change(
    elapsed_s: float,
    control: ControlInput,
    previous_value: float,
    new_value: float,
    adjustment: int,
    sample_index: int = 0,
) -> ControlChange:
    return ControlChange(
        elapsed_s=elapsed_s,
        sample_index=sample_index,
        adjustment=adjustment,
        control=control,
        previous_value=previous_value,
        new_value=new_value,
        unit=CONTROL_INPUT_UNITS[control],
    )


def test_an_empty_timeline_groups_into_nothing() -> None:
    assert group_adjustments(()) == ()


def test_one_change_is_one_adjustment_at_a_single_instant() -> None:
    timeline = (_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)

    (adjustment,) = group_adjustments(timeline)

    assert adjustment.control is ControlInput.FRESH_GAS_FLOW
    assert adjustment.started_at_s == 12.0
    assert adjustment.ended_at_s == 12.0
    assert adjustment.from_value == 4.0
    assert adjustment.to_value == 2.0
    assert adjustment.change_count == 1


def test_a_drag_reads_as_one_act_spanning_the_settings_the_model_saw() -> None:
    """The endpoints are the person's; the count is the model's.

    Both are displayed because they are different claims: what the user
    did, and how many settings the run was actually computed under.
    """

    timeline = (
        _change(10.0, ControlInput.DELIVERED, 0.02, 0.025, adjustment=1, sample_index=100),
        _change(10.1, ControlInput.DELIVERED, 0.025, 0.031, adjustment=1, sample_index=101),
        _change(10.2, ControlInput.DELIVERED, 0.031, 0.04, adjustment=1, sample_index=102),
    )

    (adjustment,) = group_adjustments(timeline)

    assert adjustment.started_at_s == 10.0
    assert adjustment.ended_at_s == 10.2
    assert adjustment.from_value == 0.02
    assert adjustment.to_value == 0.04
    assert adjustment.change_count == 3
    assert adjustment.sample_index == 100


def test_two_adjustments_of_one_control_stay_two() -> None:
    """The grouping follows the recorded number, never the timing.

    Two turns of one dial are indistinguishable from one turn by any rule
    read off the entries alone, which is why the controller carries the
    boundary instead of this module inferring it.
    """

    timeline = (
        _change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        _change(10.1, ControlInput.FRESH_GAS_FLOW, 2.0, 1.0, adjustment=2),
    )

    first, second = group_adjustments(timeline)

    assert (first.from_value, first.to_value) == (4.0, 2.0)
    assert (second.from_value, second.to_value) == (2.0, 1.0)


def test_adjustments_are_oldest_first_like_the_time_axis() -> None:
    timeline = (
        _change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        _change(20.0, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=2),
        _change(30.0, ControlInput.ALVEOLAR_VENTILATION, 4.0, 6.0, adjustment=3),
    )

    assert [adjustment.started_at_s for adjustment in group_adjustments(timeline)] == [
        10.0,
        20.0,
        30.0,
    ]


def test_every_control_has_a_display_label() -> None:
    """A control with no label would render as a blank line, not an error."""

    assert set(CONTROL_INPUT_LABELS) == set(ControlInput)
    assert all(label for label in CONTROL_INPUT_LABELS.values())


def test_the_delivered_dial_is_displayed_in_percent_not_as_a_fraction() -> None:
    """Stored as the core's fraction, read as the page's percent.

    Displaying 0.02 where every other concentration on the page reads
    "2.00%" would make one quantity read two ways on one screen.
    """

    assert format_control_value(ControlInput.DELIVERED, 0.02) == "2.00%"


def test_flow_settings_are_displayed_in_the_unit_their_sliders_are() -> None:
    assert format_control_value(ControlInput.FRESH_GAS_FLOW, 4.0) == "4.0 L/min"
    assert format_control_value(ControlInput.ALVEOLAR_VENTILATION, 4.0) == "4.0 L/min"
    assert format_control_value(ControlInput.CARDIAC_OUTPUT, 5.0) == "5.0 L/min"


def test_circuit_volume_is_displayed_in_litres_not_litres_per_minute() -> None:
    """A volume rendered as a flow is the wrong-unit failure, on screen."""

    assert format_control_value(ControlInput.CIRCUIT_VOLUME, 6.0) == "6.0 L"


def test_a_single_change_reads_as_the_instant_it_was() -> None:
    timeline = (_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)

    (adjustment,) = group_adjustments(timeline)

    assert format_adjustment(adjustment) == "12.0 s · Fresh gas flow 4.0 L/min -> 2.0 L/min"


def test_a_multi_setting_adjustment_states_its_span_and_its_count() -> None:
    timeline = (
        _change(10.0, ControlInput.DELIVERED, 0.02, 0.03, adjustment=1),
        _change(10.2, ControlInput.DELIVERED, 0.03, 0.04, adjustment=1),
    )

    (adjustment,) = group_adjustments(timeline)

    assert format_adjustment(adjustment) == (
        "10.0 s–10.2 s · Delivered agent 2.00% -> 4.00% (2 settings)"
    )


def test_a_rendered_adjustment_carries_a_unit_on_both_of_its_values() -> None:
    """Half a comparison is the wrong-unit failure waiting to happen."""

    timeline = (
        _change(10.0, ControlInput.CARDIAC_OUTPUT, 5.0, 2.5, adjustment=1),
        _change(20.0, ControlInput.DELIVERED, 0.02, 0.04, adjustment=2),
    )

    for adjustment in group_adjustments(timeline):
        rendered = format_adjustment(adjustment)
        before, after = rendered.split(" -> ")
        assert before.endswith(("L/min", "%", "L"))
        assert after.endswith(("L/min", "%", "L"))


def test_a_rendered_line_uses_only_glyphs_the_interface_can_draw() -> None:
    """The arrow is the one that bit: U+2192 draws as a replacement box.

    No test in this repository renders a font, so this cannot check what
    the client can draw - it pins the characters a rendered frame has
    confirmed instead. `·`, `–` and `%` were read off a real frame on
    2026-09-04; `→` was read off the same frame as tofu, which put the
    direction of the change - the whole point of the line - in front of the
    reader as a missing character.
    """

    timeline = (
        _change(10.0, ControlInput.DELIVERED, 0.02, 0.03, adjustment=1),
        _change(10.2, ControlInput.DELIVERED, 0.03, 0.04, adjustment=1),
    )
    confirmed = set(" ·–->()sL/min%0123456789.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    for adjustment in group_adjustments(timeline):
        assert set(format_adjustment(adjustment)) <= confirmed
