"""`tests/conftest.py`'s dealing of the costly tests, its copy of worksteal's, and its parts.

The conftest moves the tests sharing each costly computation to where it
predicts a worker's first slice begins (`PL-4Z5Y`, `PL-K5VM`). `deal` is held
here to what that move must keep, on plain values. The prediction copies
arithmetic out of pytest-xdist's scheduler, an internal, so it is held to the
installed scheduler too: a release that deals differently fails here, where
otherwise the only sign would be a slower run.

`part` picks the tests one of CI's two pytest jobs runs (`PL-T9X9`). A test it
dropped from every part would never run in CI, and the combined coverage gate
would notice only if that test was the one covering a line of `core/`. So the
parts are held here to running every test exactly once.

`computed_once_in` shares a costly computation between the workers
(`PL-F08Y`, `PL-ZWQS`). A worker that read a half-written result, or that
computed again what another had published, would fail or be slow only in CI,
so both are held here in one process.
"""

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import cast

import pytest
from xdist.scheduler.worksteal import WorkStealingScheduling
from xdist.workermanage import WorkerController

CONFTEST = Path(__file__).parents[1] / "conftest.py"


def _conftest() -> ModuleType:
    """The conftest loaded under a name of its own, since every conftest is `conftest`."""

    spec = importlib.util.spec_from_file_location("tests_conftest", CONFTEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DEALING = _conftest()


def _slices(dealt: list[int], workers: int) -> list[list[int]]:
    """`dealt` cut where worksteal will cut it into the workers' first slices."""

    slices: list[list[int]] = []
    for size in DEALING.first_slice_sizes(len(dealt), workers):
        start = sum(len(dealt_slice) for dealt_slice in slices)
        slices.append(dealt[start : start + size])
    return slices


def test_each_unit_runs_back_to_back_at_the_head_of_a_slice() -> None:
    units = [((5, 6, 7), 3.0), ((20,), 1.0), ((33, 2), 2.0)]

    slices = _slices(DEALING.deal(list(range(40)), units, 8), 8)

    heads = [tuple(dealt_slice[: len(members)]) for members, _ in units for dealt_slice in slices]
    assert all(members in heads for members, _ in units)


def test_dealing_keeps_every_test_once_and_the_rest_in_their_order() -> None:
    units = [((5, 6, 7), 3.0), ((20,), 1.0), ((33, 2), 2.0)]
    in_a_unit = {test for members, _ in units for test in members}

    dealt = DEALING.deal(list(range(40)), units, 8)

    assert sorted(dealt) == list(range(40))
    assert [test for test in dealt if test not in in_a_unit] == [
        test for test in range(40) if test not in in_a_unit
    ]


def test_the_trunks_sit_alone_at_the_head_of_their_slice() -> None:
    """The suite's own shape: six tests sharing two 24-hour runs, sixteen curve openers.

    The six cost two 24-hour runs, more than any one slice's share of the
    whole, so no curve joins them: the worker building the runs starts on
    nothing else.
    """

    trunks = (100, 101, 102, 103, 104, 105)
    curves = [((200 + index,), 1440.0) for index in range(8)]
    curves += [((300 + index,), 360.0) for index in range(8)]
    units = [*curves, (trunks, 2880.0)]

    slices = _slices(DEALING.deal(list(range(8265)), units, 8), 8)

    (theirs,) = [dealt_slice for dealt_slice in slices if dealt_slice[0] in trunks]
    in_a_unit = {test for members, _ in units for test in members}
    assert tuple(theirs[: len(trunks)]) == trunks
    assert not in_a_unit & set(theirs[len(trunks) :])


def test_units_longer_than_their_slice_leave_the_order_alone() -> None:
    assert DEALING.deal(list(range(16)), [((3, 4, 5), 1.0)], 8) == list(range(16))


def test_a_unit_naming_a_test_outside_the_collection_is_refused() -> None:
    with pytest.raises(RuntimeError, match="skip or repeat a test"):
        DEALING.deal(list(range(16)), [((99,), 1.0)], 8)


class _Worker:
    """What `WorkStealingScheduling` asks of a worker before any test has run."""

    shutting_down = False

    def __init__(self, index: int) -> None:
        self.gateway = SimpleNamespace(id=f"gw{index}")
        self.dealt: list[int] = []

    def send_runtest_some(self, indices: list[int]) -> None:
        self.dealt.extend(indices)


@pytest.mark.parametrize(("tests", "workers"), [(8265, 8), (40, 8), (17, 3), (16, 8)])
def test_the_predicted_slices_are_the_ones_worksteal_deals(tests: int, workers: int) -> None:
    config = cast(pytest.Config, SimpleNamespace(getvalue=lambda name: [f"{workers}*popen"]))
    scheduler = WorkStealingScheduling(config)
    nodes = [_Worker(index) for index in range(workers)]
    collection = [f"test_{index}" for index in range(tests)]
    for node in nodes:
        scheduler.add_node(cast(WorkerController, node))
    for node in nodes:
        scheduler.add_node_collection(cast(WorkerController, node), collection)
    scheduler.schedule()

    slices = sorted((node.dealt for node in nodes), key=lambda dealt: dealt[:1])
    assert [index for dealt in slices for index in dealt] == list(range(tests)), (
        "worksteal no longer deals the collection out in contiguous slices from the front"
    )
    assert [len(dealt) for dealt in slices] == DEALING.first_slice_sizes(tests, workers), (
        "worksteal's first slices are no longer the sizes tests/conftest.py predicts, "
        "so the costly tests no longer start at the head of a worker's slice"
    )


@pytest.mark.parametrize(
    ("parts", "shares"), [(1, None), (2, None), (3, None), (2, (2, 3)), (3, (1, 3, 2))]
)
def test_the_parts_run_every_test_exactly_once(parts: int, shares: tuple[int, ...] | None) -> None:
    tests = list(range(23))
    runs = [
        test
        for index in range(1, parts + 1)
        for test in DEALING.part(tests, {3, 4, 17}, index, parts, shares)
    ]
    assert sorted(runs) == tests


def test_each_part_takes_its_share_of_each_cycle_of_ordinary_tests() -> None:
    """With shares 2 and 3, part 1 takes the first 2 of each 5 ordinary tests."""

    tests = list(range(12))
    assert DEALING.part(tests, {0}, 1, 2, (2, 3)) == [1, 2, 6, 7, 11]
    assert DEALING.part(tests, {0}, 2, 2, (2, 3)) == [0, 3, 4, 5, 8, 9, 10]


@pytest.mark.parametrize("shares", [(2,), (2, 3, 1), (0, 3), (2, -1)])
def test_shares_that_do_not_name_one_positive_count_per_part_are_refused(
    shares: tuple[int, ...],
) -> None:
    with pytest.raises(ValueError, match="2 parts need 2 shares"):
        DEALING.part(list(range(5)), set(), 1, 2, shares)


def test_the_costly_tests_run_in_the_last_part_and_the_rest_alternate() -> None:
    tests = list(range(10))
    assert DEALING.part(tests, {0, 5}, 1, 2) == [1, 3, 6, 8]
    assert DEALING.part(tests, {0, 5}, 2, 2) == [0, 2, 4, 5, 7, 9]


def test_skipping_the_costly_tests_leaves_out_only_them() -> None:
    """`--skip-costly` drops the costly tests and keeps the rest in their order (`PL-STM6`)."""

    tests = list(range(10))
    assert DEALING.selected(tests, {0, 5}, None, skip_costly=True) == [1, 2, 3, 4, 6, 7, 8, 9]
    assert DEALING.selected(tests, {0, 5}, None, skip_costly=False) == tests


def test_skipping_the_costly_tests_leaves_the_parts_every_other_test_once() -> None:
    """With the costly tests left out, the two parts still run every ordinary test once."""

    tests = list(range(23))
    costly = {3, 4, 17}
    runs = [
        test
        for index in (1, 2)
        for test in DEALING.selected(tests, costly, (index, 2), skip_costly=True)
    ]
    assert sorted(runs) == [test for test in tests if test not in costly]


def test_part_1_unskipped_and_part_2_skipped_still_run_every_other_test_once() -> None:
    """The combination CI runs: only the second part passes `--skip-costly`.

    The first part sees the costly tests and the second does not. They still
    deal the ordinary tests alike, because `part` counts its cycle over the
    ordinary tests alone.
    """

    tests = list(range(23))
    costly = {3, 4, 17}
    runs = [
        *DEALING.selected(tests, costly, (1, 2), skip_costly=False),
        *DEALING.selected(tests, costly, (2, 2), skip_costly=True),
    ]
    assert sorted(runs) == [test for test in tests if test not in costly]


def test_without_skipping_a_part_is_the_one_part_deals() -> None:
    tests = list(range(12))
    shares = DEALING.PART_SHARES[2]
    for index in (1, 2):
        assert DEALING.selected(tests, {0}, (index, 2), skip_costly=False) == DEALING.part(
            tests, {0}, index, 2, shares
        )


def test_a_part_is_read_as_k_of_n() -> None:
    assert DEALING._part("2/2") == (2, 2)


@pytest.mark.parametrize("text", ["0/2", "3/2", "2", "1/0", "a/b", "-1/2", "1/2/3"])
def test_a_part_outside_1_to_n_is_refused(text: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="is not K/N"):
        DEALING._part(text)


@pytest.mark.skipif(DEALING.fcntl is None, reason="no fcntl, so computed_once shares nothing")
def test_a_computation_published_once_is_read_by_every_later_caller(tmp_path: Path) -> None:
    """The second caller gets the first caller's result and never runs its own computation."""

    def never() -> list[int]:
        raise AssertionError("computed again what was already published")

    first = DEALING.computed_once_in(tmp_path, "run", lambda: [1, 2, 3])
    second = DEALING.computed_once_in(tmp_path, "run", never)

    assert first == second == [1, 2, 3]
    assert second is not first
    assert sorted(path.name for path in tmp_path.iterdir()) == ["run.lock", "run.pickle"]


@pytest.mark.skipif(DEALING.fcntl is None, reason="no fcntl, so computed_once shares nothing")
def test_a_computation_that_fails_publishes_nothing_and_the_next_caller_computes(
    tmp_path: Path,
) -> None:
    """A failure leaves no result to read, so the next caller runs the computation itself."""

    def fails() -> int:
        raise RuntimeError("the run broke")

    with pytest.raises(RuntimeError, match="the run broke"):
        DEALING.computed_once_in(tmp_path, "run", fails)

    assert not (tmp_path / "run.pickle").exists()
    assert DEALING.computed_once_in(tmp_path, "run", lambda: 7) == 7
