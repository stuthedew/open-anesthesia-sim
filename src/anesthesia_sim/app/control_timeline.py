"""Turn the recorded control-input timeline into what a reader sees.

The shaping layer between `control_record.py`'s `ControlChange` and the
two places it is displayed: the marks on the chart and the list beside it.
Nothing here reads simulation state, holds a setting, or performs a
physiological calculation - the one unit conversion is the
fraction-to-percent the delivered dial is displayed in, and it is delegated
to `formatting.py` rather than spelled out again.

It is separate from the view for the reason `chart_frame.py` and
`formatting.py` are: what the timeline *means* is a
presentation-correctness concern rather than a layout one. The record the
controller keeps is faithful to the run - one entry per setting the model
integrated under, so re-applying it reproduces the run - and that is not
the same thing as a list a learner can read. A drag of one slider is one
act by the person and several settings to the model, and this module is
where the second becomes the first.

**Grouping is exact, not inferred.** An adjustment is the set of changes
sharing a `ControlChange.adjustment` number, which the controller assigns
from an input boundary the interface declares. Nothing here guesses at a
gesture from the spacing of the entries: the run's own playback rate
changes how much simulated time a drag spans, so any time threshold would
group correctly at one speed and wrongly at another.

**What a displayed adjustment asserts.** That the named control moved from
one value to another, over the simulated interval shown, in the number of
settings the model was stepped under. It asserts nothing about what the
patient did in that interval - the compartment traces are where that is
read - and it is a record of an input rather than of a measurement.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.formatting import format_elapsed, format_flow, format_percent
from anesthesia_sim.core.concentration import Fraction

__all__ = [
    "CONTROL_INPUT_LABELS",
    "AdjustmentGrouping",
    "ControlAdjustment",
    "format_adjustment",
    "format_control_value",
    "group_adjustments",
]

# What each control is called on screen. A second table beside
# `control_record.CONTROL_INPUT_UNITS` rather than a field on it, because the
# two answer to different masters: the unit is the model's and may not
# change without changing what is stored, while the label is the
# interface's and may be reworded freely. Keeping them apart is what stops
# a wording change looking like a change to the record.
#
# "Delivered agent" rather than "vaporizer": the model applies a delivered
# concentration, and a real vaporizer's dial is one machine's way of
# setting it. The slider beside the chart names the agent as well
# (`format_delivered_label`), which this cannot, since a timeline outlives
# the agent that recorded it only by being cleared with the run.
CONTROL_INPUT_LABELS: Final[Mapping[ControlInput, str]] = {
    ControlInput.FRESH_GAS_FLOW: "Fresh gas flow",
    ControlInput.DELIVERED: "Delivered agent",
    ControlInput.ALVEOLAR_VENTILATION: "Alveolar ventilation",
    ControlInput.CARDIAC_OUTPUT: "Cardiac output",
}


@dataclass(frozen=True, slots=True)
class ControlAdjustment:
    """One act by the user, however many settings the model saw for it."""

    control: ControlInput
    started_at_s: float
    """Simulated time the first change of this adjustment took effect."""
    ended_at_s: float
    """Simulated time the last one did. Equal to `started_at_s` for a
    single-change adjustment, which is the ordinary case for a keyboard
    press or a click on a slider track."""
    from_value: float
    """The value in place before the adjustment, in the control's own unit."""
    to_value: float
    """The value in place after it, in the same unit."""
    unit: str
    change_count: int
    """How many settings the model was stepped under during the adjustment.

    One for a discrete input. More for a drag, where each is a setting the
    run really was computed with - which is why the count is displayed
    rather than hidden: an adjustment made over eight settings is not the
    same run as one made in a single step, even where the endpoints match.
    """


