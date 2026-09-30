#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a git call that would prune remote refs, or
# push in a way that deletes branches on the remote itself.
#
# **What it promises** (`PL-61FT`), which is wider than what the other two
# guards promise, because a deleted ref cannot be brought back: every spelling
# git 2.43's own usage documents that deletes refs without naming them one by
# one, whether or not anybody has written it - the prune flags and settings of
# `fetch`, `pull` and `remote update` (`PL-R17X`), `remote prune`, a prune or
# mirror setting written by `config`, by its name or by the section holding it
# (`PL-VM7C`), a push with `--prune` or `--mirror` (`PL-M2NV`), `remote remove`
# or `remote rm`, which deletes every remote-tracking ref of its remote
# (`PL-R295`), and a `branch` delete of remote-tracking refs that does not spell
# out the one ref it deletes (`PL-G8TR`) - through every command shape
# `shell_split.py` reads. Outside it is what "Matched on the words" below puts
# out of reach, and a read that prunes nothing but is refused, where probing
# rather than a session found it. Each is a known gap, not a defect: a row of
# `KNOWN_GAPS` in `tests/unit/test_no_prune_guard.py`, held to the verdict it
# gets today, and filed as an item only once a session is seen writing it. A
# false refusal is worked when a session meets one, and never probed for.
#
# A stale `origin/<branch>` ref can be the only surviving copy of an item
# captured on a branch nobody merged. That is why `docket.vcs.fetch_remote`
# fetches without `--prune`, and what `bin/docket stranded` exists to recover;
# `PL-HKF4` came within one prune of losing exactly that. Removing the remote
# deletes every such ref with it (`PL-R295`). A `git push` with `--mirror` or
# `--prune` does worse: it deletes such a branch on the remote, for every
# session at once (`PL-M2NV`).
#
# **This used to be ten lines of `CLAUDE.md`, resident in every session**
# (`PL-JK0M`). A prohibition on a command string is decidable by reading the
# command, so it belongs in a check rather than in prose every session carries
# before it has read anything - `CLAUDE.md`'s own first routing disposition.
# The prose fired only if the session remembered it; this fires always.
#
# **The deny message carries the recipe, because this is the moment it is
# wanted.** A session reaching for `--prune` is usually trying to restart a
# branch whose pull request merged, and the safe form of that is three
# commands rather than a prune. Answering the question the caller actually had
# is what makes a refusal cheaper than the prose was. The message also says
# what the three leave undone - the branch on the remote - and whose that is.
# `PL-K2C8` added that to the skill's copy of the recipe
# (`.claude/skills/docket/modes/capture.md`), and this copy, the one a session
# reads at the moment it is refused, went without it until `PL-J3TV`. Keep
# the two in step.
#
# Fails open in every error path - no python3, an unreadable payload,
# `shell_split.py` missing from beside it - because a guard that breaks the
# session costs more than the ref it protects. `docs/resident-instructions.md`
# records the trade. A command bash would refuse is not one of them: bash runs
# every line before the one it cannot finish, so the lines before it are read.
set -uo pipefail

payload=$(cat)
command -v python3 >/dev/null 2>&1 || exit 0
hooks=$(dirname "${BASH_SOURCE[0]}")

PAYLOAD="$payload" HOOKS="$hooks" python3 -c '
import json, os, re, sys

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

