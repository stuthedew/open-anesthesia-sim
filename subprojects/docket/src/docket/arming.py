"""Whether a pull request may be armed for auto-merge: `bin/docket arm`'s answer for `HEAD`.

`CLAUDE.md` arms a pull request whose branch carries only item files, so a
capture reaches the default branch even when its session ends before any work
does (project owner, 2026-09-23, ratified, over "a branch carrying only
captured items is not a pull request", `PL-WNCT`). Which pushes could be armed
was a catalog of claim shapes each session applied by judgment - the empty
start commit, a queue-only commit start mode read as one - and every shape it
missed merged a claim away with its branch while the work went on (`PL-QP9Z`,
`PL-1MCK`, `PL-KWCY`). A claim is a recorded fact now (`claims`), so the
question is decided here, from the tree, and asked before arming and before
every later push while a pull request is open.

**Five answers, and an exit status for each.**

- `arm` (0): the net change a squash would land - `base...HEAD` - reaches
  nothing on the owner's read list (`READ_PATHS`, a test of the tooling under
  `tests/` aside) and leaves this module alone, which `arms_on_green` answers
  path by path; no claim bound to this
  branch is unreleased; HEAD holds every commit of the branch's copy on the
  remote; and the branch contains the base's tip. A path outside the store,
  the queue's own tooling, `subprojects/docket/`, and the pull requests'
  recovered bodies, `docs/pr-bodies/`, is named beside the answer: the owner's
  rule arms it on green unless the change raises a question for them, which
  stays the session's judgment, and asks for the reason in the report.
- `hold` (1), naming what holds it. A claim holds the pull request unarmed and
  a draft, whichever push carried it, until the branch's own copy closes or
  blocks the item or the branch yields it: merged, the branch and its claim go
  together while the work goes on. A lapsed claim is unreleased too - it is
  work nobody finished or handed back. A path on the owner's read list holds
  it unarmed, and so does a change to this module, because that work waits on
  a read rather than merging on green CI, and merges on the owner's word
  alone. Once no claim holds it, that hold also says where the ask for the
  read goes and what it carries (`READ_ASK`).
- `behind N` (1): nothing holds it, but the base has `N` commits the branch
  lacks, and `main` merges only an up-to-date branch while auto-merge never
  brings the base in (`PL-S5MF`). So the base is brought in first.
- `landed` (1): the forge says the branch's newest pull request has merged,
  and HEAD still stands on the head it merged at (`vcs.carried_merge`), so
  there is nothing to arm. Whatever came after that head is carried onto the
  base by a restart and a new pull request (`PL-8BR0`).
- `unknown` (2): something the answer rests on could not be read - no branch,
  no established base, a history git would not walk, a claim trailer that
  does not parse, a fetch that failed, a forge that could not say whether the
  pull request merged - or the branch's copy on the remote holds commits HEAD
  lacks, so HEAD is not what its pull request lands. Never `arm` from a
  partial read.

**`hold` outranks `unknown`.** A claim or a path that waits on a read is
reason enough whatever else went unread, so it is said, with what went unread beside
it, rather than withheld. Commits the remote's copy holds and HEAD lacks are
said first under either, since everything else was read from HEAD (`PL-21KN`).
**`landed` outranks every other answer**, since a claim, a path, a base that
moved or a remote copy HEAD lacks changes nothing about a pull request that
has already merged; what went unread is said beside it.

**The decisions the rule rests on**, moved here from `CLAUDE.md` with it:

- a claim holds whichever push carried it (project owner, 2026-09-23,
  ratified, over arming whatever rode the push, `PL-QP9Z`, and over reading
  only a start claim on that push, `PL-1MCK`);
- it holds until the item closes in the branch's own copy and not past it
  (same date, ratified, over holding it past the item's closing, `PL-KWCY`),
  and a block releases it too (2026-09-24, ratified, over holding it until
  closed, `PL-3FYK`) - `claims.RELEASING_STATUSES`;
- a pull request a claim rides is a draft (2026-09-24, ratified, over opening
  none while a claim rides or titling it as the capture, because `#978` was
  merged by hand while its claim was open, `PL-H14W`);
- the tooling arms on green beside the store, and everything else waits on a
  read, this module included (2026-09-25, ratified, over holding every path
  outside the store, `PL-SQTR`, built by `PL-K6B2`): the hold fired on every
  docket change and was clicked through, so it guarded nothing, the simulator
  included. This module stays held so that the gate cannot loosen itself;
- a body record arms on green beside them (2026-09-25, ratified with the
  record's form, over every pull request holding on the record it writes
  before its merge, `PL-979D`): the record is a copy of the body, never a
  change to read;
- only the owner's read list waits on a read - `src/`, `tests/` outside
  `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/`, `README.md`
  and this module - and every other path arms on green, named beside the
  answer, unless the change raises a question for the owner (the Projects
  trial's instructions, 2026-10-03, kind unrecorded, over holding every path
  outside the store, the tooling and the records; built by `PL-KKHD`). The
  rule was written there alone, so on one day `#1298` armed under it while
  `#1308` held under the old one. It reopened `PL-0JGZ` (project owner,
  2026-09-26, ratified), which kept `ROADMAP.md` and `docs/WORKING_NOTES.md`
  off what arms because the roadmap is where the owner sets direction:
  neither is on the list, so both arm, and the owner settled it so (project
  owner, 2026-10-03, ratified, over holding them as before). `.github/workflows/`
  and `.claude/hooks/` joined the list the same day, since they decide merges
  and tags as this module does (project owner, 2026-10-03, ratified, over
  leaving them armed on green; `PL-KKHD` records both answers);
- a test of the tooling under `tests/` - a file pytest collects that imports
  no `anesthesia_sim` on either side of the change - arms on green, as
  `subprojects/docket/tests/` does, and the rest of `tests/` stays on the list
  (project owner, 2026-10-05, ratified, over keeping every change under
  `tests/` on the read list; built by `PL-552M`). Since 2026-10-03, 16 of the
  51 merges held for a read had been held by such tests alone, every
  `PL-R417` slice among them, so the hold asked for reads with nothing to
  judge, the click-through that retired the hold on the tooling (`PL-SQTR`).
  The import rule is the one `tools/workflow_paths_check.py` holds
  `docket.toml`'s `workflow_paths` to, spelt here and imported there, and it
  is read from the tree rather than from `workflow_paths`, which arms on
  green: widening what arms still takes an edit the gate holds (`PL-0JGZ`).

Status dispositions and release cuts never hold arming (`PL-MB2W` § "Other
holds"): a triage pass moving statuses is the queue-only work auto-merge
exists for, and a cut's notes file lies outside the store and the tooling,
so the paths hold it already.
"""

