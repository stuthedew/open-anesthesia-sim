"""Refuse a `git push` whose tree fails a check CI would fail, as a `PreToolUse` hook on Bash.

Before a push sends this repository's tree, the hook runs the checks that most
often turn a pull request red on something `make check` already refuses
locally. It denies the push while any of them fails (`PL-PLSJ`, `PL-S1BG`,
`PL-3JG7`).

**Why these three and why here.** `PL-JYJJ`'s census counted 391 red runs; 32
were `doc_check` and 8 `branch_id_check`, rising week on week, and every one
in a 15-log sample was the branch's own text - an item quoting `start.md` by
bare name, a path that does not exist, a branch no item id names. `PL-1BGP`
then sorted its 43 store-rule runs: 40 were the branch's own, and `make
check`'s `bin/docket check --verify --verify-base origin/main` refuses all 40.
So each went out without `make check`, most often on the capture path, which
is kept cheap on purpose. Run side by side the three take about as long as
`doc_check` alone, 11 s, and cost no tokens; a red run costs a session a fix
cycle. The store check compares against the default base `docket.vcs` names -
`origin/main` here, the ref `make check` spells - as of the last fetch, and
never fetches, so a push never waits on the network. The other 2 of those 43 runs
were `main`'s, on one day and from one cause `tools/pr_record_check.py` has
refused since; on such a day this refuses a push the branch did not cause,
naming the item on `main` that is wrong.

**Four more since `PL-3JG7`**, from `PL-2D1S`'s reading of every red run on
the pull requests of items closed from 2026-09-21 to 2026-10-25. Of the 32
that failed a check `make check` also runs, 26 were on branches where this
hook runs, and four checks it did not run were behind 22 of those 26:
`tools/workflow_paths_check.py` (6), `tools/type_ignore_check.py` (9, seven of
them one branch pushing again past the same failure),
`tools/fixture_id_check.py` (4) and `tests/unit/test_line_splits.py` (3).
They cost the push no time. In a four-CPU session container on 2026-10-26,
the first three took 61 s side by side, bounded by `doc_check` alone at 59 s,
and all seven took 61 s. The four run under the tree's `.venv/bin/python`,
the interpreter `make check`'s `uv run` uses, because `fixture_id_check`
parses `src/`, whose Python 3.14 syntax the bare `python3` running this hook
need not read.

**What counts as a push**: a git call whose command, after git's own options,
is `push`, read through `shell_split.commands` as the three sibling guards
read theirs, so a push in a subshell, after `&&` or behind `timeout` counts
and one in a heredoc's text, a comment or a quoted message does not - though
one in a `$( )` in an unquoted heredoc's body runs, and counts (`PL-P95F`). A
push that sends nothing is skipped: `--delete`, `-d`, a `:<branch>` refspec,
`--dry-run` and `-n`. `--no-verify` is the one exemption, which the refusal
offers for a work-in-progress push to a branch with no pull request open,
since `quality.yml` runs no CI on one.

**Which tree**: the push's own - the payload's `cwd`, moved by any `cd`
before the push and by the push's `-C` options - and only where git's common
directory there is this project's, so a linked worktree is checked and
another repository is not. Like `make check`, the checks read the working
tree, so an uncommitted edit counts. Each runs from that tree's own copy of
its script, and is skipped in a tree without one. The four that need the
project's interpreter are skipped in a tree without `.venv/bin/python` too.
A push sends an uncommitted edit only once it is committed, so where a check
that reads the tree fails in a tree `git status` shows changes in, the
refusal says so and how to settle which tree was meant. `branch_id_check`
reads the history, where no uncommitted edit can be the cause (`PL-GR0L`).

**Known gaps**, each costing a push CI would then catch, never a false
refusal of a clean tree: in `git commit ... && git push` the hook runs before
the commit, so `branch_id_check` reads the history without it; a push of a
branch other than the one checked out is read as the checked-out one; and a
`cd` or `-C` built from a variable, `--git-dir` or `--work-tree`, and a push
inside `bash -c "..."` are not followed, so they are let through unchecked.

**After a push it lets through**, it names the `pull-request` skill beside
the push's result, as `additionalContext`. That skill's procedure applies
from this moment: open the pull request, ask `bin/docket arm`, read the body
back. `PL-SN2Z` found that a moment arriving in the middle of a task needs a
hook to name it (`PL-S2NL`). A push of another repository, or one that sends
nothing, gets no note.

Fails open in every error path - no python3, an unreadable payload, a check
that crashes (a traceback, or an exit other than 1) or runs past its
deadline - because a guard that blocks a correct push costs more than the red
run it saves. The hook is given 120 s in `.claude/settings.json`; the checks
get 100 s of it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

import hook_input
import shell_split

# isort: split
# Which word is the git command, past the options git reads as its own and
# their values, is read by `docket.gitargv`, the table `docket.vcs` reads too;
# `shell_split` has put the `src` of docket on the path (`PL-ZXCN`).
from docket.gitargv import is_git, own_options

if TYPE_CHECKING:
    from docket.vcs import GitRunner

# From `git push -h` (git 2.43): the options taking the next word as their value
# where no `=` joins one, the letter among them, and what sends nothing.
PUSH_VALUED = frozenset(
    ("--repo", "--recurse-submodules", "--receive-pack", "--exec", "--push-option")
)
SENDS_NOTHING = frozenset(("--delete", "--dry-run", "--no-verify"))
READS_THE_TREE = frozenset(
    (
        "doc_check",
        "docket check",
        "workflow_paths_check",
        "fixture_id_check",
        "type_ignore_check",
        "line-split tests",
    )
)
# The interpreter of the project, relative to the top of the tree: the one
# that the `uv run` steps of `make check` run under (`PL-3JG7`).
PROJECT_PYTHON = ".venv/bin/python"
# How long the checks may run, in seconds, before the guard stops them and lets
# the push go with a note naming them. `doc_check` alone took 38 to 101 s on
# 2026-11-03 (`PL-DST3`). The limit is kept short because the session waits on
# it at every push. A test shortens it through `PUSH_CHECK_GUARD_DEADLINE`.
DEADLINE = 100
SKILL_NOTE = (
    "This was a push of this repository. Opening, arming, updating or merging "
    "its pull request follows .claude/skills/pull-request/SKILL.md, the "
    "pull-request skill: read it once if this session has not. Ask "
    "`bin/docket arm` before arming, and again before each later push while a "
    "pull request is open (`PL-S2NL`)."
)
EXCERPT_LINES = 40


def checks(base: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Each check as a session types it to re-run it, the store check comparing against `base`.

    `base` is the default base `docket.vcs` answers for the tree, `origin/main`
    in this repository, as `make check` spells it (`PL-ZXCN`). `launch` says
    which interpreter runs each one.
    """
    return (
        ("doc_check", ("python3", "tools/doc_check.py", "check")),
        ("branch_id_check", ("python3", "tools/branch_id_check.py")),
        ("docket check", ("bin/docket", "check", "--verify", "--verify-base", base, "--no-fetch")),
        ("workflow_paths_check", (PROJECT_PYTHON, "tools/workflow_paths_check.py")),
        ("fixture_id_check", (PROJECT_PYTHON, "tools/fixture_id_check.py")),
        ("type_ignore_check", (PROJECT_PYTHON, "tools/type_ignore_check.py")),
        (
            "line-split tests",
            (
                PROJECT_PYTHON,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/unit/test_line_splits.py",
            ),
        ),
    )


