"""Every state a run has reached, one for each whole second, held in one array.

A run takes one step per second (`core/simulation_step.py`), and each step
appends the state it wrote to a `StoredStates`. A state that the interface
shows, tests a mark against or opens a branch from is read from that record.
Nothing computes such a state a second time, so two readers of one second
cannot disagree about it (`PL-MH9J`, decided in `PL-7CY5`).

A state here is the state vector of `core/governing_equations.py`, in that
module's order: the six partial-pressure fractions, the delivered and the
exhausted agent in litres since the case began, and the constant one. The two
amounts are totals for the case, where the vector that a step propagates
holds only that step's own delivered and exhausted agent.

The states are stored as one `array` of `STATE_SIZE` doubles per second. A
24-hour run holds 86 401 states, about 6.2 MB, and its compensation terms take
1.4 MB more. The same states as tuples took 30 MB (`PL-7CY5`, measured
2026-11-21). `numpy` is not available to `core/`
(`tools/import_boundary_check.py`).

The record is indexed by the case's own clock. A branch's record is a copy of
its parent's record up to the second where the branch was taken, and the
branch's steps append to the copy (`through`, `PL-FST0`). So a branch holds
the case from the same second as its parent, and each second keeps its number.

**Each second also stores the two compensation terms of the running totals.**
The delivered and the exhausted agent are sums over every step, and
`AgentSimulationValidator` keeps a compensation term beside each sum, which
carries the rounding error of the additions so far into the next addition
(`core/agent_simulation_validation.py`). A run that restarted from a stored
total with a term of zero would add the same amounts and reach a total that
can differ in its last bit. The accounting panel shows each total to
0.1 L of vapour (`app/formatting.py`), and a total can lie on the boundary
between two displayed values. So a
branch restarts from the stored total and its stored term, and repeats
its parent's totals bit for bit (`PL-FST0`).
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass
from typing import cast

from anesthesia_sim.core.agent_simulation_validation import (
    TotalsCompensation,
    require_totals_compensation,
)
from anesthesia_sim.core.checked_record import require_state_by_name, restored_through_checks
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    FRACTION_STATE_NAMES,
    STATE_SIZE,
    require_canonical_state,
)
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant

COMPENSATION_SIZE = 2
"""How many compensation terms a second stores: one for each of the two running totals."""


@restored_through_checks
@dataclass(frozen=True, slots=True)
class Keyframe:
    """A state that a run stored, and the second of the case that it belongs to.

    The application builds one from an instant and the state that a run
    stored for it, to name a fork and each end of the step that reached it
    (`SimulationController._stored_keyframe`). The two travel together so
    that a state cannot be tested or resumed from under another second's
    instant.

    Attributes:
        instant_s: The second for which the state was stored, on the case's
            own axis. That axis is simulated time since induction. It is not
            the time elapsed since the run holding the state began. A branch
            forked at 900 s holds its fork's state at 900 s, although the
            branch has taken no step.
        state: The state, in `governing_equations`' own state order,
            `STATE_SIZE` entries long. Its delivered and exhausted agent are
            totals from the start of the *case*. A branch continues its
            parent's totals, because the agent a patient has received belongs
            to the case. A branch that restarted the count at zero would
            report a mass balance for a patient who does not exist.

    Raises:
        TypeError: `instant_s` is not a `CaseInstant`, so nothing has checked
            it against the supported run length (`core/supported_ranges.py`).
            The state is not checked here. A `StoredStates` checked it when
            it stored it.
    """

    instant_s: CaseInstant
    state: tuple[float, ...]

    def __post_init__(self) -> None:
        require_case_instant("instant_s", self.instant_s)


class StoredStates:
    """The states of one run, from the second it opened at to the second it has reached.

    The record only grows, one state at a time, and each state it accepts has
    passed `require_canonical_state`. A stored state is never changed.

    Args:
        opening: The state the run opens from.
        opened_at_s: The second of the case at which the record opens. It is 0
            for a run that starts a case.
        compensation: The compensation terms of the delivered and the
            exhausted totals at `opening`
            (`AgentUptakeSystem.accounting_compensation`).

    Raises:
        TypeError: `opened_at_s` is not a `CaseInstant`, or `compensation` is
            not a `TotalsCompensation`.
        SimulationConfigurationError: `opening` is not a state that the
            equations can be applied to (`require_canonical_state`).
    """

    __slots__ = ("_compensations", "_opened_at_s", "_values")

    def __init__(
        self, opening: tuple[float, ...], opened_at_s: CaseInstant, compensation: TotalsCompensation
    ) -> None:
        require_case_instant("opened_at_s", opened_at_s)
        require_canonical_state(opening)
        require_totals_compensation(compensation)

        self._opened_at_s = opened_at_s
        self._values = array("d", opening)
        self._compensations = array("d", (compensation.delivered_l, compensation.exhausted_l))

    @property
    def opened_at_s(self) -> CaseInstant:
        """The second of the case at which this record's first state was stored."""

        return self._opened_at_s

    @property
    def reached_s(self) -> CaseInstant:
        """The second of the case at which this record's last state was stored."""

        return CaseInstant(self._opened_at_s + len(self._values) // STATE_SIZE - 1)

    def append(self, state: tuple[float, ...], compensation: TotalsCompensation) -> None:
        """Store the state of the second after `reached_s`, and the totals' compensation terms.

        Raises:
            TypeError: `compensation` is not a `TotalsCompensation`.
            SimulationConfigurationError: `state` is not a state that the
                equations can be applied to (`require_canonical_state`).
                Nothing is stored when either is refused.
        """

        require_canonical_state(state)
        require_totals_compensation(compensation)
        self._values.extend(state)
        self._compensations.extend((compensation.delivered_l, compensation.exhausted_l))

    def state_at(self, instant_s: CaseInstant) -> tuple[float, ...]:
        """Return the state stored for `instant_s`, bit for bit as its step wrote it.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: `instant_s` is before `opened_at_s`
                or after `reached_s`. The record holds no state there, and no
                state is substituted from the nearest second.
        """

        self._require_stored(instant_s)

        first = (instant_s - self._opened_at_s) * STATE_SIZE

        return tuple(self._values[first : first + STATE_SIZE])

    def compensation_at(self, instant_s: CaseInstant) -> TotalsCompensation:
        """Return the compensation terms of the two running totals at `instant_s`.

        A branch continues its totals from them
        (`AgentUptakeSystem.resume_at`).

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: The record holds no state for
                `instant_s`.
        """

        self._require_stored(instant_s)

        first = (instant_s - self._opened_at_s) * COMPENSATION_SIZE

        return TotalsCompensation(
            delivered_l=self._compensations[first], exhausted_l=self._compensations[first + 1]
        )

    def through(self, instant_s: CaseInstant) -> StoredStates:
        """Return a new record that holds this record's seconds up to and including `instant_s`.

        A branch taken at `instant_s` opens from the result
        (`SimulationState`). The result has its own arrays, so the two
        records never grow as one.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: The record holds no state for
                `instant_s`.
        """

        self._require_stored(instant_s)

        seconds = instant_s - self._opened_at_s + 1
        shortened = StoredStates.__new__(StoredStates)
        shortened._opened_at_s = self._opened_at_s
        shortened._values = self._values[: seconds * STATE_SIZE]
        shortened._compensations = self._compensations[: seconds * COMPENSATION_SIZE]

        return shortened

    def _require_stored(self, instant_s: CaseInstant) -> None:
        """Require a second that this record holds a state for.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: `instant_s` is before `opened_at_s`
                or after `reached_s`.
        """

        require_case_instant("instant_s", instant_s)

        if not self._opened_at_s <= instant_s <= self.reached_s:
            raise SimulationConfigurationError(
                f"this run stores no state at {instant_s} s: it stores one state for each "
                f"second from {self._opened_at_s} s, where it opened, to {self.reached_s} s, "
                "the second it has reached"
            )

    def fraction_series(
        self, first_s: CaseInstant, last_s: CaseInstant
    ) -> tuple[array[float], ...]:
        """Return each compartment's fraction at every second from `first_s` to `last_s`.

        The chart reads a window this way, to find the seconds at which a
        fraction is highest and lowest between two drawn columns
        (`PL-BLZJ`). Reading each second's whole state with `state_at` gives
        the same numbers. Over a twelve-hour window it took 53 ms, against
        2 ms for the six fractions read this way (measured 2026-11-21).

        Args:
            first_s: The first second to return.
            last_s: The last second to return, which is not before `first_s`.

        Returns:
            One array for each fraction, in the order that
            `FRACTION_STATE_NAMES` gives them in
            `core/governing_equations.py`: inspired, alveolar, mixed venous
            and the three tissue groups. Each array holds `last_s - first_s +
            1` fractions of 1 atm in order of time, bit for bit as each step
            wrote them. The arrays are new, so changing one does not change
            the record.

        Raises:
            TypeError: `first_s` or `last_s` is not a `CaseInstant`.
            SimulationConfigurationError: `last_s` is before `first_s`, or
                the record holds no state for `first_s` or for `last_s`.
        """

        require_case_instant("first_s", first_s)
        require_case_instant("last_s", last_s)

        if last_s < first_s:
            raise SimulationConfigurationError(
                f"a series from {first_s} s to {last_s} s ends before it begins"
            )

        if first_s < self._opened_at_s or last_s > self.reached_s:
            raise SimulationConfigurationError(
                f"this run stores no state for every second from {first_s} s to {last_s} s: "
                f"it stores one state for each second from {self._opened_at_s} s, where it "
                f"opened, to {self.reached_s} s, the second it has reached"
            )

        start = (first_s - self._opened_at_s) * STATE_SIZE
        stop = (last_s - self._opened_at_s + 1) * STATE_SIZE

        return tuple(
            self._values[start + position : stop : STATE_SIZE]
            for position, _name in FRACTION_STATE_NAMES
        )

    def __copy__(self) -> StoredStates:
        """Return a record with its own arrays, so that the two never grow as one.

        A shallow copy that shared the arrays would store every later state
        of either run in both records.
        """

        return self.through(self.reached_s)

    def __deepcopy__(self, memo: dict[int, object]) -> StoredStates:
        """Return a record with its own arrays, as `__copy__` does."""

        return self.__copy__()

    def __getstate__(self) -> dict[str, object]:
        """Return the record's opening second, states and compensation terms, by name, for a pickle.

        A copy does not use this pair. `__copy__` copies arrays that this
        record's own methods filled, and each of them checked every state
        before storing it. A pickle may have been saved by an older version or
        edited since, so it is checked again as it loads.
        """

        return {
            "opened_at_s": self._opened_at_s,
            "values": self._values,
            "compensations": self._compensations,
        }

    def __setstate__(self, state: object) -> None:
        """Rebuild an unpickled record by storing each saved second again, through its checks.

        The record opens from the first saved state, as the constructor opens
        it, and then appends each later second's state and compensation terms
        with `append`. So every state passes `require_canonical_state` again,
        and the record is refused where the constructor or `append` would
        refuse it (`PL-HXNL`).

        Raises:
            TypeError: `state` is not a dict holding exactly `opened_at_s`,
                `values` and `compensations` (`require_state_by_name`), the
                two arrays are not arrays of `float`, or `opened_at_s` is not a
                `CaseInstant`.
            SimulationConfigurationError: the arrays do not hold one whole
                state and one pair of compensation terms for each of the same
                number of seconds, at least one, or a saved state is not one
                that the equations can be applied to.
        """

        by_name = require_state_by_name(self, state, ("opened_at_s", "values", "compensations"))
        values = by_name["values"]
        compensations = by_name["compensations"]

        if not (
            isinstance(values, array)
            and values.typecode == "d"
            and isinstance(compensations, array)
            and compensations.typecode == "d"
        ):
            raise TypeError(
                "StoredStates is restored from two arrays of float, not from a "
                f"{type(values).__name__} and a {type(compensations).__name__}"
            )

        seconds = len(values) // STATE_SIZE

        if (
            seconds < 1
            or len(values) != seconds * STATE_SIZE
            or len(compensations) != seconds * COMPENSATION_SIZE
        ):
            raise SimulationConfigurationError(
                f"the saved record holds {len(values)} state values and {len(compensations)} "
                f"compensation terms, which is not {STATE_SIZE} values and "
                f"{COMPENSATION_SIZE} terms for each of the same number of seconds, at least one"
            )

        def saved(second: int) -> tuple[tuple[float, ...], TotalsCompensation]:
            """Return the state and the compensation terms saved for the `second`-th second."""

            first = second * COMPENSATION_SIZE

            return tuple(values[second * STATE_SIZE : (second + 1) * STATE_SIZE]), (
                TotalsCompensation(
                    delivered_l=compensations[first], exhausted_l=compensations[first + 1]
                )
            )

        opening, compensation = saved(0)
        StoredStates.__init__(
            self, opening, cast("CaseInstant", by_name["opened_at_s"]), compensation
        )

        for second in range(1, seconds):
            self.append(*saved(second))

    def restart_from(
        self, opening: tuple[float, ...], opened_at_s: CaseInstant, compensation: TotalsCompensation
    ) -> None:
        """Discard every stored state and open again from `opening` at `opened_at_s`.

        A run that is reset starts over, and its record starts over with it
        (`SimulationState.reset`).

        Raises:
            TypeError: `opened_at_s` is not a `CaseInstant`, or `compensation`
                is not a `TotalsCompensation`.
            SimulationConfigurationError: `opening` is not a state that the
                equations can be applied to. The record is unchanged when
                either is refused.
        """

        require_case_instant("opened_at_s", opened_at_s)
        require_canonical_state(opening)
        require_totals_compensation(compensation)

        self._opened_at_s = opened_at_s
        self._values = array("d", opening)
        self._compensations = array("d", (compensation.delivered_l, compensation.exhausted_l))
