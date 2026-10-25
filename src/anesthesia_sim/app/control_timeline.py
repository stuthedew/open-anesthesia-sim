"""Turn the recorded control-input timeline into what a reader sees.

This module shapes the `ControlChange` records of `control_record.py` for
the two places they are displayed: the marks on the chart and the list
beside it. Nothing here reads simulation state, stores a setting, or
performs a physiological calculation. The one unit conversion is from a
fraction to the percent that the delivered dial is displayed in, and
`formatting.py` performs it rather than this module spelling it out again.

This module is separate from the view for the same reason that
`chart_frame.py` and `formatting.py` are: what the timeline *means* is a
presentation-correctness concern rather than a layout one. The record that
the controller keeps is faithful to the run. It has one entry per setting
the model integrated under, so re-applying it reproduces the run. That is
not the same thing as a list a learner can read. A drag of one slider is
one act by the person but several settings to the model, and this module
is where the model's several settings become the person's one act.

**Grouping is exact, not inferred.** An adjustment is the set of changes
that share a `ControlChange.adjustment` number. The controller assigns that
number from an input boundary that the interface declares. Nothing here
guesses at a gesture from the spacing of the entries. The run's own
playback rate changes how much simulated time a drag spans, so any time
threshold would group correctly at one speed and wrongly at another.

**What a displayed adjustment asserts.** It asserts that the named control
moved from one value to another, over the simulated interval shown, in the
number of settings the model was stepped under. It asserts nothing about
what the patient did in that interval, which the compartment traces show.
It is a record of an input, not of a measurement.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.formatting import format_elapsed, format_flow, format_percent
from anesthesia_sim.core.concentration import Percent, fraction_from_percent
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant

__all__ = [
    "CONTROL_INPUT_LABELS",
    "AdjustmentGrouping",
    "ControlAdjustment",
    "format_adjustment",
    "format_control_value",
    "group_adjustments",
    "wrapping_between_parts",
]

#: The separators between a rendered line's parts: the one after the time,
#: and the arrow between the old value and the new one.
_AFTER_TIME: Final = " · "
_ARROW: Final = " -> "
_NO_BREAK_SPACE: Final = "\u00a0"

# What each control is called on screen. This is a second table beside
# `control_record.CONTROL_INPUT_UNITS` rather than a field on it, because the
# two belong to different owners. The unit belongs to the model and may not
# change without changing what is stored. The label belongs to the
# interface and may be reworded freely. Keeping them apart stops a wording
# change from looking like a change to the record.
#
# The label says "Delivered agent" rather than "vaporizer" because the model
# applies a delivered concentration, and a real vaporizer's dial is only one
# machine's way of setting it. The slider beside the chart also names the
# agent (`format_delivered_label`). This table cannot, since a timeline
# outlives the agent that recorded it only by being cleared with the run.
CONTROL_INPUT_LABELS: Final[Mapping[ControlInput, str]] = {
    ControlInput.FRESH_GAS_FLOW: "Fresh gas flow",
    ControlInput.DELIVERED: "Delivered agent",
    ControlInput.ALVEOLAR_VENTILATION: "Alveolar ventilation",
    ControlInput.CARDIAC_OUTPUT: "Cardiac output",
}


@dataclass(frozen=True, slots=True)
class ControlAdjustment:
    """One act by the user, however many settings the model saw for it.

    Raises:
        TypeError: If `started_at_s` or `ended_at_s` was not built as a
            `CaseInstant`, because then nothing has checked it against the
            supported run length (`core/supported_ranges.py`, `PL-RCYZ`).
    """

    control: ControlInput
    started_at_s: CaseInstant
    """Simulated time at which the first change of this adjustment took effect."""
    ended_at_s: CaseInstant
    """Simulated time at which the last change of this adjustment took effect.

    It equals `started_at_s` for a single-change adjustment, which is the
    ordinary case for a key press or a click on a slider track."""
    from_value: float
    """The value in place before the adjustment, in the control's own unit."""
    to_value: float
    """The value in place after the adjustment, in the same unit."""
    unit: str
    change_count: int
    """How many settings the model was stepped under during the adjustment.

    The count is one for a discrete input, and more for a drag. Each of a
    drag's settings is one that the run really was computed with. That is
    why the count is displayed rather than hidden: an adjustment made over
    eight settings is not the same run as one made in a single step, even
    where the endpoints match.
    """

    def __post_init__(self) -> None:
        require_case_instant("started_at_s", self.started_at_s)
        require_case_instant("ended_at_s", self.ended_at_s)


