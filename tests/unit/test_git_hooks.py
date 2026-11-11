"""Tests for the git hooks in `.claude/hooks/git/` and `stop_hook_patch.install_git_hooks`.

The hooks refuse what git is about to do, so every test here runs real git in
a scratch clone of a scratch remote and reads the refs afterwards (`PL-82J5`,
`PL-1ZZ0`). A test that only read a hook's verdict would pass for a hook that
said no while git went ahead. Each deleting command is therefore checked two
ways: git fails, and every ref it would have deleted is still there.

The scratch clone's worktree holds links to this repository's `tools/` and
`.claude/`, because the hooks run `tools/pr_body_check.py` and
`.claude/hooks/hook_input.py` from the clone they are installed in. The links
are untracked, so no commit in the clone carries them.

The addresses the email tests use are built when the test runs, so that this
file holds none in its own text and its own push is not refused.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
import stop_hook_patch

REPO = Path(__file__).resolve().parents[2]
SOURCES = REPO / ".claude" / "hooks" / "git"

#: An address no test may publish, made here so this file's text holds none.
PERSON = "a.person" + "@" + "clinic.org"


def _environment(tmp_path: Path, *, agent: bool = True) -> dict[str, str]:
    """This process's environment, with git's identity fixed and the agent marker set or cleared."""
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "Claude",
            "GIT_AUTHOR_EMAIL": "noreply@anthropic.com",
            "GIT_COMMITTER_NAME": "Claude",
            "GIT_COMMITTER_EMAIL": "noreply@anthropic.com",
            "HOOK_BLOCK_LOG": str(tmp_path / "blocks.tsv"),
            "CLAUDE_CODE_SESSION_ID": "session-under-test",
        }
    )
    env.pop("CLAUDECODE", None)
    if agent:
        env["CLAUDECODE"] = "1"
    return env


class Clone:
    """A scratch remote with branches `main`, `b1` and `b2`, and a clone of it with the hooks.

    `b1` and `b2` are deleted on the remote after the clone is made, so the
    clone holds two stale remote-tracking refs, the shape a prune deletes.
    """

    def __init__(self, tmp_path: Path) -> None:
        self.tmp = tmp_path
        self.remote = tmp_path / "remote.git"
        self.path = tmp_path / "clone"
        env = _environment(tmp_path, agent=False)
        seed = tmp_path / "seed"
        for args in (
            ["git", "init", "-q", "--bare", "-b", "main", str(self.remote)],
            ["git", "init", "-q", "-b", "main", str(seed)],
            ["git", "-C", str(seed), "commit", "-q", "--allow-empty", "-m", "first"],
            ["git", "-C", str(seed), "push", "-q", str(self.remote), "main", "main:b1", "main:b2"],
            ["git", "clone", "-q", str(self.remote), str(self.path)],
            ["git", "-C", str(self.remote), "branch", "-q", "-D", "b1", "b2"],
        ):
            subprocess.run(args, check=True, env=env, capture_output=True)
        (self.path / "tools").symlink_to(REPO / "tools")
        (self.path / ".claude").symlink_to(REPO / ".claude")
        assert stop_hook_patch.install_git_hooks(self.git_runner(), self.path) == ""

    def git_runner(self) -> Callable[[list[str]], tuple[int, str]]:
        def run(args: list[str]) -> tuple[int, str]:
            done = subprocess.run(
                ["git", *args], cwd=self.path, capture_output=True, text=True, check=False
            )
            return done.returncode, done.stdout

        return run

    def sh(
        self, command: str, *, agent: bool = True, stdin: str = ""
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["sh", "-c", command],
            cwd=self.path,
            env=_environment(self.tmp, agent=agent),
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )

    def refs(self) -> str:
        return self.sh("git for-each-ref --format='%(refname) %(objectname)'").stdout

    def remote_refs(self) -> str:
        return self.sh(f"git ls-remote {self.remote}").stdout


@pytest.fixture
def clone(tmp_path: Path) -> Clone:
    return Clone(tmp_path)


# --- deleting a remote-tracking ref ---------------------------------------------

#: Each spelling the review of 2026-11-03 found deleting a remote-tracking ref,
#: with those the retired Bash guard read by name. The hook refuses them by what git
#: is about to do, so a new spelling needs no new row to be refused.
DELETING = (
    "git fetch --prune",
    "git fetch -p origin",
    "git -c fetch.prune=true fetch",
    "git config fetch.prune true && git fetch",
    "git config remote.origin.prune true && git fetch origin",
    "git pull --prune",
    "git remote update --prune",
    "git remote prune origin",
    "git branch -dr origin/b1",
    "git branch -d -r origin/b1 origin/b2",
    "git for-each-ref --format='%(refname:short)' refs/remotes/origin/b* | xargs git branch -dr",
    "git update-ref -d refs/remotes/origin/b1",
    "printf 'delete refs/remotes/origin/b1\\n' | git update-ref --stdin",
    "git remote remove origin",
    "git remote rm origin",
    "git remote rename origin upstream",
    "git remote set-head origin --delete",
)


@pytest.mark.parametrize("command", DELETING)
def test_a_command_that_deletes_a_remote_tracking_ref_is_refused_with_every_ref_kept(
    clone: Clone, command: str
) -> None:
    before = clone.refs()
    assert "refs/remotes/origin/b1" in before

    done = clone.sh(command)

    assert done.returncode != 0, done.stderr
    assert "Refused: this command would delete these remote-tracking refs" in done.stderr
    assert clone.refs() == before


def test_the_refusal_names_the_refs_and_answers_what_the_caller_wanted(clone: Clone) -> None:
    done = clone.sh("git fetch --prune")

    assert "refs/remotes/origin/b1" in done.stderr
    assert "refs/remotes/origin/b2" in done.stderr
    assert "bin/docket stranded" in done.stderr
    assert "git fetch origin" in done.stderr
    assert "git checkout -B <branch> origin/main" in done.stderr
    assert "git push -u origin <branch>" in done.stderr


def test_a_refusal_is_logged_with_the_session_that_made_it(clone: Clone, tmp_path: Path) -> None:
    clone.sh("git branch -dr origin/b1")

    line = (tmp_path / "blocks.tsv").read_text(encoding="utf-8").splitlines()[-1]
    assert line.split("\t")[1:] == ["session-under-test", "git-ref-guard", "delete-tracking-ref"]


#: What a session does in a clone every day, which the hook must leave alone.
ROUTINE = (
    "git commit -q --allow-empty -m second",
    "git checkout -q -b topic && git checkout -q main && git branch -q -D topic",
    "git tag t && git tag -d t",
    "git fetch -q origin",
    "git fetch -q origin main",
    "git pack-refs --all",
    "git gc -q",
    "git remote set-url origin ../remote.git",
    "git checkout -q -b work && git commit -q --allow-empty -m w && git push -q -u origin work",
    "git stash list && git log --oneline -1",
)


@pytest.mark.parametrize("command", ROUTINE)
def test_routine_git_is_untouched(clone: Clone, command: str) -> None:
    done = clone.sh(command)

    assert done.returncode == 0, done.stderr
    assert "Refused" not in done.stderr


def test_the_restart_recipe_the_refusal_prints_replaces_the_stale_ref(clone: Clone) -> None:
    """The recipe in the hook's message moves a stale ref by a push, which deletes nothing."""
    done = clone.sh(
        "git fetch -q origin main && git checkout -q -B b1 origin/main "
        "&& git commit -q --allow-empty -m restarted && git push -q -u origin b1"
    )

    assert done.returncode == 0, done.stderr
    head = clone.sh("git rev-parse HEAD").stdout
    assert clone.sh("git rev-parse refs/remotes/origin/b1").stdout == head


