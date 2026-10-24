"""Whether a pull request may be armed for auto-merge: `bin/docket arm`'s answer for `HEAD`.

`.claude/skills/pull-request/SKILL.md` arms a pull request whose branch
carries only item files, so a capture reaches the default branch even when its
session ends before any work does (project owner, 2026-09-23, ratified, over "a branch carrying only
captured items is not a pull request", `PL-WNCT`). Which pushes could be armed
was a catalog of claim shapes each session applied by judgment - the empty
start commit, a queue-only commit start mode read as one - and every shape it
missed merged a claim away with its branch while the work went on (`PL-QP9Z`,
`PL-1MCK`, `PL-KWCY`). A claim is a recorded fact now (`claims`), so the
question is decided here, from the tree, and asked before arming and before
every later push while a pull request is open.

**Five answers, and an exit status for each.**

- `arm` (0): the net change a squash would land - `base...HEAD` - waits on
  no read from the owner: it changes or deletes no existing test pinning this
  module's answers (`PINS`), and either reaches no
  simulator path (`READ_PATHS`, a test of the tooling under `tests/` aside,
  which `arms_on_green` answers path by path) or carries the session's
  `Owner-read: not needed - <why>` record on a commit since its newest change
  there, and no record on it says `needed`; no claim bound to this
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
  work nobody finished or handed back. A simulator path no `Owner-read`
  record covers holds it until the session records whether the owner needs
  to read it (`JUDGE_ASK`), so a judgment nobody made fails safe rather than
  merging a clinical change unread. A record saying `needed` and a change to
  an existing test pinning this module's answers (`PINS`) hold it for the
  owner's read, and it merges on the owner's word alone. A change to this
  module that edits no such test arms, and the answer names it. So
  does a switch of auto-merge off that no commit records as the session's
  (`AUTO_MERGE`). Once no claim holds it, that hold prints the ask's opening
  line from the session's `Owner-ask` record (`ASK_LINE`), or, with no record,
  says that nothing goes to the owner until there is one (`READ_ASK`). With no
  record it also opens its first line with "send the owner nothing" and exits
  3 (`NO_ASK`) rather than 1, so that a session reading only the first line,
  or only the exit status, still learns it (`PL-TLPH`).
  Long docstrings and comments that a simulator change adds, and that no
  `Prose-review` record covers, hold it until the session records close-out
  step 8's review (`PROSE_ASK`), and so does a count that could not be read.
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
  included. This module stays held so that the gate cannot loosen itself
  (until 2026-10-19, below);
- a body record arms on green beside them (2026-09-25, ratified with the
  record's form, over every pull request holding on the record it writes
  before its merge, `PL-979D`): the record is a copy of the body, never a
  change to read;
- only the owner's read list waits on a read - `src/`, `tests/` outside
  `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/`, `README.md` and
  this module, until 2026-10-19 - and every other path arms on green, named
  beside the answer, unless the change raises a question for the owner (the
  Projects trial's instructions, 2026-10-03, kind unrecorded, over holding
  every path outside the store, the tooling and the records; built by
  `PL-KKHD`). The rule was written there alone, so on one day `#1298` armed
  under it while `#1308` held under the old one. It reopened `PL-0JGZ`
  (project owner, 2026-09-26, ratified), which kept `ROADMAP.md` and
  `docs/WORKING_NOTES.md` off what arms because the roadmap is where the owner
  sets direction: neither is on the list, so both arm, and the owner settled
  it so (project owner, 2026-10-03, ratified, over holding them as before).
  `.github/workflows/` and `.claude/hooks/` joined the list the same day,
  since they decide merges and tags as this module does (project owner,
  2026-10-03, ratified, over leaving them armed on green; `PL-KKHD` records
  both answers), until the owner's rule of 2026-10-12 below;
- docket's lexer, `docket/shell.py`, joined the list when `PL-JNYL` made it
  the reader every guard hook reads a Bash call through, so that a change to
  what the guards refuse still waited on a read outside `.claude/hooks/`
  (project owner, 2026-10-10, ratified, over arming lexer changes on green;
  `PL-JNYL` records the answer), until the same rule;
- workflow items need no merge confirmation (project owner, 2026-10-12: "don't
  need to ask me for merge confirmation for workflow items"), so
  `.github/workflows/`, `.claude/hooks/` and the lexer left the list and arm
  on green with the rest of the workflow lane, while a product path waits as
  before, in a change crossing both lanes too (`PL-KPM2`). This module stays
  on the list so that the gate still cannot loosen itself: a change to it
  could drop `src/` from the list and merge unread (project owner, 2026-10-12,
  ratified, over arming a change to it on green with the rest of the workflow
  lane; `PL-VKHD` records the answer), until the owner's answer of 2026-10-19
  below;
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
  green: widening what arms still takes an edit the gate holds (`PL-0JGZ`);
- a pull request reaches the owner only for a real decision or a high-risk
  change, and housekeeping merges on green (project owner, 2026-10-17: "Model
  comes to me only when there is a real decision as discussed or making a high
  risk change you want a second set of eyes on then you should present the
  case for the change, the risks etc. but house keeping stuff I don't need to
  sign off everything"; built by `PL-DKBG`). The read list had held `#1516`'s
  measured figures and tightened tests exactly as it would a changed equation,
  and its ask invented two points to judge. So the list no longer holds by
  itself: a change to it waits for the session's recorded judgment,
  `Owner-read: needed - <why>` or `not needed - <why>`, which `arm` reads from
  the branch's commits, and only `needed` and this module wait on the owner
  (this module until 2026-10-19, below). Chosen over dropping the list and
  leaving the judgment to prose, which fails open on a session that never
  makes it, and over keeping the list and rewording the ask, which leaves
  housekeeping waiting on the owner.
- a hold for the owner's read carries its ask as an `Owner-ask` record, a
  decision with at least two options and a recommendation or a risk review,
  and `arm` prints it as the ask's opening line (project owner, 2026-10-18:
  "View chooser thread just told me a generic read pull request without a
  question again" and "it's not supposed to ask for a merge if nothing to
  review"; built by `PL-9JHM`). The ask's shape was prose twice before
  (`PL-9KHK`, `PL-DKBG`), and sessions still sent a bare read. A form for
  "nothing to decide" was weighed and refused, because a pull request with
  nothing to review should not reach the owner at all: the way out of such a
  hold is `Owner-read: not needed`;
- a change to this module holds only when it changes or deletes an existing
  test pinning its answers, and otherwise arms on green with the rest of the
  tooling (project owner, 2026-10-19, ratified, over holding every change to
  it with a risk-review ask and over arming it on green with no such test;
  `PL-9JHM` records the owner's answer). It reopens `PL-VKHD`'s answer of
  2026-10-12, which held every change here so that the gate could not loosen
  itself, because nine of those holds in two weeks were mostly refactors
  with nothing to review. To loosen an existing answer, a change has to edit
  the test that pins it, so that kind of loosening still waits. A loosening
  that no test pins merges unread, and so would one that also rewrote the
  check reading the pins, since this module judges its own change;
- the gate's read covers the existing tests that pin its answers as well as
  this module, and since 2026-10-19 those tests alone (`PL-9JHM`), so a
  loosening through what the answer is read through has to edit one (project
  owner, 2026-10-12, ratified, over holding `vcs.py`, `claims.py`, `cli.py`
  and `test_cli.py` whole, and over leaving it; `PL-WW0Q`). It reopens, for
  that one route, `PL-SQTR`'s line at this module alone;
- a simulator change's new long prose waits for a recorded review: `arm`
  holds while the count that `prose_count_command` gives is above zero, or
  could not be read, and only the prose added since the newest
  `Prose-review` record is counted (2026-10-19, decided in the workflow
  decision round without the owner as the one clearly correct option, over
  relying on a pointer in close-out step 5 and measuring five more branches,
  `PL-W04Z`). Five of six simulator branches had skipped step 8's review, and
  their prose was rated awkward in 58% of verdicts against 22% for the one
  that ran it (`PL-J6CK`). Docket names no repository tool, so the count is a
  configured command, as the forge's are.

Status dispositions and release cuts never hold arming (`PL-MB2W` § "Other
holds"): a triage pass moving statuses is the queue-only work auto-merge
exists for, and a cut's notes file lies outside the store and the tooling,
so the paths hold it already.
"""

