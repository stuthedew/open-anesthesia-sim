"""Process settings every pytest run in this repository takes, however it is started.

**Git configuration no test tree may read.**
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` are set to `/dev/null`, which git
documents as the value that makes it read no configuration at that level (git
2.32 and later). Tests under `subprojects/docket/tests/` build a scratch
repository with real git per test, because what is under test is largely what
git reports, and `tests/unit/`'s hook tests run git too - so whatever the
developer keeps in `~/.gitconfig` reaches all of it, and one ordinary setting
there changes what the suite costs for reasons nothing in the tests explains.
`commit.gpgsign = true` with `gpg.format = ssh` costs 72.7 ms per commit
against 5.1 ms unsigned; over the 563 commits the `docket` tree makes that is
40.9 s of a 60.4 s run, which these two lines cut to 2.9 s of 21.5 s with no
test changed (`PL-YRYR`, measured 2026-09-21).

Speed is the half that can be measured. The half that matters more is that a
signing key held on hardware, or behind a passphrase, does not make the suite
slow - it makes `git commit` block on a prompt or fail outright, and every test
that needs history fails with it, on a machine where nothing is wrong. A suite
that builds real repositories has to own their configuration; reading the
developer's is how it becomes environment-dependent without anyone choosing
that, and the failure then arrives on someone else's machine.

Assignment rather than `setdefault`, unlike `QT_QPA_PLATFORM` in
`tests/conftest.py`: there a developer with a display may legitimately want
their own value, whereas here a test repository that reads an outside config is
the defect, so there is no version of it to preserve.

**No bytecode written, so a restored source is the one that runs** (`PL-0MLZ`).
CPython accepts a cached `.pyc` when the source's size, and its mtime truncated
to the whole second, match what the cache recorded: in
`importlib._bootstrap_external`, `SourceLoader.get_code` takes `int()` of the
mtime and `_validate_timestamp_pyc` compares the two. So an equal-length edit
that is compiled and then reverted inside one second leaves a cache that
validates against the reverted file, and the next run executes the edit the
file no longer contains. That is the mutation test's own rhythm: measured
2026-09-27, 11 of 12 cycles of mutating
`src/anesthesia_sim/core/alveolar.py`'s `gas_volume_l` from 2.5 to 2.6,
importing it, copying the original back and importing again ran 2.6 while the
file said 2.5. It fails in the direction that costs most - a test that looks
as if it catches a mutation when what ran was another build - and `PL-01GD`
met it in `make check`.

`sys.dont_write_bytecode` stops this process writing a cache, and
`PYTHONDONTWRITEBYTECODE` reaches the interpreters the suite starts - the
hooks, `tools/` and `bin/docket` runs under test. The `Makefile` exports the
same variable to its recipes, but a `verify:` command, a session iterating and
CI all run `pytest` without `make`, and uv has no setting that exports a
variable: uv 0.12.19 refuses `env` and `env-file` under `[tool.uv]` as unknown
fields and reads a `.env` only when told to. Here it follows every `pytest`
run and nothing else, so the app's own startup keeps its cache.

It stops a write and not a read: a cache written by something other than a
test run, from source mutated and restored inside one second, still shadows
the restored file.

**A test that reads the item store says so** (`PL-DXD4`). On a pull request
that changes only item files, `quality.yml` skips the full suite and runs only
the tests marked `reads_item_store`. Only a test that reads the store can
change its result when nothing but item files changed. This file registers the
marker and fails a test that reads the store without it, so the marked set
cannot fall behind the tests. The store is the directory `docket.toml` names.

A read is anything this process does to the store while a test runs or while a
test module is imported. That covers opening a file in it, listing it, globbing
in it, and starting a subprocess whose arguments name a path in it, such as a
`git ls-tree` of the store. A whole module can be marked with `pytestmark =
pytest.mark.reads_item_store`, and a module that reads the store while it is
imported must be.

A read counts against the test that makes it. So where tests share a cached
result that reads the store, the read counts against whichever of them runs
first in its process, and that depends on how the run deals the tests. Mark
every test that uses such a result, as `test_doc_check.py` marks the three
tests of `_this_repository()`.

The guard cannot see a read made by a subprocess that does not name the store,
such as `bin/docket check` run in the checkout. When the guard was added, two
runs in a scratch clone checked that no unmarked test depends on the store that
way. With every item file replaced by one unparseable line, the whole suite
had one failure, a test that reads the store in-process. With every item file
removed, two unmarked tests failed because the store's directory was gone, and
both passed with one item back. That run also found the cached read above. So
no unmarked test depends on what an item says or on which items exist.

**A failed subprocess shows what it printed** (`PL-GLHZ`). The suite runs
real git, and other programs, with `check=True` and `capture_output=True`, so a
non-zero exit raises `subprocess.CalledProcessError` holding the program's
output. Pytest prints that exception without the output, so the failure says
"exit status 128" and drops git's own message, which names the cause. That
happened once in CI on 2026-10-18, and nothing could be learned from it. So
the report of any test phase that failed with that exception gets a section
for each stream the exception captured, which pytest prints beside the
traceback. Every test is covered at once, and no fixture has to remember it.

At the repository root rather than in each tree, for two reasons. One rule
covers both trees and `pytest` resolves `rootdir` here however it is invoked -
including from inside `subprojects/docket/`, whose own `pyproject.toml`
declares no pytest section, so the walk continues up to this one. And
`tools/ignore_check.py` type-checks `tests` and `subprojects/docket/tests` in a
single mypy invocation, where a second file named `conftest` in those trees is
a duplicate-module error that stops mypy before it evaluates anything
(`PL-CR36`). This file sits outside both, so it cannot collide.
"""

