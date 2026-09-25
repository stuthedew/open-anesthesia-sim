"""What git already knows about work in progress.

Whether an item is being worked on right now is a fact the repository
already holds: a branch is carrying its commits. Storing that in the item file
instead would mean a session has to remember to write it when it starts and
to clear it when it stops - and a session that crashes, or that is simply
abandoned, leaves the item marked in-progress forever with nobody able to
tell whether that is true.

So it is derived, never stored. A branch that is gone means work that is not
in flight, which is exactly right: branches are deleted when their pull
request merges.

The same holds for finished work: which pull requests have reached the
default branch is a fact the repository holds, so an item's recorded pull
request can be checked against it rather than trusted.

And for work that never arrived: an item committed on a branch that is closed
without merging exists only on that branch, invisible to every session that
reads the store in its own checkout. Git holds the branch, so git can be asked
what is on it that nowhere else has.
"""

from __future__ import annotations

import locale
import re
import subprocess
import time
from collections import Counter
from collections.abc import Callable, Collection, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from pathlib import Path

from .model import CLOSED_STATUSES, parse_front_matter, parse_item
from .release import NOTES_DIR, version_in
from .store import ID_PATTERN

# The default branch, in the order it is looked for: a branch whose tip that
# one already contains is finished rather than in flight. Trying several means
# a repository using a different name for it still gets the filtering, and a
# checkout with no remote falls back to its local branch.
DEFAULT_BRANCHES = ("origin/main", "origin/master", "main", "master")

Runner = Callable[[list[str], Path], str]


class GitSilence(str):
    """The empty string, marked as the one git never gave.

    `Runner` is `(args, root) -> str`, and every read in this module, every
    helper one of them calls and every fake a test injects is written to that
    shape - so a failure channel has to arrive without changing it. A `str`
    subclass does: a silence still reads, splits, strips and compares as the
    `""` this module has always collapsed a failure to, so the call sites with
    no use for the distinction are untouched, while a reader that must not
    mistake "git said nothing" for "there is nothing to say" asks `answered`.

    **The marker survives no string operation.** `.strip()` and `.splitlines()`
    both return plain `str`, so it can be read off the runner's own return
    value and nowhere else. That is a real hazard for a reader added later, and
    `_Silences` is the answer to it: a read wraps its runner once and never has
    to remember again.
    """

    __slots__ = ()


#: The one silence. Every unanswered call returns this object, so a reader may
#: compare identity as well as type and nothing has to construct one.
SILENT = GitSilence()


def answered(text: str) -> bool:
    """Whether git answered the question at all, as against answering nothing.

    The distinction `_run_git` used to throw away, and the one this module turns
    on. An empty answer is a fact about the repository - no such ref, nothing
    changed, no tags - while a silence is a fact about the run, and a reader
    that reads the second as the first reports a clean result it never
    established. `_superseded` did exactly that, in the one direction its own
    docstring said it must never fail in (`PL-Q9Z1`).
    """
    return not isinstance(text, GitSilence)


class GuessedBase(str):
    """A base ref nothing established, whether or not the name is real.

    Two different answers wear this mark, and what they share is the property
    that matters: the ref came back without the reading that would make it the
    right one. Either no candidate resolved at all, and the name is the bare
    fallback; or one resolved only because a *preferred* candidate ahead of it
    went unanswered, so `origin/main` may be sitting there unread while the
    local `main` is handed back in its place. The second is the dangerous one,
    because the name is real and the ref exists - it is simply the wrong one,
    and the docstring on `default_base` measures that mistake at 20 paths
    reported outside a commission whose true answer was 4.

    `GitSilence` is this same idea one question lower down, and the pair is
    worth holding apart. There, git said nothing and the empty string carries
    the fact. Here git may have answered every probe truthfully, saying *no*
    four times over - so the ref that comes back was picked rather than read,
    which `_Silences` structurally cannot catch because nothing failed.

    A `str` subclass for the reason `GitSilence` is one: `default_base` is
    consumed as a bare ref name by sixteen reads in this module, and a guess
    still formats, compares and interpolates as the `"main"` they have always
    been handed - so a caller with no use for the distinction is untouched,
    while one that must not compare against a guessed base asks `resolved`.

    **The mark survives no string operation**, exactly as `GitSilence`'s does
    not: `f"{base}"`, `base.strip()` and `base + ""` are all plain `str`. Read
    it off `default_base`'s own return value and nowhere else - or, inside this
    module, let the read's `_Silences` wrapper carry it, which is what
    `default_base` marks on the way past.
    """

    __slots__ = ()


#: The one guess. `main` rather than the empty string because every caller
#: interpolates the base into something a person reads, and "this checkout has
#: no  to compare against" names nothing at all.
GUESSED_BASE = GuessedBase("main")


def resolved(base: str) -> bool:
    """Whether `base` is the ref this repository calls for, as against a guess.

    Stronger than "this ref exists", deliberately. It answers False for a name
    that resolves perfectly well but was reached by falling past a candidate
    git would not answer for, because a caller comparing against the local
    `main` when `origin/main` was merely unread gets a wrong answer that looks
    entirely ordinary.

    The base is the one input whose wrongness cannot be seen in any answer
    downstream of it, because every downstream answer is *about* that base: a
    diff taken against a ref that is not there reports no change, and nothing
    in that answer distinguishes it from a branch that changed nothing
    (`PL-73P0`).
    """
    return not isinstance(base, GuessedBase)


def _asks_for_a_blob(args: list[str]) -> bool:
    """Whether the call names one path inside one revision, `<rev>:<path>`.

    The one shape where git's fatal exit is an answer rather than a failure.
    `git show HEAD:docs/items/gone.md` exits 128 for a path the revision does
    not hold, and every caller of this shape already reads the empty string as
    "the base does not carry that file". `GitRunner`'s other serving path says
    the same: `cat-file --batch` prints `missing` and exits 0 for an absent path
    *and* for an absent revision alike, measured 2026-09-19, so classifying the
    fatal exit as an answer is what keeps the batch and the subprocess saying
    the same thing about the same question.

    What it costs is said out loud rather than hidden: a revision that vanished
    mid-read is indistinguishable here from a file that was never in it, and
    this layer cannot separate the two without a second process per blob.
    """
    return len(args) == 2 and args[0] in {"show", "rev-parse"} and ":" in args[1]


def _asks_for_a_diff(args: list[str]) -> bool:
    """Whether the call is a `git diff`, the one read here whose exit 1 is not a no.

    Inside a repository every diff this module asks exits 0, 128 or 129 - 128
    for a bad revision, for `A...B` with no merge base, for a root commit's
    parent and for a pathspec outside the tree - and never 1, measured against
    git 2.43.0 on 2026-09-23. Outside one, git runs a different command under
    the same name: it compares two paths on the filesystem, and git-diff(1)
    says that form "implies `--exit-code`". So `diff --name-only
    origin/main...HEAD -- docs/items` from a directory in no repository exits 1
    with `error: Could not access 'origin/main...HEAD'`, and `changed_items`
    read that as the branch having changed no item (`PL-19T3`).

    No caller loses a real 1 to this. None passes `--exit-code` or `--quiet`,
    and `_run_git` would have discarded what either said: the 1 comes back as
    `""` and carries no status.
    """
    return _subcommand(tuple(args)) == "diff"


def _run_git(args: list[str], root: Path) -> str:
    """Run git, returning its answer, or `SILENT` where it did not answer.

    A checkout without git, without a remote, or without network is a normal
    condition for this tool - the session-start digest must not fail because of
    it - so no failure raises. What changed is that a failure is no longer
    *indistinguishable* from an empty answer: it comes back as `GitSilence`, and
    a caller that cares asks `answered`.

    **The classification is git's own exit codes, measured rather than
    recalled.** One probe per shape this module issues, against git 2.43.0 on
    2026-09-19:

    | Call | Exit | Read as |
    | --- | --- | --- |
    | anything git could answer | 0 | the answer |
    | `rev-parse --verify --quiet <no such ref>` | 1 | "no such ref" - an answer |
    | `merge-base` on unrelated histories | 1 | "no merge base" - an answer |
    | `show <rev>:<path the rev lacks>` | 128 | "not there" - an answer |
    | `diff`/`log`/`ls-tree`/`rev-list` on a bad revision | 128 | **silence** |
    | `diff` outside a repository | 1 | **silence** |
    | a mistyped option | 129 | **silence** |
    | git missing, or the ten-second timeout | - | **silence** |

    So exit 1 is git saying no and exit 128 is git not saying anything, with one
    exception each way and the reason for each on the predicate that carries it:
    `_asks_for_a_blob` for the 128 that answers, `_asks_for_a_diff` for the 1
    that does not. A silence still returns the empty string, so nothing
    downstream changes shape.

    `git` is named rather than given an absolute path on purpose: the path
    differs across the environments this runs in, and resolving it through
    `PATH` is what lets the same code work in all of them. That is also why
    pinning one would not harden anything - a checkout that cannot run `git`
    is already a case this function answers with a silence.
    """
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return SILENT
    if result.returncode == 0:
        return result.stdout
    if (result.returncode == 1 and not _asks_for_a_diff(args)) or _asks_for_a_blob(args):
        return ""
    return SILENT


@dataclass
class _Silences:
    """A runner that remembers what git did not answer, for the read wrapping it.

    One public read puts tens of questions to git through a dozen helpers, and
    `.claude/rules/apparatus-standard.md`'s floor binds the answer it returns
    rather than any one of them. Threading a failure flag back out of every
    helper would change every signature in the module and would still miss the
    helper nobody remembered; wrapping the runner once at the top of a read
    catches every silence raised anywhere beneath it, including in code written
    after the wrapping.

    **It reports rather than refuses**, which is the same choice the rest of the
    module makes: the marks a read did collect are kept, and `reason` says the
    reading was partial. Over-reporting an item as in flight costs a session one
    look; under-reporting one costs two sessions a merge conflict.

    Measured on this repository 2026-09-19: eight public reads put 174 questions
    to git and every one was answered, so a `declined` built on this is silent
    in the ordinary case rather than an advisory nobody reads.
    """

    run: Runner
    #: Every call git did not answer, in the order they were put.
    unanswered: list[tuple[str, ...]] = field(default_factory=list)
    asked: int = 0
    #: Set by `default_base` when no candidate ref resolved beneath this read.
    #: Not a silence - git answered - so nothing above would otherwise see it,
    #: and every comparison the read goes on to make is against a guess.
    guessed_base: bool = False

    def __call__(self, args: list[str], root: Path) -> str:
        self.asked += 1
        text = self.run(args, root)
        if not answered(text):
            self.unanswered.append(tuple(args))
        return text

    @property
    def reason(self) -> str:
        """Why this read is partial, or `""` where git answered and the base resolved."""
        silence = ""
        if self.unanswered:
            first = " ".join(self.unanswered[0])
            silence = (
                f"git did not answer {len(self.unanswered)} of the {self.asked} questions this "
                f"read put to it, the first being `git {first}`"
            )
        if not self.guessed_base:
            return silence
        guess = (
            "no candidate default branch could be established here (tried "
            f"{', '.join(DEFAULT_BRANCHES)}), so the base fell back to `{GUESSED_BASE}` with "
            "nothing confirming it is there"
        )
        # Lead with the guess. Where no base resolved, the silences beneath it
        # are usually git refusing the very calls that name the missing ref -
        # `for-each-ref --merged=main` and the like - so reporting those first
        # sends a reader after a git failure that never happened.
        return f"{guess}; {silence}" if silence else guess


#: The subcommands that cannot change anything, whatever arguments they are
#: handed. `GitRunner`'s memo is sound for exactly these, and the set is closed
#: on purpose: `fetch` rewrites the remote-tracking refs every other read in
#: this module is answered from, and `tag` writes one unless it is given
#: `--list`. A subcommand not named here is run every time *and* empties the
#: memo, so one added later is slow rather than wrong.
_READ_ONLY = frozenset(
    {
        "cat-file",
        "diff",
        "for-each-ref",
        "log",
        "ls-tree",
        "merge-base",
        "rev-list",
        "rev-parse",
        "show",
    }
)

#: How `subprocess.run(text=True)` would have decoded git's output, so a blob
#: served from the batch below is the same `str` `git show` would have given.
_ENCODING = locale.getpreferredencoding(False)


def _subcommand(argv: tuple[str, ...]) -> str:
    """The git subcommand an argv names, ignoring the options in front of it."""
    return next((token for token in argv if not token.startswith("-")), "")


@dataclass(frozen=True)
class SubcommandCost:
    """What one git subcommand cost a command.

    `asked` counts the questions the module put; `ran` counts the ones that
    reached git. They differ by what the memo answered, which is the whole
    measurement `PL-MMVF` turns on.
    """

    subcommand: str
    asked: int
    ran: int
    distinct: int
    seconds: float

    @property
    def saved(self) -> int:
        """Calls the memo answered without asking git."""
        return self.asked - self.ran


@dataclass(frozen=True)
class RefWalk:
    """The input a profiled run was measured against.

    **Recorded because a call count without it is attributable to nothing.**
    Two machines were once compared at 220 calls against 1,107 and the ratio
    explained by three different scaling laws in one sitting, because their ref
    sets differed and had moved hours apart while other sessions pushed
    branches (`PL-XD3C`). A count is a measurement only next to the input that
    produced it, so this travels with every profile and a reader can diff two
    machines' inputs before believing anything about their outputs.

    `declined` carries what could not be read, rather than letting a partial
    walk be reported as a complete one.
    """

    listed: int = 0
    merged: int = 0
    unmerged: int = 0
    commits: int = 0
    item_edits: int = 0
    #: Per unmerged ref: its name, the commits it holds that the base does not,
    #: and how many item files it touches. The per-ref detail rather than the
    #: totals alone, because that is what makes two machines comparable by
    #: subtraction instead of by ratio.
    refs: tuple[tuple[str, int, int], ...] = ()
    #: Unmerged refs whose fork point this checkout cannot resolve, so their
    #: work went uncounted. Named rather than folded into a zero: on a
    #: truncated clone that is the difference between "introduces nothing"
    #: and "could not be read".
    unread: tuple[str, ...] = ()
    declined: str = ""


@dataclass(frozen=True)
class GitProfile:
    """What one command asked git, and what the input was when it asked."""

    asked: int
    ran: int
    processes: int
    seconds: float
    by_subcommand: tuple[SubcommandCost, ...]
    walk: RefWalk

    @property
    def saved(self) -> int:
        """Calls the memo answered without reaching git."""
        return self.asked - self.ran


class GitRunner:
    """One command's access to git: countable, memoized, and blob-batched.

    A `Runner` like `_run_git` - the same `(args, root) -> str` - so every
    function in this module takes one without changing, and a test that injects
    its own runner is untouched.

    **Its lifetime is one command, and that is a correctness property rather
    than a convenience.** `cli` holds it on the argparse namespace for exactly
    the reason it holds `FlightReport` there (`PL-PMT7`): a memo that outlived
    the command would answer from before a `fetch`, and `bin/docket branch`
    fetches in-process. That hazard is closed twice over - the memo covers only
    `_READ_ONLY` and is emptied by anything else, `fetch` included - so a
    caller that never closes this still cannot be told a stale ref.

    Three behaviours, each defeatable on its own so a caller can measure one:

    - **Counting** (`PL-XD3C`), always on and costing one `perf_counter` a
      call, because a profile nobody can take is how a question gets answered
      by ratio instead.
    - **The memo** (`PL-MMVF`). Every `merge-base` this module issues is asked
      exactly three times - `_unlanded_refs` runs once for each of
      `branches_in_flight`, `orphaned` and `cuts_in_flight` - so two of every
      three are removed by remembering the answer. **An answer, and never a
      silence** (`PL-MM7F`): a failure stored here would be served to every
      later caller asking the same question, which turns one transient fault
      into a permanent wrong answer for the rest of the command and takes away
      the one thing that would have corrected it - the next caller asking git
      again. What that costs is bounded by the memo's own saving and paid only
      where git is failing: measured on this repository 2026-09-19, one digest
      put 237 questions to git and the memo answered 106 of them, so a command
      in which *every* call failed would spawn those 106 processes rather than
      reuse them. A checkout without git fails each in microseconds, and one
      whose git hangs is already paying the ten-second timeout 131 times before
      this change, so the memo was never what made that case survivable.
    - **The blob batch** (`PL-0J9K`). `git show <rev>:<path>` is one process
      per blob and the module asks for one per item file edited on an unmerged
      ref; `git cat-file --batch` answers all of them from one.
    """

    def __init__(self, *, memoize: bool = True, batch_blobs: bool = True) -> None:
        self._memoize = memoize
        self._batch_blobs = batch_blobs
        self._memo: dict[tuple[tuple[str, ...], str], str] = {}
        self._asked: Counter[str] = Counter()
        self._ran: Counter[str] = Counter()
        self._seconds: dict[str, float] = {}
        self._distinct: dict[str, set[tuple[str, ...]]] = {}
        self._processes = 0
        self._batch: dict[str, subprocess.Popen[bytes]] = {}
        self._unbatchable: set[str] = set()

    def __call__(self, args: list[str], root: Path) -> str:
        argv = tuple(args)
        sub = _subcommand(argv)
        self._asked[sub] += 1
        self._distinct.setdefault(sub, set()).add(argv)
        key = (argv, str(root))
        memoizable = self._memoize and sub in _READ_ONLY
        if memoizable:
            remembered = self._memo.get(key)
            if remembered is not None:
                return remembered
        elif sub not in _READ_ONLY:
            # Anything this module cannot prove is a read may have changed what
            # the memo holds - `fetch` certainly has - so the memo goes rather
            # than being reasoned about per subcommand.
            self._memo.clear()
        started = time.perf_counter()
        text = self._serve(argv, root)
        self._seconds[sub] = self._seconds.get(sub, 0.0) + (time.perf_counter() - started)
        self._ran[sub] += 1
        if memoizable and answered(text):
            # Only an answer is worth remembering. A silence memoized is one
            # transient fault amortised across the whole command - and it
            # removes the single thing that would otherwise make such a fault
            # self-correcting, which is that the next caller asks git again
            # (`PL-MM7F`).
            self._memo[key] = text
        return text

    def _serve(self, argv: tuple[str, ...], root: Path) -> str:
        """The answer, from the blob batch where it can come from there."""
        if self._batch_blobs and len(argv) == 2 and argv[0] == "show" and ":" in argv[1]:
            served = self._blob(argv[1], root)
            if served is not None:
                return served
        self._processes += 1
        return _run_git(list(argv), root)

    def _blob(self, spec: str, root: Path) -> str | None:
        """One blob from the batch, or `None` for "ask `git show` instead".

        `None` is the whole safety of this: every shape the batch cannot answer
        exactly as `git show` would - a tree or a commit, which `git show`
        formats and `cat-file` returns raw; a spec carrying the newline the
        protocol delimits on; bytes that will not decode; a batch that died -
        falls back to the process it replaced rather than being guessed at.

        A *missing* path is not one of those. `git show` exits non-zero there
        and `_run_git` turns that into the empty string, so the `missing` line
        the batch prints returns the same empty string and every caller's
        absent-blob path keeps working unchanged.
        """
        if "\n" in spec:
            return None
        stream = self._process(root)
        if stream is None:
            return None
        try:
            assert stream.stdin is not None and stream.stdout is not None
            stream.stdin.write(spec.encode(_ENCODING) + b"\n")
            stream.stdin.flush()
            header = stream.stdout.readline()
        except (OSError, ValueError, UnicodeEncodeError):
            self._drop(root)
            return None
        if not header:
            self._drop(root)
            return None
        fields = header.split()
        if len(fields) >= 2 and fields[-1] == b"missing":
            return ""
        if len(fields) != 3:
            self._drop(root)
            return None
        try:
            size = int(fields[2])
        except ValueError:
            self._drop(root)
            return None
        try:
            body: bytes = stream.stdout.read(size)
            stream.stdout.read(1)  # the newline git writes after every object
        except (OSError, ValueError):
            self._drop(root)
            return None
        if fields[1] != b"blob" or body is None or len(body) != size:
            return None
        try:
            decoded = body.decode(_ENCODING)
        except UnicodeDecodeError:
            return None
        # What `subprocess.run(text=True)` would have done to the same bytes.
        return decoded.replace("\r\n", "\n").replace("\r", "\n")

    def _process(self, root: Path) -> subprocess.Popen[bytes] | None:
        """The batch process for this root, started on first use."""
        held = str(root)
        running = self._batch.get(held)
        if running is not None:
            return running
        if held in self._unbatchable:
            return None
        try:
            started = subprocess.Popen(
                ["git", "cat-file", "--batch"],
                cwd=root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, ValueError):
            self._unbatchable.add(held)
            return None
        self._processes += 1
        self._batch[held] = started
        return started

    def _drop(self, root: Path) -> None:
        """Forget a batch that answered in a shape this cannot read."""
        held = str(root)
        self._unbatchable.add(held)
        dead = self._batch.pop(held, None)
        if dead is not None:
            _close(dead)

    def close(self) -> None:
        """End every batch process this runner started.

        Idempotent, and called whether or not the command succeeded: the one
        thing a `cat-file --batch` must not do is outlive the command that
        opened it.
        """
        for dead in self._batch.values():
            _close(dead)
        self._batch.clear()

    def __enter__(self) -> GitRunner:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def profile(self, walk: RefWalk) -> GitProfile:
        """What has been asked so far, against the input it was asked about."""
        costs = tuple(
            sorted(
                (
                    SubcommandCost(
                        subcommand=sub,
                        asked=asked,
                        ran=self._ran.get(sub, 0),
                        distinct=len(self._distinct.get(sub, ())),
                        seconds=self._seconds.get(sub, 0.0),
                    )
                    for sub, asked in self._asked.items()
                ),
                key=lambda cost: (-cost.seconds, cost.subcommand),
            )
        )
        return GitProfile(
            asked=sum(self._asked.values()),
            ran=sum(self._ran.values()),
            processes=self._processes,
            seconds=sum(self._seconds.values()),
            by_subcommand=costs,
            walk=walk,
        )


def _close(process: subprocess.Popen[bytes]) -> None:
    """Shut one batch process down without letting its death raise."""
    try:
        if process.stdin is not None:
            process.stdin.close()
        process.wait(timeout=5)
    except (OSError, ValueError, subprocess.SubprocessError):
        try:
            process.kill()
        except OSError:
            pass


BRANCH_ID_RE = re.compile(
    r"(?:^|[/_-])(pl-(?:\d{3}|[0-9bcdfghjklmnpqrstvwxyz]{4}))(?:$|[/_-])", re.I
)

# The ids at the *front* of a commit subject, and only there. `CLAUDE.md`
# requires the id of the work to lead every implementation subject, so an id
# that leads is the branch's own work while one mentioned further in is
# usually somebody else's: measured over 120 commits of this project's `main`,
# 79 subjects contained an id and 64 led with one, and all 15 of the
# difference were captures, close-outs or merges rather than implementation.
#
# So matching an id anywhere in a subject would report roughly 19% false
# positives, and a false positive here is worse than the blindness it would
# cure - it makes `docket next` skip an item that is startable, which is the
# opposite of the defect. `PL-F5HB Close it out; triage PL-4CW7 with the
# environment fix applied` is the case in miniature: the leading id is the
# work, the mentioned one had merely been triaged.
#
# A subject may lead with more than one id, because one branch may carry two
# items (`PL-N7R9, PL-J295: the pull request stops being a question`), so the
# whole leading run is read rather than only its first id.
LEADING_IDS_RE = re.compile(rf"^\s*{ID_PATTERN}(?:\s*(?:,|&|and)\s*{ID_PATTERN})*", re.I)
ANY_ID_RE = re.compile(ID_PATTERN, re.I)

# An item file is named `<id>-<slug>.md`, so the id can be read from a tree
# listing or from a diff without opening anything. The id grammar comes from
# `store` rather than being spelled again here: two spellings of it would drift,
# and the one that drifted would silently stop recognising items.
ITEM_FILE_RE = re.compile(rf"^({ID_PATTERN})-")

# One line per commit: the ref that reached it, when it was committed, the
# parents this checkout holds, its hash, and its subject. `%S` needs
# `--source`, and the unit separator is used as the delimiter because a subject
# can contain anything a keyboard can type. `%p` is empty for a commit whose
# parents this checkout does not have, which is how a walk that ran off the end
# of a truncated history is told from one the default branch stopped.
#
# The full timestamp rather than the day, and the hash rather than nothing,
# because `precedence` has to put two branches in a single order that both of
# their sessions compute identically. Two sessions start minutes apart, so a
# day cannot separate them, and two commits can share a second - which is what
# the hash is there to break. A branch's age is read from the same timestamp,
# and for the same reason: an age cut to the day cannot separate a session that
# committed three minutes ago from a branch that sat all night, and across
# midnight it reads the first as the second (`PL-3QM9`).
COMMIT_FORMAT = "--format=%S%x1f%cI%x1f%p%x1f%H%x1f%s"


@dataclass(frozen=True)
class Branch:
    """One ref that is carrying an item's work.

    `last_commit` is when the newest commit the ref holds that the default
    branch does not was made - the full timestamp git wrote, offset and all,
    because the age a reader judges a branch by is measured in minutes while a
    session is live and in days once it is not (`PL-3QM9`) - or `None` when
    this checkout could read none of them: a branch created but not yet
    committed on, or one whose commits sit beyond a truncated clone's horizon.

    **`on_base` changes what a reader is told, never whether the claim is
    made** (`PL-3CTW`). A capture commit that also reaches outside the queue
    claims the ids it merely filed, because `CLAUDE.md` requires both the
    leading id and the capture - so the collision is produced by following the
    rules. Withdrawing such a claim was measured at three widths against the
    913 `(commit, id)` claims in `origin/main`'s history and refused at every
    one: the widest takes 263, of which 221 create the item at `done`,
    `dropped`, `ready`, `needs-decision` or `blocked` - an item filed *and
    finished* on one branch, which is the housekeeping rule, the
    behavior-change rule and the fix-now door each being kept. Narrowing it to
    ids the branch still calls `untriaged` takes 22, and 12 of those did the
    item's own work. No `touches` test separates them either: the motivating
    commit carries `vcs.py`, which is the first path its captured item
    declares. So nothing is taken away, and the mark goes on failing toward
    itself the way `_annotates_only` and `PL-PRHN` chose.

    What was wrong is only the wording. An item the default branch has no copy
    of is in no other session's store, so nothing can offer it and "do not
    start these again" refuses work that was never on offer - about the very
    branch `bin/docket stranded` is telling the reader to recover it from.
    `PL-G5ZH` sat in both readings at once on 2026-09-19.
    """

    name: str
    item_id: str
    last_commit: datetime | None = None
    #: Whether the default branch holds this item's file at all. `True` for an
    #: item a reader could actually start, which is every claim the older
    #: reading was right about.
    on_base: bool = True


@dataclass(frozen=True)
class QueueEdit:
    """One ref that has already changed an item's own file in the queue.

    **The weaker of the two marks, and a separate type so that no caller can
    mistake it for the stronger one.** `Branch` says a ref is *working* an
    item, which is what `docket next` excludes on; this says only that a ref
    has written to `docs/items/<id>-*.md`, which is what a second write to
    that file collides with. A triage pass, a capture, a `docket record` write
    and a note added to a brief all produce the second without the first, and
    before this they produced nothing at all - so two sessions triaging one
    item could each fetch, each run `show`, and each be told correctly that
    nothing was in flight (`PL-N1JK`).

    Structurally identical to `Branch` and deliberately not `Branch`: the two
    answer different questions, and a `QueueEdit` reaching a reader that wants
    work in flight - `plan.recommend`, `files_in_flight` - would undo
    `PL-X3WZ`. Distinct types make that a type error rather than a judgment
    call at each call site.
    """

    name: str
    item_id: str
    last_commit: datetime | None = None


@dataclass(frozen=True)
class FlightReport:
    """Which items are in flight, and which refs could not be read to find out.

    `unreadable` is why this is a type rather than a list. A ref whose commits
    this checkout cannot compare with the default branch contributes nothing
    from them, and silence about it would present a partial reading as a
    complete one - the same collapse `PullRequestHistory.declined` guards
    against, per ref rather than for the whole check, because one unreadable
    ref does not stop the others from being read.

    Two things put a ref there, and a truncated clone is behind both: no
    merge-base with the default branch that this checkout can resolve, and a
    commit walk that ran off the end of the history instead of stopping
    against the default branch. The second is not implied by the first -
    `_unmerged_commits` has the argument - so a ref answering the merge-base
    is not thereby answerable.

    **It names what went unread, not a ref that was skipped, so a ref can sit
    in both halves at once.** What the checkout could not read is the commits;
    a branch named `claude/pl-k7qx-short-slug` still names its item, and that
    read needs no history. Such a ref appears in `branches` for the id its name
    proves *and* in `unreadable` for the ids its commits might have added.

    **Every caller takes the ids from here rather than from a function that
    returns them alone.** A `set[str]` is the natural shape for ranking and
    marking, and it is exactly the shape that cannot say "and one ref went
    unread" - so a caller handed one presents a partial reading as a complete
    one, which is the collapse this type exists to prevent. `ids` is a
    property of the report for that reason: the gap travels with the answer,
    and a caller that wants to ignore it has to do so in writing.
    """

    branches: tuple[Branch, ...] = ()
    unreadable: tuple[str, ...] = ()
    #: Unlanded refs this checkout read perfectly well and could attribute to
    #: no item at all - no id in the name, and none at the front of any commit
    #: subject. The third outcome of the read, and until `PL-B73C` there was
    #: nowhere for it to go: such a ref was dropped, so the report was complete
    #: about what it could not read and silent about work it could.
    #:
    #: Reported with no suppression rule, on a count rather than an argument.
    #: The decline of 2026-09-04 rested on `origin/Review_articles` being one
    #: such ref and a line about it therefore appearing in every session for as
    #: long as it existed; `PL-JX2T` closed it, the branch is gone, and on
    #: 2026-09-14 none of the remote's ten non-default heads is unattributed.
    #: `tools/branch_id_check.py` is what holds that: it fails a `claude/*`
    #: branch of one's own that names no id. So the steady state is empty by
    #: construction and there is nothing for an age, a push-date floor or an
    #: allow-list to suppress. Should a line start appearing that nobody acts
    #: on, `CLAUDE.md`'s retirement test governs this like any other check.
    unattributed: tuple[str, ...] = ()
    #: Refs that have edited an item's file without claiming to work it, for
    #: the items no `Branch` already accounts for. Disjoint from `branches` by
    #: construction: where both would fire the stronger mark is the one a
    #: reader needs, and printing two lines about one item invites the reading
    #: that they mean different branches.
    editing: tuple[QueueEdit, ...] = ()
    base: str = ""
    #: Why this reading is partial: git was asked something and did not answer.
    #:
    #: **Distinct from `unreadable`, and the two are not substitutes.** That
    #: names a ref whose *history* this checkout does not hold, which is the
    #: normal state of an agent session's shallow container and says nothing
    #: about git having worked. This says a call failed - a ref deleted between
    #: the `for-each-ref` that listed it and the `diff` that read it, a timeout,
    #: no git at all - so every mark here was collected from an incomplete read
    #: and the absence of a mark proves nothing.
    #:
    #: The marks are kept rather than withheld, because the error that costs
    #: least is over-reporting: an item wrongly marked costs a session one look,
    #: and one wrongly unmarked costs two sessions a merge conflict.
    declined: str = ""

    @property
    def ids(self) -> frozenset[str]:
        """The items this checkout proved are in flight, for ranking and marking."""
        return frozenset(branch.item_id for branch in self.branches)

    @property
    def known(self) -> bool:
        """Whether git answered every question this reading rests on."""
        return not self.declined


def leading_ids(subject: str) -> list[str]:
    """Every item id in the run of them a commit subject opens with."""
    match = LEADING_IDS_RE.match(subject)
    if match is None:
        return []
    return [found.group(0).upper() for found in ANY_ID_RE.finditer(match.group(0))]


@dataclass(frozen=True, order=True)
class Stake:
    """When a ref said it was carrying an item, and the commit that said so.

    Ordered, and ordered on the hash after the time, because that is the whole
    job: two branches carrying one item have to be put in an order both of
    their sessions compute identically, and two commits made in the same second
    would otherwise be a tie nobody can break. The hash is arbitrary as a
    ranking and total as an order, which is the property wanted here - an
    arbitrary answer both sessions reach is worth more than a principled one
    they reach differently.
    """

    when: datetime
    commit: str