from __future__ import annotations

import ast
import fnmatch
import platform
from collections.abc import Callable, Collection, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from .claiming import _git
from .claims import LAPSED, RELEASED, Hold, holdings
from .vcs import (
    REMOTE,
    MergedPullRequest,
    PullRequestLookup,
    RemoteHeads,
    Runner,
    _head_name,
    _remotes,
    _run_git,
    _Silences,
    answered,
    carried_merge,
    changed_path_args,
    default_base,
    listed_paths,
    remote_heads,
    resolved,
)

#: The five answers, each the first word of what `arm` prints.
ARM = "arm"
HOLD = "hold"
BEHIND = "behind"
LANDED = "landed"
UNKNOWN = "unknown"

#: The exit status of each answer. `behind` and `landed` share `hold`'s: all
#: three say "not now", and the line printed says which.
EXIT = {ARM: 0, HOLD: 1, BEHIND: 1, LANDED: 1, UNKNOWN: 2}

#: How many paths outside the store, the tooling and the records a `hold`
#: names before counting the rest.
SHOWN = 5

#: What a `hold` for a read tells the session to put in the owner's ask, once
#: no claim keeps the pull request a draft. The owner asked for it as the
#: default for every pre-merge read on 2026-09-27, and only the Projects
#: instructions carried it, so a session outside the Project asked for the
#: read without one (`PL-8XQS`). It is said here, where the ask is decided,
#: rather than in a resident rule every session pays for.
#:
#: It names the closing block's line because its first wording said what the
#: ask *opens* with, and was followed to the letter: on 2026-10-03 three
#: sessions opened the reply with the summary and closed it on a bare "read
#: #N", the line the owner acts on, with housekeeping among the points
#: (`PL-9KHK`). The points run most important first because the owner's need
#: is not less to see but what matters in it made plain: "it's just hard to
#: know what's important in long text" (project owner, 2026-10-03).
READ_ASK = (
    "  Ask for this read in the closing block's own line, never as 'read #N', and repeat that "
    "line whole in every later reply that still waits on it, short enough to take in at a "
    "glance: a plain-language summary, one sentence of what the change does, what was wrong "
    "and what changed, in terms a clinician recognises; then numbered points for the owner "
    "to judge, most important first and only what matters to them - a clinical value or a "
    "docs/MODEL.md statement, what a learner sees, how sessions work, a departure from what "
    "they asked for, a risk to what already works; then what needs no review, in one "
    "clause, which is where housekeeping goes - tests, docstrings, filed items, audit notes, "
    "the apparatus's internals. With no point to judge, say so and ask for the merge word "
    "alone."
)