import os
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

#: The marker a test that reads the item store carries.
READS_ITEM_STORE = "reads_item_store"

#: The audit events through which this process reads a directory's files.
_READ_EVENTS = frozenset({"open", "os.listdir", "os.scandir", "glob.glob", "glob.glob/2"})


class _StoreReads:
    """The store's absolute path, and the reads of it since the current watch began.

    `reads` is `None` while nothing is watched, which is between tests and
    collectors, so the audit hook returns at once for every event outside a
    watch.
    """

    def __init__(self) -> None:
        self.store = ""
        self.reads: list[str] | None = None

    def holds(self, path: str) -> bool:
        return path == self.store or path.startswith(self.store + os.sep)

    def take(self) -> list[str]:
        """The reads so far, and a fresh list for the reads that follow."""
        taken, self.reads = self.reads or [], []
        return taken


_STORE_READS = _StoreReads()


def _absolute(target: object, base: str | None = None) -> str | None:
    """`target` as an absolute path, or `None` where it is not a path at all.

    A relative path is taken from `base` where one is given, and otherwise
    from this process's working directory. A file descriptor is not a path.
    """
    if not isinstance(target, (str, bytes, os.PathLike)):
        return None
    return os.path.abspath(os.path.join(base or os.getcwd(), os.fsdecode(target)))


def _audit(event: str, args: tuple[object, ...]) -> None:
    reads = _STORE_READS.reads
    if reads is None:
        return
    if event in _READ_EVENTS:
        target = args[0] if args else None
        base = None
        if event == "glob.glob/2":
            base = _absolute(args[2]) if args[2] is not None else None
        elif event != "open" and target is None:
            target = "."
        path = _absolute(target, base)
        if path is not None and _STORE_READS.holds(path):
            reads.append(path)
    elif event == "subprocess.Popen":
        _, command, cwd, _ = args
        if isinstance(command, (str, bytes)):
            words: list[object] = list(os.fsdecode(command).split())
        else:
            words = list(command) if isinstance(command, (list, tuple)) else [command]
        base = _absolute(cwd)
        for word in words:
            path = _absolute(word, base)
            if path is not None and _STORE_READS.holds(path):
                reads.append(path)
                break


