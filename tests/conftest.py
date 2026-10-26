"""Settings every test tree needs before any test module is imported, and the order xdist deals.

`QT_QPA_PLATFORM` names Qt's platform plugin. When it is unset, Qt picks
`xcb` on Linux, and `QApplication` aborts the process when no display is
attached. No display is attached on any CI runner or in any web-container
session. The Qt build's tests render under the `offscreen` plugin. This
module sets that plugin here, before any `PySide6` import, rather than on the
pytest command line. The reason is `tools/doc_check.py`'s
`check_coverage_gate`. Once it has put the coverage threshold back into the
pytest line of each of CI's two parts, it requires the `Makefile`'s pytest
line and `quality.yml`'s to be equal as strings. An environment prefix on
either line would break that comparison for a reason unrelated to coverage
(`PL-YCWZ`'s pre-port survey, 2026-09-14).

The module uses `setdefault`, not assignment. A developer running the suite
on a desktop with a display may set the variable themselves to watch a test
render, and nothing here should override their choice.

**The order `--dist worksteal` deals** (`PL-4Z5Y`, `PL-K5VM`). A few tests
compute something that takes about a sixth of the run. One kind is a 24-hour
washout curve in `tests/reference/test_late_washout_against_published_fits.py`.
The other is a controller stepped onto the 24-hour limit in
`tests/integration/test_controller.py`. Each is computed once per run and
shared between workers through the `computed_once` fixture below (`PL-F08Y`,
`PL-ZWQS`). Before this dealing, the scheduler decided where these tests ran.
At the start of a run, `worksteal` deals the collection out in contiguous
slices. After that, it steals only from the tail of a queue, as other queues
run dry. So every curve began in the last third of the run, and a slow CI
runner waited about 70 s for the curves after every other test had finished.
The six tests that read the two controller runs were split between two to
four workers, and each of those workers built the runs again.

So `pytest_collection_modifyitems` moves each unit of that work to the head of
a worker's first slice. A unit is either the first test to read a curve, or
the six controller tests as one group. The six run back to back, because one
of them reads both runs, and pytest keeps a module fixture alive only across
consecutive tests from its module. A module names its units in a table, with
what each unit costs in simulated minutes. `CURVES_READ` names the curves each
test reads, and `MODULE_FIXTURE_MINUTES` names the module's costly fixtures.
`deal` places the units heaviest first, each in the slice with the least cost
placed in it so far. This is the longest-processing-time-first rule (Graham RL,
"Bounds on multiprocessing timing anomalies", SIAM J Appl Math
1969;17(2):416-429, https://doi.org/10.1137/0117039). Every worker then starts
the run on one or two curves, or on the two controller runs. It computes them
in its own process, where coverage measures them, and every other test that
reads them finds them already built. The units' tests run apart from the rest
of their modules. That is safe because those modules share nothing else
between tests.

The dealing copies how pytest-xdist 3.8.0 deals the first slices
(`WorkStealingScheduling.check_schedule`, `xdist/scheduler/worksteal.py`).
That code is internal to xdist, so `tests/unit/test_worksteal_dealing.py`
checks that the copy still matches the installed scheduler. If the two drift
apart, the units start wherever they land, which costs speed and nothing
else. Without xdist, or under another `--dist` mode, the order is left alone.
A worker cannot read the mode from its own option, because pytest-xdist's
`setup_config` sets that option to `no`. So `pytest_configure_node` records
the controller's mode in each worker's `workerinput`. That hook runs on the
controller. The controller collects no tests, so it never loads a conftest
below this one. The dealing lives in this conftest, beside that hook, because
it deals tests from two test trees.

**The parts CI runs the suite in** (`PL-T9X9`). `quality.yml` runs the suite
in two jobs, each on its own runner, and `--part K/N` picks the tests one job
runs. Every test that reads a costly computation runs in the last part, so each
computation runs on one runner and not on both. The other tests are dealt in
cycles, so each module is split between the parts, and `PART_SHARES` sets how
many tests of each cycle each part takes. The first part's job also runs the
linters, `mypy` and the floor section, which runs the apparatus tools under the
oldest supported Python with no virtualenv. On 2026-10-17 these took about
95 s of a slow runner's 621 s job. The tests that read a costly computation took
about 22% of the suite's time, so giving all of them to the second part was
expected to balance the two jobs. It did not at first. On the split's first
run, 2026-10-17, the second part's pytest step took 462 s, and the first
part's whole job took 299 s. With half the other tests, the second part's
workers ran out of work while one worker was still building the first
controller run. `worksteal` then handed them the rest of the controller tests,
and each of those workers built the runs again, because a module fixture lives
in one process. A local profile showed four builds where the dealing expects
two. Now the controller runs are shared through `computed_once`, as the curves
are. So a worker handed a controller test waits for the run instead of
building it again (`PL-ZWQS`). The pytest line of `tools/main_ci_status.py`
shows the sum of both parts' times, so compare the two jobs' pytest steps in a
run's log instead.

**A pull request that changes only apparatus files skips the costly tests**
(`PL-STM6`). `--skip-costly` leaves out every test that reads a costly
computation. It finds them with the same `_costly_reads` that the parts and the
dealing use. `quality.yml` asks for it on the second part when
`bin/docket ci-scope` returns `apparatus`, because no apparatus file is an
input to those tests. It asks through `SKIP_COSTLY_TESTS=1`, which only this
conftest reads, and not through `PYTEST_ADDOPTS`. Every pytest that the suite
starts in a subprocess inherits `PYTEST_ADDOPTS`. The docket tests start
pytest in a scratch repository that has no `--skip-costly` option. So on the
first apparatus pull request that set the option through `PYTEST_ADDOPTS`,
that inner pytest stopped with exit code 4 (`#1774`). When the costly tests are
left out, the parts deal the ordinary tests with `SKIPPING_COSTLY_SHARES`
instead of `PART_SHARES`, because the second part then has far less to run.
Both parts ask for the skip, so they deal with the same shares. The first part
holds no costly test, so the skip changes only how many ordinary tests it
takes.

**The windows the tests leave open** (`PL-CW51`). Many tests build a dashboard
and never delete it, so a worker can end its run holding hundreds of windows.
Before this fix, the interpreter's exit destroyed them in no particular order.
Qt also keeps parentless widgets of its own. A pyqtgraph plot's layout builds
a `QGraphicsLayoutStyleInfo`, which holds one such widget in a `unique_ptr`
and deletes it with
the layout (https://github.com/qt/qtbase/blob/6.11/src/widgets/graphicsview/qgraphicslayoutstyleinfo.cpp).
Deleting such a widget before its plot makes the plot's layout delete it a
second time, which crashes the process. A drift job on CPython 3.15.0 printed
"pure virtual method called" as a worker exited. A worker here on 3.15.0 died
of a segmentation fault while the exit destroyed its windows. So, while the
application is still running, `pytest_sessionfinish` deletes the windows that
Python built. It leaves Qt's own widgets to their owners, which delete them.

**A supported-range constant set to a wrong value, on request** (`PL-0Z0F`).
`tools/restated_constants.py` runs the suite with one constant of
`anesthesia_sim.core.supported_ranges` moved, to find the tests that copy the
constant's value instead of importing its name. It asks for the move through
one environment variable, `NAME=VALUE`, whose name the tool owns. When the
variable is unset or empty, `perturb_ranges` does nothing, the header gains no
line, and the suite runs exactly as it would without this code.

When it is set, this file puts a finder at the front of `sys.meta_path` before
any module of the simulator is imported, and then imports the ranges module
through it. The finder compiles the module from its source with the one
binding of `NAME` replaced by `VALUE`, and never reads a cached `.pyc`. So the
module is built once, already holding the wrong value. A module that later
runs `from anesthesia_sim.core.supported_ranges import NAME` copies the wrong
value, as does a module-level value the ranges module derives from `NAME`.
Setting the attribute after an import would reach neither. If the ranges
module was imported before this file ran, and not by this file, the run stops
with a usage error, because the copies taken by then would hold the old value.
A test module that loads this file a second time finds the module already
built with the same perturbation, and that is allowed. The same holds if
the variable is malformed or names no numeric constant. Each xdist worker
imports this file, so each builds its own perturbed module.

The perturbation is printed in pytest's header, which is how the tool knows
that it was applied. A subprocess that a test starts imports the unperturbed
module, so a test that reads the constant only that way is not checked.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import os
import pickle
import sys
from collections.abc import Callable, Collection, Hashable, Mapping, Sequence
from itertools import islice
from pathlib import Path
from types import CodeType, ModuleType
from typing import TYPE_CHECKING, Any, Protocol

import pytest
from restated_constants import (
    PERTURBED_CONSTANT_VARIABLE,
    RANGES_MODULE,
    parse_perturbation,
    perturbation_line,
    perturbed_tree,
)

if TYPE_CHECKING:
    from xdist.workermanage import WorkerController

try:
    import fcntl
except ImportError:  # Windows, where `computed_once` shares nothing between workers
    fcntl = None

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class _PerturbedRangesLoader(importlib.machinery.SourceFileLoader):
    """Load the ranges module from its source with one constant's binding replaced."""

    def __init__(self, fullname: str, path: str, name: str, value: float) -> None:
        super().__init__(fullname, path)
        self.constant_name = name
        self.constant_value = value

    def get_code(self, fullname: str) -> CodeType:
        """Compile the perturbed source, bypassing the bytecode cache."""

        source = self.get_data(self.path).decode("utf-8")
        tree = perturbed_tree(source, self.constant_name, self.constant_value)
        return compile(tree, self.path, "exec", dont_inherit=True)