#: The queue's own tooling, which arms on green beside the store. The path is
#: this repository's layout.
TOOLING = "subprojects/docket/"

#: The pull requests' body files, which arm on green beside the store and the
#: tooling: `tools/pr_body_check.py --recover` writes one for a squash commit
#: that landed with no body, and a copy of a body is never a change to read
#: (`PL-3PH2`). `verify` sanctions the same write as `record`. The path is this
#: repository's layout, as `TOOLING`'s is.
RECORDS = "docs/pr-bodies/"

#: The one file under `TOOLING` that still waits on a read: this module, which
#: decides the answer, so a change to it could loosen the rule it states.
#: `test_cli` pins it to the module's own path, so a move cannot leave it
#: naming a file nothing reads.
GATE = TOOLING + "src/docket/arming.py"

#: The simulator's tests, at the root: `subprojects/docket/tests/` starts with
#: `subprojects/`, so the prefix leaves it to the tooling.
TESTS = "tests/"

#: Importing this is what makes a test file the simulator's. It is the rule
#: `tools/workflow_paths_check.py` holds `docket.toml`'s `workflow_paths` to
#: (`PL-JBZK`), and since 2026-10-05 the one that lets a test under `TESTS`
#: arm on green (`PL-552M`). Spelt here, in the module the gate holds, and
#: imported by the lane check, so the two read one rule and neither can
#: change it without an edit that waits on the owner's read.
PRODUCT_PACKAGE = "anesthesia_sim"

#: What pytest collects as a test module: its default `python_files`, which
#: this repository does not override. Restated rather than read, and
#: `tests/unit/test_workflow_paths_check.py` compares it with the setting its
#: own run collected under, so a changed `python_files` fails a test instead
#: of quietly turning a new test into a support module.
TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")

#: The owner's read list, spelt as they spelt the rule (2026-10-03, `PL-KKHD`):
#: a change reaching one of these waits on their read, the gate beside them,
#: and everything else arms on green. A directory holds what is under it, a
#: file is itself. `TESTS` is the simulator's, but for a test of the tooling
#: (`tests_the_tooling`), which arms on green since the owner's answer of
#: 2026-10-05. `src/anesthesia_sim/data/` lies under `src/` and is kept for
#: the reader who looks for it by name. `.github/workflows/` and
#: `.claude/hooks/` decide merges and tags as this module does, and joined on
#: the owner's answer of 2026-10-03.
READ_PATHS = (
    "src/",
    TESTS,
    "docs/MODEL.md",
    "src/anesthesia_sim/data/",
    "README.md",
    ".github/workflows/",
    ".claude/hooks/",
)

#: The list as the answers name it, the gate included.
READ_LIST = (
    f"src/, {TESTS} but a test importing no {PRODUCT_PACKAGE}, docs/MODEL.md, "
    "src/anesthesia_sim/data/, README.md, .github/workflows/, .claude/hooks/ and arming.py"
)


def imported_modules(tree: ast.Module) -> set[str]:
    """Every module name one file imports, in either import form.

    `ast` rather than a regular expression because the question is about
    imports and not about text: a package named in a docstring, in a fixture
    path or in a comment is not a dependency, and several of the apparatus
    tests here write `src/anesthesia_sim/...` as fixture data precisely because
    they check tools that read the tree.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def imports_product(tree: ast.Module) -> bool:
    """Whether a file imports the simulator, which makes any file under `tests/` the simulator's."""
    return any(
        module == PRODUCT_PACKAGE or module.startswith(PRODUCT_PACKAGE + ".")
        for module in imported_modules(tree)
    )


def is_test_file(name: str) -> bool:
    """Whether pytest collects a file of this name, rather than it supporting what it collects."""
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in TEST_FILE_PATTERNS)


