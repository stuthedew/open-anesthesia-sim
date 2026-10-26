"""A run held as the settings it was computed under, rather than as samples of itself.

The governing equations in `docs/MODEL.md` are linear and time-invariant while
every setting stays constant. So `matrix_exponential` solves each such stretch
exactly, over any horizon. A run is therefore described completely by the
settings in force at each moment, which this module calls the run's
*definition*. Every state the run passed through is a closed-form function of
that definition and of the time asked for. No state has to be recorded for it
to be recovered later.

**What the name has to convey, and the term it replaced.** What is *stored* is
the ordered list of settings and the time at which each took effect. What a
caller asks for is *derived* by playing that list forward to a given instant.
Reject names that suggest a stored trajectory, such as a run's `history`,
`samples` or `record`. The whole point is that no stored trajectory exists
here.

Through v0.4.x this quantity was called a run's *score*, in the musical sense.
A score is the written set of instructions that a performance is produced
from, not a recording of one. It is the same kind of borrowing that makes
`Keyframe` an animation term. The metaphor was exact, but it had to be taught.
`.claude/rules/core-domain.md` requires this package to read like the domain
without a translation step, so the word was retired for the plain one
(`PL-ZX12`, project owner, 2026-09-08). The old word is recorded here because
`docs/releases/` and the completed rows of `ROADMAP.md` still speak of the
score architecture. A reader arriving from those documents needs to know that
the two words name one thing.

This design has two consequences, and `PL-T691` exists for both of them:

- **Memory stops growing with the length of the run.** A recorded run costs
  one sample per solver step. A run definition costs one segment per setting
  change. As measured on 2026-09-05, a 30-day case with 50 changes a day needs
  about 70 KiB for its definition and keyframes. The same run recorded as
  samples today needs 3.16 GB.
- **The cost of computing a window stops depending on the run's length.** A
  window is computed from the keyframes that bracket it, not by scanning
  everything that came before it. So 600 columns cost the same over 30 days as
  over an hour.

**There are two evaluation paths, and they are not interchangeable.**
`state_at` is the canonical path. It forms one matrix exponential per interval
between events, and composes them in recording order from the run's opening.
So two evaluations of the same definition at the same instant perform the
identical sequence of operations and agree bit for bit. `evaluate` is the
display path. Inside one segment it reuses a single propagator across
uniformly spaced columns. That reuse is what makes a frame cheap, and it also
composes the operations in a different order. So the two paths agree only to
within floating-point composition error, not exactly.

**The chart's path keeps the propagators it used from one call to the next.**
Each frame asks `evaluate_anchored` for nearly the same propagators as the
frame before it. A propagator is a function of a stretch's settings and an
interval, and of nothing else. So a propagator kept under those two keys is,
bit for bit, the matrix that forming it again would give. Which propagators
are kept depends on the window drawn last, but no drawn value can depend on
which propagators are kept. Only the last window's propagators are kept, so the store is not a
record of the run (`.claude/rules/run-is-its-definition.md` says why that is
where the line falls). `state_at` reads none of the store.

`docs/MODEL.md` § "The canonical evaluation rule" states that separation as a
guarantee. Every stored, exported, replayed or forked value is taken
canonically. A display value may be drawn and used for nothing else. **This
module enforces the rule rather than describing it.** `evaluate` returns its
states wrapped in `DisplayState`. A `DisplayState` is not a state vector, and
the canonical entry points refuse it by name. So a display value cannot become
a keyframe, an export or a fork's opening state just because it has the same
shape as one.

This module carries no compartment names, no units and no interface concepts.
It composes the propagators that `matrix_exponential` produces from the
matrices that `governing_equations` assembles. A state here is the state
vector of `governing_equations`, in that module's own order.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import inf, isfinite
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    UptakeEquationSettings,
    build_system_matrix,
    require_canonical_state,
)
from anesthesia_sim.core.matrix_exponential import Matrix, matrix_exponential, propagate
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant
from anesthesia_sim.core.validation import require_positive_finite

_PropagatorKey = tuple[UptakeEquationSettings, float]
"""A stretch's settings and an interval, which are everything a propagator is formed from."""

MAXIMUM_WINDOW_COLUMNS: Final = 100_000
"""The largest number of columns that one call to `evaluate` or `evaluate_anchored` may ask for.

A window costs one matrix-vector product per column, about 6.2 us each
(`PL-2FM6`), so this many columns take about 0.6 s. The chart asks for one
column per logical pixel of its plot (`app/chart_frame.py`, `chart_columns`).
An 8K display is 7 680 pixels wide at a device-pixel ratio of one, so a plot
across all of it asks for less than a tenth of the bound. The bound therefore
rejects no window that a chart draws. It exists so that a request too large for
any screen to show fails at once with a named error. Without it,
`evaluate_anchored` at a spacing of 1e-300 s over one second would loop about
1e300 times and never return (`PL-06LS`).

For `evaluate_anchored`, the bound counts the grid multiples after `start_s`
and up to `stop_s`, which is how many times `_anchored_columns` loops. A
multiple that falls on `stop_s` is drawn as the window's stop rather than as a
grid column, so the count can be one more than the grid columns drawn. The
window's start and the events inside it add columns beyond the count. The
run's own record limits the events, not the request.
"""