def group_adjustments(timeline: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
    """Collapse a recorded timeline into the acts that produced it.

    The result is oldest first. That matches the order in which the changes
    were recorded and the direction in which the chart's time axis runs.

    Args:
        timeline: Recorded changes, oldest first, as
            `SimulationSnapshot.control_timeline` supplies them.

    Returns:
        One `ControlAdjustment` per distinct `ControlChange.adjustment`,
        in first-appearance order.
    """

    adjustments: list[ControlAdjustment] = []
    open_adjustment: int | None = None

    for change in timeline:
        if change.adjustment == open_adjustment:
            latest = adjustments[-1]
            adjustments[-1] = ControlAdjustment(
                control=latest.control,
                started_at_s=latest.started_at_s,
                ended_at_s=change.elapsed_s,
                from_value=latest.from_value,
                to_value=change.new_value,
                unit=latest.unit,
                change_count=latest.change_count + 1,
            )
            continue

        open_adjustment = change.adjustment
        adjustments.append(
            ControlAdjustment(
                control=change.control,
                started_at_s=change.elapsed_s,
                ended_at_s=change.elapsed_s,
                from_value=change.previous_value,
                to_value=change.new_value,
                unit=change.unit,
                change_count=1,
            )
        )

    return tuple(adjustments)


class AdjustmentGrouping:
    """Group a run's timeline once per change to it, not once per frame.

    `group_adjustments` is O(entries) and allocates one `ControlAdjustment`
    per act, and `SimulationView._refresh_view` needs its result on every
    frame. The record it reads belongs to the *run*, though, not to the
    frame. Nearly every frame follows one in which nobody touched a control,
    and recomputing an identical result for those frames is the whole of
    the cost. Measured against a synthetic timeline on this project's
    supported Python, one call takes 0.88 ms at 1,000 entries, 8.8 ms at
    10,000 and 94.6 ms at 100,000, against a 200 ms render frame
    (`RENDER_INTERVAL_S`). With one of these objects in place, a frame that
    recorded nothing costs nothing, however much the run has accumulated.

    **The cache key is the timeline object's identity, and deliberately not
    its length.** `SimulationController` never changes the record in place.
    The record is a tuple, and every change replaces it whole. So `is`
    decides exactly whether anything changed, in constant time. Keeping a
    reference to the tuple also stops its address from being reused while
    the comparison depends on it.

    This cache must not use length as its key, and the reason is a
    displayed value, not a missed optimisation.
    `SimulationController._record_control_change` *replaces* the newest
    entry when one control moves twice inside a single simulation step,
    because the run was integrated only under the value in place when the
    step ran. That leaves the timeline the same length but a different
    record. Keyed on length, this cache would go on returning the superseded
    grouping. The panel beside the chart would then state a value the run
    was never computed under, and the mark on the chart would represent it.
    A stale displayed input is a presentation-correctness failure of the
    kind that `CLAUDE.md` classes as safety-critical, so the exact key is
    the only one available here.

    A cache miss in the other direction is harmless, and it is what the
    identity key gives up in exchange for exactness. A timeline rebuilt with
    identical content is a different object and is regrouped. That costs
    one call and cannot display anything untrue.

    This is not a `functools.lru_cache` on the function, for two reasons.
    Hashing a timeline to look it up is itself O(entries), which is the cost
    being removed. And a module-level cache would keep every run's record
    for the life of the process, instead of being cleared with the view that
    owns it.
    """

    __slots__ = ("_adjustments", "_timeline")

    def __init__(self) -> None:
        # The starting timeline is `()` rather than `None`. An empty run is
        # the state that both a fresh view and a reset view are in, and it
        # groups to `()` either way. So the first frame of an untouched run is
        # a cache hit rather than a special case.
        self._timeline: Sequence[ControlChange] = ()
        self._adjustments: tuple[ControlAdjustment, ...] = ()

    def of(self, timeline: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
        """Return the adjustments in `timeline`, regrouping only if it has changed.

        Args:
            timeline: Recorded changes, oldest first, exactly as
                `group_adjustments` takes them. There must be one object per
                state of the run, which is what makes the identity test above
                sound.

        Returns:
            What `group_adjustments(timeline)` returns. Repeated calls on one
            timeline return the same tuple object, so a caller may compare
            results by identity to learn whether the run changed.
        """

        if timeline is not self._timeline:
            self._timeline = timeline
            self._adjustments = group_adjustments(timeline)

        return self._adjustments


def format_control_value(control: ControlInput, value: float) -> str:
    """Render one recorded value in the unit a reader expects to see it in.

    Every control is stored in the unit the core is set with, so that
    re-applying a timeline is a sequence of setter calls. For the delivered
    dial, that unit is the percent it was set to (`PL-NJPB`). The value is
    displayed through `format_percent`, as every other concentration on the
    page is, so the timeline and the readouts cannot come to state one
    quantity at two resolutions. That formatter takes the model's fraction,
    so the recorded percent is converted to a fraction on its way in.

    Args:
        control: Which setting the value belongs to.
        value: The recorded value, in that control's stored unit.

    Returns:
        The value with its displayed unit.
    """

    # Every remaining control is a flow in L/min, so `format_flow` covers
    # all three. A `CIRCUIT_VOLUME` branch that rendered litres was here until
    # `PL-GYH2` retired that control. Nothing recorded under it can reach
    # this function any more, and a formatter for a control that cannot be
    # changed would be a unit rule with no value to apply it to.
    if control is ControlInput.DELIVERED:
        # This is the only control whose recorded value is a concentration
        # rather than a flow, and naming the type here asserts that.
        # `ControlChange.previous_value` and `ControlChange.new_value` are
        # the same two fields for all four controls, so the fields cannot
        # carry the distinction themselves.
        return format_percent(fraction_from_percent(Percent(value)))

    return format_flow(value)


def format_adjustment(adjustment: ControlAdjustment) -> str:
    """Render one adjustment as the line the interface shows.

    The interval is shown as a range only where the adjustment spans one,
    so a single discrete input is shown as the instant it happened.

    Args:
        adjustment: The adjustment to render.

    Returns:
        One line: when, which control, and from what to what. Where the
        model was stepped under more than one setting, the line also says
        how many.
    """

    when = format_elapsed(adjustment.started_at_s)

    if adjustment.ended_at_s != adjustment.started_at_s:
        when = f"{when}–{format_elapsed(adjustment.ended_at_s)}"

    label = CONTROL_INPUT_LABELS[adjustment.control]
    # ASCII rather than U+2192. The Flutter client this interface renders in
    # has no glyph for the arrow and draws a replacement box in its place.
    # The arrow shows the direction of the change, which is the one thing
    # this line exists to state, so the reader would see that direction as a
    # missing character. This was found by rendering the running app. No
    # test in this repository would have caught it, because every assertion
    # here compares strings produced by the same process, which has no fonts.
    moved = (
        f"{format_control_value(adjustment.control, adjustment.from_value)}{_ARROW}"
        f"{format_control_value(adjustment.control, adjustment.to_value)}"
    )

    if adjustment.change_count == 1:
        return f"{when}{_AFTER_TIME}{label} {moved}"

    return f"{when}{_AFTER_TIME}{label} {moved} ({adjustment.change_count} settings)"


def wrapping_between_parts(lines: str) -> str:
    """Return rendered lines that a wrapping label may break only between their parts.

    The record column is narrower than its longest lines, so its label wraps
    (`PL-F2YS`). A wrap at any space could leave "4.0" at the end of one line
    and "L/min" at the start of the next. A value cut off from its unit is a
    misreading, and `PL-3355` stopped the readouts from wrapping to prevent
    it. So every space becomes a no-break space except the one after the
    time and the one after the arrow. A long line then breaks into three
    parts: when it was, which control moved and from what value, and the
    value it moved to.

    Args:
        lines: Lines as `format_adjustment` renders them, joined by newlines.

    Returns:
        The same text, with the same characters a reader sees.
    """

    return "\n".join(_wrapping_between_parts(line) for line in lines.split("\n"))


def _wrapping_between_parts(line: str) -> str:
    """Return one line as `wrapping_between_parts` returns it.

    A line without the separator that follows the time is not an
    adjustment, and it is returned unchanged. The text shown before any
    control has changed is one such line.
    """

    if _AFTER_TIME not in line:
        return line

    unbroken = line.replace(" ", _NO_BREAK_SPACE)

    for joint in (_AFTER_TIME, _ARROW):
        held = joint.rstrip().replace(" ", _NO_BREAK_SPACE)
        unbroken = unbroken.replace(held + _NO_BREAK_SPACE, held + " ")

    return unbroken
