"""The suite's own git configuration, which every scratch repository inherits.

The repository root's `conftest.py` points `GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_SYSTEM` at `/dev/null` so that the repositories these tests build
read no configuration from the machine running them. It is pinned from here
rather than from `tests/`, because this is the tree that builds one per test.

Nothing else in the suite fails when that stops being true: every test still
passes, three times slower, and the next thing a developer's `~/.gitconfig`
turns on decides whether they pass at all. These two tests are what makes its
removal visible instead of silent.

The same `conftest.py` puts a failed command's captured output into the test's
failure report, since git explains a failure only on its stderr (`PL-GLHZ`).
The last two tests pin that.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

#: What git documents as "read no configuration at this level" (git 2.32).
NO_CONFIG = "/dev/null"


def test_the_suite_points_git_at_no_configuration_file() -> None:
    """The mechanism, named, so a failure of the test below reads in one line."""
    assert os.environ.get("GIT_CONFIG_GLOBAL") == NO_CONFIG
    assert os.environ.get("GIT_CONFIG_SYSTEM") == NO_CONFIG


def test_a_scratch_repository_ignores_the_developer_s_own_git_config(tmp_path: Path) -> None:
    """The guarantee itself, against a home directory that turns commit signing on.

    Asserting only that the variables are set would pass on a machine whose
    `~/.gitconfig` is empty - the one machine that needs no isolation. So the
    configuration that must be ignored is built here rather than assumed, which
    makes the assertion mean the same thing on every machine.
    """
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text("[commit]\n\tgpgsign = true\n", encoding="utf-8")
    root = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)

    read = subprocess.run(
        ["git", "config", "--get", "commit.gpgsign"],
        cwd=root,
        capture_output=True,
        text=True,
        env=os.environ | {"HOME": str(home), "XDG_CONFIG_HOME": str(home)},
    )

    # `git config --get` exits 1 for a key no configuration file sets.
    assert read.returncode == 1, f"read commit.gpgsign={read.stdout.strip()!r} from outside"
    assert read.stdout == ""


def _root_conftest(config: pytest.Config) -> ModuleType:
    """The repository root's `conftest.py`, as pytest loaded it."""
    path = str(config.rootpath / "conftest.py")
    for plugin in config.pluginmanager.get_plugins():
        if isinstance(plugin, ModuleType) and plugin.__file__ == path:
            return plugin
    raise AssertionError(f"pytest did not load {path}")


def _failed_git(tmp_path: Path) -> subprocess.CalledProcessError:
    """A real git failure, captured the way the suite's fixtures capture one."""
    with pytest.raises(subprocess.CalledProcessError) as raised:
        subprocess.run(("git", "commit", "-qm", "x"), cwd=tmp_path, check=True, capture_output=True)
    return raised.value


def test_a_failed_subprocess_shows_its_output_in_the_report(
    tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    """Git's own message reaches the report, through the hook pytest calls.

    `tmp_path` is no repository, so git exits 128 and says why on stderr. The
    hook is driven by hand with a report built from that failure, which is
    what pytest does after a test phase raises.
    """
    error = _failed_git(tmp_path)
    call = pytest.CallInfo.from_call(lambda: _raise(error), "call")
    report = pytest.TestReport.from_item_and_call(request.node, call)
    hook = _root_conftest(request.config).pytest_runtest_makereport(request.node, call)
    next(hook)
    with pytest.raises(StopIteration) as finished:
        hook.send(report)

    sections = dict(finished.value.value.sections)

    assert error.returncode == 128
    assert sections == {
        "Captured stderr of the failed command `git commit -qm x`": error.stderr.decode()
    }
    assert "not a git repository" in error.stderr.decode()


def test_only_a_subprocess_failure_gains_a_section(
    tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    sections_for = _root_conftest(request.config).subprocess_output_sections
    uncaptured = subprocess.CalledProcessError(1, ("false",))

    assert sections_for(ValueError("not a subprocess")) == []
    assert sections_for(uncaptured) == []
    assert sections_for(subprocess.CalledProcessError(1, "make", output="", stderr=b"\xff")) == [
        ("Captured stderr of the failed command `make`", "\ufffd")
    ]


def _raise(error: BaseException) -> None:
    raise error
