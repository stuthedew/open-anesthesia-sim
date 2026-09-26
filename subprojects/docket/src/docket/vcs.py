"""What git already knows about work in progress.

Who holds an item is recorded; whether the work has landed is derived. This
module once derived both, because storing a hold in the item file would mean a
session has to remember to write it when it starts and to clear it when it
stops - and a session that crashes, or that is simply abandoned, leaves the
item marked in-progress forever with nobody able to tell whether that is true.
Deriving the holder failed in its own way. Read from which ids lead a commit's
subject, which paths it touched and how old the ref is, each new shape of work
was misread by some reader until it got an exception of its own, and twenty
items were that one mechanism (`PL-MB2W`). So a session records its hold as a
`Claim:` trailer on an empty commit on its own branch, nothing is written into
the store, and a claim whose branch goes seven days without a non-merge commit
lapses: the lease answers the crashed session, which was the whole case against
recording. Every reader of in-flight work asks `claims.holdings`, which reads
that record.

What stays here is what the repository holds without anybody writing it down.
A branch that is gone means work that is not in flight, which is exactly
right: branches are deleted when their pull request merges. Whether a branch's
work has landed is derived, because the merge authors that fact and no session
can record it (`_unlanded_refs`, `_landing_split`).

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
from .release import CUT_FLAGS, NOTES_DIR, cut_query, version_in
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


def changed_path_args(subcommand: str, *args: str) -> list[str]:
    """The argv for a read of which paths a change touched, a rename's two included.

    `git diff`, `show` and `log` pair a deleted path with a similar added one and
    print the pair as a rename, which under `--name-only` is the new name alone.
    Measured on git 2.43.0, 2026-09-25: `git mv` of
    `src/anesthesia_sim/core/alveolar.py` to `tools/`, committed, and both
    `git diff --name-only <base>...HEAD` and `git show --name-only` print only
    `tools/moved_core.py`. A read asking which paths the change touched then
    misses the path it deleted, and `verify`'s protected-path audit passed that
    branch as "none touched" while `arm`'s read of it listed the core file
    (`PL-KR69`). `--no-renames` reports the rename as the deletion and the
    addition it is, so every such read builds its argv here, and a new one cannot
    leave the flag out by copying whichever spelling it found first.

    `core.quotePath` is off for the same reason: a path git quotes is a path no
    caller can match. Left on, git prints a path outside ASCII as a quoted string
    of octal escapes, so a committed `src/anesthesia_sim/core/café.py` came back
    as `"src/anesthesia_sim/core/caf\\303\\251.py"`, quotes included, and the
    protected-path audit passed it as "none touched" (`PL-8HSX`). Off, it prints
    as written. A path holding a tab, newline, `"` or `\\` is quoted either way,
    measured on git 2.43.0, 2026-09-25, so a read that must see those as written
    adds `-z` and splits on NUL, as `verify.changed_paths` does. The `-c` goes
    ahead of the subcommand, where git reads it, so `argv[0]` here is `-c` and
    `subcommand_of` is what names the read.

    A read asking which file is new (`--diff-filter=A`) or where a file came from
    (`-M`, `--follow`) does not come here, because there the pairing is the
    answer: a retitled item is not a new filing.
    """
    return ["-c", "core.quotePath=false", subcommand, "--no-renames", *args]


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
    return subcommand_of(args) == "diff"


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
    | a path whose bytes are not in the locale's encoding | 0 | **silence** |

    The last row is this function's, not git's: `changed_path_args` has git
    print a path as written, and a `café.py` named in Latin-1 holds the byte
    `\\351`, which no UTF-8 decode reads, so `subprocess.run` raised out of a
    read whose contract is that nothing does (`PL-8HSX`, measured on Linux).
    Git answered; this could not read it.

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
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError):
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


def subcommand_of(argv: Sequence[str]) -> str:
    """The git subcommand an argv names, ignoring the options in front of it.

    `-c` and `-C` take their value as the next word, which is not the
    subcommand. `claims.work_under_record` asked `-c core.quotePath=false log`
    first, and read as the subcommand `core.quotePath=false` it was counted
    under that name and, being no read this module knows, emptied the memo
    (`PL-N162`). Every read `changed_path_args` builds now asks that way, which
    is why `verify` names a read that failed by this rather than by `argv[0]`.
    """
    words = iter(argv)
    for token in words:
        if token in {"-c", "-C"}:
            next(words, None)
        elif not token.startswith("-"):
            return token
    return ""


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
    #: Each unmerged ref's item files, summed across refs: an item file edited
    #: on ten refs counts ten.
    item_edits: int = 0
    #: The distinct item files those refs edit between them, so the same file
    #: counts once however many refs edit it. Printed beside the sum rather than
    #: in place of it, because the gap between the two is the overlap: on a clone
    #: of long-lived branches all editing one store the sum ran 2.6x the files,
    #: and a per-edit rate divided by the sum over-predicted by as much
    #: (`PL-3BYK`).
    item_files: int = 0
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
      `claims.holdings`, `orphaned` and `cuts_in_flight` - so two of every
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
        sub = subcommand_of(argv)
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
    `claims._history` has the argument - so a ref answering the merge-base
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
    merge whatever either commit was for - so `claims._editing` reads the same
    paths for that weaker fact and `FlightReport.editing` carries it. Two
    sessions triaged one pair of items on 2026-09-06 and the merge discarded
    one of the two answers: a triage pass has by definition no diff outside
    the queue, so it could never raise the mark this function withholds, and
    no amount of care with `show` or `flight` would have surfaced it
    (`PL-N1JK`). Nothing here is relaxed to fix that - `docket next` still
    ranks on `FlightReport.branches` alone.

    **It no longer decides who holds an item, except on old commits.** It
    could not see a session that *starts* an item by pushing only a `touches`
    fill or a `verify:` command, which is annotation by this rule and a claim
    in fact, and three promotions grew around it to recover shapes of that
    case: an item whose whole deliverable is a queue edit (`PL-7790`), one at
    `needs-decision` (`PL-VYSP`), and one the branch closes while the base
    holds it open (`PL-8FJK`). The claim record (`PL-MB2W`) ended the
    inference instead - a session claims an item with a `Claim:` trailer,
    whatever its commit's diff - and `PL-FX5Q` deleted the promotions with it.
    `claims` still reads a commit made before a session could write a claim
    by this rule alone, until `PL-CH3Z` retires that reading. `orphaned` asks
    it its own question: whether a commit wrote anywhere but the queue.
    """
    return bool(paths) and all(path.startswith(prefix) for path in paths)


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
        changed_path_args("diff", "--raw", "--no-abbrev", fork_point, ref, "--"), root
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
        output = run(changed_path_args("diff", "--numstat", base, ref, "--", *chunk), root)
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
    changed = run(changed_path_args("diff", "--name-only", f"{commit}^", commit, "--"), root)
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
    # On git's own line ends alone, never `splitlines()`: that also breaks at
    # `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, U+2028 and U+2029, and git prints
    # every one of them unchanged inside `%s`, so one pasted form feed read one
    # subject as two - the second opening with whatever id or `(#N)` followed
    # it (`PL-139L`).
    for line in listed.split("\n"):
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
    #: is how a ref is decided readable at all, and `claims.holdings` needs the
    #: same commit to test a branch's landed prefix against - asking git for it
    #: a second time could return a different answer about where the branch
    #: left from.
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


