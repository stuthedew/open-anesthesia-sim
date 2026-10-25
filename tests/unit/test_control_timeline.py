"""Tests of how the recorded control-input timeline is shown on screen."""

import pytest

from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlChange, ControlInput
from anesthesia_sim.app.control_timeline import (
    CONTROL_INPUT_LABELS,
    AdjustmentGrouping,
    ControlAdjustment,
    format_adjustment,
    format_control_value,
    group_adjustments,
    wrapping_between_parts,
)
from anesthesia_sim.app.dashboard_frame import NO_CONTROL_CHANGES_TEXT
from anesthesia_sim.core.supported_ranges import CaseInstant

#: U+00A0, the no-break space. It is written out here rather than imported, so
#: the tests below do not rely on the module to say which character keeps two
#: words together.
_NBSP = "\u00a0"


def _change(
    elapsed_s: float,
    control: ControlInput,
    previous_value: float,
    new_value: float,
    adjustment: int,
) -> ControlChange:
    return ControlChange(
        elapsed_s=CaseInstant(elapsed_s),
        adjustment=adjustment,
        control=control,
        previous_value=previous_value,
        new_value=new_value,
        unit=CONTROL_INPUT_UNITS[control],
    )


def test_a_recorded_change_and_an_adjustment_refuse_an_instant_not_built_as_one() -> None:
    """A record stamped with a bare number has had no check against the run length.

    The controller stamps every change with the running state's instant,
    which is already a `CaseInstant`. A caller building a record itself, such
    as a notebook, could otherwise list a change a billion seconds past the
    24 h supported run length, or at `nan`, in the control-change panel
    (`PL-RCYZ`).
    """

    with pytest.raises(TypeError, match="elapsed_s of 1000000000.0 was not built as CaseInstant"):
        ControlChange(
            elapsed_s=1e9,  # type: ignore[arg-type]
            adjustment=1,
            control=ControlInput.FRESH_GAS_FLOW,
            previous_value=6.0,
            new_value=2.0,
            unit=CONTROL_INPUT_UNITS[ControlInput.FRESH_GAS_FLOW],
        )

    with pytest.raises(TypeError, match="started_at_s of nan was not built as CaseInstant"):
        ControlAdjustment(
            ControlInput.FRESH_GAS_FLOW,
            float("nan"),  # type: ignore[arg-type]
            CaseInstant(60.0),
            6.0,
            2.0,
            "L/min",
            1,
        )

    with pytest.raises(TypeError, match="ended_at_s of -60.0 was not built as CaseInstant"):
        ControlAdjustment(
            ControlInput.FRESH_GAS_FLOW,
            CaseInstant(60.0),
            -60.0,  # type: ignore[arg-type]
            6.0,
            2.0,
            "L/min",
            1,
        )


def test_grouping_hands_the_recorded_instants_through_as_case_instants() -> None:
    timeline = (
        _change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 3.0, adjustment=1),
        _change(12.1, ControlInput.FRESH_GAS_FLOW, 3.0, 2.0, adjustment=1),
    )

    (adjustment,) = group_adjustments(timeline)

    assert type(adjustment.started_at_s) is CaseInstant
    assert type(adjustment.ended_at_s) is CaseInstant


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
    """The endpoints come from the person, and the count comes from the model.

    Both are displayed because they are different claims: what the user
    did, and how many settings the run was actually computed under.
    """

    timeline = (
        _change(10.0, ControlInput.DELIVERED, 2.0, 2.5, adjustment=1),
        _change(10.1, ControlInput.DELIVERED, 2.5, 3.1, adjustment=1),
        _change(10.2, ControlInput.DELIVERED, 3.1, 4.0, adjustment=1),
    )

    (adjustment,) = group_adjustments(timeline)

    assert adjustment.started_at_s == 10.0
    assert adjustment.ended_at_s == 10.2
    assert adjustment.from_value == 2.0
    assert adjustment.to_value == 4.0
    assert adjustment.change_count == 3