def group_adjustments(timeline: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
    """Collapse a recorded timeline into the acts that produced it.

    Oldest first, matching the order the changes were recorded in and the
    direction the chart's time axis runs.

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
    frame. The record it reads is a property of the *run*, though, not of
    the frame: the overwhelming majority of frames follow one in which
    nobody touched a control, and recomputing an identical answer for them
    is the whole of the cost. Measured against a synthetic timeline on this
    project's supported Python: 0.88 ms per call at 1,000 entries, 8.8 ms
    at 10,000 and 94.6 ms at 100,000, against a 200 ms render frame
    (`RENDER_INTERVAL_S`). Holding one of these makes a frame that recorded
    nothing cost nothing, whatever the run has accumulated.

    **The key is the timeline object's identity, and deliberately not its
    length.** `SimulationController` never mutates the record in place - it
    is a tuple, and every change replaces it whole - so `is` decides
    exactly whether anything changed, in constant time, and holding the
    tuple keeps its address from being reused underneath the comparison.

    Length is the key this cache must not use, and the reason is a
    displayed value rather than a missed optimisation.
    `SimulationController._record_control_change` *replaces* the newest
    entry when one control moves twice inside a single simulation step,
    because the run was integrated only under the value standing when the
    step ran. That leaves the timeline the same length and a different
    record. Keyed on length, this would go on serving the superseded
    grouping: the panel beside the chart would state a value the run was
    never computed under, and the mark on the chart would stand for it. A
    stale displayed input is a presentation-correctness failure of the kind
    `CLAUDE.md` classes as safety-critical, so the exact key is the only
    one available here.

    Missing in the other direction is harmless and is what the identity key
    trades for exactness: a timeline rebuilt with identical content is a
    different object and is regrouped, which costs one call and cannot
    display anything untrue.

    Not a `functools.lru_cache` on the function: hashing a timeline to look
    it up is itself O(entries), which is the cost being removed, and a
    module-level cache would hold every run's record for the life of the
    process rather than being cleared with the view that owns it.
    """

    __slots__ = ("_adjustments", "_timeline")

    def __init__(self) -> None:
        # `()` rather than `None`: an empty run is the state a fresh view and
        # a reset one are both in, and it groups to `()` either way, so the
        # first frame of an untouched run is a hit rather than a special case.
        self._timeline: Sequence[ControlChange] = ()
        self._adjustments: tuple[ControlAdjustment, ...] = ()

    def of(self, timeline: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
        """The adjustments in `timeline`, regrouped only if it has changed.

        Args:
            timeline: Recorded changes, oldest first, exactly as
                `group_adjustments` takes them - and as one object per state
                of the run, which is what makes the identity test above
                sound.

        Returns:
            What `group_adjustments(timeline)` returns. The same tuple
            object is returned for repeated calls on one timeline, so a
            caller may compare results by identity to learn whether the run
            changed.
        """

        if timeline is not self._timeline:
            self._timeline = timeline
            self._adjustments = group_adjustments(timeline)

        return self._adjustments


def format_control_value(control: ControlInput, value: float) -> str:
    """Render one recorded value in the unit a reader expects to see it in.

    The stored unit and the displayed unit differ for exactly one control.
    The delivered dial is stored as the fraction the core is set with, so
    that re-applying a timeline is a sequence of setter calls, and it is
    displayed as the percent every other concentration on the page is
    displayed as - through `format_percent`, so the timeline and the
    readouts cannot come to state one quantity at two resolutions.

    Args:
        control: Which setting the value belongs to.
        value: The recorded value, in that control's stored unit.

    Returns:
        The value with its displayed unit.
    """

    # Every remaining control is a flow in L/min, so `format_flow` covers
    # all three. A `CIRCUIT_VOLUME` branch rendering litres stood here until
    # `PL-GYH2` retired that control; nothing recorded under it can reach
    # this function any more, and a formatter for a control that cannot be
    # changed is a unit rule with no value to apply it to.
    if control is ControlInput.DELIVERED:
        # The only control whose recorded value is a concentration rather
        # than a flow, which is what naming the type here asserts.
        # `ControlChange.value` is one field for four controls, so it
        # cannot carry the distinction itself.
        return format_percent(Fraction(value))

    return format_flow(value)


def format_adjustment(adjustment: ControlAdjustment) -> str:
    """Render one adjustment as the line the interface shows.

    The interval is stated as a range only where the adjustment spans one,
    so a single discrete input reads as the instant it was.

    Args:
        adjustment: The adjustment to render.

    Returns:
        One line: when, which control, from what to what, and - where the
        model was stepped under more than one setting - how many.
    """

    when = format_elapsed(adjustment.started_at_s)

    if adjustment.ended_at_s != adjustment.started_at_s:
        when = f"{when}–{format_elapsed(adjustment.ended_at_s)}"

    label = CONTROL_INPUT_LABELS[adjustment.control]
    # ASCII rather than U+2192. The Flutter client this interface renders in
    # has no glyph for the arrow and draws a replacement box in its place,
    # which is the direction of the change - the one thing this line exists
    # to state - reaching the reader as a missing character. Found by
    # rendering the running app, which no test in this repository would have
    # caught: every assertion here compares strings the same font-less
    # process produced.
    moved = (
        f"{format_control_value(adjustment.control, adjustment.from_value)} -> "
        f"{format_control_value(adjustment.control, adjustment.to_value)}"
    )

    if adjustment.change_count == 1:
        return f"{when} · {label} {moved}"

    return f"{when} · {label} {moved} ({adjustment.change_count} settings)"