def tests_the_tooling(path: str, sides: Iterable[str]) -> bool:
    """Whether a change to `path` is a change to a test of the tooling, which arms on green.

    A test file under `TESTS` - one pytest collects - whose source on every
    side of the change imports no `PRODUCT_PACKAGE` (project owner,
    2026-10-05, ratified, over keeping every change under `tests/` on the
    read list, `PL-552M`). `sides` is the file's source at the merge base and
    at HEAD, `""` for a side holding no such file, so a change that drops a
    test's simulator import, or deletes a simulator test, still waits.

    A support module never is, whatever it imports: what a module pytest does
    not collect imports decides nothing about whose it is (`PL-12P8`), and
    `tests/conftest.py`, importing nothing, serves the simulator's tests. Nor
    is a file that is not Python.

    Raises what `ast.parse` raises on a side that will not parse -
    `SyntaxError`, or `ValueError` for a null byte under Python 3.11 - which
    `arm` says beside the hold it then gives.
    """
    if not path.startswith(TESTS) or not is_test_file(PurePosixPath(path).name):
        return False
    return not any(imports_product(ast.parse(side, filename=path)) for side in sides)


def waits_on_read(path: str, tooling: Collection[str] = ()) -> bool:
    """Whether a change to `path` waits on the owner's read: the read list, or the gate.

    `tooling` is the paths under `TESTS` that `tests_the_tooling` read as
    tests of the tooling, on both sides of the change, which arm on green. A
    name alone cannot say so, so a path under `TESTS` nobody read waits, and
    `tooling` clears nothing outside `TESTS`.
    """
    if path == GATE:
        return True
    if path in tooling and path.startswith(TESTS):
        return False
    return any(
        path == entry or (entry.endswith("/") and path.startswith(entry)) for entry in READ_PATHS
    )


def arms_on_green(path: str, tooling: Collection[str] = ()) -> bool:
    """Whether a change to `path` may merge on green CI without the owner's read.

    Everything but the owner's read list and `GATE` may (the Projects trial's
    instructions, 2026-10-03, kind unrecorded, over holding every path outside
    the store, the tooling and the records, `PL-SQTR`; built by `PL-KKHD`),
    and so may a test of the tooling under `TESTS`, named in `tooling`
    (project owner, 2026-10-05, ratified, `PL-552M`). `arm` holds a branch
    for each path this answers no to, and names beside an `arm` each path
    `outside_the_store` answers yes to, since the owner's rule arms those only
    while the change raises no question for them - a judgment this module
    does not make - and asks for the reason in the report.

    It is not `claims.in_queue`, which asks whether a change owes a claim and
    counts the roadmap and the notes as queue records, since a triage pass and
    a design round write them and nothing else (`PL-3CTW`). The two answers
    were kept apart on purpose: `ROADMAP.md` and `docs/WORKING_NOTES.md` owe
    no claim, and until 2026-10-03 still waited on a read (project owner,
    2026-09-26, ratified, over treating them as queue records here,
    `PL-0JGZ`), because the roadmap is the milestone map the owner sets
    direction in. The owner's read list leaves both off, so they arm now;
    `PL-KKHD` records the reopening. The rule is spelt here, in the one
    module the gate holds, rather than beside `in_queue`, so that widening
    what arms still takes an edit the gate holds (2026-09-26, ratified, over
    two named predicates in `claims`, `PL-0JGZ`), as `RECORDS` is kept here
    for `PL-F6MM`, and the import rule for `PL-552M`.
    """
    return not waits_on_read(path, tooling)


def outside_the_store(path: str, items_dir: str) -> bool:
    """Whether `path` lies outside the store, the tooling and the records.

    Until 2026-10-03 this was what held a pull request for a read; now it is
    what `arm` names beside its answer, so the report can carry the reason
    the old hold would have given.
    """
    prefix = items_dir.strip("/") + "/"
    return not path.startswith((prefix, TOOLING, RECORDS))


