"""Tests for `.claude/hooks/no-prune-guard.sh`, the remote-ref prune refusal.

It refuses the push that deletes branches on the remote beside the prune
(`PL-M2NV`), since that deletes the branches themselves rather than this
clone's copies of them.

`PL-JK0M` routed this rule out of `CLAUDE.md`, where it was ten resident lines
every session carried before it had read anything, into the hook that decides
it. What the prose bought was a session remembering; what this buys is a
refusal, so the tests that matter are about what it refuses and - more
delicately - what it lets through. A guard on a command string is one
over-broad pattern away from blocking the repository's own documentation of the
rule, which is why the heredoc and quoted-argument cases below are here.

Nothing in this file runs git. The hook decides on the command text alone.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "no-prune-guard.sh"


def _decision(command: str, *, tool: str = "Bash") -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one tool call, or `None` if it stayed quiet."""
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    result = subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


PRUNING = (
    "git fetch --prune",
    "git fetch -p origin",
    "git fetch origin --prune-tags",
    "git remote prune origin",
    "git remote update --prune",
    "git config remote.origin.prune true",
    "git config --global fetch.prune true",
    "git fetch origin && git fetch --prune",
    "GIT_TRACE=1 git fetch --prune",
    # A line continued with a backslash is one command.
    "git fetch origin \\\n  --prune",
    # A command in a subshell or a substitution runs, quoted or not (`PL-WGFY`).
    "(git fetch --prune)",
    "echo $(git fetch --prune)",
    'echo "$(git remote prune origin)"',
    'echo "$(echo a; git fetch --prune)"',
    "diff <(git fetch --prune) x",
    # A group and a negation open the command after them, as in the other guards.
    "{ git fetch --prune; }",
    "! git fetch --prune",
)


@pytest.mark.parametrize("command", PRUNING)
def test_a_pruning_call_is_denied(command: str) -> None:
    """Every spelling that deletes a remote-tracking ref is refused."""
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"
    assert decision["hookEventName"] == "PreToolUse"


def test_the_refusal_answers_the_question_the_caller_had() -> None:
    """A denial that only says no leaves the session to invent the safe form."""
    reason = _decision("git fetch --prune")["permissionDecisionReason"]
    assert "bin/docket stranded" in reason
    assert "git branch -dr origin/<branch>" in reason
    assert "git checkout -B <branch> origin/main" in reason


ALLOWED = (
    # The fetch every session runs, and the one `docket branch` runs for it.
    "git fetch origin",
    "git fetch origin main",
    "git fetch --tags",
    # The tags half of the rewrite recovery `docket branch` prints (PL-YGF3).
    "git fetch --tags --force origin",
    # A branch name is not a flag, however much of one it contains.
    "git fetch origin my-prefix-branch",
    "git fetch origin claude/pl-jk0m-prune-guard",
    # `-p` means something else on every other subcommand.
    "git log --oneline -p HEAD",
    "git show -p HEAD",
    # The safe restart the deny message recommends must not itself be denied.
    "git branch -dr origin/x && git fetch origin main",
    # Reading and writing *about* the rule. The repository does this constantly:
    # this file, the hook, `docs/resident-instructions.md`, the item.
    "grep -n -- --prune tools/doc_check.py",
    'echo "never git fetch --prune"',
    "cat > f.md <<'EOF'\ngit fetch --prune\nEOF",
    # A comment is nobody's flag.
    "git fetch origin  # never with --prune",
)


@pytest.mark.parametrize("command", ALLOWED)
def test_an_innocent_call_is_untouched(command: str) -> None:
    """Silence, not an allow: the hook must never grant a permission either."""
    assert _decision(command) is None, f"{command!r} was denied"