from __future__ import annotations

import ast
import fnmatch
import re
import string
import sys
from collections.abc import Callable, Collection, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from .claiming import _git
from .claims import LAPSED, RELEASED, Hold, holdings
from .lines import split_lines
from .python import imports
from .vcs import (
    PULL_OPEN,
    RECORDS,
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
    head_branch,
    listed_paths,
    path_in_checkout,
    remote_heads,
    resolved,
)

#: The five answers, each the first word of what `arm` prints.
#: `ALREADY_MERGED` prints as `landed`. Its name differs from `vcs.LANDED`, a
#: branch's disposition, which is a different fact spelled with the same word
#: (`PL-LGDV`).
ARM = "arm"
HOLD = "hold"
BEHIND = "behind"
ALREADY_MERGED = "landed"
UNKNOWN = "unknown"

#: The exit status of each answer. `behind` and `landed` share `hold`'s: all
#: three say "not now", and the line printed says which.
EXIT = {ARM: 0, HOLD: 1, BEHIND: 1, ALREADY_MERGED: 1, UNKNOWN: 2}

#: The exit status of a `hold` that waits on the owner's read while no
#: `OWNER_ASK` record says what to ask, so that nothing may be sent to the
#: owner yet. It differs from `hold`'s 1 so that the status alone says so: on
#: `#1612` and `#1676` a session read `arm` through `head`, missed the line
#: saying to send nothing, and sent the owner a bare read ask (`PL-TLPH`).
#: `--owner-ask` exits with it too, whenever nothing may be sent.
NO_ASK = 3

#: How many paths outside the store, the tooling and the records a `hold`
#: names before counting the rest.
SHOWN = 5

#: The commit trailer a session records its judgment in: whether the owner
#: needs to read the branch's change before it merges (project owner,
#: 2026-10-17, `PL-DKBG`). Its value is `READ_NEEDED` or `READ_NOT_NEEDED`,
#: then " - " and the reason, which the report and the pull request body
#: carry. Git reads a trailer from a commit message's last paragraph alone.
OWNER_READ = "Owner-read"
READ_NEEDED = "needed"
READ_NOT_NEEDED = "not needed"

#: The commit trailer that carries what a hold for the owner's read asks him
#: (project owner, 2026-10-18, `PL-9JHM`). `arm` prints it as the ask's
#: opening line, so the ask is a recorded fact rather than prose a session
#: may skip. It takes one of two forms, the owner's two reasons to be asked
#: (`PL-DKBG`), each a run of fields joined by `ASK_SEPARATOR`:
#:
#: - a decision: `<question>? | <option>: <what it changes> | <option>: <what
#:   it changes> | recommend <option> - <why>`, with at least two options;
#: - a risk review, for a high-risk change with no choice in it: `risk -
#:   <what could go wrong, for whom> | checked - <what was checked to rule it
#:   out> | look - <the one thing the owner should look at>`.
OWNER_ASK = "Owner-ask"
ASK_SEPARATOR = " | "
ASK_RECOMMEND = "recommend"
ASK_RISK = ("risk", "checked", "look")

#: How `parse_owner_ask` renders an `OWNER_ASK` record as the line the owner
#: is sent. `renders_owner_ask` recognizes a line in either form from these
#: same templates, so `.claude/hooks/owner_ask_guard.py` can check a
#: coordinator's post without a second copy of the form (`PL-YV90`). A risk
#: review is one template. A decision is `ASK_DECISION_SHOWN`, whose
#: `options` are two or more `ASK_OPTION_SHOWN` joined by
#: `ASK_OPTIONS_JOIN`, and whose `recommend` is `ASK_RECOMMEND_SHOWN`.
ASK_RISK_SHOWN = "Risk to review: {risk}. Checked: {checked}. Please look at: {look}."
ASK_DECISION_SHOWN = "{question} {options} {recommend}"
ASK_OPTION_SHOWN = 'Option "{label}": {change}.'
ASK_OPTIONS_JOIN = " "
ASK_RECOMMEND_SHOWN = 'I recommend "{pick}": {why}.'

#: What a hold for the owner's read prints when no `OWNER_ASK` record covers
#: the change. The ask was prose until 2026-10-18, and sessions skipped it:
#: three closed on a bare "read #N" (`PL-9KHK`), `#1516`'s ask invented two
#: points to judge (`PL-DKBG`), and the view chooser thread sent another bare
#: read on 2026-10-18. The owner's rule is that a pull request with nothing to
#: review does not reach him at all, so the way out of a hold with nothing in
#: it is `Owner-read: not needed`, never a question made up to fill the form.
#: On `#1650` the owner had to ask twice what a recorded ask asked them to
#: judge, so the text also asks for learner terms and, for a choice between
#: interface approaches, a screenshot per option (`PL-KYTY`).
READ_ASK = (
    "  Send the owner nothing about this pull request yet: no Owner-ask record on a commit "
    "since its newest change outside the store and the pull request bodies says what to "
    "ask. A hold reaches the owner only with something to decide or to review. A question "
    "whose answer is obvious is wrong, as on #1516, whose ask invented two points to judge "
    "(PL-DKBG). Record one of two forms in the last paragraph of a commit, beside its "
    "Co-authored-by line, then ask again. For a decision, with at least two options a "
    f"careful person could each pick: `{OWNER_ASK}: <question>? | <option>: <what it changes "
    f"for the owner or a learner> | <option>: <what it changes> | {ASK_RECOMMEND} <option> - "
    f"<why>`. Word it in clinical or learner terms, so that the owner sees on first reading "
    "what they are judging. Say under each option what a learner sees, and say why the "
    "choice is the owner's. A choice between approaches to the interface goes with one "
    "annotated screenshot per option, attached to the reply that carries the line "
    "(.claude/skills/run-the-app/SKILL.md). "
    f"For a high-risk change with no choice in it: `{OWNER_ASK}: {ASK_RISK[0]} - "
    f"<what could go wrong, for whom> | {ASK_RISK[1]} - <what was checked to rule it out> | "
    f"{ASK_RISK[2]} - <the one thing to look at>`. If neither form can be filled honestly, "
    f"nothing needs the owner: record `{OWNER_READ}: {READ_NOT_NEEDED} - <why>` instead, and "
    "the change merges on green. A change to a test pinning the gate's answers holds whatever "
    "that record says, so for one of those use the risk form."
)

