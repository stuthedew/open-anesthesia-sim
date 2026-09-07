"""A run held as the settings it was computed under, rather than as samples of itself.

`docs/MODEL.md`'s governing equations are linear and time-invariant while every
setting is held constant, so `matrix_exponential` solves each such stretch
exactly over any horizon. A run is therefore described completely by the
settings in force at each moment - the *score* - and every state it passed
through is a closed-form function of that score and the time asked for.
Nothing has to be recorded for a value to be recoverable.

Two consequences carry this module, and both are what `PL-T691` exists for:

- **Memory stops growing with the run.** A recorded run costs one sample per
  solver step; a score costs one segment per setting change. Measured
  2026-09-05, a 30-day case at 50 changes a day is about 70 KiB of score and
  keyframes against the 3.16 GB of samples the same run records today.
- **The cost of answering a window stops depending on the run's length.** A
  window is answered from the keyframe bracketing it rather than by scanning
  what came before, so 600 columns cost the same over 30 days as over an hour.

**Two evaluation paths, and they are not interchangeable.** `state_at` is
canonical: one matrix exponential per inter-event interval, composed in
recording order from `t = 0`, so two evaluations of the same score at the same
instant perform the identical sequence of operations and agree bit for bit.
`evaluate` is the display path: inside one segment it reuses a single
propagator across uniformly spaced columns, which is what makes a frame cheap
and which composes those operations in a different order. The two therefore
agree to floating-point composition rather than exactly. `PL-P1Z3` states that
separation as a guarantee in `docs/MODEL.md` and gates it; until it lands,
treat a value from `evaluate` as fit for drawing and not for storing, forking
or exporting.

This module carries no compartment names, no units and no interface concepts:
it composes the propagators `matrix_exponential` produces from the matrices
`governing_equations` assembles, and a state here is that module's own state
vector in that module's own order.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from math import inf, isfinite

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    STATE_SIZE,
    UNIT_STATE,
    UptakeEquationSettings,
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import Matrix, matrix_exponential, propagate


@dataclass(frozen=True, slots=True)
class Keyframe:
    """The exact state at one segment boundary, computed canonically.

    One of these per setting change, and one at `t = 0`, is the whole of what
    a run stores besides its settings. Everything between two of them is
    recovered by propagating the earlier one forward, which is why a keyframe
    is computed canonically even though the values drawn from it are not:
    an error here is inherited by every value derived from it, while an error
    on the display path affects one column of one frame.

    Attributes:
        elapsed_s: Simulated time this state was reached at, in seconds.
        state: The trajectory in `governing_equations`' own state order,
            `STATE_SIZE` entries long. The two accumulator states are
            cumulative from the start of the run rather than per segment,
            because their rows have no diagonal entry: a propagator maps each
            of them to itself with coefficient one, so carrying a running
            total through is the same arithmetic as starting from zero and
            adding.
    """

    elapsed_s: float
    state: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class ScoreSegment:
    """One stretch of a run during which every setting the equations read is constant.

    The settings and the state they start from travel together rather than in
    parallel lists, so a segment cannot come to be paired with another
    segment's opening state - which would compute a stretch of the run from
    settings it was never under, and produce a plausible trajectory that never
    happened.

    Attributes:
        settings: What `build_system_matrix` assembles $`A`$ from, in force
            from `opening.elapsed_s` until the next segment begins.
        opening: The state at the segment's first instant.
    """

    settings: UptakeEquationSettings
    opening: Keyframe


@dataclass(frozen=True, slots=True)
class SampledWindow:
    """The states at a run of uniformly spaced instants, for drawing.

    The display path's answer. Times and states travel together and are
    checked to be the same length at construction, for the reason
    `ScoreSegment` pairs its two fields: a trace drawn from one array against
    the other's time axis misstates the run from values that are individually
    correct, which `CLAUDE.md`'s safety-critical standard counts as a
    presentation failure rather than a lesser kind.

    Attributes:
        times_s: The instants sampled, ascending, in seconds.
        states: One entry per instant, each `STATE_SIZE` long, in
            `governing_equations`' state order.

    Raises:
        SimulationConfigurationError: If the two are not the same length.
    """

    times_s: tuple[float, ...]
    states: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if len(self.times_s) != len(self.states):
            raise SimulationConfigurationError(
                f"a sampled window has {len(self.times_s)} instants and "
                f"{len(self.states)} states; each state belongs to one instant"
            )


class RunScore:
    """A run, as the settings it was computed under and the states they imply.

    Built with the settings a run starts under and the state it starts from,
    then told what happened: `advance_to` moves the time the run has reached,
    and `record_change` closes the open segment at that time and opens a new
    one under new settings. Those two calls are the whole of what a run *is*.

    **A change is recorded at the run's own reach and nowhere else.** There is
    no instant argument on `record_change`, deliberately: a setting change
    takes effect when it is made, and a caller free to name a different time
    could place one inside a stretch already computed under other settings.
    That would not fail - it would return a trajectory the run never took, at
    full precision and with nothing to distinguish it. Removing the argument
    removes the failure, which `.claude/rules/expert-review.md` prefers to
    validating it.

    **It answers only within the run.** `state_at` and `evaluate` refuse a
    time past `duration_s`, because the score can be evaluated arbitrarily far
    ahead and what comes back would be a prediction of a run that has not
    happened. Drawn on the same axis as the run itself it would be
    indistinguishable from it.
    """

    __slots__ = ("_duration_s", "_segments")

    def __init__(self, settings: UptakeEquationSettings, initial_state: tuple[float, ...]) -> None:
        """Open a run at `t = 0` under `settings`, from `initial_state`.

        Args:
            settings: The settings the run begins under.
            initial_state: The state at `t = 0`, in `governing_equations`'
                state order. Its accumulators are the run's starting totals,
                which is zero for a run that has delivered nothing.

        Raises:
            SimulationConfigurationError: `initial_state` is not `STATE_SIZE`
                long, holds a non-finite value, or does not carry exactly one
                in `UNIT_STATE`. The last is what makes every forcing term in
                `build_system_matrix` mean what it says; a state that carried
                anything else there would scale the whole of the delivery term
                without changing any setting a reader can see.
        """

        _require_state(initial_state)

        self._segments: tuple[ScoreSegment, ...] = (
            ScoreSegment(settings=settings, opening=Keyframe(0.0, initial_state)),
        )
        self._duration_s = 0.0

    @property
    def segments(self) -> tuple[ScoreSegment, ...]:
        """Every stretch of constant settings this run has had, oldest first."""

        return self._segments

    @property
    def duration_s(self) -> float:
        """The simulated time the run has reached, in seconds."""

        return self._duration_s

    def advance_to(self, elapsed_s: float) -> None:
        """Move the time the run has reached to `elapsed_s`.

        Records no state: the states are already implied by the settings and
        recovered on demand. What this changes is how far the score may be
        evaluated, which is what stops a prediction being drawn as the run.

        Raises:
            SimulationConfigurationError: `elapsed_s` is not finite, or is
                earlier than the time already reached. A run cannot un-happen,
                and rewinding the reach would leave the segments recorded
                after it describing a stretch the score would then refuse to
                evaluate.
        """

        if not isfinite(elapsed_s):
            raise SimulationConfigurationError(
                f"a run's elapsed time is {elapsed_s}, which is not finite"
            )

        if elapsed_s < self._duration_s:
            raise SimulationConfigurationError(
                f"a run cannot go back from {self._duration_s} s to {elapsed_s} s"
            )

        self._duration_s = elapsed_s

    def record_change(self, settings: UptakeEquationSettings) -> None:
        """Note that the run continues under `settings` from now on.

        "Now" is `duration_s`, the time the run has reached; see the class
        docstring for why that is not an argument.

        Three calls change nothing and are dropped rather than recorded, each
        for a reason about the run rather than about tidiness. Settings equal
        to the ones in force describe no change the model would integrate
        differently. A second change at an instant already opened - two
        controls moved between one step and the next - belongs to the same
        stretch, so it replaces that stretch's settings instead of opening a
        zero-length one: the run was computed under whatever stood when the
        step ran, which is the last value written. And where that replacement
        lands back on the settings the previous stretch already had - a dial
        moved and moved back before a step ran - the stretch goes entirely,
        because nothing about the run differs.

        The third is what keeps a score a record of the run rather than of the
        mouse, and it is the same rule the interface's own control timeline
        applies to the entries a reader sees.
        """

        open_segment = self._segments[-1]

        if settings == open_segment.settings:
            return

        if self._duration_s == open_segment.opening.elapsed_s:
            if len(self._segments) > 1 and settings == self._segments[-2].settings:
                self._segments = self._segments[:-1]
                return

            self._segments = (*self._segments[:-1], ScoreSegment(settings, open_segment.opening))
            return

        self._segments = (
            *self._segments,
            ScoreSegment(
                settings, Keyframe(self._duration_s, self._canonical_state_at(self._duration_s))
            ),
        )

    def state_at(self, elapsed_s: float) -> tuple[float, ...]:
        """The canonical state at `elapsed_s`, in `governing_equations`' state order.

        One matrix exponential from the keyframe that opens the segment
        `elapsed_s` falls in, over the interval between them. Two calls with
        the same argument on the same score perform the identical sequence of
        operations, so they return bit-identical values; this is the path a
        keyframe, an export or a fork's starting state is taken from.

        Raises:
            SimulationConfigurationError: `elapsed_s` is not finite, is
                negative, or is past the time the run has reached.
        """

        self._require_within_run(elapsed_s)

        return self._canonical_state_at(elapsed_s)

    def evaluate(self, start_s: float, stop_s: float, columns: int) -> SampledWindow:
        """`columns` states evenly spaced across `[start_s, stop_s]`, for drawing.

        The display path. Inside one segment the columns are uniformly spaced,
        so a single propagator over the column spacing serves all of them and
        each column costs one matrix-vector product; the work is therefore
        proportional to the columns asked for plus the setting changes the
        window contains, and not to the run's length. Two matrix exponentials
        are formed per segment in view - one for the offset from its keyframe
        to its first column, one for the spacing - against `columns` of them
        if each column were taken canonically.

        What that buys costs bit-identity: chaining composes the same
        operations in a different order from `state_at`. Values from here are
        for drawing; see the module docstring.

        Args:
            start_s: The window's first instant, in seconds.
            stop_s: The window's last instant, in seconds. Equal to `start_s`
                for a window of one instant.
            columns: How many instants to sample, at least one. One returns
                `start_s` alone.

        Raises:
            SimulationConfigurationError: `columns` is below one; either bound
                is not finite; `start_s` is negative; `stop_s` precedes
                `start_s`; or `stop_s` is past the time the run has reached.
        """

        if columns < 1:
            raise SimulationConfigurationError(f"a window needs at least one column, not {columns}")

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
                _propagator(segment, times_s[column] - segment.opening.elapsed_s),
                segment.opening.state,
            )
            states.append(state)

            if last > column:
                chained = _propagator(segment, spacing_s)

                for _ in range(last - column):
                    state = _advanced(chained, state)
                    states.append(state)

            column = last + 1

        return SampledWindow(times_s=times_s, states=tuple(states))

    def _canonical_state_at(self, elapsed_s: float) -> tuple[float, ...]:
        """`state_at` without the bounds check, for the keyframe path.

        `record_change` evaluates at `duration_s`, which is inside the run by
        construction, so it would otherwise re-check what it just established.
        """

        segment = self._segments[self._segment_index_at(elapsed_s)]

        return _advanced(
            _propagator(segment, elapsed_s - segment.opening.elapsed_s), segment.opening.state
        )

    def _segment_index_at(self, elapsed_s: float) -> int:
        """Index of the segment the run was under at `elapsed_s`.

        By binary search, which is what keeps the cost of answering a window a
        property of the window rather than of the run: a linear walk would put
        the run's whole length back into every frame, in the one method the
        closed form exists to take it out of. The openings ascend because
        `record_change` only ever appends at `duration_s`, which never
        decreases.
        """

        return bisect_right(self._segments, elapsed_s, key=_opening_of) - 1

    def _advance_index_to(self, elapsed_s: float, from_index: int) -> int:
        """Index of the segment holding `elapsed_s`, searching forward from `from_index`.

        The window walk's own lookup. It hands back the index it last used, so
        the whole walk costs one pass over the segments the window covers
        rather than a fresh search per column - and it skips the segments too
        short to hold one, which is the case a walk assuming one segment per
        column would get wrong.
        """

        index = from_index

        while (
            index + 1 < len(self._segments)
            and self._segments[index + 1].opening.elapsed_s <= elapsed_s
        ):
            index += 1

        return index

    def _opening_after(self, index: int) -> float:
        """When the segment after `index` opens, or infinity where it is the last.

        Infinity rather than the run's duration: what the caller wants is the
        first instant this segment's settings no longer apply, and for the
        last segment there is no such instant.
        """

        if index + 1 < len(self._segments):
            return self._segments[index + 1].opening.elapsed_s

        return inf

    def _require_within_run(self, elapsed_s: float) -> None:
        """Refuse an instant the run has not reached, or one before it began.

        Raises:
            SimulationConfigurationError: `elapsed_s` is not finite, is
                negative, or is past `duration_s`.
        """

        if not isfinite(elapsed_s):
            raise SimulationConfigurationError(f"{elapsed_s} s is not a finite instant")

        if elapsed_s < 0.0:
            raise SimulationConfigurationError(
                f"a run has no state at {elapsed_s} s, before it began"
            )

        if elapsed_s > self._duration_s:
            raise SimulationConfigurationError(
                f"this run has reached {self._duration_s} s, so it has no state at "
                f"{elapsed_s} s; that would be a prediction rather than the run"
            )


def _opening_of(segment: ScoreSegment) -> float:
    """When `segment` opens - the key the segment search is ordered on."""

    return segment.opening.elapsed_s


def _last_column_before(limit_s: float, times_s: tuple[float, ...], first_column: int) -> int:
    """Index of the last of `times_s`, from `first_column` on, that precedes `limit_s`.

    The columns from `first_column` to here share one segment, so one
    propagator over the column spacing serves all of them.
    """

    column = first_column

    while column + 1 < len(times_s) and times_s[column + 1] < limit_s:
        column += 1

    return column


def _propagator(segment: ScoreSegment, interval_s: float) -> Matrix | None:
    """`exp(A * interval_s)` for `segment`'s settings, or `None` for no interval.

    `matrix_exponential` refuses a non-positive interval, and rightly: an
    interval is a horizon to propagate over and zero is not one. Asking for
    the state exactly at a keyframe is nonetheless an ordinary request - the
    first column of a window often lands on one - and the answer to it is the
    keyframe itself, so the identity is expressed by having nothing to apply
    rather than by building a matrix that does nothing.
    """

    if interval_s <= 0.0:
        return None

    return matrix_exponential(build_system_matrix(segment.settings), interval_s)


def _advanced(propagator: Matrix | None, state: tuple[float, ...]) -> tuple[float, ...]:
    """Apply `propagator` to `state`, holding the unit state at exactly one.

    The unit state is the constant one that turns `dy/dt = Ay + b` into
    `dy/dt = Ay`, and its row in the system matrix is empty, so it is constant
    by construction. Its propagator entry is nonetheless a product of two
    rounded factors - `matrix_exponential` computes the shift and the shifted
    series separately - and lands within a few units in the last place of one
    rather than on it. Left to drift, the constant that scales every delivery
    term would drift with it. Writing it back is restating what the matrix
    already says, and it is what the stepped path does too: it reads the
    vector out of the compartments each step with this entry set to one.
    """

    if propagator is None:
        return state

    advanced = list(propagate(propagator, state))
    advanced[UNIT_STATE] = 1.0

    return tuple(advanced)


def _require_state(state: tuple[float, ...]) -> None:
    """Refuse a state vector the equations could not be read against.

    Raises:
        SimulationConfigurationError: `state` is not `STATE_SIZE` long, holds
            a non-finite value, or does not carry exactly one in `UNIT_STATE`.
    """

    if len(state) != STATE_SIZE:
        raise SimulationConfigurationError(
            f"a state has {len(state)} entries but the equations carry {STATE_SIZE}"
        )

    for index, value in enumerate(state):
        if not isfinite(value):
            raise SimulationConfigurationError(f"state[{index}] is {value}, which is not finite")

    if state[UNIT_STATE] != 1.0:
        raise SimulationConfigurationError(
            f"state[{UNIT_STATE}] is the constant one the forcing terms are read against, "
            f"not {state[UNIT_STATE]}"
        )