# Each deleted a remote-tracking ref when run on git 2.43.0 against a scratch
# remote (`PL-R17X`), but `git fetch -P` and a `pruneTags` setting, which delete
# tags once pruning is on and are refused as `--prune-tags` is, since a config
# file the hook never reads can have turned it on.
SPELLINGS = (
    "git pull --prune",
    "git pull -p",
    "git pull -np",
    "git remote update -p",
    "git remote -v update -p",
    "git fetch -P",
    # A bundle of short flags prunes where its prune letter comes first.
    "git fetch -tp",
    "git fetch -pj4",
    # A setting ahead of the command name holds for the whole call; a name with
    # no `=` reads as true, and git reads the name without regard to case.
    "git -c fetch.prune=true fetch origin",
    "git -c remote.origin.prune=true pull",
    "git -c fetch.prune fetch",
    "git -c FETCH.PRUNE=Yes fetch",
    "git -c fetch.pruneTags=true fetch",
    "git --config-env=fetch.prune=PRUNE fetch",
    "git --config-env fetch.prune=PRUNE fetch",
    # Found past the options that take the next word as their value.
    "git -C . --git-dir .git --work-tree . -c fetch.prune=on fetch",
    "git config fetch.pruneTags true",
    "git config FETCH.PRUNE true",
)


@pytest.mark.parametrize("command", SPELLINGS)
def test_every_pruning_spelling_is_refused(command: str) -> None:
    """The spellings the four shapes missed are refused like `git fetch --prune` (`PL-R17X`)."""
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"


# Each deleted nothing on the same scratch remote, so none is refused.
NOT_PRUNING = (
    # A setting that reads as false turns nothing on.
    "git -c fetch.prune= fetch",
    "git -c fetch.prune=off fetch",
    "git -c fetch.prune=0 fetch",
    "git -c fetch.prune=NO fetch",
    # A letter taking a value takes the rest of the word: `-j4p` is jobs `4p`.
    "git fetch -j4p",
    "git pull -rp",
    "git pull -Sp",
    # Ahead of the command name, `-p` and `-P` are --paginate and --no-pager.
    "git -p fetch origin",
    "git -P fetch origin",
    # After it, `-c` is an option of that command: a count, a reused message.
    "git grep -c fetch.prune",
    "git commit -c HEAD",
)


@pytest.mark.parametrize("command", NOT_PRUNING)
def test_a_spelling_that_prunes_nothing_is_untouched(command: str) -> None:
    """Reading git as git reads it cuts both ways: what it would not prune passes."""
    assert _decision(command) is None, f"{command!r} was denied"


def test_only_a_heredoc_body_is_removed() -> None:
    """The prose in a body stays allowed, and a prune after its terminator is refused (`PL-39LD`).

    The hook read only the text before the first `<<`, so a prune on any line
    after a heredoc was never seen - including after the commit message this
    repository writes through one.
    """
    for heredoc in (
        "cat > f.md <<'EOF'\ngit fetch --prune\nEOF\n",
        "git commit -m \"$(cat <<'EOF'\nNever run git fetch --prune here.\nEOF\n)\"\n",
    ):
        assert _decision(heredoc + "git fetch origin") is None
        assert _decision(heredoc + "git fetch --prune") is not None


def test_a_quoted_separator_starts_no_command() -> None:
    """A `;` or a flag inside quoted text is that text, and starts nothing (`PL-WGFY`).

    The hook found a command position with a regex of its own over text that
    kept quoted content as written, so a `;` inside quotes read as a separator
    and a commit message read as a command's flags. The first case is the shape
    of the call that filed the item: a loop over command strings, one of them a
    prune, none of them run.
    """
    for quoted in (
        "for c in 'git fetch origin; git fetch --prune' 'x'; do echo \"$c\"; done",
        "echo 'a; git fetch --prune'",
        'echo "a; git fetch --prune"',
        "git commit -m 'never fetch with --prune'",
        'git commit -m "a; git remote prune origin"',
    ):
        assert _decision(quoted) is None, f"{quoted!r} was denied"
    assert _decision("echo a; git fetch --prune") is not None