# Where each command starts is the answer `shell_split.py` gives, which the
# three Bash guards share (`PL-PVW2`), and this guard reads every command it
# finds: those in a subshell or a `$( )` too, quoted or not, since each runs,
# and the git a wrapper runs, so `timeout 60 git fetch --prune` is the prune it
# is (`PL-TRMN`). Its words are the ones bash hands git, every redirection
# lifted out, so `2>/dev/null git fetch --prune` is one too, and so is a
# setting passed after a redirection (`PL-K9QL`). A quoted argument stays one
# word, so a `;` or a flag inside it is the text it is, where the regex this
# file used took a `;` inside quotes for a separator (`PL-WGFY`). Heredoc
# bodies and comments are gone, which is what lets this repository write prose
# *about* pruning - `CLAUDE.md`, this hook, the ledger - without the guard
# eating its own documentation; a prune after the terminator of a heredoc is
# read like any other line (`PL-39LD`).
#
# **What prunes is read from git 2.43 itself** (`PL-R17X`): its usage lines,
# `git -h`, `git fetch -h`, `git pull -h`, `git remote -h` and `git config -h`,
# and each spelling run against a scratch remote, the one way to learn which
# spellings delete a ref rather than which ones say they might. Three readings:
#
# - A setting passed ahead of the command name, as `-c <name>=<value>` or
#   `--config-env=<name>=<envvar>`, holds for the whole call. A prune setting
#   there prunes unless its value reads as false, and one written with no `=`
#   reads as true. The value `--config-env` names sits in the environment, out
#   of sight, so that setting is refused whatever it holds, and either is
#   refused whatever command follows. There `-p` and `-P` are --paginate and
#   --no-pager, and a `-c` after the command name is an option of that command
#   (`git grep -c` counts), so only the options git reads as its own are
#   read, stepping over each value a word of its own carries.
# - Four shapes delete refs, each a `git` command whose words include these in
#   this order. `fetch`, `pull` and `remote update` prune on a flag, spelled
#   long or as a letter among bundled short flags - `-tp` is `-t -p` - up to
#   the first letter taking a value, which takes the rest of the word: `-j4p`
#   is jobs `4p`, an error, and prunes nothing. `remote prune` always prunes.
# - A `config` naming a prune setting writes one that every later fetch reads,
#   unless it only reads it, and until `PL-YFT4` a read was refused as a write.
#   A read is told from a write as git 2.43 tells them, each spelling measured
#   in a scratch repository: its options stop at the first word that is not
#   one, so `git config fetch.prune --get` writes the value `--get`; a `--no-`
#   form clears the action before it, so `git config --get --no-get
#   fetch.prune true` writes; and with no action a name alone is read, and a
#   name with a value written. So a call reads only where each option ahead of
#   its first other word is one this hook knows - a read action, a location, a
#   type or a display option, or the value one of those takes - with a read
#   action among them, or none and a single name after them. An option it does
#   not know, an abbreviation included, is read as a write rather than guessed
#   at, and so is a call holding a `$`, a backtick or a brace, from which bash
#   makes new words after this hook has read them: `--get "$x"` writes where
#   `x` holds `--no-get`. Each costs a read spelled that way one call, and is
#   a known gap.
# - A `config` that removes or renames a section writes every setting in it,
#   so one naming a section a guarded setting sits in - `fetch`, or
#   `remote.<name>` - names that setting, in either place of a rename
#   (`PL-VM7C`). Measured: `--remove-section fetch` dropped a local
#   `fetch.prune = false`, and the next plain fetch pruned under a global
#   `true`; `--rename-section foo fetch` moved a `foo.prune = true` this hook
#   never reads into place. git matches a section as the file spells it, so a
#   hand-written `[Fetch]` goes with `--remove-section Fetch`, and the name is
#   read without regard to case, as the name of a setting is.
#
# `--prune-tags`, `-P` and the `pruneTags` settings delete tags, and only where
# pruning is on, which a config file this hook never reads may have turned on,
# so they are refused beside the flags that turn it on.
#
# **A push can delete the branches themselves** (`PL-M2NV`): on the remote,
# for every session at once, where a prune deletes only the copies this clone
# tracks. Read from `git push -h` and the same scratch remote, pushed to from a
# clone holding only `main`: `--mirror` deleted the branch the clone did not
# hold, and so did `--prune` with `--all`, a wildcard refspec, the matching
# refspec `:` or `push.default=matching`, where `--prune origin main` deleted
# nothing. A push naming no refspec takes one from a config file this hook
# never reads, so either flag is refused on any push, after the repository and
# the refspecs as well as before them, since git reads an option in either
# place. A `--dry-run` or a later `--no-mirror` beside it is not read, which
# costs a session that wanted only the preview one call. `remote.<name>.mirror`
# makes every push to that remote a mirror push - `--mirror` is "the default if
# the configuration option `remote.<remote>.mirror` is set", in git v2.43.0
# `Documentation/git-push.txt` - so it is read as the prune settings are: ahead
# of the command name, or written by `config`, whose `--rename-section foo
# remote.origin` carried a `foo.mirror = true` there and made a plain push
# delete the branch the clone did not hold (`PL-VM7C`). A branch deleted by
# name, with `--delete` or a `:<branch>` refspec, is not refused: it names what
# it deletes.
#
# **Removing a remote deletes every ref it tracks** (`PL-R295`): the stale ones
# a prune would take and the live ones beside them, so `git remote remove
# origin` leaves no `origin/<branch>` at all. `git remote -h` documents
# `remove`, and git v2.43.0 `Documentation/git-remote.txt` documents `rm`
# beside it. Run in a clone of the same scratch remote, `remove`, `rm`, `-v
# remove`, `--verbose rm` and `remove --` each deleted every remote-tracking
# ref of the remote, the only copy of a branch deleted on the remote among
# them. No setting removes a remote, so only the spellings are read. `remote
# rename` moves the refs rather than deleting them, and `remote set-head -d`
# deletes only the symbolic `<name>/HEAD`, which holds no commit, so neither
# is refused.
#
# **A delete by name is a prune when the names are generated** (`PL-G8TR`).
# `git branch -dr origin/<branch>` is the remedy two refusals below print, and
# it names the one ref it deletes. On 2026-09-06 a session piped `git
# for-each-ref` through a filter into `xargs -r -I{} git branch -dr origin/{}`,
# which deletes the set `--prune` deletes, each ref by name: what made the
# remedy safe was one ref, chosen, not the absence of a flag. So a `branch`
# call deleting remote-tracking refs - `-d`, `-D` or `--delete` beside `-r` or
# `--remotes`, read past the options `git branch -h` gives a value - passes only
# where the whole command deletes exactly one ref and spells it out. `xargs`
# hands its command names from its input, which only the wrapper shows. A `$`,
# a backtick, a brace or a glob is a name bash builds after this hook has read
# the words, and `"origin/$b"` in a loop reads exactly as a lone
# `"origin/$BRANCH"` does, so a variable counts too. Names are counted across
# the whole command, since the next thing a refused session tries is the same
# deletes split by `;`. None at all is refused with the rest: git deletes
# nothing then, and only `xargs` supplies the names. Run on git 2.43.0 in a
# scratch clone, two names deleted both, `-rd`, `--remotes --delete` and `-r
# -D` each deleted, `-d -r --merged` and a bare `-dr` deleted nothing, and the
# 2026-09-06 pipeline deleted the only copy of a branch the remote had dropped.
#
# Matched on the words because that is what the hook is handed. Out of reach:
# an alias; a setting passed in `GIT_CONFIG_PARAMETERS` or `GIT_CONFIG_COUNT`;
# an abbreviated long option, though `git pull --pru` prunes and `git push
# --mir` mirrors; the mirror setting `git remote add --mirror` and `git clone
# --mirror` write, which only a push to that new remote or from that new clone
# reads; a shell that builds the flag from a variable; a command handed to
# another shell as a string (`bash -c "..."`); and a generated list deleted by
# a command other than `branch` - `update-ref --stdin` reading `delete` lines,
# or a push `--delete` handed a substitution. None is how any session has
# written it, so each is a known gap, pinned by a row of `KNOWN_GAPS`.
TAKES_A_WORD = frozenset(
    ("-C", "-c", "--config-env", "--git-dir", "--work-tree", "--namespace", "--attr-source")
)
PRUNE_SETTING = re.compile(r"\b(?:fetch|remote\.\S+)\.prune(?:tags)?\b", re.IGNORECASE)
MIRROR_SETTING = re.compile(r"\bremote\.\S+\.mirror\b", re.IGNORECASE)
FALSE = frozenset(("", "false", "no", "off", "0"))
# The options of a `config` that reads, from `git config -h` (`PL-YFT4`).
READS = frozenset(
    ("--get", "--get-all", "--get-regexp", "--get-urlmatch", "--get-color", "--get-colorbool")
    + ("--list", "-l")
)
BESIDE = frozenset(
    ("--global", "--system", "--local", "--worktree", "--fixed-value", "--includes")
    + ("--bool", "--int", "--bool-or-int", "--bool-or-str", "--path", "--expiry-date")
    + ("-z", "--null", "--name-only", "--show-origin", "--show-scope")
)
VALUED = frozenset(("-f", "--file", "--blob", "-t", "--type", "--default"))
EXPANDS = re.compile(r"[$`{]")
GLOB = re.compile(r"[*?\[]")
# The actions of a `config` that write a section whole, from `git config -h`,
# and the names under a section that the two setting patterns guard (`PL-VM7C`).
SECTION_ACTIONS = frozenset(("--remove-section", "--rename-section"))
GUARDED_NAMES = ("prune", "prunetags", "mirror")
# The long options of a `branch` that take the next word as their value where
# no `=` joins one, from `git branch -h`; `-u` is the one such letter (`PL-G8TR`).
BRANCH_VALUED = frozenset(
    ("--set-upstream-to", "--contains", "--no-contains", "--merged", "--no-merged")
    + ("--sort", "--points-at", "--format")
)


