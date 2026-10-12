"""The compartment selection the dashboard owns, held without a toolkit.

`app/compartment_selection.py` holds which compartments the chart draws as a
value rather than as the state of the legend's boxes (`PL-VN6M`). Two
properties carry the safety argument, and both are held here: no selection
over the cap can be built, so the boxes and the curves drawn from one
selection cannot disagree; and a reader's click is honoured, with the
longest-standing compartment making room for it. The second is checked
against every selection a reader can reach, not a handful of examples.
"""

import subprocess
import sys
from collections import deque
from dataclasses import FrozenInstanceError
from functools import cache
from itertools import combinations, permutations

import pytest

from anesthesia_sim.app.chart_frame import COMPARED_COMPARTMENT_CAP, compared_compartments
from anesthesia_sim.app.compartment_selection import (
    INITIAL_COMPARTMENT_SELECTION,
    CompartmentSelection,
)
from anesthesia_sim.app.dashboard_frame import MAX_DISPLAYED_RUNS
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity

CIRCUIT = RecordedQuantity.CIRCUIT
ALVEOLAR = RecordedQuantity.ALVEOLAR
MUSCLE = RecordedQuantity.MUSCLE
FAT = RecordedQuantity.FAT


@cache
def _reachable() -> frozenset[CompartmentSelection]:
    """Every selection a reader can reach by clicking, on one run and on two.

    Walked breadth first from the selection the dashboard opens with, and from
    the selection a second run reduces it to, over every click a legend can
    send: each compartment, shown or hidden.
    """

    starts = (INITIAL_COMPARTMENT_SELECTION, INITIAL_COMPARTMENT_SELECTION.with_run_count(2))
    seen = set(starts)
    queue = deque(starts)

    while queue:
        selection = queue.popleft()

        for quantity in COMPARTMENT_QUANTITIES:
            for shown in (True, False):
                after = selection.with_compartment(quantity, shown)

                if after not in seen:
                    seen.add(after)
                    queue.append(after)

    return frozenset(seen)


# ------------------------------------------------------------- what it holds


def test_the_dashboard_opens_on_every_compartment_on_one_run() -> None:
    """What a reader who has chosen nothing sees: all six, in table order."""

    assert INITIAL_COMPARTMENT_SELECTION.order == COMPARTMENT_QUANTITIES
    assert INITIAL_COMPARTMENT_SELECTION.run_count == 1
    assert INITIAL_COMPARTMENT_SELECTION.shown == COMPARTMENT_QUANTITIES


def test_what_is_shown_is_in_table_order_whatever_order_it_was_asked_for_in() -> None:
    """The order is the click rule's; the drawn order is the table's, as the chart draws it."""

    selection = CompartmentSelection((FAT, CIRCUIT, MUSCLE), 1)

    assert selection.order == (FAT, CIRCUIT, MUSCLE)
    assert selection.shown == (CIRCUIT, MUSCLE, FAT)


def test_every_selection_a_reader_can_reach_is_exactly_what_the_chart_draws() -> None:
    """The property the legend's agreement with the plot rests on.

    `assemble_chart_frame` draws `compared_compartments` of the selection it
    is handed, and the legend checks `shown`. For every reachable selection
    the two are the same compartments and nothing is left undrawn, so a box
    checked in the legend is a curve on the plot.
    """

    reachable = _reachable()

    # Every ordering of every subset on one run, and every ordering of every
    # subset of at most the cap on two: the walk reaches the whole space.
    assert len(reachable) == sum(
        len(list(permutations(COMPARTMENT_QUANTITIES, size)))
        for size in range(len(COMPARTMENT_QUANTITIES) + 1)
    ) + sum(
        len(list(permutations(COMPARTMENT_QUANTITIES, size)))
        for size in range(COMPARED_COMPARTMENT_CAP + 1)
    )

    for selection in reachable:
        assert compared_compartments(selection.order, selection.run_count) == (selection.shown, 0)
        assert set(selection.shown) == set(selection.order)


def test_a_selection_cannot_be_changed_in_place() -> None:
    """The legend keeps the selection it was last shown, which must stay the owner's value."""

    with pytest.raises(FrozenInstanceError):
        INITIAL_COMPARTMENT_SELECTION.order = ()  # type: ignore[misc]


# ------------------------------------------------------------ a reader's click


