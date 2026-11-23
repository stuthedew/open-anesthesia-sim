"""Each test runs under a time limit, so a loop that never ends fails one test by name.

Nothing limited how long a single test could run until `PL-FKVR`. A fault that
made a loop run forever hung the whole run until the CI job's own
`timeout-minutes`, and the log named no test, because the run never reported
one. `timeout` in `pyproject.toml`'s `[tool.pytest.ini_options]` now sets the
limit, which the pytest-timeout plugin reads.

Two things have to hold, and reading the file shows only the first:

- `pyproject.toml` sets a limit, as a whole number of seconds greater than
  zero. The plugin treats zero as no limit at all. The comment beside the
  setting carries the measurement the number comes from.
- pytest resolves that same limit for a real run in this repository, and with
  the `signal` method, which fails the one test and lets the run finish. The
  plugin prints the limit and the method in its part of the report header, so
  collecting one test file reads both back.

The second test catches three ways the limit can stop applying. The setting is
deleted. The plugin is left out of the `dev` dependency group, after which
pytest only warns that it does not recognise the option. The method is changed
to `thread`, which ends the whole process rather than failing the one test.

The third test lets the limit fire. Code in this repository can stop the
plugin's alarm from ever going off: `.claude/hooks/guard.py` once replaced it
with its own. So the test runs two tests that never end, under this
repository's configuration and the parallel runner, one of them after building
a Qt widget, and checks that each fails by name while the run finishes.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _limit_s() -> int:
    """The per-test limit in seconds, as `tomllib` reads it from `pyproject.toml`."""
    config = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    options = config["tool"]["pytest"]["ini_options"]
    assert "timeout" in options, "[tool.pytest.ini_options] sets no time limit for a test"
    limit: int = options["timeout"]
    return limit


def test_the_configuration_sets_a_time_limit_for_each_test() -> None:
    limit = _limit_s()

    assert isinstance(limit, int), "the limit is a whole number of seconds"
    assert limit > 0, "the plugin reads a limit of zero as no limit"


def test_pytest_resolves_that_limit_with_the_method_that_fails_one_test() -> None:
    """A real collection reports the limit from `pyproject.toml` and the `signal` method.

    This file is the one collected, so the test depends on no other file's
    name. The header is read from a pytest process rather than from the
    plugin's settings in this one, because a session, `make check` and CI each
    start their own process, and the question is what that process resolves.
    """
    limit = _limit_s()

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-p", "no:cacheprovider", __file__],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"timeout: {float(limit)}s" in result.stdout, result.stdout
    assert "timeout method: signal" in result.stdout, result.stdout


#: Two tests that never end. The second builds and shows a Qt widget first, as
#: the interface tests do, and then loops in Python.
_LOOPING_TESTS = """\
from PySide6.QtWidgets import QApplication, QLabel


def test_a_plain_loop_that_never_ends():
    while True:
        pass


def test_a_loop_that_never_ends_after_a_qt_widget_is_shown():
    application = QApplication.instance() or QApplication([])
    label = QLabel("a widget")
    label.show()
    application.processEvents()

    while True:
        pass
"""


def test_a_test_that_never_ends_fails_by_name_and_the_run_finishes(tmp_path: Path) -> None:
    """Two endless tests under this repository's configuration each fail by name.

    The run reads `pyproject.toml` as its configuration, so it has the same
    plugins, path and options as `make check`, and runs under the parallel
    runner with two workers. Only the limit is shortened, to two seconds, so
    the test takes seconds rather than ten minutes. If the limit never fired,
    the outer `timeout` of `subprocess.run` would stop the run and fail this
    test with `TimeoutExpired`.
    """
    looping = tmp_path / "test_looping.py"
    looping.write_text(_LOOPING_TESTS, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            str(REPO / "pyproject.toml"),
            "--rootdir",
            str(REPO),
            "-p",
            "no:cacheprovider",
            "--timeout",
            "2",
            "-n",
            "2",
            str(looping),
        ],
        cwd=tmp_path,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    report = result.stdout + result.stderr

    assert result.returncode == 1, report
    assert "2 failed" in result.stdout, report

    for name in (
        "test_a_plain_loop_that_never_ends",
        "test_a_loop_that_never_ends_after_a_qt_widget_is_shown",
    ):
        assert "Failed: Timeout (>2.0s) from pytest-timeout." in _failure_of(name, result.stdout), (
            report
        )


def _failure_of(name: str, report: str) -> str:
    """The part of a pytest report under the heading of the failed test `name`.

    pytest heads each failure with its test's name between rules of
    underscores, and the part runs to the next such heading or to the summary.
    """
    lines = report.splitlines()
    starts = [
        index for index, line in enumerate(lines) if line.startswith("_") and line.endswith("_")
    ]
    for position, start in enumerate(starts):
        if f" {name} " in lines[start]:
            end = starts[position + 1] if position + 1 < len(starts) else len(lines)
            return "\n".join(lines[start:end])
    raise AssertionError(f"the report has no failure headed {name}:\n{report}")
