"""The record of a run's stored states returns each state for its own second, unchanged.

Every expected state below is a literal written in this file, so no test
reads its expected value back from the record it exercises.
"""

import copy
import pickle
from collections.abc import Callable

import pytest

from anesthesia_sim.core.agent_simulation_validation import TotalsCompensation
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

# The compensation terms stored beside each state, in litres. Each is the
# size of a rounding error in its total, and a term may be negative.
NO_TERMS = TotalsCompensation(delivered_l=0.0, exhausted_l=0.0)
TERMS_AFTER_ONE = TotalsCompensation(delivered_l=6.9e-18, exhausted_l=-1.1e-18)
TERMS_AFTER_TWO = TotalsCompensation(delivered_l=-2.3e-17, exhausted_l=5.4e-17)
TERMS_AFTER_THREE = TotalsCompensation(delivered_l=7.6e-17, exhausted_l=1.1e-17)


def _record_of_four(opened_at_s: int) -> StoredStates:
    record = StoredStates(OPENING, CaseInstant(opened_at_s), NO_TERMS)

    for state, terms in (
        (AFTER_ONE, TERMS_AFTER_ONE),
        (AFTER_TWO, TERMS_AFTER_TWO),
        (AFTER_THREE, TERMS_AFTER_THREE),
    ):
        record.append(state, terms)

    return record


def test_each_second_returns_the_state_stored_for_it_bit_for_bit() -> None:
    record = _record_of_four(opened_at_s=0)

    assert record.opened_at_s == 0
    assert record.reached_s == 3
    assert record.state_at(CaseInstant(0)) == OPENING
    assert record.state_at(CaseInstant(1)) == AFTER_ONE
    assert record.state_at(CaseInstant(2)) == AFTER_TWO
    assert record.state_at(CaseInstant(3)) == AFTER_THREE


def test_each_second_returns_the_compensation_terms_stored_for_it() -> None:
    record = _record_of_four(opened_at_s=1_800)

    assert record.compensation_at(CaseInstant(1_800)) == NO_TERMS
    assert record.compensation_at(CaseInstant(1_801)) == TERMS_AFTER_ONE
    assert record.compensation_at(CaseInstant(1_802)) == TERMS_AFTER_TWO
    assert record.compensation_at(CaseInstant(1_803)) == TERMS_AFTER_THREE


@pytest.mark.parametrize("instant_s", [1_799, 1_804])
def test_compensation_terms_are_refused_for_a_second_the_record_does_not_hold(
    instant_s: int,
) -> None:
    record = _record_of_four(opened_at_s=1_800)

    with pytest.raises(SimulationConfigurationError, match=f"no state at {instant_s} s"):
        record.compensation_at(CaseInstant(instant_s))

    with pytest.raises(TypeError, match="CaseInstant"):
        record.compensation_at(1_801)  # type: ignore[arg-type]


@pytest.mark.parametrize("terms", [(1e-17, 2e-17), [1e-17, 2e-17], 1e-17, None])
def test_terms_that_were_not_built_as_a_totals_compensation_are_refused(terms: object) -> None:
    """A refused pair stores nothing, so the states and the terms stay one for each second."""

    record = _record_of_four(opened_at_s=0)

    with pytest.raises(TypeError, match="not TotalsCompensation"):
        record.append(AFTER_ONE, terms)  # type: ignore[arg-type]

    assert record.reached_s == 3
    assert record.compensation_at(CaseInstant(3)) == TERMS_AFTER_THREE

    with pytest.raises(TypeError, match="not TotalsCompensation"):
        StoredStates(OPENING, CaseInstant(0), terms)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="not TotalsCompensation"):
        record.restart_from(OPENING, CaseInstant(0), terms)  # type: ignore[arg-type]

    assert record.reached_s == 3
    assert record.state_at(CaseInstant(3)) == AFTER_THREE


def test_a_record_cut_at_a_second_holds_the_states_and_terms_up_to_that_second() -> None:
    """A branch taken at second 1 802 opens from the record up to and including that second."""

    record = _record_of_four(opened_at_s=1_800)

    shortened = record.through(CaseInstant(1_802))

    assert shortened.opened_at_s == 1_800
    assert shortened.reached_s == 1_802
    assert shortened.state_at(CaseInstant(1_800)) == OPENING
    assert shortened.state_at(CaseInstant(1_801)) == AFTER_ONE
    assert shortened.state_at(CaseInstant(1_802)) == AFTER_TWO
    assert shortened.compensation_at(CaseInstant(1_801)) == TERMS_AFTER_ONE
    assert shortened.compensation_at(CaseInstant(1_802)) == TERMS_AFTER_TWO

    with pytest.raises(SimulationConfigurationError, match="no state at 1803 s"):
        shortened.state_at(CaseInstant(1_803))


def test_a_record_cut_at_a_second_grows_apart_from_the_record_it_was_cut_from() -> None:
    record = _record_of_four(opened_at_s=1_800)

    shortened = record.through(CaseInstant(1_801))
    shortened.append(AFTER_THREE, TERMS_AFTER_THREE)

    assert shortened.state_at(CaseInstant(1_802)) == AFTER_THREE
    assert shortened.compensation_at(CaseInstant(1_802)) == TERMS_AFTER_THREE
    assert record.state_at(CaseInstant(1_802)) == AFTER_TWO
    assert record.compensation_at(CaseInstant(1_802)) == TERMS_AFTER_TWO
    assert record.reached_s == 1_803


