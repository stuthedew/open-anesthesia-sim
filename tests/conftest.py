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
`tests/reference/test_late_washout_against_published_fits.py`, and a
controller stepped onto the 24-hour limit in
`tests/integration/test_controller.py`. Each is computed once per run and
shared between workers through the `computed_once` fixture below (`PL-F08Y`,
`PL-ZWQS`). Where they ran was left to the scheduler,
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
computation runs on one runner and not on both. The other tests are dealt in
cycles, so each module is split between the parts, and `PART_SHARES` sets how
many of each cycle each part takes. The first part's job also
runs the linters, `mypy` and the floor section, which took about 95 s of a slow
runner's 621 s job on 2026-10-17. The tests that read a costly computation took
about 22% of the suite's time, so giving all of them to the second part was
expected to balance the two jobs. It did not at first. On the split's first
run, 2026-10-17, the second part's pytest step took 462 s and the first part's
whole job 299 s. With half the other tests, the second part's workers ran out
of work while one worker was still building the first controller run.
`worksteal` then handed them the rest of the controller tests, and each of
those workers built the runs again, because a module fixture lives in one
process. A local profile showed four builds where the dealing expects two. Now
the controller runs are shared through `computed_once` as the curves are, so a
worker handed a controller test waits for the run instead of building it
again (`PL-ZWQS`). `tools/main_ci_status.py`'s pytest line reads the parts'
sum, so compare the two jobs' pytest steps in a run's log.

**A pull request that changes only apparatus files skips the costly tests**
(`PL-STM6`). `--skip-costly` leaves out every test that reads a costly
computation, by the same `_costly_reads` that the parts and the dealing use.
`quality.yml` passes it to the second part when `bin/docket ci-scope` answers
`apparatus`, because no apparatus file is an input to those tests. With them
gone, `PART_SHARES` stays as it is: the first part's linters already make up
for most of the gap that leaving them out opens.

