"""Tests for `.claude/hooks/no-prune-guard.sh`, the remote-ref prune refusal.

It refuses the push that deletes branches on the remote beside the prune
(`PL-M2NV`), since that deletes the branches themselves rather than this
clone's copies of them, the removal of a remote, which deletes every copy
this clone holds of that remote's branches at once (`PL-R295`), and a delete
by name handed a generated list, which deletes what the prune would
(`PL-G8TR`).

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


# Each read a prune or mirror setting and wrote nothing, run on git 2.43.0 in a
# scratch repository on 2026-09-26 (`PL-YFT4`). The first is the read the
# project owner met in ordinary work, verbatim.
CONFIG_READS = (
    "git config --get fetch.prune",
    "git config --get remote.origin.mirror",
    "git config --get-all remote.origin.prune",
    "git config --get-regexp 'remote.*.prune'",
    "git config --get-urlmatch fetch.prune https://example.com",
    # `--list` takes no name, so one reaches it only as a file named for one.
    "git config -f fetch.prune.cfg --list",
    "git config -l --file remote.origin.mirror.cfg",
    # After `--get`, a second word is a pattern the value must match, not a value.
    "git config --get fetch.prune true",
    # With no action, a name alone is read.
    "git config fetch.prune",
    "git config remote.origin.mirror",
    # Beside a location, a type or a display option, its value stuck or not.
    "git config --global --get fetch.prune",
    "git config --type=bool --get fetch.prune",
    "git config -t bool --get fetch.prune",
    "git config --file=.git/config --show-origin --get-all fetch.prune",
    "git config --default false --get fetch.prune",
    "git config --get -- fetch.prune",
    # Wherever the call runs.
    'echo "$(git config --get fetch.prune)"',
    "git config --get fetch.prune || echo unset",
)


@pytest.mark.parametrize("command", CONFIG_READS)
def test_a_read_that_prunes_nothing_is_admitted(command: str) -> None:
    """A `config` that only reads a prune or mirror setting passes (`PL-YFT4`).

    The guard refused every `config` naming either setting, read or write, so
    `git config --get fetch.prune`, met in ordinary work, was refused with a
    reason saying it prunes.
    """
    assert _decision(command) is None, f"{command!r} was denied"


# Each wrote the setting it names on the same scratch repository, though a read
# action or a read's shape is among its words, so each stays refused.
CONFIG_WRITES = (
    "git config fetch.prune true",
    # git reads options only up to the first word that is not one, so this
    # writes the value `--get`.
    "git config fetch.prune --get",
    # A `--no-` form clears the action before it, leaving a name and a value.
    "git config --get --no-get fetch.prune true",
    "git config --list --no-list fetch.prune true",
    # After `--`, or beside a type alone, a name and a value are written.
    "git config -- fetch.prune true",
    "git config --bool fetch.prune true",
    "git config --add fetch.prune true",
    "git config --unset fetch.prune",
    "git config --replace-all remote.origin.mirror true",
    # Bash makes new words of these after the hook has read the call, an option
    # among them, so a call holding one is read as a write.
    'x=--no-get; git config --get "$x" fetch.prune true',
    'git config --get "$(echo --no-get)" fetch.prune true',
    "git config --get `echo --no-get` fetch.prune true",
    "git config --get {--no-get,} fetch.prune true",
)


@pytest.mark.parametrize("command", CONFIG_WRITES)
def test_a_config_that_writes_is_refused_whatever_it_reads_like(command: str) -> None:
    """A `config` write stays refused beside a read action or a read's shape (`PL-YFT4`)."""
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"


# Each removes or renames a section holding a prune or mirror setting, which
# writes every setting in it. Measured on git 2.43.0 in scratch clones on
# 2026-09-27 (`PL-VM7C`): with a `fetch.prune = true` in a wider config file
# behind a narrower `false`, removing `fetch` or renaming it away let the next
# plain fetch prune; a section the guard never reads, renamed into `fetch` or a
# remote's, carried its `prune` there and a plain fetch pruned, or its `mirror`
# and a plain push deleted a branch on the remote.
SECTION_WRITES = (
    # The item's reproductions, verbatim.
    "git config --remove-section fetch",
    "git config --rename-section fetch kept",
    # Past a location, the file an option names, and `--`.
    "git config -f .git/config --remove-section fetch",
    "git config --global --remove-section fetch",
    "git config --remove-section -- fetch",
    # Into the section, from one the guard never reads.
    "git config --rename-section foo fetch",
    "git config --rename-section foo remote.origin",
    # A remote's section goes with the remote, and its override with it: the
    # next plain fetch has no remote to read, and prunes once one is added back.
    "git config --remove-section remote.origin",
    "git config --rename-section remote.origin remote.kept",
    # git matches a section as the file spells it: this removes a hand-written
    # `[Fetch]`, which `fetch` does not.
    "git config --remove-section Fetch",
    # Read wherever a setting is: run by a wrapper, past git's own options.
    "timeout 60 git config --remove-section fetch",
    "git -C . config --rename-section foo remote.origin",
)