#: What a hold for the owner's read prints before the line its `OWNER_ASK`
#: record renders. The line goes in the closing block, because a wording
#: that said only what the ask opens with was followed to the letter
#: (`PL-9KHK`).
ASK_LINE = (
    "  Open the ask with this line, word for word, as the closing block's own line, never "
    "as 'read #N', and repeat it whole in every later reply that still waits on it:"
)

#: What a `hold` without a claim tells a session about a repair push. A
#: session never arms a held pull request, so a held one that is armed was
#: armed by the owner, and `docs/maintainer.md` § "Bring a stale base in when
#: you merge, with Update branch" has the repair land on it unread
#: (`PL-XTBF`, decided 2026-10-12). Whether the owner armed it is prose, not a
#: computed branch: a session's GitHub calls are the owner's too, so `arm`
#: cannot tell who armed it.
REPAIR_EXCEPTION = (
    "  The exception is a repair. If the pull request already held before this push "
    "and is armed, the owner armed it after reading it. Leave it armed, and auto-merge "
    "lands the fix once CI is green, as docs/maintainer.md says."
)

#: The commit trailer a session records its own switch of auto-merge off in,
#: with the value `AUTO_MERGE_OFF - <why>`. GitHub names the owner's account
#: as the actor of every arm and every disarm, the ones a session makes
#: through its tools included, so nothing the forge keeps says who switched it
#: off (`PL-8TPV`, checked on `#1478` and `#1586`, 2026-10-18). A session
#: switches it off only before a push that brings a hold, or when told to
#: change nothing, so it records that in the next commit it makes; a switch no
#: record covers is the owner's.
AUTO_MERGE = "Auto-merge"
AUTO_MERGE_OFF = "off"

#: What a `hold` tells a session when auto-merge was switched off and no
#: commit records this session doing it. The owner switches it off to choose
#: the order pull requests merge in, so a session that armed it again, or
#: merged it once CI was green, would override that choice: ten switches on
#: five pull requests on 2026-10-17 were the owner's, and the sessions read
#: them as theirs to undo (`PL-8TPV`).
OWNER_OFF = (
    "  The owner switched auto-merge off to hold it back, most often so that another pull "
    "request merges first. Leave it off, and arm or merge it only on the owner's word. If "
    "this session switched it off itself, as its own transcript shows, record that as "
    f"`{AUTO_MERGE}: {AUTO_MERGE_OFF} - <why>` in the last paragraph of a commit made after "
    "the switch, and ask again."
)

#: The commit trailer a session records close-out step 8's prose review in, with
#: the value `read N, rewrote M, rejected K` (`PL-W04Z`). A long docstring or
#: comment that a simulator change adds after the newest such record holds the
#: pull request, so a code fix after the review needs no second review, while a
#: new long docstring does.
PROSE_REVIEW = "Prose-review"
PROSE_FORM = re.compile(r"read \d+, rewrote \d+, rejected \d+")

#: What a `hold` on unreviewed long prose tells the session. The step's own
#: instructions are in the close-out mode, so they are pointed at, not restated.
PROSE_ASK = (
    "  Run close-out step 8's prose review (.claude/skills/docket/modes/close-out.md) on "
    "the long docstrings and comments the branch adds, apply the rewrites you accept, and "
    "record the review as a trailer in the last paragraph of a commit made after it, beside "
    f"its Co-authored-by line: `{PROSE_REVIEW}: read N, rewrote M, rejected K`. One commit can "
    f"carry this and an {OWNER_READ} record together. Then ask again."
)

#: What a `hold` tells the session when the count of long prose could not be read.
PROSE_UNCOUNTED = (
    "  A branch whose prose could not be counted is never armed as though it had none. Make "
    "the count readable, most often by fixing a file Python will not parse, and ask again."
)

#: What a `hold` on a simulator path with no record tells the session. The
#: test for a real decision is the design round's, so it is pointed at rather
#: than restated, and the high-risk cases are the ones the owner's rule names
#: in this repository's terms. What a learner can be misled by is the first,
#: because the safety-critical standard in `CLAUDE.md` makes it so.
JUDGE_ASK = (
    "  Decide whether the owner needs to read it, and record the answer as a trailer in "
    "the last paragraph of a commit made after the change, beside its Co-authored-by "
    f"line: `{OWNER_READ}: {READ_NEEDED} - <why>` or `{OWNER_READ}: {READ_NOT_NEEDED} - "
    "<why>`. It is needed for a real decision, one "
    ".claude/skills/docket/modes/design.md step 4 makes the owner's, and for a high-risk "
    "change: one that changes a clinical value the "
    "simulator computes or displays, or what docs/MODEL.md says one means, beyond "
    "restating what the change's own tests measure; one that changes a rule sessions run "
    "under that the owner did not ask for in their own words; or one whose breakage CI "
    "would not show or a revert would not undo. Anything else is housekeeping and not "
    "needed: a refactor with its outputs pinned, a tightened test, a figure restated from "
    "a measurement. Then ask again."
)

#: This module, which decides the answer. Since 2026-10-19 a change to it
#: waits on a read only when it edits a test pinning its answers or moves it
#: off the path the base holds it at (`PL-9JHM`), and `arm` names it beside an
#: `arm`. It is
#: the module's own path from the root of the checkout holding it, so a move
#: cannot leave it naming a file nothing reads, and the package spells none of
#: this repository's layout (`PL-QFCR`). It is read from the module rather than
#: from `docket.toml`, because a change to `docket.toml` arms on green: a
#: setting naming the gate could point it at another file and let the next
#: change to this one merge unread. `""` where no checkout holds the module,
#: since then no path of the repository being asked about is the gate.
GATE = path_in_checkout(Path(__file__))


def _tooling(gate: str) -> str | None:
    """The package's project directory, which holds `src/docket/` and so this module.

    `""` where that directory is the checkout's root, so that every path is
    the tooling's, and `None` where no checkout holds the module, so that none
    is.
    """
    if not gate:
        return None
    home = PurePosixPath(gate).parents[2].as_posix()
    return "" if home == "." else home + "/"


#: The queue's own tooling, which arms on green beside the store. It is found
#: from `GATE`, as the directory the package lives in.
TOOLING = _tooling(GATE)

#: The test file whose arm tests pin the gate's answers. A change to what the
#: answer is read through - `vcs.changed_path_args`, `claims.holdings`,
#: `cli.cmd_arm` - arms on green, so a loosening there passes unread unless it
#: also has to edit a pinned answer. So a change to or a deletion of an
#: existing pinned test waits on the owner's read, which since 2026-10-19 is
#: what holds a change to `GATE` too (`PL-9JHM`), and a new test arms (project
#: owner, 2026-10-12, ratified, over holding `vcs.py`, `claims.py`, `cli.py`
#: and `test_cli.py` whole, `PL-WW0Q`). `None` where no checkout holds the
#: module.
PINS = None if TOOLING is None else TOOLING + "tests/test_cli.py"

#: How a top-level name in `PINS` marks the definition as one of the arm
#: tests, their helpers or their constants.
PIN_PREFIXES = ("test_arm_", "_arm", "ARM_")

