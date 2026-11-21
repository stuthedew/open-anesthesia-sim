"""The record of a run's stored states returns each state for its own second, unchanged.

Every expected state below is a literal written in this file, so no test
reads its expected value back from the record it exercises.
"""

import copy
import pickle
from collections.abc import Callable

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.stored_states import StoredStates
from anesthesia_sim.core.supported_ranges import CaseInstant

# Each state is six fractions of 1 atm, the delivered and the exhausted agent
# in litres since the case began, and the constant one. The values are chosen
# to be told apart at a glance, and several have no short binary form, so a
# record that rounded a value would return a different one.
OPENING = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
AFTER_ONE = (0.011, 0.0052, 0.0007, 0.0013, 3.1e-05, 1.7e-06, 0.1 / 3.0, 0.01, 1.0)
AFTER_TWO = (0.012, 0.0061, 0.0009, 0.0016, 4.2e-05, 2.3e-06, 0.2 / 3.0, 0.02, 1.0)
AFTER_THREE = (0.013, 0.0068, 0.0011, 0.0019, 5.5e-05, 3.1e-06, 0.3 / 3.0, 0.03, 1.0)


def _record_of_four(opened_at_s: int) -> StoredStates:
    record = StoredStates(OPENING, CaseInstant(opened_at_s))

    for state in (AFTER_ONE, AFTER_TWO, AFTER_THREE):
        record.append(state)

    return record


def test_each_second_returns_the_state_stored_for_it_bit_for_bit() -> None:
    record = _record_of_four(opened_at_s=0)

    assert record.opened_at_s == 0
    assert record.reached_s == 3
    assert record.state_at(CaseInstant(0)) == OPENING
    assert record.state_at(CaseInstant(1)) == AFTER_ONE
    assert record.state_at(CaseInstant(2)) == AFTER_TWO
    assert record.state_at(CaseInstant(3)) == AFTER_THREE


def test_a_record_opened_part_way_through_a_case_keeps_the_cases_seconds() -> None:
    """A branch's record opens at its fork, and each second keeps its number in the case."""

    record = _record_of_four(opened_at_s=1_800)

    assert record.opened_at_s == 1_800
    assert record.reached_s == 1_803
    assert record.state_at(CaseInstant(1_800)) == OPENING
    assert record.state_at(CaseInstant(1_802)) == AFTER_TWO
    assert record.state_at(CaseInstant(1_803)) == AFTER_THREE


@pytest.mark.parametrize("instant_s", [1_799, 1_804, 0, 86_400])
def test_a_second_the_record_does_not_hold_is_refused_and_named(instant_s: int) -> None:
    """No state is returned from the nearest stored second in place of a missing one."""

    record = _record_of_four(opened_at_s=1_800)

    with pytest.raises(SimulationConfigurationError) as refusal:
        record.state_at(CaseInstant(instant_s))

    message = str(refusal.value)
    assert f"no state at {instant_s} s" in message
    assert "from 1800 s" in message
    assert "to 1803 s" in message


def test_an_instant_that_was_not_built_as_a_case_instant_is_refused() -> None:
    record = _record_of_four(opened_at_s=0)

    with pytest.raises(TypeError, match="CaseInstant"):
        record.state_at(2)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="CaseInstant"):
        StoredStates(OPENING, 0)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("state", "names"),
    [
        ((0.011, 1.2, 0.0007, 0.0013, 3.1e-05, 1.7e-06, 0.03, 0.01, 1.0), "alveolar"),
        ((0.011, 0.0052, 0.0007, 0.0013, 3.1e-05, 1.7e-06, 0.03, 0.01, 0.5), "state"),
        ((0.011, 0.0052, 0.0007, 0.0013, 3.1e-05, 1.7e-06, 0.03, 0.01), "8 entries"),
        ((0.011, 0.0052, 0.0007, 0.0013, 3.1e-05, 1.7e-06, -0.03, 0.01, 1.0), "delivered"),
    ],
)
def test_a_state_the_equations_cannot_use_is_refused_and_nothing_is_stored(
    state: tuple[float, ...], names: str
) -> None:
    record = _record_of_four(opened_at_s=0)

    with pytest.raises(SimulationConfigurationError, match=names):
        record.append(state)

    assert record.reached_s == 3
    assert record.state_at(CaseInstant(3)) == AFTER_THREE

    with pytest.raises(SimulationConfigurationError, match=names):
        StoredStates(state, CaseInstant(0))


def test_restarting_a_record_discards_every_state_it_held() -> None:
    record = _record_of_four(opened_at_s=600)

    record.restart_from(AFTER_TWO, CaseInstant(0))

    assert record.opened_at_s == 0
    assert record.reached_s == 0
    assert record.state_at(CaseInstant(0)) == AFTER_TWO

    with pytest.raises(SimulationConfigurationError, match="no state at 600 s"):
        record.state_at(CaseInstant(600))


def test_a_refused_restart_leaves_the_record_as_it_was() -> None:
    record = _record_of_four(opened_at_s=600)
    not_a_state = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0)

    with pytest.raises(SimulationConfigurationError):
        record.restart_from(not_a_state, CaseInstant(0))

    assert record.opened_at_s == 600
    assert record.state_at(CaseInstant(603)) == AFTER_THREE


def _pickled(record: StoredStates) -> StoredStates:
    restored = pickle.loads(pickle.dumps(record))
    assert isinstance(restored, StoredStates)

    return restored


@pytest.mark.parametrize("duplicate", [copy.copy, copy.deepcopy, _pickled])
def test_a_copy_holds_the_same_states_and_grows_apart_from_the_original(
    duplicate: Callable[[StoredStates], StoredStates],
) -> None:
    """A copy that shared its array would store one run's later states in both records."""

    record = _record_of_four(opened_at_s=1_800)
    record_copy = duplicate(record)

    assert record_copy.opened_at_s == 1_800
    assert record_copy.reached_s == 1_803
    assert record_copy.state_at(CaseInstant(1_801)) == AFTER_ONE
    assert record_copy.state_at(CaseInstant(1_803)) == AFTER_THREE

    record_copy.append(AFTER_ONE)

    assert record_copy.reached_s == 1_804
    assert record.reached_s == 1_803