def test_every_click_from_every_reachable_selection_follows_the_rule() -> None:
    """Hide removes; show adds as the newest; over the cap, the oldest makes room.

    Checked against an oracle that counts against `COMPARED_COMPARTMENT_CAP`
    directly, rather than through `compared_compartments` as the module does,
    so the two routes to the cap are held to one answer.
    """

    for selection in _reachable():
        for quantity in COMPARTMENT_QUANTITIES:
            for shown in (True, False):
                after = selection.with_compartment(quantity, shown)

                if shown == (quantity in selection.order):
                    expected = selection.order
                elif not shown:
                    expected = tuple(held for held in selection.order if held is not quantity)
                else:
                    expected = (*selection.order, quantity)

                    if selection.run_count > 1:
                        expected = expected[-COMPARED_COMPARTMENT_CAP:]

                assert after.order == expected
                assert after.run_count == selection.run_count
                # The compartment asked for is the one the reader gets.
                assert (quantity in after.shown) is shown


def test_a_check_over_the_cap_drops_the_longest_standing_compartment() -> None:
    """A cap that refused the click would leave a reader pressing a box that does not respond."""

    selection = INITIAL_COMPARTMENT_SELECTION.with_run_count(2)

    assert selection.order == (CIRCUIT, ALVEOLAR)

    selection = selection.with_compartment(FAT, True)

    assert selection.order == (ALVEOLAR, FAT)
    assert selection.shown == (ALVEOLAR, FAT)

    selection = selection.with_compartment(MUSCLE, True)

    assert selection.order == (FAT, MUSCLE)
    assert selection.shown == (MUSCLE, FAT)


def test_a_click_for_the_state_already_held_changes_nothing() -> None:
    """Showing a shown compartment does not renew its place, so it is not saved from the cap."""

    selection = CompartmentSelection((CIRCUIT, ALVEOLAR), 2)

    assert selection.with_compartment(CIRCUIT, True) is selection
    assert selection.with_compartment(FAT, False) is selection

    # CIRCUIT is still the longest-standing, so it is the one a third check drops.
    assert selection.with_compartment(FAT, True).order == (ALVEOLAR, FAT)


def test_one_run_takes_every_check_and_drops_nothing() -> None:
    """The cap binds only once a second run spends the width channel."""

    selection = CompartmentSelection((), 1)

    for quantity in reversed(COMPARTMENT_QUANTITIES):
        selection = selection.with_compartment(quantity, True)

    assert selection.order == tuple(reversed(COMPARTMENT_QUANTITIES))
    assert selection.shown == COMPARTMENT_QUANTITIES


def test_a_reader_may_hide_every_compartment() -> None:
    """An empty selection is a state the dashboard says so about, not one it refuses."""

    selection = INITIAL_COMPARTMENT_SELECTION

    for quantity in COMPARTMENT_QUANTITIES:
        selection = selection.with_compartment(quantity, False)

    assert selection.order == ()
    assert selection.shown == ()


# ---------------------------------------------------------- the run count


def test_a_second_run_keeps_exactly_what_the_chart_would_draw() -> None:
    """The top of the compartment table: `compared_compartments`' rule, not a pair chosen here."""

    reduced = INITIAL_COMPARTMENT_SELECTION.with_run_count(2)

    assert reduced.run_count == 2
    assert reduced.order == (CIRCUIT, ALVEOLAR)
    assert reduced.shown == compared_compartments(COMPARTMENT_QUANTITIES, 2)[0]


def test_the_run_count_keeps_the_click_order_of_what_it_keeps() -> None:
    """What survives the cap keeps its standing, so the next check over it drops the right one."""

    selection = CompartmentSelection((FAT, MUSCLE, CIRCUIT), 1).with_run_count(2)

    # The table's top two of the three, kept in the order they were asked for.
    assert selection.order == (MUSCLE, CIRCUIT)
    assert selection.with_compartment(ALVEOLAR, True).order == (CIRCUIT, ALVEOLAR)


def test_every_selection_on_one_run_reduces_to_what_the_chart_draws_for_two() -> None:
    """Whatever the reader had chosen, the second run's boxes are the second run's curves."""

    for size in range(len(COMPARTMENT_QUANTITIES) + 1):
        for chosen in combinations(COMPARTMENT_QUANTITIES, size):
            reduced = CompartmentSelection(chosen, 1).with_run_count(2)

            assert reduced.shown == compared_compartments(chosen, 2)[0]