#: Names whose use in a test marks it as pinning an answer of `arm`'s: the
#: helper that runs the command, and this module.
PIN_NAMES = frozenset({"_arm", "arming"})

#: The simulator's tests, at the root: `subprojects/docket/tests/` starts with
#: `subprojects/`, so the prefix leaves it to the tooling.
TESTS = "tests/"

#: Importing this is what makes a test file the simulator's. It is the rule
#: `tools/workflow_paths_check.py` holds `docket.toml`'s `workflow_paths` to
#: (`PL-JBZK`), and since 2026-10-05 the one that lets a test under `TESTS`
#: arm on green (`PL-552M`). Spelt here, in the module the gate holds, and
#: imported by the lane check, so the two read one rule. Since 2026-10-19 an
#: edit to it waits on the owner's read only where it edits a pinned test
#: (`PL-9JHM`).
PRODUCT_PACKAGE = "anesthesia_sim"

#: What pytest collects as a test module: its default `python_files`, which
#: this repository does not override. Restated rather than read, and
#: `tests/unit/test_workflow_paths_check.py` compares it with the setting its
#: own run collected under, so a changed `python_files` fails a test instead
#: of quietly turning a new test into a support module.
TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")

#: The simulator's paths, which were the owner's read list as they spelt it
#: (2026-10-03, `PL-KKHD`). Since 2026-10-17 a change reaching one of these
#: waits for the session's `OWNER_READ` record rather than for the owner, and
#: only a record saying `READ_NEEDED` waits on them (`PL-DKBG`). A directory
#: holds what is under it, and a file is itself. `TESTS` is the simulator's,
#: but for a test of the tooling (`tests_the_tooling`), which arms on green
#: since the owner's answer of 2026-10-05. `src/anesthesia_sim/data/` lies
#: under `src/` and is kept for the reader who looks for it by name.
#: `.github/workflows/`, `.claude/hooks/` and docket's lexer, which joined on
#: the owner's answers of 2026-10-03 and 2026-10-10, left it on his rule of
#: 2026-10-12 that workflow items need no merge confirmation (`PL-KPM2`): what
#: is left is the simulator's.
READ_PATHS = ("src/", TESTS, "docs/MODEL.md", "src/anesthesia_sim/data/", "README.md")

#: The simulator's paths as the answers name them.
READ_LIST = (
    f"src/, {TESTS} but a test importing no {PRODUCT_PACKAGE}, docs/MODEL.md, "
    "src/anesthesia_sim/data/ and README.md"
)


def imports_product(tree: ast.Module) -> bool:
    """Whether a file imports the simulator, which makes any file under `tests/` the simulator's.

    Read from the parsed tree by `python.imports`, rather than by a regular
    expression, because the question is about imports and not about text: a
    package named in a docstring, in a fixture path or in a comment is not a
    dependency. A dynamic import of a literal name counts, as it does for
    `tools/import_boundary_check.py`, which reads the same function. A file
    loading `anesthesia_sim.core` through `importlib.import_module` read as
    importing nothing here until `PL-8W1J`.
    """
    return any(imported.reaches(PRODUCT_PACKAGE) for imported in imports(tree))


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
    """Whether a change to `path` waits on a read: a simulator path.

    It waits for the session's `OWNER_READ` record (`PL-DKBG`). `GATE` does
    not wait by its path since 2026-10-19: a change to it waits only when it
    edits a test in `PINS`, which `arm` reads apart (`PL-9JHM`).

    `tooling` is the paths under `TESTS` that `tests_the_tooling` read as
    tests of the tooling, on both sides of the change, which arm on green. A
    name alone cannot say so, so a path under `TESTS` nobody read waits, and
    `tooling` clears nothing outside `TESTS`.
    """
    if path in tooling and path.startswith(TESTS):
        return False
    return any(
        path == entry or (entry.endswith("/") and path.startswith(entry)) for entry in READ_PATHS
    )


def arms_on_green(path: str, tooling: Collection[str] = ()) -> bool:
    """Whether a change to `path` may merge on green CI without a recorded judgment.

    A path this answers no to waits for the session's `OWNER_READ` record
    (project owner, 2026-10-17, `PL-DKBG`).

    Everything but the owner's read list may (the Projects trial's
    instructions, 2026-10-03, kind unrecorded, over holding every path outside
    the store, the tooling and the records, `PL-SQTR`; built by `PL-KKHD`),
    and so may a test of the tooling under `TESTS`, named in `tooling`
    (project owner, 2026-10-05, ratified, `PL-552M`). `arm` holds a branch
    for each path this answers no to, and names beside an `arm` each path
    `outside_the_store` answers yes to, since the owner's rule arms those only
    while the change raises no question for them - a judgment this module
    does not make - and asks for the reason in the report.

    It is not `vcs.in_queue`, which asks whether a change owes a claim and
    counts the roadmap and the notes as queue records, since a triage pass and
    a design round write them and nothing else (`PL-3CTW`). The two answers
    were kept apart on purpose: `ROADMAP.md` and `docs/WORKING_NOTES.md` owe
    no claim, and until 2026-10-03 still waited on a read (project owner,
    2026-09-26, ratified, over treating them as queue records here,
    `PL-0JGZ`), because the roadmap is the milestone map the owner sets
    direction in. The owner's read list leaves both off, so they arm now;
    `PL-KKHD` records the reopening. The rule is spelt here, in the one
    module the gate is, rather than beside `in_queue`, so that widening what
    arms takes an edit to the gate and to its pinned tests (2026-09-26, ratified, over
    two named predicates in `claims`, `PL-0JGZ`), as the import rule is for
    `PL-552M`.

    The pull requests' body files arm on green too. `tools/pr_body_check.py
    --recover` writes one for a squash commit that landed with no body, and a
    copy of a body is never a change to read (`PL-3PH2`). Their directory is
    `vcs.RECORDS`, read from there rather than spelt here. This module kept a
    copy until 2026-10-24, so that widening it would wait on a read, but since
    2026-10-19 an edit to this module waits on no read. What still holds a
    widening is the pinned tests, which name the directory (`PL-9JHM`,
    `PL-F6MM`, `PL-LGDV`).
    """
    return not waits_on_read(path, tooling)


def outside_the_store(path: str, items_dir: str) -> bool:
    """Whether `path` lies outside the store, the tooling and the records.

    Until 2026-10-03 this was what held a pull request for a read; now it is
    what `arm` names beside its answer, so the report can carry the reason
    the old hold would have given.
    """
    prefix = items_dir.strip("/") + "/"
    if TOOLING is not None and path.startswith(TOOLING):
        return False
    return not path.startswith((prefix, RECORDS))


