"""Settings every test tree needs before any test module is imported, and the order xdist deals.

`QT_QPA_PLATFORM`: unset, Qt picks `xcb` on Linux and `QApplication` aborts
the process when no display is attached - which is every CI runner and every
web-container session. `offscreen` is the platform plugin the Qt build's
tests render under, so it is set here, before any `PySide6` import, rather
than on the pytest command line: `tools/doc_check.py`'s `check_coverage_gate`
holds the `Makefile`'s pytest line and `quality.yml`'s to string equality, once
it has put the threshold back into each of CI's two parts, and
an environment prefix on either would break that comparison for a reason
unrelated to coverage (`PL-YCWZ`'s pre-port survey, 2026-09-14).

`setdefault`, not assignment: a developer running the suite on a desktop with
a display may set the variable themselves to watch a test render, and nothing
here should override that.

**The order `--dist worksteal` deals** (`PL-4Z5Y`, `PL-K5VM`). A few tests
compute something that takes about a sixth of the run: a 24-hour washout curve in
`tests/reference/test_late_washout_against_published_fits.py`, computed once
per run and shared between workers through its `washout_curve` fixture
(`PL-F08Y`), and a controller stepped onto the 24-hour limit in
`tests/integration/test_controller.py`, a module fixture built again in every
worker that runs a test reading it. Where they ran was left to the scheduler,
and `worksteal` deals the collection out in contiguous slices at the start and
steals only from the tail of a queue as other queues run dry. So every curve
began in the last third of the run, and a slow CI runner waited about 70 s for
them after every other test had finished; and the six tests reading the two
controller runs were split between two to four workers, each building the runs
again.

So `pytest_collection_modifyitems` moves each unit of that work to the head of
a worker's first slice: the first test to read each curve, and the six
controller tests as one group, back to back, since one of them reads both runs
and pytest keeps a module fixture alive only across consecutive tests from its
module. A module names its units in a table, with what each costs in simulated
minutes - `CURVES_READ` for the curves each test reads, `MODULE_FIXTURE_MINUTES`
for its costly module fixtures - and `deal` places them heaviest first, each
in the slice with the least placed in it so far: longest processing time
first (Graham RL, "Bounds on multiprocessing timing anomalies", SIAM J Appl
Math 1969;17(2):416-429, https://doi.org/10.1137/0117039). Every worker then
starts the run on one or two curves or on the two controller runs, computed in
its own process where coverage measures them, and every other test reading them
finds them built. The units' tests run apart from the rest of their modules,
which share nothing else between tests.

It mirrors how pytest-xdist 3.8.0 deals the first slices
(`WorkStealingScheduling.check_schedule`, `xdist/scheduler/worksteal.py`), an
internal, so `tests/unit/test_worksteal_dealing.py` holds the mirror to the
installed scheduler. If the two part, the units start wherever they land, which
costs speed and nothing else. Without xdist, or under another `--dist` mode,
the order is left alone. A worker cannot read the mode from its own option,
which pytest-xdist's `setup_config` sets to `no`, so `pytest_configure_node`
records the controller's mode in each worker's `workerinput`. That hook runs on
the controller, which collects nothing and so never loads a conftest below this
one; the dealing sits beside it because it deals two test trees.

**The parts CI runs the suite in** (`PL-T9X9`). `quality.yml` runs the suite
in two jobs, each on its own runner, and `--part K/N` picks the tests one job
runs. Every test that reads a costly computation runs in the last part, so each
computation runs on one runner and not on both. The other tests are dealt round
robin, so each module is split between the parts. The first part's job also
runs the linters, `mypy` and the floor section, which took about 95 s of a slow
runner's 621 s job on 2026-10-17. The 46 tests that read a costly computation
took about 22% of the suite's time, about 110 s of that runner's 506 s. So
giving all of them to the second part balances the two jobs to within about
20 s. If the parts drift apart, `tools/main_ci_status.py`'s pytest line still
reads their sum, so compare the two jobs' pytest steps in a run's log.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Collection, Hashable, Sequence
from itertools import islice
from types import ModuleType
from typing import TYPE_CHECKING, Protocol

import pytest

if TYPE_CHECKING:
    from xdist.workermanage import WorkerController

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class _CurveRead(Protocol):
    """One curve a washout test reads, as its module's `CURVES_READ` names it."""

    @property
    def elimination_duration_min(self) -> float: ...