@dataclass(frozen=True)
class Verdict:
    """`arm`'s answer for `HEAD`, and what it rests on.

    `claims` are the unreleased claims bound to this branch, `read` the paths
    a merge would land on the owner's read list, `outside` the paths it would
    land outside the store, the tooling and the records that arm all the same
    and are named, `gate` whether it would change this module, and `behind`
    how many of the base's commits the branch lacks. `unpulled` is what the branch's copy on
    the remote holds that HEAD lacks, with what brings it in, or why that
    could not be read, said before anything else. `unread` is why the answer
    is `unknown`, or what went unread beside a `hold` or a `landed`. `merged`
    is the merged pull request a `landed` names, and what came after it.
    """

    answer: str
    branch: str = ""
    base: str = ""
    items_dir: str = ""
    claims: tuple[Hold, ...] = ()
    read: tuple[str, ...] = ()
    outside: tuple[str, ...] = ()
    gate: bool = False
    behind: int = 0
    unpulled: str = ""
    unread: tuple[str, ...] = ()
    merged: MergedPullRequest | None = None

    @property
    def code(self) -> int:
        return EXIT[self.answer]

    @property
    def lines(self) -> tuple[str, ...]:
        """What `bin/docket arm` prints: the answer first, then what to do."""
        notes = tuple(f"  note: {reason}" for reason in self.unread)
        if self.answer == UNKNOWN:
            reasons = (self.unpulled, *self.unread) if self.unpulled else self.unread
            first, *rest = reasons or ("nothing the answer rests on could be read",)
            return (f"unknown - {first}", *(f"  {reason}" for reason in rest))
        if self.answer == BEHIND:
            commits = "commit" if self.behind == 1 else "commits"
            return (
                f"behind {self.behind} - {self.base} has {self.behind} {commits} {self.branch} "
                "lacks, and main merges only an up-to-date branch",
                f"  Bring it in once - `update_pull_request_branch`, or merge {self.base} and "
                "push - then ask again.",
            )
        if self.answer == ARM:
            said = [
                f"arm - {self.branch} changes nothing on the owner's read list ({READ_LIST}), "
                f"holds no open claim, and contains {self.base}'s tip: mark its pull request "
                "ready and arm it"
            ]
            if self.outside:
                count = len(self.outside)
                noun = "path" if count == 1 else "paths"
                said.append(
                    f"  It changes {count} {noun} outside {self._arming}, which arm on green "
                    "under the owner's read list unless the change raises a question "
                    "for them - this session's judgment, not this answer's - so name "
                    f"{'it' if count == 1 else 'them'} in the report as the hold's reason:"
                )
                said.append(f"  {self._shown(self.outside)}")
            return tuple(said)
        if self.answer == LANDED and (merged := self.merged) is not None:
            said = [
                f"landed - #{merged.number} merged {self.branch} at {merged.head[:12]}, and "
                "nothing merges a merged pull request again, so there is nothing to arm"
            ]
            if self.unpulled:
                said.append(f"  {self.unpulled}")
            if merged.carried:
                oldest, count = merged.carried[0], len(merged.carried)
                others = f", and {count - 1} more" if count > 1 else ""
                came = "1 commit here came" if count == 1 else f"{count} commits here came"
                said.append(
                    f"  {came} after it and land{'s' if count == 1 else ''} nowhere until "
                    f"carried onto {self.base}: {oldest.sha[:9]} {oldest.subject}{others}"
                )
                said.append(
                    f"  Restart the branch on {self.base} and carry "
                    f"{'it' if count == 1 else 'them'}, then push over the old branch the "
                    "remote may still hold, never `git pull`, and open a new pull request - "
                    "`bin/docket branch` prints the commands."
                )
            else:
                said.append(
                    f"  Everything {self.branch} holds is on {self.base}: restart it there before "
                    "the next commit, which would otherwise land nowhere, and push over the old "
                    "branch the remote may still hold, never `git pull` - `bin/docket branch` "
                    "prints the commands."
                )
            return (*said, *notes)
        read = ", so its pull request waits on a read" if self.read or self.gate else ""
        said = [f"hold - {self.branch}: " + " and ".join(self._holding()) + read]
        if self.unpulled:
            said.append(f"  {self.unpulled}")
        for hold in self.claims:
            said.append(f"  {_described(hold)}")
        if self.read:
            said.append(f"  {self._shown(self.read)}")
        said.append(
            "  Leave auto-merge off, disarming it before the push that brings this if it is "
            "armed"
            + (
                ", and keep the pull request a draft while a claim holds it."
                if self.claims
                else "."
            )
        )
        # A claim keeps the pull request a draft, which nobody is asked to read.
        if read and not self.claims:
            said.append(READ_ASK)
        return (*said, *notes)

    @property
    def _arming(self) -> str:
        """The store, the tooling and the records, as `arm` names the paths outside them."""
        return f"{self.items_dir}, {TOOLING.rstrip('/')} and {RECORDS.rstrip('/')}"

    @staticmethod
    def _shown(paths: tuple[str, ...]) -> str:
        """The first `SHOWN` paths, and a count of the rest."""
        shown = ", ".join(paths[:SHOWN])
        more = len(paths) - SHOWN
        return f"{shown}{f', and {more} more' if more > 0 else ''}"

    def _holding(self) -> list[str]:
        """The one-clause reasons a `hold` names: claims, then the read list, then the gate."""
        reasons = []
        if self.claims:
            keys = ", ".join(hold.key for hold in self.claims)
            reasons.append(f"a merge would erase its open claim on {keys}")
        if self.read:
            count = len(self.read)
            noun = "path" if count == 1 else "paths"
            reasons.append(f"it changes {count} {noun} on the owner's read list")
        if self.gate:
            reasons.append(f"it changes {GATE}, the gate itself")
        return reasons