def test_a_reserved_word_opens_the_command_after_it() -> None:
    """A prune after `do`, `then`, `else` or `time` is the prune it is (`PL-0X0G`).

    `shell_split.command_words` read the reserved word as the command's name,
    so each of these read as a command named `do` or `then` rather than `git`.
    The first two are the item's reproductions, verbatim.
    """
    for reserved in (
        "for x in a; do git fetch --prune; done",
        "if true; then git fetch --prune; fi",
        "if git fetch --prune; then :; fi",
        "if false; then :; else git remote prune origin; fi",
        "until git fetch --prune; do sleep 1; done",
        "time -p git fetch --prune",
        "(if true; then git fetch --prune; fi)",
    ):
        assert _decision(reserved) is not None, f"{reserved!r} was allowed"
    # Written as an argument, a reserved word is a word and starts nothing.
    assert _decision("echo then git fetch --prune") is None


WRAPPED = (
    # `PL-TRMN`'s reproductions, verbatim.
    ("timeout 60 git fetch --prune", True),
    ("env GIT_TRACE=1 git fetch --prune", True),
    ("command git fetch --prune", True),
    ("/usr/bin/git fetch --prune", True),
    # The other wrappers, each by its own grammar, and nested.
    ("timeout --signal KILL 60 nice -n 5 git remote prune origin", True),
    ("nohup git fetch -p origin", True),
    ("exec -a fetch git fetch --prune", True),
    ("echo origin | xargs -n 1 git fetch --prune", True),
    # What the wrapper runs decides, so a harmless call stays harmless.
    ("timeout 60 git fetch origin", False),
    ("env -i PATH=/usr/bin git fetch origin", False),
    ("command -v git", False),
    # An option after the command is the command's: this `-p` is git's.
    ("timeout 5 git log -p", False),
)