class _PerturbedRangesFinder(importlib.abc.MetaPathFinder):
    """Find the ranges module where the path finder does, and hand it the perturbing loader."""

    def __init__(self, name: str, value: float) -> None:
        self.constant_name = name
        self.constant_value = value

    def find_spec(
        self, fullname: str, path: Sequence[str] | None, target: ModuleType | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname != RANGES_MODULE:
            return None
        found = importlib.machinery.PathFinder.find_spec(fullname, path)
        if found is None or found.origin is None:
            raise pytest.UsageError(f"{PERTURBED_CONSTANT_VARIABLE}: {fullname} was not found")
        loader = _PerturbedRangesLoader(
            fullname, found.origin, self.constant_name, self.constant_value
        )
        return importlib.util.spec_from_file_location(fullname, found.origin, loader=loader)


def perturb_ranges(setting: str | None) -> str | None:
    """Build the ranges module with the constant `setting` names moved, and say what moved.

    `setting` is the environment variable's value. Unset or empty, nothing
    happens and the result is `None`. The module docstring says why the
    finder has to be installed before anything imports the module.
    """

    if not setting:
        return None
    try:
        name, value = parse_perturbation(setting)
    except ValueError as error:
        raise pytest.UsageError(str(error)) from error
    loaded = sys.modules.get(RANGES_MODULE)
    if loaded is not None:
        # A test module that loads this file again, as `test_worksteal_dealing.py`
        # does, finds the module already built with this perturbation.
        loader = getattr(loaded.__spec__, "loader", None)
        built_with = (
            getattr(loader, "constant_name", None),
            getattr(loader, "constant_value", None),
        )
        if built_with == (name, value):
            return perturbation_line(name, value)
        raise pytest.UsageError(
            f"{PERTURBED_CONSTANT_VARIABLE} is set, but {RANGES_MODULE} was imported before "
            "tests/conftest.py could perturb it, so earlier copies would hold the old value"
        )
    sys.meta_path.insert(0, _PerturbedRangesFinder(name, value))
    try:
        importlib.import_module(RANGES_MODULE)
    except ValueError as error:
        raise pytest.UsageError(str(error)) from error
    return perturbation_line(name, value)


_PERTURBATION = perturb_ranges(os.environ.get(PERTURBED_CONSTANT_VARIABLE))


def pytest_report_header(config: pytest.Config) -> list[str]:
    """Name the perturbed constant in pytest's header, and add nothing when there is none."""

    return [_PERTURBATION] if _PERTURBATION else []


class _CurveRead(Protocol):
    """One curve a washout test reads, as its module's `CURVES_READ` names it."""

    @property
    def elimination_duration_min(self) -> float: ...


def first_slice_sizes(tests: int, workers: int) -> list[int]:
    """Return the sizes of the slices that `--dist worksteal` deals the collection out in.

    `check_schedule` gives the i-th of n idle workers `len(pending) // (n - i)`
    of the tests still left, taken from the front. So the slices are
    contiguous, in order, and their sizes differ by one at most.
    """

    sizes: list[int] = []
    for worker in range(workers):
        sizes.append((tests - sum(sizes)) // (workers - worker))
    return sizes


def deal[Test: Hashable](
    tests: Sequence[Test], units: Sequence[tuple[Sequence[Test], float]], workers: int
) -> list[Test]:
    """Return `tests` reordered to put each unit at the head of a worker's first slice.

    A unit is a group of tests that share one costly computation, paired with
    what that computation costs. The tests of a unit run back to back. The
    units are placed heaviest first, each in the worker's slice with the least
    cost placed in it so far. So a slice that holds one heavy unit takes no
    other unit until every slice holds as much.
    The tests that belong to no unit keep their order and fill each slice
    behind its head. If a slice's units would not fit in it, `tests` is
    returned unchanged, because dealing them would run them into the next
    slice.
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


#: How many tests of each cycle each part takes, keyed by the number of parts.
#: The cycles deal only the ordinary tests, which are those that read no costly
#: computation. The first part's job also runs about 115 s of linters and tree
#: checks outside pytest. With an even split, that job finished last on both of
#: `PL-ZWQS`'s measured runs, by 17 s and by 116 s. So the first part takes 2 of
#: every 5 ordinary tests. Retune this when the two jobs' times drift apart. A
#: number of parts that is not named here splits the tests evenly.
PART_SHARES: dict[int, tuple[int, ...]] = {2: (2, 3)}

#: How many tests of each cycle each part takes when the costly tests are left
#: out, keyed by the number of parts (`PL-STM6`). With `PART_SHARES`, the first
#: part finished last on all 37 apparatus pull request runs measured on
#: 2026-10-26, by a median of 74 s. On the 26 of them that ran after `PL-GQCQ`
#: added the bytecode step, the first part's job spent a median of 163 s outside
#: pytest and the second part's 39 s. Their pytest steps took 119 s for 2 of
#: every 5 ordinary tests and 164 s for 3 of every 5. That puts the ordinary
#: tests at about 45 s of step time per fifth, plus about 28 s of start-up in
#: each step. Giving the first part 2 of every 9 ordinary tests then brings both
#: jobs to about 240 s. This is an estimate from those medians, not a measurement.
SKIPPING_COSTLY_SHARES: dict[int, tuple[int, ...]] = {2: (2, 7)}


def part[Test: Hashable](
    tests: Sequence[Test],
    costly: Collection[Test],
    index: int,
    parts: int,
    shares: Sequence[int] | None = None,
) -> list[Test]:
    """Return the tests that part `index` of `parts` runs, in their order in `tests`.

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
    """Return the tests that a run keeps, in their order in `tests`.

    With `skip_costly`, every test in `costly` is left out. When `chosen` is a
    `(K, N)` pair from `--part`, `part` then picks part K of N from the
    remaining tests. It uses the shares that `SKIPPING_COSTLY_SHARES` names for
    N parts with `skip_costly`, and those that `PART_SHARES` names without it.
    So every part of one run has to be given the same `skip_costly`.
    """

    kept = [test for test in tests if test not in costly] if skip_costly else list(tests)
    if chosen is None:
        return kept
    shares = SKIPPING_COSTLY_SHARES if skip_costly else PART_SHARES
    return part(kept, costly, *chosen, shares.get(chosen[1]))


def _part(text: str) -> tuple[int, int]:
    """Parse `--part K/N` into (K, N), refusing a K outside 1 to N."""

    index, _, parts = text.partition("/")
    if not (index.isdigit() and parts.isdigit() and 1 <= int(index) <= int(parts)):
        raise argparse.ArgumentTypeError(
            f"{text!r} is not K/N with 1 <= K <= N, such as 1/2 for the first of two parts"
        )
    return int(index), int(parts)


#: The environment variable that asks for `--skip-costly`, set to "1". Only this
#: conftest reads it, so a pytest started in another repository never sees it.
SKIP_COSTLY_VARIABLE = "SKIP_COSTLY_TESTS"


def skip_costly_asked(environ: Mapping[str, str]) -> bool:
    """Return whether the environment asks for `--skip-costly`, which only the value "1" does."""

    return environ.get(SKIP_COSTLY_VARIABLE) == "1"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add `--part K/N` and `--skip-costly`, the two ways CI narrows a run of the suite.

    Also add `--write-assertion-cache K/N`, which CI's step before the suite
    runs. The root `conftest.py` says what it does.
    """

    parser.addoption(
        "--part",
        type=_part,
        metavar="K/N",
        help="run only part K of N, as each of quality.yml's two pytest jobs does",
    )
    parser.addoption(
        "--skip-costly",
        action="store_true",
        default=skip_costly_asked(os.environ),
        help="leave out every test that reads a costly computation, as quality.yml does on a "
        "pull request that changes only apparatus files",
    )
    # The root `conftest.py` acts on this option, because it owns the bytecode
    # guard and its hooks reach both test trees. It is registered here so that
    # it is parsed by `_part`, the one parser of `K/N` (`PL-GQCQ`).
    parser.addoption(
        "--write-assertion-cache",
        type=_part,
        metavar="K/N",
        help="with --collect-only, collect share K of N of the test modules and write "
        "pytest's rewritten bytecode for each, as quality.yml does before its pytest step",
    )


def _costly_reads(
    items: Sequence[pytest.Item],
) -> tuple[dict[pytest.Function, tuple[_CurveRead, ...]], dict[ModuleType, list[pytest.Function]]]:
    """Return the tests that read a costly computation.

    The first mapping gives the curves that each test reads. The second gives,
    for each module, the tests that use one of its costly module fixtures.
    """

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
    """Return the units to deal: each costly computation's tests, with its cost in minutes."""

    reads, groups = _costly_reads(items)

    # A curve's opener is the first test that reads it as its first curve. If no test does,
    # the opener is the first test that reads the curve at all.
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
    """Return `compute()`, run by the first process to ask for `name`, read from `store` by others.

    The first process to ask takes a lock on `name`, runs `compute()` and
    publishes the pickled result in `store`. A process that asks meanwhile
    waits on the lock and then reads what was published. The result is written
    whole and then renamed into place. The lock is `flock`, which the kernel
    releases if the process holding it dies. So after a crash, the next process
    runs `compute()` itself, rather than reading half a result or waiting for
    ever.
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


@pytest.fixture(autouse=True, scope="session")
def _hook_block_log(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Keep the guards' refusals out of this machine's real block log (`PL-SG93`).

    The guard tests run each hook with this process's environment, and a hook
    that refuses appends a line to the log `HOOK_BLOCK_LOG` names. Without
    this, every test run would add hundreds of refusals that no session made.
    """
    os.environ["HOOK_BLOCK_LOG"] = str(tmp_path_factory.mktemp("hooks") / "hook-blocks.tsv")


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
    one worker with `--dist loadgroup` would also compute each value once.
    That approach was measured for the curves and set aside. It slowed the
    rest of the suite by 8 to 11 s, and the whole run by 19 s, compared with
    this fixture (`PL-F08Y` has the figures).

    The store is a directory inside the run's own base temporary directory,
    which is the parent of each worker's temporary directory. Pytest makes that
    directory afresh for every run and empties it when one is named with
    `--basetemp`. So a value published there cannot be served to a later run
    built from different source, which is the hazard `PL-0MLZ` closed for
    bytecode. For the same reason, the fixture decides whether to share by
    checking `workerinput`, which xdist sets on a worker's own configuration.
    It does not check `PYTEST_XDIST_WORKER`, which a pytest started inside a
    worker would inherit. The parent of that inner run's base directory
    outlives the inner run. Without xdist, one process runs every test, so
    `compute()` runs once anyway. Windows has no `fcntl`, so there each worker
    computes what it needs.
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

    The hook is `trylast`, so that it deals the order that every other hook has
    finished with. Every worker runs this hook on the same collection and gets
    the same result. xdist requires that of a collection before it schedules
    any of its tests. The costs are summed in table order, never in a set's
    order, so no worker's hash seed can round them differently. The part is
    chosen before the dealing, so the dealing places only the units this part
    runs.
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
    """Return the parentless windows among `windows` that Python built, in their order.

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
