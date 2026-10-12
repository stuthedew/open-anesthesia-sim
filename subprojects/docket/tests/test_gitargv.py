"""Tests for `docket.gitargv`: which word of a git call is its command.

One table, read by `docket.vcs` and by the Bash guards under `.claude/hooks/`
(`PL-ZXCN`), so these pin the reading itself; `tests/unit/test_no_prune_guard.py`
and `tests/unit/test_push_check_guard.py` pin that the guards read it.
"""

from __future__ import annotations

import pytest

from docket.gitargv import TAKES_A_WORD, is_git, own_options, subcommand_of

#: A value each option in the table takes, as a session might write it.
VALUES = {
    "-C": "/x",
    "-c": "core.quotePath=false",
    "--config-env": "core.editor=EDITOR",
    "--git-dir": "/x/.git",
    "--work-tree": "/x",
    "--namespace": "ns",
    "--attr-source": "HEAD",
}


def test_every_option_the_table_names_has_a_case_here() -> None:
    """An option added to the table without a case here would go unread by the two below."""
    assert set(VALUES) == TAKES_A_WORD


@pytest.mark.parametrize("option", sorted(TAKES_A_WORD))
def test_a_value_written_as_its_own_word_is_not_the_command(option: str) -> None:
    """`PL-ZXCN`: `git --git-dir /x/.git log` runs `log`, where `vcs` read `/x/.git`."""
    assert subcommand_of([option, VALUES[option], "log", "-1"]) == "log"


@pytest.mark.parametrize("option", sorted(TAKES_A_WORD - {"-C", "-c"}))
def test_a_value_joined_by_an_equals_sign_takes_no_word(option: str) -> None:
    joined = [f"{option}={VALUES[option]}", "log"]

    assert own_options(joined) == ([(option, VALUES[option])], 1)
    assert subcommand_of(joined) == "log"


def test_an_option_taking_no_value_is_stepped_over_alone() -> None:
    args = ["--no-pager", "-c", "a.b=c", "log", "-p"]

    assert own_options(args) == ([("--no-pager", ""), ("-c", "a.b=c")], 3)
    assert subcommand_of(args) == "log"


def test_a_call_naming_no_command_names_none() -> None:
    assert subcommand_of([]) == ""
    assert subcommand_of(["--git-dir"]) == ""
    assert subcommand_of(["-c", "a.b=c"]) == ""


def test_a_tuple_reads_as_a_list_does() -> None:
    """`GitRunner` names each call it counts by a tuple of its argv (`PL-N162`)."""
    assert subcommand_of(("-c", "core.quotePath=false", "log")) == "log"


@pytest.mark.parametrize(
    ("words", "runs"),
    [
        (["git", "fetch"], True),
        (["/usr/bin/git", "fetch", "--prune"], True),
        (["gitk"], False),
        (["./git-lfs", "push"], False),
        ([], False),
    ],
)
def test_git_runs_by_name_or_by_path(words: list[str], runs: bool) -> None:
    assert is_git(words) is runs
