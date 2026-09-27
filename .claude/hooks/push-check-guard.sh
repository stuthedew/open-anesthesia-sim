#!/usr/bin/env bash
# PreToolUse hook on Bash: before a `git push` sends this repository's tree,
# run the three checks that most often turn a pull request red on something
# `make check` already refuses locally, and deny the push while any fails
# (`PL-PLSJ`, `PL-S1BG`).
#
# **Why these three and why here.** `PL-JYJJ`'s census counted 391 red runs; 32
# were `doc_check` and 8 `branch_id_check`, rising week on week, and every one
# in a 15-log sample was the branch's own text - an item quoting `start.md` by
# bare name, a path that does not exist, a branch no item id names. `PL-1BGP`
# then sorted its 43 store-rule runs: 40 were the branch's own, and `make
# check`'s `bin/docket check --verify --verify-base origin/main` refuses all 40.
# So each went out without `make check`, most often on the capture path, which
# is kept cheap on purpose. Run side by side the three take about as long as
# `doc_check` alone, 11 s, and cost no tokens; a red run costs a session a fix
# cycle. The store check reads `origin/main` as of the last fetch and never
# fetches, so a push never waits on the network. The other 2 of those 43 runs
# were `main`'s, on one day and from one cause `tools/pr_record_check.py` has
# refused since; on such a day this refuses a push the branch did not cause,
# naming the item on `main` that is wrong.
#
# **What counts as a push**: a git call whose command, after git's own options,
# is `push`, read through `shell_split.commands` as the three sibling guards
# read theirs, so a push in a subshell, after `&&` or behind `timeout` counts
# and one in a heredoc, a comment or a quoted message does not. A push that
# sends nothing is skipped: `--delete`, `-d`, a `:<branch>` refspec,
# `--dry-run` and `-n`. `--no-verify` is the one exemption, which the refusal
# offers for a work-in-progress push to a branch with no pull request open,
# since `quality.yml` runs no CI on one.
#
# **Which tree**: the push's own - the payload's `cwd`, moved by any `cd`
# before the push and by the push's `-C` options - and only where git's common
# directory there is this project's, so a linked worktree is checked and
# another repository is not. Like `make check`, the checks read the working
# tree, so an uncommitted edit counts. Each runs from that tree's own copy of
# its script, and is skipped in a tree without one.
#
# **Known gaps**, each costing a push CI would then catch, never a false
# refusal of a clean tree: in `git commit ... && git push` the hook runs before
# the commit, so `branch_id_check` reads the history without it; a push of a
# branch other than the one checked out is read as the checked-out one; and a
# `cd` or `-C` built from a variable, `--git-dir` or `--work-tree`, and a push
# inside `bash -c "..."` are not followed, so they are let through unchecked.
#
# Fails open in every error path - no python3, an unreadable payload, a check
# that crashes (a traceback, or an exit other than 1) or runs past its
# deadline - because a guard that blocks a correct push costs more than the red
# run it saves. The hook is given 120 s in `.claude/settings.json`; the checks
# get 100 s of it.
set -uo pipefail

payload=$(cat)
command -v python3 >/dev/null 2>&1 || exit 0
hooks=$(dirname "${BASH_SOURCE[0]}")

PAYLOAD="$payload" HOOKS="$hooks" python3 -c '
import json, os, re, subprocess, sys, time

sys.path.insert(0, os.environ["HOOKS"])
import shell_split

try:
    data = json.loads(os.environ["PAYLOAD"])
except (ValueError, KeyError):
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
command = data.get("tool_input", {}).get("command")
if not isinstance(command, str):
    sys.exit(0)

# The options git reads ahead of the command name that take the next word, as
# `no-prune-guard.sh` reads them.
TAKES_A_WORD = frozenset(
    ("-C", "-c", "--config-env", "--git-dir", "--work-tree", "--namespace", "--attr-source")
)
# From `git push -h` (git 2.43): the options taking the next word as their value
# where no `=` joins one, the letter among them, and what sends nothing.
PUSH_VALUED = frozenset(("--repo", "--recurse-submodules", "--receive-pack", "--exec", "--push-option"))
SENDS_NOTHING = frozenset(("--delete", "--dry-run", "--no-verify"))
EXPANDS = re.compile(r"[$`{]")
# Each check as a session types it to re-run it: `python3` runs as this
# interpreter, and `bin/docket`, a bash wrapper, runs under bash.
CHECKS = (
    ("doc_check", ("python3", "tools/doc_check.py", "check")),
    ("branch_id_check", ("python3", "tools/branch_id_check.py")),
    ("docket check", ("bin/docket", "check", "--verify", "--verify-base", "origin/main", "--no-fetch")),
)
DEADLINE = 100
SHOWN = 40


