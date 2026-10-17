"""Hold the root `conftest.py`'s store-read guard to what it promises (`PL-DXD4`).

On a pull request that changes only item files, CI runs only the tests marked
`reads_item_store`, so a test that reads the store without the marker would be
skipped exactly when an item file could change its result. The guard fails
such a test, and these cases show it doing so for each kind of read it claims
to see, and leaving alone the reads it should.

Each case is a real pytest run in a scratch project that holds a copy of the
root `conftest.py`, a `docket.toml` and a one-item store. The store is named
`records` rather than `docs/items`, so a guard that spelled the store's
directory itself, instead of reading `docket.toml`, fails here. The run is
repeated under `pytest-xdist`, because CI runs the suite that way and a report
changed in a worker has to reach the controller.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

_CASES = """
import glob
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
ITEM = ROOT / "records" / "PL-B1C2-an-item.md"


def test_unmarked_open():
    ITEM.read_text(encoding="utf-8")


@pytest.mark.reads_item_store
def test_marked_open():
    ITEM.read_text(encoding="utf-8")


def test_unmarked_listing():
    os.listdir(ROOT / "records")


def test_unmarked_glob():
    glob.glob("*.md", root_dir=ROOT / "records")


def test_unmarked_subprocess_naming_the_store():
    subprocess.run(["ls", "records"], cwd=ROOT, check=True, capture_output=True)


@pytest.fixture
def item_text():
    return ITEM.read_text(encoding="utf-8")


def test_unmarked_fixture(item_text):
    assert item_text


def test_a_store_of_the_same_name_elsewhere(tmp_path):
    copy = tmp_path / "records" / "PL-B1C2-an-item.md"
    copy.parent.mkdir()
    copy.write_text("a copy", encoding="utf-8")
    assert copy.read_text(encoding="utf-8") == "a copy"


def test_reading_something_beside_the_store():
    (ROOT / "records-notes.md").read_text(encoding="utf-8")
"""

_MODULE_MARKED = """
from pathlib import Path

import pytest

pytestmark = pytest.mark.reads_item_store

ITEMS = sorted((Path(__file__).parent / "records").iterdir())


def test_reads_at_import_and_in_the_test():
    assert ITEMS[0].read_text(encoding="utf-8")
"""

_IMPORT_UNMARKED = """
from pathlib import Path

ITEMS = sorted((Path(__file__).parent / "records").iterdir())


def test_never_runs():
    assert ITEMS
"""

#: The scratch project's test modules, which the run names one by one. Named
#: rather than collected, so pytest does not walk into the store looking for
#: tests, which the real suite's `testpaths` never does either.
_MODULES = {
    "test_cases.py": _CASES,
    "test_module_marked.py": _MODULE_MARKED,
    "test_import_unmarked.py": _IMPORT_UNMARKED,
}

#: What each case should come to, by the node id pytest's summary prints.
_EXPECTED = {
    "test_cases.py::test_unmarked_open": "FAILED",
    "test_cases.py::test_marked_open": "PASSED",
    "test_cases.py::test_unmarked_listing": "FAILED",
    "test_cases.py::test_unmarked_glob": "FAILED",
    "test_cases.py::test_unmarked_subprocess_naming_the_store": "FAILED",
    "test_cases.py::test_unmarked_fixture": "ERROR",
    "test_cases.py::test_a_store_of_the_same_name_elsewhere": "PASSED",
    "test_cases.py::test_reading_something_beside_the_store": "PASSED",
    "test_module_marked.py::test_reads_at_import_and_in_the_test": "PASSED",
    "test_import_unmarked.py": "ERROR",
}

_SUMMARY = re.compile(r"^(PASSED|FAILED|ERROR) (\S+)", re.MULTILINE)


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "records").mkdir(parents=True)
    (root / "records" / "PL-B1C2-an-item.md").write_text(
        "---\nid: PL-B1C2\n---\n", encoding="utf-8"
    )
    (root / "records-notes.md").write_text("Next to the store, not in it.\n", encoding="utf-8")
    (root / "docket.toml").write_text('[docket]\nitems_dir = "records"\n', encoding="utf-8")
    (root / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    conftest = (REPO / "conftest.py").read_text(encoding="utf-8")
    (root / "conftest.py").write_text(conftest, encoding="utf-8")
    for name, source in _MODULES.items():
        (root / name).write_text(textwrap.dedent(source), encoding="utf-8")
    return root


@pytest.mark.parametrize("workers", [(), ("-n", "2")], ids=["serial", "xdist"])
def test_the_guard_fails_each_unmarked_read_of_the_store(
    tmp_path: Path, workers: tuple[str, ...]
) -> None:
    """Every unmarked read fails, and a marked read or a read elsewhere passes."""
    root = _project(tmp_path)
    environment = {key: value for key, value in os.environ.items() if key != "PYTEST_ADDOPTS"}
    environment["PYTHONPATH"] = str(REPO / "subprojects" / "docket" / "src")

    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-rA",
            "-p",
            "no:cacheprovider",
            # One module's collection error otherwise stops the run before
            # any test in the other two has run.
            "--continue-on-collection-errors",
            *workers,
            *_MODULES,
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    outcomes = {node: outcome for outcome, node in _SUMMARY.findall(done.stdout)}
    assert outcomes == _EXPECTED, done.stdout + done.stderr
    assert (
        "test_cases.py::test_unmarked_open (call) read the item store "
        "(records/PL-B1C2-an-item.md) without the `reads_item_store` marker"
    ) in done.stdout
    assert "test_cases.py::test_unmarked_fixture (setup) read the item store" in done.stdout
    assert "test_import_unmarked.py read the item store (records)" in done.stdout