def launch(top: str, argv: tuple[str, ...]) -> list[str] | None:
    """The command that runs `argv` in `top`, or None where `top` lacks a file it needs.

    `python3` runs as this interpreter, and `bin/docket`, a bash wrapper, runs
    under bash. A check under the project interpreter needs that interpreter
    in the tree as well as the file it runs, which is its last word.
    """
    needed: tuple[str, ...]
    if argv[0] == "python3":
        needed, command = (argv[1],), [sys.executable, *argv[1:]]
    elif argv[0] == "bin/docket":
        needed, command = (argv[0],), ["bash", *argv]
    else:
        needed, command = (argv[0], argv[-1]), [os.path.join(top, argv[0]), *argv[1:]]
    if all(os.path.isfile(os.path.join(top, path)) for path in needed):
        return command
    return None


def sends(words: list[str]) -> bool:
    """Whether a git call is a push that sends commits: not a delete, a dry run or exempt."""
    args = words[1:]
    _, at = own_options(args)
    if args[at : at + 1] != ["push"]:
        return False
    rest = iter(args[at + 1 :])
    for word in rest:
        if word == "--":
            return not any(ref.lstrip("+").startswith(":") for ref in rest)
        option, equals, _ = word.partition("=")
        if option in SENDS_NOTHING:
            return False
        if word.startswith("--"):
            if option in PUSH_VALUED and not equals:
                next(rest, None)
        elif word.startswith("-") and word != "-":
            for position, letter in enumerate(word[1:], 2):
                if letter in "dn":
                    return False
                if letter == "o":
                    # Its value is the rest of the word, or the next word if none is left.
                    if position == len(word):
                        next(rest, None)
                    break
        elif word.lstrip("+").startswith(":"):
            return False
    return True