def flag(long_forms, prune, value):
    """A test for one word: a long form, or a bundle holding a letter in `prune` before any in `value`."""

    def prunes(word):
        if word in long_forms:
            return True
        if word.startswith("--") or not word.startswith("-"):
            return False
        for letter in word[1:]:
            if letter in value:
                return False
            if letter in prune:
                return True
        return False

    return prunes


SHAPES = (
    ("fetch", flag(("--prune", "--prune-tags"), "pP", "jo")),
    ("pull", flag(("--prune",), "p", "rsXSjo")),
    ("remote", "prune"),
    ("remote", "update", flag(("--prune",), "p", "")),
)
PUSH_SHAPES = (("push", flag(("--mirror", "--prune"), "", "")),)
REMOVE_SHAPES = (("remote", "remove"), ("remote", "rm"))


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


def sets(pattern, words):
    """Whether the options git reads ahead of the command name pass a setting `pattern` names."""
    for option, value in own_options(words)[0]:
        name, equals, setting = value.partition("=")
        if not pattern.fullmatch(name):
            continue
        if option == "--config-env":
            return True
        if option == "-c" and not (equals and setting.lower() in FALSE):
            return True
    return False


def in_order(words, steps):
    """Whether `words` holds a word for each step, in order: one equal to it, or passing it."""
    at = 0
    for step in steps:
        passes = step if callable(step) else step.__eq__
        while at < len(words) and not passes(words[at]):
            at += 1
        if at == len(words):
            return False
        at += 1
    return True