def arm(
    root: Path,
    *,
    items_dir: str,
    now: datetime,
    fetch: bool = True,
    runner: Runner | None = None,
    newest: Callable[[str, str], PullRequestLookup] | None = None,
) -> Verdict:
    """Whether the pull request `HEAD`'s branch would open, or has open, may be armed.

    Fetches first unless `fetch` is false, because `behind` read from a stale
    base is a confident wrong answer; a fetch that fails leaves every answer
    but `hold` unknown. `now` judges the claims' leases, as it does for
    `claims.holdings`, and must carry its offset.

    **HEAD is the pull request only while it holds the branch's copy on the
    remote.** Another writer - GitHub's *Update branch*, a second session - can
    push commits HEAD lacks, and everything read from HEAD is then read from a
    commit the pull request has moved past: `arm` said `behind 1` of a pull
    request already level with its base, and armed one landing a path outside
    the store (`PL-21KN`). So that copy is read before anything else, by
    `_unpulled`, from the remote's listing where the fetch answered - taken
    once and handed to `holdings` too, so a tracking ref for a branch the
    remote deleted is neither the copy nor a holder (`PL-MT3R`).

    **And its pull request may already have merged**, which nothing in the
    tree says where the branch carried only item files (`PL-8BR0`). `newest`
    is the caller's way to ask the forge about the branch's newest pull
    request, handed the branch and the default branch's name: a merge that
    `vcs.carried_merge` confirms HEAD still stands on is `landed` at once, and
    a forge that could not be asked is unread, since arming a pull request that
    merged is the answer this exists to stop.
    """
    unread: list[str] = []
    ran = runner or _run_git
    heads: RemoteHeads | None = None
    if fetch:
        fetched = _git(["fetch", "--quiet", REMOTE], root)
        if fetched.code == 0:
            # The refs just moved, and a runner that remembers answers would
            # give the ones from before the fetch.
            ran = _run_git
            heads = remote_heads(root, runner=ran)
        else:
            said = " ".join(fetched.err.split()) or f"exit {fetched.code}"
            unread.append(
                f"`git fetch {REMOTE}` failed ({said}), so whether the base has moved past this "
                "branch is not known; refresh the refs and pass --no-fetch, or ask again"
            )
    run = _Silences(ran)
    remotes = _remotes(root, run)
    name = run(["rev-parse", "--abbrev-ref", "HEAD"], root).strip()
    # A git that answered nothing is said as that, not as the "no branch" or
    # "no base" it would otherwise read as (`vcs.branch_state` has the case).
    if run.reason or name in {"", "HEAD"}:
        reason = run.reason or "HEAD is on no branch, so there is no pull request to answer for"
        return Verdict(UNKNOWN, unread=(reason, *unread))
    base = default_base(root, runner=run)
    if not resolved(base):
        reason = run.reason or f"no default branch could be established to compare {name} with"
        return Verdict(UNKNOWN, branch=name, unread=(reason, *unread))
    branch = _head_name(name, remotes)
    if branch == _head_name(base, remotes):
        reason = f"HEAD is on {name}, the default branch, which opens no pull request of its own"
        return Verdict(UNKNOWN, branch=name, base=base, unread=(reason,))
    unpulled = _unpulled(root, run, heads, name, branch)
    if newest is not None:
        asked = newest(branch, _head_name(base, remotes))
        pull = asked.newest
        if asked.declined:
            unread.append(
                f"whether {name}'s pull request has already merged could not be asked - "
                f"{asked.declined}"
            )
        elif pull is not None:
            probe = _Silences(ran)
            merged = carried_merge(pull, base, root, runner=probe)
            if probe.reason:
                unread.append(
                    f"git could not compare {name} with {pull.head[:12]}, the head "
                    f"#{pull.number} merged at - {probe.reason}"
                )
            elif merged is not None:
                return Verdict(
                    LANDED,
                    branch=name,
                    base=base,
                    unpulled=unpulled,
                    unread=tuple(unread),
                    merged=merged,
                )

    prefix = items_dir.strip("/") + "/"
    # Both sides of a rename, so a file moved into the store shows the deletion
    # it made outside it, which a rename would print as one path under the store.
    changed = run(changed_path_args("diff", "--name-only", f"{base}...HEAD", "--"), root)
    on_list: tuple[str, ...] = ()
    outside: tuple[str, ...] = ()
    gate = False
    if answered(changed):
        paths = set(listed_paths(changed))
        # The gate is reported apart, and asked for directly rather than read
        # back out of what `arms_on_green` holds.
        gate = GATE in paths
        rest = paths - {GATE}
        tooling, unreadable = _tests_of_the_tooling(sorted(rest), base, root, run)
        unread.extend(unreadable)
        on_list = tuple(sorted(path for path in rest if not arms_on_green(path, tooling)))
        outside = tuple(
            sorted(
                path
                for path in rest
                if arms_on_green(path, tooling) and outside_the_store(path, prefix)
            )
        )
    else:
        unread.append(f"git would not diff {name} against {base}, so what a merge lands is unknown")

    read = holdings(root, now=now, items_dir=items_dir, remote=heads, runner=ran)
    if not read.known:
        unread.append(f"who holds what could not be read - {read.declined}")
    claims = tuple(
        hold
        for hold in read.holds
        if hold.state != RELEASED and _head_name(hold.ref, remotes) == branch
    )
    for ref in read.unreadable:
        if _head_name(ref, remotes) == branch:
            unread.append(f"{ref} could not be compared with {base}, so a claim on it was not read")
    for line in read.malformed:
        # `<hash> on <ref>: Claim: <text>`, as `claims` writes it; a ref name
        # can hold neither a space nor a colon.
        where, _, _ = line.partition(": ")
        if _head_name(where.partition(" on ")[2], remotes) == branch:
            unread.append(f"a trailer on {name} is not a claim record, so it was not read: {line}")

    counted = run(["rev-list", "--count", f"HEAD..{base}"], root).strip()
    behind = int(counted) if counted.isdigit() else 0
    if not counted.isdigit():
        unread.append(f"git would not count {base}'s commits that {name} lacks")
    if run.reason:
        unread.append(run.reason)

    found = Verdict(
        HOLD,
        branch=name,
        base=base,
        items_dir=prefix.rstrip("/"),
        claims=claims,
        read=on_list,
        outside=outside,
        gate=gate,
        behind=behind,
        unpulled=unpulled,
        unread=tuple(unread),
    )
    if claims or on_list or gate:
        return found
    if unpulled or unread:
        return Verdict(UNKNOWN, branch=name, base=base, unpulled=unpulled, unread=tuple(unread))
    if behind:
        return Verdict(BEHIND, branch=name, base=base, items_dir=found.items_dir, behind=behind)
    return Verdict(ARM, branch=name, base=base, items_dir=found.items_dir, outside=outside)