def test_a_record_cut_at_its_first_or_last_second_holds_one_state_or_all_of_them() -> None:
    record = _record_of_four(opened_at_s=1_800)

    first = record.through(CaseInstant(1_800))
    whole = record.through(CaseInstant(1_803))

    assert first.reached_s == 1_800
    assert first.state_at(CaseInstant(1_800)) == OPENING
    assert first.compensation_at(CaseInstant(1_800)) == NO_TERMS
    assert whole.reached_s == 1_803
    assert whole.state_at(CaseInstant(1_803)) == AFTER_THREE
    assert whole.compensation_at(CaseInstant(1_803)) == TERMS_AFTER_THREE


@pytest.mark.parametrize("instant_s", [1_799, 1_804])
def test_a_record_is_not_cut_at_a_second_it_does_not_hold(instant_s: int) -> None:
    record = _record_of_four(opened_at_s=1_800)

    with pytest.raises(SimulationConfigurationError, match=f"no state at {instant_s} s"):
        record.through(CaseInstant(instant_s))

    with pytest.raises(TypeError, match="CaseInstant"):
        record.through(1_801)  # type: ignore[arg-type]


def test_a_record_opened_part_way_through_a_case_keeps_the_cases_seconds() -> None:
    """A record that opens after the case began keeps each second's number in the case."""

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
        StoredStates(OPENING, 0, NO_TERMS)  # type: ignore[arg-type]


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
        record.append(state, TERMS_AFTER_ONE)

    assert record.reached_s == 3
    assert record.state_at(CaseInstant(3)) == AFTER_THREE
    assert record.compensation_at(CaseInstant(3)) == TERMS_AFTER_THREE

    with pytest.raises(SimulationConfigurationError, match=names):
        StoredStates(state, CaseInstant(0), NO_TERMS)


def test_restarting_a_record_discards_every_state_it_held() -> None:
    record = _record_of_four(opened_at_s=600)

    record.restart_from(AFTER_TWO, CaseInstant(0), TERMS_AFTER_TWO)

    assert record.opened_at_s == 0
    assert record.reached_s == 0
    assert record.state_at(CaseInstant(0)) == AFTER_TWO
    assert record.compensation_at(CaseInstant(0)) == TERMS_AFTER_TWO

    with pytest.raises(SimulationConfigurationError, match="no state at 600 s"):
        record.state_at(CaseInstant(600))


def test_a_refused_restart_leaves_the_record_as_it_was() -> None:
    record = _record_of_four(opened_at_s=600)
    not_a_state = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0)

    with pytest.raises(SimulationConfigurationError):
        record.restart_from(not_a_state, CaseInstant(0), NO_TERMS)

    assert record.opened_at_s == 600
    assert record.state_at(CaseInstant(603)) == AFTER_THREE
    assert record.compensation_at(CaseInstant(603)) == TERMS_AFTER_THREE


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
    assert record_copy.compensation_at(CaseInstant(1_801)) == TERMS_AFTER_ONE
    assert record_copy.compensation_at(CaseInstant(1_803)) == TERMS_AFTER_THREE

    record_copy.append(AFTER_ONE, TERMS_AFTER_ONE)

    assert record_copy.reached_s == 1_804
    assert record.reached_s == 1_803


def test_each_fraction_is_returned_as_a_series_in_order_of_time() -> None:
    record = _record_of_four(opened_at_s=1_800)

    series = record.fraction_series(CaseInstant(1_800), CaseInstant(1_803))

    # One series for each of the six fractions, and none for the two amounts
    # or the constant one.
    assert [list(values) for values in series] == [
        [0.0, 0.011, 0.012, 0.013],
        [0.0, 0.0052, 0.0061, 0.0068],
        [0.0, 0.0007, 0.0009, 0.0011],
        [0.0, 0.0013, 0.0016, 0.0019],
        [0.0, 3.1e-05, 4.2e-05, 5.5e-05],
        [0.0, 1.7e-06, 2.3e-06, 3.1e-06],
    ]


def test_a_series_can_cover_part_of_the_record_or_one_second() -> None:
    record = _record_of_four(opened_at_s=1_800)

    inner = record.fraction_series(CaseInstant(1_801), CaseInstant(1_802))
    last = record.fraction_series(CaseInstant(1_803), CaseInstant(1_803))

    assert list(inner[1]) == [0.0052, 0.0061]
    assert list(inner[5]) == [1.7e-06, 2.3e-06]
    assert [list(values) for values in last] == [
        [0.013],
        [0.0068],
        [0.0011],
        [0.0019],
        [5.5e-05],
        [3.1e-06],
    ]


def test_changing_a_returned_series_does_not_change_the_record() -> None:
    record = _record_of_four(opened_at_s=0)
    series = record.fraction_series(CaseInstant(0), CaseInstant(3))

    series[0][1] = 0.5

    assert record.state_at(CaseInstant(1)) == AFTER_ONE


@pytest.mark.parametrize(
    ("first_s", "last_s", "names"),
    [
        (1_802, 1_801, "from 1802 s to 1801 s ends before it begins"),
        (1_799, 1_803, "from 1799 s to 1803 s"),
        (1_800, 1_804, "from 1800 s to 1804 s"),
    ],
)
def test_a_series_the_record_cannot_give_is_refused_and_named(
    first_s: int, last_s: int, names: str
) -> None:
    record = _record_of_four(opened_at_s=1_800)

    with pytest.raises(SimulationConfigurationError, match=names):
        record.fraction_series(CaseInstant(first_s), CaseInstant(last_s))


def test_a_series_refuses_an_instant_of_the_wrong_type() -> None:
    record = _record_of_four(opened_at_s=0)

    with pytest.raises(TypeError, match="CaseInstant"):
        record.fraction_series(0, CaseInstant(3))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="CaseInstant"):
        record.fraction_series(CaseInstant(0), 3)  # type: ignore[arg-type]