def pytest_configure(config: pytest.Config) -> None:
    """Register the marker, find the store, and start the audit hook that watches it."""
    from docket.config import load as load_config

    config.addinivalue_line(
        "markers",
        f"{READS_ITEM_STORE}: the test reads the item store, so CI runs it on a pull "
        "request that changes only item files (`PL-DXD4`)",
    )
    root = Path(__file__).resolve().parent
    _STORE_READS.store = str(root / load_config(root).items_dir)
    sys.addaudithook(_audit)


def _unmarked(what: str, reads: list[str]) -> str:
    """The failure for a test or module that read the store without the marker."""
    first = os.path.relpath(reads[0], Path(__file__).resolve().parent)
    others = f" and {len(reads) - 1} more" if len(reads) > 1 else ""
    return (
        f"{what} read the item store ({first}{others}) without the "
        f"`{READS_ITEM_STORE}` marker, so CI would skip it on a pull request that "
        f"changes only item files. Mark it with `@pytest.mark.{READS_ITEM_STORE}`, or "
        f"mark the module with `pytestmark = pytest.mark.{READS_ITEM_STORE}`. The root "
        "conftest.py says why."
    )


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(
    item: pytest.Item, nextitem: pytest.Item | None
) -> Generator[None, object, object]:
    """Watch the store from the start of a test's setup to the end of its teardown."""
    _STORE_READS.reads = []
    try:
        return (yield)
    finally:
        _STORE_READS.reads = None


def subprocess_output_sections(error: BaseException) -> list[tuple[str, str]]:
    """The report sections that show what a failed subprocess printed.

    One section for each stream that `error` captured and that is not empty,
    in the order stderr, then stdout, since stderr is where git explains a
    failure. Any other exception, or one whose streams were not captured,
    gives no section. Bytes are decoded with replacement, so a stream that is
    not valid UTF-8 still shows.
    """
    if not isinstance(error, subprocess.CalledProcessError):
        return []
    command = error.cmd if isinstance(error.cmd, str) else " ".join(map(str, error.cmd))
    sections = []
    for name, stream in (("stderr", error.stderr), ("stdout", error.stdout)):
        text = stream.decode(errors="replace") if isinstance(stream, bytes) else stream
        if text:
            sections.append((f"Captured {name} of the failed command `{command}`", text))
    return sections


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Show a failed subprocess's output, and fail a phase that read the store unmarked.

    The report is made right after its phase, so the reads taken here are that
    phase's own.
    """
    report = yield
    if call.excinfo is not None:
        report.sections.extend(subprocess_output_sections(call.excinfo.value))
    reads = _STORE_READS.take()
    if reads and item.get_closest_marker(READS_ITEM_STORE) is None:
        report.outcome = "failed"
        report.longrepr = _unmarked(f"{item.nodeid} ({call.when})", reads)
        if hasattr(report, "wasxfail"):
            del report.wasxfail
    return report


@pytest.hookimpl(wrapper=True)
def pytest_make_collect_report(
    collector: pytest.Collector,
) -> Generator[None, pytest.CollectReport, pytest.CollectReport]:
    """Fail the collection of a test module or class that read the store without the marker.

    A test module is imported while it is collected, so a read at import time
    belongs to its collector, and its tests can only be marked through
    `pytestmark`. A directory's collector is not watched: it lists its own
    directory to find tests, and the test paths never include the store. The
    session can collect a module inside its own collection, so whatever watch
    was running around this one is put back afterwards.
    """
    if not isinstance(collector, (pytest.Module, pytest.Class)):
        return (yield)
    around, _STORE_READS.reads = _STORE_READS.reads, []
    try:
        report = yield
    finally:
        reads, _STORE_READS.reads = _STORE_READS.reads or [], around
    if reads and collector.get_closest_marker(READS_ITEM_STORE) is None:
        report.outcome = "failed"
        report.longrepr = _unmarked(collector.nodeid or "collection", reads)
    return report