def _bound_names(node: ast.stmt) -> tuple[str, ...]:
    """The names a top-level statement defines: a function's, or an assignment's targets."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return (node.name,)
    if isinstance(node, ast.Assign):
        return tuple(target.id for target in node.targets if isinstance(target, ast.Name))
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return (node.target.id,)
    return ()


def pinned_definitions(tree: ast.Module) -> dict[str, str]:
    """Each definition in `PINS` that pins `arm`'s answers, with a dump of what it says.

    A definition is pinned when its name starts with one of `PIN_PREFIXES`,
    or when it is a test that uses one of `PIN_NAMES`. The dump leaves out a
    function's docstring, so rewording what a test says about itself is not a
    change to what it pins. It also leaves out formatting and comments, which
    `ast` does not keep.
    """
    found: dict[str, str] = {}
    for node in tree.body:
        for name in _bound_names(node):
            uses = {sub.id for sub in ast.walk(node) if isinstance(sub, ast.Name)}
            if not name.startswith(PIN_PREFIXES) and not (
                name.startswith("test_") and uses & PIN_NAMES
            ):
                continue
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body = node.body[1:] if ast.get_docstring(node, clean=False) else node.body
                parts: list[ast.AST] = [*node.decorator_list, node.args, *body]
                if node.returns is not None:
                    parts.append(node.returns)
                found[name] = "\n".join(ast.dump(part) for part in parts)
            else:
                found[name] = ast.dump(node)
    return found


def changed_pins(before: str, after: str) -> tuple[str, ...]:
    """The pinned definitions of `before` that `after` changes or deletes, sorted.

    A definition `after` adds is not among them: a new pinned answer loosens
    nothing. Raises what `ast.parse` raises on a side that will not parse.
    """
    old = pinned_definitions(ast.parse(before, filename=PINS or "test_cli.py"))
    new = pinned_definitions(ast.parse(after, filename=PINS or "test_cli.py"))
    return tuple(sorted(name for name, said in old.items() if new.get(name) != said))


@dataclass(frozen=True)
class AutoMerge:
    """What the forge says of a pull request's auto-merge: its latest switch, and when.

    `state` is `AUTO_MERGE_ON` or `AUTO_MERGE_OFF` for the latest switch, and
    `""` where nobody ever switched it on. `at` is when that switch was made,
    in ISO 8601. `declined` says why the forge could not be asked, so that
    "could not ask" never reads as "never armed".
    """

    state: str = ""
    at: str = ""
    declined: str = ""


#: `AutoMerge.state` for a pull request whose latest switch armed it.
AUTO_MERGE_ON = "on"


@dataclass(frozen=True)
class ProseCount:
    """How many long docstrings and comments need a review, as `prose_count_command` says.

    `count` is that number. `declined` says why it could not be read, so that
    "could not count" never reads as "nothing to review".
    """

    count: int = 0
    declined: str = ""


@dataclass(frozen=True)
class OwnerRead:
    """A session's recorded judgment of whether the owner needs to read the branch.

    `commit` carries the `OWNER_READ` trailer, `needed` is its answer, and
    `why` is the reason the session gave, which the report repeats.
    """

    commit: str
    needed: bool
    why: str


def parse_owner_read(value: str) -> tuple[bool, str] | None:
    """`(needed, why)` from an `OWNER_READ` value, or `None` for one in neither form.

    The form is `needed - <why>` or `not needed - <why>`, and the reason is
    required, because a judgment with no reason cannot be audited.
    """
    word, dash, why = value.partition(" - ")
    word = word.strip().lower()
    if not dash or not why.strip() or word not in {READ_NEEDED, READ_NOT_NEEDED}:
        return None
    return word == READ_NEEDED, why.strip()


@dataclass(frozen=True)
class OwnerAsk:
    """What a hold for the owner's read asks him, from a session's `OWNER_ASK` record.

    `commit` carries the trailer, and `line` is the ask's opening line as
    `parse_owner_ask` renders it.
    """

    commit: str
    line: str


def parse_owner_ask(value: str) -> tuple[str, str]:
    """`(line, "")` from an `OWNER_ASK` value in one of its forms, or `("", why)` otherwise.

    A decision needs a question ending in "?", at least two options that each
    say what they change, distinct labels, and a recommendation naming one of
    them with its reason. A risk review needs its three fields in order, each
    with a value. Whether a question's answer is obvious is judgment, so the
    printed instructions say it and this does not try.
    """
    fields = [field.strip() for field in value.split(ASK_SEPARATOR)]
    named = [field.partition(" -") for field in fields]
    if [word.strip().lower() for word, _, _ in named] == list(ASK_RISK):
        if not all(dash and said.strip() for _, dash, said in named):
            return "", "a risk review needs a value after each of risk, checked and look"
        risk, checked, look = (said.strip().rstrip(".") for _, _, said in named)
        return ASK_RISK_SHOWN.format(risk=risk, checked=checked, look=look), ""
    question, options = fields[0], fields[1:-1]
    recommend = fields[-1] if len(fields) > 1 else ""
    if not question.endswith("?"):
        return "", (
            "it is neither a risk review nor a decision whose first field is a question, and "
            f"{ASK_SEPARATOR.strip()!r} with a space either side separates its fields"
        )
    word, _, rest = recommend.partition(" ")
    pick, dash, why = rest.partition(" - ")
    if word.lower() != ASK_RECOMMEND or not dash or not pick.strip() or not why.strip():
        return "", f"its last field is not '{ASK_RECOMMEND} <option> - <why>'"
    if len(options) < 2:
        return "", "a decision needs at least two options"
    pairs = [option.partition(": ") for option in options]
    if not all(label.strip() and colon and change.strip() for label, colon, change in pairs):
        return "", "each option needs '<option>: <what it changes>'"
    labels = [label.strip().lower() for label, _, _ in pairs]
    if len(set(labels)) < len(labels):
        return "", "two options share a label"
    if pick.strip().lower() not in labels:
        return "", f"it recommends {pick.strip()!r}, which is not one of its options"
    shown = ASK_OPTIONS_JOIN.join(
        ASK_OPTION_SHOWN.format(label=label.strip(), change=change.strip().rstrip("."))
        for label, _, change in pairs
    )
    recommended = ASK_RECOMMEND_SHOWN.format(pick=pick.strip(), why=why.strip().rstrip("."))
    return ASK_DECISION_SHOWN.format(question=question, options=shown, recommend=recommended), ""


def _shown_pattern(template: str, fields: dict[str, str]) -> str:
    """A regular expression for `template`, its text literal and each field replaced by a pattern.

    `string.Formatter().parse` splits a template into its literal text and
    its field names, the same split `str.format` uses, so the pattern cannot
    drift from what `parse_owner_ask` renders.
    """
    pattern = ""
    for literal, field, _, _ in string.Formatter().parse(template):
        pattern += re.escape(literal)
        if field is not None:
            pattern += fields[field]
    return pattern


#: Any field's text: at least one character, as few as will do.
_SHOWN_VALUE = r".+?"

#: A label or a recommended pick, which the rendered line puts in quote marks.
_SHOWN_LABEL = r'[^"]+'

_SHOWN_OPTION = _shown_pattern(ASK_OPTION_SHOWN, {"label": _SHOWN_LABEL, "change": _SHOWN_VALUE})

#: The two forms `parse_owner_ask` renders. A decision needs a question ending
#: in "?" and at least two options, as `parse_owner_ask` does.
_SHOWN_ASKS = (
    re.compile(
        _shown_pattern(
            ASK_RISK_SHOWN, {"risk": _SHOWN_VALUE, "checked": _SHOWN_VALUE, "look": _SHOWN_VALUE}
        ),
        re.IGNORECASE,
    ),
    re.compile(
        _shown_pattern(
            ASK_DECISION_SHOWN,
            {
                "question": _SHOWN_VALUE + r"\?",
                "options": _SHOWN_OPTION
                + "(?:"
                + re.escape(ASK_OPTIONS_JOIN)
                + _SHOWN_OPTION
                + ")+",
                "recommend": _shown_pattern(
                    ASK_RECOMMEND_SHOWN, {"pick": _SHOWN_LABEL, "why": _SHOWN_VALUE}
                ),
            },
        ),
        re.IGNORECASE,
    ),
)


def renders_owner_ask(text: str) -> bool:
    """Whether `text` holds a line in one of the forms `parse_owner_ask` renders.

    This recognizes the form and proves nothing more. It cannot say whether
    the line is the one recorded on the pull request's branch, because only
    `arm` on that branch can. `.claude/hooks/owner_ask_guard.py` uses it for
    the coordinator's posts, whose checkout is on no pull request's branch
    (project owner, 2026-10-24, ratified, over having `arm` answer for a
    named pull request, `PL-YV90`). Pass the text with its whitespace already
    squeezed to single spaces, since a message may wrap the line.
    """
    return any(pattern.search(text) for pattern in _SHOWN_ASKS)


@dataclass(frozen=True)
class Verdict:
    """`arm`'s answer for `HEAD`, and what it rests on.

    `claims` are the unreleased claims bound to this branch, `read` the
    simulator paths a merge would land, `record` the newest `OWNER_READ`
    record that covers them (or, with none, the branch), `ask` the newest
    `OWNER_ASK` record made since the branch's newest change outside the store,
    and `misasked` why such a record did not parse, `outside` the paths it would
    land outside the store, the tooling and the records that arm all the same
    and are named, `gate` whether it would change this module, `moved`
    whether it brings the module in at a path the base does not hold it at,
    `pinned` the
    existing tests in `PINS` pinning its answers that it would change or
    delete, `switched_off` when the owner switched its auto-merge off,
    `unreviewed` how many long docstrings and comments it adds that no
    `PROSE_REVIEW` record covers, `prose_since` the commit carrying the newest
    such record, `prose_declined` why that count could not be read, and
    `behind`
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
    record: OwnerRead | None = None
    ask: OwnerAsk | None = None
    misasked: str = ""
    outside: tuple[str, ...] = ()
    gate: bool = False
    moved: bool = False
    pinned: tuple[str, ...] = ()
    switched_off: str = ""
    unreviewed: int = 0
    prose_since: str = ""
    prose_declined: str = ""
    behind: int = 0
    unpulled: str = ""
    unread: tuple[str, ...] = ()
    merged: MergedPullRequest | None = None

    @property
    def code(self) -> int:
        return NO_ASK if self.unasked else EXIT[self.answer]

    @property
    def asks_owner(self) -> bool:
        """Whether this is a hold that may go to the owner: one for their read, with no claim.

        A claim keeps the pull request a draft, which nobody is asked to read.
        """
        return self.answer == HOLD and self.needs_owner and not self.claims

    @property
    def unasked(self) -> bool:
        """Whether it waits on the owner's read and no valid `OWNER_ASK` record says what to ask."""
        return self.asks_owner and self.ask is None

    @property
    def sendable(self) -> str | None:
        """The ask's opening line, where something may be sent to the owner; None otherwise.

        This is what `bin/docket arm --owner-ask` prints, and what
        `.claude/hooks/owner_ask_guard.py` requires in a reply that asks the
        owner to read or merge the pull request (`PL-TLPH`).
        """
        return self.ask.line if self.asks_owner and self.ask is not None else None

    @property
    def unjudged(self) -> bool:
        """Whether simulator paths change and no record says whether the owner must read them."""
        return bool(self.read) and self.record is None

    @property
    def prose_held(self) -> bool:
        """Whether long prose with no recorded review, or a count that failed, holds it."""
        return self.unreviewed > 0 or bool(self.prose_declined)

    @property
    def needs_owner(self) -> bool:
        """Whether the pull request waits on the owner's read.

        It does for a change to a test pinning the gate's answers, for a move
        of the gate, and for a record saying needed. Any other change to the
        gate itself does not, since 2026-10-19 (`PL-9JHM`). A move does,
        because `PINS` is found from where the module is, so a module moved to
        another depth reads a test file that does not exist and finds no pin.
        """
        return self.moved or bool(self.pinned) or (self.record is not None and self.record.needed)

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
                f"arm - {self.branch} waits on no read from the owner, holds no open claim, "
                f"and contains {self.base}'s tip: mark its pull request ready and arm it"
            ]
            if self.read and self.record is not None:
                count = len(self.read)
                noun = "path" if count == 1 else "paths"
                said.append(
                    f"  It changes {count} simulator {noun}, which the {OWNER_READ} record on "
                    f"{self.record.commit[:12]} judges need no read: {self.record.why}. Say so "
                    "in the pull request body, with the paths:"
                )
                said.append(f"  {self._shown(self.read)}")
            if self.gate:
                said.append(
                    f"  It changes {GATE}, the gate itself, and changes or deletes no test in "
                    f"{PINS} pinning its answers, so it arms on green with the rest of the "
                    "tooling: name it in the report."
                )
            if self.outside:
                count = len(self.outside)
                noun = "path" if count == 1 else "paths"
                said.append(
                    f"  It changes {count} {noun} outside {self._arming}, which arm on green "
                    "unless the change needs the owner's read - this session's judgment, "
                    f"recorded as `{OWNER_READ}: {READ_NEEDED} - <why>`, not this answer's - "
                    f"so name {'it' if count == 1 else 'them'} in the report:"
                )
                said.append(f"  {self._shown(self.outside)}")
            return tuple(said)
        if self.answer == ALREADY_MERGED and (merged := self.merged) is not None:
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
        read = ", so its pull request waits on the owner's read" if self.needs_owner else ""
        # The instruction leads the first line, so that a session reading only
        # that line still sees it (`PL-TLPH`).
        lead = (
            f"send the owner nothing about this pull request yet, because no {OWNER_ASK} "
            "record says what to ask. "
            if self.unasked
            else ""
        )
        said = [f"hold - {lead}{self.branch}: " + " and ".join(self._holding()) + read]
        if self.unpulled:
            said.append(f"  {self.unpulled}")
        for hold in self.claims:
            said.append(f"  {_described(hold)}")
        if self.read:
            said.append(f"  {self._shown(self.read)}")
        said.append(
            "  Leave auto-merge off, disarming it before the push that brings this if it is "
            f"armed and recording that as `{AUTO_MERGE}: {AUTO_MERGE_OFF} - <why>` in the next "
            "commit"
            + (
                ", and keep the pull request a draft while a claim holds it."
                if self.claims
                else "."
            )
        )
        # A session never arms a held pull request, so one that held before
        # this push and is armed was armed by the owner, and the repair rides
        # it, as docs/maintainer.md says (`PL-XTBF`). A draft has no such case.
        if not self.claims:
            said.append(REPAIR_EXCEPTION)
        if self.switched_off:
            said.append(OWNER_OFF)
        # A claim keeps the pull request a draft, which nobody is asked to read.
        if self.unjudged and not self.claims:
            said.append(JUDGE_ASK)
        if self.unreviewed:
            said.append(PROSE_ASK)
        if self.prose_declined:
            said.append(PROSE_UNCOUNTED)
        if read and not self.claims:
            if self.misasked:
                said.append(f"  {self.misasked}")
            if self.ask is None:
                said.append(READ_ASK)
            else:
                said.extend((ASK_LINE, f"  {self.ask.line}"))
        return (*said, *notes)

    @property
    def _arming(self) -> str:
        """The store, the tooling and the records, as `arm` names the paths outside them."""
        named = [self.items_dir]
        if TOOLING is not None:
            named.append(TOOLING.rstrip("/") or "the tooling")
        return f"{', '.join(named)} and {RECORDS.rstrip('/')}"

    @staticmethod
    def _shown(paths: tuple[str, ...]) -> str:
        """The first `SHOWN` paths, and a count of the rest."""
        shown = ", ".join(paths[:SHOWN])
        more = len(paths) - SHOWN
        return f"{shown}{f', and {more} more' if more > 0 else ''}"

    def _holding(self) -> list[str]:
        """The one-clause reasons a `hold` names: claims, the judgment, then the gate."""
        reasons = []
        if self.claims:
            keys = ", ".join(hold.key for hold in self.claims)
            reasons.append(f"a merge would erase its open claim on {keys}")
        if self.unjudged:
            count = len(self.read)
            noun = "path" if count == 1 else "paths"
            reasons.append(
                f"it changes {count} simulator {noun} and no {OWNER_READ} record on a commit "
                "since its newest change there says whether the owner must read it"
            )
        if self.prose_held:
            since = (
                f"the {PROSE_REVIEW} record on {self.prose_since[:12]}"
                if self.prose_since
                else "it forked"
            )
            if self.prose_declined:
                reasons.append(
                    f"how many long docstrings and comments it adds since {since} could not be "
                    f"counted - {self.prose_declined}"
                )
            else:
                noun = "docstring or comment" if self.unreviewed == 1 else "docstrings and comments"
                reasons.append(
                    f"it adds {self.unreviewed} long {noun} in the simulator since {since}, and "
                    f"no {PROSE_REVIEW} record covers {'it' if self.unreviewed == 1 else 'them'}"
                )
        if self.record is not None and self.record.needed:
            reasons.append(
                f"the {OWNER_READ} record on {self.record.commit[:12]} asks for the owner's "
                f"read: {self.record.why}"
            )
        if self.switched_off:
            reasons.append(
                f"auto-merge was switched off at {self.switched_off}, after it was armed, and "
                "no commit since records this session doing it"
            )
        if self.moved:
            reasons.append(
                f"it brings in {GATE}, the gate itself, at a path the base does not hold it at, "
                f"so {PINS} may not be the file that pins its answers"
            )
        if self.pinned:
            count = len(self.pinned)
            tests = "test" if count == 1 else "tests"
            gate = f"it changes {GATE}, the gate itself, and " if self.gate else "it "
            reasons.append(
                f"{gate}changes or deletes {count} {tests} in {PINS} pinning the gate's answers: "
                f"{self._shown(self.pinned)}"
            )
        return reasons