def test_the_recipe_forces_nothing_onto_a_branch_the_remote_still_holds(clone: Clone) -> None:
    """A commit pushed after the merge leaves the old branch on the remote.

    The recipe's push is then refused, and the refusal message names no forced
    push, because GitHub refuses one on every branch (`PL-39Y1`). Once the
    project owner has deleted the old branch, the same push lands and moves the
    stale ref.
    """
    clone.sh(
        "git checkout -q -b b3 && git commit -q --allow-empty -m left-behind "
        "&& git push -q -u origin b3 && git checkout -q main"
    )
    left_behind = clone.sh("git rev-parse refs/remotes/origin/b3").stdout

    restarted = clone.sh(
        "git fetch -q origin main && git checkout -q -B b3 origin/main "
        "&& git commit -q --allow-empty -m carried"
    )
    assert restarted.returncode == 0, restarted.stderr
    assert clone.sh("git push -q -u origin b3").returncode != 0
    assert clone.sh("git ls-remote origin refs/heads/b3").stdout.split()[0] == left_behind.strip()
    said = " ".join(clone.sh("git branch -dr origin/b3").stderr.split())
    assert "--force" not in said
    assert "Never force that push" in said
    assert "ask the project owner to archive and delete the old branch" in said

    subprocess.run(
        ["git", "-C", str(clone.remote), "branch", "-q", "-D", "b3"],
        check=True,
        env=_environment(clone.tmp, agent=False),
        capture_output=True,
    )
    done = clone.sh("git push -q -u origin b3")

    assert done.returncode == 0, done.stderr
    head = clone.sh("git rev-parse HEAD").stdout
    assert clone.sh("git rev-parse refs/remotes/origin/b3").stdout == head