@dataclass(frozen=True)
class BranchFiles:
    """What one in-flight ref has actually changed since the default branch.

    `item_ids` is every item the in-flight report holds on this ref, so a
    reader told their file is being edited can also be told by whom. It may be
    empty in principle and is not in practice: a ref reaches here only because
    it holds an item, by a claim, a status disposition or its name.
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

    Kept out of `claims.holdings` deliberately. That read is on the hot path
    of `next`, `list`, `triage`, `status` and the session-start digest, and this
    one costs a `git diff` per unmerged ref - so it is paid by the two callers
    that ask the file question and by nobody else.

    A ref `claims.holdings` could not read is not read here either. Its
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
                    for line in run(
                        changed_path_args("diff", "--name-only", f"{base}...{name}"), root
                    ).splitlines()
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

    `item_ids` is every item this ref holds, all of them closed in the ref's
    own copy; `last_commit` is when it last moved, carried across from the
    holdings so a reader judging how long it has sat does not have to look it
    up separately. `claims.settled_branches` builds it: it reads the claims,
    which this module cannot import.
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

    Asked through the same `opened` that `claims.settled_branches` takes, and for the
    same reason: this package answers from a bare checkout with no network and
    knows nothing about GitHub, so the caller supplies the way to ask. It is
    asked only where a ref is carrying something, and a caller holding both
    readings passes one memoized callable to each so the forge is asked once.

    Unlike `claims.settled_branches`, it asks on every run that has a row to answer
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

    How old the refs behind it are is not a field here. This reads what the
    checkout holds and never fetches - the decision has to stay answerable
    from a bare checkout with no network - so a caller that did not refresh
    `origin/main` first gets an answer as stale as its last fetch, and saying
    so is the difference between a report and a guess. `Snapshot.fresh` says
    it, once for every report read from the same refs; the `fetched` field
    that repeated it here could disagree with it, and was retired (`PL-Z909`).

    `absent` separates the two shapes of "no position" that the session-start
    hook has always distinguished by staying silent. A detached HEAD, a
    checkout with no base, and the default branch itself with no remote copy
    are cases where *no comparison exists*, and a digest resent on every turn
    should not carry a line saying so. A clone that shares no readable history
    is the other shape: the comparison exists and could not be made, which is
    the one that has to be said out loud.

    It records that a refresh *arrived*, not merely that one was tried: since
    `PL-XBV4` the caller sets it from `fetch_remote`'s outcome, which reads
    git's exit status rather than its silent output, so a fetch that failed
    leaves this `False` and the report says what the refs rest on instead of
    reading as fresh.
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

    Only a leading id counts, for the reason `LEADING_IDS_RE` gives: a
    subject mentioning an item further in is usually bookkeeping about somebody
    else's work. Bounded, because a branch forked long ago would otherwise
    print a release's worth of ids into a digest line - the newest are the ones
    a session waiting on something wants.
    """
    output = run(["log", f"-n{limit}", "--format=%s", f"{fork}..{base}", "--"], root)
    found: list[str] = []
    # On `\n` alone, for the reason `change_landed` gives (`PL-139L`).
    for line in output.split("\n"):
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
    # On `\n` alone, for the reason `change_landed` gives: cut at a separator,
    # two different subjects share a key and this side's own work reads as the
    # base's (`PL-139L`).
    for line in output.split("\n"):
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


