"""The suite's own git configuration, which every scratch repository inherits.

The repository root's `conftest.py` points `GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_SYSTEM` at `/dev/null` so that the repositories these tests build
read no configuration from the machine running them. It is pinned from here
rather than from `tests/`, because this is the tree that builds one per test.

Nothing else in the suite fails when that stops being true: every test still
passes, three times slower, and the next thing a developer's `~/.gitconfig`
turns on decides whether they pass at all. These two tests are what makes its
removal visible instead of silent.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

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