def test_two_adjustments_of_one_control_stay_two() -> None:
    """The grouping follows the recorded adjustment number, never the timing.

    No rule that reads only the entries can tell two turns of one dial from one
    turn. That is why the controller records the boundary, instead of this
    module inferring it.
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
    """The setting is stored as the percent dialled (`PL-NJPB`) and shown as a percent.

    It is displayed through the same formatter as every other concentration on
    the page. That formatter takes the model's fraction, so the recorded
    percent is converted before it goes in. Formatted without that conversion,
    a 2% setting would show "200.00%" beside readouts that show "2.00%".
    """

    assert format_control_value(ControlInput.DELIVERED, 2.0) == "2.00%"


def test_flow_settings_are_displayed_in_the_unit_their_sliders_are() -> None:
    assert format_control_value(ControlInput.FRESH_GAS_FLOW, 4.0) == "4.0 L/min"
    assert format_control_value(ControlInput.ALVEOLAR_VENTILATION, 4.0) == "4.0 L/min"
    assert format_control_value(ControlInput.CARDIAC_OUTPUT, 5.0) == "5.0 L/min"


def test_every_control_has_a_label_and_a_unit() -> None:
    """`PL-GYH2` removed a member, and the three tables must stay in step.

    `ControlInput`, `CONTROL_INPUT_UNITS` and `CONTROL_INPUT_LABELS` are
    written separately on purpose, because the unit belongs to the model and
    the label belongs to the interface. So only this test keeps them to the
    same set of controls. A member left in one table after it was retired from
    the enum would give a displayed line with no unit, or a unit with nothing
    to put it on.
    """

    assert set(CONTROL_INPUT_LABELS) == set(ControlInput)
    assert set(CONTROL_INPUT_UNITS) == set(ControlInput)


def test_a_single_change_reads_as_the_instant_it_was() -> None:
    timeline = (_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)

    (adjustment,) = group_adjustments(timeline)

    assert format_adjustment(adjustment) == "12s · Fresh gas flow 4.0 L/min -> 2.0 L/min"


def test_a_multi_setting_adjustment_states_its_span_and_its_count() -> None:
    timeline = (
        _change(10.0, ControlInput.DELIVERED, 2.0, 3.0, adjustment=1),
        _change(10.2, ControlInput.DELIVERED, 3.0, 4.0, adjustment=1),
    )

    (adjustment,) = group_adjustments(timeline)

    assert format_adjustment(adjustment) == (
        "10s–10.2s · Delivered agent 2.00% -> 4.00% (2 settings)"
    )


def test_a_rendered_adjustment_carries_a_unit_on_both_of_its_values() -> None:
    """A comparison with a unit on only one side invites a wrong-unit reading."""

    timeline = (
        _change(10.0, ControlInput.CARDIAC_OUTPUT, 5.0, 2.5, adjustment=1),
        _change(20.0, ControlInput.DELIVERED, 2.0, 4.0, adjustment=2),
    )

    for adjustment in group_adjustments(timeline):
        rendered = format_adjustment(adjustment)
        before, after = rendered.split(" -> ")
        assert before.endswith(("L/min", "%", "L"))
        assert after.endswith(("L/min", "%", "L"))


def test_a_rendered_line_uses_only_glyphs_the_interface_can_draw() -> None:
    """The arrow caused the failure: U+2192 draws as a replacement box.

    No test in this repository renders a font, so this test cannot check what
    the client can draw. Instead, it pins the characters that a rendered frame
    has confirmed. `·`, `–` and `%` were seen drawn correctly on a real frame on
    2026-09-04. On the same frame, `→` drew as tofu, an empty box. So the
    direction of the change, which is the whole point of the line, reached the
    reader as a missing character.
    """

    timeline = (
        _change(10.0, ControlInput.DELIVERED, 2.0, 3.0, adjustment=1),
        _change(10.2, ControlInput.DELIVERED, 3.0, 4.0, adjustment=1),
    )
    confirmed = set(" ·–->()sL/min%0123456789.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    for adjustment in group_adjustments(timeline):
        assert set(format_adjustment(adjustment)) <= confirmed


def test_an_unchanged_record_is_grouped_once_rather_than_once_per_frame() -> None:
    """The cache saves work only on a frame that recorded nothing.

    The test asserts the identity of the returned tuple rather than a call
    count, because the view depends on that property. The panel, the chart
    marks and the discard warning must all receive the same adjustments, from
    one grouping of one record.
    """

    grouping = AdjustmentGrouping()
    timeline = (
        _change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
        _change(20.0, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=2),
    )

    first = grouping.of(timeline)

    assert grouping.of(timeline) is first
    assert grouping.of(timeline) is first
    assert first == group_adjustments(timeline)


def test_a_superseded_change_is_regrouped_though_the_record_did_not_grow() -> None:
    """This is why the cache key is the record's identity and not its length.

    `SimulationController._record_control_change` replaces the newest entry
    when one control moves twice inside a single simulation step, because
    the run was integrated only under the value in effect when the step ran.
    The record is then the same length and a different record. A cache
    keyed on length would go on serving the superseded grouping, and the
    panel beside the chart would state a value the run was never computed
    under.
    """

    grouping = AdjustmentGrouping()
    superseded = (_change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)
    standing = (_change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 3.0, adjustment=1),)

    assert len(superseded) == len(standing)
    assert grouping.of(superseded)[0].to_value == 2.0
    assert grouping.of(standing)[0].to_value == 3.0


def test_a_run_that_has_recorded_nothing_needs_no_grouping_at_all() -> None:
    """A fresh view and a reset view are both in this state."""

    grouping = AdjustmentGrouping()

    assert grouping.of(()) == ()
    assert grouping.of(()) == ()


def test_a_grouping_does_not_answer_for_another_run() -> None:
    """Clearing the record is what `reset()` and a change of agent do.

    An empty timeline is a legitimate state to arrive back at, so the cache
    has to serve it rather than treat it as nothing to do.
    """

    grouping = AdjustmentGrouping()
    timeline = (_change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)

    assert len(grouping.of(timeline)) == 1
    assert grouping.of(()) == ()
    assert len(grouping.of(timeline)) == 1


# --- wrapping the record column's lines (`PL-F2YS`) ---------------------------


def test_a_flow_line_breaks_only_after_its_time_and_after_its_arrow() -> None:
    """A wrap never separates a value from its unit (`PL-3355`)."""

    line = "12s · Fresh gas flow 4.0 L/min -> 2.0 L/min"

    assert wrapping_between_parts(line).split(" ") == [
        f"12s{_NBSP}·",
        f"Fresh{_NBSP}gas{_NBSP}flow{_NBSP}4.0{_NBSP}L/min{_NBSP}->",
        f"2.0{_NBSP}L/min",
    ]


def test_a_multi_setting_line_keeps_its_count_with_the_new_value() -> None:
    line = "10s–10.2s · Delivered agent 2.00% -> 4.00% (2 settings)"

    assert wrapping_between_parts(line).split(" ") == [
        f"10s–10.2s{_NBSP}·",
        f"Delivered{_NBSP}agent{_NBSP}2.00%{_NBSP}->",
        f"4.00%{_NBSP}(2{_NBSP}settings)",
    ]


def test_wrapping_changes_no_character_a_reader_sees() -> None:
    """Three lines are used, so a change to only the first or the last line would show."""

    timeline = (
        _change(10.0, ControlInput.CARDIAC_OUTPUT, 5.0, 2.5, adjustment=1),
        _change(20.0, ControlInput.DELIVERED, 2.0, 4.0, adjustment=2),
        _change(30.0, ControlInput.ALVEOLAR_VENTILATION, 4.0, 6.0, adjustment=3),
    )
    lines = "\n".join(format_adjustment(a) for a in group_adjustments(timeline))

    wrapped = wrapping_between_parts(lines)

    assert wrapped.replace(_NBSP, " ") == lines
    assert len(wrapped.splitlines()) == 3
    assert all(line.count(" ") == 2 for line in wrapped.splitlines())


def test_a_line_that_records_no_change_is_left_as_it_is() -> None:
    """The text shown before any setting has changed is a sentence, so it may wrap freely."""

    assert wrapping_between_parts(NO_CONTROL_CHANGES_TEXT) == NO_CONTROL_CHANGES_TEXT
