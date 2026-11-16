"""Fixtures shared by the dashboard's integration tests in this directory.

Each test module gets its own application handle and tears down the dashboards it showed, as the
one file these tests came from did (`PL-1FPR`).
"""

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from tests.integration.simulation_view.simulation_view_support import _delete_shown_views


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture(scope="module", autouse=True)
def _torn_down_views(application: QApplication) -> Iterator[None]:
    yield

    _delete_shown_views(application)
