"""Keep the seeded random runs out of every pytest run that does not ask for them.

`test_multisession.py`'s random interleavings take minutes, and a finding they
make is a new item rather than a regression in the change under test. So a
test marked `slow` is deselected unless the `-m` expression names `slow`, as
`pytest -m slow subprojects/docket/tests/test_multisession.py` does. It is
deselected rather than skipped, because `-ra` prints a line for every skip on
every run, which nobody acts on.
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "slow: a seeded random run, deselected unless -m names slow")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if "slow" in (config.getoption("markexpr") or ""):
        return
    slow = [item for item in items if item.get_closest_marker("slow")]
    if slow:
        config.hook.pytest_deselected(items=slow)
        items[:] = [item for item in items if not item.get_closest_marker("slow")]