# Sorts a carrier with no readable stake behind every carrier that has one,
# without ever being compared against a real one: the flag ahead of it in the
# sort key separates the two groups first. Aware, so that a comparison against
# one of these does not raise if a later change puts them side by side.
_UNDATED = Stake(when=datetime.min.replace(tzinfo=UTC), commit="")

# Earlier than any commit git can write, and aware for the reason `_UNDATED`
# is: every timestamp compared against it comes from `%cI`, which carries its
# offset.
_EARLIEST = datetime.min.replace(tzinfo=UTC)


@dataclass(frozen=True)
class _Walk:
    """What one pass over the unlanded refs produced.

    Six readings of the same commits. They are kept together because they come
    from one `git log`: separating them into functions of their own would mean
    walking the history once per question, and the questions are asked together
    every time.
    """

    #: Per ref, when its newest unlanded commit was made - the timestamp, not
    #: the day, so an age can be told to the minute (`PL-3QM9`).
    last: dict[str, datetime]
    #: Per item id, every ref whose commit subjects led with it, ordered by
    #: candidate rank. **Every carrier rather than the nearest**, because the
    #: guards that judge a claim judge it per *ref*: collapsing here put a
    #: spent claim on a bystander branch in front of a live one, and
    #: `_taken_on_base` finding the bystander's claim spent then deleted the
    #: id for both (`PL-2BZY`). The first entry is the one a reader is shown,
    #: which is all the collapse ever decided.
    ids: dict[str, tuple[str, ...]]
    #: Refs at least one of whose commit subjects opened with an item id, read
    #: before `_annotates_only` has a say. `ids` answers "who is working what";
    #: this answers the weaker question "is this ref attributable to anything
    #: at all", which is what separates a capture push from a ref nobody can
    #: name (`PL-B73C`). A ref appears here and contributes no claim whenever
    #: its whole diff sits in the queue.
    named: set[str]
    #: Per item id, every ref whose commits changed its file and the path each
    #: changed, ordered by candidate rank. The path rides along because the
    #: mark is only worth raising where the edit is still unmerged, which
    #: `branches_in_flight` tests against the base rather than taking on trust
    #: (`PL-8MJ3`).
    #:
    #: **Every carrier rather than the nearest**, for the reason `ids` keeps
    #: every claim: the test that decides whether an edit is still worth
    #: reporting is `_superseded`, which is a fact about one *ref's* copy of
    #: one path. Collapsing here let a bystander branch whose copy had landed
    #: take a live edit's mark with it, and the id left `editing` entirely
    #: (`PL-RY2R`). One path per ref, the newest the walk saw, which is all the
    #: collapse ever decided within a ref; the head of the list is the carrier
    #: a reader is shown where nothing removes it.
    edited: dict[str, tuple[tuple[str, str], ...]]
    #: Per ref and item id, the newest queue-only commit that both led with the
    #: id and changed that id's own file, with the item paths it changed - a
    #: commit *about* an item that wrote *into* it. That is what a decision
    #: recorded into the item it decides looks like, what a grooming pass
    #: dropping an item looks like, and also what a capture and a note written
    #: into a brief look like; the walk cannot tell them apart and does not
    #: try. `_own_edit_claims` reads the item off the base, and the commit's
    #: parent or the ref's tip, to decide for both `branches_in_flight` and
    #: `precedence` (`PL-7790`, `PL-VYSP`, `PL-8FJK`). Never populated for a
    #: commit that reached past the queue, whose claim `ids` already carries.
    own_edits: dict[tuple[str, str], tuple[str, tuple[str, ...]]]
    #: The earliest such commit per ref and id, dated the way `staked` dates a
    #: claim, so that two design rounds on one item can be ordered.
    own_staked: dict[tuple[str, str], Stake]
    staked: dict[tuple[str, str], Stake]
    #: The *newest* claiming commit per ref and id, where `staked` keeps the
    #: earliest. The two answer opposite questions and both are needed: when a
    #: ref began carrying an item is what orders two sessions against each
    #: other, and when it last said so is what says whether a merge that took
    #: the id could have taken this ref's work (`PL-8JQQ`). A ref that goes on
    #: committing under an id after its own pull request squash-merged is the
    #: shape that needs it, and it is the shape every long-lived branch here
    #: eventually takes.
    claimed_last: dict[tuple[str, str], Stake]
    opened: dict[str, Stake]
    unbounded: set[str]


def _annotates_only(paths: list[str], prefix: str) -> bool:
    """Whether a commit's whole diff sits inside the queue directory.

    **The rule that separates recording an item from working on it**, and it
    is deliberately about where the commit wrote rather than about what it
    wrote there. `CLAUDE.md` requires a finding to be captured before a session
    ends, requires the leading id on every commit subject, and requires a
    behavior change to land in the session that asks for it - so a capture, a
    triage pass, a `docket record` write and a note added to a brief all lead
    with an id they are not implementing. Reading their subjects alone marked
    the item as work somebody held, and `docket next` withheld it from every
    session until the branch merged, which for a branch nobody merges is
    forever (`PL-X3WZ`).

    Measured over the eight false marks that item recorded: every one is a
    commit whose entire diff is inside the queue directory, and the one branch
    genuinely implementing an item is not. Nothing finer was needed - no
    frontmatter-versus-body parse, which would in any case have failed on the
    capture and triage commits, since both write frontmatter.

    **It fails toward keeping the mark, and both of its silences do.** A commit
    with no paths at all is a merge - `--name-only` prints none for one - or a
    read that went wrong, and neither is evidence of annotation, so an empty
    list is not annotation. A path git quoted, which it does for one carrying
    non-ASCII bytes, fails the prefix test and lands the same way. That is the
    cheaper error of the two available: an item wrongly left marked is one a
    session picks around, while an item wrongly unmarked is two sessions on one
    piece of work (`PL-PRHN`).

    **What it withholds is the claim to be *working* an item, which is all it
    was ever asked to withhold.** A commit that only annotates still edited
    that item's file, and a second session editing the same file collides at
    merge whatever either commit was for - so `_item_file_ids` reads the same
    paths for that weaker fact and `FlightReport.editing` carries it. Two
    sessions triaged one pair of items on 2026-09-06 and the merge discarded
    one of the two answers: a triage pass has by definition no diff outside
    the queue, so it could never raise the mark this function withholds, and
    no amount of care with `show` or `flight` would have surfaced it
    (`PL-N1JK`). Nothing here is relaxed to fix that - `docket next` still
    ranks on `FlightReport.branches` alone, which is `PL-X3WZ`'s reading
    intact.

    The residual case it cannot see is a session that *starts* an item by
    pushing only a `touches` fill or a `verify:` command, which is annotation
    by this rule and a claim in fact. **Three shapes of it are recovered a
    level up, and none of them here.** `_unmerged_commits` records one shape - a
    queue-only commit leading with an id and changing that id's own file - and
    `_own_edit_claims` promotes it back to a claim where the item says the
    queue edit is the work:

    - **Its whole deliverable is a queue edit** (`PL-7790`): `_queue_only_work`
      reads the item's own declared `touches`, so a tag item, a triage item
      or a recovery item is a claim.
    - **It is at `needs-decision`** (`PL-VYSP`). Its next step is a decision,
      and a decision is recorded into the item file - so a design round may
      never produce a diff outside the queue at all, and this test withheld
      its claim for the whole life of the work. `bin/docket show PL-BHVM`
      called that item startable on 2026-09-19 while a live session held it
      with three `PL-BHVM` commits pushed; the mark appeared only when the
      round happened to edit `ROADMAP.md`.
    - **The branch closes it while the base holds it open** (`PL-8FJK`). A
      grooming pass closes items, and "nothing finer was needed" above was
      measured on eight marks none of which closed anything: `#914` dropped
      `PL-027`, `PL-043` and `PL-ZBR6` in queue-only commits leading with each
      id, and `docket next` went on offering all three.

    Nothing changes in this test, deliberately: it answers "did this commit
    reach past the queue", which is a fact about the commit, and each
    promotion answers a question about the item - where its work lives, what
    its status is on the base, what the branch has made it. Reading them in
    one place is what made the two path-level refinements fail.

    What is left is a session filling in the `touches` of an item whose work is
    elsewhere, which stays unmarked until its first commit outside the queue -
    though `show` reports the file edit underneath, which is the warning that
    case previously had nowhere to come from. The start procedure's empty
    commit, which this test reads as work, is what claims such an item.
    """
    return bool(paths) and all(path.startswith(prefix) for path in paths)


def _item_files(paths: list[str], prefix: str) -> list[tuple[str, str]]:
    """The items whose own file a commit changed, as `(id, path)`, read from the paths alone.

    **The path is returned beside the id because the mark has to be checked
    against the base before it is believed** (`PL-8MJ3`). Which file a commit
    changed is a fact about that commit and says nothing about whether the
    change is still only on the branch - so the id alone was enough to raise the
    mark and never enough to keep it.

    **The weaker of the two readings this walk makes, and the one that infers
    nothing.** `_annotates_only` and `leading_ids` between them decide what a
    commit was *for*, which is a judgment about a subject; this decides which
    item files it *changed*, which is a measurement of a diff. The second is
    what a merge conflict is actually made of, so it is what a session about to
    edit the same file needs (`PL-N1JK`).

    The store names each file for its item - `docs/items/PL-K7QX-do-it.md` - so
    the id is the head of the basename, and `store.filename_for` is what
    guarantees it. `ITEM_FILE_RE` is the same constant `_items_at` reads a tree
    listing with, for the reason stated where it is defined: two spellings of
    one id format are two answers waiting to disagree.

    **It fails toward silence where `_annotates_only` fails toward the mark**,
    and the directions differ because the costs do. A path git quoted for its
    non-ASCII bytes, or a store outside the repository whose prefix no path can
    match, drops the edit rather than inventing one. What is lost is an
    advisory a session would have picked around; what a false one costs is a
    session told to leave alone an item nobody is holding.
    """
    found: list[tuple[str, str]] = []
    for path in paths:
        if not path.startswith(prefix):
            continue
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
        if match is not None:
            found.append((match.group(1), path))
    return found


def _unmerged_commits(
    refs: list[str], base: str, root: Path, run: Runner, *, items_dir: str = "docs/items"
) -> _Walk:
    """The newest commit day per ref, the ref leading with each id, and what went unread.

    One `git log` covers every ref at once: `--source` reports which ref on the
    command line reached each commit, so the walk that finds the ids also dates
    the branches.

    **Which ref a shared commit is credited to is decided here, not by git.**
    `--source` names *a* ref that reached each commit and promises nothing about
    which, and measured on this repository it varies per commit inside a single
    walk: on 2026-09-04, with `claude/next-workflow-item-knjkkt` and its tracking
    ref holding identical history, one walk credited the branch's newest
    `PL-YHD3` commit to the local ref and its oldest to `origin/...`
    (`PL-R6D8`). So a commit two refs share - a local branch and its own
    tracking ref - is attributed by *candidate order* instead, which prefers the
    local branch: the id is kept against the earliest ref that accounts for it,
    and the order the caller passed is the order it will report in.

    `branches_in_flight` survives git's own answer, because it needs only some
    ref per id, which is why this was never visible as a bug. What it cost is
    smaller and real: `flight` and `triage` printed whichever ref the walk
    happened to credit, so a session could be shown `origin/claude/...` for work
    its own local branch was carrying - the exact confusion those lines exist to
    remove. A docstring claiming git guaranteed it was the worse half, because
    the next reader builds on it, and `PL-YHD3`'s `precedence` did.

    **A walk must stop because the default branch accounted for what came next,
    never because the checkout ran out of history.** `^base` excludes only the
    commits this checkout can reach *from* `base`, and in a truncated clone
    `base`'s own history ends at a grafted commit - so everything below that
    graft goes unexcluded. A ref reaching round it, which a merge of the
    default branch into a branch is enough to do, then has the default
    branch's own commits reported as its work and the ids leading their
    subjects reported as items somebody is implementing. A merge-base that
    resolves does not rule this out: it proves the two share *a* commit this
    checkout can see, never that the walk can see the rest.

    The signature is a commit with no parents in this checkout. A walk that
    emits a parentless commit ran off the end of a grafted history, so nothing
    it produced is proven and the ref it belongs to is returned as unread. The
    repository's true root reads the same way and is answered the same way -
    it sits on the default branch, so a walk reaching it is one `base` failed
    to exclude. Reading the commits is what settles this rather than
    `is_shallow`, so a git too old to say whether the checkout is truncated is
    guarded too.

    **The converse does not hold, and the limit is accepted rather than
    unnoticed** (`PL-W1LN`, decided with the project owner 2026-09-13). A walk
    that ends against a commit `base` excluded is *not* thereby proven: where
    the default branch reaches the root down one path and is grafted on
    another, a single `--depth` truncates unevenly, and a branch forked from a
    commit below the graft descends through commits `^base` cannot exclude
    before terminating against the fork point the *short* path still reaches.
    Every commit it emits carries a parent, so this signature stays silent.
    Reproduced end to end in
    `subprojects/docket/tests/test_cli.py::test_flight_reports_below_an_uneven_horizon_which_is_the_accepted_limit`,
    where three of the default branch's own commits are reported as work a
    branch is carrying.

    It is accepted because no *sound* replacement exists inside a truncated
    checkout: the decisive question is whether an emitted commit is one the base
    reaches in the **full** history, and the commits that would answer it are
    exactly the ones the clone does not hold. Naming a ref unread whenever the
    base is grafted is sound and would silence this read in every agent
    container, which is the common case rather than the exotic one; fetching to
    deepen would answer it exactly and breaks the rule that these commands run
    from a bare tree with no network; distrusting a commit older than the base's
    newest graft would cover it cheaply on commit dates, which a rebase moves.
    The test pins the behaviour so that changing it is a decision rather than an
    accident.

    **`staked` and `opened` keep the *earliest* commit where the rest keeps the
    newest**, and the difference is which question each answers. How long a
    branch has been sitting is a question about its last commit; when a branch
    began carrying an item - the only fact two sessions can order themselves by
    - is a question about its first. `staked` dates the claim a commit subject
    makes, per ref and per id, so a branch that picked up a rider is dated from
    the rider rather than from its own first commit; `opened` dates the branch
    itself, which is the claim a branch *name* makes from the moment there is
    anything on it.

    **`ids` and `staked` read the commit's diff as well as its subject**, and
    `opened` does not. A leading id says which item a commit concerns, never
    that the commit implements it, so `_annotates_only` withholds the ones
    whose whole diff sits in the queue directory - a capture, a triage pass, a
    recovered item, a note written into a brief. `opened` is the claim a branch
    *name* makes, which no diff qualifies.

    **`edited` reads the diff and nothing else.** Which item files a commit
    changed is a fact about paths, so it is neither withheld by
    `_annotates_only` nor taken from the subject at all: a commit leading with
    one id, or with none, still collides with a second edit to the file it
    changed. It is the weaker claim of the two, and `branches_in_flight` keeps
    it apart from the stronger one for exactly that reason.
    """
    if not refs:
        return _Walk(
            last={},
            ids={},
            named=set(),
            edited={},
            own_edits={},
            own_staked={},
            staked={},
            claimed_last={},
            opened={},
            unbounded=set(),
        )
    # `--name-only` rather than a `git show --stat` per commit, and that is the
    # whole reason the diff can be read at all here. This walk is on the hot
    # path of `next`, `list`, `triage`, `status` and the session-start digest,
    # so a subprocess per commit would have put the read out of reach; asking
    # the walk that is already running to also name the paths costs one pass
    # over the same trees. Measured on this repository: 4.6 ms to 8.8 ms over
    # 50 commits, 9.5 ms to 25.1 ms over 200 - against roughly 4 ms of process
    # spawn *each* for the per-commit form.
    #
    # The trailing `--` is what keeps a branch sharing a name with a file from
    # being read as a path, which git refuses to guess at and answers with an
    # error - and every error here collapses to "nothing known".
    output = run(["log", "--source", COMMIT_FORMAT, "--name-only", f"^{base}", *refs, "--"], root)
    prefix = items_dir.strip("/") + "/"
    last: dict[str, datetime] = {}
    claimed: dict[str, list[str]] = {}
    named: set[str] = set()
    edited: dict[str, list[tuple[str, str]]] = {}
    own_edits: dict[tuple[str, str], tuple[str, tuple[str, ...]]] = {}
    own_staked: dict[tuple[str, str], Stake] = {}
    staked: dict[tuple[str, str], Stake] = {}
    claimed_last: dict[tuple[str, str], Stake] = {}
    opened: dict[str, Stake] = {}
    unbounded: set[str] = set()

    # A commit's paths follow its formatted line, so the claim it makes cannot
    # be judged until the next commit begins or the output ends. Only the id
    # half is held back: the dates and the parentless-commit guard are
    # properties of the commit itself and are read where they are parsed.
    pending: tuple[str, Stake | None, str, str] | None = None
    paths: list[str] = []

    # Candidate order is what settles a commit two refs share, since `--source`
    # will not: the caller lists local branches before their tracking refs, so
    # the lower rank is the one a reader wants to be shown. It orders each id's
    # carriers now rather than choosing between them, which is what the per-ref
    # guards downstream need (`PL-2BZY`, `PL-RY2R`).
    rank = {name: position for position, name in enumerate(refs)}

    def credit_claims() -> None:
        """Credit the held commit's leading ids, unless its diff only annotates."""
        if pending is None:
            return
        ref, stake, subject, commit = pending
        leading = leading_ids(subject)
        item_files = _item_files(paths, prefix)
        # Credited before the annotation test and never withheld by it: an
        # annotating commit is not work, and it has still written to the file a
        # second session is about to write to.
        for identifier, path in item_files:
            # Appended rather than compared against a held carrier, for the
            # reason the claims below are: `_superseded` judges an edit per
            # ref, so every ref that edited the file has to reach the caller
            # (`PL-RY2R`). One entry per ref - the first the walk offers, which
            # is its newest commit - keeps what the comparison decided *within*
            # a ref, where a round that renames the file changes two paths.
            editors = edited.setdefault(identifier, [])
            if all(name != ref for name, _ in editors):
                editors.append((ref, path))
        # Before the annotation test, deliberately: a capture, a triage pass
        # and a `docket record` write all name the item they concern, and a
        # ref that has done one of those is attributable even though it claims
        # nothing. Only a ref that names nothing anywhere is unattributed.
        if leading:
            named.add(ref)
        if _annotates_only(paths, prefix):
            # The one annotation shape a reader can promote: the commit led
            # with an id and wrote that id's own file. Recorded as a shape
            # only; whether it is a design round, a capture or a note is for
            # the callers, who read the item's status off the base and the
            # path off the commit's parent (`PL-VYSP`). Every path the commit
            # changed for the id rides along, because a round that renames the
            # file changes two.
            for identifier in leading:
                own_paths = tuple(path for found, path in item_files if found == identifier)
                if not own_paths:
                    continue
                # Newest first is the walk's order, so the first commit seen
                # per ref and id is the one kept.
                own_edits.setdefault((ref, identifier), (commit, own_paths))
                if stake is not None:
                    held = own_staked.get((ref, identifier))
                    if held is None or stake < held:
                        own_staked[(ref, identifier)] = stake
            return
        for identifier in leading:
            # Appended rather than compared against a held carrier: which ref
            # is *reported* is settled by rank at the end, and which refs claim
            # the id at all is what the per-ref guards need (`PL-2BZY`).
            carriers = claimed.setdefault(identifier, [])
            if ref not in carriers:
                carriers.append(ref)
            if stake is not None:
                held = staked.get((ref, identifier))
                if held is None or stake < held:
                    staked[(ref, identifier)] = stake
                # The other end of the same claim, and compared rather than
                # taken from the walk's order: newest-first is git's habit
                # rather than its promise, and this end decides whether a
                # merge could have taken the ref's work (`PL-8JQQ`).
                newest = claimed_last.get((ref, identifier))
                if newest is None or newest < stake:
                    claimed_last[(ref, identifier)] = stake

    for line in output.splitlines():
        parts = line.split("\x1f", 4)
        if len(parts) != 5:
            # Everything that is not a commit line is one of that commit's
            # paths, or the blank line git writes between the two. A path can
            # no more carry four unit separators than a subject can, so the
            # field count keeps the two apart without a second delimiter.
            if line.strip():
                paths.append(line.strip())
            continue
        credit_claims()
        pending, paths = None, []
        ref, committed, parents, commit, subject = parts
        if not parents.strip():
            unbounded.add(ref)
        try:
            when: datetime | None = datetime.fromisoformat(committed)
        except ValueError:
            # A date this checkout's git wrote in some other shape. The commit
            # still names whatever it names, so the ids are read from it as
            # before and only the ordering loses a data point - the direction
            # that reports less rather than the one that reports wrongly.
            when = None
        stake = None if when is None else Stake(when=when, commit=commit)
        if when is not None and when > last.get(ref, _EARLIEST):
            last[ref] = when
        if stake is not None:
            first = opened.get(ref)
            if first is None or stake < first:
                opened[ref] = stake
        pending = (ref, stake, subject, commit)
    credit_claims()
    return _Walk(
        last=last,
        ids={
            identifier: tuple(sorted(carriers, key=lambda name: rank.get(name, len(refs))))
            for identifier, carriers in claimed.items()
        },
        named=named,
        edited={
            identifier: tuple(sorted(carriers, key=lambda pair: rank.get(pair[0], len(refs))))
            for identifier, carriers in edited.items()
        },
        own_edits=own_edits,
        own_staked=own_staked,
        staked=staked,
        claimed_last=claimed_last,
        opened=opened,
        unbounded=unbounded,
    )


def _base_blobs(base: str, root: Path, run: Runner) -> frozenset[str]:
    """Every blob the default branch's history holds, read in one walk.

    The question each caller actually asks is per blob - has the default
    branch ever held this content - and `git log --find-object` answers it
    one blob at a time, walking the whole history for each. Listing the
    objects reachable from the base answers it for all of them at once, and
    the two agree by construction: a blob some commit on the base introduced
    is a blob some tree on the base holds.

    Measured on this repository at 425 commits: 17 `--find-object` walks cost
    0.62 s and this costs 0.033 s, so the *complete* split below is cheaper
    than the short-circuited all-or-nothing test it replaced.

    A truncated clone reaches fewer commits and so returns fewer blobs, which
    reads as "not landed" - the same safe direction `_landing_split` documents
    and the same one `--find-object` gave.
    """
    found: set[str] = set()
    for line in run(["rev-list", "--objects", base], root).splitlines():
        oid, _, path = line.partition(" ")
        # Only entries carrying a path are blobs or trees; a bare oid is a
        # commit. Trees cost a membership test that can never match, since
        # nothing compared against this set is a tree.
        if path.strip():
            found.add(oid.strip())
    return frozenset(found)


def _landing_split(
    ref: str, fork_point: str, base_blobs: frozenset[str], root: Path, run: Runner
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The paths a ref introduces, split into what the base holds and what it does not.

    Containment answers "has this branch landed" for a merge commit and never
    for a squash: the squash writes one new commit carrying the branch's
    *content* and none of its commits, so `--merged` calls the branch unmerged
    for as long as its ref survives, and every id leading one of its subjects
    reports in flight forever. GitHub deleting the head branch on merge is what
    usually hides that; a long-lived checkout that does not prune is where it
    bites.

    So the question asked here is about content rather than ancestry: of the
    blobs the ref adds to the tree it forked from, has the default branch held
    each one at some point? That is `stranded`'s rule - compare what the trees
    hold, never how the commits got there - pointed the other way, and it
    answers a rebase or a cherry-pick the same way it answers a squash.

    **The default branch's history, not its tip.** Comparing against the base
    tree alone would call a squash-merged branch unlanded again the moment
    anyone edited a file it had touched - which in this store is what the next
    triage pass does to every item a branch captured, so the branch would be
    back to reporting in flight one merge later. Asking whether the blob was
    ever on the default branch does not decay.

    **Both sides are returned, because two readers need opposite halves.**
    `_work_already_on_base` needs to know the outstanding side is empty;
    `orphaned` needs to know neither side is, which is what a branch looks like
    when its pull request took part of its work and something pushed the rest
    afterwards. Computing them separately would be two spellings of one
    question, and two spellings are two answers waiting to disagree.

    Two silences read as "not landed", which is the safe direction. A ref that
    adds no blob at all - one with no commits yet, one that only deletes, or
    one git could not read - and a blob whose landing sits below a truncated
    clone's horizon: both keep the ref in the report. Reporting a merged branch
    as in flight is the noise this removes; reporting a live session's branch
    as merged would hand its item to a second session, which is the collision
    the whole read exists to prevent.
    """
    landed: list[str] = []
    outstanding: list[str] = []
    for line in run(
        ["diff", "--raw", "--no-renames", "--no-abbrev", fork_point, ref, "--"], root
    ).splitlines():
        # `:<src mode> <dst mode> <src blob> <dst blob> <status>\t<path>`. The
        # fields end at the first tab, and everything after it is the path -
        # which can itself contain a tab, so it is taken whole rather than
        # split. git quotes a path it cannot print literally, and such a path
        # is reported the way git wrote it.
        head, _, path = line.partition("\t")
        fields = head.split()
        if len(fields) == 5 and set(fields[3]) != {"0"}:
            (landed if fields[3] in base_blobs else outstanding).append(path or fields[3])
    return tuple(landed), tuple(outstanding)


def _work_already_on_base(split: tuple[tuple[str, ...], tuple[str, ...]]) -> bool:
    """Whether everything a ref adds is content the default branch has held.

    `_landing_split` carries the reasoning; this is the all-or-nothing reading
    of it, kept as a named rule rather than spelled at the one call site so
    that `orphaned`'s reading of the same split sits beside it and the two can
    be compared. A ref introducing nothing has an empty landed side and reads
    as not landed, which is what keeps a branch with no commits yet in the
    report.
    """
    landed, outstanding = split
    return bool(landed) and not outstanding


#: How many bytes of pathspec one `git diff` may be handed at a time. Every
#: path a caller names goes on the command line, and the callers hand over
#: whole sets: a triage pass edits several hundred item files on one branch.
#:
#: **The split is a safety bound rather than a speed one.** An argv over the
#: platform's `ARG_MAX` makes `subprocess` raise, `_run_git` answer the empty
#: string, and `_superseded` read that silence as "the tips agree about every
#: path it was asked" - which drops every in-flight mark the ref carries, the
#: one direction this module must not fail in (`PL-DMDF`). Chosen far below
#: any limit rather than tuned to one; `getconf ARG_MAX` measures 2,097,152 on
#: the session container, and the smallest limit this has ever run against is
#: three orders of magnitude above the ~5 KB a real branch asks for. At ~60
#: bytes a queue path this holds about 1,000 of them, so no branch in this
#: store's history has needed a second chunk.
_PATHSPEC_BYTES = 64 * 1024


def _pathspec_chunks(paths: tuple[str, ...]) -> Iterator[tuple[str, ...]]:
    """`paths`, in runs short enough to spell on one command line.

    A single path longer than the whole budget is still yielded, alone: leaving
    it out would drop it from the answer silently, which is the failure this
    split exists to prevent rather than one it can repair.
    """
    held: list[str] = []
    used = 0
    for path in paths:
        cost = len(path.encode(_ENCODING, "replace")) + 1
        if held and used + cost > _PATHSPEC_BYTES:
            yield tuple(held)
            held = []
            used = 0
        held.append(path)
        used += cost
    if held:
        yield tuple(held)


def _superseded(ref: str, base: str, paths: tuple[str, ...], root: Path, run: Runner) -> set[str]:
    """Of `paths`, those the base's tip already accounts for, so nothing is left behind.

    **The blob walk asks whether the base ever held a *version*; this asks
    whether the base still needs one.** They differ wherever a path's content
    was replaced after the branch introduced it, and `_landing_split` calls
    every such path outstanding because no commit on the base ever carried that
    exact blob. Two shapes reach it and neither is work anybody lost
    (`PL-XLQ5`):

    - **Superseded on the branch.** An early commit wrote one version and a
      later commit on the same branch rewrote it, so the squash carried only
      the final version and the intermediate blob is genuinely one the base has
      never held. The branch changed its mind once; nothing was left behind.
      Observed 2026-09-05 on `origin/claude/next-workflow-item-c2b07p`, where
      `git diff origin/main HEAD` was empty while four files were reported.
    - **Superseded on the base.** The base took the branch's content and then
      added to it in the same commit - a recovery note appended to an item that
      was re-applied (`PL-1VFK`, `#437`) - so the blob the branch introduced is
      again one the base never held, while the base's copy is a strict superset
      of it. This is the expensive one: the `recover:` line a reader is handed
      is a `git checkout` of the branch's older copy over the base's newer one,
      which deletes the note.

    The test is the two-dot diff that disproved both by hand, read per path:

    - **Absent from the diff.** The base's tip and the ref's tip agree, so
      there is nothing the base is missing. That is supersession on the branch.
    - **Removals only.** Going from the base to the ref *deletes* lines and
      adds none, so the base holds everything the ref holds and more. That is
      supersession on the base.
    - **Anything added or changed.** The ref's tip carries content the base's
      tip does not, which is what work left behind looks like.

    **The direction of the read is what makes it safe**, and it is the
    direction the rest of the module takes. Every silence here - a git that did
    not answer, a path git answered for in a shape this cannot parse, a binary
    file git writes as `-` rather than a count - leaves the path outstanding and
    so leaves the branch reported. A path wrongly called superseded would hide
    work nothing merged, which is the loss `orphaned` exists to catch; a path
    wrongly left outstanding costs a reader one two-dot diff, which is what
    they were doing by hand before this.

    **Two of those three used to be inverted, and the sentence above was the
    only place that said otherwise** (`PL-Q9Z1`). "Absent from the diff" is what
    a chunk git never answered for looks like, so a failed `git diff` read as
    the tips agreeing about every path it was handed, and a line git wrote in an
    unexpected shape read the same way for that one path. Both now stay
    outstanding, and neither is reachable by argument: the failing direction is
    driven by a test, because this docstring stating the rule correctly is
    exactly what did not enforce it. Reachable in this repository rather than in
    theory - a ref deleted by another session between the `for-each-ref` that
    lists it and the `diff` that reads it makes git answer `fatal: bad
    revision`, and one such call took `branches_in_flight` from fourteen
    `editing` marks to none, with `FlightReport.unreadable` empty in both cases.

    `--no-renames` because the paths compared against come from
    `_landing_split`, which also passes it: a rename read on one side and not
    the other would compare two different path sets.

    **`paths` is the whole set to ask about, and asking it whole is the point**
    (`PL-DMDF`). One `git diff` answers for every path it is given, so a caller
    that loops over its own set calling this once per path pays a process per
    item file instead of a process per ref. `_pathspec_chunks` is the only
    thing between the set and the command line, and it splits on a byte budget
    rather than on a count, so the single-call shape survives any branch a
    reader will actually meet.
    """
    superseded: set[str] = set()
    for chunk in _pathspec_chunks(paths):
        output = run(["diff", "--numstat", "--no-renames", base, ref, "--", *chunk], root)
        if not answered(output):
            # Git did not answer for this chunk, so nothing in it has been shown
            # to be anything. Every path it named stays outstanding, which is
            # the whole safety of the read: the empty string a failure comes
            # back as is byte-identical to the empty string two agreeing tips
            # produce, and only `answered` separates them.
            continue
        differing: dict[str, tuple[str, str]] = {}
        for line in output.splitlines():
            fields = line.split("\t", 2)
            if len(fields) != 3:
                continue
            added, deleted, path = fields
            differing[path.strip()] = (added.strip(), deleted.strip())
        # Read within the chunk that asked, never against the union: "absent
        # means the tips agree" is sound only about paths this call named.
        for path in chunk:
            counts = differing.get(path)
            if counts is None:
                # The two tips agree on this path, so the base is missing
                # nothing. A path git did not report on at all reads the same
                # way only because it was asked for by name, and only because
                # the guard above established that git answered at all: git
                # names every path it was given that differs.
                superseded.add(path)
                continue
            added, deleted = counts
            if added == "0" and deleted.isdigit() and int(deleted) > 0:
                superseded.add(path)
    return superseded


#: The number GitHub's squash merge writes at the end of the commit it lands,
#: `Title (#934)`. A merge commit or a direct push carries none.
_SQUASH_NUMBER = re.compile(r"\(#(\d+)\)\s*$")


@dataclass(frozen=True)
class Landing:
    """The commit on the default branch whose tree first held another commit's change."""

    commit: str
    subject: str

    @property
    def pull_request(self) -> int | None:
        """The pull request that landed it, where the subject is a squash merge's."""
        found = _SQUASH_NUMBER.search(self.subject)
        return int(found.group(1)) if found else None


def change_landed(
    commit: str, base: str, root: Path, *, runner: Runner | None = None
) -> Landing | None:
    """Where the default branch took `commit`'s change, or None where it has not.

    **The one landing test that reads the change itself** (`PL-GHHW`). Every
    other test here reads something coarser - containment reads commits,
    `_landing_split` reads blobs, `_superseded` reads whole files at the two
    tips - and each misses a change that reached the base through a pull
    request other than its own branch's. That pull request's squash carries the
    change *and more*, so no commit on the base is the commit, no blob on the
    base is the blob, and the base's copy of the file is ahead of the branch's
    rather than a superset of it. Porting a fix that is also landing elsewhere
    is what the drive-to-green rules prescribe for a red base, so the shape is
    routine, and it had been filed four times against three readers before it
    was fixed once here (`PL-XLQ5`, `PL-MBTZ`, `PL-PXZ3`, `PL-GHHW`).

    **`git patch-id` was the first candidate and cannot answer it.** It matches
    a whole diff to a whole diff, and a squash that carries the port plus the
    rest of its pull request matches nothing; matching against the other pull
    request's own head commits instead needs `refs/pull/*`, which a checkout
    does not fetch and `orphaned` must answer without.

    **The test is the cherry-pick git would make.** Replay the commit onto a
    base commit as a three-way merge whose merge base is the commit's own
    parent - `git merge-tree --write-tree --merge-base=<commit>^ <base>
    <commit>` - and ask whether the result is the base commit's own tree. If
    applying the change to that tree changes nothing, the tree already holds
    it; that is the condition `git cherry-pick` reports as "now empty". It is
    hunk by hunk by construction, so a base that edited other lines of the
    same file does not confound it, which is the case every coarser test
    misses.

    **Ever held, not held now**, which is `_landing_split`'s rule for the same
    reason: a base that took the change and then rewrote the line has still
    taken it, and recovering the commit would revert the rewrite. So the
    candidates are the default branch's first-parent commits since the fork
    point that touch the commit's paths, oldest first, and the first that holds
    the change is the one returned. Its subject is how a reader is told which
    pull request landed it.

    **Every failure reads as not landed**, which is the direction the readers
    need: they keep reporting the commit, as they did before this test existed.
    A conflict (git exits 1, answered as `""`), a git older than 2.40, which
    has no `--merge-base` and so answers nothing, a root commit and a merge
    commit, which have no one parent to replay from - none produces a tree to
    match. The known recall cost is a change the base took together with an
    edit to the line next to it: git merges adjacent changes as one hunk and
    calls it a conflict, so that commit is still reported.

    `--write-tree` writes the merged tree into the object store. No ref moves,
    and gc prunes what nothing reaches; a tree equal to the base's writes
    nothing new at all.

    One merge per candidate, and a reader asks only of a commit it would
    otherwise report. Measured 2026-09-23 on this repository: a commit forked
    300 commits back and touching `vcs.py` and `test_cli.py`, two of its
    busiest files, met 48 candidates, held at none, in 1.1 s.
    """
    run = runner or _run_git
    changed = run(["diff", "--name-only", "--no-renames", f"{commit}^", commit, "--"], root)
    paths = tuple(line.strip() for line in changed.splitlines() if line.strip())
    if not paths:
        return None
    fork = run(["merge-base", base, commit], root).strip()
    if not fork:
        return None
    # Path-limited where the pathspec fits one command line, which is every
    # commit a reader has asked about so far; past that, every first-parent
    # commit is a candidate, which is slower and gives the same answer.
    limit = paths if len(list(_pathspec_chunks(paths))) == 1 else ()
    listed = run(
        [
            "log",
            "--first-parent",
            "--reverse",
            "--format=%H%x1f%T%x1f%s",
            f"{fork}..{base}",
            "--",
            *limit,
        ],
        root,
    )
    for line in listed.splitlines():
        fields = line.split("\x1f", 2)
        if len(fields) != 3:
            continue
        candidate, tree, subject = (part.strip() for part in fields)
        merged = run(
            ["merge-tree", "--write-tree", f"--merge-base={commit}^", candidate, commit], root
        )
        if not answered(merged):
            # Not a conflict, which git answers: git said nothing about this
            # candidate, so a later one that holds the change cannot be called
            # the first, and naming it would name the wrong pull request.
            return None
        if merged.splitlines()[:1] == [tree]:
            return Landing(commit=candidate, subject=subject)
    return None


@dataclass(frozen=True)
class _Refs:
    """Every ref this checkout holds, split by what can be believed about it.

    `candidates` keeps the order refs were listed in, because that order
    decides which of two refs holding one piece of work - a local branch and
    its own tracking ref - is the one reported for it.
    """

    #: How many refs the listing returned before the merged ones were removed.
    #: The count rather than the names, because the only caller needs to tell
    #: "git listed nothing" - no git, no repository - from "every ref it listed
    #: has landed", and those are opposite answers that an empty `candidates`
    #: reports identically.
    listed: int
    candidates: list[str]
    unlanded: list[str]
    unreadable: set[str]
    #: Per unlanded ref, the paths it introduces that the base already holds
    #: and the paths it does not. Kept because deciding a ref is unlanded
    #: computes it, and `orphaned` would otherwise ask git the same question a
    #: second time to find out *which* half was which.
    landing: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]
    #: Per candidate ref, the commit it forked from. Kept because resolving it
    #: is how a ref is decided readable at all, and `_taken_on_base` needs the
    #: same commit to bound its window - asking git for it a second time could
    #: return a different answer about where the branch left from.
    fork: dict[str, str]
    #: Every blob the base's history holds, which the split above was judged
    #: against. Kept because `claims.holdings` asks the same per-blob question
    #: of each commit for its landed prefix, and a second walk of the base's
    #: objects could answer from a base that had moved in between.
    base_blobs: frozenset[str] = frozenset()