def _tests_of_the_tooling(
    paths: Sequence[str], base: str, root: Path, run: Runner
) -> tuple[frozenset[str], tuple[str, ...]]:
    """The tests of the tooling among `paths`, and why any other test under `TESTS` went unread.

    Each test file under `TESTS` is read on both sides of the change: at the
    merge base, the side `base...HEAD` compares against, and at HEAD, which is
    what a squash lands. Git answers a side holding no such file - a test the
    branch added or deleted - with nothing, which imports nothing.

    A test git would not hand over, or that will not parse here, is not read
    as the tooling's: it waits, and the reason goes beside the hold, since a
    hold that cannot say why is a partial read handed over as a whole one.
    `bin/docket` runs on the bare `python3`, which can be older than the
    project's own interpreter, so a test written in newer grammar is the
    likeliest such case; none under `TESTS` was, measured 2026-10-05.
    """
    tests = [
        path for path in paths if path.startswith(TESTS) and is_test_file(PurePosixPath(path).name)
    ]
    if not tests:
        return frozenset(), ()
    fork = run(["merge-base", base, "HEAD"], root).strip()
    if not fork:
        one = len(tests) == 1
        which = "the test it changes" if one else f"the {len(tests)} tests it changes"
        return frozenset(), (
            f"git gave no merge base of {base} and HEAD, so what {which} under {TESTS} "
            f"import{'s' if one else ''} was not read, and {'it' if one else 'each'} waits on "
            "the read",
        )
    tooling: set[str] = set()
    unreadable: list[str] = []
    for path in tests:
        sides = [run(["show", f"{rev}:{path}"], root) for rev in (fork, "HEAD")]
        if not all(answered(side) for side in sides):
            unreadable.append(
                f"git would not hand over {path} on both sides of the change, so whether it "
                f"imports {PRODUCT_PACKAGE} was not read, and it waits on the read"
            )
            continue
        try:
            if tests_the_tooling(path, sides):
                tooling.add(path)
        except (SyntaxError, ValueError, RecursionError) as error:
            line = error.lineno if isinstance(error, SyntaxError) else None
            where = f", line {line}" if line else ""
            said = error.msg if isinstance(error, SyntaxError) else str(error)
            unreadable.append(
                f"{path} would not parse under this python3 ({platform.python_version()}): "
                f"{said}{where}, so whether it imports {PRODUCT_PACKAGE} was not read, and it "
                "waits on the read"
            )
    return frozenset(tooling), tuple(unreadable)