def first_slice_sizes(tests: int, workers: int) -> list[int]:
    """The slices `--dist worksteal` deals the collection out in, in order.

    `check_schedule` hands the i-th of n idle workers `len(pending) // (n - i)`
    of what is left, from the front, so the slices are contiguous and differ
    in size by one at most.
    """

    sizes: list[int] = []
    for worker in range(workers):
        sizes.append((tests - sum(sizes)) // (workers - worker))
    return sizes


def deal[Test: Hashable](
    tests: Sequence[Test], units: Sequence[tuple[Sequence[Test], float]], workers: int
) -> list[Test]:
    """`tests` reordered so each unit runs back to back at the head of a worker's first slice.

    A unit is the tests that share one costly computation, with what it costs.
    Heaviest first, each goes to the slice with the least placed in it so far,
    so a slice holding one heavy unit takes no other until every slice holds as
    much. The tests in no unit keep their order and fill each slice behind its
    head. Where a slice's units would not fit in it, `tests` comes back as it
    is, since dealing them would run them into the next slice.
    """

    load = [0.0] * workers
    heads: list[list[Test]] = [[] for _ in range(workers)]
    for members, cost in sorted(units, key=lambda unit: -unit[1]):
        lightest = load.index(min(load))
        heads[lightest].extend(members)
        load[lightest] += cost

    sizes = first_slice_sizes(len(tests), workers)
    if any(len(head) > size for head, size in zip(heads, sizes, strict=True)):
        return list(tests)
    placed = {test for head in heads for test in head}
    rest = iter([test for test in tests if test not in placed])
    dealt = [
        test
        for head, size in zip(heads, sizes, strict=True)
        for test in (*head, *islice(rest, size - len(head)))
    ]
    if len(dealt) != len(tests) or set(dealt) != set(tests):
        raise RuntimeError(
            f"dealing the costly tests first turned {len(tests)} tests into {len(dealt)}, "
            f"{len(set(dealt))} of them distinct, which would skip or repeat a test"
        )
    return dealt


def part[Test: Hashable](
    tests: Sequence[Test], costly: Collection[Test], index: int, parts: int
) -> list[Test]:
    """The tests that part `index` of `parts` runs, in their order in `tests`.

    Parts are numbered from 1. Every test in `costly` runs in the last part.
    The other tests are dealt round robin, so the i-th of them, counting from
    0, runs in part i mod `parts` + 1. Every test runs in exactly one part.
    """

    chosen: list[Test] = []
    dealt = 0
    for test in tests:
        if test in costly:
            if index == parts:
                chosen.append(test)
            continue
        if dealt % parts == index - 1:
            chosen.append(test)
        dealt += 1
    return chosen


def _part(text: str) -> tuple[int, int]:
    """Parse `--part K/N` into (K, N), refusing a K outside 1 to N."""

    index, _, parts = text.partition("/")
    if not (index.isdigit() and parts.isdigit() and 1 <= int(index) <= int(parts)):
        raise argparse.ArgumentTypeError(
            f"{text!r} is not K/N with 1 <= K <= N, such as 1/2 for the first of two parts"
        )
    return int(index), int(parts)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add `--part K/N`, which runs one of the parts CI splits the suite into."""

    parser.addoption(
        "--part",
        type=_part,
        metavar="K/N",
        help="run only part K of N, as each of quality.yml's two pytest jobs does",
    )


def _costly_reads(
    items: Sequence[pytest.Item],
) -> tuple[dict[pytest.Function, tuple[_CurveRead, ...]], dict[ModuleType, list[pytest.Function]]]:
    """The tests that read a costly computation: each curve's readers, and each module's group."""

    reads: dict[pytest.Function, tuple[_CurveRead, ...]] = {}
    groups: dict[ModuleType, list[pytest.Function]] = {}
    for item in items:
        if not isinstance(item, pytest.Function):
            continue
        curves_read = getattr(item.module, "CURVES_READ", {})
        if item.function in curves_read:
            reads[item] = curves_read[item.function](**item.callspec.params)
        if getattr(item.module, "MODULE_FIXTURE_MINUTES", {}).keys() & set(item.fixturenames):
            groups.setdefault(item.module, []).append(item)
    return reads, groups


def _units(items: Sequence[pytest.Item]) -> list[tuple[tuple[pytest.Item, ...], float]]:
    """Each costly computation the collection's modules name, as the tests it is dealt with."""

    reads, groups = _costly_reads(items)

    # A test that reads the curve first opens it; failing one, the first to read it at all.
    openers: dict[_CurveRead, pytest.Function] = {}
    for item, curves in reads.items():
        openers.setdefault(curves[0], item)
    for item, curves in reads.items():
        for curve in curves:
            openers.setdefault(curve, item)
    opened: dict[pytest.Function, float] = {}
    for curve, item in openers.items():
        opened[item] = opened.get(item, 0.0) + curve.elimination_duration_min

    units: list[tuple[tuple[pytest.Item, ...], float]] = [
        ((item,), minutes) for item, minutes in opened.items()
    ]
    for module, members in groups.items():
        read = {name for member in members for name in member.fixturenames}
        minutes = sum(cost for name, cost in module.MODULE_FIXTURE_MINUTES.items() if name in read)
        units.append((tuple(members), minutes))
    return units


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node: WorkerController) -> None:
    """Record the controller's `--dist` mode where a worker can read it."""

    node.workerinput["dist"] = node.config.getoption("dist")


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Keep the part `--part` names, then deal each costly computation to a worker's first slice.

    `trylast`, so that the order dealt is the one every other hook has finished
    with. Every worker runs this on the same collection and gets the same
    answer, which xdist requires of a collection before it schedules any; the
    costs are summed in table order, never a set's, so no worker's hash seed
    can round them differently. The part is chosen before the dealing, so the
    dealing places only the units this part runs.
    """

    chosen = config.getoption("part")
    if chosen is not None:
        reads, groups = _costly_reads(items)
        costly = set(reads).union(*groups.values())
        kept = part(items, costly, *chosen)
        kept_set = set(kept)
        config.hook.pytest_deselected(items=[item for item in items if item not in kept_set])
        items[:] = kept

    workerinput = getattr(config, "workerinput", None)
    if workerinput is None or workerinput.get("dist") != "worksteal":
        return

    items[:] = deal(items, _units(items), workerinput["workercount"])