def _unlanded_refs(base: str, root: Path, run: Runner, *, include_remote: bool) -> _Refs:
    """Which refs still carry work the default branch has not taken.

    Split out because two reads need exactly this and would otherwise each
    spell the four git questions it asks - listing the refs, subtracting the
    merged ones, resolving each fork point, and asking after the content a
    squash merge keeps - and two spellings of one question are two answers
    waiting to disagree.
    """
    args = ["for-each-ref", "--format=%(refname:short)", "refs/heads"]
    if include_remote:
        args.append("refs/remotes")
    merged = {
        name.strip() for name in run([*args, f"--merged={base}"], root).splitlines() if name.strip()
    }
    listing = [name.strip() for name in run(args, root).splitlines() if name.strip()]
    candidates = [name for name in listing if name not in merged]

    # A truncated clone is the normal state of an agent session's container,
    # and a ref with no readable merge-base is one whose commits this checkout
    # simply does not have. Excluding `^base` from a walk that cannot reach
    # `base` would report the ref's whole visible history as its own work, so
    # it is named as unread instead of answered wrongly. This is the first of
    # two guards and not the sufficient one: a merge-base that resolves says
    # the two share a commit this checkout can see, not that the walk below it
    # is complete, which is what the second guard tests.
    #
    # The merge-base is the fork point the content test compares against, so
    # the read that decides whether a ref can be answered at all is the same
    # one that answers it - two calls asking git the same question could
    # disagree about which commit the branch left from.
    unlanded: list[str] = []
    unreadable: set[str] = set()
    landing: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    fork: dict[str, str] = {}
    # One walk of the base's objects, before the loop rather than inside it:
    # the question is per blob and the answer is the same set for every ref.
    base_blobs = _base_blobs(base, root, run)
    for name in candidates:
        fork_point = run(["merge-base", base, name], root).strip()
        if not fork_point:
            unreadable.add(name)
            continue
        fork[name] = fork_point
        split = _landing_split(name, fork_point, base_blobs, root, run)
        if not _work_already_on_base(split):
            unlanded.append(name)
            landing[name] = split
    return _Refs(
        listed=len(listing),
        candidates=candidates,
        unlanded=unlanded,
        unreadable=unreadable,
        landing=landing,
        fork=fork,
        base_blobs=base_blobs,
    )


def _preferred(name: str, candidates: list[str]) -> str:
    """The local branch where the checkout holds it and its tracking ref both.

    **A name-level rule, because the walk cannot supply one.** `--source` names
    *a* ref that reached each commit and promises nothing about which, and
    measured on this repository it varies per commit inside one walk
    (`PL-R6D8`). So which of two refs holding one piece of work gets reported
    cannot be read off the walk at all - and it is worth deciding, because
    `flight` and `triage` showing `origin/claude/...` for work the reader's own
    local branch is carrying is the confusion those lines exist to remove.

    A tracking ref ends with its local branch's whole name after a separator, so
    a candidate that is a proper suffix of this one is that branch. Matched that
    way rather than against a list of remotes, which would cost a git call to
    learn what `origin` is called here and answer nothing extra: a local branch
    genuinely named `bar/x` alongside another named `foo/bar/x` is the only
    shape that collides, and reporting either for the other names the same work.
    """
    for candidate in candidates:
        if candidate != name and name.endswith(f"/{candidate}"):
            return candidate
    return name


def _item_paths_on(base: str, items_dir: str, root: Path, run: Runner) -> dict[str, str]:
    """Each item id the base holds, mapped to its file's path there, from one tree listing.

    The store names each file for its item - `docs/items/PL-K7QX-do-it.md` -
    which `store.filename_for` guarantees, so the id is the head of the
    basename. The three readers of the base's copy of an item share this so
    that the one question they all open with is spelled once.
    """
    prefix = items_dir.strip("/") + "/"
    names: dict[str, str] = {}
    for line in run(["ls-tree", "--name-only", base, "--", prefix], root).splitlines():
        path = line.strip()
        if not path:
            continue
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
        if match is not None:
            names.setdefault(match.group(1).upper(), path)
    return names


def _closed_on_base(
    ids: set[str], items_dir: str, base: str, root: Path, run: Runner
) -> frozenset[str]:
    """Of `ids`, those whose item the default branch already records as closed.

    **Why the line needs this at all.** The in-flight mark is read from branch
    refs, and a ref outlives the merge that took its work: nothing prunes
    `origin/<branch>`, deliberately, because a stale ref can be the only
    surviving copy of an item captured on a branch nobody merged. So an item can
    ship and go on being named under "do not start these again" for as long as
    the ref survives - two of them for two releases, measured 2026-09-07, and
    one reading of the line where all three entries were false (`PL-6BDX`).

    It misroutes nothing: `docket next` does not offer closed items. What it
    costs is the line's credibility, and `CLAUDE.md` is explicit that a check
    firing every run without changing a decision is a defect in the check,
    because it trains a session to skim the output where a real entry also
    appears. The real entries here are the ones that stop two sessions
    colliding.

    **Closed on the base, never closed in this checkout**, and the difference is
    the whole care of it. A session closing an item right now has that closure
    on its own branch, and reading the working tree would suppress exactly the
    live work the line exists to protect. The base is the one tree that cannot
    be carrying an unmerged session's answer.

    One tree listing maps ids to file names - the store names each file for its
    item - and then one `git show` per id asked about, which is the few the
    report is about to name rather than the whole store. An id whose file the
    base does not hold is not closed there, which is the safe direction: it
    keeps the entry.
    """
    if not ids:
        return frozenset()
    names = _item_paths_on(base, items_dir, root, run)
    closed: set[str] = set()
    for identifier in ids:
        path = names.get(identifier.upper(), "")
        if not path:
            continue
        text = run(["show", f"{base}:{path}"], root)
        if text and parse_item(text, path.rsplit("/", 1)[-1]).status in CLOSED_STATUSES:
            closed.add(identifier)
    return frozenset(closed)


def _claimed_again_since(mine: Stake | None, taken: datetime | None) -> bool:
    """Whether a ref said it was carrying an item *after* the base took that id.

    Split out so the direction each silence fails in is stated once. A ref with
    no dated claim and a take this checkout could not date both answer `False`,
    which leaves `_taken_on_base` deciding on the two facts it had before this -
    the reading every carrier whose claim comes from its branch *name* gets,
    there being no commit to date. A comparison that raises answers `True` and
    keeps the claim: a git that wrote one of the two dates without an offset is
    an anomaly, and over-reporting is the direction this module fails in.
    """
    if mine is None or taken is None:
        return False
    try:
        return mine.when > taken
    except TypeError:
        return True


def _taken_on_base(
    claims: dict[str, tuple[str, ...]],
    forks: dict[str, str],
    claimed_last: dict[tuple[str, str], Stake],
    items_dir: str,
    base: str,
    root: Path,
    run: Runner,
) -> frozenset[tuple[str, str]]:
    """Of `claims`, the carriers with nothing left to give - without closing the item.

    **`_closed_on_base` is the same question asked of the only answer it can
    see, and a triage pass is the gap between them.** That guard drops an id
    whose item the base records as *closed*, which covers a branch that shipped
    something. A pass that triages an item lands it at `ready`, `blocked` or
    `needs-decision`, so the item is open on the base, the guard cannot fire,
    and the spent claim outlives the merge (`PL-LKFP`). Measured 2026-09-16 on
    `origin/main` at `2a538ec1`: `PL-2M4X` read `P3 - S - ready` there and
    `bin/docket show` still printed `do not start PL-2M4X again`, naming a
    branch whose `#616` had merged forty minutes earlier.

    **Why the ref-level content test cannot catch it.** `_work_already_on_base`
    asks whether every blob a ref introduces is one the base has held, and one
    shared file is enough to make a fully landed branch answer no forever: a
    squash resolves `ROADMAP.md` against a base that has moved, and later merges
    then rewrite lines the branch added, so the branch's own copy is a blob the
    base has never held. Both branches measured that day were outstanding on
    that path and on nothing else - 6 item blobs of 7 landed on one, 13 of 14 on
    the other. `_superseded` answers the second of them and not the first,
    because a rewrite reads as an addition rather than as a removal.

    So the question moves to where the report's own subject already is: per id,
    rather than per ref. Two facts, and both are needed.

    - **The base's copy of the item's own file is the ref's copy**, byte for
      byte, so the ref carries no unmerged change to that item. On its own this
      is not enough: a session that has pushed `src/` work under its item's id
      but not yet edited the item file looks exactly like this.
    - **The base took a commit leading with that id, at or after the ref's fork
      point, and not before the ref's newest commit claiming it.** That is what
      says the base has already had this ref's work under this name. The fork
      point is what keeps it honest - an *older* commit naming the id is the
      item's own capture, which every session's branch forks from, and counting
      it would suppress the live work this whole read exists to protect.

    **The second bound is the one a squash merge needs** (`PL-8JQQ`). Both facts
    above are made true *by* a pull request merging from the ref itself: the
    squash carries the item file, so the copies agree byte for byte, and its
    subject leads with the id, so the base has taken it since the fork. Nothing
    then distinguishes a branch whose work is finished from one that has gone on
    committing - and an implementation commit following a merged design round is
    exactly that shape, `src/` and `tests/` under the same id with the item file
    untouched. Measured 2026-09-20: `PL-3K9B`'s whole implementation, 8 files
    and 637 insertions pushed with the id leading its subject, appeared in no
    reading of the report, and the same command had reported it before `#801`
    merged. The project owner caught it; three replies had by then recommended
    that a fresh session start the item a live one was implementing.

    Dated on the committer date both sides already carry, because ancestry
    cannot answer it: a squash keeps none of the ref's commits, so there is
    nothing to contain. The failure directions are the module's usual ones. A
    rebase rewrites the ref's dates forward and keeps a claim whose work
    merged, which costs a reader one look; a date this checkout could not read
    on either side falls back to the two facts above, which is where this
    guard stood before. Only a commit backdated behind the merge that took it
    reads the wrong way, and nothing in this workflow writes one.

    Every silence keeps the claim: no fork point, no file on either side, a blob
    git would not resolve. That is the direction the module fails in by
    construction - an item wrongly left marked costs a session one alternative
    pick, an item wrongly unmarked costs two sessions one merge.

    The residual case is a session whose *own* branch has a commit leading with
    its id already merged from underneath it while the item file stayed
    untouched. That branch is the `PL-3D2M` shape - work its pull request left
    behind - which `orphaned` reports on its own terms.

    **Asked per carrier, and answered per carrier** (`PL-2BZY`). Every fact
    above is a fact about one *ref* - its copy of the item file, where it
    forked, what the base took since - so an id two branches carry has two
    answers, and which of them is spent says nothing about the other. It used
    to be handed one ref per id, chosen by candidate rank before any guard ran,
    and to answer in ids: on 2026-09-19 a branch whose pull request had
    squash-merged sorted first among the remote refs, its was the only claim
    judged, and dropping the id under "do not start these again" dropped two
    live design rounds with it. The caller reports the first carrier absent
    from this set and drops the id only where every one of them is in it.
    """
    if not claims:
        return frozenset()
    prefix = items_dir.strip("/") + "/"
    names: dict[str, str] = {}
    for line in run(["ls-tree", "--name-only", base, "--", prefix], root).splitlines():
        path = line.strip()
        if not path:
            continue
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
        if match is not None:
            names.setdefault(match.group(1).upper(), path)
    # One subject walk per fork point rather than per id: two refs that forked
    # from the same commit ask git the identical question. The base's own copy
    # of an item file is read once per path for the same reason - it is the
    # fixed end of every comparison, whichever carrier is being judged, so a
    # second carrier costs one `rev-parse` rather than two.
    since: dict[str, dict[str, datetime | None]] = {}
    held: dict[str, str] = {}
    taken: set[tuple[str, str]] = set()
    for identifier, carriers in claims.items():
        path = names.get(identifier.upper(), "")
        if not path:
            continue
        for ref in carriers:
            fork_point = forks.get(ref, "")
            if not fork_point:
                continue
            if path not in held:
                held[path] = run(["rev-parse", f"{base}:{path}"], root).strip()
            theirs = run(["rev-parse", f"{ref}:{path}"], root).strip()
            if not held[path] or not theirs or held[path] != theirs:
                continue
            if fork_point not in since:
                # Which ids the base took, and the newest take of each - the
                # last time the base heard this name rather than the first, so
                # a ref that committed under it later is judged against the
                # whole of what merged. An id every one of whose takes this
                # checkout's git dated in some other shape is recorded with no
                # date at all, which leaves the id taken and the second bound
                # unasked: the reading this guard had before it was bounded on
                # that side.
                dated: dict[str, datetime | None] = {}
                for line in run(
                    ["log", "--format=%cI%x1f%s", f"{fork_point}..{base}"], root
                ).splitlines():
                    stamp, _, subject = line.partition("\x1f")
                    try:
                        when: datetime | None = datetime.fromisoformat(stamp.strip())
                    except ValueError:
                        when = None
                    for found in leading_ids(subject):
                        current = dated.setdefault(found, None)
                        if when is not None and (current is None or when > current):
                            dated[found] = when
                since[fork_point] = dated
            if identifier.upper() not in since[fork_point]:
                continue
            # The take is real and the ref has committed under the id since, so
            # the merge cannot have carried what the ref is holding now.
            if _claimed_again_since(
                claimed_last.get((ref, identifier)), since[fork_point][identifier.upper()]
            ):
                continue
            taken.add((identifier, ref))
    return frozenset(taken)


def _queue_only_touches(text: str, name: str, items_dir: str) -> bool:
    """Whether an item's `touches` names the queue directory and nothing outside it.

    **One reading of the field, in one place, because two callers ask it of
    different trees.** `_queue_only_work` asks it of the base, to tell a session
    that is *starting* an item whose work is the queue from one merely filing an
    item (`PL-7790`); `_declares_queue_only` asks it of a closure commit, to tell
    that same item's work from a closure that landed without its work
    (`PL-YFXG`). Which tree to read is each caller's question; what the field
    means is not, and the two readings drifting apart would put `bin/docket
    record` and `bin/docket next` on opposite sides of one item.

    An item declaring no `touches` at all is not queue-only work: it has said
    nothing about where its work lives, and both callers default to withholding.
    """
    prefix = items_dir.strip("/")

    def inside(declared: str) -> bool:
        """Whether one `touches` entry names the queue directory or something in it."""
        declared = declared.strip().rstrip("/")
        return declared == prefix or declared.startswith(prefix + "/")

    touches = parse_item(text, name).touches
    return bool(touches) and all(inside(declared) for declared in touches)


def _queue_only_work(
    ids: set[str], items_dir: str, base: str, root: Path, run: Runner
) -> frozenset[str]:
    """Of `ids`, those whose whole declared deliverable is a write to the queue.

    **The reading that separates "filed this item" from "started this item",
    and it reads the item rather than the commit** (`PL-7790`). `_annotates_only`
    decides from the diff's paths, so a session that genuinely starts an item by
    pushing only a `touches` fill - or by doing work whose entire output is a
    queue edit - stakes a claim that looks exactly like a capture. Two
    path-level refinements were tried against `PL-X3WZ`'s eight false marks and
    both reintroduced them; anything that recovers this case has to read
    something other than the paths, and the item's own `touches` is the
    something.

    Measured against those eight ids - `PL-HKF4`, `PL-PGZK`, `PL-5WFS`,
    `PL-22Z3`, `PL-WW08`, `PL-PMT7`, `PL-55JM`, `PL-N5WZ` - not one declares
    `touches` inside the queue alone, so all eight stay excluded on this test
    with no path-level help at all. 61 of 920 items declare one, about twenty of
    them open: the tag items, the triage items, the recovery items, whose work
    *is* editing item files.

    **Read from the base, and a file the base does not hold is not queue-only
    work.** That is what keeps a capture out: a capture creates the item file,
    so the base has no copy to declare anything and the id is dropped rather
    than marked. It is also the one tree that cannot be carrying an unmerged
    session's answer, which is why `_closed_on_base` reads the same one.

    **Asked only of an item a subject led with, and it was once asked of every
    item a branch edited** (`PL-3W3P`). A pass that rewrites many item files for
    its own item's reason then claimed every queue-only item it passed through:
    `PL-0HPV`'s `verify:` reorder, led by `PL-0HPV`, rewrote 96 item files and
    marked `PL-LBW5`, `PL-RWBV`, `PL-YVV4` and `PL-YZKK` in flight on its branch,
    none of them named by any subject, until its pull request merged.
    `_own_edit_claims` now hands this the ids of queue-only commits that led
    with the id and wrote its own file, the shape the other two promotions read.

    One tree listing and one `git show` per id asked about, and it is asked only
    about that handful - never the store.
    """
    if not ids:
        return frozenset()
    names = _item_paths_on(base, items_dir, root, run)
    queue_only: set[str] = set()
    for identifier in ids:
        path = names.get(identifier.upper(), "")
        if not path:
            continue
        text = run(["show", f"{base}:{path}"], root)
        if text and _queue_only_touches(text, _basename(path), items_dir):
            queue_only.add(identifier)
    return frozenset(queue_only)


def _deciding_on_base(
    ids: set[str], items_dir: str, base: str, root: Path, run: Runner
) -> frozenset[str]:
    """Of `ids`, those whose item the default branch holds at `needs-decision`.

    **The second reading that separates "filed this item" from "started this
    item", and like `_queue_only_work` it reads the item rather than the
    commit** (`PL-VYSP`). An item at `needs-decision` has a decision as its
    next step, and a decision is recorded into the item file - so a design
    round's whole output may be queue edits, and `_annotates_only` withheld
    its claim for the whole life of the work. Observed 2026-09-19 on
    `PL-BHVM`: three commits pushed, every subject led by the id, a live
    session on the branch, and `bin/docket show` calling the item startable.
    The mark appeared only when the round happened to edit `ROADMAP.md`.

    **Counted before it was adopted, against the two rules it was chosen over.**
    Over the 1,006 commits then on `origin/main`, a rule marking any queue-only
    commit that led with an id and changed that id's own file - the candidate
    the item itself proposed - would have marked 316 (commit, id) pairs, 81 of
    them captures and recoveries creating the file; requiring the base to hold
    the file already left 235, of which 120 were triage passes moving an item
    out of `untriaged`. Both readmit `PL-X3WZ`'s false marks wholesale. Adding
    this status test left 23, and reading their subjects found 21 to be the
    item's own decision work - the answer, a measurement for it, or its
    disposition - and two notes written into one item on consecutive days in
    the project's first week. That is the direction `_annotates_only` already
    prefers: an item wrongly left marked is one a session picks around.

    **Why the subject has to lead with the id.** A design round re-points its
    cluster, so one commit edits a dozen other items' files, some of them at
    `needs-decision` themselves. Promoting those on the file edit alone would
    mark items the round merely wrote about, under "do not start these again",
    for sessions that are working them. `_unmerged_commits.own_edits` carries
    that conjunction, and `_queue_only_work` is now asked through it too, for
    the same reason (`PL-3W3P`).

    Read from the base for the reason `_queue_only_work` is: it is the one
    tree that cannot be carrying an unmerged session's answer, and a capture
    creating the file has no copy there to be at any status. A closed item is
    not at `needs-decision`, so the closedness re-check the other promotion
    needs is answered here by the status itself. What the base cannot answer
    is a capture that merged by another route and was triaged there while its
    own branch lives on; `_modified_by` asks the commit's parent for that.
    """
    if not ids:
        return frozenset()
    names = _item_paths_on(base, items_dir, root, run)
    deciding: set[str] = set()
    for identifier in ids:
        path = names.get(identifier.upper(), "")
        if not path:
            continue
        text = run(["show", f"{base}:{path}"], root)
        if text and parse_item(text, path.rsplit("/", 1)[-1]).status == "needs-decision":
            deciding.add(identifier)
    return frozenset(deciding)


def _modified_by(commit: str, paths: tuple[str, ...], root: Path, run: Runner) -> bool:
    """Whether `commit` changed a file it inherited, rather than only creating one.

    **What separates a design round from a stale capture once the base holds
    the item at `needs-decision`.** A capture creates the file; a round writes
    into one that exists. The base cannot tell them apart when the capture
    merged by another route and was triaged there, because the capture's
    branch then leads with the id and changes its own file too - and its ref
    outlives the merge. Measured live on 2026-09-19, the status test alone
    promoted three such branches, every one eleven days old, which is the
    "branch nobody merges, forever" false mark `PL-X3WZ` removed (`PL-VYSP`).
    The commit's own first parent answers it: a path the parent did not hold
    was created there.

    Any of the paths is enough, because a round that renames the item's file
    changes two, and the one it inherited is the evidence. A parent this
    checkout cannot resolve answers nothing - but a commit with no readable
    parent already put its ref in `_Walk.unbounded`, so nothing reaches here
    on that path.
    """
    return any(
        run(["rev-parse", "--verify", "--quiet", f"{commit}^:{path}"], root).strip()
        for path in paths
    )


def _own_edit_claims(
    rounds: Mapping[str, Sequence[tuple[str, str, tuple[str, ...]]]],
    items_dir: str,
    base: str,
    root: Path,
    run: Runner,
) -> dict[str, list[str]]:
    """Per id, the refs whose queue-only edit to the item is its work rather than a note.

    **One shape in, three item-level tests out, and both readers share them.**
    `rounds` holds, per id and in the order a carrier would be reported, each
    ref's newest queue-only commit that led with the id and wrote the id's own
    file (`_Walk.own_edits`), kept only where the base has not already taken
    that ref's copy (`_superseded`). A capture, a triage pass and a note have
    that shape too, so a round is a claim only where the item says the queue
    edit is the work:

    - **its whole declared deliverable is the queue** (`PL-7790`,
      `_queue_only_work`), and the base does not record it closed - a `docket
      record` write onto a shipped tag item has the shape, and naming a closed
      item under "do not start these again" is `PL-6BDX`;
    - **the base holds it at `needs-decision`** (`PL-VYSP`,
      `_deciding_on_base`), and the commit wrote into a copy it inherited
      (`_modified_by`), which is what tells a round from a capture that merged
      by another route and was triaged there;
    - **the base holds it open and this ref's tip holds it closed**
      (`PL-8FJK`): a grooming pass dropping items it never claimed. `#914`
      dropped `PL-027`, `PL-043` and `PL-ZBR6` in commits leading with each
      id, and all three stayed on offer in `docket next`. The tip is read
      rather than the commit, so a branch that dropped an item and then
      reopened it claims nothing; the paths read are the ones the round
      wrote, and only a later commit leading with some other id can move the
      file from under them - the read then answers "open", which leaves the
      item offered.

    **The feed is the subject-led shape for all three** (`PL-3W3P`). The first
    promotion used to be fed from every edit to an item's file, so a pass
    rewriting many item files for its own item's reason claimed each queue-only
    one it passed through. Leading with the id is also what bounds the cost:
    one `git show` of the base's copy per id a subject named, rather than one
    per item file a branch touched - about 96 on `PL-0HPV`'s branch alone.

    **The limit, stated so nobody mistakes it for coverage.** A closure under a
    subject that does not lead with the closed id stays in
    `FlightReport.editing`, never here. `CLAUDE.md` requires a closing commit to
    lead with every id it closes, so the case is that rule not being kept -
    and reading the closure off any edit instead is `PL-3W3P` again.

    Each item-level test is asked once per id, because each is a fact about
    the base; `_modified_by` and the tip's status are facts about one carrier
    and are asked of each. Every ref that passes is returned, in the order
    `rounds` gave: the head of a list is the carrier `branches_in_flight`
    reports, and the whole list is what `precedence` orders.
    """
    ids = set(rounds)
    if not ids:
        return {}
    closed = _closed_on_base(ids, items_dir, base, root, run)
    queue_only = _queue_only_work(ids, items_dir, base, root, run) - closed
    deciding = _deciding_on_base(ids - queue_only, items_dir, base, root, run)
    held = _item_paths_on(base, items_dir, root, run)
    claims: dict[str, list[str]] = {}
    for identifier in sorted(ids):
        open_on_base = identifier.upper() in held and identifier not in closed
        for name, commit, paths in rounds[identifier]:
            if (
                identifier in queue_only
                or (identifier in deciding and _modified_by(commit, paths, root, run))
                or (open_on_base and any(_closed_at_ref(name, path, root, run) for path in paths))
            ):
                claims.setdefault(identifier, []).append(name)
    return claims