#: The remote every fetch here goes to, and the one a snapshot dates its refs by.
REMOTE = "origin"

# What a command did about the network before it read, as `Snapshot.fetch`
# carries it. Strings rather than an enum so a report can print one as it is,
# and so a test can assert the decision without matching prose (`PL-XBV4`).
#: This command refreshed the refs and the remote answered: the refs are now.
FETCHED = "fetched"
#: This command tried and the remote did not answer: the refs are whatever
#: the last fetch before it left, and `refs_at` says when that was.
FETCH_FAILED = "fetch failed"
#: The caller said not to (`--no-fetch`): the refs are as the last fetch left
#: them, dated by `refs_at` where the checkout records it.
UNFETCHED = "unfetched"
#: There is no `origin` to fetch from, so the refs are the checkout's own and
#: no fetch could make them fresher.
UNFETCHABLE = "no remote"
#: Git was asked nothing (`--no-git`), so no ref was read at all.
UNASKED = "unasked"


@dataclass(frozen=True)
class Fetch:
    """What one `fetch_remote` did, and when the refs it found were last refreshed.

    `refs_at` is read *before* the fetch, because a fetch that fails truncates
    `FETCH_HEAD` to nothing on its way out - measured against git 2.43 on
    2026-09-26 - and with it the only record the checkout keeps of when the
    refs were last refreshed. Read first, the moment survives the failure and
    the report can still say how old the refs it answered from are.
    """

    outcome: str
    refs_at: datetime | None = None


def _fetch_head_at(root: Path, run: Runner) -> datetime | None:
    """When this checkout last fetched, as `FETCH_HEAD` records it, or `None`.

    Git writes `FETCH_HEAD` on every fetch that reaches the remote - a fetch
    that found nothing new still lists the refs it compared - and truncates it
    to nothing on one that did not, so an empty file is the trace of a failed
    attempt and dates nothing. A clone writes no `FETCH_HEAD` at all, so its
    absence means no fetch since the clone. Asked through `--git-path` rather
    than `.git/FETCH_HEAD`, because a worktree's `.git` is a file.
    """
    where = run(["rev-parse", "--git-path", "FETCH_HEAD"], root).strip()
    if not where:
        return None
    path = Path(where)
    if not path.is_absolute():
        path = root / path
    try:
        stat = path.stat()
    except OSError:
        return None
    if stat.st_size == 0:
        return None
    return datetime.fromtimestamp(stat.st_mtime, UTC)