def reads(words):
    """Whether the words after `config` only read, as git 2.43 parses them (`PL-YFT4`).

    Its options run to the first word that is not one, or to `--`, and each must
    be one this hook knows, with a read action among them or none and a single
    name after them. A glob where a second word would change what git does - in
    an option value, or in that single name - reads as a write.
    """
    read, at = False, 0
    while at < len(words) and words[at] not in ("-", "--") and words[at].startswith("-"):
        word = words[at]
        at += 1
        option, equals, value = word.partition("=")
        if word in VALUED:
            value = words[at] if at < len(words) else ""
            at += 1
        elif word[:2] in ("-f", "-t"):
            value = word[2:]
        elif not (equals and option in VALUED) and word not in READS | BESIDE:
            return False
        if GLOB.search(value):
            return False
        read = read or word in READS
    names = words[at:]
    if names[:1] == ["--"]:
        names = names[1:]
    return read or (len(names) == 1 and not GLOB.search(names[0]))


def sections(words):
    """The sections the words after `config` remove or rename whole (`PL-VM7C`).

    Its options run to the first word that is not one, or to `--`, as `reads`
    reads them; where a section action is among them, the names after them are
    the sections it writes, the one `--remove-section` takes or both of a rename.
    """
    action, at = False, 0
    while at < len(words) and words[at] not in ("-", "--") and words[at].startswith("-"):
        action = action or words[at] in SECTION_ACTIONS
        at += 2 if words[at] in VALUED else 1
    names = words[at:]
    if names[:1] == ["--"]:
        names = names[1:]
    return names if action else []