@pytest.mark.parametrize("command", SECTION_WRITES)
def test_a_config_section_write_is_refused(command: str) -> None:
    """A section removed or renamed is every setting in it written (`PL-VM7C`).

    The guard read a `config` call for a setting's name, so `git config --unset
    fetch.prune` was refused while `git config --remove-section fetch`, which
    removes the same setting with the rest of its section, ran unrefused.
    """
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"


def test_a_section_renamed_into_a_remote_is_refused_as_a_push_too() -> None:
    """A rename into `remote.<name>` can carry a `mirror` there, so it is refused as a push as well.

    After `git config foo.mirror true`, `git config --rename-section foo
    remote.origin` made a plain `git push origin` delete a branch on the remote
    (`PL-VM7C`), which is `PL-M2NV`'s outcome, so the push reason is given too.
    """
    reason = _decision("git config --rename-section foo remote.origin")["permissionDecisionReason"]
    assert "git push -u origin <branch>" in reason
    assert "git branch -dr origin/<branch>" in reason
    fetch_only = _decision("git config --remove-section fetch")["permissionDecisionReason"]
    assert "git push -u origin <branch>" not in fetch_only


# None of these writes a prune or mirror setting, so none is refused: a section
# holding neither; a bare `remote`, which git 2.43 answers "no such section"
# rather than reaching the remotes under it; and a section action after the
# name, where git has stopped reading options and writes nothing.
SECTION_WRITES_THAT_KEEP_THE_SETTINGS = (
    "git config --remove-section alias",
    "git config --rename-section branch.main branch.trunk",
    "git config --remove-section remote",
    "git config fetch --remove-section",
)


@pytest.mark.parametrize("command", SECTION_WRITES_THAT_KEEP_THE_SETTINGS)
def test_a_section_holding_no_guarded_setting_is_untouched(command: str) -> None:
    """A section action on a section no prune or mirror setting sits in passes (`PL-VM7C`)."""
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


# Each runs the prune in bash 5.2.21 and was read as hiding it (`PL-97CF`): a
# continuation inside `<<-` or `<<<`, a delimiter one joins, a `<<` inside a
# `${...}` carried across lines, a quote inside a `${...}` in double quotes,
# and a `$'...'` its `$` reaches past a continuation.
RESHAPED = (
    "cat <<\\\n-EOF\n\thello\n\tEOF\nPRUNE",
    "cat <<\\\n< word\nPRUNE",
    "cat <<EOF\nabc\nEO\\\nF\nPRUNE",
    "echo ${x:-<<EOF\n}\nPRUNE\nEOF\n",
    'echo "${x:-"\'"}"; PRUNE; echo \'#\'',
    "echo $\\\n'\\''; PRUNE #'",
)


@pytest.mark.parametrize("shape", RESHAPED)
def test_a_continuation_or_an_expansion_hides_no_prune(shape: str) -> None:
    """A prune bash runs after a shape a continuation or a `${...}` makes is refused (`PL-97CF`)."""
    command = shape.replace("PRUNE", "git fetch --prune")
    assert _decision(command) is not None, f"{command!r} was allowed"


def test_a_here_document_beside_a_substitution_carried_across_lines_hides_no_prune() -> None:
    """A body waits for the end of the line its substitution closes on (`PL-QSN5`).

    POSIX XCU § 2.7.4 starts a here-document's body after the next newline,
    and a newline inside a `$( )` or a `<( )` is not one: bash 5.2.21 prints
    `body` and runs the prune, which the reader took for the body's text.
    """
    for opening in ("$(", "<("):
        command = f"cat <<EOF; x={opening}echo a\necho b); git fetch --prune\nbody\nEOF\n"
        assert _decision(command) is not None, f"{command!r} was allowed"