@dataclass(frozen=True, slots=True)
class Keyframe:
    """The exact state at one segment boundary, computed canonically.

    A run stores one keyframe at its opening and one at each setting change,
    and no other state. Every state between two keyframes is recovered by
    propagating the earlier one forward. That is why a keyframe is computed
    canonically even though the values drawn from it are not. An error in a
    keyframe is inherited by every value derived from it, while an error on
    the display path affects one column of one frame.

    Attributes:
        instant_s: The instant at which this state was reached, in seconds,
            on the case's own axis. That axis is simulated time since
            induction. It is not the time elapsed since the run holding the
            keyframe began. The two are the same number for a run that opens
            at induction, but not for a branch. A branch forked at 900 s opens
            with a keyframe stamped 900.0, although the branch has lasted no
            time at all.
        state: The state, in `governing_equations`' own state order,
            `STATE_SIZE` entries long. The two accumulator states are
            cumulative from the start of the *case*, not reset for each
            segment. Their rows in the system matrix have no diagonal entry,
            so a propagator maps each of them to itself with coefficient one.
            Carrying a running total through is therefore the same arithmetic
            as starting from zero and adding. The totals count from the start
            of the case, not from the start of the run that holds the
            keyframe. A branch opens carrying its parent's totals, so the
            accumulators in its first keyframe count litres delivered before
            the branch existed. That is intended. The agent a patient has
            received belongs to the case. A branch that restarted the count at
            zero would report a mass balance for a patient who does not exist.

    Raises:
        TypeError: `instant_s` is not a `CaseInstant`, so nothing has checked
            it against the supported run length (`core/supported_ranges.py`).
            The state is checked by the `RunDefinition` that holds it, which
            refuses a display value by name before anything reads it.
    """

    instant_s: CaseInstant
    state: tuple[float, ...]

    def __post_init__(self) -> None:
        require_case_instant("instant_s", self.instant_s)


@dataclass(frozen=True, slots=True)
class RunSegment:
    """One stretch of a run during which every setting the equations read is constant.

    The settings and the state they start from travel together, not in
    parallel lists. So a segment's settings cannot end up paired with another
    segment's opening state. That pairing would compute a stretch of the run
    from settings it was never under, and produce a plausible trajectory that
    never happened.

    Attributes:
        settings: The record that `build_system_matrix` assembles $`A`$ from.
            It is in force from `opening.instant_s` until the next segment
            begins. Its flows are the litres per minute that were set, and its
            delivered concentration is the percent that was dialled. So a
            system configured from them rebuilds these settings exactly
            (`PL-SM5V`, `PL-NJPB`). The vaporizer maximum that the dial was
            set under travels with the settings, and the record refuses a dial
            above that maximum (`PL-BBMG`).
        opening: The state at the segment's first instant.
    """

    settings: UptakeEquationSettings
    opening: Keyframe


@dataclass(frozen=True, slots=True)
class DisplayState:
    """A state produced by the display path, which the canonical path refuses to accept.

    It is a wrapper rather than a bare tuple, and deliberately not a tuple
    subclass. The separation that `docs/MODEL.md` § "The canonical evaluation
    rule" states has to hold at sinks that have never heard of this class,
    such as an exporter, a save format or a fork. Only a value that is
    structurally not a state vector is refused by all of them. A subclass
    would pass through every one of those sinks silently. It would be caught
    only by the checks that somebody remembered to write.

    Unwrapping is therefore explicit, and that is intended. Each read of
    `values` is a line where a reader can see a value meant for drawing being
    taken out of the one container that says what it is.

    Attributes:
        values: The state, in `governing_equations`' own state order,
            `STATE_SIZE` entries long. It equals the canonical state at the
            same instant only to within floating-point composition error, not
            exactly. The measured difference is in `docs/MODEL.md`.
    """

    values: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class SampledWindow:
    """The states at a run of uniformly spaced instants, for drawing.

    This is what the display path returns. Times and states travel together
    and are checked to be the same length at construction. They travel
    together for the same reason that `RunSegment` pairs its two fields. A
    trace drawn from one
    array against the other's time axis misstates the run from values that are
    each correct. `CLAUDE.md`'s safety-critical standard counts that as a
    presentation failure, not as a lesser kind of error.

    Attributes:
        times_s: The instants sampled, ascending, in seconds.
        states: One entry per instant, each a `DisplayState` carrying
            `STATE_SIZE` values in `governing_equations`' state order.

    Raises:
        SimulationConfigurationError: If the times and the states are not the
            same length.
    """

    times_s: tuple[float, ...]
    states: tuple[DisplayState, ...]

    def __post_init__(self) -> None:
        if len(self.times_s) != len(self.states):
            raise SimulationConfigurationError(
                f"a sampled window has {len(self.times_s)} instants and "
                f"{len(self.states)} states; each state belongs to one instant"
            )