def holds(pattern, section):
    """Whether `section` holds a setting `pattern` names, as `fetch` holds `fetch.prune`."""
    return any(pattern.fullmatch(f"{section}.{name}") for name in GUARDED_NAMES)


def writes(pattern, words):
    """Whether a `config` among `words` names a setting `pattern` names, or a section holding one, and does more than read it."""
    if "config" not in words[1:]:
        return False
    after = words[words.index("config", 1) + 1 :]
    named = any(pattern.search(word) for word in after)
    if not (named or any(holds(pattern, section) for section in sections(after))):
        return False
    return any(EXPANDS.search(word) for word in words) or not reads(after)


def is_git(words):
    """Whether `words` run git. A path to git is git: `/usr/bin/git fetch --prune` prunes (`PL-TRMN`)."""
    return words[0].rsplit("/", 1)[-1] == "git"


def runs(shapes, pattern, calls):
    """Whether a git call in `calls` passes or writes a setting `pattern` names, where there is one, or takes one of `shapes`."""
    return any(
        is_git(words)
        and (
            (pattern is not None and (sets(pattern, words) or writes(pattern, words)))
            or any(in_order(words[1:], shape) for shape in shapes)
        )
        for words in calls
    )


def remote_deletes(words):
    """The names a `git branch` call deletes from the remote-tracking refs, or None where it deletes none (`PL-G8TR`).

    Its options are read as `git branch -h` gives them, bundled or not, and
    every word after `--` is a name.
    """
    _, at = own_options(words)
    if words[at : at + 1] != ["branch"]:
        return None
    delete = remote = False
    names = []
    rest = iter(words[at + 1 :])
    for word in rest:
        if word == "--":
            names.extend(rest)
        elif word.startswith("--"):
            option, equals, _ = word.partition("=")
            delete = delete or option == "--delete"
            remote = remote or option == "--remotes"
            if option in BRANCH_VALUED and not equals:
                next(rest, None)
        elif word.startswith("-") and word != "-":
            for position, letter in enumerate(word[1:], 2):
                delete = delete or letter in "dD"
                remote = remote or letter == "r"
                if letter == "u":
                    # Its value is the rest of the word, or the next word if none is left.
                    if position == len(word):
                        next(rest, None)
                    break
        else:
            names.append(word)
    return names if delete and remote else None


def generated(calls):
    """Whether the `branch` deletes of remote-tracking refs in `calls` do other than spell out one ref (`PL-G8TR`).

    One `xargs` runs, or a name holding a character bash expands, is refused
    outright; otherwise the names are counted across every call, so one ref
    passes and none or several do not.
    """
    named, found = set(), False
    for words in calls:
        names = remote_deletes(words) if is_git(words) else None
        if names is None:
            continue
        if "xargs" in words.wrappers or any(EXPANDS.search(n) or GLOB.search(n) for n in names):
            return True
        found = True
        named.update(names)
    return found and len(named) != 1


calls = shell_split.commands(command)
pushes = runs(PUSH_SHAPES, MIRROR_SETTING, calls)
prunes = runs(SHAPES, PRUNE_SETTING, calls)
removes = runs(REMOVE_SHAPES, None, calls)
deletes = generated(calls)
if not (pushes or prunes or removes or deletes):
    sys.exit(0)

