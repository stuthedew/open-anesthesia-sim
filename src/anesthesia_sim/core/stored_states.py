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
24-hour run holds 86 401 states, about 6.2 MB. The same states as tuples took
30 MB (`PL-7CY5`, measured 2026-11-21). `numpy` is not available to `core/`
(`tools/import_boundary_check.py`).

The record is indexed by the case's own clock. A branch's record opens at the
second where the branch was taken, and that second keeps its number.
"""

from __future__ import annotations

from array import array

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import STATE_SIZE, require_canonical_state
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant


class StoredStates:
    """The states of one run, from the second it opened at to the second it has reached.

    The record only grows, one state at a time, and each state it accepts has
    passed `require_canonical_state`. A stored state is never changed.

    Args:
        opening: The state the run opens from.
        opened_at_s: The second of the case at which the run opens. It is 0
            for a run that starts a case, and the fork's second for a branch.

    Raises:
        TypeError: `opened_at_s` is not a `CaseInstant`.
        SimulationConfigurationError: `opening` is not a state that the
            equations can be applied to (`require_canonical_state`).
    """

    __slots__ = ("_opened_at_s", "_values")

    def __init__(self, opening: tuple[float, ...], opened_at_s: CaseInstant) -> None:
        require_case_instant("opened_at_s", opened_at_s)
        require_canonical_state(opening)

        self._opened_at_s = opened_at_s
        self._values = array("d", opening)

    @property
    def opened_at_s(self) -> CaseInstant:
        """The second of the case at which this record's first state was stored."""

        return self._opened_at_s

    @property
    def reached_s(self) -> CaseInstant:
        """The second of the case at which this record's last state was stored."""

        return CaseInstant(self._opened_at_s + len(self._values) // STATE_SIZE - 1)

    def append(self, state: tuple[float, ...]) -> None:
        """Store the state of the second after `reached_s`.

        Raises:
            SimulationConfigurationError: `state` is not a state that the
                equations can be applied to (`require_canonical_state`).
                Nothing is stored when it is refused.
        """

        require_canonical_state(state)
        self._values.extend(state)

    def state_at(self, instant_s: CaseInstant) -> tuple[float, ...]:
        """Return the state stored for `instant_s`, bit for bit as its step wrote it.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: `instant_s` is before `opened_at_s`
                or after `reached_s`. The record holds no state there, and no
                state is substituted from the nearest second.
        """

        require_case_instant("instant_s", instant_s)

        if not self._opened_at_s <= instant_s <= self.reached_s:
            raise SimulationConfigurationError(
                f"this run stores no state at {instant_s} s: it stores one state for each "
                f"second from {self._opened_at_s} s, where it opened, to {self.reached_s} s, "
                "the second it has reached"
            )

        first = (instant_s - self._opened_at_s) * STATE_SIZE

        return tuple(self._values[first : first + STATE_SIZE])

    def __copy__(self) -> StoredStates:
        """Return a record with its own array, so that the two never grow as one.

        A shallow copy that shared the array would store every later state
        of either run in both records.
        """

        duplicate = StoredStates.__new__(StoredStates)
        duplicate._opened_at_s = self._opened_at_s
        duplicate._values = array("d", self._values)

        return duplicate

    def __deepcopy__(self, memo: dict[int, object]) -> StoredStates:
        """Return a record with its own array, as `__copy__` does."""

        return self.__copy__()

    def restart_from(self, opening: tuple[float, ...], opened_at_s: CaseInstant) -> None:
        """Discard every stored state and open again from `opening` at `opened_at_s`.

        A run that is reset starts over, and its record starts over with it
        (`SimulationState.reset`).

        Raises:
            TypeError: `opened_at_s` is not a `CaseInstant`.
            SimulationConfigurationError: `opening` is not a state that the
                equations can be applied to. The record is unchanged when it
                is refused.
        """

        require_case_instant("opened_at_s", opened_at_s)
        require_canonical_state(opening)

        self._opened_at_s = opened_at_s
        self._values = array("d", opening)