def fetch_remote(root: Path, *, runner: Runner | None = None) -> Fetch:
    """Refresh the remote-tracking refs, and say whether the remote answered.

    The one read in this module that goes to the network, kept apart from the
    rest for exactly that reason: a caller that must not touch it simply does
    not call this. Every branch tip rather than `main` alone, and deliberately
    not `--prune` - a branch deleted on the remote leaves a tracking ref that
    is the only surviving copy of anything committed on it, which is the case
    `stranded` exists to catch.

    **Its result is the answer, not a side effect** (`PL-8Z1T`, `PL-XBV4`).
    This returned nothing and swallowed the exit status, so a checkout whose
    fetch failed - no network, a remote gone - was reported on by `branch` as
    `current with origin/main` and by `stranded` with recovery commands and no
    caveat, on refs as old as the last fetch that worked. `_run_git` has told a
    failure from an empty answer since `PL-Q9Z1`, so the outcome is read off
    the runner: `FETCHED` where the remote answered, `FETCH_FAILED` where it
    did not, `UNFETCHABLE` where there is no `origin` to ask. Where nothing is
    configured the fetch is not tried, because git's refusal there is an
    answer about the checkout and not about the network.
    """
    run = runner or _run_git
    if REMOTE not in _remotes(root, run):
        return Fetch(UNFETCHABLE)
    before = _fetch_head_at(root, run)
    if answered(run(["fetch", "--quiet", REMOTE], root)):
        return Fetch(FETCHED, before)
    return Fetch(FETCH_FAILED, before)


@dataclass(frozen=True)
class Snapshot:
    """Which moment a read command answered from (`PL-XBV4`).

    Every read command assembled its own picture of the world: the store from
    the working tree, holds from refs some command had fetched and some had
    not, a failed fetch discarded, so each answered from a different moment and
    none said which. This is the one record of that moment, built once per
    command and read by every read beneath it, so a stale answer cannot pass
    for a fresh one in any command without passing in all of them.

    `fetch` is what the command did about the network, one of the five
    outcomes above. `refs_at` is when the remote-tracking refs were last
    refreshed, where the checkout records it: `now` after a fetch that
    answered, the last fetch's moment where none was tried or this one failed,
    and `None` where nothing dates them - a clone nothing has fetched since,
    or a checkout with no remote. `branch` is where the working tree stands
    against the default branch, read against the same refs, so the store the
    command reads from the working tree and the refs it reads holds from are
    placed relative to each other in the same breath.

    The forge - which branches have a pull request open, merged or closed - is
    not here, on a decision recorded in `PL-XBV4`: one command asks it, the
    lookup has an eight-second timeout that every other command would then
    pay, and the two members that wanted it moved to heads of their own.

    `declined` carries the meaning it has everywhere in this module: the read
    was partial, and why.
    """

    fetch: str = UNASKED
    refs_at: datetime | None = None
    branch: BranchState = field(default_factory=BranchState)
    declined: str = ""

    @property
    def fresh(self) -> bool:
        """Whether this command's own fetch is what the refs rest on."""
        return self.fetch == FETCHED


def snapshot(
    root: Path, *, now: datetime, fetch: Fetch | None = None, runner: Runner | None = None
) -> Snapshot:
    """The moment a command is answering from, read against what the checkout holds.

    `fetch` is what the command did about the network before asking, and
    `None` says it did nothing - `--no-fetch` - so the refs are dated here from
    `FETCH_HEAD`. **It never fetches itself**: the command fetches and the
    function does not, which is the rule every read in this module follows and
    the reason `fetch_remote` is a separate call.

    `now` is the caller's instant rather than the clock, for `holdings`'
    reason: an age is a subtraction, and a read that took the clock itself
    could not be replayed.

    A silence beneath any of the reads here marks the whole answer partial,
    the branch position included, exactly as `branch_state` marks its own.
    """
    run = _Silences(runner or _run_git)
    outcome = UNFETCHED if fetch is None else fetch.outcome
    if outcome == UNFETCHED and REMOTE not in _remotes(root, run):
        outcome = UNFETCHABLE
    if outcome == FETCHED:
        refs_at: datetime | None = now
    elif outcome == FETCH_FAILED:
        refs_at = fetch.refs_at if fetch is not None else None
    elif outcome == UNFETCHED:
        refs_at = _fetch_head_at(root, run)
    else:
        refs_at = None
    branch = _branch_state(root, run)
    if run.reason:
        return Snapshot(
            fetch=outcome,
            refs_at=refs_at,
            branch=replace(branch, absent=True, declined=run.reason),
            declined=run.reason,
        )
    return Snapshot(fetch=outcome, refs_at=refs_at, branch=branch)