push_reason = (
    "A push that can delete branches on the remote is refused in this "
    "repository. `--mirror` deletes every branch on the remote that this clone "
    "does not hold, and `--prune` every such branch its refspec reaches - the "
    "unmerged branches of other sessions among them, for every session at once "
    "- and a push to a remote whose `remote.<name>.mirror` setting is on is a "
    "mirror push. A branch nobody merged can be the only copy of an item "
    "captured on it. Which refspec a push uses can sit in a config file, so "
    "either flag is refused whatever the rest of the push holds.\n\n"
    "To push this branch, name it, without the flag or the setting:\n\n"
    "    git push -u origin <branch>\n\n"
    "Deleting branches on the remote is left to the project owner: list them in "
    "the reply, with the command that deletes them (`CLAUDE.md`, the "
    "housekeeping bullet)."
)
prune_reason = (
    "Pruning remote-tracking refs is refused in this repository. A stale "
    "`origin/<branch>` ref can be the only surviving copy of an item captured "
    "on a branch nobody merged (`PL-HKF4` came within one prune of losing "
    "one), so `docket.vcs.fetch_remote` fetches without `--prune` and "
    "`bin/docket stranded` recovers what such a ref holds.\n\n"
    "Run `bin/docket stranded` first: it prints every item that exists only on "
    "a branch, with the `git checkout` line that restores the file.\n\n"
    "To restart a branch whose pull request has already merged, clear the ref "
    "this clone keeps for it and rebase the name onto the merged base:\n\n"
    "    git branch -dr origin/<branch>\n"
    "    git fetch origin main\n"
    "    git checkout -B <branch> origin/main\n\n"
    "That leaves the branch on the remote alone: `git branch -dr` clears the "
    "ref in this clone and nothing else, and while the branch is still there "
    "the next `git fetch origin` brings the ref back. GitHub deletes a branch "
    "when its own pull request merges, `branch-sweep.yml` deletes a finished "
    "`claude/*` branch daily, and `python3 tools/branch_sweep.py` names any the "
    "sweep keeps. Deleting one that should go anyway is for the project owner "
    "to run, since a push from a session is refused, so name it in the reply: "
    "`git push origin --delete <branch>` (`docs/worker.md`, `PL-K2C8`, "
    "`PL-X8SV`).\n\n"
    "To fetch without pruning, drop the flag or the setting: `git fetch origin`."
)
delete_reason = (
    "A `git branch -dr` handed a generated list is a prune by another "
    "spelling: it deletes what `--prune` would, with no stop to ask whether "
    "any of those refs is the only copy of something (`PL-G8TR`). It passes "
    "only where one Bash call deletes exactly one ref, spelled out - not "
    "handed its names by `xargs`, not built by the shell from a variable, a "
    "substitution, a brace or a glob, and not one of several. Delete each ref "
    "in a call of its own.\n\n"
)
remove_reason = (
    "Removing a remote is refused in this repository. `git remote remove` and "
    "`git remote rm` delete every remote-tracking ref of the remote they name, "
    "so removing `origin` deletes every `origin/<branch>`, and a stale one can "
    "be the only surviving copy of an item captured on a branch nobody merged.\n\n"
    "Run `bin/docket stranded` first: it prints every item that exists only on "
    "a branch, with the `git checkout` line that restores the file.\n\n"
    "To point the remote somewhere else, keep it and its refs:\n\n"
    "    git remote set-url <name> <url>\n\n"
    "To delete one of its refs, name it: `git branch -dr <name>/<branch>`. A "
    "remote no longer wanted can be left in place."
)
reason = "\n\n".join(
    text
    for refused, text in (
        (pushes, push_reason),
        (prunes or deletes, (delete_reason if deletes else "") + prune_reason),
        (removes, remove_reason),
    )
    if refused
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