def own_options(words):
    """The options git reads ahead of the command name, each with its value, and where that name stands."""
    options, at = [], 1
    while at < len(words) and words[at].startswith("-"):
        option, equals, value = words[at].partition("=")
        at += 1
        if option in TAKES_A_WORD and not equals:
            value = words[at] if at < len(words) else ""
            at += 1
        options.append((option, value))
    return options, at


def is_git(words):
    """Whether `words` run git, by name or by path."""
    return words[0].rsplit("/", 1)[-1] == "git"


def sends(words):
    """Whether a git call is a push that sends commits: not a delete, a dry run or an exempted push."""
    _, at = own_options(words)
    if words[at : at + 1] != ["push"]:
        return False
    rest = iter(words[at + 1 :])
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


def moved(where, target):
    """`where` after a change of directory to `target`, or None where the target is built by the shell."""
    if where is None or target == "-" or EXPANDS.search(target):
        return None
    return os.path.join(where, os.path.expanduser(target))


def directory(words, where):
    """Where a git call runs: `where`, moved by each `-C` in turn, or None where git is pointed elsewhere."""
    for option, value in own_options(words)[0]:
        if option in ("--git-dir", "--work-tree"):
            return None
        if option == "-C":
            where = moved(where, value)
    return where


def git(where, *args):
    """What git prints for `args` run in `where`, or None where it fails."""
    try:
        done = subprocess.run(
            ["git", "-C", where, *args], capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else None


def common_directory(where):
    found = git(where, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return os.path.realpath(found) if found else None


def excerpt(text):
    """The report a refusal shows: its first line and its errors, up to its advisories, at most SHOWN lines."""
    report = text.splitlines()
    errors = [at for at, line in enumerate(report) if line.startswith("Errors (")]
    if errors:
        report = report[:1] + [""] + report[errors[0] :]
    lines = []
    for line in report:
        if line.startswith(("Advisories (", "Grooming advisories (", "Not checked (")):
            break
        lines.append(line)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) > SHOWN:
        cut = len(lines) - SHOWN
        lines = lines[:SHOWN] + [f"... {cut} more lines cut"]
    return "\n".join(lines)


where = data.get("cwd") or os.getcwd()
targets = []
for words in shell_split.commands(command):
    if words[0] == "cd":
        where = moved(where, words[-1] if len(words) > 1 else "~")
    elif is_git(words) and sends(words):
        targets.append(directory(words, where))
if not targets:
    sys.exit(0)

project = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.join(os.environ["HOOKS"], "..", "..")
ours = common_directory(project)
trees = []
for target in targets:
    if ours is None or target is None or common_directory(target) != ours:
        continue
    top = git(target, "rev-parse", "--show-toplevel")
    if top and top not in trees:
        trees.append(top)

running = []
for top in trees:
    for name, argv in CHECKS:
        python = argv[0] == "python3"
        if os.path.isfile(os.path.join(top, argv[1] if python else argv[0])):
            process = subprocess.Popen(
                [sys.executable, *argv[1:]] if python else ["bash", *argv],
                cwd=top,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            running.append((name, argv, process))

deadline = time.monotonic() + DEADLINE
refusals = []
for name, argv, process in running:
    try:
        out, err = process.communicate(timeout=max(0.0, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        process.kill()
        continue
    if process.returncode == 1 and "Traceback (most recent call last)" not in err:
        rerun = " ".join(argv)
        report = "\n".join(part for part in (out.rstrip(), err.rstrip()) if part)
        refusals.append(f"`{name}` failed (`{rerun}` re-runs it):\n\n{excerpt(report)}")
if not refusals:
    sys.exit(0)

reason = (
    "This push is refused until the tree it sends passes the checks CI runs on "
    "every pull request, since each would turn the pull request red and cost a "
    "fix cycle there (`PL-PLSJ`, `PL-S1BG`).\n\n"
    + "\n\n".join(refusals)
    + "\n\nFix what it names, commit, and push again. A work-in-progress push to "
    "a branch with no pull request open runs no CI, and only that push may go "
    "out unchecked, with `git push --no-verify`."
)
sys.stdout.write(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )
)
' 2>/dev/null || exit 0