def branch_state(root: Path, *, runner: Runner | None = None) -> BranchState:
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
    decision, so refreshing `origin/main` is the caller's, and whether it did
    is `Snapshot.fresh`'s to say (`PL-Z909`). What is reported is therefore
    stale by exactly one fetch at worst, which is an acceptable error for a
    report and would be an unacceptable one for a claim.

    **A silence outranks whatever the body concluded while git was quiet**
    (`PL-Q9Z1`). This declined under a total git failure before the channel
    existed, which looked like compliance and was not: it declined saying "no
    branch is checked out here", and no branch being checked out is a claim
    about the repository that nothing had established. A wrong reason on a
    correct refusal is still the floor breached, because a reader acts on the
    reason - here by looking for a branch that is in fact there.
    """
    run = _Silences(runner or _run_git)
    state = _branch_state(root, run)
    if run.reason:
        return replace(state, absent=True, declined=run.reason)
    return state


def _branch_state(root: Path, run: Runner) -> BranchState:
    """`branch_state`'s reading, against a runner whose silences are watched."""
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    if not branch or branch == "HEAD":
        return BranchState(
            absent=True, declined="no branch is checked out here, so there is nothing to compare"
        )

    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return BranchState(
            branch=branch, absent=True, declined=f"this checkout has no {base} to compare against"
        )

    # The default branch with no remote copy of it: `default_base` fell all the
    # way back to the local branch, which is the one already checked out, and
    # comparing a ref with itself answers nothing. Distinct from being current,
    # because there is no other side to have moved.
    if base == branch:
        return BranchState(
            branch=branch,
            base=base,
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
            branch=branch, base=base, absent=True, declined="git would not count the two sides"
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
    )


@dataclass(frozen=True)
class BaseCopy:
    """The default branch's copy of one item it changed after this checkout forked (`PL-Y48N`).

    A read command takes the store from the working tree and the holds from
    refs its own fetch has just refreshed, and since `PL-XBV4` it says which
    moment the refs are from - but a working tree behind `origin/main` still
    holds every item as it stood at the fork. So `next` offered, and `show`
    called ready, an item another session had closed and merged since, and
    `claim` pushed a claim its own read-back then found dead. This is the newer
    copy, read from the base through the command's runner, and `supersedes`
    says whether it is the one to answer from.
    """

    identifier: str
    #: Its path on the base, which a retitle can have moved.
    path: str
    #: The base's copy, whole.
    text: str
    #: Whether this checkout changed the item after the fork as well, committed
    #: on the branch or only in the working tree.
    changed_here: bool = False

    @property
    def status(self) -> str:
        """The `status:` the base's copy records."""
        return parse_front_matter(self.text)[0].get("status", "")

    def supersedes(self, here: str) -> bool:
        """Whether this copy is the one to answer from, given the status read here.

        Where only the base changed the item, its copy is the newer one and
        nothing in this checkout adds to it. Where this checkout changed it
        too, the checkout's own edit stands - it is work the base has not seen
        - except over a closure: `claims.holdings` releases every claim on an
        item the base has closed, whatever the branch's copy says, so
        answering from the branch's copy there offers an item no claim on can
        hold.
        """
        if not self.changed_here:
            return True
        return self.status in CLOSED_STATUSES and here not in CLOSED_STATUSES


@dataclass(frozen=True)
class BaseCopies:
    """The items the default branch changed after this checkout forked, or why that is unread."""

    base: str = ""
    #: Each such item's copy on the base, by id.
    copies: Mapping[str, BaseCopy] = field(default_factory=dict)
    declined: str = ""

    def of(self, identifier: str) -> BaseCopy | None:
        """The base's copy of `identifier`, where the base changed it after the fork."""
        return self.copies.get(identifier.upper())


