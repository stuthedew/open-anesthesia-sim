"""Tests for `.claude/hooks/push-check-guard.sh`, the checks run before a push (`PL-PLSJ`).

The hook runs `tools/doc_check.py`, `tools/branch_id_check.py` and `bin/docket
check --verify` (`PL-S1BG`) from the tree a `git push` sends, and denies the
push while any fails. Each test builds a scratch repository whose three scripts
are stubs printing a known report, and points `CLAUDE_PROJECT_DIR` at it, so
what is pinned is the hook's own rule: which commands are pushes, which tree is
checked, what a refusal shows, and that every error path lets the push through.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "push-check-guard.sh"

PASS = 'print("branch-id: visible in flight - PL-K7QX")'
DOC_ERROR = "docs/items/PL-K7QX-a.md: cites `start.md`, which does not exist"
DOC_FAILS = (
    "import sys\n"
    'print("documentation: 1 error, 1 advisory")\n'
    'print("resident instructions: a size summary nobody needs at push time")\n'
    'print("")\n'
    'print("Errors (the documentation is wrong; fix before committing):")\n'
    f'print("  {DOC_ERROR}")\n'
    'print("")\n'
    'print("Advisories (judgment needed):")\n'
    'print("  an advisory nobody needs at push time")\n'
    "sys.exit(1)"
)
BRANCH_FAILS = (
    "import sys\n"
    'print("branch-id: 2 commit(s) ahead of origin/main, and no item id names any of them.",'
    " file=sys.stderr)\n"
    "sys.exit(1)"
)
# `bin/docket` is a bash wrapper, so its stubs are bash.
STORE_PASS = 'echo "docket: 1 open, 0 errors, 0 advisories"'
STORE_ERROR = "PL-K7QX is open but its `verify:` command already passes (1 of 1 checked)"
STORE_FAILS = (
    "cat <<'EOF'\n"
    "docket: 1 open, 1 errors, 1 advisories\n"
    "  verify: a cost line nobody needs at push time\n"
    "\n"
    "Errors (the store is wrong; fix before committing):\n"
    f"  {STORE_ERROR}\n"
    "\n"
    "Grooming advisories (judgment needed; nothing is failing):\n"
    "  a grooming advisory nobody needs at push time\n"
    "EOF\n"
    "exit 1"
)


def _git(where: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-C", str(where), *args],
        check=True,
        capture_output=True,
    )


def _stub(tree: Path, doc: str = PASS, branch: str = PASS, store: str = STORE_PASS) -> None:
    (tree / "tools").mkdir(exist_ok=True)
    (tree / "tools" / "doc_check.py").write_text(doc + "\n")
    (tree / "tools" / "branch_id_check.py").write_text(branch + "\n")
    (tree / "bin").mkdir(exist_ok=True)
    (tree / "bin" / "docket").write_text(store + "\n")


@pytest.fixture
def project(tmp_path: Path) -> Path:
    tree = tmp_path / "project"
    tree.mkdir()
    _git(tree, "init", "-q")
    _stub(tree)
    _git(tree, "add", "-A")
    _git(tree, "commit", "-q", "-m", "init")
    return tree


def _decision(command: str, *, cwd: Path, project: Path) -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one Bash call, or `None` if it let the call through."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)})
    result = subprocess.run(
        ["bash", str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)},
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


def test_a_push_whose_doc_check_fails_is_refused(project: Path) -> None:
    _stub(project, doc=DOC_FAILS)
    decision = _decision("git push -u origin claude/x", cwd=project, project=project)
    assert decision is not None
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    assert "`doc_check` failed (`python3 tools/doc_check.py check` re-runs it)" in reason
    assert DOC_ERROR in reason
    # The bypass is offered for the one push CI never sees.
    assert "git push --no-verify" in reason


def test_a_push_whose_branch_id_check_fails_is_refused(project: Path) -> None:
    _stub(project, branch=BRANCH_FAILS)
    decision = _decision("git push", cwd=project, project=project)
    assert decision is not None
    reason = decision["permissionDecisionReason"]
    assert "`branch_id_check` failed" in reason
    assert "no item id names any of them" in reason
    assert "doc_check" not in reason


def test_a_push_whose_store_check_fails_is_refused(project: Path) -> None:
    _stub(project, store=STORE_FAILS)
    decision = _decision("git push", cwd=project, project=project)
    assert decision is not None
    reason = decision["permissionDecisionReason"]
    # The re-run is `make check`'s own store check, reading the base without a fetch.
    assert (
        "`docket check` failed "
        "(`bin/docket check --verify --verify-base origin/main --no-fetch` re-runs it)"
    ) in reason
    assert STORE_ERROR in reason
    assert "a cost line nobody needs at push time" not in reason
    assert "a grooming advisory nobody needs at push time" not in reason
    assert "doc_check" not in reason


def test_a_push_every_check_passes_goes_through(project: Path) -> None:
    assert _decision("git push -u origin claude/x", cwd=project, project=project) is None


PUSHES = (
    "git push",
    "git push origin HEAD",
    "git push -uf origin claude/x",
    "timeout 60 git push -u origin claude/x",
    "git add -A && git commit -m x && git push",
    "(git push origin claude/x)",
    "git -c push.default=current push",
    # A value that looks like a refspec or a flag is still only a value.
    "git push -o :x origin claude/x",
    "git push --push-option -n origin claude/x",
    "git push --repo=origin",
)


@pytest.mark.parametrize("command", PUSHES)
def test_every_push_that_sends_is_checked(project: Path, command: str) -> None:
    _stub(project, doc=DOC_FAILS)
    decision = _decision(command, cwd=project, project=project)
    assert decision is not None, command
    assert decision["permissionDecision"] == "deny"


NOT_SENDING = (
    'git commit -m "note: git push later"',
    "echo git push",
    "cat <<'EOF'\ngit push origin claude/x\nEOF",
    "# git push\ngit status",
    "git stash push -m wip",
    "git log --grep push",
    "git push --delete origin claude/x",
    "git push origin --delete claude/x",
    "git push -d origin claude/x",
    "git push origin :claude/x",
    "git push origin -- :claude/x",
    "git push --dry-run origin claude/x",
    "git push -n origin claude/x",
    "git push --no-verify -u origin claude/x",
)


@pytest.mark.parametrize("command", NOT_SENDING)
def test_a_call_that_sends_nothing_is_untouched(project: Path, command: str) -> None:
    _stub(project, doc=DOC_FAILS)
    assert _decision(command, cwd=project, project=project) is None, command


def test_the_refusal_shows_the_summary_and_the_errors_alone(project: Path) -> None:
    _stub(project, doc=DOC_FAILS)
    decision = _decision("git push", cwd=project, project=project)
    assert decision is not None
    reason = decision["permissionDecisionReason"]
    assert "documentation: 1 error, 1 advisory" in reason
    assert DOC_ERROR in reason
    assert "a size summary nobody needs at push time" not in reason
    assert "an advisory nobody needs at push time" not in reason


def test_a_long_report_is_cut(project: Path) -> None:
    lines = "\n".join(f'print("  error {n}")' for n in range(100))
    _stub(project, doc=f"import sys\n{lines}\nsys.exit(1)")
    decision = _decision("git push", cwd=project, project=project)
    assert decision is not None
    reason = decision["permissionDecisionReason"]
    assert "error 39" in reason
    assert "error 40" not in reason
    assert "60 more lines cut" in reason


@pytest.mark.parametrize(
    "doc",
    ['raise RuntimeError("the check itself broke")', "import sys\nsys.exit(2)"],
    ids=["traceback", "other-exit"],
)
def test_a_check_that_breaks_lets_the_push_through(project: Path, doc: str) -> None:
    _stub(project, doc=doc)
    assert _decision("git push", cwd=project, project=project) is None


def test_a_push_in_another_repository_is_not_checked(project: Path, tmp_path: Path) -> None:
    _stub(project, doc=DOC_FAILS)
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    _stub(other, doc=DOC_FAILS)
    assert _decision("git push", cwd=other, project=project) is None
    assert _decision(f"git -C {other} push", cwd=project, project=project) is None
    assert _decision(f"cd {other} && git push", cwd=project, project=project) is None


def test_a_push_moved_into_the_project_is_checked(project: Path, tmp_path: Path) -> None:
    _stub(project, doc=DOC_FAILS)
    assert _decision(f"cd {project} && git push", cwd=tmp_path, project=project) is not None
    assert _decision(f"git -C {project} push", cwd=tmp_path, project=project) is not None


def test_a_directory_the_shell_builds_is_not_followed(project: Path) -> None:
    _stub(project, doc=DOC_FAILS)
    assert _decision('cd "$WORKTREE" && git push', cwd=project, project=project) is None


def test_a_linked_worktree_is_checked_from_its_own_tree(project: Path, tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    _git(project, "worktree", "add", "-q", "--detach", str(worktree))
    _stub(worktree, doc=DOC_FAILS)
    # The project's own tree passes; the worktree's fails, and is the one pushed.
    assert _decision("git push", cwd=project, project=project) is None
    assert _decision("git push", cwd=worktree, project=project) is not None