@pytest.mark.parametrize(("command", "refused"), WRAPPED)
def test_a_wrapper_runs_the_command_after_it(command: str, refused: bool) -> None:
    """A prune run through `timeout`, `env` or another wrapper is a prune (`PL-TRMN`).

    So is one run by a path to git. The guard read the wrapper as the command
    and compared a path with `git`, so each refused spelling here pruned
    unrefused.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


REDIRECTED = (
    # `PL-K9QL`'s reproductions, verbatim: ahead of git, and among a wrapper's
    # words.
    ("2>/dev/null git fetch --prune", True),
    ("env 2>/dev/null git fetch --prune", True),
    # Among git's own words, ahead of the setting it reads for the whole call.
    ("git 2>/dev/null -c fetch.prune=true fetch origin", True),
    # A redirection's word is a file, never a flag.
    ("git fetch origin 2>-p", False),
    ("2>/dev/null git fetch origin", False),
)


@pytest.mark.parametrize(("command", "refused"), REDIRECTED)
def test_a_redirection_is_not_a_word_of_the_command(command: str, refused: bool) -> None:
    """Bash lifts a redirection out wherever it stands, so it hides no prune (`PL-K9QL`).

    The guard read `2>/dev/null` as the word `2` and took it for the command,
    a wrapper stopped reading at the `>`, and git's own options stopped at it.
    """
    decision = _decision(command)
    assert (decision is not None) is refused, f"{command!r}: refused={decision is not None}"


# Each deleted `other-session-branch` on a scratch remote holding it and `main`,
# pushed to from a clone holding only `main`, on git 2.43.0 (`PL-M2NV`).
DELETING_PUSHES = (
    # The item's reproductions, verbatim.
    "git push --prune origin 'refs/heads/*:refs/heads/*'",
    "git push --mirror origin",
    # git reads an option after the repository and the refspecs too.
    "git push origin --mirror",
    "git push origin 'refs/heads/*:refs/heads/*' --prune",
    # `--prune` deletes through every refspec that reaches the branch.
    "git push --prune origin 'refs/heads/*'",
    "git push --all --prune origin",
    "git push --prune origin :",
    "git -c push.default=matching push --prune origin",
    # `remote.<name>.mirror` makes a push to that remote a mirror push, read as
    # a prune setting is: on unless it reads as false, named in any case, and
    # written by `config` for every later push.
    "git -c remote.origin.mirror=true push origin",
    "git -c remote.origin.mirror push origin",
    "git -c REMOTE.origin.MIRROR=yes push origin",
    "MIRROR=true git --config-env=remote.origin.mirror=MIRROR push origin",
    "git config remote.origin.mirror true",
    # Read wherever a fetch is: run by a wrapper, past a redirection, past
    # git's own options.
    "timeout 60 git push --mirror origin",
    "2>/dev/null git push --prune origin 'refs/heads/*'",
    "git -C . push --mirror origin",
    # Each deleted nothing there and is refused all the same: a push naming no
    # refspec takes one from a config file the hook never reads, so either flag
    # is refused whatever the rest of the push holds, a dry run included.
    "git push --prune origin main",
    "git push --mirror --dry-run origin",
)


@pytest.mark.parametrize("command", DELETING_PUSHES)
def test_a_push_that_prunes_the_remote_is_refused(command: str) -> None:
    """A push that deletes branches on the remote is refused (`PL-M2NV`).

    The guard had no shape for `git push`, so each of these ran unrefused,
    and a prune of this clone's copies was refused while the push deleting
    the branches themselves, for every session at once, was not.
    """
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"


# Each deleted nothing on the same scratch remote, so none is refused: the
# pushes a session makes, a mirror setting that reads as false, and a flag
# that is only named.
PUSHES_THAT_DELETE_NOTHING = (
    "git push -u origin claude/pl-m2nv-kz12da",
    "git push origin HEAD",
    "git push --force-with-lease origin claude/pl-m2nv-kz12da",
    "git push origin v0.5.13",
    "git push --tags origin",
    "git -c remote.origin.mirror=false push origin",
    "git push --no-mirror origin main",
    'git commit -m "never git push --mirror"',
    "echo git push --mirror origin",
    "grep -n -- --mirror .claude/hooks/no-prune-guard.sh",
)


@pytest.mark.parametrize("command", PUSHES_THAT_DELETE_NOTHING)
def test_a_push_that_deletes_nothing_is_untouched(command: str) -> None:
    """The push every session runs, and writing about the flags, pass (`PL-M2NV`)."""
    assert _decision(command) is None, f"{command!r} was denied"


def test_the_push_refusal_answers_the_question_the_caller_had() -> None:
    """A push is refused with its own recipe, since the fetch one is not true of it.

    A session reaching for `--mirror` or `--prune` on a push wants its branch on
    the remote, or other branches gone from it: the first is a push by name, and
    the second is the project owner's to do (`PL-M2NV`).
    """
    reason = _decision("git push --mirror origin")["permissionDecisionReason"]
    assert "git push -u origin <branch>" in reason
    assert "project owner" in reason
    assert "git branch -dr" not in reason
    both = _decision("git fetch --prune && git push --mirror origin")["permissionDecisionReason"]
    assert "git push -u origin <branch>" in both
    assert "git branch -dr origin/<branch>" in both


def test_a_prune_before_a_line_bash_cannot_read_is_refused() -> None:
    """Bash runs every line before a syntax error, so the hook reads them.

    The gate and floor guards fail open on a command bash would refuse. This
    one cannot: the prune on the first line runs before bash reaches the
    unclosed quote or the `<<` with no word on the second.
    """
    assert _decision('git fetch --prune\necho "unclosed') is not None
    assert _decision("git remote prune origin\ncat <<") is not None


def test_another_tool_is_not_this_hook_s_business() -> None:
    """The matcher is `Bash`; a payload from anything else is passed over."""
    assert _decision("git fetch --prune", tool="Edit") is None


def test_an_unreadable_payload_fails_open() -> None:
    """A guard that breaks the session costs more than the ref it protects."""
    result = subprocess.run(
        ["bash", str(HOOK)], input="not json", capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0
    assert not result.stdout.strip()


def test_the_hook_is_wired_into_the_settings_it_guards() -> None:
    """An unwired hook is prose with extra steps, and nothing would say so."""
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for entry in settings["hooks"]["PreToolUse"]
        if entry.get("matcher") == "Bash"
        for hook in entry["hooks"]
    ]
    assert any("no-prune-guard.sh" in command for command in commands)