def arm(
    root: Path,
    *,
    items_dir: str,
    now: datetime,
    fetch: bool = True,
    runner: Runner | None = None,
    newest: Callable[[str, str], PullRequestLookup] | None = None,
    auto_merge: Callable[[int], AutoMerge] | None = None,
    prose_count: Callable[[str], ProseCount] | None = None,
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

    **And its auto-merge may have been switched off by the owner** (`PL-8TPV`).
    `auto_merge` asks the forge for the latest switch on an open pull request,
    handed its number. A switch off that no `AUTO_MERGE` record on a commit
    made since covers holds the pull request, and a forge that could not be
    asked is unread.

    **And a simulator change's new long prose may have had no review**
    (`PL-W04Z`). `prose_count` counts the long docstrings and comments the
    branch adds, handed the commit carrying the newest `PROSE_REVIEW` record,
    or `""` where none does. It is asked only where the change reaches a
    simulator path. A count above zero holds the pull request, and so does a
    count that could not be read.
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
    name = head_branch(root, run, remotes)
    # A git that answered nothing is said as that, not as the "no branch" or
    # "no base" it would otherwise read as (`vcs.branch_state` has the case).
    if run.reason or not name:
        reason = run.reason or "HEAD is on no branch, so there is no pull request to answer for"
        return Verdict(UNKNOWN, unread=(reason, *unread))
    base = default_base(root, runner=run)
    if not resolved(base):
        reason = run.reason or f"no default branch could be established to compare {name} with"
        return Verdict(UNKNOWN, branch=name, unread=(reason, *unread))
    branch = name
    if branch == _head_name(base, remotes):
        reason = f"HEAD is on {name}, the default branch, which opens no pull request of its own"
        return Verdict(UNKNOWN, branch=name, base=base, unread=(reason,))
    unpulled = _unpulled(root, run, heads, name, branch)
    switched_off = ""
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
                    ALREADY_MERGED,
                    branch=name,
                    base=base,
                    unpulled=unpulled,
                    unread=tuple(unread),
                    merged=merged,
                )
            if pull.state == PULL_OPEN and auto_merge is not None:
                switch = auto_merge(pull.number)
                if switch.declined:
                    unread.append(
                        f"whether auto-merge on #{pull.number} was switched off could not be "
                        f"asked - {switch.declined}"
                    )
                elif switch.state == AUTO_MERGE_OFF:
                    owned, misread = _switched_off_here(root, run, base, switch.at)
                    unread.extend(misread)
                    if not owned:
                        switched_off = switch.at

    prefix = items_dir.strip("/") + "/"
    # Both sides of a rename, so a file moved into the store shows the deletion
    # it made outside it, which a rename would print as one path under the store.
    changed = run(changed_path_args("diff", "--name-only", f"{base}...HEAD", "--"), root)
    on_list: tuple[str, ...] = ()
    outside: tuple[str, ...] = ()
    worked: tuple[str, ...] = ()
    gate = False
    moved = False
    pinned: tuple[str, ...] = ()
    if answered(changed):
        paths = set(listed_paths(changed))
        worked = tuple(sorted(path for path in paths if not path.startswith((prefix, RECORDS))))
        # The gate is reported apart, and asked for directly rather than read
        # back out of what `arms_on_green` holds.
        gate = GATE in paths
        rest = paths - {GATE}
        if gate:
            fork = run(["merge-base", base, "HEAD"], root).strip()
            held = run(["ls-tree", "-z", "--name-only", fork, "--", GATE], root) if fork else ""
            moved = held.rstrip("\0") != GATE
        tooling, unreadable = _tests_of_the_tooling(sorted(rest), base, root, run)
        unread.extend(unreadable)
        if PINS is not None and PINS in paths:
            pinned, unpinned = _pins_changed(base, root, run)
            unread.extend(unpinned)
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
    unreviewed = 0
    prose_since = ""
    prose_declined = ""
    if on_list and prose_count is not None:
        prose_since, value = _newest_trailer(root, run, ["HEAD", f"^{base}"], PROSE_REVIEW)
        if prose_since and not PROSE_FORM.fullmatch(value):
            unread.append(
                f"the {PROSE_REVIEW} record on {prose_since[:12]} is not 'read N, rewrote M, "
                f"rejected K', so it was not read: {value}"
            )
            prose_since = ""
        prose = prose_count(prose_since)
        prose_declined = prose.declined
        unreviewed = 0 if prose_declined else prose.count
    record, misread = _owner_read(root, run, base, on_list)
    unread.extend(misread)
    ask, misasked = _owner_ask(root, run, base, worked)

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
        record=record,
        ask=ask,
        misasked=misasked,
        outside=outside,
        gate=gate,
        moved=moved,
        pinned=pinned,
        switched_off=switched_off,
        unreviewed=unreviewed,
        prose_since=prose_since,
        prose_declined=prose_declined,
        behind=behind,
        unpulled=unpulled,
        unread=tuple(unread),
    )
    if claims or found.unjudged or found.needs_owner or switched_off or found.prose_held:
        return found
    if unpulled or unread:
        return Verdict(UNKNOWN, branch=name, base=base, unpulled=unpulled, unread=tuple(unread))
    if behind:
        return Verdict(BEHIND, branch=name, base=base, items_dir=found.items_dir, behind=behind)
    return Verdict(
        ARM,
        branch=name,
        base=base,
        items_dir=found.items_dir,
        read=on_list,
        record=record,
        outside=outside,
        gate=gate,
    )