def test_a_prune_in_an_unquoted_heredoc_substitution_is_refused() -> None:
    """Bash expands the body of a delimiter with no quoted part, so a `$( )` in it runs (`PL-P95F`).

    POSIX XCU § 2.7.4. A quoted delimiter's body stays text, as
    `test_only_a_heredoc_body_is_removed` holds, and so does the rest of an
    unquoted one.
    """
    for heredoc in (
        "cat <<EOF\n$(git fetch --prune)\nEOF\n",
        "cat <<-EOF\n\t$(git fetch --prune)\n\tEOF\n",
    ):
        assert _decision(heredoc) is not None, f"{heredoc!r} was allowed"
    assert _decision("cat <<EOF\nNever run git fetch --prune here.\nEOF\n") is None


def test_a_body_line_a_continuation_carries_onto_the_delimiter_ends_nothing() -> None:
    """Bash joins `abc\\` to the `EOF` under it, so the prune after is body (`PL-97CF`)."""
    assert _decision("cat <<EOF\nabc\\\nEOF\ngit fetch --prune\nEOF\n") is None
    assert _decision("cat <<'EOF'\nabc\\\nEOF\ngit fetch --prune\n") is not None


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


# Each deleted every remote-tracking ref of `origin` on git 2.43.0, in a scratch
# clone whose `origin/other` held the only copy of a branch deleted on the
# remote (`PL-R295`).
REMOVING_A_REMOTE = (
    # The item's reproductions, verbatim.
    "git remote remove origin",
    "git remote rm origin",
    # `-v` ahead of the subcommand, and `--` ahead of the name.
    "git remote -v remove origin",
    "git remote --verbose rm origin",
    "git remote remove -- origin",
    # Read wherever a prune is: past git's own options, run by a wrapper, in a
    # list.
    "git -C . remote remove origin",
    "timeout 60 git remote rm origin",
    "git fetch origin && git remote remove origin",
)


@pytest.mark.parametrize("command", REMOVING_A_REMOTE)
def test_removing_a_remote_is_refused(command: str) -> None:
    """A remote removed is every ref it tracks deleted at once (`PL-R295`).

    The guard had no shape for `git remote remove` or its `rm`, so each of these
    ran unrefused, deleting more refs than any prune the guard refused.
    """
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"


# Each git call here deleted no branch's ref in the same scratch clone, so none
# is refused: `rename` moved the refs, `set-head -d` deleted only the symbolic
# `origin/HEAD`, and `branch -dr` names the one ref it deletes. The recipe the
# refusal prints must pass, and so must writing about the spelling.
REMOTE_CALLS_THAT_KEEP_THE_REFS = (
    "git remote -v",
    "git remote add upstream https://example.com/x.git",
    "git remote set-url origin https://example.com/x.git",
    "git remote rename origin kept",
    "git remote set-head origin -d",
    "git branch -dr origin/x",
    'git commit -m "never git remote remove origin"',
    "echo git remote rm origin",
)


@pytest.mark.parametrize("command", REMOTE_CALLS_THAT_KEEP_THE_REFS)
def test_a_remote_call_that_keeps_the_refs_is_untouched(command: str) -> None:
    """Reading, renaming or re-pointing a remote, and writing about removing one, pass."""
    assert _decision(command) is None, f"{command!r} was denied"


def test_the_remove_refusal_answers_the_question_the_caller_had() -> None:
    """A removal is refused with its own recipe, since neither other one is about a remote.

    A session removing a remote usually wants it pointed somewhere else, which
    `set-url` does and keeps its refs, or one of its refs gone, which a delete
    by name does (`PL-R295`).
    """
    reason = _decision("git remote remove origin")["permissionDecisionReason"]
    assert "git remote set-url <name> <url>" in reason
    assert "git branch -dr <name>/<branch>" in reason
    assert "bin/docket stranded" in reason
    assert "git checkout -B <branch> origin/main" not in reason
    assert "git push -u origin <branch>" not in reason


