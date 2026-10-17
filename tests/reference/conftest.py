"""Start each washout curve at the head of a different xdist worker's first slice.

`test_late_washout_against_published_fits.py` computes eight 24-hour curves and
eight 6-hour ones, each once per run, shared between workers through its
`washout_curve` fixture (`PL-F08Y`). Where they run is left to the scheduler,
and under `--dist worksteal` that puts them last: it deals the collection out
in contiguous slices at the start, the module's tests sit 522 deep in the first
worker's, and nothing steals them sooner, since stealing starts only as other
slices run dry. So every curve began in the last third of the run, and a slow
CI runner waited about 70 s for them after every other test had finished
(`PL-4Z5Y` has the measurements).

This moves the first test to read each curve to the head of a slice, the 24-hour
curves first and each curve to the slice with the least to compute so far, so
every worker starts the run on one or two curves, computed in its own process
where coverage measures them, and every other washout test reads them from the
cache. Sixteen tests run apart from their module, which shares nothing between
its tests but that fixture.

It mirrors how pytest-xdist 3.8.0 deals the first slices
(`WorkStealingScheduling.check_schedule`, `xdist/scheduler/worksteal.py`), an
internal, so `tests/unit/test_reference_conftest.py` holds the mirror to the
installed scheduler. If the two part, the curves start wherever the moved tests
land, which costs speed and nothing else. Without xdist, or under another
`--dist` mode, the order is left alone: a worker reads the mode from its
`workerinput`, where `tests/conftest.py` puts it, since its own option says
`no`.
"""

from __future__ import annotations

from itertools import islice

import pytest


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


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Move the first reader of each curve to the head of a worker's first slice.

    `trylast`, so that the order dealt is the one every other hook has finished
    with. Every worker runs this on the same collection and gets the same
    answer, which xdist requires of a collection before it schedules any.
    """

    workerinput = getattr(config, "workerinput", None)
    if workerinput is None or workerinput.get("dist") != "worksteal":
        return

    from test_late_washout_against_published_fits import CURVES_READ, CurveRead

    reads: dict[pytest.Item, tuple[CurveRead, ...]] = {}
    for item in items:
        if isinstance(item, pytest.Function) and item.function in CURVES_READ:
            reads[item] = CURVES_READ[item.function](**item.callspec.params)
    if not reads:
        return

    # A test that reads the curve first opens it; failing one, the first to read it at all.
    openers: dict[CurveRead, pytest.Item] = {}
    for item, curves in reads.items():
        openers.setdefault(curves[0], item)
    for item, curves in reads.items():
        for curve in curves:
            openers.setdefault(curve, item)

    workers: int = workerinput["workercount"]
    load = [0] * workers
    heads: list[list[pytest.Item]] = [[] for _ in range(workers)]
    slice_of: dict[pytest.Item, int] = {}
    for curve, item in sorted(openers.items(), key=lambda pair: -pair[0].elimination_duration_min):
        if item not in slice_of:
            slice_of[item] = load.index(min(load))
            heads[slice_of[item]].append(item)
        load[slice_of[item]] += curve.elimination_duration_min

    sizes = first_slice_sizes(len(items), workers)
    if any(len(head) > size for head, size in zip(heads, sizes, strict=True)):
        return
    rest = iter([item for item in items if item not in slice_of])
    dealt = [
        test
        for head, size in zip(heads, sizes, strict=True)
        for test in (*head, *islice(rest, size - len(head)))
    ]
    if len(dealt) != len(items) or set(dealt) != set(items):
        raise RuntimeError(
            f"dealing the washout curves first turned {len(items)} tests into {len(dealt)}, "
            f"{len(set(dealt))} of them distinct, which would skip or repeat a test"
        )
    items[:] = dealt