def _switched_off_here(root: Path, run: Runner, base: str, at: str) -> tuple[bool, tuple[str, ...]]:
    """Whether a commit of the branch records this session switching auto-merge off at `at`.

    A record counts when its commit's committer date is `at` or later: a
    session switches it off and then commits, so a record made before the
    switch cannot be for it. A time that does not parse leaves the answer
    unread, and so does a commit date that does not.
    """
    try:
        switched = datetime.fromisoformat(at.replace("Z", "+00:00"))
    except ValueError:
        return False, (f"the forge's time for the switch, {at!r}, is not a time",)
    fmt = f"--format=%cI%x1f%(trailers:key={AUTO_MERGE},valueonly,unfold,separator=%x1e)"
    for line in split_lines(run(["log", fmt, f"{base}..HEAD", "--"], root)):
        when, _, values = line.partition("\x1f")
        said = [value for value in values.split("\x1e") if value.strip()]
        if not any(value.partition(" - ")[0].strip().lower() == AUTO_MERGE_OFF for value in said):
            continue
        try:
            committed = datetime.fromisoformat(when)
        except ValueError:
            return False, (f"a commit's date, {when!r}, is not a time",)
        if committed >= switched:
            return True, ()
    return False, ()


def _since_change(
    root: Path, run: Runner, base: str, paths: Sequence[str], *, merges: bool = True
) -> list[str] | None:
    """The revisions `git log` walks for a record made since the newest commit changing `paths`.

    With no `paths`, every commit of the branch. `None` when no commit of the
    branch changed them, so no record can be for them. Without `merges`, a
    merge does not count as a change, so bringing the base in, which the
    owner's *Update branch* does, leaves a record standing.
    """
    span = ["HEAD", f"^{base}"]
    if paths:
        skip = [] if merges else ["--no-merges"]
        newest = run(
            ["log", "-1", *skip, "--format=%H", f"{base}..HEAD", "--", *paths], root
        ).strip()
        if not newest:
            return None
        parents = run(["rev-parse", f"{newest}^@"], root).split()
        span.extend(f"^{parent}" for parent in parents)
    return span