# Each deletes remote-tracking refs from names generated rather than spelled
# out, and each spelling that deleted anything did so on git 2.43.0 in a scratch
# clone on 2026-09-27; the last deletes nothing, and only `xargs` hands a
# `branch -dr` names it does not spell (`PL-G8TR`).
GENERATED_DELETES = (
    # The item's reproduction, verbatim: it deleted the only copy of a branch
    # the remote had dropped.
    "git for-each-ref --format='%(refname:short)' refs/remotes/origin | sed 's#^origin/##' \\\n"
    "  | grep -vxFf <(git ls-remote --heads origin | sed 's#.*refs/heads/##') \\\n"
    "  | xargs -r -I{} git branch -dr origin/{}",
    # `xargs` hands the names, whatever its replace string, or with none.
    "git for-each-ref refs/remotes/origin | xargs -I % git branch -dr %",
    "timeout 60 xargs -n1 git branch -Dr < refs.txt",
    # A name the shell builds: a substitution, a variable, a brace, a backtick.
    "git branch -dr $(git for-each-ref --format='%(refname:short)' refs/remotes/origin)",
    'for b in a b; do git branch -dr "origin/$b"; done',
    'git for-each-ref refs/remotes/origin | while read r; do git branch -dr "$r"; done',
    'BRANCH=claude/x; git branch -dr "origin/$BRANCH"',
    "git branch -dr origin/{a,b}",
    "git branch -dr `cat refs.txt`",
    # Several at once, in one call or split across the command, spelled any way.
    "git branch -dr origin/a origin/b",
    "git branch -dr origin/a; git branch -dr origin/b",
    "git branch --remotes --delete origin/a origin/b",
    "git -C . branch -r -D origin/a origin/b",
    # None at all.
    "git branch -dr",
)


@pytest.mark.parametrize("command", GENERATED_DELETES)
def test_a_generated_list_of_refs_is_refused_as_a_prune(command: str) -> None:
    """A delete by name deletes what `--prune` does once the names are generated (`PL-G8TR`).

    The guard read every `git branch -dr` as the one-ref remedy its refusals
    print, so the pipeline that deletes the set a prune computes ran
    unrefused, `xargs` naming each ref.
    """
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"


# One ref spelled out is the remedy the prune and remove refusals print. The
# last three delete no remote-tracking ref at all: two local branches, a
# listing, and the rule written about.
ONE_REF_SPELLED_OUT = (
    "git branch -dr origin/claude/pl-g8tr-x",
    "git branch --delete --remotes -- origin/x",
    # The restart the prune refusal prints, and one ref named twice.
    "git branch -rd origin/x && git fetch origin main && git checkout -B x origin/main",
    "git branch -dr origin/x || git branch -Dr origin/x",
    "git branch -D claude/a claude/b",
    "git branch -r --list 'origin/claude/*'",
    'git commit -m "never xargs git branch -dr origin/a origin/b"',
)


@pytest.mark.parametrize("command", ONE_REF_SPELLED_OUT)
def test_one_ref_spelled_out_is_untouched(command: str) -> None:
    """The remedy the refusals print still runs beside its generated form (`PL-G8TR`)."""
    assert _decision(command) is None, f"{command!r} was denied"


def test_the_generated_list_refusal_says_why_it_counts_as_a_prune() -> None:
    """A session that took its list for the remedy is told why not, then refused as a prune."""
    reason = _decision("git branch -dr origin/a origin/b")["permissionDecisionReason"]
    assert "prune by another spelling" in reason
    assert "bin/docket stranded" in reason
    assert "git branch -dr origin/<branch>" in reason
    assert "another spelling" not in _decision("git fetch --prune")["permissionDecisionReason"]
    both = _decision("git fetch --prune && xargs git branch -dr")["permissionDecisionReason"]
    assert both.count("Run `bin/docket stranded` first") == 1


# Why each spelling below is outside the promise the hook's header opens with,
# naming what found it.
PROBED_READ = (
    "a read that prunes nothing, found by piping it to the hook rather than met by a "
    "session: `PL-YFT4`, found working `PL-R17X`, which fixes the one spelling of it a "
    "session met, `git config --get fetch.prune`"
)
BY_SETTING = (
    "a prune git takes from an alias, a setting in the environment or an abbreviated "
    "long option, which no usage line of git 2.43 spells and no session has written: out "
    "of reach since `PL-R17X`"
)
BY_MIRROR = (
    "a mirror push reached through an abbreviated option or a remote's mirror setting, "
    "which no session has written: out of reach since `PL-M2NV`"
)
BY_VARIABLE = (
    "a flag built from a variable, which bash expands after the hook has read the words, "
    "and which no session has written: out of reach since `PL-JK0M`"
)
BY_SHELL = (
    "a command handed to another shell as a string, which the hook reads as one quoted "
    "word, and which no session has written: out of reach since `PL-WGFY`"
)
UNREAD_CONFIG = (
    "a `config` read the hook cannot read whole - an option it does not know, or a word "
    "bash expands after the hook has read it - which it takes for a write rather than "
    "guess, found building `PL-YFT4`"
)
BY_OTHER_COMMAND = (
    "a generated list of refs deleted by a command other than `branch`, which no session "
    "has written: out of reach since `PL-G8TR`, found building it"
)