def test_the_owners_own_git_is_left_alone(clone: Clone) -> None:
    """Without `CLAUDECODE`, no agent ran the command, and the hook says nothing."""
    done = clone.sh("git branch -dr origin/b1", agent=False)

    assert done.returncode == 0, done.stderr
    assert "refs/remotes/origin/b1" not in clone.refs()


# --- a push that deletes a branch on the remote --------------------------------

#: Each push that deletes a branch on the remote. `--mirror` is the one whose
#: deletions git leaves out of the list it hands the hook, so it is refused by
#: the remote-tracking refs it would send instead.
DELETING_PUSHES = (
    "git push origin --delete other",
    "git push -d origin other",
    "git push origin :other",
    "git push origin :refs/heads/other",
    "git push --prune origin 'refs/heads/*:refs/heads/*'",
    "git push --all --prune origin",
    "git push --mirror origin",
    "git config remote.origin.mirror true && git push origin",
)


@pytest.mark.parametrize("command", DELETING_PUSHES)
def test_a_push_that_deletes_a_branch_on_the_remote_is_refused_and_sends_nothing(
    clone: Clone, command: str
) -> None:
    clone.sh(
        "git checkout -q -b other && git push -q origin other "
        "&& git checkout -q main && git branch -q -D other"
    )
    before = clone.remote_refs()
    assert "refs/heads/other" in before

    done = clone.sh(command)

    assert done.returncode != 0, done.stderr
    assert "Refused: this push would change these refs on the remote" in done.stderr
    assert clone.remote_refs() == before


def test_a_push_the_owner_runs_is_left_alone(clone: Clone) -> None:
    clone.sh("git checkout -q -b other && git push -q origin other")

    done = clone.sh("git push -q origin --delete other", agent=False)

    assert done.returncode == 0, done.stderr
    assert "refs/heads/other" not in clone.remote_refs()


# --- an email address in the commits a push publishes ----------------------------


def test_an_address_in_a_commit_message_is_refused_and_nothing_is_sent(clone: Clone) -> None:
    clone.sh("git checkout -q -b work")
    clone.sh(f"git commit -q --allow-empty -m 'Asked by {PERSON}.'")

    done = clone.sh("git push -q -u origin work")

    assert done.returncode != 0
    assert f"`{PERSON}`" in done.stderr
    assert "its message" in done.stderr
    assert "refs/heads/work" not in clone.remote_refs()


def test_a_work_in_progress_push_still_screens_for_an_address(clone: Clone) -> None:
    """The push guard's work-in-progress exemption leaves this hook to run (`PL-5R11`)."""
    clone.sh("git checkout -q -b work")
    clone.sh(f"git commit -q --allow-empty -m 'Asked by {PERSON}.'")

    done = clone.sh("PUSH_CHECKS=skip git push -q -u origin work")

    assert done.returncode != 0
    assert f"`{PERSON}`" in done.stderr
    assert "refs/heads/work" not in clone.remote_refs()


def test_an_address_in_a_line_a_commit_adds_is_refused_with_its_file(clone: Clone) -> None:
    clone.sh("git checkout -q -b work")
    (clone.path / "notes.md").write_text(f"Write to {PERSON}.\n", encoding="utf-8")
    clone.sh("git add notes.md && git commit -q -m notes")

    done = clone.sh("git push -q -u origin work")

    assert done.returncode != 0
    assert "lines it adds to `notes.md`" in done.stderr


def test_an_address_as_a_commits_author_is_refused(clone: Clone) -> None:
    clone.sh("git checkout -q -b work")
    clone.sh(f"GIT_AUTHOR_EMAIL={PERSON} git commit -q --allow-empty -m plain")

    done = clone.sh("git push -q -u origin work")

    assert done.returncode != 0
    assert "its author or committer" in done.stderr


def test_a_refused_push_is_logged_under_the_email_guard(clone: Clone, tmp_path: Path) -> None:
    clone.sh("git checkout -q -b work")
    clone.sh(f"git commit -q --allow-empty -m 'Asked by {PERSON}.'")
    clone.sh("git push -q -u origin work")

    line = (tmp_path / "blocks.tsv").read_text(encoding="utf-8").splitlines()[-1]
    assert line.split("\t")[1:] == [
        "session-under-test",
        "pr-body-email-guard",
        "email-address-push",
    ]