**The windows the tests leave open** (`PL-CW51`). Many tests build a dashboard
and never delete it, so a worker can end its run holding hundreds of windows.
The interpreter's exit then destroyed them in no particular order. Qt also
keeps parentless widgets of its own: each `QGraphicsLayoutStyleInfo`, which a
pyqtgraph plot's layout builds, holds one in a `unique_ptr` and deletes it with
the layout (https://github.com/qt/qtbase/blob/6.11/src/widgets/graphicsview/qgraphicslayoutstyleinfo.cpp).
Deleting such a widget before its plot makes the plot's layout delete it a
second time, which crashes the process. A drift job on CPython 3.15.0 printed
"pure virtual method called" as a worker exited, and a worker here on 3.15.0
died of a segmentation fault while the exit destroyed its windows. So
`pytest_sessionfinish` deletes the windows Python built while the application
still runs, and leaves Qt's own widgets to their owners, which delete them.
"""

from __future__ import annotations

import argparse
import os
import pickle
import sys
from collections.abc import Callable, Collection, Hashable, Sequence
from itertools import islice
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Protocol

import pytest

if TYPE_CHECKING:
    from xdist.workermanage import WorkerController

try:
    import fcntl
except ImportError:  # Windows, where `computed_once` shares nothing between workers
    fcntl = None

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


#: How many of each cycle of ordinary tests each part takes, by the number of
#: parts. The first part's job also runs about 115 s of linters and tree checks
#: outside pytest. With an even split it finished last on both of `PL-ZWQS`'s
#: measured runs, by 17 s and by 116 s. So of every 5 ordinary tests it takes 2.
#: Retune this when the two jobs drift apart. A split not named here is even.
PART_SHARES: dict[int, tuple[int, ...]] = {2: (2, 3)}


def part[Test: Hashable](
    tests: Sequence[Test],
    costly: Collection[Test],
    index: int,
    parts: int,
    shares: Sequence[int] | None = None,
) -> list[Test]:
    """The tests that part `index` of `parts` runs, in their order in `tests`.

    Parts are numbered from 1. Every test in `costly` runs in the last part.
    The other tests are dealt in repeating cycles. In each cycle, part 1 takes
    the first `shares[0]` tests, part 2 the next `shares[1]`, and so on. With
    no `shares`, each part takes one test per cycle, which is round robin.
    Every test runs in exactly one part.
    """

    shares = (1,) * parts if shares is None else tuple(shares)
    if len(shares) != parts or any(share < 1 for share in shares):
        raise ValueError(f"{parts} parts need {parts} shares of at least 1 each, not {shares}")
    owner = [k for k, share in enumerate(shares, start=1) for _ in range(share)]

    chosen: list[Test] = []
    dealt = 0
    for test in tests:
        if test in costly:
            if index == parts:
                chosen.append(test)
            continue
        if owner[dealt % len(owner)] == index:
            chosen.append(test)
        dealt += 1
    return chosen


def selected[Test: Hashable](
    tests: Sequence[Test],
    costly: Collection[Test],
    chosen: tuple[int, int] | None,
    *,
    skip_costly: bool,
) -> list[Test]:
    """The tests a run keeps, in their order in `tests`.

    With `skip_costly`, every test in `costly` is left out. With `chosen`, a
    `(K, N)` pair from `--part`, `part` then picks part K of N from the rest,
    with the shares `PART_SHARES` names for N parts.
    """

    kept = [test for test in tests if test not in costly] if skip_costly else list(tests)
    if chosen is None:
        return kept
    return part(kept, costly, *chosen, PART_SHARES.get(chosen[1]))


def _part(text: str) -> tuple[int, int]:
    """Parse `--part K/N` into (K, N), refusing a K outside 1 to N."""

    index, _, parts = text.partition("/")
    if not (index.isdigit() and parts.isdigit() and 1 <= int(index) <= int(parts)):
        raise argparse.ArgumentTypeError(
            f"{text!r} is not K/N with 1 <= K <= N, such as 1/2 for the first of two parts"
        )
    return int(index), int(parts)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add `--part K/N` and `--skip-costly`, the two ways CI narrows a run of the suite."""

    parser.addoption(
        "--part",
        type=_part,
        metavar="K/N",
        help="run only part K of N, as each of quality.yml's two pytest jobs does",
    )
    parser.addoption(
        "--skip-costly",
        action="store_true",
        help="leave out every test that reads a costly computation, as quality.yml does on a "
        "pull request that changes only apparatus files",
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


def computed_once_in[Value](store: Path, name: str, compute: Callable[[], Value]) -> Value:
    """`compute()`, run by the first process to ask for `name` and read from `store` by the rest.

    The first process to ask takes a lock on `name`, runs `compute()` and
    publishes the pickled result in `store`. A process that asks meanwhile
    waits on the lock and then reads what was published. The result is written
    whole and then renamed into place. The lock is `flock`, which the kernel
    releases if the process holding it dies. So a crash leaves the next process
    to run `compute()`, rather than to read half a result or to wait for ever.
    """

    published = store / f"{name}.pickle"
    with (store / f"{name}.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if published.exists():
            value: Value = pickle.loads(published.read_bytes())
            return value
        value = compute()
        partial = store / f"{name}.partial"
        partial.write_bytes(pickle.dumps(value))
        partial.replace(published)
        return value


@pytest.fixture(scope="session")
def computed_once(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Callable[[str, Callable[[], object]], object]:
    """Run a costly computation once per pytest run, however many xdist workers read it.

    A test calls it with a name that is unique in the run and a function that
    computes the value. Each worker then gets its own unpickled copy, as it
    would from a module fixture built in that worker. This is what shares the
    24-hour washout curves (`PL-F08Y`) and the two controller runs stepped
    onto the 24-hour limit (`PL-ZWQS`). Sending each computation's tests to
    one worker with `--dist loadgroup` would compute each once too. It was
    measured for the curves and set aside: it slowed the rest of the suite by
    8 to 11 s, and the whole run by 19 s against this (`PL-F08Y` has the
    figures).

    The store is a directory in the run's own base temporary directory, the
    parent of each worker's. Pytest makes that directory afresh for every run
    and empties it when one is named with `--basetemp`. So a value published
    there cannot be served to a later run built from different source, which
    is the hazard `PL-0MLZ` closed for bytecode. For the same reason, whether
    to share turns on `workerinput`, which xdist sets on a worker's own
    configuration, and not on `PYTEST_XDIST_WORKER`, which a pytest started
    inside a worker would inherit: that run's base directory's parent outlives
    it. Without xdist one process runs every test, so `compute()` runs once
    anyway. Windows has no `fcntl`, so there each worker computes what it
    needs.
    """

    if fcntl is None or not hasattr(request.config, "workerinput"):
        return lambda _name, compute: compute()

    store = tmp_path_factory.getbasetemp().parent / "computed-once"
    store.mkdir(exist_ok=True)
    return lambda name, compute: computed_once_in(store, name, compute)


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node: WorkerController) -> None:
    """Record the controller's `--dist` mode where a worker can read it."""

    node.workerinput["dist"] = node.config.getoption("dist")


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Keep the tests that `--skip-costly` and `--part` select, then deal the costly ones.

    `--skip-costly` leaves out every test that reads a costly computation, and
    `--part` then picks one part of what is left. Each costly computation that
    remains is dealt to the head of a worker's first slice.

    `trylast`, so that the order dealt is the one every other hook has finished
    with. Every worker runs this on the same collection and gets the same
    answer, which xdist requires of a collection before it schedules any; the
    costs are summed in table order, never a set's, so no worker's hash seed
    can round them differently. The part is chosen before the dealing, so the
    dealing places only the units this part runs.
    """

    chosen = config.getoption("part")
    skip_costly = config.getoption("skip_costly")
    if chosen is not None or skip_costly:
        reads, groups = _costly_reads(items)
        costly = set(reads).union(*groups.values())
        kept = selected(items, costly, chosen, skip_costly=skip_costly)
        kept_set = set(kept)
        config.hook.pytest_deselected(items=[item for item in items if item not in kept_set])
        items[:] = kept

    workerinput = getattr(config, "workerinput", None)
    if workerinput is None or workerinput.get("dist") != "worksteal":
        return

    items[:] = deal(items, _units(items), workerinput["workercount"])


def windows_built(windows: Sequence[Any]) -> list[Any]:
    """The parentless windows among `windows` that Python built, in their order.

    A window Qt built for its own use is left out, because its owner deletes it
    and a second deletion crashes the process (`PL-CW51`).
    """

    import shiboken6

    return [
        window
        for window in windows
        if window.parent() is None and shiboken6.createdByPython(window)
    ]


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Delete the windows the tests built, while the application still runs (`PL-CW51`).

    A run that never started a `QApplication` is left alone, and nothing from
    Qt is imported for it.
    """

    widgets = sys.modules.get("PySide6.QtWidgets")
    if widgets is None or widgets.QApplication.instance() is None:
        return

    from PySide6.QtCore import QCoreApplication, QEvent

    for window in windows_built(widgets.QApplication.topLevelWidgets()):
        window.deleteLater()

    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