def _newest_trailer(root: Path, run: Runner, span: Sequence[str], key: str) -> tuple[str, str]:
    """The newest commit in `span` carrying the trailer `key`, and its last value.

    `("", "")` where no commit in `span` carries it.
    """
    fmt = f"--format=%H%x1f%(trailers:key={key},valueonly,unfold,separator=%x1e)"
    for line in split_lines(run(["log", fmt, *span, "--"], root)):
        commit, _, values = line.partition("\x1f")
        said = [value for value in values.split("\x1e") if value.strip()]
        if said:
            return commit, said[-1].strip()
    return "", ""


def _owner_ask(
    root: Path, run: Runner, base: str, paths: Sequence[str]
) -> tuple[OwnerAsk | None, str]:
    """The newest `OWNER_ASK` record since the newest change to `paths`, or why it did not parse.

    `paths` are what the branch changes outside the store and the records, so
    an ask made before a later change to the work does not cover it, while
    the closure, `record` and claim commits that follow the work do not
    disturb it, and nor does a merge of the base: the ask has already gone to
    the owner by then, and a merge brings in no work of the branch's.
    """
    span = _since_change(root, run, base, paths, merges=False)
    if span is None:
        return None, ""
    commit, value = _newest_trailer(root, run, span, OWNER_ASK)
    if not commit:
        return None, ""
    line, why = parse_owner_ask(value)
    if why:
        return None, f"The {OWNER_ASK} record on {commit[:12]} was not read: {why}."
    return OwnerAsk(commit=commit, line=line), ""


def _owner_read(
    root: Path, run: Runner, base: str, paths: Sequence[str]
) -> tuple[OwnerRead | None, tuple[str, ...]]:
    """The newest `OWNER_READ` record that covers `paths`, and what went unread.

    With `paths`, only a commit made since the newest one that changed them
    counts, so a judgment cannot cover a change made after it. With none, any
    commit of the branch counts, since a `needed` record holds a branch
    whatever it changes. The newest commit carrying the trailer decides, and
    its last value where it carries several. A value in neither form is said
    and not read, so it covers nothing: a simulator change it was meant for
    still holds, and anything else is `unknown` rather than armed.
    """
    span = _since_change(root, run, base, paths)
    if span is None:
        return None, ()
    commit, value = _newest_trailer(root, run, span, OWNER_READ)
    if not commit:
        return None, ()
    parsed = parse_owner_read(value)
    if parsed is None:
        return None, (
            f"the {OWNER_READ} record on {commit[:12]} is neither "
            f"'{READ_NEEDED} - <why>' nor '{READ_NOT_NEEDED} - <why>', so it was not read: "
            f"{value}",
        )
    return OwnerRead(commit=commit, needed=parsed[0], why=parsed[1]), ()


def _pins_changed(base: str, root: Path, run: Runner) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The pinned tests in `PINS` the change edits or deletes, and why they went unread.

    The file is read at the merge base and at HEAD, the two sides
    `_tests_of_the_tooling` reads. A side git would not hand over, or one that
    will not parse here, leaves the answer unread, so `arm` never arms on a
    comparison it could not make.
    """
    fork = run(["merge-base", base, "HEAD"], root).strip()
    if not fork:
        return (), (
            f"git gave no merge base of {base} and HEAD, so whether the change edits a test "
            f"in {PINS} pinning the gate's answers was not read",
        )
    sides = [run(["show", f"{rev}:{PINS}"], root) for rev in (fork, "HEAD")]
    if not all(answered(side) for side in sides):
        return (), (
            f"git would not hand over {PINS} on both sides of the change, so whether it edits "
            "a test pinning the gate's answers was not read",
        )
    try:
        return changed_pins(*sides), ()
    except (SyntaxError, ValueError, RecursionError) as error:
        return (), (
            f"{PINS} would not parse under this python3 ({error}), so whether the change edits "
            "a test pinning the gate's answers was not read",
        )


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
            version = ".".join(str(part) for part in sys.version_info[:3])
            unreadable.append(
                f"{path} would not parse under this python3 ({version}): "
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