def base_copies(
    root: Path,
    base: str,
    *,
    items_dir: str = "docs/items",
    keys: Collection[str] | None = None,
    runner: Runner | None = None,
) -> BaseCopies:
    """The items `base` changed after `HEAD` forked from it, each with the base's copy.

    A three-dot diff, as `_changed_items` reads this checkout's side, so what
    the base changed is measured from where `HEAD` left it and a file only
    this branch touched is not counted as the base's. A checkout current with
    the base gets nothing, since the diff is then empty, so a caller already
    told it is not behind need not ask. `keys` narrows the copies read to the
    ids a caller asked about, which is all `claim` needs.

    By id rather than by path, for the reason `records_on_base` gives: a
    retitle renames the file, and the base's copy is read from wherever the
    base keeps it.

    A silence marks the answer partial rather than empty, `_Silences`' rule: a
    diff git would not give reports no newer copy, and `declined` says so.
    """
    run = _Silences(runner or _run_git)
    listing = run(changed_path_args("diff", "--name-only", f"HEAD...{base}", "--", items_dir), root)
    moved = _item_ids(listing)
    if keys is not None:
        moved &= {key.upper() for key in keys}
    if not moved:
        return BaseCopies(base=base, declined=run.reason)
    here = {key.upper() for key in _changed_items(root, base, items_dir, run)}
    paths = _item_paths_on(base, items_dir, root, run)
    copies: dict[str, BaseCopy] = {}
    for key in sorted(moved):
        path = paths.get(key, "")
        text = run(["show", f"{base}:{path}"], root) if path else ""
        if text:
            copies[key] = BaseCopy(identifier=key, path=path, text=text, changed_here=key in here)
    return BaseCopies(base=base, copies=copies, declined=run.reason)


def _item_ids(listing: str) -> set[str]:
    """The item ids a `--name-only` listing names, by the store's file names."""
    found: set[str] = set()
    # On `\n` alone, for the reason `change_landed` gives (`PL-139L`).
    for line in listing.split("\n"):
        path = line.strip()
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1]) if path else None
        if match is not None:
            found.add(match.group(1).upper())
    return found


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
            *changed_path_args(
                "log",
                "--no-merges",
                f"--since={filed.isoformat()} 00:00:00 +0000",
                "--format=%x1f%H",
                "-z",
                "--name-status",
                "HEAD",
                "--",
                *touches,
            ),
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
    `HEAD` contains the ref's tip rather than by comparing names, because a
    name matches the local branch alone and never its tracking ref or a branch
    pushed under a third name - and a session told to yield to itself would
    stop for nobody.

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
    items' `milestone:`, so a read of ids alone is blind to the widest write
    in the repository, and two sessions cut v0.3.7
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
                    changed_path_args(
                        "diff", "--name-only", f"{base}...{ref}", "--", f"{notes_dir}/"
                    ),
                    root,
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