# Spellings outside the promise, each read wrongly today (`PL-61FT`): the
# command, whether it is refused today, what git does with it, and why it is
# outside. A session probing the guard records what it finds here rather than
# filing it, and a row becomes an item only once a session is seen writing it.
# What each does was measured on git 2.43.0 on 2026-09-26, against a scratch
# remote holding `main` and `other` and a clone holding only `main`, with
# `other` deleted on the remote first wherever a prune was measured.
KNOWN_GAPS = (
    ("git remote prune -n origin", True, "prunes nothing, since `-n` is `--dry-run`", PROBED_READ),
    (
        "git log -S fetch -p",
        True,
        "prunes nothing: a search of the history for `fetch`, printed with patches",
        PROBED_READ,
    ),
    (
        "git log --grep pull -p",
        True,
        "prunes nothing: a search of commit messages for `pull`, printed with patches",
        PROBED_READ,
    ),
    (
        "git config --get-a fetch.prune",
        True,
        "reads `fetch.prune`, since git takes `--get-a` for `--get-all`",
        UNREAD_CONFIG,
    ),
    (
        'repo=.; git -C "$repo" config --get fetch.prune',
        True,
        "reads `fetch.prune`, once bash expands `$repo`",
        UNREAD_CONFIG,
    ),
    (
        "git -c alias.fp='fetch --prune' fp",
        False,
        "prunes, since the alias runs `git fetch --prune`",
        BY_SETTING,
    ),
    (
        "GIT_CONFIG_PARAMETERS=\"'fetch.prune'='true'\" git fetch origin",
        False,
        "prunes, since git reads `fetch.prune` from the environment",
        BY_SETTING,
    ),
    (
        "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=fetch.prune GIT_CONFIG_VALUE_0=true git fetch origin",
        False,
        "prunes, since git reads `fetch.prune` from the environment",
        BY_SETTING,
    ),
    (
        "git pull --pru",
        False,
        "prunes, since git takes an unambiguous prefix of a long option for the option",
        BY_SETTING,
    ),
    (
        "git push --mir origin",
        False,
        "deletes every branch on the remote that the clone does not hold, as `--mirror`",
        BY_MIRROR,
    ),
    (
        "git remote add --mirror=push copy ../remote.git && git push copy",
        False,
        "deletes every branch on `copy` that the clone does not hold, since the remote's "
        "mirror setting makes the push a mirror push",
        BY_MIRROR,
    ),
    ("p=--prune; git fetch origin $p", False, "prunes, once bash expands `$p`", BY_VARIABLE),
    ("bash -c 'git fetch --prune'", False, "prunes, in the shell it starts", BY_SHELL),
    # Measured 2026-09-27 the same way, the remote holding `claude/` branches.
    (
        "git for-each-ref --format='delete %(refname)' refs/remotes/origin/claude"
        " | git update-ref --stdin",
        False,
        "deletes every `origin/claude/` tracking ref, each named on its input",
        BY_OTHER_COMMAND,
    ),
    (
        "git push origin --delete"
        " $(git ls-remote --heads origin | sed 's#.*refs/heads/##' | grep -vx main)",
        False,
        "deletes on the remote every branch but `main`, each named by the substitution",
        BY_OTHER_COMMAND,
    ),
)


@pytest.mark.parametrize(("command", "refused", "effect", "outside"), KNOWN_GAPS)
def test_a_known_gap_keeps_todays_verdict(
    command: str, refused: bool, effect: str, outside: str
) -> None:
    """A spelling outside the promise gets the verdict it was recorded with (`PL-61FT`).

    What is pinned is the record, not the behaviour - and not as `xfail`, which
    `bin/docket verify --self` counts as a suppressed test. A change that closes
    a gap, meant or not, fails here: the row then moves into the tables above,
    and the promise in the hook's header is widened to hold it.
    """
    assert "PL-" in outside, f"{command!r}: name the item or branch that found it"
    decision = _decision(command)
    assert (decision is not None) is refused, (
        f"{command!r} is a known gap recorded as {'refused' if refused else 'admitted'} "
        f"({outside}), and it no longer is. Run, it {effect}. Move the row into the tables "
        "above, and widen the promise in the hook's header to hold it."
    )


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