def moved(where: str | None, target: str) -> str | None:
    """`where` after a change of directory to `target`, or None where the shell builds it."""
    if where is None or target == "-" or shell_split.EXPANDS.search(target):
        return None
    return os.path.join(where, os.path.expanduser(target))


def directory(words: list[str], where: str | None) -> str | None:
    """Where a git call runs: `where` moved by each `-C`, or None where git is pointed elsewhere."""
    for option, value in own_options(words[1:])[0]:
        if option in ("--git-dir", "--work-tree"):
            return None
        if option == "-C":
            where = moved(where, value)
    return where


def git(run: GitRunner, where: str, *args: str) -> str | None:
    """What git prints for `args` run in `where`, or None where it does not answer.

    Read through the runner of `docket.vcs`, which decodes what git prints as
    git wrote it, so a raw carriage return in a directory name stays in the
    path, where text mode made it a line end (`PL-0R4M`, `PL-ZXCN`).
    """
    return run(list(args), Path(where)).strip() or None


def common_directory(run: GitRunner, where: str) -> str | None:
    """Git's common directory for `where` as an absolute path, or None where git gives none."""
    found = git(run, where, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return os.path.realpath(found) if found else None


def uncommitted(run: GitRunner, top: str) -> int:
    """How many paths `git status --short` lists in `top`, or 0 where git cannot say."""
    from docket.lines import split_lines

    listed = git(run, top, "status", "--porcelain")
    return len(split_lines(listed)) if listed else 0


def excerpt(text: str) -> str:
    """The report a refusal shows: its first line and its errors, cut to `EXCERPT_LINES`.

    The advisories after the errors are left out.
    """
    # Imported here, as `docket.vcs` is in `decide`: only a push pays for it.
    from docket.lines import split_lines

    report = split_lines(text)
    errors = [at for at, line in enumerate(report) if line.startswith("Errors (")]
    if errors:
        report = report[:1] + [""] + report[errors[0] :]
    lines: list[str] = []
    for line in report:
        if line.startswith(("Advisories (", "Grooming advisories (", "Not checked (")):
            break
        lines.append(line)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) > EXCERPT_LINES:
        cut = len(lines) - EXCERPT_LINES
        lines = lines[:EXCERPT_LINES] + [f"... {cut} more lines cut"]
    return "\n".join(lines)


def unfinished_note(unfinished: list[str]) -> str:
    """The note naming each check that gave no answer, or "" where every one did.

    A check stopped at the deadline, or one that crashed, neither passed nor
    failed. Letting the push go without saying so would read to the session
    as a push whose checks passed (`PL-DST3`, `PL-9KSJ`).
    """
    if not unfinished:
        return ""
    return (
        "These checks gave no answer, so this push was not checked against them: "
        + ", ".join(unfinished)
        + ". Run each by hand before treating the push as checked."
    )


def push_targets(command: str, where: str) -> list[str | None]:
    """The directory each push in `command` runs in, or None where it cannot be followed."""
    targets: list[str | None] = []
    cwd: str | None = where
    for words in shell_split.commands(command):
        if words[0] == "cd":
            cwd = moved(cwd, words[-1] if len(words) > 1 else "~")
        elif is_git(words) and sends(words):
            targets.append(directory(words, cwd))
    return targets


