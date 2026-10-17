"""`tests/reference/conftest.py`'s copy of how `--dist worksteal` deals its first slices.

The conftest moves the first reader of each washout curve to where it predicts
a worker's first slice begins (`PL-4Z5Y`). The prediction copies arithmetic out
of pytest-xdist's scheduler, an internal, so this holds it to the installed
scheduler: a release that deals differently fails here, where otherwise the
only sign would be a slower run.
"""

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import cast

import pytest
from xdist.scheduler.worksteal import WorkStealingScheduling
from xdist.workermanage import WorkerController

CONFTEST = Path(__file__).parents[1] / "reference" / "conftest.py"


def _conftest() -> ModuleType:
    """The conftest loaded under a name of its own, since every conftest is `conftest`."""

    spec = importlib.util.spec_from_file_location("reference_conftest", CONFTEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Worker:
    """What `WorkStealingScheduling` asks of a worker before any test has run."""

    shutting_down = False

    def __init__(self, index: int) -> None:
        self.gateway = SimpleNamespace(id=f"gw{index}")
        self.dealt: list[int] = []

    def send_runtest_some(self, indices: list[int]) -> None:
        self.dealt.extend(indices)


@pytest.mark.parametrize(("tests", "workers"), [(5614, 8), (40, 8), (17, 3), (16, 8)])
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
    assert [len(dealt) for dealt in slices] == _conftest().first_slice_sizes(tests, workers), (
        "worksteal's first slices are no longer the sizes tests/reference/conftest.py predicts, "
        "so the washout curves no longer start at the head of a worker's slice"
    )