def test_addresses_that_are_nobodys_own_are_pushed(clone: Clone) -> None:
    clone.sh("git checkout -q -b work")
    (clone.path / "test_x.py").write_text(
        'ADDRESS = "t@example.com"\nREMOTE = "git@github.com:o/r"\n', encoding="utf-8"
    )
    clone.sh(
        "git add test_x.py && git commit -q -m 'Co-authored-by: Claude <noreply@anthropic.com>'"
    )

    done = clone.sh("git push -q -u origin work")

    assert done.returncode == 0, done.stderr
    assert "refs/heads/work" in clone.remote_refs()


def test_only_the_commits_no_remote_ref_holds_are_read(clone: Clone) -> None:
    """A commit already on the remote was published before this push, so it is not read again."""
    clone.sh("git checkout -q -b work")
    clone.sh(f"git commit -q --allow-empty -m 'Asked by {PERSON}.'")
    clone.sh("git push -q -u origin work", agent=False)
    clone.sh("git commit -q --allow-empty -m clean")

    done = clone.sh("git push -q origin work")

    assert done.returncode == 0, done.stderr


def test_a_push_with_no_screen_in_its_checkout_goes_ahead_with_a_warning(clone: Clone) -> None:
    (clone.path / "tools").unlink()
    clone.sh("git checkout -q -b work")
    clone.sh(f"git commit -q --allow-empty -m 'Asked by {PERSON}.'")

    done = clone.sh("git push -q -u origin work")

    assert done.returncode == 0, done.stderr
    assert "was not screened for email addresses" in done.stderr


# --- the installer --------------------------------------------------------------


def test_the_installed_hooks_are_the_sources_and_executable(clone: Clone) -> None:
    for name in stop_hook_patch.GIT_HOOKS:
        installed = clone.path / ".git" / "hooks" / name
        assert installed.read_text(encoding="utf-8") == (SOURCES / name).read_text(encoding="utf-8")
        assert os.access(installed, os.X_OK)


def test_every_source_opens_with_the_mark_the_installer_knows_it_by() -> None:
    for name in stop_hook_patch.GIT_HOOKS:
        lines = (SOURCES / name).read_text(encoding="utf-8").split("\n")
        assert lines[0] == "#!/bin/sh"
        assert stop_hook_patch.GIT_HOOK_MARK in lines[1]


def test_an_outdated_copy_of_our_own_hook_is_replaced(clone: Clone) -> None:
    installed = clone.path / ".git" / "hooks" / "pre-push"
    installed.write_text(
        "#!/bin/sh\n# " + stop_hook_patch.GIT_HOOK_MARK + ": old\nexit 0\n", encoding="utf-8"
    )

    assert stop_hook_patch.install_git_hooks(clone.git_runner(), clone.path) == ""
    assert installed.read_text(encoding="utf-8") == (SOURCES / "pre-push").read_text(
        encoding="utf-8"
    )


def test_a_hook_somebody_else_wrote_is_kept_and_reported(clone: Clone) -> None:
    installed = clone.path / ".git" / "hooks" / "pre-push"
    installed.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")

    reason = stop_hook_patch.install_git_hooks(clone.git_runner(), clone.path)

    assert "holds a hook of its own" in reason
    assert installed.read_text(encoding="utf-8") == "#!/bin/sh\necho mine\n"


def test_a_clone_git_cannot_name_reports_why(tmp_path: Path) -> None:
    def run(args: list[str]) -> tuple[int, str]:
        return 128, ""

    assert stop_hook_patch.install_git_hooks(run, tmp_path) != ""


def test_a_moved_hooks_directory_is_where_the_hooks_go(clone: Clone) -> None:
    """`core.hooksPath` moves the directory git reads, so the installer follows it."""
    clone.sh("git config core.hooksPath shared-hooks")

    assert stop_hook_patch.install_git_hooks(clone.git_runner(), clone.path) == ""
    assert (clone.path / "shared-hooks" / "reference-transaction").exists()


@pytest.mark.parametrize("name", stop_hook_patch.GIT_HOOKS)
def test_each_hook_parses_under_dash(name: str) -> None:
    """The hooks run under `/bin/sh`, which is `dash` on Debian and Ubuntu."""
    done = subprocess.run(
        ["sh", "-n", str(SOURCES / name)], capture_output=True, text=True, check=False
    )

    assert done.returncode == 0, done.stderr