def decide(payload: str) -> str:
    """The refusal of a push in `payload` whose tree fails a check, the skill note, or ""."""
    call = hook_input.bash_call(payload)
    if call is None:
        return ""
    targets = push_targets(call.command, call.cwd or os.getcwd())
    if not targets:
        return ""

    # A push is being sent, so the reads of `docket.vcs` are worth their import,
    # which a Bash call that pushes nothing never pays.
    from docket import vcs

    run = vcs.GitRunner()
    project = str(hook_input.project_root())
    ours = common_directory(run, project)
    trees: list[str] = []
    for target in targets:
        if ours is None or target is None or common_directory(run, target) != ours:
            continue
        top = git(run, target, "rev-parse", "--show-toplevel")
        if top and top not in trees:
            trees.append(top)

    running: list[tuple[str, str, tuple[str, ...], subprocess.Popen[str]]] = []
    for top in trees:
        for name, argv in checks(vcs.default_base(Path(top), runner=run)):
            command = launch(top, argv)
            if command is not None:
                process = subprocess.Popen(
                    command, cwd=top, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                running.append((top, name, argv, process))

    limit = float(os.environ.get("PUSH_CHECK_GUARD_DEADLINE") or DEADLINE)
    deadline = time.monotonic() + limit
    refusals: list[str] = []
    unfinished: list[str] = []
    readers: set[str] = set()
    read_trees: set[str] = set()
    for top, name, argv, process in running:
        try:
            out, err = process.communicate(timeout=max(0.0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            unfinished.append(f"`{name}` (stopped at the {limit:g}-second limit)")
            continue
        crashed = "Traceback (most recent call last)" in err
        if crashed or process.returncode not in (0, 1):
            last = err.strip().rpartition("\n")[2]
            unfinished.append(
                f"`{name}` (exited {process.returncode}{': ' + last if last else ''})"
            )
            continue
        if process.returncode == 1:
            rerun = " ".join(argv)
            report = "\n".join(part for part in (out.rstrip(), err.rstrip()) if part)
            refusals.append(f"`{name}` failed (`{rerun}` re-runs it):\n\n{excerpt(report)}")
            if name in READS_THE_TREE:
                readers.add(name)
                read_trees.add(top)
    unchecked = unfinished_note(unfinished)
    if not refusals:
        if not trees:
            return ""
        context = unchecked + "\n\n" + SKILL_NOTE if unchecked else SKILL_NOTE
        note = {"hookEventName": "PreToolUse", "additionalContext": context}
        return json.dumps({"hookSpecificOutput": note})

    reason = (
        "This push is refused until the checks CI runs on every pull request pass "
        "in this checkout, since each would turn the pull request red and cost a "
        "fix cycle there (`PL-PLSJ`, `PL-S1BG`).\n\n" + "\n\n".join(refusals)
    )
    if unchecked:
        reason += "\n\n" + unchecked
    changed = sum(uncommitted(run, top) for top in read_trees)
    if changed:
        listed = ["`" + name + "`" for name, _ in checks("") if name in readers]
        names = listed[-1] if len(listed) == 1 else ", ".join(listed[:-1]) + " and " + listed[-1]
        paths = "1 path" if changed == 1 else f"{changed} paths"
        reason += (
            f"\n\n{names} read the working tree, and `git status --short` lists {paths} "
            "there with uncommitted changes, which a push sends only once they are "
            "committed. Commit them if this push should carry them, and the refusal "
            "stands. If it should not, stash them with `git stash --include-untracked`, "
            "push again so the checks read only what is sent, and `git stash pop` after."
        )
    reason += (
        "\n\nFix what it names, commit, and push again. A work-in-progress push to "
        "a branch with no pull request open runs no CI, and only that push may go "
        "out unchecked, with `git push --no-verify`."
    )
    return hook_input.deny("push-check-guard", "checks-failed", reason, payload)


if __name__ == "__main__":
    hook_input.run(decide)