def test_back_to_one_run_a_reduced_selection_stays_reduced() -> None:
    """Nothing remembers what the cap took off, as nothing did while the legend held it."""

    reduced = INITIAL_COMPARTMENT_SELECTION.with_run_count(2)
    restored = reduced.with_run_count(1)

    assert restored.run_count == 1
    assert restored.order == (CIRCUIT, ALVEOLAR)


def test_the_same_run_count_keeps_the_same_selection() -> None:
    """Told the run count it already has, the selection loses nothing and reorders nothing."""

    selection = CompartmentSelection((FAT, CIRCUIT), 2)

    assert selection.with_run_count(2) == selection


# ---------------------------------------------------------------- refusals


def test_a_selection_over_the_cap_is_refused() -> None:
    """The one state in which the boxes would name a curve the plot is not drawing."""

    with pytest.raises(ValueError, match="would leave 1 off the plot"):
        CompartmentSelection((CIRCUIT, ALVEOLAR, FAT), 2)

    with pytest.raises(ValueError, match=f"cap of {COMPARED_COMPARTMENT_CAP}"):
        CompartmentSelection(COMPARTMENT_QUANTITIES, 2)


@pytest.mark.parametrize("order", [[CIRCUIT], {CIRCUIT}, CIRCUIT, None])
def test_an_order_that_is_not_a_tuple_is_refused(order: object) -> None:
    with pytest.raises(TypeError, match="order is a tuple"):
        CompartmentSelection(order, 1)  # type: ignore[arg-type]


@pytest.mark.parametrize("member", ["circuit", None, 0])
def test_a_member_that_is_not_a_recorded_quantity_is_refused(member: object) -> None:
    """A bare string spelling a member compares equal to it, so it is refused by type first."""

    with pytest.raises(TypeError, match="RecordedQuantity members"):
        CompartmentSelection((member,), 1)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="RecordedQuantity members"):
        INITIAL_COMPARTMENT_SELECTION.with_compartment(member, True)  # type: ignore[arg-type]


def test_the_wash_in_ratio_is_refused_as_not_a_compartment() -> None:
    """A quotient of two compartments has no trace and no box."""

    with pytest.raises(ValueError, match="wash_in_ratio is not a compartment"):
        CompartmentSelection((RecordedQuantity.WASH_IN_RATIO,), 1)

    with pytest.raises(ValueError, match="wash_in_ratio is not a compartment"):
        INITIAL_COMPARTMENT_SELECTION.with_compartment(RecordedQuantity.WASH_IN_RATIO, False)


def test_a_compartment_named_twice_is_refused_and_named() -> None:
    with pytest.raises(ValueError, match="names fat more than once"):
        CompartmentSelection((FAT, CIRCUIT, FAT), 1)


@pytest.mark.parametrize("run_count", [True, 1.0, "1", None])
def test_a_run_count_that_is_not_an_int_is_refused(run_count: object) -> None:
    """A `bool` is an `int` to Python, and would make `True` one run."""

    with pytest.raises(TypeError, match="a run count is an int"):
        CompartmentSelection((), run_count)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a run count is an int"):
        INITIAL_COMPARTMENT_SELECTION.with_run_count(run_count)  # type: ignore[arg-type]


@pytest.mark.parametrize("run_count", [0, -1, MAX_DISPLAYED_RUNS + 1])
def test_a_run_count_the_dashboard_cannot_draw_is_refused(run_count: int) -> None:
    with pytest.raises(ValueError, match=f"1 to {MAX_DISPLAYED_RUNS} runs"):
        CompartmentSelection((), run_count)

    with pytest.raises(ValueError, match=f"1 to {MAX_DISPLAYED_RUNS} runs"):
        INITIAL_COMPARTMENT_SELECTION.with_run_count(run_count)


def test_importing_the_selection_loads_no_toolkit() -> None:
    """The selection is a value the dashboard holds, so it loads no widget library.

    Asserted of everything the module reaches when it is imported, in a fresh
    interpreter, since this test process may already hold Qt from another test.
    """

    probe = (
        "import sys\n"
        "import anesthesia_sim.app.compartment_selection\n"
        "loaded = sorted(name for name in sys.modules "
        "if name.split('.')[0] in {'PySide6', 'pyqtgraph', 'shiboken6'})\n"
        "print(loaded)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "[]"