@dataclass(frozen=True)
class Cut:
    """The commit a release was cut on, as one ref's history records it.

    `commits` is every commit the lookup named, newest first: one where the
    notes were added once, none where the ref never carried them, several where
    they were added, deleted and added again. `declined` says why nothing was
    read, as `TagSet`'s does, so "no cut on this ref" and "could not look" stay
    two answers.
    """

    commits: tuple[str, ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def commit(self) -> str:
        """The cut, or `""` unless git answered with exactly one commit."""
        return self.commits[0] if self.known and len(self.commits) == 1 else ""


def find_cut(version: str, ref: str, root: Path, *, runner: Runner | None = None) -> Cut:
    """The commit that cut `version`, read from `ref` by `release.cut_query`.

    Ask it of the default branch or of a tag, never of a branch's `HEAD`:
    `release.CUT_FLAGS` says why. **A shallow clone can name the wrong
    commit**: its oldest fetched commit reads as a root, adding every file in
    its tree, so a cut older than the clone's depth is reported as that commit.
    A caller that prints the answer asks `is_shallow` first.
    """
    run = runner or _run_git
    query = cut_query(version, ref)
    text = run(query, root)
    if not answered(text):
        return Cut(declined=f"git did not answer `git {' '.join(query)}`")
    return Cut(commits=tuple(line.strip() for line in text.splitlines() if line.strip()))


def notes_added(
    commits: Collection[str], root: Path, *, runner: Runner | None = None
) -> dict[str, frozenset[str]] | None:
    """The release notes each commit added, compared with its first parent.

    `release.CUT_FLAGS` applied to named commits, all in one `git log
    --no-walk` rather than one lookup each: 11 ms for this repository's 74
    tags against 1.29 s (measured 2026-09-26). Every commit asked about is a
    key, holding an empty set where it added none; `commits` are full hashes,
    since that is how git names them back. `None` where git did not answer,
    which a caller must not read as "added nothing".

    Truncation can only add to the answer, never take from it: a shallow
    clone's oldest commit reads as adding everything in its tree, so a commit
    reported as adding nothing did add nothing.
    """
    if not commits:
        return {}
    run = runner or _run_git
    text = run(
        [
            "log",
            "--no-walk",
            *CUT_FLAGS,
            "--format=%x00%H",
            "--name-only",
            *commits,
            "--",
            NOTES_DIR,
        ],
        root,
    )
    if not answered(text):
        return None
    added: dict[str, set[str]] = {commit: set() for commit in commits}
    for block in text.split("\0")[1:]:
        commit, _, paths = block.partition("\n")
        added.setdefault(commit.strip(), set()).update(
            line.strip() for line in paths.splitlines() if line.strip()
        )
    return {commit: frozenset(paths) for commit, paths in added.items()}


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
    # On `\n` alone, for the reason `change_landed` gives (`PL-139L`).
    for subject in subjects.split("\n"):
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
    # On `\n` alone, for the reason `change_landed` gives (`PL-139L`).
    for line in log.split("\n"):
        if line.startswith("\x00"):
            commit, _, subject = line[1:].partition("\x01")
            continue
        if not commit or not line.strip() or not line.split("\t")[0].startswith("A"):
            continue
        path = line.split("\t")[-1]
        match = ITEM_FILE_RE.match(path.rsplit("/", 1)[-1]) if path.startswith(prefix) else None
        if match is not None:
            filed.setdefault(match.group(1), (commit, subject))

    found: dict[str, FilingCommit] = {}
    for item_id in sorted(item_ids):
        entry = filed.get(item_id)
        if entry is None or item_id not in leading_ids(entry[1]):
            continue
        commit, subject = entry
        changed = run(changed_path_args("show", "--format=", "--name-only", commit), root).split()
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

    *Which pull request* landed a closure is not read from history at all, any
    more. The number is recorded before the merge by the branch that closes
    the item, and the pull request's own required check refuses a closure that
    does not carry it (`PL-HMZZ`). This once derived it afterwards, from the
    merge subjects on the base and then from each item file's own history, and
    every new shape of history - a rider id that led no subject, a rename, a
    closure split from its work, a queue-only closure, a graft boundary -
    misled one reading or the other until it got an exception of its own: ten
    items in three weeks were that one mechanism. So the only question left
    about a landed closure is what the base's own copy of the item records,
    which is the same tree read, and `recorded` carries it: a checkout holding
    a stale copy of an item is not told the number is missing when the base
    already has it.

    `unlanded` is the other half of the answer, and `_check_provenance` reads
    it. A closure this checkout holds that the base does not yet is the one
    whose recorded number names a pull request the base has not merged - by
    construction rather than by mistake, since the branch wrote its own open
    pull request's number there.
    """

    base: str = ""
    landed: frozenset[str] = frozenset()
    #: The closures asked about that do not read `done` on the base: still in
    #: flight, on this branch.
    unlanded: frozenset[str] = frozenset()
    #: The `pr` the base's own copy records, for each landed closure that
    #: records one. Pairs rather than a mapping to keep the type hashable like
    #: everything else here; `numbers` unpacks it.
    recorded: tuple[tuple[str, int], ...] = ()
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined

    @property
    def numbers(self) -> dict[str, int]:
        return dict(self.recorded)


def closures_on_base(
    root: Path,
    closures: Mapping[str, str],
    *,
    items_dir: str = "docs/items",
    runner: Runner | None = None,
) -> ClosureReport:
    """Which of `closures` read `status: done` on the default base, and what each records there.

    `closures` maps an item id to the file name that holds it, and is expected
    to carry only the items whose closure is in question: each one costs a
    `git show`, and the caller is the one that knows which those are.

    An item absent from the base is a closure that has not landed, which is
    the whole point rather than a failure to read it. One whose file the base
    holds under another name is read at that name: retitling an item renames
    its file, so the old path stops resolving, and the ids the base holds are
    one `ls-tree` away - paid only when a name fails to resolve, which on a
    healthy store is never. Reading a renamed closure as unlanded was safe
    while nothing wrote on the strength of it; `docket record N` now does, and
    would have replaced a landed closure's number with the branch's own.
    """
    run = _Silences(runner or _run_git)
    base = default_base(root, runner=run)
    if not run(["rev-parse", "--verify", "--quiet", base], root).strip():
        return ClosureReport(declined="no default branch this checkout can read")
    landed: set[str] = set()
    recorded: dict[str, int] = {}
    held: dict[str, str] | None = None
    for identifier, name in closures.items():
        path = f"{items_dir}/{name}"
        text = run(["show", f"{base}:{path}"], root)
        if not text:
            if held is None:
                held = _items_at(base, root, items_dir, run)
            elsewhere = held.get(identifier)
            if elsewhere is None or elsewhere == path:
                continue
            path, name = elsewhere, elsewhere.rsplit("/", 1)[-1]
            text = run(["show", f"{base}:{path}"], root)
            if not text:
                continue
        item = parse_item(text, name)
        if item.status != "done":
            continue
        landed.add(identifier)
        if item.pr and item.pr.isdigit():
            recorded[identifier] = int(item.pr)
    return ClosureReport(
        declined=run.reason,
        base=base,
        landed=frozenset(landed),
        unlanded=frozenset(closures) - frozenset(landed),
        recorded=tuple(sorted(recorded.items())),
    )


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

    How old the *comparison point* is belongs to the answer for the same
    reason `refs_read` does. Every finding here rests on the default branch
    not holding the item, so a base nobody refreshed reports whatever merged
    since the last fetch as lost. That is not hypothetical:
    `PL-XLQ5` merged at 01:13 on 2026-09-05, this checkout's `origin/main` was
    from 01:05, and at 01:16 the item read as stranded and the recovery command
    restored its pre-triage copy over the triaged one the merge had just landed
    (`PL-KBFN`). The deleted remote branch corroborated nothing - a merge
    deletes the branch too - so freshness is the whole of what separates a hole
    from a merge.

    It is not a field here, for `BranchState`'s reason: `Snapshot.fresh` says
    whether a refresh *arrived*, from `fetch_remote`'s outcome, once for every
    report read from those refs, so a fetch that failed reads as one and the
    report says what the refs rest on (`PL-XBV4`). The `fetched` field that
    copied it could disagree with it, and was retired (`PL-Z909`).
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
        for line in run(
            changed_path_args("diff", "--name-only", revision, "--", items_dir), root
        ).splitlines():
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
    It asks the question of one commit, and needs no subject to parse because
    the caller already has the number: `docket record N --merge SHA`, for a
    closure that reached the base without one (`PL-HMZZ`).

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
    two readings that once derived a closure's number from history, which
    asked the same question without this guard until `PL-KX9N`; they are gone
    since `PL-HMZZ` retired the inference, and `_parent_in_reach` stays here
    as the one place the question is asked.
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
    listing = run(
        changed_path_args("diff", "--name-only", f"{revision}^", revision, "--", items_dir), root
    )
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
    root: Path, known_ids: set[str], *, items_dir: str = "docs/items", runner: Runner | None = None
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

    **It never fetches, and takes no word for whether anything did.** The rule
    the rest of this module follows - a read that must work from a bare
    checkout with no network - applies here too, so refreshing the base is
    `cmd_stranded`'s and it is not optional there: every finding is a claim
    about what the base does *not* hold, and that claim is only as old as the
    last fetch. `Snapshot.fresh` carries what happened into the output
    (`PL-Z909`).

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
        return StrandedReport(declined="no branch refs this checkout can read")

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
            else f"no items found on {base}, so every branch would read as stranding its own"
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
        items=tuple(found), edits=tuple(edits), base=base, refs_read=len(refs), declined=run.reason
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

    `_annotates_only` is the test, which is the reading the in-flight read
    applied to the same commits, for the same reason, until the claim record
    replaced it: a capture, a triage pass, a recovered item and a `record` write all
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
    # Not `changed_path_args`: each commit's paths are matched against
    # `_landing_split`'s, which holds only the paths a change puts content at,
    # so a rename's deleted side would match neither set and leave the commit
    # unclassified (`PL-KR69`).
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
    distinct: set[str] = set()
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
            for line in run(
                changed_path_args("diff", "--name-only", fork, name, "--", prefix), root
            ).splitlines()
            if line.strip()
        ]
        walked.append((name, int(ahead) if ahead.isdigit() else 0, len(touched)))
        distinct.update(touched)
    return RefWalk(
        listed=len(listing),
        merged=len(merged),
        unmerged=len(walked) + len(unread),
        commits=sum(ahead for _, ahead, _ in walked),
        item_edits=sum(edits for _, _, edits in walked),
        item_files=len(distinct),
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
        changed_path_args("diff", "--name-only", f"{base}...HEAD"),
        changed_path_args("diff", "--name-only", "HEAD"),
        ["ls-files", "--others", "--exclude-standard"],
    ):
        found.update(line.strip() for line in run(args, root).splitlines() if line.strip())
    return WorkingPaths(paths=tuple(sorted(found)), base=base, declined=run.reason)