def _unpulled(root: Path, run: Runner, heads: RemoteHeads | None, name: str, branch: str) -> str:
    """What the branch's copy on the remote holds that HEAD lacks, and what brings it in.

    `""` where HEAD holds all of it, or the remote has no copy. The copy is
    the listing's where the command's fetch answered, since no fetch here
    prunes and a tracking ref outlives a branch the remote deleted - one a
    session restarted from the base would otherwise be sent to pull back in
    (`PL-MT3R`). With no listing - `--no-fetch`, or a fetch that failed - it
    is the tracking ref, read as it is, and named as that.

    `merge-base --is-ancestor` answers 0 for "holds it" and 1 for "does not";
    anything else is git unable to say, most often a tip the listing names
    that this clone has not fetched, where it exits 128. That is said as
    unread and never read as "holds it", which would give back the answer
    from HEAD (`PL-C3MN`). The remedies are `git pull` from the remote's copy,
    never the tracking ref, so one run against a branch the remote deleted
    fails loudly rather than merging a stale ref.
    """
    if heads is not None:
        where = f"{REMOTE}'s copy of {name}"
        tip = heads.tip(branch)
        if tip is None:
            unknown = f"whether {where} has commits {name} lacks is not known"
            return f"{heads.failed}, so {unknown}; ask again"
    else:
        where = f"the tracking ref {REMOTE}/{branch}"
        ref = f"refs/remotes/{REMOTE}/{branch}^{{commit}}"
        tip = run(["rev-parse", "--verify", "--quiet", ref], root).strip()
    if not tip:
        return ""
    held = _git(["merge-base", "--is-ancestor", tip, "HEAD"], root).code
    if held == 0:
        return ""
    if held != 1:
        return (
            f"{where} is at {tip[:12]}, a commit git could not compare with HEAD - most often one "
            "this clone has not fetched - so whether HEAD is what its pull request lands is not "
            f"known; bring it in with `git pull --no-rebase {REMOTE} {branch}` and ask again"
        )
    lacks = run(["rev-list", "--count", f"HEAD..{tip}"], root).strip()
    own = run(["rev-list", "--count", f"{tip}..HEAD"], root).strip()
    said = f"{where} has {_counted(lacks)} {name} lacks"
    pull = f"bring them in with `git pull --ff-only {REMOTE} {branch}`"
    # A fast-forward cannot bring them in past a commit of HEAD's own, and
    # where git would not count those, the merge serves either way.
    if own != "0":
        pull = f"merge them with `git pull --no-rebase {REMOTE} {branch}`"
        if own.isdigit():
            said += f", and {name} has {_counted(own)} that copy lacks"
    return f"{said}, so HEAD is not what its pull request lands; {pull} and ask again"


def _counted(count: str) -> str:
    """`1 commit`, `2 commits`, or `commits` where git gave no count."""
    if not count.isdigit():
        return "commits"
    return f"{count} commit" + ("" if count == "1" else "s")


def _described(hold: Hold) -> str:
    """One claim holding the branch: which item, since when, and how it ends."""
    when = hold.since.strftime("%Y-%m-%d %H:%M %z")
    line = f"{hold.key}: claimed in {hold.commit[:12]} on {when}"
    if hold.state == LAPSED:
        return (
            f"{line}, lapsed with no commit since {hold.renewed.strftime('%Y-%m-%d')}; "
            f"`bin/docket yield {hold.key}` ends it, `bin/docket claim {hold.key}` renews it"
        )
    return (
        f"{line}; released when this branch's copy closes or blocks it, "
        f"or by `bin/docket yield {hold.key}`"
    )
