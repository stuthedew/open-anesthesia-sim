"""The settings that each stretch of a run was stepped under, and when each stretch opened.

A setting changes only when a reader moves a control. Between two changes,
every setting that the equations read is constant, and this module calls that
span a *stretch*. A `RunDefinition` records each stretch of one run: its
settings, and the second of the case at which it opened.

**This module computes no state.** A run stores the state that each of its
steps wrote (`core/stored_states.py`), and every reader of a second that the
run has reached takes the state from that record. The application reads two
things from this module: the settings that a step ran under, and the seconds
at which a setting changed. `core/prediction.py` computes the states that a
preview draws past the second a run has reached.

The record does not grow with the length of the run. It holds one stretch for
each setting change, however many seconds the run has stepped.

Through v0.4.x this record was called a run's *score*, in the musical sense,
and `docs/releases/` and the completed rows of `ROADMAP.md` still use that
word (`PL-ZX12`, project owner, 2026-09-08). Until `PL-Z6C8` the record also
computed a state from its settings by formula, so older documents describe a
run as its definition.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import isfinite

from anesthesia_sim.core.checked_record import restore_through_checks
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import UptakeEquationSettings
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant


@dataclass(frozen=True, slots=True)
class RunSegment:
    """One stretch of a run during which every setting the equations read is constant.

    Attributes:
        settings: The record that `build_system_matrix` assembles $`A`$ from.
            It is in force from `opened_at_s` until the next stretch opens.
            Its flows are the litres per minute that were set, and its
            delivered concentration is the percent that was dialled. So a
            system configured from them rebuilds these settings exactly
            (`PL-SM5V`, `PL-NJPB`). The vaporizer maximum that the dial was
            set under travels with the settings, and the record refuses a dial
            above that maximum (`PL-BBMG`).
        opened_at_s: The second at which the stretch opened, on the case's
            own axis. That axis is simulated time since induction. It is not
            the time elapsed since the run holding the stretch began. The two
            are the same number for a run that opens at induction, but not
            for a branch. The first step under these settings is the step
            from this second to the next.

    Raises:
        TypeError: `opened_at_s` is not a `CaseInstant`, so nothing has
            checked it against the supported run length
            (`core/supported_ranges.py`).
    """

    settings: UptakeEquationSettings
    opened_at_s: CaseInstant

    def __post_init__(self) -> None:
        require_case_instant("opened_at_s", self.opened_at_s)

    def __setstate__(self, state: object) -> None:
        """Restore an unpickled or copied record through the constructor's checks (`PL-8W1Q`)."""

        restore_through_checks(self, state)