def branches_in_flight(
    root: Path,
    *,
    include_remote: bool = True,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> FlightReport:
    """Every item whose work sits on a branch the default branch has not taken.

    **The id is read from the commit subjects as well as from the branch
    name**, and that is the whole point of the read. A branch a session names
    for itself carries the id (`claude/pl-k7qx-short-slug`); a branch the web
    harness names is built from the opening prompt
    (`claude/roadmap-release-write-failure-nhsjwo`) and carries nothing, and
    cannot be renamed afterwards. Reading names alone therefore went blind in
    exactly the case this exists for, and `docket next` would hand a session an
    item another session was already implementing.

    Refs are read from what is already fetched, so the answer can be stale by
    exactly one fetch. That is an acceptable error for an advisory and an
    unacceptable one for a lock, which is why this reports rather than blocks.

    **A second and weaker reading rides along, and it is the one a triage pass
    is visible in.** `editing` names the refs that have changed an item's own
    file without earning the mark above - which is every capture, triage pass,
    `docket record` write and note added to a brief, since `_annotates_only`
    withholds exactly those. That is not work in flight and must never be
    ranked as such; it is a merge conflict waiting in one file, which is what a
    second session about to edit that file needs to know (`PL-N1JK`). `ids`
    stays the strong reading alone, so `docket next` is untouched.

    Branches whose work has landed are excluded, and that exclusion matters
    more than it looks: deleting a branch on the remote does not remove the
    local remote-tracking ref until someone prunes, so without this every item
    ever shipped goes on being reported as in-flight work and the signal
    becomes noise within a few releases. It is asked twice, because one test
    cannot answer it. `--merged` is exact and cheap for a branch the default
    branch contains; a squash merge keeps none of the branch's commits, so
    `_work_already_on_base` asks after the content instead.

    What that leaves is read, and only what the checkout can prove is reported.
    Both reads of a ref's *commits* against the default branch need history the
    checkout may not hold, so each has a guard and neither guard covers the
    other: a merge-base that will not resolve, and a commit walk that ran off
    the end of a grafted history rather than stopping against the default
    branch. Either one names the ref as unread - and naming it so stops its
    commits being believed, not its name being read, because the id a branch
    name carries needs no history at all.

    What remains is qualified rather than filtered. An unmerged branch may be a
    live session or work nobody will ever merge, and only the date of its last
    commit separates the two - so that is carried into the report and left to
    the reader, the way `stranded` reports rather than decides.

    **A subject's leading id is a claim only where the commit did more than
    write to the queue.** Capturing a finding, triaging an item, recovering a
    stranded one and recording a merged pull request number all lead with ids
    under rules `CLAUDE.md` makes mandatory, and none of them is work in
    progress; read as claims they withheld startable items from every session
    until the branch merged. `_annotates_only` carries that reading and the
    error it prefers.

    **Unless the item says the queue edit is its work, which is read from the
    item rather than from the commit.** A queue-only commit that leads with the
    id *and* changes that id's own file is the one shape read, and the
    conjunction is what keeps the other items a pass writes out of it: a
    `verify:` reorder led by `PL-0HPV` claimed four queue-only items it merely
    passed through while the first promotion was fed from any edit
    (`PL-3W3P`). `_own_edit_claims` then promotes the shape in three cases:

    - **The item's own work is a queue edit** (`PL-7790`). A release tag item,
      a triage pass and a stranded recovery deliver nothing but a write to
      `docs/items/`, so the path test excludes the very work it was built to
      find. Measured live on 2026-09-14: `PL-XR8K` was being closed on
      `origin/claude/loving-ride-mo6njm` and appeared in no reading of this
      report at all.
    - **The item is at `needs-decision`** (`PL-VYSP`). Its next step is a
      decision and the decision is written into the item file, so a design
      round can run its whole course without a diff outside the queue - and
      the path test then withheld the claim for as long as the work lasted, on
      exactly the items a recorded generator ranks above every band but `P0`.
    - **The branch closes the item while the base holds it open** (`PL-8FJK`).
      A grooming pass disposes of items it never claimed: `#914` dropped
      `PL-027`, `PL-043` and `PL-ZBR6` under subjects leading with each id,
      and `docket next` went on offering all three to sessions that would have
      started work another had already decided to drop.

    **And a ref that names nothing is reported rather than dropped**
    (`PL-B73C`). `unattributed` is the third outcome beside a claim and an
    unreadable ref: read without difficulty, and attributable to no item. It
    fires on nothing in the steady state, because `tools/branch_id_check.py`
    refuses a `claude/*` branch of one's own that names no id.

    **And a git that did not answer is `declined` rather than a clean report**
    (`PL-Q9Z1`). Every read below collapses a failure to the empty string, and
    several of them read an empty string as good news - no unmerged refs, no
    remaining difference, nothing left outstanding. `_Silences` watches the
    runner rather than each of them, so a silence anywhere beneath this reaches
    the report whether or not the helper that met it thought to look.
    """
    run = _Silences(runner or _run_git)

    # One base for the whole read: what counts as merged, what a ref is
    # compared against, and what the commit walk excludes have to agree, or the
    # answer is assembled from two different questions.
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    candidates, unlanded, unreadable = refs.candidates, refs.unlanded, set(refs.unreadable)

    # A resolvable merge-base answers only half of it. The walk that reads the
    # ids has to be able to exclude the default branch's own commits, and in a
    # truncated clone it cannot always reach them - so a ref whose walk ran off
    # the end of the history joins the ones the merge-base could not answer
    # rather than contributing what it appeared to say. The direction matters:
    # an id wrongly reported here is removed from `docket next` under the words
    # "do not start these again", so an unread ref is the cheaper error.
    walk = _unmerged_commits(unlanded, base, root, run, items_dir=items_dir)
    last_commit, subject_ids = walk.last, walk.ids
    if walk.unbounded:
        unreadable |= walk.unbounded
        unlanded = [name for name in unlanded if name not in walk.unbounded]
        # Per carrier rather than per id: an id claimed by an unread ref *and*
        # by one the walk could read keeps the readable carrier, where dropping
        # the id wholesale discarded a claim that was never in doubt.
        subject_ids = {
            identifier: kept
            for identifier, names in subject_ids.items()
            if (kept := tuple(name for name in names if name not in walk.unbounded))
        }
    unlanded_set = set(unlanded)

    # **A ref whose name carries an id contributes it whether or not its
    # commits could be read.** The two reads need different evidence and only
    # one of them needs history: `^base` can exclude the default branch's own
    # work only where the checkout holds it, while `claude/pl-k7qx-short-slug`
    # names its item in a checkout holding nothing at all. Sending an unread
    # ref past this loop discarded the answer that was certain along with the
    # ones that were not.
    #
    # It cuts against the direction the two guards above take, and the
    # difference is what is being believed. There an id was *inferred* from a
    # walk the history could not support, and a wrong one withholds a startable
    # item under "do not start these again". Here the id is proven and only the
    # branch's landedness is open - which is the cheaper uncertainty, because
    # an item whose work landed is closed and never a candidate for `docket
    # next` anyway, while dropping the id offers an item a live session is
    # holding. That is the collision this whole read exists to prevent.
    #
    # A local branch and its remote tracking ref are one piece of work, and so
    # are a branch named for an item and its own commits: the first ref that
    # accounts for an id is the one reported for it. Candidate order decides
    # that, which prefers a local branch to its tracking ref and a ref that was
    # read to one that was not.
    #
    # **Every carrier is kept, in the order one would be reported in**
    # (`PL-2BZY`). The guard below judges a claim per ref, so a list is what it
    # needs; the head of each list is the single name this used to keep, which
    # is what a reader is shown where nothing removes it.
    named = [name for name in candidates if name in unlanded_set or name in unreadable]
    claimants: dict[str, list[Branch]] = {}

    def claim(identifier: str, name: str, moved: datetime | None) -> None:
        """Record `name` as a carrier of `identifier`, behind any already held."""
        carriers = claimants.setdefault(identifier, [])
        if all(branch.name != name for branch in carriers):
            carriers.append(Branch(name=name, item_id=identifier, last_commit=moved))

    for name in named:
        match = BRANCH_ID_RE.search(name)
        if match is None:
            continue
        claim(match.group(1).upper(), name, last_commit.get(name))
    for identifier, names in subject_ids.items():
        for name in names:
            # `_preferred` is what keeps a reader from being shown the tracking
            # ref for work their own local branch is carrying, which git's own
            # attribution cannot be relied on to avoid (`PL-R6D8`).
            reported = _preferred(name, candidates)
            claim(identifier, reported, last_commit.get(reported) or last_commit.get(name))

    # **An item the base already records as closed leaves the line**, whatever
    # ref still carries its name. Asked here rather than earlier because the set
    # to ask about is exactly what the report was about to name, which keeps the
    # cost to the few entries that exist rather than the whole store
    # (`PL-6BDX`).
    for identifier in _closed_on_base(set(claimants), items_dir, base, root, run):
        del claimants[identifier]

    # **And an item the base took without closing leaves it too** (`PL-LKFP`).
    # `_closed_on_base` above covers a branch that shipped something; a triage
    # pass lands its items open, so the guard cannot fire and the claim outlives
    # the merge. Asked of what is left rather than of what that guard already
    # removed, and asked per id because the ref-level content test is what a
    # shared file defeats.
    #
    # **The ref's newest claim under the id goes with the question** (`PL-8JQQ`).
    # Both facts that guard read as true the moment a pull request merges from
    # the ref itself, and stay true however much the ref commits afterwards, so
    # a branch that continues past its own squash went silent on every item its
    # later commits named.
    #
    # **Every carrier is judged, and the id leaves only where every one of them
    # is spent** (`PL-2BZY`). A claim is a fact about a ref, so the answer is
    # per `(id, ref)`; the first carrier the guard did not take is the one
    # reported, which is the same head the collapse used to choose wherever
    # nothing is spent at all.
    spent = _taken_on_base(
        {
            identifier: tuple(branch.name for branch in carriers)
            for identifier, carriers in claimants.items()
        },
        refs.fork,
        walk.claimed_last,
        items_dir,
        base,
        root,
        run,
    )
    in_flight: dict[str, Branch] = {}
    for identifier, carriers in claimants.items():
        live = next((branch for branch in carriers if (identifier, branch.name) not in spent), None)
        if live is not None:
            in_flight[identifier] = live

    # Refs whose commits went unread contribute no paths either, for the reason
    # they contribute no subject ids: the commits are what the checkout is
    # missing. A branch *name* still proves its id, which is why the loop above
    # reads unread refs and this does not - a name is not a diff.
    # **An edit the base already holds is not an edit on a branch**, and until
    # this was asked the mark could not be read as evidence of anything
    # (`PL-8MJ3`). A squash merge keeps none of the branch's commits, so the
    # branch stays ahead of the base indefinitely and goes on reporting every
    # item file it ever touched. Measured 2026-09-07: a triage pass was told to
    # skip four of its five items, and all four branch copies were
    # byte-identical to the copy on `origin/main`. `SKILL.md` tells a pass to
    # obey this mark, so the wrong answer was on the side that loses work.
    #
    # `_superseded` is the test, the same one `orphaned` narrows its outstanding
    # side with: a path whose tips agree, or whose diff from the base only
    # removes lines, is one the base is not missing. Its silences leave the mark
    # standing, which is the direction this read has always failed in - an item
    # wrongly left marked is one a session picks around, while an item wrongly
    # unmarked is two sessions resolving one file.
    #
    # **Asked once per ref rather than once per path** (`PL-DMDF`).
    # `_superseded` takes the whole set and spells it as one pathspec - both of
    # its other callers hand it one - so calling it from inside a comprehension
    # put a `git diff` on the command line for every item file edited on every
    # unmerged ref. Measured against a fabricated store of 30 unmerged refs
    # carrying 390 item-file edits, chosen to match the project owner's clone:
    # 593 `diff` calls before the hoist and 148 after, of 1,237 git calls and
    # 792. The marks are collected first because the two cheap filters decide
    # what is worth asking about, and `walk.edited`'s order is kept so the
    # report is assembled in the order the walk found the ids.
    #
    # **Every carrier is kept and each is judged** (`PL-RY2R`). `_superseded` is
    # a fact about one ref's copy of one path, so an id two refs have both
    # edited has two answers and the spent one says nothing about the other.
    # Collapsing to the rank-first ref before the test meant a bystander whose
    # copy had landed - a squash merge, a rebase, a cherry-pick - took a live
    # edit's mark with it, and the id left `editing` with nothing printing that
    # it had. The `walk.unbounded` filter is per carrier for the same reason:
    # an unread ref contributes no paths, and it used to discard the readable
    # ref's edit along with its own.
    marks: list[tuple[str, str, str]] = []
    asked_of: dict[str, list[str]] = {}
    for identifier, editors in walk.edited.items():
        if identifier in in_flight:
            continue
        for name, path in editors:
            if name in walk.unbounded:
                continue
            marks.append((identifier, name, path))
            held = asked_of.setdefault(name, [])
            if path not in held:
                held.append(path)
    # The own-file edits ride the same diff, so a design round or a closure
    # whose copy the base already holds is found superseded in the one call
    # rather than a second (`PL-VYSP`).
    #
    # **And they are kept per carrier too** (`PL-61MD`). The walk already keys
    # them `(ref, id)`, so this collapse was the caller's alone: both tests
    # below it - `_superseded` on the ref's copy and `_modified_by` on the
    # commit's own parent - are facts about the chosen carrier, so a bystander
    # branch whose round had landed, or whose commit only ever created the
    # file, suppressed a live round another ref was running on the same item.
    # Ordered by rank here rather than chosen, which leaves the carrier a
    # reader is shown unchanged wherever nothing is spent.
    rank = {name: position for position, name in enumerate(candidates)}
    own: dict[str, list[tuple[str, str, tuple[str, ...]]]] = {}
    for (name, identifier), (commit, paths) in walk.own_edits.items():
        if name in walk.unbounded or identifier in in_flight:
            continue
        own.setdefault(identifier, []).append((name, commit, paths))
        held = asked_of.setdefault(name, [])
        held.extend(path for path in paths if path not in held)
    for rounds in own.values():
        rounds.sort(key=lambda entry: rank.get(entry[0], len(rank)))
    superseded_by_ref = {
        name: _superseded(name, base, tuple(paths), root, run) for name, paths in asked_of.items()
    }
    # The first carrier whose edit the base has not taken, and the id drops out
    # only where every one of them is superseded or unread. `marks` is in
    # `walk.edited`'s order and each id's carriers are in rank order within it,
    # so the head of a list nothing removes is the ref the collapse chose.
    edited: dict[str, str] = {}
    for identifier, name, path in marks:
        if identifier in edited or path in superseded_by_ref[name]:
            continue
        edited[identifier] = _preferred(name, candidates)

    # **A queue-only commit about an item that wrote into it is work where the
    # item says so** (`PL-7790`, `PL-VYSP`, `PL-8FJK`). `_annotates_only`
    # withheld the claim because the diff never left `docs/items/`, which is
    # where the work lives for an item whose deliverable is the queue, for one
    # at `needs-decision`, and for one a grooming pass is closing - so the mark
    # is restored from the item rather than from the commit's paths, by
    # `_own_edit_claims`, which `precedence` asks the same way. The carrier is
    # the ref that led with the id, never whichever ref `editing` happened to
    # credit the file to: a batch pass writing the same file must not be named
    # as the session doing the work, and feeding the first promotion from
    # `editing` is what claimed four items a `verify:` reorder passed through
    # (`PL-3W3P`). A copy the base already holds was found superseded above and
    # is not a claim.
    #
    # **Each carrier is offered, and the first survivor is the claim**
    # (`PL-61MD`). Supersession is asked here, per carrier; the rest are asked
    # by the helper, once per id where the answer is a fact about the base and
    # once per carrier where it is a fact about that ref. The id leaves the
    # promotion only where every carrier fails.
    offered = {
        identifier: unspent
        for identifier, rounds in own.items()
        if (
            unspent := [
                (name, commit, paths)
                for name, commit, paths in rounds
                if any(path not in superseded_by_ref.get(name, set()) for path in paths)
            ]
        )
    }
    claimed = _own_edit_claims(offered, items_dir, base, root, run)
    for identifier, claimers in sorted(claimed.items()):
        edited.pop(identifier, None)
        carrier = _preferred(claimers[0], candidates)
        in_flight[identifier] = Branch(
            name=carrier,
            item_id=identifier,
            last_commit=last_commit.get(carrier) or last_commit.get(claimers[0]),
        )

    # **Read, and attributable to nothing.** Confined to refs whose commits the
    # walk actually reached: an unread ref contributes no subjects, so calling
    # it unattributed would be inventing the absence of an id rather than
    # reading one. `_preferred` collapses a local branch and its tracking ref,
    # which are one piece of work named twice.
    # `--source` credits a commit to whichever of two refs holding it git
    # reached first, and a local branch and its tracking ref are one piece of
    # work; so both sides are collapsed through `_preferred` before they are
    # compared, or a branch whose commits git credited to its tracking ref
    # reads as naming nothing.
    attributed = {_preferred(name, candidates) for name in walk.named}
    unattributed = {
        preferred
        for preferred in (
            _preferred(name, candidates) for name in candidates if name in unlanded_set
        )
        if preferred not in attributed and BRANCH_ID_RE.search(preferred) is None
    }
    # **The base's own copy decides the wording, and only the wording**
    # (`PL-3CTW`). One tree listing, which the promotions above have
    # usually already paid for - the runner memoizes, so asking again is free.
    landed = set(_item_paths_on(base, items_dir, root, run))
    return FlightReport(
        branches=tuple(
            sorted(
                (
                    replace(branch, on_base=branch.item_id.upper() in landed)
                    for branch in in_flight.values()
                ),
                key=lambda branch: branch.item_id,
            )
        ),
        unreadable=tuple(name for name in candidates if name in unreadable),
        unattributed=tuple(name for name in candidates if name in unattributed),
        editing=tuple(
            QueueEdit(name=name, item_id=identifier, last_commit=last_commit.get(name))
            for identifier, name in sorted(edited.items())
        ),
        base=base,
        declined=run.reason,
    )


@dataclass(frozen=True)
class Carrier:
    """One piece of work carrying an item, and the commit where it said so.

    Identified by that commit rather than by the ref that reached it, because a
    local branch and its own tracking ref are one session's work seen twice and
    telling a session to yield to itself is the one answer this must never
    give. `ref` is therefore a label - whichever ref git credited the commit to
    - and never the thing being compared.

    `mine` follows from the same identity: this checkout is carrying the work
    when its `HEAD` *contains* the staking commit, which is true of the local
    branch, its tracking ref, and a branch pushed under some third name alike.
    Matching branch names would answer only the first of those, and would
    answer it wrongly the moment `--source` credited the shared commit to the
    tracking ref - which is what it does whenever the local branch is ahead by
    so much as a merge.

    `staked` is `None` for a ref whose name carries the id and whose commits
    this checkout could not read. That is a claim it cannot date rather than
    one made at the beginning of time, so it sorts *behind* every dated claim:
    an unread ref put first would make every session that can read its own
    commits yield to it, which in a truncated clone is every session.
    """

    ref: str
    item_id: str
    staked: Stake | None = None
    last_commit: datetime | None = None
    mine: bool = False


@dataclass(frozen=True)
class Precedence:
    """Which branch carrying an item continues, and which yield to it.

    **The point is that two sessions compute this identically, so it is a total
    order rather than a judgment.** Everything else this module does about
    parallel sessions detects a collision; nothing said which of the two
    discovering it was the one to stop, and two sessions reasoning in prose
    from the same evidence can reach the same answer as each other or the
    opposite one, with no way to tell which happened until the merge. The
    failure that costs the most is not both continuing - that is merely today -
    but both standing down, after which the work is unstarted and each session
    believes the other has it.

    So the order is over commits: the earliest commit naming the item holds it,
    a tie breaks on that commit's hash. Both properties are load-bearing. It is
    the *earliest* commit rather than the newest, so a session that pushes
    after a break does not overtake one that started before it; and it is a
    commit rather than a push time, because git records no push time and
    because a commit's date is the same fact in both checkouts.

    Two sessions can still both continue, when one has pushed nothing the other
    can see. That is the state of the world before this existed, so it is not a
    regression, and it is what `PL-SK88`'s "push the first commit as soon as
    there is one" shrinks. What cannot happen is both yielding: yielding needs
    a carrier strictly ahead of your own in one order, and two carriers cannot
    each be ahead of the other.
    """

    item_id: str
    carriers: tuple[Carrier, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""
    branch: str = ""
    #: Why this ordering is partial: git was asked something and did not answer.
    #:
    #: It matters more here than anywhere else in the module, because the whole
    #: point above is that two sessions compute one order from one set of facts.
    #: A silence gives them *different* sets - one session's `diff` fails and
    #: the other's does not - so the guarantee that they cannot both stand down
    #: rests on both of them knowing when the evidence was incomplete
    #: (`PL-Q9Z1`).
    declined: str = ""

    @property
    def holder(self) -> Carrier | None:
        """The carrier that continues, or `None` where nothing carries the item."""
        return self.carriers[0] if self.carriers else None

    @property
    def mine(self) -> Carrier | None:
        """This checkout's own claim, or `None` where it has staked none."""
        return next((carrier for carrier in self.carriers if carrier.mine), None)

    @property
    def yields(self) -> bool:
        """Whether this checkout is carrying the item and is not the one that continues.

        False where this checkout carries nothing, which is the ordinary state
        of a session that has not started: there is no work to hand over and
        nothing to yield. That case is what `branches_in_flight` already
        reports, and reporting it here as a yield would turn the first guard a
        session meets into an instruction to stop before it began.
        """
        mine = self.mine
        return mine is not None and mine is not self.holder

    @property
    def known(self) -> bool:
        """Whether git answered every question this ordering rests on."""
        return not self.declined


def _head_carries(stake: Stake | None, root: Path, run: Runner) -> bool:
    """Whether this checkout's `HEAD` holds the commit that staked a claim.

    Asked by containment rather than by comparing branch names, because a
    session's own work reaches it under several names - the local branch, its
    tracking ref, a branch pushed under a third one - and the walk credits the
    commit to exactly one of them. A name comparison therefore reports "not
    yours" for a session's own branch as soon as it is ahead of its tracking
    ref by anything at all, including the merge that keeps it current, and a
    session told to yield to itself would stop for nobody.

    `merge-base` rather than `--is-ancestor`, whose answer is an exit code:
    every failure in this module collapses to the empty string, and an exit
    code that means "no" would be indistinguishable from git not running.
    """
    if stake is None:
        return False
    return run(["merge-base", stake.commit, "HEAD"], root).strip() == stake.commit


def precedence(
    root: Path,
    item_id: str,
    *,
    include_remote: bool = True,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> Precedence:
    """Every branch carrying one item, in the order that decides which continues.

    `branches_in_flight` reports one branch per item deliberately - it is
    answering "is this startable", and a second name adds nothing to that. Here
    the second name *is* the answer, so the same evidence is read again without
    that collapse, and with the timestamps a day-resolution report has no use
    for.

    **Only what is pushed can settle it, and this reads local refs anyway.** A
    claim nobody else can fetch cannot enter the other session's ordering, so
    two sessions reading only remote refs is the configuration in which they
    always agree. But a session's own unpushed branch is exactly what it needs
    to be told about - that its claim is invisible, and one push makes it real
    - and dropping local refs would hide the case rather than fix it. The
    asymmetry it leaves is the benign one: a session whose rival has pushed
    nothing sees no rival and continues, which is where the world already was.
    """
    run = _Silences(runner or _run_git)
    identifier = item_id.upper()
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    walk = _unmerged_commits(refs.unlanded, base, root, run, items_dir=items_dir)
    unreadable = refs.unreadable | walk.unbounded
    readable = {name for name in refs.unlanded if name not in walk.unbounded}
    # A queue-only commit that led with the id and wrote its own file is
    # withheld by `staked`, and for an item whose work is the queue, one at
    # `needs-decision` or one this ref is closing it is the claim - so it is
    # read here through the helper and the supersession test
    # `branches_in_flight` promotes it with. The two reads have to agree about
    # what is carrying the item, and not only for the verdict: `show` prints
    # the in-flight mark *through* this verdict, so a promotion read there and
    # not here printed no mark at all (`PL-VYSP`, `PL-7790`, `PL-8FJK`). Asked
    # only where some readable ref made such a commit.
    offered: list[tuple[str, str, tuple[str, ...]]] = []
    for name in refs.candidates:
        if name not in readable or (name, identifier) not in walk.own_edits:
            continue
        commit, paths = walk.own_edits[(name, identifier)]
        taken = _superseded(name, base, paths, root, run)
        if any(path not in taken for path in paths):
            offered.append((name, commit, paths))
    claiming = (
        set(_own_edit_claims({identifier: offered}, items_dir, base, root, run).get(identifier, []))
        if offered
        else set()
    )

    # Candidate order, so that the ref a group is *named* by is chosen the same
    # way `branches_in_flight` chooses it: a local branch ahead of its own
    # tracking ref.
    staked: dict[str, Stake | None] = {}
    grouped: dict[str, list[str]] = {}
    moved: dict[str, datetime] = {}
    for name in refs.candidates:
        if name not in readable and name not in unreadable:
            continue
        match = BRANCH_ID_RE.search(name)
        by_name = match is not None and match.group(1).upper() == identifier
        claims: list[Stake] = []
        if name in readable:
            # A branch named for the item has been carrying it since its first
            # commit; a branch named for anything else has been carrying it
            # only since the commit that said so, which is what dates a rider
            # picked up mid-branch from the branch it rode in on.
            if by_name and (opened := walk.opened.get(name)) is not None:
                claims.append(opened)
            if (subject := walk.staked.get((name, identifier))) is not None:
                claims.append(subject)
            if name in claiming and (own := walk.own_staked.get((name, identifier))) is not None:
                claims.append(own)
        if not claims and not by_name:
            continue
        stake = min(claims) if claims else None

        # The commit is the identity of the claim, so one piece of work reached
        # by two refs groups under it whatever those refs are called. A claim
        # with no readable commit can only be grouped by its own name, which is
        # right: nothing proves it is the same work as anything else.
        key = stake.commit if stake is not None else f"\x00{name}"
        grouped.setdefault(key, []).append(name)
        staked[key] = stake
        if (when := walk.last.get(name)) is not None and when > moved.get(key, _EARLIEST):
            moved[key] = when

    branch = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    if branch == "HEAD":
        # A detached HEAD is not a branch, and nothing here needs it to be one:
        # the claims are matched against what HEAD *contains*.
        branch = ""
    carriers = sorted(
        (
            Carrier(
                ref=names[0],
                item_id=identifier,
                staked=staked[key],
                last_commit=moved.get(key),
                mine=_head_carries(staked[key], root, run),
            )
            for key, names in grouped.items()
        ),
        key=lambda carrier: (carrier.staked is None, carrier.staked or _UNDATED, carrier.ref),
    )

    # One session, one claim. A branch whose commits reach two of these is
    # carrying one piece of work that git happened to credit to two refs, and
    # the earliest of them is when this checkout began carrying it - so the
    # later ones are dropped rather than listed as rivals of the first.
    seen_mine = False
    collapsed: list[Carrier] = []
    for carrier in carriers:
        if carrier.mine:
            if seen_mine:
                continue
            seen_mine = True
        collapsed.append(carrier)

    return Precedence(
        item_id=identifier,
        carriers=tuple(collapsed),
        unreadable=tuple(name for name in refs.candidates if name in unreadable),
        base=base,
        branch=branch,
        declined=run.reason,
    )


@dataclass(frozen=True)
class BranchFiles:
    """What one in-flight ref has actually changed since the default branch.

    `item_ids` is every item `branches_in_flight` attributed to this ref, so a
    reader told their file is being edited can also be told by whom. It may be
    empty in principle and is not in practice: a ref reaches here only because
    an id was read from its name or its subjects.
    """

    branch: str
    item_ids: tuple[str, ...]
    paths: tuple[str, ...]


@dataclass(frozen=True)
class FlightFiles:
    """What the in-flight branches are changing, and which could not be read.

    This is the *observed* half of the contention question, against `touches`,
    which is the declared half. The two fail in opposite directions and that is
    why both are worth having. A `touches` list is a prediction written before
    the work, so it is complete about intent and silent about drift; a branch
    diff is a measurement taken during the work, so it is exact about what has
    happened so far and says nothing about what the branch will touch next.
    Neither certifies a pair as safe, and this one does not either: it names
    what has *already* collided.

    `unreadable` carries the same obligation it does on `FlightReport`, for the
    same reason. `_run_git` answers a failure with an empty string, so an
    unreadable diff and a branch that changed nothing arrive here identically -
    and reporting the first as the second would turn a gap in the evidence into
    a clean bill of health, which is the one thing this package refuses to do.
    """

    branches: tuple[BranchFiles, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""
    #: Why this reading is partial, in the sense `FlightReport.declined` carries
    #: it: git was asked something and did not answer, so a branch that appears
    #: to have changed nothing may only have gone unread (`PL-Q9Z1`).
    declined: str = ""

    @property
    def known(self) -> bool:
        """Whether git answered every question this reading rests on."""
        return not self.declined


def files_in_flight(
    root: Path, report: FlightReport, *, runner: Runner | None = None
) -> FlightFiles:
    """The files each in-flight branch has changed, read from the branch itself.

    Kept out of `branches_in_flight` deliberately. That read is on the hot path
    of `next`, `list`, `triage`, `status` and the session-start digest, and this
    one costs a `git diff` per unmerged ref - so it is paid by the two callers
    that ask the file question and by nobody else.

    A ref `branches_in_flight` could not read is not read here either. Its
    commits are the thing the checkout is missing, and a three-dot diff needs
    exactly the merge-base that already failed to resolve, so asking again
    would produce an empty answer indistinguishable from a branch that changed
    nothing.

    The diff is `base...ref` rather than `base..ref`: the two-dot form re-reports
    every file the default branch has changed since the fork as though the
    branch had changed it, which for a session started a day ago is most of the
    tree. The three-dot form is the branch's own work, which is the question.
    """
    run = _Silences(runner or _run_git)
    base = report.base
    if not base:
        return FlightFiles(declined=report.declined)

    ids: dict[str, list[str]] = {}
    for branch in report.branches:
        ids.setdefault(branch.name, []).append(branch.item_id)

    unread = set(report.unreadable)
    found: list[BranchFiles] = []
    for name, item_ids in ids.items():
        if name in unread:
            continue
        paths = tuple(
            sorted(
                {
                    line.strip()
                    for line in run(["diff", "--name-only", f"{base}...{name}"], root).splitlines()
                    if line.strip()
                }
            )
        )
        # An empty diff is either a branch whose commits cancel out or a git
        # that failed, and the two must not be conflated. A ref carrying
        # commits the base does not have owes a non-empty file list, so when it
        # does not, the read is named as unread rather than reported as clean.
        if not paths and _has_own_commits(name, base, root, run):
            unread.add(name)
            continue
        found.append(BranchFiles(branch=name, item_ids=tuple(sorted(item_ids)), paths=paths))

    return FlightFiles(
        # The report is half the evidence, so a reading it could not complete is
        # one this cannot complete either: the branches it never named are
        # branches whose files are not asked about here (`PL-Q9Z1`).
        declined=report.declined or run.reason,
        branches=tuple(sorted(found, key=lambda entry: entry.branch)),
        unreadable=tuple(sorted(unread)),
        base=base,
    )


def _has_own_commits(name: str, base: str, root: Path, run: Runner) -> bool:
    """Whether the ref holds commits the default branch does not.

    Only asked to disambiguate an empty diff, so the cost is paid on the rare
    branch rather than on every one.
    """
    count = run(["rev-list", "--count", f"{base}..{name}"], root).strip()
    return count.isdigit() and int(count) > 0


@dataclass(frozen=True)
class SettledBranch:
    """One unmerged ref on which nothing is left for anybody to work.

    `item_ids` is every item this ref claimed, all of them closed in the ref's
    own copy; `last_commit` is when it last moved, carried across from the
    flight report so a reader judging how long it has sat does not have to look
    it up separately.
    """

    name: str
    item_ids: tuple[str, ...]
    last_commit: datetime | None = None


@dataclass(frozen=True)
class SettledReport:
    """Which unmerged refs are finished, and whether the forge could be asked.

    **`asked` is why this is a type rather than a list**, and it is the same
    refusal `FlightReport.unreadable` and `PullRequestHistory.declined` make:
    an empty answer meaning "could not look" must never render as "looked, and
    found none open". A ref is settled here only when its items are closed
    *and* nobody has a pull request open on it, so a reading that could not ask
    the second question has proved half of the claim. It is reported as half,
    and the caller that prints it says which half.

    `declined` carries the usual meaning: git was asked something and did not
    answer, so an absent row may only have gone unread.
    """

    branches: tuple[SettledBranch, ...] = ()
    #: Whether the pull-request half of the test was answered at all. `False`
    #: is a bare checkout, no token, no network, or a forge that refused - and
    #: every row here is then "every item closed" alone.
    asked: bool = True
    declined: str = ""

    @property
    def known(self) -> bool:
        """Whether every question this reading rests on was answered."""
        return not self.declined and self.asked


def _remotes(root: Path, run: Runner) -> frozenset[str]:
    """The remotes this checkout knows, for stripping a tracking ref's prefix."""
    return frozenset(name.strip() for name in run(["remote"], root).splitlines() if name.strip())


def _head_name(name: str, remotes: frozenset[str]) -> str:
    """The branch name a forge knows this ref by.

    `origin/claude/pl-k7qx-thing` and `claude/pl-k7qx-thing` are one branch, and
    a pull request names the second. Stripped against the remotes git actually
    lists rather than against the first path segment, so a local branch that
    happens to be called `origin/...` - or, more plausibly, one whose first
    segment is a word like `feature` - keeps its whole name.
    """
    prefix, _, rest = name.partition("/")
    return rest if rest and prefix in remotes else name


def settled_branches(
    root: Path,
    report: FlightReport,
    *,
    opened: Callable[[], Collection[str] | None] | None = None,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> SettledReport:
    """The in-flight refs that have finished: every item closed, and nothing open.

    `branches_in_flight` cannot tell a live session from a branch nobody will
    merge, says so, and leaves the age to separate them. Age is a weak
    separator where a session turns around in under an hour, and it fails in
    the costly direction on the one case that matters most: work that is
    *finished*, sitting on a branch with no pull request behind it, reported to
    every session as "in flight ... do not start these again". That reading is
    exactly backwards - nobody is doing it, and nobody will. `PL-Q664` is the
    worked instance: two items at `status: done`, ten item files existing
    nowhere else, and three hours before anybody noticed.

    Two facts separate that case, and neither is the age. Every item the ref
    claims is closed **in the ref's own copy**, which is where a session that
    finished the work wrote it; and no pull request is open on the ref, which
    is what a session that finished *and* opened one would have left. Both
    together are what says nothing is being worked. Either one alone is
    ordinary: a branch mid-review has closed its items, and a branch with no
    pull request is usually a session still working.

    **Kept out of `branches_in_flight` for the reason `files_in_flight` is.**
    That read is on the hot path of `next`, `list`, `triage`, `show` and the
    session-start digest, and this one costs a `git show` per claimed item plus,
    where there is a candidate at all, whatever asking the forge costs. It is
    paid by the command that asks the question and by nobody else.

    **It never changes what is in flight.** The ids stay excluded from `docket
    next`, because the work exists on a branch and offering it again would have
    a second session redo it. What changes is only how a reader is told: a row
    moved out of the list the age is meant to separate, into one that says
    plainly that nothing there is being worked.

    **The forge is asked through `opened`, never reached from here.** This
    package answers from a bare checkout with no network and knows nothing
    about GitHub; the caller supplies a way to ask which branch names have a
    pull request open, and `None` - no way to ask, no token, no network - is
    carried into the report as `asked=False` rather than read as "none is
    open". It is a callable rather than a collection so that the cost is paid
    only where the cheap half found a candidate: a checkout whose branches are
    all still working never asks at all.

    Every silence fails toward the live reading. A ref whose commits went
    unread, an item the ref does not hold a copy of, a `git show` that returned
    nothing: each leaves the ref out of this report and in the ordinary
    in-flight list, because a live session wrongly called finished is the
    expensive mistake and finished work wrongly called live is the one this
    repository already has.
    """
    run = _Silences(runner or _run_git)
    unread = set(report.unreadable)
    carried: dict[str, list[str]] = {}
    for branch in report.branches:
        if branch.name in unread:
            continue
        carried.setdefault(branch.name, []).append(branch.item_id)

    finished: list[SettledBranch] = []
    for name, ids in carried.items():
        held = _items_at(name, root, items_dir, run)
        paths = [held.get(identifier.upper(), "") for identifier in ids]
        if not all(paths) or not all(_closed_at_ref(name, path, root, run) for path in paths):
            continue
        finished.append(
            SettledBranch(
                name=name,
                item_ids=tuple(sorted(ids)),
                last_commit=next((b.last_commit for b in report.branches if b.name == name), None),
            )
        )

    if not finished:
        # Nothing to ask the forge about, so it is not asked - and the report
        # says the question was answered, because a set with no members in it
        # has no member whose pull request went unchecked.
        return SettledReport(declined=report.declined or run.reason)
    if opened is None:
        return SettledReport(
            branches=tuple(sorted(finished, key=lambda entry: entry.name)),
            asked=False,
            declined=report.declined or run.reason,
        )
    answer = opened()
    if answer is None:
        return SettledReport(
            branches=tuple(sorted(finished, key=lambda entry: entry.name)),
            asked=False,
            declined=report.declined or run.reason,
        )
    remotes = _remotes(root, run)
    heads = {head.strip() for head in answer if head.strip()}
    return SettledReport(
        branches=tuple(
            sorted(
                (entry for entry in finished if _head_name(entry.name, remotes) not in heads),
                key=lambda entry: entry.name,
            )
        ),
        declined=report.declined or run.reason,
    )


@dataclass(frozen=True)
class OpenPullRequests:
    """Which in-flight refs have a pull request open, where the forge was asked.

    **`asked` is why this is a type rather than a mapping**, for the reason
    `SettledReport.asked` is: a ref absent from `numbers` has no pull request
    open *only when the forge answered*, and "could not look" read as "none is
    open" would tell a reader that work waiting on review is a session still
    typing.
    """

    #: Per ref, spelled as `FlightReport.branches` spells it, the number of the
    #: pull request open for it - `None` where the forge named the branch
    #: without a number. Every ref the forge was asked about and did not name
    #: is absent.
    numbers: Mapping[str, int | None] = field(default_factory=dict)
    #: Whether the forge answered at all. `False` is a bare checkout, no token,
    #: no network, `--no-remote`, or a forge that refused.
    asked: bool = False
    #: Git was asked something beneath this reading and did not answer - the
    #: flight report's own silence, or the remotes this matches names against.
    declined: str = ""

    @property
    def known(self) -> bool:
        """Whether every question this reading rests on was answered."""
        return not self.declined and self.asked


def open_pull_requests(
    root: Path,
    report: FlightReport,
    *,
    opened: Callable[[], Mapping[str, int | None] | None] | None = None,
    runner: Runner | None = None,
) -> OpenPullRequests:
    """Which of the refs carrying an item have a pull request open on them.

    **The second fact a row needs, because the age alone cannot fire in the
    first hour** (`PL-7TVT`). A branch outlives its session, so a young branch
    and a branch whose session ended ten minutes ago read alike by age, and the
    one reading that separates part of that is the forge's: with a pull request
    open, the work is written and waits on review, whoever or nothing is still
    driving it. PR `#757` sat green for 25 minutes after its session was
    archived while its three items read as somebody's live work, and nothing
    `flight` printed could have said otherwise.

    Asked through the same `opened` that `settled_branches` takes, and for the
    same reason: this package answers from a bare checkout with no network and
    knows nothing about GitHub, so the caller supplies the way to ask. It is
    asked only where a ref is carrying something, and a caller holding both
    readings passes one memoized callable to each so the forge is asked once.

    Unlike `settled_branches`, it asks on every run that has a row to answer
    for - which is nearly every run. That is the price of the row carrying the
    fact, and it was measured before it was paid: one request, 0.55 s in an
    agent session on 2026-09-22, and every way it fails is a row printed
    without the clause.
    """
    names = {branch.name for branch in report.branches}
    if not names or opened is None:
        return OpenPullRequests(declined=report.declined)
    answer = opened()
    if answer is None:
        return OpenPullRequests(declined=report.declined)
    run = _Silences(runner or _run_git)
    remotes = _remotes(root, run)
    if run.reason:
        # Without the remotes, `origin/claude/x` cannot be matched to the
        # branch a pull request names, and every row would read "none open" -
        # the confident wrong answer `asked` exists to prevent.
        return OpenPullRequests(declined=report.declined or run.reason)
    heads = {head.strip(): number for head, number in answer.items() if head.strip()}
    return OpenPullRequests(
        numbers={
            name: heads[head]
            for name in sorted(names)
            if (head := _head_name(name, remotes)) in heads
        },
        asked=True,
        declined=report.declined,
    )


def _closed_at_ref(ref: str, path: str, root: Path, run: Runner) -> bool:
    """Whether the ref's own copy of one item records it closed.

    The ref's copy rather than the base's, which is the whole distinction:
    `_closed_on_base` asks whether an item has *shipped*, and this asks whether
    the session on this branch finished it. A read that comes back empty is a
    `git show` that failed or a file that is not there, and answers `False`,
    which keeps the ref in the ordinary in-flight list.
    """
    text = run(["show", f"{ref}:{path}"], root)
    return bool(text) and parse_item(text, path.rsplit("/", 1)[-1]).status in CLOSED_STATUSES


def default_base(root: Path, *, runner: Runner | None = None) -> str:
    """The ref a branch should be compared against, preferring the remote's.

    `main` names the *local* branch, which in a fresh clone - the normal state
    for an agent session, which starts from one - can sit many commits behind
    what everyone else has pushed. A diff taken against it reports every file
    that landed in between as this branch's own work: verifying PL-VP7N that
    way named 20 paths outside the item's commission where the true answer was
    4, the other 16 being item files other sessions had merged. So the remote
    ref is preferred wherever it resolves, because that is what the branch
    actually forked from.

    **An answer nothing established is marked, and two cases reach that mark.**
    Where no candidate resolves, the answer is `GUESSED_BASE` rather than the
    bare literal `main`. Where one resolves only after a preferred candidate
    went unanswered, that name comes back marked too - it is a real ref, and
    still not the one this repository forks from. The
    two compare equal and format alike, so a caller with no use for the
    distinction reads what it always read; one that must not compare against a
    ref nobody established asks `resolved`. Before `PL-73P0` the fallback was
    the bare literal, and a checkout holding no default branch was handed a
    string indistinguishable from one where `main` was really there.

    Two different failures reach that fallback, and only one of them was ever
    visible. Git may answer nothing - no repository, no git - which `_Silences`
    catches beneath any read that wraps its runner (`PL-Q9Z1`). Or git may
    answer, truthfully, `no` to all four candidates, which is a checkout that
    genuinely has no default branch: nothing failed, so no silence is raised
    and the wrapper sees nothing. That second case is why marking the return
    value is not enough on its own, and why this also sets `guessed_base` on a
    `_Silences` runner on the way past - the sixteen reads in this module that
    wrap one then decline with the cause rather than with whichever call git
    happened to refuse afterwards.

    The two callers that pass no wrapped runner - `cli`'s `verify` and
    `tools/branch_id_check` - read `resolved` directly, which is the whole of
    what `PL-29HL` asked for before it was folded in here.
    """
    run = runner or _run_git
    silenced = False
    for candidate in DEFAULT_BRANCHES:
        answer = run(["rev-parse", "--verify", "--quiet", candidate], root)
        if answer.strip():
            # Reached by falling past a candidate git would not answer for, so
            # the ref that did resolve is not established as the preferred one:
            # `origin/main` may be sitting there unread. Marked rather than
            # returned plain, because this is the fallback the docstring above
            # measures at 20 paths reported against a true 4.
            return GuessedBase(candidate) if silenced else candidate
        if not answered(answer):
            silenced = True
    if isinstance(run, _Silences):
        run.guessed_base = True
    return GUESSED_BASE


def behind_remote(root: Path, base: str, *, runner: Runner | None = None) -> int | None:
    """How many commits `base` trails its own remote-tracking branch.

    `None` when the question does not arise - `base` is already a remote ref,
    has no counterpart on `origin`, or the count cannot be read - and `0` when
    it is current. The distinction is worth keeping after `default_base` moved
    the default to the remote ref, because `--base main` can still be passed
    by hand, and a stale answer that looks clean is the failure being guarded
    against rather than the flag that produced it.
    """
    run = runner or _run_git
    if "/" in base:
        return None
    remote = f"origin/{base}"
    if not run(["rev-parse", "--verify", "--quiet", remote], root).strip():
        return None
    counts = run(["rev-list", "--count", f"{base}..{remote}"], root).strip()
    return int(counts) if counts.isdigit() else None


# What a branch should do about where it stands, decided from the counts rather
# than from the words used to say it. `render` turns one of these into a
# sentence and a command; keeping the choice here is what lets a test assert
# the decision without matching prose, and what stops two callers wording the
# same state differently.
CURRENT = "current"
RESTART = "restart"
PULL = "pull"
MERGE = "merge"
REWRITTEN = "rewritten"
#: A branch the base has already taken work from, which has gained a commit
#: since. The counts cannot reach it: a squash merge leaves the branch
#: containing none of the commits that landed its content, so `ahead` counts
#: them all and `RESTART` - which fires at `ahead == 0` - is never reached.
#: It is read from the content instead, by `landed_whole` (`PL-8M8H`).
LANDED = "landed"


@dataclass(frozen=True)
class RewriteReport:
    """A divergence that is one history under two sets of hashes, and what only one side holds.

    A history rewrite - `filter-repo`, `filter-branch`, a force-pushed rebase
    of the default branch - replaces every commit on the base. A branch still
    sitting on the old history is then counted as hundreds behind *and*
    hundreds ahead, which reads exactly like a branch carrying a great deal of
    work. It is not: almost every one of those commits is the base's own under
    its old hash. The few that are not are the only copy of themselves
    anywhere, and `git merge`, `git reset --hard` and `git checkout -B` - the
    three things that ahead/behind line invites - each lose or bury them.
    `PL-YGF3` is the incident: two commits survived only because the session
    that wrote them still held them in a live working tree.

    `duplicated` counts the branch's own commits that reappear on the base
    under a different hash; `own` is the rest, oldest first, which is the work
    that exists nowhere else and has to be carried across by hand. `merges`
    says whether any of those is a merge commit, because that changes the
    recovery - `git cherry-pick` refuses one without `-m`.
    """

    duplicated: int = 0
    own: tuple[tuple[str, str], ...] = ()
    merges: bool = False

    @property
    def total(self) -> int:
        """How many commits the branch holds that the base does not, counted by hash."""
        return self.duplicated + len(self.own)


@dataclass(frozen=True)
class BranchState:
    """Where the working branch stands against the default branch, and what moved.

    `declined` carries the meaning it does everywhere else here: the question
    could not be answered, and why. A checkout sharing no readable history with
    the default branch is the case that matters, because `git rev-list
    --left-right --count A...B` does not fail there - it prints the size of
    each side of an unrelated pair, which reads exactly like a real answer. A
    fabricated "98 ahead" tells a session it is carrying work it does not have,
    which argues against merging in the very case this exists to catch.

    `landed` is what makes it worth running twice. The counts say the base
    moved; the ids say *what* moved, which is what a session waiting on another
    session actually wants to know, and it costs one `git log` over a range
    already computed.

    `fetched` is not about git's answer but about how old the refs behind it
    are. This reads what the checkout holds and never fetches - the decision
    has to stay answerable from a bare checkout with no network - so a caller
    that did not refresh `origin/main` first gets an answer as stale as its
    last fetch, and saying so is the difference between a report and a guess.

    `absent` separates the two shapes of "no position" that the session-start
    hook has always distinguished by staying silent. A detached HEAD, a
    checkout with no base, and the default branch itself with no remote copy
    are cases where *no comparison exists*, and a digest resent on every turn
    should not carry a line saying so. A clone that shares no readable history
    is the other shape: the comparison exists and could not be made, which is
    the one that has to be said out loud.

    It records that the caller *attempted* a refresh, not that one arrived: a
    quiet `git fetch` prints nothing whether it succeeded or failed, and no
    read here can tell those apart. So it is reported only in the negative -
    nothing tried - which is the claim that can be made. A fetch that tried and
    failed leaves the answer stale by exactly one fetch, which is the error the
    session-start hook has always accepted.
    """

    branch: str = ""
    base: str = ""
    behind: int = 0
    ahead: int = 0
    landed: tuple[str, ...] = ()
    #: Whether the base has already taken a whole commit of this branch's work,
    #: read from the content rather than from the counts or from `landed`.
    #:
    #: Populated by `branch_state` only where the counts would otherwise say
    #: `MERGE`, because that is the one arm whose advice it changes and the
    #: read costs three git calls that every other arm would pay for nothing.
    #: `False` therefore means "not asked" as often as it means "no", which is
    #: the safe direction: a branch wrongly left at `MERGE` is where this
    #: started, and a branch wrongly sent to `LANDED` is told to restart.
    #:
    #: **Not `landed` above, which is subject-derived.** `_landed_since` reads
    #: leading ids off the base's new subjects, so it proves nothing about
    #: content and names ids from every branch that merged rather than this
    #: one. It already contradicts the `MERGE` advice printed above it, two
    #: lines apart, and it still must not be the detector.
    landed_whole: bool = False
    rewrite: RewriteReport | None = None
    fetched: bool = False
    declined: str = ""
    absent: bool = False

    @property
    def disposition(self) -> str:
        """Which of the six states this is, or `""` when there is no answer.

        `REWRITTEN` outranks both `PULL` and `MERGE` because it contradicts
        them: where the divergence is duplicated history, pulling or merging
        replays the base's own commits against themselves, and it is the
        default branch - the `PULL` case - where a local copy left on the old
        history does the most damage.

        `LANDED` sits below `REWRITTEN` and above `MERGE` for the same reason
        and in the same direction. It contradicts `MERGE` outright - a push to
        a branch whose pull request already merged is merged by nothing, so
        merging the base in and pushing loses the commit at the one moment
        recovering it is still free (`#284`, `PL-8M8H`). And it must sit
        *below* `REWRITTEN`, because a branch left on pre-rewrite history has
        every mark of one whose pull request merged: the rewrite changed every
        hash and left every byte alone, so the content split cannot tell them
        apart, and the existing arm excludes that shape at no cost.
        """
        if self.declined:
            return ""
        if self.behind == 0:
            return CURRENT
        if self.rewrite is not None:
            return REWRITTEN
        if self.is_default:
            return PULL
        if self.ahead == 0:
            return RESTART
        return LANDED if self.landed_whole else MERGE

    @property
    def is_default(self) -> bool:
        """Whether the working branch is the default branch itself."""
        return bool(self.branch) and self.base.rsplit("/", 1)[-1] == self.branch


def _landed_since(
    fork: str, base: str, root: Path, run: Runner, limit: int = 40
) -> tuple[str, ...]:
    """The ids leading the subjects the default branch gained since the fork.

    Only a leading id counts, for the reason `_unmerged_commits` gives: a
    subject mentioning an item further in is usually bookkeeping about somebody
    else's work. Bounded, because a branch forked long ago would otherwise
    print a release's worth of ids into a digest line - the newest are the ones
    a session waiting on something wants.
    """
    output = run(["log", f"-n{limit}", "--format=%s", f"{fork}..{base}", "--"], root)
    found: list[str] = []
    for line in output.splitlines():
        for identifier in leading_ids(line):
            if identifier not in found:
                found.append(identifier)
    return tuple(found)


def _duplicated_history(
    base: str, root: Path, run: Runner, *, ref: str = "HEAD"
) -> RewriteReport | None:
    """Whether the divergence from `base` is one rewritten history, and what only this side holds.

    `ref` is which side to read, and it defaults to the checkout's own `HEAD`
    because `branch_state` - which this was built for - advises the session
    about the branch it is standing on. `orphaned` passes a named ref instead:
    a branch left on pre-rewrite history reads there as one whose pull request
    merged, because that report's evidence is file content and a rewrite
    changes every hash while leaving content untouched (`PL-Y31G`).

    **Stateless, and that is a requirement rather than a preference.** The
    obvious test - has the remote ref moved to something that is not a
    descendant of what this checkout last saw - needs a memory of the old
    value, and the only one git keeps is the remote-tracking reflog. A
    container clones fresh, so in the session that most needs the answer - one
    opened after the rewrite, with nothing left in a working tree to copy out -
    that reflog holds a single entry and the test cannot fire. This reads the
    shape of the divergence instead, which any checkout can do at any moment.

    The fingerprint is that a rewrite **preserves author date and subject while
    changing every hash**, so the two sides of the symmetric difference hold
    the same commits twice over. The rule is that the *oldest* commit unique to
    this side has a counterpart on the base: the divergence begins in
    duplicated history, which is what a rewrite leaves behind and what forking
    and then committing cannot produce. A branch that merely sat while the base
    moved matches nothing there and gets `None`.

    Matched on author date and subject rather than on patch id - what `git
    cherry` uses - for two reasons that both bit the incident behind
    `PL-YGF3`. The rewrite stripped a file out of history, so the patch of
    every commit that had ever touched it changed; and `git cherry` drops merge
    commits entirely, while one of the two commits actually lost was a merge.

    Returns `None` rather than a claim wherever the read fails, which leaves
    the ordinary behind/ahead advice in place. That is the same posture the
    rest of this module takes: what it reports present is present, and silence
    is never evidence.
    """
    output = run(
        [
            "log",
            "--topo-order",
            "--reverse",
            "--left-right",
            "--format=%m%x00%h%x00%at%x00%p%x00%s",
            f"{base}...{ref}",
            "--",
        ],
        root,
    )
    ours: list[tuple[str, str, str, bool]] = []
    theirs: Counter[str] = Counter()
    for line in output.splitlines():
        parts = line.split("\0")
        if len(parts) != 5:
            continue
        side, short, when, parents, subject = parts
        key = f"{when}\0{subject}"
        if side == ">":
            ours.append((key, short, subject, len(parents.split()) > 1))
        elif side == "<":
            theirs[key] += 1
    # `--reverse` on `--topo-order` puts ancestors first, so `ours[0]` is where
    # this side's divergence begins and is the one commit the rule turns on.
    if not ours or not theirs[ours[0][0]]:
        return None

    duplicated = 0
    own: list[tuple[str, str]] = []
    merges = False
    for key, short, subject, is_merge in ours:
        # Decremented rather than tested, so two commits on this side sharing a
        # date and a subject do not both match one commit on the base.
        if theirs[key]:
            theirs[key] -= 1
            duplicated += 1
            continue
        own.append((short, subject))
        merges = merges or is_merge
    return RewriteReport(duplicated=duplicated, own=tuple(own), merges=merges)


def fetch_remote(root: Path, *, runner: Runner | None = None) -> None:
    """Refresh the remote-tracking refs, or fail quietly having tried.

    The one read in this module that goes to the network, kept apart from the
    rest for exactly that reason: a caller that must not touch it simply does
    not call this. Every branch tip rather than `main` alone, and deliberately
    not `--prune` - a branch deleted on the remote leaves a tracking ref that
    is the only surviving copy of anything committed on it, which is the case
    `stranded` exists to catch.
    """
    run = runner or _run_git
    run(["fetch", "--quiet", "origin"], root)


def branch_state(root: Path, *, runner: Runner | None = None, fetched: bool = False) -> BranchState:
    """Where the working branch stands against the default branch.

    This was fifty lines of bash in the session-start hook, which is the only
    place it could run: at session start, once, on a condition that develops
    *during* a session. A session opened to discuss the next piece of work
    while another session finishes something is told its base is current, talks
    for a while, and starts implementing against a base that moved - and the
    staleness surfaces at push time as a merge conflict, which is the rework
    cycle the check exists to prevent.

    So the decision lives here, where a command can ask it again at any moment
    and a test can hold it to an answer. The hook keeps only the fetch.

    **It never fetches.** The rule the rest of this module follows - a read
    that must work from a bare checkout with no network - applies to the
    decision, so refreshing `origin/main` is the caller's, and `fetched` says
    whether the caller did it. What is reported is therefore stale by exactly
    one fetch at worst, which is an acceptable error for a report and would be
    an unacceptable one for a claim.

    **A silence outranks whatever the body concluded while git was quiet**
    (`PL-Q9Z1`). This declined under a total git failure before the channel
    existed, which looked like compliance and was not: it declined saying "no
    branch is checked out here", and no branch being checked out is a claim
    about the repository that nothing had established. A wrong reason on a
    correct refusal is still the floor breached, because a reader acts on the
    reason - here by looking for a branch that is in fact there.
    """
    run = _Silences(runner or _run_git)
    state = _branch_state(root, run, fetched=fetched)
    if run.reason:
        return replace(state, absent=True, declined=run.reason)
    return state


def _branch_state(root: Path, run: Runner, *, fetched: bool) -> BranchState:
    """`branch_state`'s reading, against a runner whose silences are watched."""
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    if not branch or branch == "HEAD":
        return BranchState(
            fetched=fetched,
            absent=True,
            declined="no branch is checked out here, so there is nothing to compare",
        )

    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return BranchState(
            branch=branch,
            fetched=fetched,
            absent=True,
            declined=f"this checkout has no {base} to compare against",
        )

    # The default branch with no remote copy of it: `default_base` fell all the
    # way back to the local branch, which is the one already checked out, and
    # comparing a ref with itself answers nothing. Distinct from being current,
    # because there is no other side to have moved.
    if base == branch:
        return BranchState(
            branch=branch,
            base=base,
            fetched=fetched,
            absent=True,
            declined=f"{branch} is the default branch and has no remote copy to compare with",
        )

    # A missing fork point is why the counts cannot be trusted on their own:
    # `rev-list --left-right --count` on refs sharing no history reports each
    # side's whole length instead of failing, and a count invented that way is
    # worse than no count at all.
    fork = run(["merge-base", "HEAD", base], root).strip()

    counts = run(["rev-list", "--left-right", "--count", f"{base}...HEAD"], root).split()
    if len(counts) != 2 or not all(part.isdigit() for part in counts):
        return BranchState(
            branch=branch,
            base=base,
            fetched=fetched,
            absent=True,
            declined="git would not count the two sides",
        )

    behind, ahead = int(counts[0]), int(counts[1])
    # Asked before the missing-fork-point guard rather than after it, because a
    # rewrite is the case that most needs an answer and the case least likely
    # to have a fork point: `filter-repo` and `filter-branch` rebuild every
    # commit, so the old history and the new one usually share nothing at all.
    # Measured 2026-09-06 against a `filter-branch --index-filter` rewrite of a
    # four-commit repository - no merge base, and `rev-list` reporting 5 and 5.
    # Proving the two sides are one duplicated history is what makes those
    # numbers mean something; without it this branch declined, and declined
    # with advice about `--depth` that does nothing to a rewritten clone.
    rewrite = _duplicated_history(base, root, run) if behind and ahead else None
    if not fork and rewrite is None:
        return BranchState(
            branch=branch,
            base=base,
            fetched=fetched,
            declined=(
                f"this clone shares no readable history with {base}, so its position "
                "cannot be counted - something ran a `--depth` fetch, and "
                "`git fetch --deepen=100 origin` restores the answer"
            ),
        )

    # Asked only where the counts would otherwise say `MERGE`, which is the one
    # arm whose advice this changes: behind, ahead, not the default branch, and
    # not a rewrite. `CURRENT`, `PULL`, `RESTART` and `REWRITTEN` pay nothing,
    # which matters because the session-start hook runs this every session and
    # the read costs three git calls.
    says_merge = bool(behind and ahead and rewrite is None and base.rsplit("/", 1)[-1] != branch)
    return BranchState(
        branch=branch,
        base=base,
        behind=behind,
        ahead=ahead,
        # Nothing "landed" across a rewrite with no fork point: every commit on
        # the base is then outside this history, and naming a release's worth
        # of ids would answer a question nobody asked.
        landed=_landed_since(fork, base, root, run) if behind and fork else (),
        landed_whole=says_merge and landed_whole(base, root, run),
        rewrite=rewrite,
        fetched=fetched,
    )


def is_shallow(root: Path, *, runner: Runner | None = None) -> bool | None:
    """Whether this checkout is truncated, or `None` when git will not say.

    Three answers rather than two, because the callers need the difference. A
    shallow clone is missing history and tags it can name; a git too old for
    `--is-shallow-repository`, a directory that is not a repository, or no git
    at all leaves the question open. Both forbid inferring anything from
    something's absence, and only the first can explain why.
    """
    run = runner or _run_git
    answer = run(["rev-parse", "--is-shallow-repository"], root).strip()
    if answer == "true":
        return True
    if answer == "false":
        return False
    return None


def in_tree(root: Path, path: str) -> bool:
    """Whether a declared `touches` path is in the working tree now, as a file or a directory.

    Read from the filesystem rather than from git, so it answers under
    `--no-git` and in a checkout with no history: the tree on disk is what a
    session is about to work against. `PL-8JY7` asks the same question of every
    open item's `touches` in `docket check`, and reuses this rather than
    spelling the test again.
    """
    return (root / path).exists()


@dataclass(frozen=True)
class TouchedPath:
    """One declared `touches` path, and what it has been through since its item was filed."""

    path: str
    #: In the working tree now, from `in_tree`.
    exists: bool
    #: Commits on or after the filing date that changed it, or `None` where the
    #: history was not read - never `0` for a question nobody asked.
    commits: int | None = None
    #: Gone from the tree, and one of those commits is what deleted it.
    deleted: bool = False


@dataclass(frozen=True)
class SinceFiled:
    """What an open item's declared paths went through after it was filed, or why that is unread.

    The facts half of re-confirming an old item before it is worked
    (`PL-TQN2`), and only the facts. Whether the problem the brief describes
    still exists is a reading of the brief against the tree, which is the start
    mode's judgment: a deleted file can take its problem with it or only move
    it, and 20-50% of self-admitted-debt removals turned out to be the comment
    leaving with its code rather than the debt being paid (Zampetti,
    Serebrenik and Di Penta, MSR 2018, doi:10.1145/3196398.3196423).

    A type rather than the tuple because `declined` has to travel with it: a
    count of zero and a count nobody read would otherwise print alike, and the
    first tells a session the code has not moved.
    """

    filed: date
    paths: tuple[TouchedPath, ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @classmethod
    def unread(cls, root: Path, touches: Sequence[str], filed: date, reason: str) -> SinceFiled:
        """What the tree alone answers - whether each path is there - and why git was not asked."""
        return cls(filed, tuple(TouchedPath(p, in_tree(root, p)) for p in touches), declined=reason)


def since_filed(
    root: Path, touches: Sequence[str], filed: date, *, runner: Runner | None = None
) -> SinceFiled:
    """How many commits on or after `filed` changed each declared path, in one `git log` read.

    Counted from `HEAD`, the tree the session is about to work in, and from
    the first instant of the filing date in UTC - the date `docket new` writes
    carries no time, so a commit made earlier on the filing day counts as
    after it. That errs towards "this has moved", which costs one look; the
    other way would hide a same-day change from the reader it exists for.

    Each flag is there for one misreading. `--no-merges` keeps a merge from
    counting the work it brought in a second time. `--no-renames` reports a
    renamed path as deleted under its old name, which is what it is to a brief
    that names the old one. `--literal-pathspecs` keeps a path from being read
    as a glob, so git and `in_tree` answer about the same path. `-z` returns
    each path as its bytes: without it git quotes a name it thinks unusual,
    `é.py` arriving as `"\\303\\251.py"` (measured 2026-09-23), which matches no
    declared path and would print "unchanged" over a file changed every day.

    **A shallow clone declines rather than counting**, for the reason
    `merged_pull_requests` gives: the commits it is missing are the oldest, and
    this read is about the oldest items. So would a git that cannot say whether
    the history is complete, and any question git did not answer.
    """
    if not touches:
        return SinceFiled(filed)
    run = _Silences(runner or _run_git)
    shallow = is_shallow(root, runner=run)
    if shallow is True:
        return SinceFiled.unread(
            root,
            touches,
            filed,
            "this clone is shallow, so the commits it is missing may be the ones since filing",
        )
    if shallow is None:
        return SinceFiled.unread(
            root, touches, filed, "git cannot say whether this checkout's history is complete"
        )
    text = run(
        [
            "--literal-pathspecs",
            "log",
            "--no-merges",
            "--no-renames",
            f"--since={filed.isoformat()} 00:00:00 +0000",
            "--format=%x1f%H",
            "-z",
            "--name-status",
            "HEAD",
            "--",
            *touches,
        ],
        root,
    )
    if run.unanswered:
        return SinceFiled.unread(root, touches, filed, run.reason)
    bare = {path: path.rstrip("/") for path in touches}
    counts: Counter[str] = Counter()
    deleted: set[str] = set()
    in_commit: set[str] = set()
    status = ""
    # NUL-separated: `\x1f<hash>`, then status and path in turn, the first
    # status carrying the newline that ended the commit's own line.
    for token in text.split("\0"):
        if token.startswith("\x1f"):
            # The commit before is complete. Counted once per commit, however
            # many files beneath one declared directory it changed.
            counts.update(in_commit)
            in_commit, status = set(), ""
        elif not status:
            status = token.lstrip("\n")
        else:
            for path, prefix in bare.items():
                if token == prefix or token.startswith(prefix + "/"):
                    in_commit.add(path)
                    if status == "D":
                        deleted.add(path)
            status = ""
    counts.update(in_commit)
    present = {path: in_tree(root, path) for path in touches}
    return SinceFiled(
        filed,
        tuple(
            TouchedPath(path, present[path], counts[path], path in deleted and not present[path])
            for path in touches
        ),
    )


@dataclass(frozen=True)
class BaseRelease:
    """What the default branch already records as shipped, or that it is unread.

    `known` carries the obligation every read in this module carries.
    `_run_git` answers a failure with the empty string, so a base this
    checkout cannot read and a base that has never cut a release arrive here
    identically - and reporting the first as the second would let a duplicate
    release through under a check that appeared to have run, which is the one
    thing a guard must never do.

    The version file is what decides it. A project being cut releases for has
    one; a ref that cannot produce it is a ref this checkout has no answer
    about, whether because there is no remote, no network since the clone, or
    no such branch. An empty `notes` under `known` is the other case and a
    real answer: the base holds no notes for anything.

    Read from the ref as it stands in this checkout, so it is stale by
    whatever the last fetch left behind. That is a floor on what the answer
    can prove, not a flaw in it: what it reports present is present.
    """

    base: str = ""
    #: The version the base's own version file declares, unparsed of its `v`.
    version: str = ""
    #: Notes file names as they sit in `notes_dir` on the base - `v0.3.7.md`,
    #: not the path to it, because the directory is the caller's own constant.
    notes: frozenset[str] = frozenset()
    known: bool = False


def released_on_base(
    root: Path,
    *,
    version_file: str,
    notes_dir: str,
    base: str | None = None,
    runner: Runner | None = None,
) -> BaseRelease:
    """Which releases the default branch already holds, read from the ref itself.

    Two reads of one ref rather than of the working tree, and that is the
    whole point: the working tree is this session's own release in progress,
    which would answer "yes, already cut" to its own work. The base is what
    everyone else has, so it is the only place a second copy of a release can
    be seen from.

    Costs two `git` calls and no network, so a caller that has just fetched
    gets a current answer and one that cannot fetch still gets a sound one -
    older, and never wrong about what it names.

    **`known` is withheld from a reading git left a hole in** (`PL-Q9Z1`). The
    notes listing is the half that matters: silenced, it gives an empty set,
    which is `known=True` saying the base has shipped nothing and is exactly the
    answer that lets a duplicate release through.
    """
    run = _Silences(runner or _run_git)
    ref = base or default_base(root, runner=run)

    declared = run(["show", f"{ref}:{version_file}"], root)
    if not declared.strip():
        return BaseRelease(base=ref)

    return BaseRelease(
        base=ref,
        version=version_in(declared),
        notes=_notes_on(ref, notes_dir, root, run),
        known=not run.unanswered,
    )


def _notes_on(ref: str, notes_dir: str, root: Path, run: Runner) -> frozenset[str]:
    """The notes file names a ref holds in `notes_dir` - `v0.3.7.md`, not the path to it.

    Shared by `released_on_base` and `claims.holdings`, whose cut holds leave
    out a version the base already holds, so that the two agree about which.
    """
    return frozenset(
        line.strip().rsplit("/", 1)[-1]
        for line in run(["ls-tree", "--name-only", ref, f"{notes_dir}/"], root).splitlines()
        if line.strip()
    )


@dataclass(frozen=True)
class BranchCut:
    """One ref carrying a release the default branch has not taken.

    `mine` is this checkout's own cut seen from outside - a local branch, its
    tracking ref, or a branch pushed under a third name - decided by whether
    `HEAD` contains the ref's tip rather than by comparing names, for the
    reason `Carrier.mine` gives: a session told to yield to itself would stop
    for nobody.

    `cut` dates the commit that wrote the notes, not the ref's tip, because
    the question a reader has is how old the *release* is. It separates a live
    session from a branch nobody will merge, and this reports it rather than
    deciding between them, the way `flight` and `stranded` do.

    A train holder, which `cli._with_train` builds, bends all three: with
    `item` set and `versions` empty it has cut nothing, `cut` is its claim's
    date, and `mine` is False because the train is decided by branch name,
    which has already excluded `HEAD`'s own. One whose branch this checkout
    merged keeps its cut's versions and date, and is not `mine` for the same
    reason.
    """

    ref: str
    #: Versions without their `v`, so they compare against a version string.
    versions: tuple[str, ...]
    cut: date | None = None
    mine: bool = False
    #: The release item whose claim holds the release train on this ref, for a
    #: holder that has filed and claimed its release but cut nothing yet: then
    #: `versions` is empty and this is the only evidence. Empty for a holder
    #: known only by its notes file, which is what `cuts_in_flight` reads.
    item: str = ""


@dataclass(frozen=True)
class CutsInFlight:
    """Which refs are cutting a release nobody has merged, or which could not be read.

    **The cut itself still carries no `PL-` id**: its commits stamp other
    items' `milestone:`, so `branches_in_flight` and everything reading it are
    blind to the widest write in the repository, and two sessions cut v0.3.7
    within an hour (`PL-66FP`). The evidence here is the notes file a ref
    introduces, which is the one artifact a cut cannot happen without. The id
    the release guard reads is the release item's instead: its claim holds the
    release train (`model.RELEASE_TRAIN`), which `claims.Holdings.holder`
    answers for, and `bin/docket release` and the digest add a train holder
    that has cut nothing yet to `branches` beside these (`PL-331V`).

    `unreadable` carries the obligation it carries everywhere else here: a ref
    whose history this checkout does not hold is named, never reported clean.
    """

    branches: tuple[BranchCut, ...] = ()
    unreadable: tuple[str, ...] = ()
    base: str = ""
    #: Why this reading is partial, in the sense `FlightReport.declined` carries
    #: it. It matters more here than in most: this guard is the one stopping two
    #: sessions cutting one release, and a silence read as "no cut in flight" is
    #: the answer that lets the second one through (`PL-66FP`, `PL-Q9Z1`).
    declined: str = ""

    @property
    def known(self) -> bool:
        """Whether git answered every question this reading rests on."""
        return not self.declined


@dataclass(frozen=True)
class CutWindow:
    """What the default branch took while this checkout's release cut sat unmerged.

    **The seam this exists to make visible.** `bin/docket release` stamps the
    finished work with `milestone: vX.Y.Z` and renders the notes from it; the
    tag then goes on the *merge* commit, per `ROADMAP.md` § "Tags". Anything
    that merges between those two moments is inside the tag's span and named in
    no release notes at all until the next release claims it, so two documents
    answer "what shipped in vX.Y.Z" differently and neither is wrong on its own
    terms (`PL-028F`).

    **It is not rare, and it is invisible afterwards.** Measured 2026-09-14
    across 47 tagged spans: 12 closing pull requests merged inside a tag's span
    while its own notes named them nowhere, in 11 distinct spans - close to one
    release in four. The window itself leaves no trace: a squash merge gives
    the release commit the same author and commit date, so nothing in `main`'s
    history records how long the branch was open. That is why the report is
    made here, while the cut is still unmerged and re-running it would absorb
    the newcomers, rather than reconciled later from a history that cannot say.

    `landed` is **subject-derived**, and the advisory that prints it says so.
    `_landed_since` reads leading ids off the base's new subjects, which names
    a commit's own item and not necessarily a *closure*. That is the right
    accuracy for something a person is asked to look at and would be the wrong
    accuracy for anything acting on its own - `PL-8M8H` is the case where the
    same read had to be refused for exactly that reason.
    """

    #: The version this checkout is cutting, without its `v`; empty when none.
    version: str = ""
    #: The ids leading subjects the base gained since the cut was written.
    landed: tuple[str, ...] = ()
    declined: str = ""


def cut_window(
    root: Path, *, notes_dir: str = NOTES_DIR, runner: Runner | None = None
) -> CutWindow:
    """Whether this checkout carries an unmerged cut, and what landed since.

    Reads only the checkout's own `HEAD`, unlike `cuts_in_flight` which walks
    every ref: the question here is what *this* session is about to merge and
    tag, which is the one release it can still do anything about.

    Args:
        root: Repository root.
        notes_dir: Where a cut writes its notes file.
        runner: The git runner; the module default when omitted.

    Returns:
        An empty window where this checkout is not cutting anything, which is
        every session but one. `declined` where git would not answer, because a
        silent empty answer here would read as "nothing landed in the window".
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return CutWindow(declined=f"this checkout has no {base} to compare against")
    prefix = notes_dir.strip("/") + "/"
    added = [
        line.strip()
        for line in run(
            ["diff", "--name-only", "--diff-filter=A", f"{base}...HEAD", "--", notes_dir], root
        ).splitlines()
        if line.strip().startswith(prefix)
    ]
    if not added:
        return CutWindow(declined=run.reason)
    versions = sorted({name[len(prefix) :].removesuffix(".md").lstrip("v") for name in added})
    fork = run(["merge-base", "HEAD", base], root).strip()
    if not fork:
        return CutWindow(
            version=versions[-1], declined=f"this clone shares no readable history with {base}"
        )
    return CutWindow(
        version=versions[-1], landed=_landed_since(fork, base, root, run), declined=run.reason
    )


def cuts_in_flight(
    root: Path,
    *,
    notes_dir: str,
    on_base: frozenset[str] = frozenset(),
    include_remote: bool = True,
    runner: Runner | None = None,
) -> CutsInFlight:
    """Every release being cut on a ref the default branch has not taken.

    **`on_base` is what makes the answer usable, and leaving it out breaks
    this.** A squash merge keeps none of the branch's commits, so a merged
    release branch stays "unlanded" by `_work_already_on_base`'s test whenever
    it carries anything else the base did not take - measured 2026-09-04, the
    branch whose v0.3.9 release had merged twenty minutes earlier was still
    listed. A three-dot diff then reports its notes file forever, and a guard
    that fires on every release after the first is one nobody reads. So a
    version the base already holds is not in flight, by definition, and the
    caller passes what the base holds.

    Read from refs, so it is stale by exactly one fetch and blind to a session
    that has pushed nothing. Both are floors on what it can prove rather than
    flaws in it: what it names, it names on evidence a second checkout would
    read identically.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)

    found: list[BranchCut] = []
    for name in refs.unlanded:
        versions = _cut_versions(name, base, notes_dir, on_base, root, run)
        if not versions:
            continue
        tip = run(["rev-parse", name], root).strip()
        found.append(
            BranchCut(
                ref=name,
                versions=versions,
                cut=_cut_date(name, notes_dir, versions[0], root, run),
                mine=bool(tip) and run(["merge-base", tip, "HEAD"], root).strip() == tip,
            )
        )

    return CutsInFlight(
        branches=tuple(sorted(found, key=lambda entry: entry.ref)),
        unreadable=tuple(sorted(refs.unreadable)),
        base=base,
        declined=run.reason,
    )


def _cut_versions(
    ref: str, base: str, notes_dir: str, on_base: frozenset[str], root: Path, run: Runner
) -> tuple[str, ...]:
    """The versions a ref is cutting: notes it changed since its fork that the base lacks.

    Without their `v`, sorted. Shared by `cuts_in_flight` and
    `claims.holdings`'s cut holds, so the two cannot disagree about what a
    ref is cutting.
    """
    return tuple(
        sorted(
            {
                version
                for line in run(
                    ["diff", "--name-only", f"{base}...{ref}", "--", f"{notes_dir}/"], root
                ).splitlines()
                if (leaf := line.strip().rsplit("/", 1)[-1])
                and leaf not in on_base
                and (version := leaf.removesuffix(".md").lstrip("v"))
            }
        )
    )


def _cut_date(ref: str, notes_dir: str, version: str, root: Path, run: Runner) -> date | None:
    """When the notes for a version were written on a ref, or `None` if unreadable."""
    stamp = run(
        ["log", "-1", "--format=%cI", ref, "--", f"{notes_dir}/v{version}.md"], root
    ).strip()
    try:
        return datetime.fromisoformat(stamp).astimezone(UTC).date()
    except ValueError:
        return None


@dataclass(frozen=True)
class TagSet:
    """Every tag the repository holds, or why that could not be read.

    `declined` for the reason `PullRequestHistory` carries one, and the tag
    read is where an empty set is least safe to guess from. `release.is_untagged`
    reads an answered emptiness as "this project does not tag" and holds the
    project to nothing - the right reading, and the one that made a silence
    free: a `git tag --list` that failed skipped the release gate outright,
    with nothing said, on the one check that exists because the gap it guards
    cannot be repaired afterwards (`PL-ZPDM`).

    The direction is what makes it worth a type. A silence read as "no tags"
    is not a wrong answer a caller can question - it is the right *shape* of
    answer carrying a fact the caller has no way to doubt.
    """

    names: frozenset[str] = frozenset()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def tags(root: Path, *, runner: Runner | None = None) -> TagSet:
    """Every tag name the repository holds, or why git could not say.

    Three answers rather than the two this used to give. `names` empty and
    `known` is a checkout with no tags; `declined` is git not answering at all -
    no repository, no git, a `tag --list` that failed. **A truncated clone is
    neither**: it answers with the tags reachable within its depth and silently
    omits the rest, so a caller reasoning from a tag's absence must still ask
    `is_shallow` first (`PL-J295`).

    What an *answered* emptiness means stays the caller's to decide:
    `release.is_untagged` reads it as "this project does not tag" rather than
    as "every release is untagged", because a tool that started refusing
    releases in a project that never tagged would be teaching a practice rather
    than holding one. That reading is only sound once a silence cannot reach
    it, which is what the type is for.
    """
    run = _Silences(runner or _run_git)
    names = frozenset(
        line.strip() for line in run(["tag", "--list"], root).splitlines() if line.strip()
    )
    return TagSet(names=names, declined=run.reason)


# A pull request number as it reaches the default branch. GitHub writes one of
# two subjects depending on how the merge was made: `Merge pull request #71
# from owner/branch` for a merge commit, and `Title (#71)` for a squash. Both
# are matched, because a repository that switches from one to the other keeps
# the history it already has.
PR_SUBJECT_RE = re.compile(r"^Merge pull request #(\d+)\b|\(#(\d+)\)\s*$")


@dataclass(frozen=True)
class PullRequestHistory:
    """Which pull requests the default branch names, or why that is not known.

    `declined` is the whole reason this is a type rather than a set. A caller
    handed an empty set cannot tell "this project does not use pull requests"
    from "this checkout cannot see them", and the two demand opposite
    behaviour: the first is a clean answer, the second must be reported as a
    check that did not run. Collapsing them is the failure this guards.
    """

    numbers: frozenset[int] = frozenset()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def merged_pull_requests(root: Path, *, runner: Runner | None = None) -> PullRequestHistory:
    """Every pull request number named by a commit on the default branch.

    A shallow clone is a worse condition than a bare one, and the difference is
    why this declines rather than returning what it found. In a bare checkout
    git cannot answer and every read here already collapses to silence; in a
    shallow clone git answers confidently and wrongly. The commits it is
    missing are exactly the oldest, so the provenance that has been settled
    longest is what would be reported as never having landed - and the
    container an agent session runs in is normally shallow, so that is the
    common case rather than the exotic one.

    So the only state that permits an answer is a repository that says outright
    it is not shallow. Truncation, no git, no repository, or a git too old to
    have `--is-shallow-repository` all decline, each with the reason, so the
    caller can report a check that did not run instead of one that passed.

    Deliberately no fetch. `docket check` runs from a bare tree with no
    network, and deepening the history here would trade that away to answer a
    question the caller is perfectly able to skip.
    """
    run = runner or _run_git
    shallow = is_shallow(root, runner=run)
    if shallow is True:
        return PullRequestHistory(
            declined="the checkout is a shallow clone, so the commits it is missing are "
            "the oldest ones and the longest-settled provenance would read as broken"
        )
    if shallow is None:
        return PullRequestHistory(declined="git cannot say whether this checkout is complete")
    subjects = run(["log", "--format=%s", default_base(root, runner=run)], root)
    if not subjects.strip():
        return PullRequestHistory(declined="no default branch this checkout can read")
    found: set[int] = set()
    for subject in subjects.splitlines():
        match = PR_SUBJECT_RE.search(subject.strip())
        if match is not None:
            found.add(int(match.group(1) or match.group(2)))
    return PullRequestHistory(numbers=frozenset(found))


@dataclass(frozen=True)
class FilingCommit:
    """The commit that added an item's file, where that commit also changed code.

    It records what the commit **did** and never what the item *is*. Everything
    here is read off one diff and one subject - the sha, the subject, the paths
    outside the queue - so every field is true by construction whenever this
    prints. That is the whole design constraint, and `PL-SWP3` is the
    measurement behind it: no key over this data can decide whether such a
    commit *finished* the item it filed, because that is a relation between the
    item's intent and the diff's content rather than a property of the diff.
    Three keys were counted and all three failed on it.
    """

    item_id: str
    commit: str
    subject: str
    paths: tuple[str, ...]

    @property
    def pull_request(self) -> int | None:
        """The pull request the filing commit arrived through, where the subject names one."""
        match = PR_SUBJECT_RE.search(self.subject.strip())
        return int(match.group(1) or match.group(2)) if match is not None else None


@dataclass(frozen=True)
class FilingReport:
    """Which items were filed by a commit that also changed code, or why that is unknown.

    `declined` for the same reason `PullRequestHistory` carries one: an empty
    mapping cannot tell "no item was filed this way" from "this checkout could
    not look", and a triage pass shown the first while the second is true is
    being handed a partial reading as a complete one.
    """

    filings: Mapping[str, FilingCommit] = field(default_factory=dict)
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def filed_with_work(
    item_ids: frozenset[str],
    root: Path,
    *,
    prefix: str = "docs/items/",
    runner: Runner | None = None,
) -> FilingReport:
    """Items whose own file was added by a commit that also changed something outside the queue.

    The shape `PL-3CBS`'s landed-work advisory cannot reach. That advisory is
    keyed on `verify:` and scoped to `ready` and `needs-decision`, so an item
    captured *and* worked in one commit never becomes a candidate for it: it
    never passes through `ready`, so it never acquires a command. `#635` landed
    385 lines of this file while filing `PL-0J9K` and `PL-MMVF`, and both were
    still `untriaged` on the default branch days later, offered to the project
    owner as live work.

    **It reports rather than concludes, and that is the finding rather than a
    caution.** `PL-SWP3` measured three keys over this store. The bare shape -
    an open item whose file was added beside any code change - matches 248 of
    319 open items and 10 of the 11 rows a triage pass actually reads, because
    filing findings alongside unrelated work is the shape `CLAUDE.md` asks for.
    Adding the subject test cuts that to 6, and none of the 6 is an item that
    should have closed: sessions lead a subject with the ids they *captured* as
    readily as the ids they *worked*. Replayed over history it fires 22 times at
    27% precision, and the script scoring it misjudges in both directions -
    scoring the two genuine instances false and two captured follow-ups true.

    So the subject test is kept for what it does do, which is suppress the 78%,
    and nothing is claimed from it. What prints is the commit and the paths, for
    a reader who is about to decide the item's fate and can open them.

    **The subject test uses `leading_ids`** rather than any id in the subject:
    the run a subject opens with is this project's declared grammar, and
    `PL-SVRW` is the standing item about not spelling it a second time. It also
    makes a slug rename harmless - `git mv` shows here as an add, but a rename
    pass leads its subject with its own housekeeping id, not with the ids of the
    files it moved.

    **Cost is one `git log` for the whole store, plus one `git show` per item
    that survives the subject test** - typically none. The subject arrives with
    the log, so the expensive call is made only where the annotation will print.
    """
    run = _Silences(runner or _run_git)
    if not item_ids:
        return FilingReport()
    shallow = is_shallow(root, runner=run)
    if shallow is True:
        return FilingReport(
            declined="the checkout is a shallow clone, so an item filed before its horizon "
            "would read as filed by nobody"
        )
    if shallow is None:
        return FilingReport(declined="git cannot say whether this checkout is complete")
    log = run(
        [
            "log",
            default_base(root, runner=run),
            "--diff-filter=A",
            "--format=%x00%H%x01%s",
            "--name-status",
            "--",
            prefix,
        ],
        root,
    )
    if not log.strip():
        return FilingReport(
            declined="no default branch this checkout can read, so nothing says which "
            "commit filed an item"
        )

    # Newest add wins: a file added, removed and restored is carried by the
    # commit that put the copy being read there, which is the one a reader
    # opening it would find.
    filed: dict[str, tuple[str, str]] = {}
    commit = subject = ""
    for line in log.splitlines():
        if line.startswith("\x00"):
            commit, _, subject = line[1:].partition("\x01")
            continue
        if not commit or not line.strip() or not line.split("\t")[0].startswith("A"):
            continue
        for item_id, _path in _item_files([line.split("\t")[-1]], prefix):
            filed.setdefault(item_id, (commit, subject))

    found: dict[str, FilingCommit] = {}
    for item_id in sorted(item_ids):
        entry = filed.get(item_id)
        if entry is None or item_id not in leading_ids(entry[1]):
            continue
        commit, subject = entry
        changed = run(["show", "--format=", "--name-only", commit], root).split()
        outside = tuple(path for path in changed if not path.startswith(prefix))
        if outside:
            found[item_id] = FilingCommit(
                item_id=item_id, commit=commit, subject=subject, paths=outside
            )
    return FilingReport(filings=found, declined=run.reason)


@dataclass(frozen=True)
class ClosureReport:
    """Which item closures already stand on the default base, or why that is unknown.

    Reading *whether* a closure landed is deliberately not gated on
    `is_shallow`, unlike `merged_pull_requests`. That reader needs history,
    which a shallow clone answers confidently and wrongly; this one needs a
    single tree read, which `git show <ref>:<path>` answers correctly however
    truncated the history behind the ref is. The distinction earns its own
    type: a shallow clone is the normal state of an agent session, so a reader
    that declined there would decline in exactly the case this exists to cover.

    Reading *which pull request* landed it is the other kind of question, and
    `shallow` is what qualifies the *absence* of a number here. At
    `fetch-depth: 1` there is one commit to search, so every closure but the
    newest yields nothing, and a caller that read that as "no commit names a
    number" would call correct provenance lost. It did: `main` was red on
    97573ae and 3b37a75 for a `pr` recoverable from a commit the clone no
    longer held (`PL-99Y4`). So the emptiness is reported with the depth that
    produced it, and the caller decides - the rule `PL-J295` already set for
    `tags`, applied to the question beside it.

    A number that *is* derived was once held to be trustworthy at any depth, on
    the reasoning that the commit was found and finding it is proof enough. It
    is not, and `shallow` was never what would have caught it: what a truncated
    history breaks is the parent comparison that tells a closure from every
    later commit touching the same file, and `_closed_at` now refuses that
    question rather than answering it. Until it did, `record` wrote `#401` onto
    five items on a `--depth 1` clone and four of them had merged in `#399`,
    `#400` and `#402` (`PL-KX9N`). So a derived number means the parent was
    there to compare against, at whatever depth.
    """

    base: str = ""
    landed: frozenset[str] = frozenset()
    #: The pull request each landed closure's own merge commit names, where
    #: the base still holds that commit. Pairs rather than a mapping to keep
    #: the type hashable like everything else here; `numbers` unpacks it.
    derived: tuple[tuple[str, int], ...] = ()
    #: Whether the history behind `base` is truncated, or `None` where git
    #: will not say - straight from `is_shallow`, and read only to qualify
    #: what a *missing* `derived` entry is allowed to mean. Defaults to `None`
    #: so that a report built without it claims nothing.
    shallow: bool | None = None
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def numbers(self) -> dict[str, int]:
        return dict(self.derived)


def closures_on_base(
    root: Path,
    closures: Mapping[str, str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> ClosureReport:
    """Which of `closures` already read `status: done` on the default base.

    `closures` maps an item id to the file name that holds it, and is expected
    to carry only the items whose closure is in question: each one costs a
    `git show`, and the caller is the one that knows which those are.

    An item absent from the base is a closure that has not landed, which is
    the whole point rather than a failure to read it. So is one whose file is
    there under another name, because retitling an item renames its file and
    the old path stops resolving. Both are accepted rather than reported, which
    is the safe direction: this rule's failure mode is blocking a closure that
    is already correct.

    Each landed closure is also asked which pull request its own merge commit
    names, which is the question that decides whether a missing `pr` is a gap
    or a transcription still owed. It costs one history read for the whole
    set, made only when something landed, and it reuses the two parsers that
    already exist: the subject a squash merge writes carries the item ids it
    opens with and the number in trailing parentheses.

    Deriving nothing is a normal answer, not a failure, and `shallow` is
    recorded alongside so the caller can tell which kind of nothing it is. A
    complete history that names no number means none exists; a truncated one
    means the commit may simply be outside it, which at `fetch-depth: 1` is
    true of every closure but the newest.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return ClosureReport(declined="no default branch this checkout can read")
    landed: set[str] = set()
    for identifier, name in closures.items():
        text = run(["show", f"{base}:{items_dir}/{name}"], root)
        if text and parse_item(text, name).status == "done":
            landed.add(identifier)
    return ClosureReport(
        declined=run.reason,
        base=base,
        landed=frozenset(landed),
        derived=_merges_naming(landed, closures, items_dir, base, root, run),
        shallow=is_shallow(root, runner=run),
    )


def _merges_naming(
    identifiers: set[str],
    closures: Mapping[str, str],
    items_dir: str,
    base: str,
    root: Path,
    run: Runner,
) -> tuple[tuple[str, int], ...]:
    """The pull request number each id's closure on `base` can be traced to.

    Two readings, tried in that order. The subject scan is first because it is
    one history read for the whole set: one commit can close two items - a
    subject may open with a run of ids - so a single merge answers for several,
    and each is recorded against the same number. Only the newest such commit
    counts: an id that led an earlier subject too, most often the capture that
    filed it, was not the merge that landed its work.

    **Recency is not enough, and the scan's answer is confirmed before it is
    believed.** Leading a subject proves the commit is *about* the item, never
    that it *closed* it, and several kinds of commit are about a closed item:
    the bookkeeping merge that writes its `pr` back, a follow-up fix, a triage
    that filed it. Measured 2026-09-04 over the 122 closed items on `main` that
    a leading-id subject names, the unconfirmed scan answered 21 of them with a
    number that is not their closure - `PL-1TF4` and `PL-J49T` with `250`, whose
    subject reads "record #249"; `PL-B0YN` and `PL-G1MF` with `188` from "record
    their pull request" against a true `186`; `PL-YLZQ` with `159`, the commit
    that triaged it, against a true `204` (`PL-GW37`). The rider closure this
    was raised for is one shape of that, not the whole of it.

    So each answer is put to the test `_number_closing` already uses on the
    file: the commit must read `status: done` in its own tree and not in its
    parent's. That is what distinguishes the closure from every other commit
    naming the item, it costs two `git show` for each id the scan answered, and
    it is asked only of items whose `pr` is missing - a handful, not the store.
    Over the same 122 it agreed with the file reading in every case where both
    could answer, and disagreed in none.

    A checkout that does not hold the parent cannot run that test at all, and
    `_closed_at` says so rather than answering. An unconfirmable candidate
    falls through to the file reading below exactly as an unanswered one does,
    and declines again there - which is the point, because the file reading is
    the half that stamped one number across four items (`PL-KX9N`).

    Whatever the subjects do not answer - or answer unconfirmably - falls back
    to the item's own file, per `PL-2XTF`. A squash merge takes its subject from
    the pull request title, which is written by whoever opened it and need not
    lead with any id - `#220` was created from the Claude Code UI, closed three
    items, and left `main` red with an error no recovery could clear, because
    the one subject that landed named none of them. The file always knows: the
    commit that wrote `status: done` into it *is* the closure, and it carries
    `(#N)` like every other squash. That is strictly more evidence than the
    subject scan, not less, and it costs a read only for the ids the cheap pass
    missed.

    That fallback had a defect of its own when this was written, and routing
    more ids into it is what made the defect worth fixing: it walked `git log --
    <path>` without rename detection, so for an item whose file was renamed
    after it closed, the oldest commit the walk could see was the rename, whose
    parent does not hold that path at all. `_walk_following_renames` is the
    repair (`PL-S5LB`).
    """
    if not identifiers:
        return ()
    found: dict[str, int] = {}
    candidates: dict[str, tuple[str, int]] = {}
    for line in run(["log", "--format=%H%x1f%s", base], root).splitlines():
        revision, _, subject = line.partition("\x1f")
        subject = subject.strip()
        match = PR_SUBJECT_RE.search(subject)
        if match is None:
            continue
        number = int(match.group(1) or match.group(2))
        for identifier in leading_ids(subject):
            if identifier in identifiers:
                candidates.setdefault(identifier, (revision.strip(), number))
    for identifier, (revision, number) in candidates.items():
        path = f"{items_dir}/{closures[identifier]}"
        if _closed_at(revision, path, path, root, run):
            found[identifier] = number
    for identifier in sorted(identifiers - set(found)):
        recovered = _number_closing(closures[identifier], items_dir, base, root, run)
        if recovered is not None:
            found[identifier] = recovered
    return tuple(sorted(found.items()))


def _number_closing(name: str, items_dir: str, base: str, root: Path, run: Runner) -> int | None:
    """The number on the commit that wrote `status: done` into one item's file.

    Walks the commits on `base` that touched the file, newest first, and takes
    the first one that closed it - `done` in that commit's tree and not in its
    parent's. The parent comparison is what keeps a *later* edit from being
    read as the closure: backfilling a `pr` field, or correcting a brief, both
    touch the file long after the work landed and both carry their own `(#N)`.
    Answering with one of those would record a false provenance, which is worse
    than the missing one this exists to supply.

    The walk follows renames and reads each commit at the name the file carried
    there, per `_walk_following_renames`. Without that, a rename *is* the shape
    this test looks for - the new name is done in the renaming commit's tree and
    absent from its parent's - so an item whose title was edited after it closed
    was attributed to whichever pull request happened to rename it, and one
    whose renaming commit named no number was declined instead (`PL-S5LB`).

    A commit whose parent this checkout does not hold ends the walk with no
    answer, per `_closed_at`. That reasoning used to run the other way: a
    failed `git show` collapses to "not done there", which was called the safe
    direction because it could only make the walk accept an older commit than
    it should have. It is not safe. At a graft boundary git reports every file
    in the tree as added, so the oldest commit held reads as "done here and not
    in the parent" for every closed item there is, and its number is stamped
    across all of them - `#401` onto five items on a `--depth 1` clone of this
    repository, four of which had merged in `#399`, `#400` and `#402`
    (`PL-KX9N`). Nothing older than that commit is in the walk either, so
    stopping loses nothing that a deeper fetch would not restore.
    """
    path = f"{items_dir}/{name}"
    for revision, subject, here, there in _walk_following_renames(path, base, root, run):
        match = PR_SUBJECT_RE.search(subject.strip())
        if match is None:
            continue
        closed = _closed_at(revision, here, there, root, run)
        if closed is None:  # its parent is outside this checkout, and so is everything older
            return None
        if closed:
            # **A closure that landed without its work names the wrong pull
            # request, so it names none** (`PL-YDL6`). This walk finds the commit
            # that wrote `status: done`; where the work and the closure landed in
            # different pull requests, that commit carries the closure and none
            # of the code, and `pr:` would record a change whose diff does not
            # contain the work the item describes. `commit:` was retired
            # (`PL-T63T`), so `pr` is the only surviving link to the work and a
            # wrong one is worse than an absent one.
            #
            # A closure commit that carries its work touches something outside
            # the queue, so `_annotates_only` separates the two - the same rule
            # that tells recording an item from working on it everywhere else in
            # this module. Declining is the answer rather than a guess at which
            # pull request held the work: nothing here knows which files an
            # item's work was, and `PL-99Y4` already settled that a provenance
            # question the checkout cannot answer is reported rather than
            # invented.
            #
            # Audited over real history while fixing `PL-S5LB`: 249 of the 252
            # closures this can answer agree with what the store recorded, and
            # all three that disagree are this shape, each off by one. The store
            # already holds the better answer in every case, so declining loses
            # nothing that was ever right. All three predate the same-commit
            # closure rule (`PL-D2GW`, then `PL-P5S0`), which is what keeps the
            # shape rare rather than impossible.
            #
            # **The diff is not the test for an item whose work *is* the
            # queue** (`PL-YFXG`). A commit changing nothing outside
            # `docs/items/` is a closure separated from its work only where the
            # work was somewhere else to begin with; for a release-tag item, a
            # triage pass, a stranded recovery or a rename pass it is what
            # landing correctly looks like, and that is a standing category here
            # rather than an accident. `_carried_work` therefore falls back to
            # the item's own `touches`, the same field `branches_in_flight`
            # already reads to draw the same distinction (`PL-7790`). `PL-YTDN`
            # is the worked example: its whole deliverable was renaming drifted
            # item files, so `#712` changed 12 files and every one was an item,
            # the number was declined, and `origin/main` was left failing
            # `docket check` with an error no command could clear - the bare
            # `record` writes only what the base can supply, and this was a
            # number it decided it could not.
            if not _carried_work(revision, here, items_dir, root, run):
                return None
            return int(match.group(1) or match.group(2))
    return None


def _carried_work(revision: str, item_path: str, items_dir: str, root: Path, run: Runner) -> bool:
    """Whether `revision`'s diff holds the work of the item it closed there.

    Two readings, and the second is the whole of `PL-YFXG`. A diff reaching
    outside the queue carried work, whatever the item says. A diff wholly
    inside the queue carried work only where the item's own `touches` says the
    queue is where its work lives - so the `PL-YDL6` hazard stays refused for
    every item declaring work outside it, which is the set that hazard was
    measured on, and the standing category of items whose deliverable is a
    queue edit stops being unanswerable by construction.

    `git diff` against the first parent rather than a bare `diff-tree`, for the
    reason `closed_by` gives beside the same call: a true merge commit shows an
    empty `diff-tree` by default and would read as touching nothing.

    Silence reads as "no work", so a commit this checkout cannot diff declines
    the number rather than supplying it, and no declaration rescues it: an
    unreadable diff is not evidence that the work was a queue edit. That is the
    direction the caller wants: an absent `pr` is a transcription still owed and
    a wrong one is a false provenance that nothing else will catch.
    """
    listing = run(["diff", "--name-only", f"{revision}^", revision], root)
    paths = [line.strip() for line in listing.splitlines() if line.strip()]
    if not paths:
        return False
    if not _annotates_only(paths, items_dir.strip("/") + "/"):
        return True
    return _declares_queue_only(revision, item_path, items_dir, root, run)


def _declares_queue_only(
    revision: str, item_path: str, items_dir: str, root: Path, run: Runner
) -> bool:
    """Whether the item at `item_path` declared, in `revision`'s tree, work wholly in the queue.

    **Read from the closure commit, where `_queue_only_work` reads the same
    field from the base, and the difference is what each is asking.** That one
    asks whether an *unmerged* branch is working a queue-only item, so the base
    is the one tree that cannot be carrying the session's own answer. Here the
    commit is already on the base, and the question is what the item declared
    when its closure landed - a `touches` repaired afterwards would otherwise
    change the recorded provenance of a merge that is already history, and
    repairing one is ordinary work here rather than a hypothetical: it was
    `PL-YTDN`'s own deliverable. The name to read comes from the walk, so an
    item renamed since costs no lookup of its own.

    Its silence declines, like every other read in this module: an item file
    this checkout cannot show has declared nothing.
    """
    text = run(["show", f"{revision}:{item_path}"], root)
    return bool(text) and _queue_only_touches(text, _basename(item_path), items_dir)


def _basename(path: str) -> str:
    """The file name in a path the walk carries, for `parse_item` to record."""
    return path.rsplit("/", 1)[-1]


def _walk_following_renames(
    path: str, base: str, root: Path, run: Runner
) -> tuple[tuple[str, str, str, str], ...]:
    """Every commit on `base` that touched one item's file, newest first.

    Four fields each: the revision, its subject, the name the file carried in
    that commit's tree, and the name it carried in its parent's. Those last two
    differ exactly where the commit renamed the file - which is an ordinary
    event rather than a rare one, because `docket` names a file from a slug of
    its title, so editing a title renames it and `bin/docket release` renames
    every item whose title has drifted since the last release.

    **Rename detection is half the fix, and on its own it is the half that does
    nothing.** `--follow` reaches past the rename, but each commit it returns
    still has to be *read* at the name the file had there. Asking `git show
    <rev>:<the name it has today>` of a commit older than the rename fails,
    `_run_git` answers a failed `show` with empty output, and the closure behind
    the rename therefore reads as "not done" - leaving the renaming commit still
    looking like the one that closed the item. Measured against this repository
    on 2026-09-06: `--follow` alone still answered `PL-3D2M` with `319`, the
    pull request that renamed the file in passing, against a true `313`.

    So the names come from `--name-status`, whose rename entry carries both of
    them. `-z` is what makes that parseable - every field NUL-terminated, which
    leaves the `--format` output's own newline at the front of the status token
    following it, and keeps a path containing a tab or a newline in one piece.

    A commit listed without a name-status entry - a merge, which git shows with
    no diff - keeps the name carried back from the newer side of the walk, which
    is what the file was called there.
    """
    fields = run(
        ["log", "--format=%H%x1f%s", "-z", "--name-status", "-M", "--follow", base, "--", path],
        root,
    ).split("\0")
    commits: list[tuple[str, str, str, str]] = []
    revision = subject = ""
    entry: list[str] = []
    carried = path
    for token in (*fields, "\x1f"):
        if token.startswith("\n"):
            entry = [token.lstrip("\n")]
        elif "\x1f" in token:
            if revision:
                here = there = carried
                if len(entry) > 2 and entry[0].startswith("R"):
                    there, here = entry[1], entry[2]
                elif len(entry) > 1:
                    here = there = entry[1]
                commits.append((revision, subject, here, there))
                carried = there
            revision, _, subject = token.partition("\x1f")
            entry = []
        elif token:
            entry.append(token)
    return tuple(commits)


def _done_at(revision: str, path: str, name: str, root: Path, run: Runner) -> bool:
    """Whether the item at `path` reads `status: done` in that revision's tree."""
    text = run(["show", f"{revision}:{path}"], root)
    return bool(text) and parse_item(text, name).status == "done"


def _parent_in_reach(revision: str, root: Path, run: Runner) -> bool:
    """Whether this checkout holds the parent `revision` would be compared against.

    False for a true root commit and for the graft boundary of a shallow clone
    alike, which is right: neither has a parent tree here to be read, and the
    callers' question is answerable only against one.
    """
    return bool(run(["rev-parse", "--verify", "--quiet", f"{revision}^^{{commit}}"], root).strip())


def _closed_at(revision: str, here: str, there: str, root: Path, run: Runner) -> bool | None:
    """Whether `revision` is the commit that closed one item, or `None` if unanswerable.

    The test both readings above apply: the item reads `status: done` in this
    commit's tree and not in its parent's. `here` and `there` are the names the
    file carried in each, which differ exactly where the commit renamed it.

    Three answers rather than two, for the reason `is_shallow` has three. The
    parent is the whole of what separates the closure from every later commit
    that touches a closed item - a `pr` written back, a retitle, a follow-up
    fix - so a checkout that does not hold it cannot make the comparison at
    all. Saying so costs one `rev-parse`; the alternative is not `False` but a
    confident wrong answer, because `_run_git` collapses a failed `git show`
    into "not done there". At a graft boundary git reports every file in the
    tree as added, so that collapse made the oldest commit held look like the
    closure of every closed item in the store, and `record` wrote its number
    onto all of them - `#401` onto five items on a `--depth 1` clone, four of
    which had merged in `#399`, `#400` and `#402` (`PL-KX9N`).

    `closed_by` has refused exactly this since it was written, asking the same
    question of one commit rather than of one file. These two readings never
    got the guard, which is the whole of that defect.
    """
    if not _done_at(revision, here, _basename(here), root, run):
        return False
    if not _parent_in_reach(revision, root, run):
        return None
    return not _done_at(f"{revision}^", there, _basename(there), root, run)


@dataclass(frozen=True)
class StrandedItem:
    """An item that exists on a branch and nowhere the store can see."""

    identifier: str
    title: str
    path: str
    branches: tuple[str, ...]


@dataclass(frozen=True)
class StrandedEdit:
    """An item the default branch holds, whose branch copy carries more than it.

    Kept apart from `StrandedItem` rather than folded in with it, because the
    two findings take opposite recoveries and the recipe for one destroys the
    other. Nothing on the base is overwritten by restoring a file the base
    does not have, so a stranded item is handed a `git checkout`; the base
    does hold this one, so what this is handed is a diff to read (`PL-KSCW`,
    `PL-MBTZ`). Folding them together would also change what the session-start
    digest's stranded line means, which is a claim about items that exist
    nowhere else and says `to recover`.

    `base_path` is carried beside `path` because a retitle renames an item's
    file, so the two sides of the comparison can sit at different paths and
    the diff has to name both.
    """

    identifier: str
    title: str
    path: str
    base_path: str
    branches: tuple[str, ...]


@dataclass(frozen=True)
class StrandedReport:
    """What is only on a branch, and how much of the repository was read.

    `refs_read` is part of the answer rather than diagnostics. The check can
    only see refs this checkout holds, and a container that cloned one branch
    holds two - so "nothing stranded" from a checkout that read two refs and
    the same words from one that read twenty are different claims, and the
    count is what tells them apart.

    `declined` carries the same meaning it does for `PullRequestHistory`: a
    check that could not run, reported as such rather than as a clean result.

    `fetched` is how old the *comparison point* is, and it is part of the
    answer for the same reason `refs_read` is. Every finding here rests on the
    default branch not holding the item, so a base nobody refreshed reports
    whatever merged since the last fetch as lost. That is not hypothetical:
    `PL-XLQ5` merged at 01:13 on 2026-09-05, this checkout's `origin/main` was
    from 01:05, and at 01:16 the item read as stranded and the recovery command
    restored its pre-triage copy over the triaged one the merge had just landed
    (`PL-KBFN`). The deleted remote branch corroborated nothing - a merge
    deletes the branch too - so freshness is the whole of what separates a hole
    from a merge.

    It records that the caller *attempted* a refresh, not that one arrived, and
    for `BranchState`'s reason: a quiet `git fetch` prints nothing whether it
    reached the remote or not. So it is reported only in the negative - nothing
    tried - which is the claim that can be made.
    """

    items: tuple[StrandedItem, ...] = ()
    #: Items the base holds whose copy on some ref is ahead of it. A second
    #: field rather than more `items`, for the reason `StrandedEdit` gives:
    #: every reader of `items` is told the base does not have them.
    edits: tuple[StrandedEdit, ...] = ()
    #: The ref every finding here is a claim against. Carried rather than
    #: recomputed by the reader, because the diff `edits` is read with names
    #: both sides and a second guess at the default branch is a second answer.
    base: str = ""
    refs_read: int = 0
    declined: str = ""
    fetched: bool = False

    @property
    def known(self) -> bool:
        return not self.declined


def _item_blobs(ref: str, root: Path, items_dir: str, run: Runner) -> dict[str, tuple[str, str]]:
    """Every item id the ref's tree holds, mapped to its blob and the path holding it.

    `ls-tree` reads one tree and needs no history behind it, which is what
    makes this work in the shallow clone an agent session starts from. Every
    commit-graph answer - is this branch merged, how far ahead is it - is
    unreliable there, because the commits that would prove containment are
    exactly the ones a shallow clone is missing.

    **The blob comes off the same read as the path.** "Does this ref hold the
    item" and "does it hold the same copy of it" are asked of one tree by one
    caller, and `ls-tree` answers both in a line. Opening the files to compare
    them instead costs a `git show` per item per ref, and the comparison is
    settled without opening anything for almost all of them: 24,829 of the
    27,009 ref-and-item pairs this repository held on 2026-09-21 carry the
    same blob on the branch and on the default branch.

    The long form rather than `--name-only`, so the object id is in the line:
    `<mode> <type> <object>\t<path>`, with everything after the first tab
    taken as the path because a path may contain one and git quotes what it
    cannot print.
    """
    found: dict[str, tuple[str, str]] = {}
    for line in run(["ls-tree", "-r", ref, "--", items_dir], root).splitlines():
        head, _, path = line.partition("\t")
        fields = head.split()
        path = path.strip()
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1]) if path and len(fields) == 3 else None
        if match is not None:
            found.setdefault(match.group(1), (fields[2], path))
    return found


def _items_at(ref: str, root: Path, items_dir: str, run: Runner) -> dict[str, str]:
    """Every item id the ref's tree holds, mapped to the file that holds it.

    The path half of `_item_blobs`, for readers whose question is only whether
    the item is there at all. One spelling of the `ls-tree` rather than two,
    because two spellings of one question are two answers waiting to disagree.
    """
    return {
        identifier: path
        for identifier, (_blob, path) in _item_blobs(ref, root, items_dir, run).items()
    }


#: What one ref's copy of an item file holds that the default branch's copy
#: does not. Three values rather than a boolean because the two mistakes they
#: separate are opposite in cost: a copy wrongly called `_AHEAD` costs a
#: reader one diff, and a copy wrongly called `_BEHIND` is a finding nobody
#: receives - or, where `orphaned` prints a `git checkout` for it, a newer
#: copy overwritten by an older one.
_AHEAD = "ahead"
_BEHIND = "behind"
_EQUAL = "equal"


def _standing(base_text: str, ref_text: str) -> str:
    """Whether a ref's copy of one item carries anything the base's copy does not.

    `stranded` used to key on whether an item's *id* was on the default
    branch, which answers a narrower question than the one it is asked. An
    item the base holds can still have its substance on a branch - a whole
    section of `PL-879R`'s brief sat unreported that way (`PL-KSCW`) - and a
    branch's copy can be an earlier revision of one the base has closed since,
    which is the case `orphaned` offered a `git checkout` for, restoring an
    `untriaged` copy over `main`'s `done` one (`PL-MBTZ`, and `PL-XLQ5` before
    it). One per-file predicate answers both (`PL-BHVM`, project owner,
    2026-09-19, ratified).

    **Content only.** No date, no commit count and no ancestry: this runs
    against refs a shallow clone holds no history for, and `closed:` is a
    field a branch can be holding a stale answer to rather than evidence about
    which copy is later.

    The three cases:

    - **`_EQUAL`.** The two copies agree.
    - **`_BEHIND` by removal.** The ref's copy spells no field differently and
      no line of prose the base's copy lacks, so the base holds everything it
      holds and more. This is `_superseded`'s "removals only" read, asked of
      one item file rather than of a path set.
    - **`_BEHIND` by closure.** The base's copy is `done` or `dropped` and the
      ref's is not; the ref's prose adds nothing; and every field it spells
      differently is one the base spells too. A field has one value, and on a
      closed item the base's is the one the project settled on - `status:
      untriaged` against `status: done`, with `closed:`, `pr:` and `verify:`
      beside it - so the branch's line is not content the base is missing.
    - **`_AHEAD` otherwise.** Including two copies that each hold something
      the other lacks: the reader is handed a diff either way, and calling
      that case ahead reports it rather than hiding it.

    **What the closure case costs, counted rather than asserted.** It is wrong
    exactly where a branch *reopens* an item the base closed, and a reopening
    is 2 of the 1,377 items in this store's history, both in one commit -
    measured 2026-09-21 by replaying every one of the 889 commits touching
    `docs/items/` on `main` and reading each item's `status` as it changed.
    Against that: on 2026-09-21 the rule was what separated 7 branch copies
    carrying real unmerged prose - among them a ratified project-owner
    decision on `PL-DMDF` that reached no other report - from 7 that carried
    nothing but an older `status:` line. Without it the report is 14 entries
    of which half are noise, which is the shape a reader learns to skim.
    """
    if base_text == ref_text:
        return _EQUAL
    base_fields, base_body = parse_front_matter(base_text)
    ref_fields, ref_body = parse_front_matter(ref_text)
    held = set(base_body.splitlines())
    if any(line.strip() and line not in held for line in ref_body.splitlines()):
        return _AHEAD
    differing = [key for key, value in ref_fields.items() if base_fields.get(key) != value]
    if not differing:
        return _BEHIND
    closed_on_base = base_fields.get("status", "") in CLOSED_STATUSES
    closed_on_ref = ref_fields.get("status", "") in CLOSED_STATUSES
    if closed_on_base and not closed_on_ref and all(key in base_fields for key in differing):
        return _BEHIND
    return _AHEAD


def _behind_on_base(
    ref: str, base: str, paths: tuple[str, ...], root: Path, items_dir: str, run: Runner
) -> set[str]:
    """Of `paths`, the item files whose copy on `ref` is behind the base's.

    The narrowing `_superseded` cannot make. That read is a two-dot diff, so a
    path the base has moved on from reads as outstanding the moment the ref's
    older copy spells one field differently: `status: untriaged` against
    `status: done` *adds* a line, and "anything added" is the outstanding arm
    of its rule. That is how `orphaned` came to print a `git checkout` of
    `origin/claude/next-version-release-o2zzaf`'s copy of `PL-THPB` - a
    recovery that replaces a `done` item with an `untriaged` one and discards
    the `closed:`, `milestone:` and `pr:` the base recorded on it (`PL-MBTZ`,
    and `PL-XLQ5` before it, whose cost `PL-KBFN` and `PL-39B7` record).

    Only item files, and only for `orphaned`. `_superseded` stays generic and
    content-only, because nothing else it is asked about is a document whose
    front matter this store owns; `landed_whole` keeps the narrower reading it
    was measured with, since the recovery *it* leads to deletes a ref.

    A silence leaves the path outstanding, which is `_superseded`'s direction
    and for its reason: a comparison nobody could read must not come back as
    "the base already has it".
    """
    behind: set[str] = set()
    on_base = _item_blobs(base, root, items_dir, run)
    for path in paths:
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
        recorded = on_base.get(match.group(1)) if match is not None else None
        if recorded is None:
            continue
        base_text = run(["show", f"{base}:{recorded[1]}"], root)
        ref_text = run(["show", f"{ref}:{path}"], root)
        if base_text and ref_text and _standing(base_text, ref_text) == _BEHIND:
            behind.add(path)
    return behind


@dataclass(frozen=True)
class BaseRecord:
    """What the default base's copy of one closed item records about the work landing.

    `verify` is what proved it, and `closed` and `milestone` are the two facts
    beside it that are records in the same sense: when the work landed, and which
    release shipped it. All three are written once, by the branch that closed the
    item, and all three are read back long afterwards - `closed` by `docket gate`
    deciding which side of a freeze an item falls on, `milestone` by `docket
    release` and `wave` deciding which release's notes it belongs in (`PL-JSRH`).

    `pr` is the fourth and is guarded from the other side: `docket record`
    refuses to overwrite a different number, which is what made the gap in these
    two visible.
    """

    identifier: str
    verify: str
    closed: date | None = None
    milestone: str = ""


@dataclass(frozen=True)
class RecordReport:
    """What the base recorded as the `verify:` of the closed items changed here.

    A closed item's command is a record of an experiment that was performed:
    this command was run, it failed before the work and passed after. It is a
    fact about a tree that no longer exists, not a claim about `main` today,
    and it stops resolving as a matter of course - measured over this store,
    14 of the 179 closed items carrying one no longer resolve, and every one
    of the 14 is a later change correctly consuming the state the earlier item
    established. Four are `grep '^blocked-by: PL-...'` commands whose blocker
    was resolved, which is to say commands written to stop resolving.

    So the reading this supports is not "has the command rotted" - it has, and
    that is the system working - but "is this branch about to rewrite one".
    Re-pointing a closed command at whatever covers the ground now replaces the
    command that proved the work with one that never ran it, which is a false
    provenance where there was a true one.

    `declined` carries the same meaning it does everywhere else here: a check
    that could not run, reported as such rather than as a clean result.
    """

    base: str = ""
    #: One entry per closed item this checkout changed that the base also reads
    #: `done`. An id absent from the base, open on it, or untouched here is
    #: absent from this, so a missing entry is "nothing to compare" rather than
    #: "compared and matched".
    records: tuple[BaseRecord, ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def commands(self) -> dict[str, str]:
        return {record.identifier: record.verify for record in self.records}

    @property
    def landings(self) -> dict[str, BaseRecord]:
        """Each record by id, for the reads that want the fields beside `verify:`."""
        return {record.identifier: record for record in self.records}


def _changed_items(root: Path, base: str, items_dir: str, run: Runner) -> set[str]:
    """The item ids this checkout has changed, committed on the branch or not.

    Two diffs, because `make check` runs at two moments and each is blind to
    the other's case. `<base>...HEAD` is what the branch's commits changed,
    which is what CI sees on a pull request; `HEAD` is what the working tree
    holds and has not committed, which is what a session sees running `make
    check` before committing - the moment an edit can still be undone cheaply.

    Neither is `<base>` against the working tree, which would have been one
    call for both. That form also lists the files *the base* changed and this
    branch did not, so a branch merely behind `main` would be asked to answer
    for somebody else's edit. A check that accuses the wrong branch is one
    every session learns to route around, which is the failure `CLAUDE.md`
    reserves its retirement rule for.

    A `...` with no merge base to resolve returns nothing here, because git
    exits non-zero and `_run_git` answers with an empty string *marked* as one
    it never gave. Both callers wrap their runner in `_Silences`, so what
    reaches a reader is a decline rather than "this branch changed no items":
    `records_on_base` since it was written, `changed_items` since `PL-ZPDM`.
    The answer itself still under-reports rather than guessing, which is what
    keeps a partial read from reporting a rewrite that did not happen.
    """
    changed: set[str] = set()
    for revision in (f"{base}...HEAD", "HEAD"):
        for line in run(["diff", "--name-only", revision, "--", items_dir], root).splitlines():
            path = line.strip()
            match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1]) if path else None
            if match is not None:
                changed.add(match.group(1))
    return changed


@dataclass(frozen=True)
class ChangedItems:
    """The items a checkout changed against a base, or why that is not known.

    `declined` because of what the one caller does with the set.
    `docket check --verify --verify-base` scopes the `verify:` replay to these
    ids, so an empty set that means "git would not say" scopes the replay to
    nothing and the run reports a clean result it never established - the
    permissive direction, on the gate CI is holding a pull request to
    (`PL-ZPDM`). The private form has always had a channel, because
    `records_on_base` wraps its runner; this is that channel reaching the
    public read.
    """

    identifiers: frozenset[str] = frozenset()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def changed_items(
    root: Path, base: str, *, items_dir: str = "docs/items", runner: Runner | None = None
) -> ChangedItems:
    """The item ids this checkout has changed against `base`, or why that is unread.

    The public form of `_changed_items`, which `records_on_base` has used
    internally since it was written. `docket check --verify-base` reads it to
    narrow the replay to the items a branch can actually have changed
    (`PL-SDHR`), which is a different caller with the same question.

    Its one-sidedness is the property both callers rely on and is documented on
    the private function: what it cannot read it leaves out rather than
    guessing at. That makes a scoped run check nothing rather than the wrong
    thing - correct, and half an answer until the run can also say *why* the
    scope is empty, which is what `declined` carries.
    """
    run = _Silences(runner or _run_git)
    return ChangedItems(
        identifiers=frozenset(_changed_items(root, base, items_dir, run)), declined=run.reason
    )


def records_on_base(
    root: Path,
    closed: Mapping[str, str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> RecordReport:
    """What the default base records as the `verify:` of each closed item changed here.

    `closed` maps an item id to the file name holding it, for every item that
    reads `done` in the working tree. Narrowing that to the ones this checkout
    actually changed happens here rather than in the caller, because it is a
    question about git rather than about the store: the store cannot tell
    which of two hundred closed items this branch has an opinion about, and
    asking after all of them would be a `git show` each on every `make check`.

    Resolution is by id, never by path. Retitling an item renames its file, so
    the working tree's path need not exist on the base at all and a comparison
    by path would read the rename as an item the base does not hold - the gap
    `closures_on_base` accepts, closed here because one `ls-tree` answers it
    for the whole store and is read only when something changed.

    Needs no history behind the base: one tree listing and one `git show` per
    changed closed item, which is what lets it answer in the shallow clone an
    agent session starts from.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return RecordReport(declined="no default branch this checkout can read")
    changed = _changed_items(root, base, items_dir, run) & set(closed)
    if not changed:
        return RecordReport(base=base, declined=run.reason)
    at_base = _items_at(base, root, items_dir, run)
    records: list[BaseRecord] = []
    for identifier in sorted(changed):
        path = at_base.get(identifier)
        if path is None:  # closed here, and the base has never held the item
            continue
        text = run(["show", f"{base}:{path}"], root)
        if not text:
            continue
        recorded = parse_item(text, path.rsplit("/", 1)[-1])
        if recorded.status == "done":
            records.append(
                BaseRecord(
                    identifier=identifier,
                    verify=recorded.verify,
                    closed=recorded.closed,
                    milestone=recorded.milestone,
                )
            )
    return RecordReport(base=base, records=tuple(records), declined=run.reason)


@dataclass(frozen=True)
class WrittenReport:
    """Which open items' `verify:` this checkout wrote, rather than inherited from the base.

    The authoring moment of a command, which the store cannot date: `added:`
    says when an item was captured, not when its command was written, and a
    rule dated by capture never reaches the commands written for older items -
    the ones given a command at triage, and the legacy ones rewritten as their
    items start. The branch that changes a command is where it was written, so
    a rule about what a command may be is held to it there (`PL-1P5V`).

    One-sided, as `RecordReport` is: an id absent from `identifiers` was not
    written here or could not be read, and `declined` says which.
    """

    base: str = ""
    identifiers: frozenset[str] = frozenset()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def commands_written_here(
    root: Path,
    commands: Mapping[str, str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> WrittenReport:
    """The open items whose `verify:` this checkout wrote, against the default base.

    `commands` maps each open item carrying a command to that command. An item
    is written here when the branch changed its file and the base's copy
    records a different command, or none, or the base has never held the item.
    Resolved by id, as `records_on_base` is, so a retitle is not read as a new
    item; and one `git show` per changed open item, which is usually none.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return WrittenReport(declined="no default branch this checkout can read")
    changed = _changed_items(root, base, items_dir, run) & set(commands)
    if not changed:
        return WrittenReport(base=base, declined=run.reason)
    at_base = _items_at(base, root, items_dir, run)
    written: set[str] = set()
    for identifier in sorted(changed):
        path = at_base.get(identifier)
        text = run(["show", f"{base}:{path}"], root) if path else ""
        recorded = parse_item(text, path.rsplit("/", 1)[-1]).verify if path and text else ""
        if recorded != commands[identifier]:
            written.add(identifier)
    return WrittenReport(base=base, identifiers=frozenset(written), declined=run.reason)


@dataclass(frozen=True)
class ClosedByReport:
    """Which items one commit closed, or why that could not be read.

    The counterpart to `ClosureReport`, asked from the other end. That one
    starts from a set of closures and walks history backwards looking for the
    merge that landed each; this starts from one merge and reads what it
    closed. A caller that already knows the number - the merge-time job, which
    is handed it by the event that fired it - needs only this one, and needs no
    subject parsing at all.
    """

    revision: str = ""
    #: Item id to the path holding it in that commit's tree. Pairs rather than
    #: a mapping, to stay hashable like every other report in this module;
    #: `paths` unpacks it.
    closed: tuple[tuple[str, str], ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def paths(self) -> dict[str, str]:
        return dict(self.closed)


def closed_by(
    revision: str, root: Path, *, items_dir: str = "docs/items", runner: Runner | None = None
) -> ClosedByReport:
    """The items whose closure `revision` itself landed, as id to path.

    Closed *here* means `status: done` in this commit's tree and not in its
    parent's. That is the question a merge-time caller is asking, and the
    stricter half of it is the parent: a pull request records its number on
    what it closed, never on what was already closed when it branched.
    `_number_closing` asks the same question of one file, walking backwards
    until it finds the commit that closed it; this asks it of one commit,
    forwards, and needs no subject to parse because the caller already has the
    number.

    The comparison is by id rather than by path. A title edit renames an item's
    file, so a path missing from the parent tree proves nothing about whether
    the item was already done - it may have been done under its old name.
    Reading the parent's ids costs one `ls-tree` and removes the whole class.

    `git diff` against the first parent rather than `diff-tree`, because a true
    merge commit shows an empty `diff-tree` by default and would read as
    closing nothing. Only the files the commit touched are examined, which is
    what keeps this at a handful of tree reads instead of one per item: a file
    the commit did not touch cannot have been closed by it.

    A revision whose parent this checkout does not hold declines rather than
    answering. At `fetch-depth: 1` there is nothing to compare against, and
    "no parent" would otherwise read as "everything done here was closed here"
    - the confident wrong answer this module refuses to give, and here it would
    stamp one pull request number across the whole store. It did, through the
    two readings behind `closures_on_base`, which asked the same question
    without this guard until `PL-KX9N`. `_parent_in_reach` is shared with them
    now, so the three cannot drift apart again.
    """
    run = _Silences(runner or _run_git)
    if not run(["rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}"], root).strip():
        return ClosedByReport(declined=f"what `{revision}` closed: it names no commit here")
    if not _parent_in_reach(revision, root, run):
        return ClosedByReport(
            declined=(
                f"what `{revision}` closed: its parent is outside this checkout, so its tree "
                f"has nothing to be compared against"
            )
        )

    touched: dict[str, str] = {}
    listing = run(["diff", "--name-only", f"{revision}^", revision, "--", items_dir], root)
    for line in listing.splitlines():
        path = line.strip()
        name = path.rsplit("/", 1)[-1]
        match = ITEM_FILE_RE.match(name) if path else None
        if match is not None and _done_at(revision, path, name, root, run):
            touched[match.group(1)] = path
    if not touched:
        return ClosedByReport(revision=revision, declined=run.reason)

    before = _items_at(f"{revision}^", root, items_dir, run)
    closed = {
        identifier: path
        for identifier, path in touched.items()
        if not _done_before(before.get(identifier), revision, root, run)
    }
    return ClosedByReport(
        revision=revision, closed=tuple(sorted(closed.items())), declined=run.reason
    )


def _done_before(path: str | None, revision: str, root: Path, run: Runner) -> bool:
    """Whether the item held at `path` already read `done` in `revision`'s parent.

    An id absent from the parent tree is new in this commit, which cannot have
    been done before it.
    """
    if path is None:
        return False
    return _done_at(f"{revision}^", path, path.rsplit("/", 1)[-1], root, run)


def _title_at(ref: str, path: str, root: Path, run: Runner) -> str:
    """The title an item file carries on a branch, or empty if it cannot be read."""
    text = run(["show", f"{ref}:{path}"], root)
    return parse_item(text, path).title if text else ""


def stranded(
    root: Path,
    known_ids: set[str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
    fetched: bool = False,
) -> StrandedReport:
    """Items that exist on some branch and in neither the store nor the default branch.

    An item is committed on whatever branch the capturing session was on. If
    that branch is never merged the item exists only there, and since every
    other session reads `docs/items/` in its own checkout, nothing will ever
    mention it again. This is the read that finds those.

    Comparison is by **id and content, never by commit counts**, and that is
    the whole design. A squash-merged branch is never contained in the default
    branch, so a containment test calls it unmerged forever and reports every
    item it carries as lost; a renamed item file was added twice and deleted
    once, so a test over added paths reports the old name as lost. Both are
    answered by looking at what the trees actually hold: an id present on the
    default branch is not stranded, however its commits got there.

    `known_ids` is what the calling session can already see - the store in its
    own working tree - so an item captured on this branch a moment ago is not
    reported back to the session that captured it. The default branch's own
    ids are added to that, because a branch forked before an item landed has a
    working tree missing it and would otherwise report it as stranded.

    **It never fetches, and `fetched` is what the caller says it did.** The
    rule the rest of this module follows - a read that must work from a bare
    checkout with no network - applies here too, so refreshing the base is
    `cmd_stranded`'s and it is not optional there: every finding is a claim
    about what the base does *not* hold, and that claim is only as old as the
    last fetch. `StrandedReport.fetched` carries what happened into the output.

    **The second half: an item the base holds whose substance is on a
    branch.** An item file is created once and appended to by every session
    that learns something about it, so the unmerged *section* is the commoner
    loss and the id test above is blind to it - a whole section of `PL-879R`'s
    brief sat on an abandoned branch with nothing reporting it (`PL-KSCW`).
    `_standing` decides per item file which side is ahead, and only the ref's
    being ahead is reported. That direction is the other half of the defect:
    a ref holding an older copy carries nothing to recover, and offering one
    for recovery is how `main`'s `done` copy of `PL-THPB` came to be handed a
    `git checkout` of a branch's `untriaged` one (`PL-MBTZ`).

    **Three filters before anything is read, in cost order.** The ref's blob
    equal to the base's settles 24,829 of this repository's 27,009
    ref-and-item pairs; a blob the base's history has held settles a further
    2,158, and settles them *correctly* rather than merely cheaply, since the
    base replacing its own prose leaves the ref holding lines the base lacks -
    judged on text alone that reads as ahead, and 873 of them did. What
    survives is 15 pairs to open, and the measured cost of the whole read is
    0.35 s against 13.4 s without the blob filter (2026-09-21).

    **An edit this session is itself holding is not reported back to it**,
    which is `known_ids` above applied to content rather than to ids: a copy
    whose blob `HEAD` also holds is one the session can see, whether it
    pushed it a moment ago or is working it now.
    """
    run = _Silences(runner or _run_git)
    refs = [
        line.strip()
        for line in run(
            ["for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"], root
        ).splitlines()
        if line.strip()
    ]
    if not refs:
        return StrandedReport(declined="no branch refs this checkout can read", fetched=fetched)

    base = default_base(root, runner=run)
    on_base = _item_blobs(base, root, items_dir, run)
    if not on_base:
        # Either the read failed or the store does not live where it was said
        # to. Both would make every item on every branch look stranded, which
        # is the one output worse than none: it is long, alarming and wrong.
        #
        # A third cause reaches here and needs its own words: where no base
        # resolved, saying "no items found on main" asserts the very ref that
        # is missing, and sends a reader to look at a branch rather than at
        # their checkout (`PL-73P0`).
        return StrandedReport(
            declined=run.reason
            if run.guessed_base
            else f"no items found on {base}, so every branch would read as stranding its own",
            fetched=fetched,
        )

    known = {identifier.upper() for identifier in known_ids} | set(on_base)
    held = _base_blobs(base, root, run)
    here = _item_blobs("HEAD", root, items_dir, run)
    elsewhere: dict[str, tuple[str, list[str]]] = {}
    edited: dict[str, tuple[str, str, str, list[str]]] = {}
    for ref in refs:
        if ref == base:
            continue
        for identifier, (blob, path) in _item_blobs(ref, root, items_dir, run).items():
            recorded = on_base.get(identifier)
            if recorded is None:
                if identifier in known:
                    # The session's own store holds it and the base does not,
                    # which is at risk rather than lost - and nothing here can
                    # compare a copy the base has never had.
                    continue
                # Every branch holding it is recorded, not just the first. A
                # branch missing from the report strands nothing and is safe to
                # delete on that count; naming only one copy would make the
                # branch holding the other look clean.
                elsewhere.setdefault(identifier, (path, []))[1].append(ref)
                continue
            base_blob, base_path = recorded
            mine = here.get(identifier, ("", ""))[0]
            if blob in (base_blob, mine) or blob in held:
                continue
            ref_text = run(["show", f"{ref}:{path}"], root)
            base_text = run(["show", f"{base}:{base_path}"], root)
            if ref_text and base_text and _standing(base_text, ref_text) != _AHEAD:
                continue
            # A copy neither side could be read for is reported rather than
            # dropped, the direction `_superseded` takes for the same reason:
            # an unread comparison must not come back as "the base has it".
            title = parse_item(ref_text, path).title if ref_text else ""
            edited.setdefault(identifier, (path, base_path, title, []))[3].append(ref)

    found = [
        StrandedItem(
            identifier=identifier,
            title=_title_at(branches[0], path, root, run),
            path=path,
            branches=tuple(branches),
        )
        for identifier, (path, branches) in sorted(elsewhere.items())
    ]
    edits = [
        StrandedEdit(
            identifier=identifier,
            title=title,
            path=path,
            base_path=base_path,
            branches=tuple(branches),
        )
        for identifier, (path, base_path, title, branches) in sorted(edited.items())
    ]
    return StrandedReport(
        items=tuple(found),
        edits=tuple(edits),
        base=base,
        refs_read=len(refs),
        fetched=fetched,
        declined=run.reason,
    )


@dataclass(frozen=True)
class LostItem:
    """An item file this ref's history held, and its tree no longer does.

    `blob` rather than the commit that held it, for two reasons. It is what
    recovers the content - `git cat-file -p <blob>` works for as long as any
    checkout holds the object, and keeps working after the branch is deleted,
    which a `git show <commit>:<path>` recovery does not. And finding the
    commit would cost a `--find-object` history walk per blob, which is the
    expense `PL-01CK` measures against exactly this kind of read.
    """

    identifier: str
    path: str
    blob: str


@dataclass(frozen=True)
class LostReport:
    """Items removed from the tree without any commit deleting them.

    `truncated` carries the same honesty `StrandedReport.refs_read` does: a
    clean answer from a clone holding twenty commits and a clean answer from
    one holding the whole history are different claims, and only one of them
    means the store is sound.

    `declined` means the check could not run, reported as such rather than as
    a clean result.
    """

    items: tuple[LostItem, ...] = ()
    ref: str = ""
    truncated: bool = False
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def lost(
    root: Path, *, ref: str = "HEAD", items_dir: str = "docs/items", runner: Runner | None = None
) -> LostReport:
    """Item ids this ref's history holds a file for, and its tree does not.

    **Why the object walk rather than a diff.** A conflict resolution deletes
    the file in the *merge's own tree*, and a merge is not diffed against
    either parent by default, so `git log --diff-filter=D -- docs/items/`
    returns nothing for the case this exists to catch. Reproduced 2026-09-02
    against a scratch repository: the deletion is invisible to the diff walk
    and plainly visible in the object walk, which lists every blob reachable
    from the ref with the path it was stored under.

    **Why it must be asked of a branch, not of the default branch.** After a
    squash merge the branch's commits are not ancestors of anything, so its
    objects stop being reachable and the evidence is gone. Measured on this
    repository: `PL-Q8QX` was captured on the v0.3.0 release branch, dropped
    by a merge resolution, and is reachable from no commit `main` holds - a
    check run on `main` reports it clean and is wrong to. So this runs on the
    branch, in CI, on the pull request, before the squash collapses the
    history. It still catches an ordinary merge on the default branch; it
    cannot catch a squashed one, and nothing run there can.

    **Comparison is by id, never by path.** An item file is renamed whenever
    its title changes, which adds one path and removes another. By path that
    reads as a loss; by id it reads as what it is.
    """
    run = _Silences(runner or _run_git)
    present = _items_at(ref, root, items_dir, run)
    if not present:
        # The same guard `stranded` keeps: an unreadable store makes every id
        # in the history look lost, which is the one output worse than none.
        return LostReport(
            ref=ref, declined=f"no items found on {ref}, so its whole history would read as lost"
        )

    prefix = items_dir.rstrip("/") + "/"
    ever: dict[str, tuple[str, str]] = {}
    for line in run(["rev-list", "--objects", ref], root).splitlines():
        blob, _, path = line.partition(" ")
        path = path.strip()
        if not path.startswith(prefix):
            continue
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1])
        if match is not None:
            # `rev-list` walks newest commit first, so the first blob seen for
            # an id is the last content it had. That is the version worth
            # handing back for recovery.
            ever.setdefault(match.group(1), (blob.strip(), path))

    gone = tuple(
        LostItem(identifier=identifier, path=path, blob=blob)
        for identifier, (blob, path) in sorted(ever.items())
        if identifier not in present
    )
    return LostReport(
        items=gone,
        ref=ref,
        truncated=is_shallow(root, runner=run) is not False,
        declined=run.reason,
    )


@dataclass(frozen=True)
class OrphanedCommit:
    """A commit on a branch carrying content the default branch does not hold."""

    commit: str
    subject: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class OrphanedBranch:
    """A branch the default branch took part of and not the rest.

    `landed` is what makes this different from an ordinary branch in flight,
    and it is most of the evidence. A branch nobody has merged has landed
    nothing; a branch merged whole is not reported here at all, because
    `_unlanded_refs` already excluded it. Both sides non-empty means the base
    holds some of what this branch introduced and not the rest - which is what
    a branch looks like after its pull request merged and something pushed to
    it afterwards.

    It is not the *whole* of the evidence, and `_commits_by_landing` carries
    the rest: these paths are only evidence of a merge where the base took a
    whole commit of this branch, since two sessions running `bin/docket record`
    write identical lines and each then holds content the other landed
    (`PL-5TRV`). The paths are still what a reader is shown, because the count
    is what makes the finding legible; the commits are what make it true.
    """

    ref: str
    landed: tuple[str, ...]
    outstanding: tuple[str, ...]
    commits: tuple[OrphanedCommit, ...]


@dataclass(frozen=True)
class OrphanedReport:
    """Work that exists only on a branch whose pull request has already merged.

    The counterpart to `StrandedReport`, asked of the tree instead of the
    store. That one finds an *item* nobody merged, by comparing ids across
    trees; this finds any *content* nobody merged, and the asymmetry it closes
    is the finding in `PL-3D2M`: the queue had a stranded-work detector and the
    rest of the repository had none, so a dropped commit that touched
    `docs/items/` surfaced in the next session and one that touched a skill, a
    rule or `src/` did not.

    `refs_read` and `unreadable` carry the same meaning they do for
    `StrandedReport` and `FlightReport`: what was compared, and which refs the
    checkout could not compare, so a clean answer from a container holding two
    refs is not mistaken for one from a checkout holding twenty.
    """

    branches: tuple[OrphanedBranch, ...] = ()
    refs_read: int = 0
    unreadable: tuple[str, ...] = ()
    #: Refs that match this report's rule but whose divergence from the base is
    #: duplicated history, so the content evidence cannot tell them from a
    #: merge. Kept apart from `branches` because the recipe a merged branch
    #: leads a reader to deletes the ref, and on pre-rewrite history that ref is
    #: the only copy of the commits it carries (`PL-Y31G`).
    rewritten: tuple[str, ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def _commits_by_landing(
    ref: str,
    base: str,
    landed: frozenset[str],
    outstanding: frozenset[str],
    root: Path,
    run: Runner,
    items_prefix: str,
) -> tuple[tuple[OrphanedCommit, ...], bool]:
    """One walk of the ref's commits, read for both halves of the rule.

    Returns the commits *none* of whose work reached the base, newest first,
    and whether the base took any commit of this branch **whole**. The two
    readings come off one `git log` because they are one question asked from
    opposite ends, and two walks would be two answers waiting to disagree.

    **Wholly, not partly, and that is the whole of the rule.** A commit whose
    changes are partly on the base is a commit the merge *took*: the squash
    landed it and merged it with whatever the base had changed underneath, so
    the files they both touched differ from the branch's copies while the work
    itself is there. A commit none of whose changes reached the base is one
    nothing took. Only the second is work left behind.

    That distinction was learned from this check's own first live firing
    (`PL-JHJ3`). `origin/claude/snapshot-run-history-copy-dw6djz` carried the
    v0.3.8 release commit, which `#312` squash-merged while `#311` was landing
    edits to the same `ROADMAP.md` prose; the merge wrote the combined text, so
    three of that commit's ten paths read as never landed and the branch was
    reported as carrying lost work. `main` was *ahead* of it, not missing
    anything. Ten paths touched and seven landed is the signature of a merge
    that happened, and no content comparison of the outstanding three can see
    that - only counting them against the rest of the same commit can.

    A merge commit lists no paths of its own under `--name-only`, which is the
    wanted behaviour: merging the default branch into a branch introduces no
    work to leave behind, and such a commit is neither reported nor counted.

    The cost is recall, in one narrow shape: a commit pushed after the merge
    that happens to leave one file in a state the base has held reads as partly
    landed and goes unreported. Silence is this check's expensive direction
    everywhere else, and the trade is taken here only because the alternative
    was an advisory firing in every session's digest - which `CLAUDE.md` calls
    a defect in the check rather than coverage.

    **The same rule pointed at the landed side, which is the second half.**
    Agreement with the base does not mean the base took it: `bin/docket record`
    writes a value the tool dictates rather than one a session chooses, so two
    branches running it write byte-identical lines and each reads as holding
    the other's landed work. `#372` was reported as merged on the strength of
    eight such files while its pull request was open and none of its triage had
    landed anywhere (`PL-5TRV`). No comparison of those blobs can ever tell
    convergence from a merge, because there is nothing to tell apart - the
    bytes are the same. What differs is the *unit*: a squash merge takes whole
    commits, so a merged branch has a commit every path of which the base
    holds, and convergence scatters files inside commits and leaves no whole
    one. Hence the boolean, and hence it is computed the same way the commits
    above are rather than from a count or a ratio.

    Its own recall cost is the mirror of the one above and just as narrow: a
    branch whose every pre-merge commit was re-merged against a base that moved
    under it has no wholly landed commit either, and a post-merge push to it
    goes unreported.

    **A commit that only wrote to the queue is not merge evidence either, and
    that is the last of the convergence shapes** (`PL-JBRC`). The unit test
    above holds because a squash takes whole commits while convergence scatters
    files inside them - but a commit whose *entire* diff is `bin/docket record`
    output converges whole, every path of it agreeing with the base because the
    tool dictated the value rather than a session choosing it. So a branch
    carrying one of those and one genuinely outstanding commit read as a merged
    pull request with work left behind, and the recipe that verdict leads to
    deletes the ref an open pull request was raised against - `PL-5TRV`'s harm
    reached by a narrower route.

    `_annotates_only` is the test, which is the same reading
    `branches_in_flight` already applies to the same commits for the same
    reason: a capture, a triage pass, a recovered item and a `record` write all
    lead with an id they are not implementing, and none of them is work a merge
    took. Using it here rather than matching `pr:` lines keeps one rule for
    "this commit wrote to the queue and nowhere else" instead of two spellings
    that can disagree, and it covers the other three shapes at no extra cost.

    Its recall cost is a branch whose only wholly landed commit is a queue
    write and which was then pushed to - now unreported. That is the direction
    to fail in: this half of the rule exists to convict a branch of having
    merged, and the reader it convinces is handed a ref deletion.

    `\\x1e` opens each record so a subject containing a newline cannot be read
    as the start of another commit.
    """
    output = run(["log", "--format=%x1e%H%x1f%s", "--name-only", f"^{base}", ref, "--"], root)
    found: list[OrphanedCommit] = []
    took_one_whole = False
    for record in output.split("\x1e"):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        commit, _, subject = header.partition("\x1f")
        touched = tuple(line.strip() for line in body.splitlines() if line.strip())
        if not touched:
            # A merge commit, which lists no paths of its own: it introduces no
            # work to leave behind and proves no merge of this branch either.
            continue
        if all(path in outstanding for path in touched):
            found.append(
                OrphanedCommit(commit=commit.strip(), subject=subject.strip(), paths=touched)
            )
        elif all(path in landed for path in touched) and not _annotates_only(
            list(touched), items_prefix
        ):
            took_one_whole = True
    return tuple(found), took_one_whole


def landed_whole(
    base: str, root: Path, run: Runner, *, ref: str = "HEAD", items_dir: str = "docs/items"
) -> bool:
    """Whether the default branch has already taken a whole commit of this ref's work.

    **The question the commit counts cannot answer.** A squash merge writes one
    new commit carrying the branch's content and none of its commits, so the
    branch still counts every one of them as `ahead` and never reaches the
    `ahead == 0` that `RESTART` fires on. It reads as `MERGE` - "merge the base
    in" - which on a merged pull request is advice that loses the commit the
    session is holding, because nothing merges a merged pull request a second
    time (`#284`, `PL-8M8H`).

    **The reading is `orphaned`'s, deliberately not a second one.** Every guard
    the verdict needs is already written and tested next door, and the project
    owner's decision of 2026-09-12 requires them rather than the unqualified
    "the landed side is non-empty" the item's own brief asserted: two documented
    shapes satisfy that and neither is a merge. So the pipeline is reused whole
    - `_landing_split` for the content split, `_superseded` to drop paths the
    base's tip no longer needs (`PL-XLQ5`), and `_commits_by_landing` for the
    unit test that a squash takes commits whole where convergence scatters
    files inside them (`PL-JHJ3`, `PL-5TRV`) and for its refusal to read a
    queue-only annotation as merge evidence (`PL-JBRC`).

    **Where it differs from `orphaned`, and why.** That report wants a branch
    whose work the base took only *part* of, so it requires a commit left
    behind as well as one taken whole. This wants the whole of that family: a
    branch whose every commit landed is exactly the case observed on
    `claude/focused-carson-ji73cn`, where `git diff --diff-filter=A` against
    the base was empty and the branch was still told to merge. Requiring
    something left behind would decline the commonest instance of the defect.

    **A wrong answer here is not symmetric, and the asymmetry decides the
    trade.** Saying `MERGE` where the truth is `LANDED` is the defect - one
    commit lost silently. Saying `LANDED` where the truth is `MERGE` costs a
    reader one look at the pull request before restarting, and `format_branch_state`
    prints the verdict rather than acting on it, as everything here does.
    Nevertheless the narrowed reading is what is used, because the recovery it
    leads to deletes a ref.

    Args:
        base: The default branch to compare against.
        root: Repository root.
        run: The git runner.
        ref: Which side to read; the checkout's own `HEAD` by default.
        items_dir: The queue directory, whose commits are not merge evidence.

    Returns:
        `True` only where the base holds a whole commit of this ref that is not
        a queue annotation. `False` where it does not, and where git would not
        answer - an unreadable fork point is the `MERGE` status quo rather than
        an invitation to restart.
    """
    fork_point = run(["merge-base", base, ref], root).strip()
    if not fork_point:
        return False
    landed, outstanding = _landing_split(ref, fork_point, _base_blobs(base, root, run), root, run)
    if not landed:
        return False
    superseded = _superseded(ref, base, outstanding, root, run)
    outstanding = tuple(path for path in outstanding if path not in superseded)
    _, took_one_whole = _commits_by_landing(
        ref, base, frozenset(landed), frozenset(outstanding), root, run, items_dir.strip("/") + "/"
    )
    return took_one_whole


def orphaned(
    root: Path,
    *,
    include_remote: bool = True,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> OrphanedReport:
    """Branches carrying work the default branch took only part of.

    **The failure it detects.** A pull request merges; the session pushes one
    more commit to the same branch afterwards. Nothing merges a merged pull
    request a second time, so that commit lands nowhere - and it is silent in
    every direction that would normally catch a mistake. There is no conflict,
    no red check and no advisory; the branch reads as merged, the pull request
    reads as merged, and the next session starts from a default branch missing
    work everyone believes landed. Observed 2026-09-04 on `#284`, whose
    follow-up `#286` says it outright: "That pull request merged at its first
    commit, so the behavior change pushed to the same branch afterwards never
    landed."

    **Why the branch ref is the evidence and the pull request is not.** GitHub
    freezes `refs/pull/<n>/head` when the pull request closes, so the commit
    pushed after the merge appears in no pull-request ref and no merge-time
    check could see it. Measured against this repository: all 311 pull refs
    survive branch deletion, and comparing each merged head against the commit
    that landed it found no discrepancy in any of the 204 then merged - the loss
    is not visible from that side at all. What does survive is the branch,
    precisely because the post-merge push recreates or keeps it.

    That 204 is a sample and not a proof, and saying so is the point: the very
    next merge produced a shape it did not contain - a release branch whose
    prose the base had edited under it - and the check fired falsely on it. The
    population a measurement covered is part of what it measured.

    **Beside the exact check, never replaced by it** (`PL-BHVM`, `PL-LF2C`).
    `tools/left_behind_check.py` asks the same question from the pull-request
    side - does the branch's tip descend from the head its merged pull request
    froze - and where both answer and disagree, that one wins and says so. It
    is not a superset of this one even in principle, because its evidence is
    GitHub's and this one's is the checkout's. It answers only where GitHub
    does, since git keeps no record of which pull request came from which
    branch. And GitHub can take the evidence away: pull refs survive branch
    deletion, as measured above, but not a request to delete them, which this
    repository made for `#297`-`#386` (`PL-0SCG`). All 90 were gone by
    2026-09-23, so for a branch whose merged pull request is among them that
    check declines with `no such ref` even online. Reading the head the
    pull-request record kept (`PL-P3GV`, left unbuilt) would narrow the gap
    without closing it, since that record is GitHub's too. Wherever that check
    declines, this one is all that stands between a commit pushed after the
    merge and its loss.

    **The rule, in three parts, and only the first was got right first time.**
    A branch whose introduced content is partly on the base and partly not,
    *and* which carries a commit none of whose paths reached the base at all,
    *and* one of whose commits the base took whole. The content split alone
    selects candidates - a branch nobody merged has landed nothing and is
    ordinary work in flight; a branch merged whole never reaches here - but it
    cannot tell a commit nothing took from a commit the merge took and
    *merged*, which is what a squash against a base that moved underneath
    produces (`PL-JHJ3`), and it cannot tell content the base took from content
    the base and the branch wrote identically and independently (`PL-5TRV`).
    `_commits_by_landing` carries both of those halves and the branch that
    taught each.

    **A commit whose change reached the base through another pull request is
    cleared by `change_landed`**, the one test `tools/left_behind_check.py`
    reads too (`PL-GHHW`), so the two checks no longer disagree about a port.

    **What it can get wrong**, now that agreement alone no longer convicts. Two
    directions, both silence. A commit pushed after the merge that happens to
    leave one file in a state the base has held is not reported; nor is a
    post-merge push to a branch whose every pre-merge commit was re-merged
    against a base that had moved under it, since neither side then has a whole
    commit. Silence is the expensive direction here and both trades are taken
    deliberately; `_commits_by_landing` says why. The reader decides, the way
    they do for `flight` and `stranded`.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    refs = _unlanded_refs(base, root, run, include_remote=include_remote)
    if not refs.listed:
        # No git, no repository, or a listing git could not answer. An empty
        # result would otherwise read as "every branch is accounted for",
        # which is the confident wrong answer this module refuses to give.
        return OrphanedReport(declined="no branch refs this checkout can read")
    branches: list[OrphanedBranch] = []
    rewritten: list[str] = []
    for name in refs.unlanded:
        landed, outstanding = refs.landing.get(name, ((), ()))
        if not (landed and outstanding):
            continue
        # **The outstanding side is narrowed to what the base's tip is missing
        # before anything is decided on it.** `_landing_split` answers per
        # historical blob, so a path whose content was replaced after the branch
        # introduced it - on the branch, or on the base - is outstanding there
        # and missing from nowhere. `_superseded` carries both shapes and why
        # the wrong answer was expensive rather than untidy.
        superseded = _superseded(name, base, outstanding, root, run)
        # And the narrowing a two-dot diff cannot make: an item file whose copy
        # here is an earlier revision of one the base has closed since. It
        # reads as outstanding above because its older `status:` line is an
        # addition, and the recovery offered for it overwrites the base's
        # closed copy with it (`PL-MBTZ`).
        superseded |= _behind_on_base(name, base, outstanding, root, items_dir, run)
        outstanding = tuple(path for path in outstanding if path not in superseded)
        if not outstanding:
            continue
        left, took_one_whole = _commits_by_landing(
            name,
            base,
            frozenset(landed),
            frozenset(outstanding),
            root,
            run,
            items_dir.strip("/") + "/",
        )
        # A split alone is not enough in either direction, and the branch that
        # taught each half is named in `_commits_by_landing`. The split says
        # some of the branch's content is not on the base, which a squash
        # merged against a moving base produces on its own; a commit *wholly*
        # absent says nothing took it, and without one there is also nothing to
        # hand a reader. And the landed side is only evidence of a merge where
        # the base took a whole commit, because two branches running `docket
        # record` write identical lines and neither merged the other.
        if left and took_one_whole:
            # **A rewritten history reads exactly like a merge here, and the
            # difference cannot be seen in the content.** This report's evidence
            # is which blobs the base holds, and a rewrite changes every hash
            # while leaving every byte alone - so a branch left on pre-rewrite
            # history has all the marks of one whose pull request merged
            # (`PL-YGF3`, observed on `claude/fresh-gas-flow-range-4bom2g`).
            # Asked last because it costs a walk of its own and only a branch
            # this report would otherwise name needs it.
            #
            # It is named rather than reported, and the asymmetry is the point.
            # The recovery this report hands a reader copies a file; the recipe
            # the `docket` skill prescribes for a merged pull request deletes
            # the ref, and on pre-rewrite history that ref holds the only copy
            # of commits nothing else has. So the branch leaves the list that
            # leads there and keeps a line of its own (`PL-Y31G`).
            if _duplicated_history(base, root, run, ref=name) is not None:
                rewritten.append(name)
                continue
            # **A commit whose change the base took through another pull
            # request is not left behind** (`PL-GHHW`), though every path of it
            # reads as outstanding: that pull request's squash carried the
            # change and more, so the base never held this commit's blob, and
            # its copy of the file is ahead of the branch's. The `recover:`
            # line would have handed a reader a checkout reverting it. Asked
            # after the rewrite test, because a rewritten ref's commits all
            # hold changes the base has, and that ref needs its own line.
            left = tuple(
                commit
                for commit in left
                if change_landed(commit.commit, base, root, runner=run) is None
            )
            if not left:
                continue
            # The branch's outstanding side is narrowed to the paths of the
            # commits actually reported. The wider set includes files a merged
            # commit touched that the base then merged differently, which are
            # not missing from anywhere and must not be offered for recovery.
            carried = tuple(sorted({path for commit in left for path in commit.paths}))
            branches.append(
                OrphanedBranch(ref=name, landed=landed, outstanding=carried, commits=left)
            )
    return OrphanedReport(
        declined=run.reason,
        branches=tuple(branches),
        refs_read=len(refs.candidates),
        unreadable=tuple(sorted(refs.unreadable)),
        rewritten=tuple(sorted(rewritten)),
    )


# One record per commit, then its `--numstat` block. `%x01` opens the header
# so it cannot be confused with a numstat line, which always begins with a
# count or a `-`. `%as` is the *author* date: it says when the change was
# written, where the committer date says when it was last applied and moves
# under a rebase or a squash merge.
CHURN_FORMAT = "--format=%x01%as"


@dataclass(frozen=True)
class Churn:
    """Lines written and removed, by the day of the commit and by the file.

    Added and deleted are summed rather than kept apart. The question this
    serves is where effort went, and a deleted line was written by somebody
    too - keeping the two apart invites reading a large deletion as negative
    work, which is the opposite of what it usually is.
    """

    by_day: Mapping[date, Mapping[str, int]] = field(default_factory=dict)
    #: Why this reading is partial, in the sense `FlightReport.declined` carries
    #: it. A silenced `git log` gives no days at all, which reads as a
    #: repository nobody has committed to (`PL-Q9Z1`).
    declined: str = ""

    def __bool__(self) -> bool:
        return bool(self.by_day)

    @property
    def known(self) -> bool:
        """Whether git answered every question this reading rests on."""
        return not self.declined


def _numstat_path(text: str) -> str:
    """The path a numstat line names, after any rename notation.

    Rename detection is left on, so a file moved without being edited costs
    nothing rather than counting its whole length twice. The price is that
    git writes the pair in one field, in either of two shapes - `old => new`
    and `dir/{old => new}/file` - and the second is not a prefix of the path
    it describes, so a moved file would be bucketed by a name beginning `{`.
    """
    if "=>" not in text:
        return text
    if "{" in text and "}" in text:
        before, rest = text.split("{", 1)
        inner, after = rest.split("}", 1)
        text = before + inner.split("=>")[-1].strip() + after
    else:
        text = text.split("=>")[-1].strip()
    return text.replace("//", "/")


def churn(root: Path, *, runner: Runner | None = None) -> Churn:
    """Every commit's line counts, by day and by path.

    Merges are excluded. A merge commit's `--numstat` against its first
    parent repeats the lines its branch already accounted for, so counting
    both doubles every change that arrived through a pull request - which is
    all of them here.

    Binary files are skipped rather than counted as zero: git reports them as
    `-`, and a repository's images have no line count to attribute.
    """
    run = _Silences(runner or _run_git)
    out = run(["log", "--no-merges", "--numstat", CHURN_FORMAT], root)
    by_day: dict[date, Counter[str]] = {}
    when: date | None = None
    for line in out.splitlines():
        if line.startswith("\x01"):
            try:
                when = date.fromisoformat(line[1:].strip())
            except ValueError:
                when = None
            continue
        parts = line.split("\t", 2)
        if when is None or len(parts) != 3 or parts[0] == "-" or parts[1] == "-":
            continue
        try:
            lines = int(parts[0]) + int(parts[1])
        except ValueError:
            continue
        by_day.setdefault(when, Counter())[_numstat_path(parts[2])] += lines
    return Churn({day: dict(counts) for day, counts in by_day.items()}, declined=run.reason)


def ref_walk(root: Path, items_dir: str, *, runner: Runner | None = None) -> RefWalk:
    """The ref set a profiled command walked, and the work hanging off it.

    Asked with a plain runner rather than the profiled one, and only when
    `--profile` was given, so measuring never appears in what it measures.

    The numbers are the ones that turned out to drive the counts, and they are
    reported per ref as well as in total because that is what lets two machines
    be compared by subtraction: `merge-base` is asked once per unmerged ref,
    `show` once per item file a ref introduces, and `diff` scales with both.

    **From each ref's fork point, never from the base's tip.** A two-dot diff
    against the base counts everything the *base* changed since the ref left it,
    which on this store is every item a triage pass has touched since: measured
    2026-09-16 it reported 4,767 item edits across 16 refs that introduce 50. A
    number that wrong is worse than none, because a profile is read as the
    controlled input that settles an argument.

    A ref whose merge-base this checkout cannot resolve is named in `unread`
    rather than counted as zero, for the reason `_unlanded_refs` names it: a
    truncated clone is the normal state of a container, and "introduces nothing"
    and "could not be read" are opposite answers.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return RefWalk(declined="no default branch this checkout can read")
    args = ["for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"]
    listing = [name.strip() for name in run(args, root).splitlines() if name.strip()]
    merged = {
        name.strip() for name in run([*args, f"--merged={base}"], root).splitlines() if name.strip()
    }
    prefix = items_dir.strip("/") + "/"
    walked: list[tuple[str, int, int]] = []
    unread: list[str] = []
    for name in listing:
        if name in merged:
            continue
        # The same fork point the walk itself compares against, so the profile
        # describes the input the command actually had rather than a second
        # reading of it that could disagree.
        fork = run(["merge-base", base, name], root).strip()
        if not fork:
            unread.append(name)
            continue
        ahead = run(["rev-list", "--count", f"{fork}..{name}"], root).strip()
        touched = [
            line
            for line in run(["diff", "--name-only", fork, name, "--", prefix], root).splitlines()
            if line.strip()
        ]
        walked.append((name, int(ahead) if ahead.isdigit() else 0, len(touched)))
    return RefWalk(
        listed=len(listing),
        merged=len(merged),
        unmerged=len(walked) + len(unread),
        commits=sum(ahead for _, ahead, _ in walked),
        item_edits=sum(edits for _, _, edits in walked),
        refs=tuple(walked),
        unread=tuple(sorted(unread)),
        declined=run.reason,
    )


@dataclass(frozen=True)
class WorkingPaths:
    """What this checkout is changing, and whether git answered in full.

    The proxy `bin/docket new` uses for a `touches` a fresh capture does not
    have. A capture is made *while* working on the thing that produced it, so
    what the working tree is changing is a good guess at what the capture is
    about - and it is the only guess available, since capture writes no
    `touches` and may not start asking for one.

    `declined` carries the same obligation it does on `FlightReport` and
    `FlightFiles`: an empty `paths` means "nothing changed" or "git did not
    answer", and the two must not be conflated. Here the consequence of
    conflating them is mild - the near-duplicate search finds nothing and the
    command behaves as it did before it existed - which is why the field is
    read rather than printed. It is still recorded, because a caller that
    wants to distinguish the two must be able to.
    """

    paths: tuple[str, ...] = ()
    base: str = ""
    declined: str = ""

    @property
    def known(self) -> bool:
        """Whether git answered every question this reading rests on."""
        return not self.declined


def working_paths(root: Path, *, runner: Runner | None = None) -> WorkingPaths:
    """The files this checkout has changed: committed on the branch, and not yet.

    Both halves, because a session captures a finding at any point in its work.
    The branch-local commits are what it has finished, and the uncommitted
    changes are what it is in the middle of - and the middle is where a finding
    is usually made, since it is what the session is looking at.

    Three reads rather than one `status --porcelain`, deliberately: the
    porcelain format carries status codes, rename arrows and shell-quoted paths
    with spaces, so parsing it is three chances to get a path wrong. Each of
    these prints one path per line and nothing else.

    The branch diff is `base...HEAD` rather than `base..HEAD` for the reason
    `files_in_flight` gives: the two-dot form re-reports every file the default
    branch changed since the fork as though this branch had changed it, which
    for a session started a day ago is most of the tree - and here that would
    make every capture match everything.

    **The store is not excluded, which was considered and refused.** Every
    session edits `docs/items/`, so it is tempting to read it as noise - but 28
    of this store's 341 open items declare a path under it, and they are the
    triage passes, backfills and queue-shape decisions that a capture *about*
    the queue genuinely duplicates. Two open triage items is exactly the warning
    worth having, and the recurring-by-design clusters are already dropped by
    scoring open items alone, which is where that job belongs.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    found: set[str] = set()
    for args in (
        ["diff", "--name-only", f"{base}...HEAD"],
        ["diff", "--name-only", "HEAD"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        found.update(line.strip() for line in run(args, root).splitlines() if line.strip())
    return WorkingPaths(paths=tuple(sorted(found)), base=base, declined=run.reason)