class RunDefinition:
    """A run, as the settings it was computed under and the states they imply.

    It is built with the settings a run starts under and the state it starts
    from, and is then told what happened. `advance_to` moves the time the run
    has reached. `record_change` closes the open segment at that time and
    opens a new one under new settings. Those two calls are the whole of what
    a run *is*.

    **A change is recorded at the time the run has reached, and nowhere
    else.** `record_change` deliberately has no instant argument. A setting
    change takes effect when it is made. A caller free to name a different
    time could place a change inside a stretch already computed under other
    settings. That would not fail. It would return a trajectory the run never
    took, at full precision and with nothing to mark it as wrong. Removing the
    argument removes the failure, and `.claude/rules/expert-review.md` prefers
    that to validating the argument.

    **It returns states only within the run.** `state_at` and `evaluate`
    refuse a time past `reached_s`. The run definition could be evaluated
    arbitrarily far ahead, but what came back would be a prediction of a run
    that has not happened. Drawn on the same axis as the run itself, that
    prediction would be indistinguishable from the run.
    """

    __slots__ = ("_last_window_propagators", "_reached_s", "_segments")

    def __init__(
        self,
        settings: UptakeEquationSettings,
        initial_state: tuple[float, ...],
        *,
        opened_at_s: CaseInstant,
    ) -> None:
        """Open a run at `opened_at_s` under `settings`, from `initial_state`.

        **The opening instant is on the case's axis, and it is required.** A
        run that begins at induction opens at zero. A branch opens at the
        instant it was forked from. Both instants are on the same axis.
        Simulated time is measured from induction for both, because uptake is
        a function of time since induction and a branch is one patient's case
        continuing. The parameter deliberately has no default. A default of
        zero would be wrong in exactly one case, a branch. Being wrong there
        means a whole trajectory drawn under a patient context the case never
        had, with every value in it individually correct. `CLAUDE.md`'s
        safety-critical standard refuses a silently substituted default for
        that reason. So a caller must say which instant it means, and a caller
        that forgets gets a `TypeError` rather than a plausible run.

        Args:
            settings: The settings the run begins under. Their flows are
                inside the supported flow ranges by construction. Each flow is
                a checked type that cannot hold a value outside its range, so
                neither this method nor `record_change` checks a flow again
                (`PL-HSFV`). The dial can be delivered, by the same kind of
                construction. The record carries the vaporizer maximum beside
                the dial and refuses a dial above that maximum. So any record a
                run can be handed is one the circuit would have accepted
                (`PL-BBMG`).
            initial_state: The state at `opened_at_s`, in
                `governing_equations`' state order. Its accumulators hold the
                run's starting totals. They are zero for a run that has
                delivered nothing, and the parent's running totals for a fork.
            opened_at_s: The case instant at which this run opens, in seconds.
                It is zero for a run beginning at induction. For a branch, it
                is the instant of the parent keyframe that the branch carries
                as its `initial_state`. That keyframe is the fork itself for a
                branch taken at a control event, and the keyframe before the
                fork for a branch taken at a bookmark (`app/controller.py`,
                `SimulationController._open_at`). It is a `CaseInstant`, so it
                is at or after induction and inside the supported run length.
                That length belongs to the case, not to this run. A branch
                inherits this instant as the origin of everything it reports,
                so the instant is checked where the branch is built, not at
                the first step past it (`PL-73ZN`).

        Raises:
            TypeError: `opened_at_s` is not a `CaseInstant`, so nothing has
                checked it against the supported run length
                (`core/supported_ranges.py`).
            SimulationConfigurationError: `initial_state` came from the
                display path, is not `STATE_SIZE` long, holds a non-finite
                value, or does not carry exactly one in `UNIT_STATE`. The
                display-path case is a fork opening from a value meant for
                drawing, which `docs/MODEL.md` § "The canonical evaluation
                rule" refuses. Requiring exactly one in `UNIT_STATE` is what
                makes every forcing term in `build_system_matrix` mean what it says.
                A state that carried any other value there would scale the
                whole delivery term without changing any setting a reader can
                see.
        """

        _require_state(initial_state)
        require_case_instant("opened_at_s", opened_at_s)

        self._segments: tuple[RunSegment, ...] = (
            RunSegment(settings=settings, opening=Keyframe(opened_at_s, initial_state)),
        )
        self._reached_s = opened_at_s
        self._last_window_propagators: dict[_PropagatorKey, Matrix] = {}

    @property
    def opened_at_s(self) -> CaseInstant:
        """The case instant this run opens at: zero at induction, a parent keyframe for a branch.

        It is read from the first segment rather than stored beside it. So the
        run's opening is recorded in one place, with no second copy to fall
        out of step with it. `_require_within_run` reads the same field. That
        is why a caller may clip an axis to this instant and be sure that the
        call will not be refused.

        **It is the earliest instant from which this definition may be
        evaluated. On a branch, that instant is at or before the one where the
        branch itself began.** A branch taken at a bookmark opens here, at the
        keyframe before its fork, so that it propagates from the same keyframe
        as its parent. The stretch between that keyframe and the fork belongs
        to the parent, and the branch never lived it. That is why the app
        layer clips a drawn axis at the fork rather than here
        (`SimulationController.began_at_s`).
        """

        return self._segments[0].opening.instant_s

    @property
    def segments(self) -> tuple[RunSegment, ...]:
        """Every stretch of constant settings this run has had, oldest first."""

        return self._segments

    @property
    def reached_s(self) -> CaseInstant:
        """The simulated time the run has reached, in seconds."""

        return self._reached_s

    def advance_to(self, instant_s: CaseInstant) -> None:
        """Move the time the run has reached to `instant_s`.

        It records no state, because the states are already implied by the
        settings and are recovered on demand. What it changes is how far the
        run definition may be evaluated. That limit is what stops a prediction
        from being drawn as if it were the run.

        The time reached needs no lower bound of its own. `__init__` sets it
        from `opened_at_s`, and this method is its only other writer and never
        lowers it. That invariant is what lets `_require_within_run` treat the
        span from the opening to the time reached as a closed interval. So a
        second writer of `_reached_s`, such as a reset in place or a
        deserializer restoring a saved run, would have to re-establish the
        invariant rather than assume it.

        Its upper bound is the same as the opening's: the end of the supported
        run length. The `CaseInstant` type enforces that bound. A time past it
        cannot be built as a `CaseInstant` to pass in, so the run definition
        is never evaluated over a stretch the model is not claimed to cover.
        The application moves the time reached only to an instant that a step
        count lands on: the instant of each step, or of a branch's fork
        (`app/controller.py`). `SimulationState.advance` refuses the step that
        would carry that count past the span. So no step already taken lands
        on an instant that cannot be built. `maximum_step_count` decides which
        step is the last from the time at which that step lands, and that time
        is the instant passed here (`PL-8H2R`).

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`, so nothing has
                checked it against the supported run length
                (`core/supported_ranges.py`).
            SimulationConfigurationError: `instant_s` is earlier than the time
                already reached. A run cannot un-happen. Moving the time
                reached backwards would leave the segments recorded after it
                describing a stretch that the run definition would then refuse
                to evaluate. The check runs before the time reached moves, so
                a refused call leaves it where it was.
        """

        require_case_instant("instant_s", instant_s)

        if instant_s < self._reached_s:
            raise SimulationConfigurationError(
                f"a run cannot go back from {self._reached_s} s to {instant_s} s"
            )

        self._reached_s = instant_s

    def record_change(self, settings: UptakeEquationSettings) -> None:
        """Note that the run continues under `settings` from now on.

        "Now" is `reached_s`, the time the run has reached. The class
        docstring says why "now" is not an argument.

        Three kinds of call change nothing and open no new stretch. Each is
        handled that way for a reason about the run, not for tidiness. First,
        settings equal to the ones in force describe no change that the model
        would integrate differently, so the call is dropped. Second, a change
        at an instant where a stretch has already opened belongs to that same
        stretch. This happens when two controls are moved between one step and
        the next. The change replaces that stretch's settings instead of
        opening a zero-length one, because the run was computed under the
        settings in force when the step ran, which are the last ones written.
        Third, if that replacement lands back on the settings the previous
        stretch already had, the open stretch is removed entirely, because
        nothing about the run differs. This happens when a dial is moved and
        moved back before a step runs.

        The third case is what keeps a run definition a record of the run
        rather than of the mouse. The interface's own control timeline applies
        the same rule to the entries a reader sees.
        """

        open_segment = self._segments[-1]

        if settings == open_segment.settings:
            return

        if self._reached_s == open_segment.opening.instant_s:
            if len(self._segments) > 1 and settings == self._segments[-2].settings:
                self._segments = self._segments[:-1]
                return

            self._segments = (*self._segments[:-1], RunSegment(settings, open_segment.opening))
            return

        self._segments = (
            *self._segments,
            RunSegment(
                settings, Keyframe(self._reached_s, self._canonical_state_at(self._reached_s))
            ),
        )

    def state_at(self, instant_s: float) -> tuple[float, ...]:
        """The canonical state at `instant_s`, in `governing_equations`' state order.

        It forms one matrix exponential over the interval from the keyframe
        that opens the segment containing `instant_s` to `instant_s` itself.
        Two calls with the same argument on the same definition perform the
        identical sequence of operations, so they return bit-identical values.
        A keyframe, an export or a fork's starting state is taken from this
        path. `docs/MODEL.md` § "The canonical evaluation rule" states the
        guarantee that the path provides.

        Its result is a function of the run definition and of nothing else. It
        uses no cache and no memory of earlier queries. So a run queried at
        arbitrary instants as it goes returns the same values as the same run
        never queried at all. `tests/reference/test_canonical_evaluation.py`
        tests that. The propagators that `evaluate_anchored` keeps between
        frames are not read here.

        Raises:
            SimulationConfigurationError: `instant_s` is not finite, precedes
                `opened_at_s`, or is past the time the run has reached.
        """

        self._require_within_run(instant_s)

        return self._canonical_state_at(instant_s)

    def segment_at(self, instant_s: float) -> RunSegment:
        """The stretch of constant settings in force from `instant_s` onward.

        The segment holds the settings that the equations were assembled from
        at that instant, together with the keyframe they start from. A state
        at `instant_s` is one propagation from that keyframe.

        **At an instant where a stretch opens, this is the stretch that
        opens there.** It is the settings that the next step runs under,
        including a change made at `instant_s`. The step that reached
        `instant_s` ran under the stretch before it, which
        `reaching_segment_at` returns. The two differ only at a keyframe.
        `docs/MODEL.md` § "The canonical evaluation rule" says which of the
        two a branch opens from (`PL-ZR49`).

        This method returns the segment rather than its index. An index is
        meaningful only beside the tuple it came from. A caller that held an
        index across a `record_change` would read a different stretch from the
        one it asked for.

        Raises:
            SimulationConfigurationError: `instant_s` is not finite, precedes
                `opened_at_s`, or is past the time the run has reached.
        """

        self._require_within_run(instant_s)

        return self._segments[self._segment_index_at(instant_s)]

    def reaching_segment_at(self, instant_s: float) -> RunSegment:
        """The stretch of constant settings that the step reaching `instant_s` ran under.

        This is the last stretch that opens strictly before `instant_s`. At
        an instant inside a stretch it is the same stretch that `segment_at`
        returns. At a keyframe it is the stretch before the keyframe, because
        the keyframe's settings apply only from that instant onward. At the
        run's opening no step has reached the instant, so the result is the
        first stretch. The state at the opening is a keyframe that no setting
        produced.

        **No later change can alter the result**, which is why a branch reads
        its provenance from here (`PL-ZR49`). `record_change` opens a stretch
        only at `reached_s` and can replace only the stretch that opens
        there. A stretch that opens strictly before `reached_s` is fixed. So
        once the run stands on `instant_s`, the stretch returned here stays
        in `segments` however the settings are changed at `instant_s`. The
        one exception is the run's opening, where the first stretch opens at
        `instant_s` itself and a change there replaces it.

        Raises:
            SimulationConfigurationError: `instant_s` is not finite, precedes
                `opened_at_s`, or is past the time the run has reached.
        """

        self._require_within_run(instant_s)

        return self._segments[max(bisect_left(self._segments, instant_s, key=_opening_of) - 1, 0)]

    def evaluate(self, start_s: float, stop_s: float, columns: int) -> SampledWindow:
        """`columns` states evenly spaced across `[start_s, stop_s]`, for drawing.

        This is the display path. Inside one segment the columns are uniformly
        spaced, so a single propagator over the column spacing serves all of
        them. Each column then costs one matrix-vector product. The work is
        therefore proportional to the number of columns asked for plus the
        number of setting changes inside the window, and not to the run's
        length. Two matrix exponentials are formed for each segment in view.
        One covers the offset from the segment's keyframe to its first column,
        and one covers the spacing. Taking each column canonically would
        instead form `columns` of them.

        That saving costs bit-identity. Chaining composes the same operations
        in a different order from `state_at`. Values from this method are for
        drawing. They come back as `DisplayState`, so that they cannot be
        stored, exported or forked from just because they have the same shape
        as a canonical state. The module docstring explains why.

        Args:
            start_s: The window's first instant, in seconds.
            stop_s: The window's last instant, in seconds. Equal to `start_s`
                for a window of one instant.
            columns: How many instants to sample, at least one. With one
                column, only `start_s` is sampled.

        Raises:
            TypeError: `columns` is not an `int`, or is a `bool`.
            SimulationConfigurationError: `columns` is less than one or more
                than `MAXIMUM_WINDOW_COLUMNS`, either bound is not finite,
                either bound precedes `opened_at_s`, `stop_s` precedes
                `start_s`, or `stop_s` is past the time the run has reached.
        """

        if isinstance(columns, bool) or not isinstance(columns, int):
            raise TypeError(
                f"columns of {shown(columns)} has type {type(columns).__name__}, not int: "
                "a window is sampled at a whole number of instants"
            )

        if columns < 1:
            raise SimulationConfigurationError(f"a window needs at least one column, not {columns}")

        if columns > MAXIMUM_WINDOW_COLUMNS:
            raise SimulationConfigurationError(
                f"a window of {columns} columns is more than the {MAXIMUM_WINDOW_COLUMNS} "
                "that one call may ask for"
            )

        self._require_within_run(start_s)
        self._require_within_run(stop_s)

        if stop_s < start_s:
            raise SimulationConfigurationError(
                f"a window from {start_s} s to {stop_s} s ends before it begins"
            )

        spacing_s = 0.0 if columns == 1 else (stop_s - start_s) / (columns - 1)
        times_s = tuple(start_s + column * spacing_s for column in range(columns))
        states: list[tuple[float, ...]] = []
        segment_index = self._segment_index_at(start_s)
        column = 0

        while column < columns:
            segment_index = self._advance_index_to(times_s[column], segment_index)
            segment = self._segments[segment_index]
            last = _last_column_before(self._opening_after(segment_index), times_s, column)
            state = _advanced(
                _propagator(segment, times_s[column] - segment.opening.instant_s),
                segment.opening.state,
            )
            states.append(state)

            if last > column:
                chained = _propagator(segment, spacing_s)

                for _ in range(last - column):
                    state = _advanced(chained, state)
                    states.append(state)

            column = last + 1

        return SampledWindow(times_s=times_s, states=tuple(DisplayState(state) for state in states))

    def evaluate_anchored(self, start_s: float, stop_s: float, spacing_s: float) -> SampledWindow:
        """Columns on an absolute grid across `[start_s, stop_s]`, plus every event in it.

        This is the chart's own display path. It differs from `evaluate` in
        two ways that a drawn trace needs and a bare window does not.

        **The grid is anchored to the case's zero, not to the window and not
        to `opened_at_s`.** Columns land on absolute multiples of `spacing_s`
        on the case's own axis. So a window that follows the run reuses every
        column time it had in the last frame, and gains at most one new column
        time. `evaluate` spaces its columns across whatever bounds it is given,
        which makes every column a new instant on every frame. The drawn
        points then all move. `PL-Q197` measured that movement as what
        saturated the Flutter client, at 2 700 discrete control mutations a
        frame, before decimation was anchored for exactly this reason.
        Anchoring the *evaluation* times applies the same fix at the next
        level.

        **Do not re-anchor this grid to the run's own opening.** For a run
        opening at induction the two are the same number, so the distinction
        looks like pedantry. For a branch they differ, and anchoring each run
        separately is precisely the defect that `PL-2R2C` recorded. That item
        measured a branch forked at 55.3 s and drawn on a 13-column 120 s
        axis. The branch shared 2 of its 8 columns with its trunk when
        anchored to its own opening, and 8 of 8 when anchored here. Two traces
        on one axis can be read against each other only at matched instants.
        So a difference trace or a shared tooltip built over per-run grids
        would be wrong, not merely coarse. `docs/MODEL.md` § "What the chart
        draws" states the same rule.

        **Every control event inside the window gets its own column, at no
        cost.** Between events the trajectory is a sum of exponentials with
        bounded curvature and no hidden transients. So every sharp feature in
        a run is at an event boundary, and a grid that steps over an event
        draws a straight line through a kink. Each event is a segment opening,
        and a segment's opening state is already stored as its keyframe. So
        these columns are read rather than computed. They are exact, and no
        propagator is formed for them. `docs/MODEL.md` § "What the chart
        draws" states the guarantee that these event columns provide.

        Both bounds are always columns. In particular, the numeric readouts
        show the state at `stop_s`. Drawing `stop_s` keeps the right-hand end
        of the trace from disagreeing with the readout beside it.

        The cost is that of `evaluate`, plus one propagator for each bound.
        Like `evaluate`, this method forms two matrix exponentials for each
        segment in view. One runs from the segment's keyframe to its first
        grid column, and one covers the spacing that carries the rest. The
        event columns are free. Forming a propagator takes about 1.29 ms,
        against 6.2 us for a chained product (measured 2026-09-08, `PL-2FM6`).
        That is why the grid stays uniform within a segment, rather than each
        column being taken from its keyframe.

        **Those propagators are formed once, not once a frame.** All but three
        of them are over an interval that the grid fixes, and there are two
        kinds of such interval. One is the spacing, which the time base fixes.
        The other is a segment's offset to its first grid column, which the
        anchoring fixes. So a window drawn a frame later asks for the same
        propagators again, and each call keeps the ones it used for the next
        call. The three that change are the two bounds' propagators and the
        propagator for the offset in the segment where the window opens. That
        segment's first grid column is the first one past `start_s`, so it
        moves each time the left edge passes a column. A frame that follows
        the run forms the propagators for its two bounds. It forms the third
        only on a frame whose left edge has passed a column, and it forms
        those of any segment newly in view. A new spacing, from a new time
        base or plot width, forms them all once more. `docs/MODEL.md` § "The
        run is that record, and every state is derived from it" says how often
        that happens and what it costs (`PL-CNCF`).

        Reuse cannot change a drawn value by even one bit. A propagator is a
        function of a segment's settings and an interval alone, and it is kept
        under both. The settings record is frozen and compared by value for
        exactly this use (`UptakeEquationSettings`). So a kept propagator is
        exactly the matrix that forming it again would give. Only the last
        call's propagators are kept, so the store is bounded by one window. It
        holds two for each segment in view and one for each bound. It never
        holds more than one for each column, even at a spacing too fine for
        its multiples to be distinct instants. The store is replaced on each
        call rather than added to. So it does not grow with the run, or with
        how often or where the run was drawn.

        Args:
            start_s: The window's first instant, in seconds. Always a column.
            stop_s: The window's last instant, in seconds. Always a column,
                and equal to `start_s` for a window of one instant.
            spacing_s: The distance between grid columns, in seconds. It must
                be positive. The caller sets it from the width it is drawing
                and the number of columns it can afford. This class knows
                neither.

        Returns:
            Ascending, duplicate-free instants and the state at each.

        Raises:
            TypeError: `spacing_s` is not an `int` or a `float`, or is a
                `bool` (`require_positive_finite`).
            SimulationConfigurationError: `spacing_s` is not positive or not
                finite, either bound is not finite, either bound precedes
                `opened_at_s`, `stop_s` precedes `start_s`, `stop_s` is past
                the time the run has reached, or `spacing_s` is so fine that
                the grid's multiples up to `stop_s` cannot be counted. Before
                `PL-YZ17`, that last case raised a bare `OverflowError`. It is
                also raised when the window holds more than
                `MAXIMUM_WINDOW_COLUMNS` grid multiples, counted as that
                constant's docstring says. Before `PL-06LS`, such a window
                looped once per multiple and could fail to return. A
                fine spacing is otherwise accepted. Unlike a run's step, it is
                chained at most once per column, so its rounding error does
                not accumulate beyond what the columns asked for.
        """

        require_positive_finite("spacing_s", spacing_s)

        self._require_within_run(start_s)
        self._require_within_run(stop_s)

        if stop_s < start_s:
            raise SimulationConfigurationError(
                f"a window from {start_s} s to {stop_s} s ends before it begins"
            )

        if not isfinite(stop_s / spacing_s):
            raise SimulationConfigurationError(
                f"a column spacing of {spacing_s} s puts more grid columns before {stop_s} s "
                "than can be counted"
            )

        # `_anchored_columns` loops once for each multiple in this range, so
        # this is exactly how many times it loops. Each quotient is a finite
        # float, and `int()` converts it without rounding. At a very fine
        # spacing the quotients are themselves rounded, so the message gives
        # the count to six significant figures rather than as a long integer
        # whose later digits are rounding error.
        grid_multiples = int(stop_s // spacing_s) - int(start_s // spacing_s)

        if grid_multiples > MAXIMUM_WINDOW_COLUMNS:
            raise SimulationConfigurationError(
                f"a column spacing of {spacing_s} s puts {float(grid_multiples):.6g} grid "
                "multiples after "
                f"{start_s} s and up to {stop_s} s, more than the {MAXIMUM_WINDOW_COLUMNS} that "
                "one call may ask for"
            )

        times_s, grid_index = self._anchored_columns(start_s, stop_s, spacing_s)
        propagators = _WindowPropagators(self._last_window_propagators)
        states: list[tuple[float, ...]] = [()] * len(times_s)
        segment_index = self._segment_index_at(times_s[0])
        column = 0

        while column < len(times_s):
            segment_index = self._advance_index_to(times_s[column], segment_index)
            segment = self._segments[segment_index]
            opening_after_s = self._opening_after(segment_index)
            state = self._state_from_opening(segment, times_s[column], propagators)
            states[column] = state
            chained: Matrix | None = None

            # Consecutive grid columns are consecutive multiples of the
            # spacing. So one propagator over the spacing carries the whole
            # sequence of them inside this segment. A bound or an event
            # column ends the sequence, because its gap to its neighbour is
            # not the spacing.
            while column + 1 < len(times_s) and times_s[column + 1] < opening_after_s:
                here, next_ = grid_index[column], grid_index[column + 1]

                if here is None or next_ is None or next_ != here + 1:
                    break

                if chained is None:
                    chained = propagators.over(segment.settings, spacing_s)

                state = _advanced(chained, state)
                column += 1
                states[column] = state

            column += 1

        self._last_window_propagators = propagators.used

        return SampledWindow(times_s=times_s, states=tuple(DisplayState(state) for state in states))

    def _anchored_columns(
        self, start_s: float, stop_s: float, spacing_s: float
    ) -> tuple[tuple[float, ...], list[int | None]]:
        """The column times, and the grid multiple of each time that lies on the grid.

        The grid index travels with the time because the walk above uses it to
        tell two kinds of column apart. One propagator can carry a sequence of
        consecutive grid columns. It cannot carry a bound or an event column,
        because the gap from such a column to its neighbour is not the
        spacing. Deriving the index back from the time would mean testing a
        float for divisibility.

        Returns:
            Ascending, duplicate-free times, and one entry per time. Each
            entry holds the time's multiple of `spacing_s`, or `None` where
            the time is a bound or an event.
        """

        indexed: dict[float, int | None] = {start_s: None, stop_s: None}

        for multiple in range(int(start_s // spacing_s) + 1, int(stop_s // spacing_s) + 1):
            time_s = multiple * spacing_s

            if start_s < time_s < stop_s:
                indexed.setdefault(time_s, multiple)

        for segment in self._segments:
            event_s = segment.opening.instant_s

            if start_s < event_s < stop_s:
                # An event column overrides a grid column at the same
                # instant. Both draw the same state, and marking the instant
                # `None` keeps the walk from chaining across a segment
                # boundary.
                indexed[event_s] = None

        times_s = tuple(sorted(indexed))

        return times_s, [indexed[time_s] for time_s in times_s]

    def _state_from_opening(
        self, segment: RunSegment, instant_s: float, propagators: _WindowPropagators
    ) -> tuple[float, ...]:
        """The state at `instant_s`, propagated from `segment`'s own keyframe.

        A column that lands exactly on the keyframe is the event-column case.
        Its state is read from the keyframe, rather than computed by forming a
        propagator over a zero interval. Any other column is propagated with
        the window's own `propagators`, so a propagator that the last window
        used is reused.

        Raises:
            SimulationConfigurationError: `instant_s` precedes the keyframe,
                which `matrix_exponential` refuses as a non-positive interval
                rather than returning the keyframe. No call here passes such
                an instant, because each column is read from the segment it
                falls in.
        """

        if instant_s == segment.opening.instant_s:
            return segment.opening.state

        return propagate(
            propagators.over(segment.settings, instant_s - segment.opening.instant_s),
            segment.opening.state,
        )

    def _canonical_state_at(self, instant_s: float) -> tuple[float, ...]:
        """`state_at` without the bounds check, for the keyframe path.

        `record_change` evaluates at `reached_s`, which is inside the run by
        construction. Going through `state_at` would re-check what is already
        established.
        """

        segment = self._segments[self._segment_index_at(instant_s)]

        return _advanced(
            _propagator(segment, instant_s - segment.opening.instant_s), segment.opening.state
        )

    def _segment_index_at(self, instant_s: float) -> int:
        """Index of the segment the run was under at `instant_s`.

        It uses a binary search, which keeps the cost of computing a window a
        property of the window rather than of the run. A linear walk would put
        the run's whole length back into the cost of every frame, in the one
        method that the closed form exists to remove it from. The segment
        openings ascend because `record_change` only ever appends at
        `reached_s`, which never decreases.

        **An instant before the first opening is refused rather than wrapped
        round.** `bisect_right` returns zero there, so the index is `-1`.
        Python treats that index as the *last* segment, the one furthest from
        any right answer. Nothing then fails. `_propagator` returns `None` for
        the non-positive interval that follows, so the caller is handed that
        segment's keyframe as though it were the state at an instant when the
        run did not exist. `_require_within_run` already refuses such an
        instant on every public path, so this check is the second of two
        guards rather than the first. It is here because the failure it
        prevents is silent and the check costs one comparison.
        `_canonical_state_at` is the one caller that uses this search without
        the bounds check, by design.

        Raises:
            SimulationConfigurationError: `instant_s` precedes the instant the
                run opens at.
        """

        index = bisect_right(self._segments, instant_s, key=_opening_of) - 1

        if index < 0:
            raise SimulationConfigurationError(
                f"this run opens at {self._segments[0].opening.instant_s} s, so it was under "
                f"no settings at {instant_s} s"
            )

        return index

    def _advance_index_to(self, instant_s: float, from_index: int) -> int:
        """Index of the segment holding `instant_s`, searching forward from `from_index`.

        This is the lookup that the window walk uses. The walk passes back the
        index it last used, so the whole walk costs one pass over the segments
        the window covers, not a fresh search per column. The lookup also
        skips segments too short to contain a column. A walk that assumed one
        segment per column would get that case wrong.
        """

        index = from_index

        while (
            index + 1 < len(self._segments)
            and self._segments[index + 1].opening.instant_s <= instant_s
        ):
            index += 1

        return index

    def _opening_after(self, index: int) -> float:
        """When the segment after `index` opens, or infinity where it is the last.

        It returns infinity rather than the run's duration. The caller wants
        the first instant at which this segment's settings no longer apply,
        and for the last segment there is no such instant.
        """

        if index + 1 < len(self._segments):
            return self._segments[index + 1].opening.instant_s

        return inf

    def _require_within_run(self, instant_s: float) -> None:
        """Refuse an instant the run has not reached, or one before it began.

        **The lower bound is the run's own opening, not the literal zero.**
        The two are the same number for a run that opens at induction, and
        different for a run that opens anywhere else. Reading the bound from
        the segments keeps the refusal correct for both kinds of run, without
        the caller saying which kind it holds. A bound left at zero would
        accept every instant in the span before such a run existed.
        `_segment_index_at` rejects an instant in that span too, so this check
        is the first of two guards rather than the only one.

        Raises:
            SimulationConfigurationError: `instant_s` is not finite, precedes
                the instant the run opens at, or is past `reached_s`.
        """

        if not isfinite(instant_s):
            raise SimulationConfigurationError(f"{instant_s} s is not a finite instant")

        opening_s = self._segments[0].opening.instant_s

        if instant_s < opening_s:
            raise SimulationConfigurationError(
                f"a run that opens at {opening_s} s has no state at {instant_s} s, before it began"
            )

        if instant_s > self._reached_s:
            raise SimulationConfigurationError(
                f"this run has reached {self._reached_s} s, so it has no state at "
                f"{instant_s} s; that would be a prediction rather than the run"
            )


def _opening_of(segment: RunSegment) -> float:
    """When `segment` opens, which is the key that the segment search is ordered on."""

    return segment.opening.instant_s


def _last_column_before(limit_s: float, times_s: tuple[float, ...], first_column: int) -> int:
    """Index of the last of `times_s`, from `first_column` on, that precedes `limit_s`.

    The columns from `first_column` to the returned index share one segment, so one
    propagator over the column spacing serves all of them.
    """

    column = first_column

    while column + 1 < len(times_s) and times_s[column + 1] < limit_s:
        column += 1

    return column


def _propagator(segment: RunSegment, interval_s: float) -> Matrix | None:
    """`exp(A * interval_s)` for `segment`'s settings, or `None` for no interval.

    `matrix_exponential` refuses a non-positive interval, and rightly so. An
    interval is a horizon to propagate over, and zero is not one. Asking for
    the state exactly at a keyframe is nonetheless an ordinary request,
    because the first column of a window often lands on one. The correct
    result is the keyframe itself. So the identity is expressed by returning nothing to
    apply, rather than by building a matrix that does nothing.
    """

    if interval_s <= 0.0:
        return None

    return matrix_exponential(build_system_matrix(segment.settings), interval_s)


class _WindowPropagators:
    """The propagators one drawn window applies, reusing those the window before it used.

    `RunDefinition.evaluate_anchored` builds one of these per call, from what
    the last call `used`, and keeps this call's `used` for the next call.
    `used` holds every propagator this window applied, whether it formed the
    propagator or found it kept. So a propagator that the last window used and
    this window never asks for is not carried on. That is what bounds the
    store to one window.
    """

    __slots__ = ("_kept", "used")

    def __init__(self, kept: dict[_PropagatorKey, Matrix]) -> None:
        self._kept = kept
        self.used: dict[_PropagatorKey, Matrix] = {}

    def over(self, settings: UptakeEquationSettings, interval_s: float) -> Matrix:
        """`exp(A * interval_s)` for `settings`, formed only when neither window already has it.

        The store is keyed by the settings and the interval together, which
        are everything that `build_system_matrix` and `matrix_exponential`
        read. So no `record_change` can leave a kept propagator in use for a
        stretch it was not formed under, because a propagator is found only by
        the settings it was formed from.

        Raises:
            SimulationConfigurationError: `interval_s` is not positive and
                finite, which `matrix_exponential` refuses. The caller reads a
                keyframe rather than asking for a propagator over no interval.
        """

        key = (settings, interval_s)
        propagator = self.used.get(key)

        if propagator is None:
            propagator = self._kept.get(key)

        if propagator is None:
            propagator = matrix_exponential(build_system_matrix(settings), interval_s)

        self.used[key] = propagator

        return propagator


def _advanced(propagator: Matrix | None, state: tuple[float, ...]) -> tuple[float, ...]:
    """Apply `propagator` to `state`, or return `state` when there is no interval.

    The unit state comes back exactly one, as it went in, and nothing is
    written over it. `matrix_exponential` returns the unit state's row equal
    to the identity's row, to the last bit. That row, applied to a state
    carrying one in the unit state, is one term of one times one plus the rest
    times zero. Until `PL-2MD9` the entry was a product of two rounded
    factors, and this function overwrote it. That kept the unit state exact,
    but not the forcing column, into which the squarings had multiplied the
    same drift. The fix belonged in the propagator. The tests now check the
    unit state's one where they read it back out of `state_at`.
    """

    if propagator is None:
        return state

    return propagate(propagator, state)


def _require_state(state: tuple[float, ...] | DisplayState) -> None:
    """Refuse a state vector the equations could not be read against.

    A display value is refused first, and by name. Otherwise it would fail the
    structural test in `require_canonical_state` with a message naming its
    type. That message is true but tells the reader nothing about *why* a
    wrapper exists, and the error a safety-critical path raises is part of
    what makes the path auditable. Every check after that refusal is about the
    state vector rather than about this module. So those checks belong to
    `governing_equations.require_canonical_state`, and the live system that a
    branch resumes into applies the identical guard by calling it too.

    Raises:
        SimulationConfigurationError: `state` came from the display path, or is
            not `STATE_SIZE` long, holds a non-finite value, or does not carry
            exactly one in `UNIT_STATE`.
    """

    if isinstance(state, DisplayState):
        raise SimulationConfigurationError(
            "this state came from the display path, which composes its arithmetic in a "
            "different order and so does not reproduce the canonical value bit for bit; "
            "a state that is stored, exported, replayed or forked from is taken from "
            "state_at"
        )

    require_canonical_state(state)