class RunDefinition:
    """The settings one run was stepped under, as one stretch for each setting change.

    It is built with the settings a run starts under and the second it opens
    at, and is then told what happened. `advance_to` moves the second the run
    has reached. `record_change` closes the open stretch at that second and
    opens a new one under new settings. Those two calls are the whole of what
    the record takes.

    **A change is recorded at the second the run has reached, and nowhere
    else.** `record_change` deliberately has no instant argument. A setting
    change takes effect when it is made. A caller free to name a different
    second could place a change inside a span that the run had already stepped
    under other settings. That would not fail. The record would then name
    settings that no step of that span ran under, with nothing to mark it as
    wrong. Removing the argument removes the failure, and
    `.claude/rules/expert-review.md` prefers that to validating the argument.

    **It returns a stretch only within the run.** `segment_at` and
    `reaching_segment_at` refuse a second before the run opened and a second
    past `reached_s`.
    """

    __slots__ = ("_reached_s", "_segments")

    def __init__(self, settings: UptakeEquationSettings, *, opened_at_s: CaseInstant) -> None:
        """Open the record at `opened_at_s`, with one stretch under `settings`.

        **The opening instant is on the case's axis, and it is required.** A
        run that begins at induction opens at zero. A branch's record opens
        at the second at which its parent's stretch opened, which is the
        stretch that the step reaching the fork ran under. Both instants are
        on the same axis. The parameter deliberately has no default. A
        default of zero would be wrong for a branch, whose stretches would
        then all be placed at seconds the case never changed a setting at. So
        a caller must say which instant it means, and a caller that forgets
        gets a `TypeError`.

        Args:
            settings: The settings the run begins under. Their flows are
                inside the supported flow ranges by construction. Each flow is
                a checked type that cannot hold a value outside its range, so
                neither this method nor `record_change` checks a flow again
                (`PL-HSFV`). The record carries the vaporizer maximum beside
                the dial and refuses a dial above that maximum. So any record
                a run can be handed is one the circuit would have accepted
                (`PL-BBMG`).
            opened_at_s: The case instant at which the first stretch opens, in
                seconds. It is zero for a run beginning at induction. For a
                branch, it is the second at which the parent's stretch opened
                that the step reaching the fork ran under. It lies before the
                fork, unless the fork is at the case's opening
                (`app/controller.py`, `SimulationController._open_at`). It is
                a `CaseInstant`, so it is at or after induction and inside
                the supported run length (`PL-73ZN`).

        Raises:
            TypeError: `opened_at_s` is not a `CaseInstant`, so nothing has
                checked it against the supported run length
                (`core/supported_ranges.py`).
        """

        self._segments: tuple[RunSegment, ...] = (RunSegment(settings, opened_at_s),)
        self._reached_s = opened_at_s

    @property
    def opened_at_s(self) -> CaseInstant:
        """The case instant at which this record's first stretch opens.

        It is read from the first stretch rather than stored beside it, so
        the opening is recorded in one place. `_require_within_run` reads the
        same field.

        **On a branch, this instant is at or before the fork.** A branch's
        first stretch is its parent's stretch that the step reaching the fork
        ran under, and that stretch opened before the fork. The span between
        this instant and the fork belongs to the parent. That is why the app
        layer clips a drawn axis at the fork rather than here
        (`SimulationController.began_at_s`).
        """

        return self._segments[0].opened_at_s

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

        It records no state. A run stores each step's state in a record of
        its own (`core/stored_states.py`). What this method changes is the
        second at which `record_change` opens the next stretch, and the last
        second for which `segment_at` returns one.

        The time reached needs no lower bound of its own. `__init__` sets it
        from `opened_at_s`, and this method is its only other writer and never
        lowers it. That invariant is what lets `_require_within_run` treat the
        span from the opening to the time reached as a closed interval. So a
        second writer of `_reached_s`, such as a reset in place or a
        deserializer restoring a saved run, would have to re-establish the
        invariant rather than assume it.

        Its upper bound is the same as the opening's: the end of the supported
        run length. The `CaseInstant` type enforces that bound. The
        application moves the time reached only to an instant that a step
        count lands on: the instant of each step, or of a branch's fork
        (`app/controller.py`). `SimulationState.advance` refuses the step that
        would carry that count past the span. So no step already taken lands
        on an instant that cannot be built. `MAXIMUM_STEP_COUNT` in
        `core/supported_ranges.py` is the last step's count, and the instant
        at which that step lands is the end of the supported run length
        (`PL-8H2R`).

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`, so nothing has
                checked it against the supported run length
                (`core/supported_ranges.py`).
            SimulationConfigurationError: `instant_s` is earlier than the time
                already reached. A run cannot un-happen. Moving the time
                reached backwards would leave the stretches recorded after it
                opening at seconds the record says the run has not reached.
                The check runs before the time reached moves, so a refused
                call leaves it where it was.
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
        would step differently, so the call is dropped. Second, a change
        at an instant where a stretch has already opened belongs to that same
        stretch. This happens when two controls are moved between one step and
        the next. The change replaces that stretch's settings instead of
        opening a zero-length one, because the next step runs under the
        settings in force when it starts, which are the last ones written.
        Third, if that replacement lands back on the settings the previous
        stretch already had, the open stretch is removed entirely, because
        nothing about the run differs. This happens when a dial is moved and
        moved back before a step runs.

        The third case is what keeps the record one of the run rather than of
        the mouse. The interface's own control timeline applies the same rule
        to the entries a reader sees.
        """

        open_segment = self._segments[-1]

        if settings == open_segment.settings:
            return

        if self._reached_s == open_segment.opened_at_s:
            if len(self._segments) > 1 and settings == self._segments[-2].settings:
                self._segments = self._segments[:-1]
                return

            self._segments = (*self._segments[:-1], RunSegment(settings, open_segment.opened_at_s))
            return

        self._segments = (*self._segments, RunSegment(settings, self._reached_s))

    def segment_at(self, instant_s: float) -> RunSegment:
        """The stretch of constant settings in force from `instant_s` onward.

        **At an instant where a stretch opens, this is the stretch that
        opens there.** It is the settings that the next step runs under,
        including a change made at `instant_s`. The step that reached
        `instant_s` ran under the stretch before it, which
        `reaching_segment_at` returns. The two differ only at a second where
        a setting changed (`PL-ZR49`).

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
        returns. At a second where a setting changed it is the stretch before
        the change, because the new settings apply only from that second
        onward. At the run's opening no step has reached the instant, so the
        result is the first stretch.

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

    def _segment_index_at(self, instant_s: float) -> int:
        """Index of the segment the run was under at `instant_s`.

        It uses a binary search, so the cost does not grow with the number of
        setting changes as a linear walk would. The segment openings ascend
        because `record_change` only ever appends at `reached_s`, which never
        decreases.

        **An instant before the first opening is refused rather than wrapped
        round.** `bisect_right` returns zero there, so the index is `-1`.
        Python treats that index as the *last* segment, the one furthest from
        any right answer, and nothing then fails. `_require_within_run`
        already refuses such an instant on every public path, so this check
        is the second of two guards rather than the first. It is here because
        the failure it prevents is silent and the check costs one comparison.

        Raises:
            SimulationConfigurationError: `instant_s` precedes the instant the
                run opens at.
        """

        index = bisect_right(self._segments, instant_s, key=_opening_of) - 1

        if index < 0:
            raise SimulationConfigurationError(
                f"this run opens at {self._segments[0].opened_at_s} s, so it was under "
                f"no settings at {instant_s} s"
            )

        return index

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

        opening_s = self._segments[0].opened_at_s

        if instant_s < opening_s:
            raise SimulationConfigurationError(
                f"a run that opens at {opening_s} s was under no settings at {instant_s} s, "
                "before it began"
            )

        if instant_s > self._reached_s:
            raise SimulationConfigurationError(
                f"this run has reached {self._reached_s} s, so it has been under no settings "
                f"at {instant_s} s"
            )


def _opening_of(segment: RunSegment) -> float:
    """When `segment` opens, which is the key that the segment search is ordered on."""

    return segment.opened_at_s
