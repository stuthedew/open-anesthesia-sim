"""Decide whether `HEAD`'s pull request may be armed for auto-merge (`bin/docket arm`).

Under `.claude/skills/pull-request/SKILL.md`, a session arms a pull request
whose branch carries only item files, so a capture reaches the default branch
even when its session ends before any work does (project owner, 2026-09-23,
ratified, over "a branch carrying only captured items is not a pull request",
`PL-WNCT`). Sessions once decided by judgment which pushes could be armed,
from a catalog of claim shapes such as the empty start commit, or a
queue-only commit that start mode treated as one. Each shape the catalog
missed let a merge take a claim away with its branch while the work went on
(`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`). A claim is now a recorded fact (`claims`),
so this module decides the question from the tree, before arming and before
every later push while a pull request is open.

**Five answers, and an exit status for each.**

- `arm` (0): the net change that a squash would land (`base...HEAD`) waits on
  no read from the owner. That needs all of these:
  - it changes or deletes no existing test that pins this module's answers
    (`PINS`);
  - it touches no simulator path (`READ_PATHS`), or a commit made since its
    newest change there carries the session's `Owner-read: not needed - <why>`
    record and no record on the change says `needed`. A test of the tooling
    under `tests/` is not a simulator path here, and `arms_on_green` decides
    such tests path by path;
  - no claim bound to this branch is unreleased;
  - HEAD holds every commit of the branch's copy on the remote;
  - the branch contains the base's tip.
  The answer names each path that the change lands outside the store,
  outside the queue's own tooling (`subprojects/docket/`) and outside the pull
  requests' recovered bodies (`docs/pr-bodies/`). Under the owner's rule, such
  a path arms on green unless the change raises a question for the owner.
  Whether it does stays the session's judgment, and the rule asks the session
  to give its reason in the report.
- `hold` (1), naming what holds it. A claim keeps the pull request unarmed and
  a draft, whichever push carried it, until the branch's own copy closes or
  blocks the item, or the branch yields the claim. A merge before then would
  take the branch and its claim together while the work goes on. A lapsed
  claim also counts as unreleased, because it is work nobody finished or
  handed back. A simulator path that no `Owner-read` record covers holds it
  until the session records whether the owner needs to read it
  (`JUDGE_ASK`), so a judgment nobody made fails safe rather than merging a
  clinical change unread. A record saying `needed` holds it for the owner's
  read, and so does a change to an existing test that pins this module's
  answers (`PINS`). The pull request then waits for the owner's answer,
  which the session records as `Owner-read: given` with the date and their
  words (`READ_GIVEN`). `merge_hold` gives this same answer for a branch's
  copy on the remote, so that a required check on GitHub refuses the merge
  of a held pull request whoever arms it (`PL-39Y1`).
  A change to this module that edits no such test arms, and the answer names
  it. A switch of auto-merge off that no commit records as the session's also
  holds it (`AUTO_MERGE`). Once no claim holds it, a hold for the owner's
  read prints the ask from the session's `Owner-ask` record, one line for
  each of its parts (`ASK_LINE`). With no record, it says that nothing goes to the owner until
  there is one (`READ_ASK`), opens its first line with "send the owner
  nothing" and exits 3 (`NO_ASK`) rather than 1, so that a session reading
  only the first line, or only the exit status, still learns it (`PL-TLPH`).
  A simulator change holds until its newest `Blind-review` record says
  that at least as many blind review passes ran as it owes (`BLIND_ASK`). A
  count of the passes owed that could not be read holds it too.
- `behind N` (1): nothing holds it, but the base has `N` commits the branch
  lacks, and `main` merges only an up-to-date branch while auto-merge never
  brings the base in (`PL-S5MF`). So the base is brought in first.
- `landed` (1): the forge says the branch's newest pull request has merged,
  and HEAD still stands on the head it merged at (`vcs.carried_merge`), so
  there is nothing to arm. Whatever came after that head is carried onto the
  base by a restart and a new pull request (`PL-8BR0`).
- `unknown` (2): something the answer rests on could not be read, or the
  branch's copy on the remote holds commits HEAD lacks, so HEAD is not what
  its pull request lands. What could not be read may be the branch, an
  established base, a history git would not walk, a claim trailer that does
  not parse, a fetch that failed, or a forge that could not say whether the
  pull request merged. Never `arm` from a partial read.

**`hold` outranks `unknown`.** A claim or a path that waits on a read is
reason enough to hold, whatever else went unread, so the answer is `hold`
with what went unread named beside it. Under either answer, the commits that
the remote's copy holds and HEAD lacks are named first, since everything else
was read from HEAD (`PL-21KN`).
**`landed` outranks every other answer**, since a claim, a path, a base that
moved or a remote copy HEAD lacks changes nothing about a pull request that
has already merged. What went unread is named beside it.

**The decisions behind these rules** are each recorded in their items:

- A claim holds whichever push carried it, until the branch's own copy closes
  or blocks the item, and a pull request that a claim rides is a draft
  (`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`, `PL-3FYK`, `PL-H14W`).
- The queue's tooling and the pull request body records arm on green beside
  the store (`PL-SQTR`, `PL-K6B2`, `PL-979D`).
- Every other path arms on green unless the change raises a question for the
  owner, and a workflow change needs no merge confirmation (`PL-KKHD`,
  `PL-0JGZ`, `PL-JNYL`, `PL-KPM2`).
- A test under `tests/` counts as a test of the tooling, and arms on green,
  when it imports no `anesthesia_sim` on either side of the change
  (`PL-552M`). The import rule is spelt here and imported by
  `tools/workflow_paths_check.py`. It is read from the tree, not from
  `docket.toml`'s `workflow_paths`, so widening what arms still takes an edit
  that this gate holds.
- A simulator change waits for the session's `Owner-read:` judgment, and only
  `needed` waits on the owner (`PL-DKBG`). A hold for the owner's read carries
  its question as an `Owner-ask` record (`PL-9JHM`).
- A change to this module waits on the owner only when it changes or deletes
  an existing test that pins its answers (`PL-9JHM`, `PL-VKHD`, `PL-WW0Q`). A
  loosening that no test pins merges unread, and so would one that also
  rewrote the check that reads the pins, since this module judges its own
  change.
- A simulator change waits for its blind review passes (`PL-HDRN`). Its new
  prose held it too until 2026-11-11, when the owner removed the copy edit of
  each branch (`PL-J1ZM`). A blind review record is not undone by a later change, because close-out
  step 9 says a fix made for a finding needs no further pass.

The dated reasoning for each rule, as this header held it until 2026-11-03,
is in `PL-Q28F`.

No rule of its own holds arming for status changes or release cuts (`PL-MB2W`
§ "Other holds"). A triage pass that moves statuses is the queue-only work
that auto-merge exists for. A cut's notes file lies outside the store and the
tooling, so the path rules already hold it.
"""

from __future__ import annotations

import ast
import fnmatch
import re
import sys
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path, PurePosixPath

from .claiming import _git
from .claims import LAPSED, RELEASED, Hold, holdings
from .digits import whole_number
from .lines import split_lines
from .model import TESTS as TESTS
from .python import imports
from .store import ID_PATTERN
from .vcs import (
    PULL_OPEN,
    RECORDS,
    REMOTE,
    MergedPullRequest,
    NewestPullRequest,
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

#: The answer `arm(owner_ask=True)` gives where the pull request does not wait
#: on the owner's read. That reading stops before the checks that decide
#: between `arm`, `behind` and the other holds, so it names none of them
#: (`PL-3D2F`).
NOT_HELD = "not held"

#: The exit status of each answer. `behind` and `landed` share `hold`'s: all
#: three say "not now", and the line printed says which. `not held` shares it
#: too, since that reading cannot say whether the pull request may be armed.
EXIT = {ARM: 0, HOLD: 1, BEHIND: 1, ALREADY_MERGED: 1, NOT_HELD: 1, UNKNOWN: 2}

#: The exit status of a `hold` that waits on the owner's read while no
#: `OWNER_ASK` record says what to ask, so that nothing may be sent to the
#: owner yet. It differs from `hold`'s 1 so that the status alone says so: on
#: `#1612` and `#1676` a session read `arm` through `head`, missed the line
#: saying to send nothing, and sent the owner a bare read ask (`PL-TLPH`).
#: `--owner-ask` exits with it in exactly that state, and with 1 or 2 in every
#: other state that has nothing to send, so `.claude/hooks/owner_ask_guard.py`
#: can tell a thread held for the owner's read, whose message it tells the
#: owner that nothing is recorded, from a checkout `arm` cannot answer for
#: (`PL-R1HT`, `PL-X4MD`).
NO_ASK = 3

#: How many paths outside the store, the tooling and the records a `hold`
#: names before counting the rest.
SHOWN = 5

#: The commit trailer a session records its judgment in: whether the owner
#: needs to read the branch's change before it merges (project owner,
#: 2026-10-17, `PL-DKBG`). Its value is `READ_NEEDED` or `READ_NOT_NEEDED`,
#: then " - " and the reason, which the report and the pull request body
#: carry. Git reads a trailer from a commit message's last paragraph alone.
#:
#: `READ_GIVEN` is a third value, the owner's own answer on a pull request held
#: for them: `given - <date>, "<the owner's words>"`. It releases every hold
#: that waits on the owner, for the change as it stood when they answered
#: (project owner, 2026-11-11, ratified, over a label only the owner sets,
#: `PL-39Y1`). The session writes it, so it is a record to audit and not a
#: proof: a session's writes are the owner's account's on GitHub, and nothing
#: there tells the two apart.
OWNER_READ = "Owner-read"
READ_NEEDED = "needed"
READ_NOT_NEEDED = "not needed"
READ_GIVEN = "given"

#: The commit trailer that carries what a hold for the owner's read asks him
#: (project owner, 2026-10-18, `PL-9JHM`). `arm` prints it as the ask's
#: opening lines, so the ask is a recorded fact rather than prose a session
#: may skip. It is one form, a run of fields joined by `ASK_SEPARATOR`:
#:
#: `<question>? | <option>: <what it gets>; cost: <what it gives up> |
#: <option>: <what it gets>; cost: <what it gives up> | recommend <option> -
#: <why its gain is worth its cost> | context - <what changed, or what the
#: choice is about> | why - <why the choice is the owner's> | checked - <what
#: was already checked>`
#:
#: It has at least two options, and `checked` may be left out. Every option
#: names its cost, the recommended one included. With only what each option
#: does, a session wrote one good option and one bad one, and the owner asked
#: "why would I ever choose the bad" (project owner, 2026-11-14, `PL-GG4V`). A held
#: pull request is asked as a choice between the change and what it was chosen
#: over, never as merging against holding, because holding gains the owner
#: nothing they can name: "either you shouldn't be asking me in the first place
#: because it's not a real question, or you need to tell me what I need to make
#: an informed decision" (project owner, 2026-11-14, `PL-GG4V`). The reply
#: quotes the text to judge, before and after, under the ask, because a
#: pointer into a file sent the owner to dig for it (project owner,
#: 2026-11-02, `PL-77QB`).
#:
#: Until 2026-11-14 there were two forms, and each carried only part of what
#: `.claude/rules/instruction-writing.md` rule 10 asks of a question. The
#: review form (`changed`, `question`, `why`, `checked`, `reply`) had no
#: options, recommendation or trade-off. The decision form ended at its
#: recommendation, with no context and no reason the choice was the owner's.
#: Sessions left out what the form did not ask for, and the owner corrected
#: the asks one missing element at a time: "you are still asking me to make
#: decisions without any context, recommendations, trade offs etc" (project
#: owner, 2026-11-14, `PL-GG4V`). So a record in either old form is refused,
#: as is the older `risk`, `checked` and `look` review (`PL-BGN1`), and the
#: refusal names the fields to add.
OWNER_ASK = "Owner-ask"
ASK_SEPARATOR = " | "
ASK_RECOMMEND = "recommend"
ASK_CONTEXT = "context"
ASK_WHY = "why"
ASK_CHECKED = "checked"
#: What separates an option's gain from its cost.
ASK_COST = "; cost: "
#: The named fields after the recommendation, in order. The last may be left out.
ASK_NAMED = (ASK_CONTEXT, ASK_WHY, ASK_CHECKED)
#: The first word of every review form refused since 2026-11-02 and 2026-11-14.
ASK_OLD_REVIEW_WORDS = frozenset({"changed", "risk"})

#: What no field of an `OWNER_ASK` record may hold, because the owner reads it
#: in a reply and cannot look it up: code in backquotes, a file name, a
#: command-line flag, a `bin/` command, a snake_case name and an item id. On
#: `#1947` an ask told the owner "tools/model_rewrite.py lost accounts for
#: every figure" and "verify --self ACCEPTs" (project owner, 2026-11-02,
#: `PL-BGN1`). This finds the names a tool or file goes by. Whether the rest
#: of a sentence is plain is judgment, which the printed instructions ask for.
ASK_JARGON = re.compile(
    r"`"
    r"|\b[\w/.-]+\.(?:py|md|toml|ya?ml|json|txt)\b"
    r"|(?<!\S)--[a-z][\w-]*"
    r"|\bbin/\w"
    r"|\b[a-z]+_[a-z_]+\b"
    rf"|\b(?:{ID_PATTERN})"
)

#: How `parse_owner_ask` renders an `OWNER_ASK` record as the lines the owner
#: is sent, in this order: the question, the recommendation, the context, each
#: option, why it is the owner's, and what was checked. Rule 10 of
#: `.claude/rules/instruction-writing.md` puts the question and the
#: recommendation first. That order replaced a review that led with what
#: changed (`PL-BGN1`), and the owner kept it over the context first (project
#: owner, 2026-11-14, ratified, `PL-GG4V`).
#:
#: Each part is a line of its own. All the parts on one line read as a dense
#: paragraph that the owner found hard to follow (project owner, 2026-11-10,
#: `PL-M2JP`). Each part after the question starts with "- ", so that a reply
#: rendered as Markdown keeps the parts on separate lines rather than joining
#: them back into one paragraph.
ASK_QUESTION_SHOWN = "**{question}**"
ASK_RECOMMEND_SHOWN = '- **I recommend "{pick}":** {why}.'
ASK_CONTEXT_SHOWN = "- **Context:** {context}."
ASK_OPTION_SHOWN = '- **Option "{label}":** {gain}. **Costs and risks:** {cost}.'
ASK_WHY_SHOWN = "- **Why it is yours:** {why}."
ASK_CHECKED_SHOWN = "- **Already checked:** {checked}."

#: What a hold for the owner's read prints when no `OWNER_ASK` record covers
#: the change. The ask was prose until 2026-10-18, and sessions skipped it:
#: three closed on a bare "read #N" (`PL-9KHK`), `#1516`'s ask invented two
#: points to judge (`PL-DKBG`), and the view chooser thread sent another bare
#: read on 2026-10-18. The owner's rule is that a pull request with nothing to
#: review does not reach him at all, so the way out of a hold with nothing in
#: it is `Owner-read: not needed`, never a question made up to fill the form.
#: On `#1650` the owner had to ask twice what a recorded ask asked them to
#: judge, so the text also asks for learner terms and, for a choice between
#: interface approaches, a screenshot per option (`PL-KYTY`). On `#1946` a
#: risk ask read "a pinned test of the owner-ask guard changes, so a relayed
#: ask in the new form could be refused", and the owner could not tell what
#: it meant. So every field is written in plain words, and each question
#: asks one thing (project owner, 2026-11-02, `PL-BGN1`). The question is
#: one the owner can decide as the owner or as a clinician. On `#1947` an ask
#: put to him whether reworded paragraphs kept their meaning, which the
#: reviews had already checked: "How am I supposed to judge that?".
READ_ASK = (
    "  Send the owner nothing about this pull request yet: no Owner-ask record on a commit "
    "since its newest change outside the store and the pull request bodies says what to "
    "ask. A hold reaches the owner only with something to decide. A question whose answer "
    "is obvious is wrong, as on #1516, whose ask invented two points to judge (PL-DKBG). "
    "Record one in the last paragraph of a commit, beside its Co-authored-by line, then ask "
    f"again: `{OWNER_ASK}: <question>? | <option>: <what it changes for the owner or a "
    f"learner>{ASK_COST}<what it gives up> | <option>: <what it changes>{ASK_COST}<what it "
    f"gives up> | {ASK_RECOMMEND} <option> - <why its gain is worth its cost> | "
    f"{ASK_CONTEXT} - <what changed, or what the choice is about> | "
    f"{ASK_WHY} - <why the choice is the owner's rather than the session's> | {ASK_CHECKED} - "
    f"<what was already checked>`. Give at least two options a careful person could each "
    f"pick, and leave out {ASK_CHECKED} only when nothing was checked. For a held pull "
    "request, the options are the change and what it was chosen over: what the owner asked "
    "for, the behavior it replaces, a smaller version, or the larger rework it would need. "
    "Merging against holding for changes is not a choice, because holding gains the owner "
    "nothing they can name. The question is one the owner can decide as the owner or as a "
    "clinician. Word the "
    "question in clinical or learner terms and in one clause, so that the owner sees on "
    "first reading what they are judging, and put its background in the context field. "
    "Under each option, say what a learner sees or what changes for the owner, and what "
    "that option gives up, the recommended one included: a choice between one good option "
    "and one bad one is not a choice. Put in each option's cost the consequences the owner "
    "would not see from the option alone: what else it changes or breaks, the follow-on "
    "work it opens, and whether it can be undone. If you cannot say what the option you do "
    "not recommend "
    "gains, there is no choice, and the owner is not asked. A choice "
    "between approaches to the interface goes with one annotated screenshot per option, "
    "attached to the reply that carries the lines (.claude/skills/run-the-app/SKILL.md). "
    "Each field is printed on its own line, the question first and the recommendation "
    "second. Never ask the owner to re-check what the tests or reviews already checked, "
    "such as whether a rewording kept its meaning: they cannot judge that from a reply. "
    "Under the ask, the reply quotes the text to judge, before and after. "
    "Write every field in plain words for a clinician who has not read this repository "
    "(.claude/rules/plain-writing.md): say what the owner or a learner would notice, and "
    "never name a test, check, file or tool by its internal name. If no question can be "
    f"filled honestly, nothing needs the owner: record `{OWNER_READ}: {READ_NOT_NEEDED} - "
    "<why>` instead, and the change merges on green. A change to a test pinning the gate's "
    "answers holds whatever that record says. For one of those, the options are the gate as "
    "changed and the gate as it was, each with what it refuses that the other accepts."
)

#: What a hold for the owner's read prints before the line its `OWNER_ASK`
#: record renders. The line goes in the closing block, because a wording
#: that said only what the ask opens with was followed to the letter
#: (`PL-9KHK`). The text to judge goes in the reply too. On 2026-11-02 an
#: ask said "Please look at: the hazard table's 21 rows", and the owner had
#: to open the file to find them. Their rule: "I want it to just show me the
#: relevant text rather than me trying to dig through", as the default, unasked
#: (project owner, 2026-11-02, `PL-77QB`). A changed sentence quoted alone
#: was still hard to judge: "it's hard to judge an isolated sentence change"
#: without the surrounding context (project owner, 2026-11-02, `PL-BGN1`).
ASK_LINE = (
    "  Open the ask with these lines, word for word and each on its own line, as one item of "
    "the closing block, never as 'read #N', and repeat them whole in every later reply that "
    "still waits on it. Under "
    "it, quote the text the owner is to judge in the reply itself: the changed sentences, "
    "rows or values, before and after, each with enough of its surroundings, such as the "
    "whole paragraph, for the change to make sense. Never send the owner into a file to "
    "find it. Attach "
    "a generated file only for the full set of changes, and still quote the ones that "
    "change meaning:"
)

#: What a hold for the owner's read says about releasing it. Since `PL-39Y1`
#: the `merge-hold` check on GitHub runs this module's rule on every pull
#: request, so a held one cannot merge on the owner's word alone: their answer
#: has to be on the branch.
GIVEN_ASK = (
    "  Once the owner has answered, record their go-ahead on a commit that changes nothing "
    f'else, as `{OWNER_READ}: {READ_GIVEN} - <date>, "<their words>"`, and push it. The '
    "`merge-hold` check on the pull request runs this rule, so the pull request cannot merge "
    "before that. Record only what the owner said: never write a go-ahead they did not give."
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

#: The commit trailer a session records close-out step 9's blind generalist
#: review passes in (`PL-HDRN`). Its value lists every finding by pass, as
#: `parse_blind_review` reads it (`PL-0BRY`). The newest such record covers the
#: branch while its passes are at least the number `blind_count_command` says
#: the branch owes. A later change does not undo it, because close-out step 9
#: says a fix made for a finding needs no further pass. A later change that
#: raises the number owed, such as a first change to the model's code, does.
BLIND_REVIEW = "Blind-review"

#: The severities a blind reviewer gives a finding, in the order its brief
#: names them. `tools/blind_review.py`'s brief reads them from here.
BLIND_SEVERITIES = ("blocking", "should-fix", "optional")

#: What happened to a finding, as close-out step 9 defines each one.
BLIND_OUTCOMES = ("fixed", "filed", "rejected")

#: The word that marks a finding a lower-numbered pass also named.
BLIND_REPEAT = "repeat"

#: The whole entry for a pass that wrote `NO FINDINGS`.
BLIND_NONE = "none"

#: One entry per finding, grouped by pass. The form `BLIND_ASK` gives.
BLIND_EXAMPLE = (
    "pass 1: blocking fixed, optional rejected; pass 2: blocking fixed repeat, should-fix filed"
)

#: The older form, which totals the passes together. Read for its pass count,
#: because 28 records on merged pull requests and branches in flight use it.
_BLIND_TOTALS = re.compile(
    r"passes (\d+), findings (\d+), fixed (\d+), filed (\d+), rejected (\d+)", re.ASCII
)
_BLIND_PASS = re.compile(r"pass (\d+): (.+)", re.ASCII)


@dataclass(frozen=True)
class BlindFinding:
    """One finding of a blind review pass: its severity, its outcome, and whether it repeats one.

    `repeat` is true where a lower-numbered pass also named the fault.
    """

    severity: str
    outcome: str
    repeat: bool = False


@dataclass(frozen=True)
class BlindTotals:
    """The counts the older record form gives, summed over every pass."""

    findings: int
    fixed: int
    filed: int
    rejected: int


@dataclass(frozen=True)
class BlindRecord:
    """What one `BLIND_REVIEW` trailer records about a branch's blind review passes.

    `split` holds each pass's findings, pass 1 first, for a record in the
    per-finding form. It is empty for a record in the older form, which keeps
    only `totals`, summed over every pass. So a reader can always ask how many
    passes ran, and can ask which pass found what only where `split` says.
    """

    passes: int
    split: tuple[tuple[BlindFinding, ...], ...] = ()
    totals: BlindTotals | None = None


def parse_blind_review(value: str) -> BlindRecord:
    """Read a `BLIND_REVIEW` trailer's value, or raise `ValueError` saying why it cannot be read.

    The per-finding form is one `pass N: ...` entry per pass, separated by
    semicolons and numbered from 1 in order. Each entry is `none`, for a pass
    that wrote `NO FINDINGS`, or its findings separated by commas. A finding
    is a severity from `BLIND_SEVERITIES`, then an outcome from
    `BLIND_OUTCOMES`, then `repeat` where a lower-numbered pass named it too,
    so pass 1 can hold no `repeat`. The older form,
    `passes N, findings F, fixed X, filed Y, rejected Z`, is read as a record
    whose findings are not split by pass.
    """
    text = " ".join(value.split())
    totals = _BLIND_TOTALS.fullmatch(text)
    if totals is not None:
        counts = [whole_number(group) for group in totals.groups()]
        if any(count is None for count in counts):
            raise ValueError("a count is not a whole number")
        passes, *sums = (count or 0 for count in counts)
        return BlindRecord(passes, totals=BlindTotals(*sums))
    split: list[tuple[BlindFinding, ...]] = []
    for entry in text.split(";"):
        match = _BLIND_PASS.fullmatch(entry.strip())
        if match is None:
            raise ValueError(f"{entry.strip()!r} is not 'pass N: ...'")
        number = whole_number(match.group(1))
        if number != len(split) + 1:
            raise ValueError(
                f"pass {match.group(1)} is out of order: expected pass {len(split) + 1}"
            )
        body = match.group(2).strip()
        if body == BLIND_NONE:
            split.append(())
            continue
        findings = []
        for said in body.split(","):
            words = said.split()
            if len(words) not in (2, 3) or (len(words) == 3 and words[2] != BLIND_REPEAT):
                raise ValueError(
                    f"pass {number}: {said.strip()!r} is not 'severity outcome [repeat]'"
                )
            if words[0] not in BLIND_SEVERITIES:
                raise ValueError(
                    f"pass {number}: {words[0]!r} is not one of {', '.join(BLIND_SEVERITIES)}"
                )
            if words[1] not in BLIND_OUTCOMES:
                raise ValueError(
                    f"pass {number}: {words[1]!r} is not one of {', '.join(BLIND_OUTCOMES)}"
                )
            repeat = len(words) == 3
            if repeat and number == 1:
                raise ValueError("pass 1 cannot repeat a finding, since no earlier pass ran")
            findings.append(BlindFinding(words[0], words[1], repeat))
        split.append(tuple(findings))
    return BlindRecord(len(split), split=tuple(split))


@dataclass(frozen=True)
class BlindReading:
    """The newest `BLIND_REVIEW` record in a span of commits, as `arm` and the report read it.

    `commit` is `""` where no commit in the span carries one. `record` is
    `None` where none does or where its value could not be read, and then
    `misread` says why. `declined` says why git could not be asked, so a read
    that never happened is not reported as a branch with no record.
    """

    commit: str = ""
    value: str = ""
    record: BlindRecord | None = None
    misread: str = ""
    declined: str = ""


def newest_blind_record(
    root: Path, span: Sequence[str], *, runner: Runner | None = None
) -> BlindReading:
    """The newest `BLIND_REVIEW` record in `span`, a list of revisions as `git log` takes them.

    `arm` reads the branch's record through this, and so does
    `tools/blind_review_report.py`, so the two read one record the same way.
    """
    run = runner or _run_git
    silent: list[str] = []

    def watched(args: list[str], at: Path) -> str:
        said = run(args, at)
        if not answered(said):
            silent.append(f"git did not answer a log of {' '.join(span)}")
        return said

    commit, value = _newest_trailer(root, watched, span, BLIND_REVIEW)
    if silent:
        return BlindReading(declined=silent[0])
    if not commit:
        return BlindReading()
    try:
        return BlindReading(commit, value, parse_blind_review(value))
    except ValueError as error:
        return BlindReading(commit, value, misread=str(error))


#: What a `hold` on missing blind review passes tells the session. The step's
#: own instructions are in the close-out mode, so they are pointed at.
BLIND_ASK = (
    "  Run close-out step 9's blind generalist review passes "
    "(.claude/skills/docket/modes/close-out.md): commit the work, run "
    "`python3 tools/blind_review.py`, start one subagent per brief it prints, and deal with "
    "each finding as the step says. Then record the passes as a trailer in the last paragraph "
    "of a commit made after them, beside its Co-authored-by line, with one entry per "
    f"finding by pass: `{BLIND_REVIEW}: {BLIND_EXAMPLE}`. One commit can "
    f"carry this and an {OWNER_READ} record together. Then ask again."
)

#: What a `hold` tells the session when the passes owed could not be counted.
BLIND_UNCOUNTED = (
    "  A branch whose blind review passes could not be counted is never armed as though it "
    "owed none. Make `python3 tools/blind_review.py --count` answer, and ask again."
)

#: What a `hold` on a simulator path with no record tells the session. The
#: test for a real decision is the design round's, so it is pointed at rather
#: than restated, and the high-risk cases are the ones the owner's rule names
#: in this repository's terms. What a learner can be misled by is the first,
#: because the safety-critical standard in `CLAUDE.md` makes it so. A rewrite
#: of docs/MODEL.md or docs/INTERFACE.md that keeps every value, equation, code
#: span and citation is
#: housekeeping, and only a sentence whose meaning needs a clinician's judgment
#: reaches the owner (project owner, 2026-11-02, ratified, over holding every
#: section part of `PL-ZT47` for the owner's read, `PL-ZTZF`).
JUDGE_ASK = (
    "  Decide whether the owner needs to read it, and record the answer as a trailer in "
    "the last paragraph of a commit made after the change, beside its Co-authored-by "
    f"line: `{OWNER_READ}: {READ_NEEDED} - <why>` or `{OWNER_READ}: {READ_NOT_NEEDED} - "
    "<why>`. It is needed for a real decision, one "
    ".claude/skills/docket/modes/design.md step 4 makes the owner's, and for a high-risk "
    "change: one that changes a clinical value the "
    "simulator computes or displays, or what docs/MODEL.md or docs/INTERFACE.md says one "
    "means, beyond "
    "restating what the change's own tests measure; one that changes a rule sessions run "
    "under that the owner did not ask for in their own words; or one whose breakage CI "
    "would not show or a revert would not undo. Anything else is housekeeping and not "
    "needed: a refactor with its outputs pinned, a tightened test, a figure restated from "
    "a measurement. A rewrite of docs/MODEL.md or docs/INTERFACE.md is not needed when "
    "`python3 "
    "tools/model_rewrite.py lost` adds no equation, code span, citation or number, every "
    "line it prints as dropped is history or a duplicate the document still holds, and no "
    "sentence changes what a value means or what a hazard row or limitation promises. "
    "Where one does, it is needed, and the ask quotes that sentence before and after. "
    "Then ask again."
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

#: The simulator's source tree, at the root. The tools read it through
#: `tools/product_paths.py`, since `docket` cannot import `tools/` (`PL-S08Z`).
SOURCE = "src/"

#: The specification of the implemented model. Spelt once here for the gate's
#: path lists and for every tool, which reads it through `product_paths`.
MODEL_DOC = "docs/MODEL.md"

#: What the interface must show and do. Its sections were part of `MODEL_DOC`
#: until the project owner split that document by reader on 2026-11-11
#: (`PL-P3GZ`, `PL-CTXZ`).
INTERFACE_DOC = "docs/INTERFACE.md"

#: The documents that together specify the simulator. The safety-critical
#: standard in `CLAUDE.md` applies to each. The gate's path lists below and
#: every tool that checks the specification read this tuple, so a document
#: that joins the specification is added here and nowhere else (`PL-CTXZ`).
SPECIFICATION_DOCS = (MODEL_DOC, INTERFACE_DOC)

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
READ_PATHS = (SOURCE, TESTS, *SPECIFICATION_DOCS, "src/anesthesia_sim/data/", "README.md")

#: The simulator's paths as the answers name them.
READ_LIST = (
    f"{SOURCE}, {TESTS} but a test importing no {PRODUCT_PACKAGE}, "
    f"{', '.join(SPECIFICATION_DOCS)}, src/anesthesia_sim/data/ and README.md"
)

#: The paths whose change earns a second blind generalist review pass: the
#: model's code, its parameter files and its specification. `CLAUDE.md`'s
#: fix-in-place rule treats the same three as the clinical floor. A missed
#: defect here can produce a wrong clinical value, so the second pass is spent
#: here and not on every simulator change (project owner, 2026-10-24, ratified,
#: over two passes on every simulator pull request and over one pass
#: everywhere, `PL-TDV9`).
#:
#: Each path is written out, because `tools/config_home_check.py` reads this
#: tuple as text and compares it with `docket.toml`'s `protected_paths`. So
#: the documents of `SPECIFICATION_DOCS` are named here a second time, and
#: that check fails when the two lists differ.
SECOND_PASS_PATHS = (
    "src/anesthesia_sim/core/",
    "src/anesthesia_sim/data/",
    "docs/MODEL.md",
    "docs/INTERFACE.md",
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


def blind_passes(paths: Iterable[str], tooling: Collection[str] = ()) -> int:
    """How many blind generalist review passes a change to `paths` owes before it merges.

    None where no path is the simulator's, as `waits_on_read` decides it. Two
    where a path lies under `SECOND_PASS_PATHS`, and one otherwise.
    `PL-TBQS`'s replay of 20 merged simulator pull requests chose generalist
    passes over a specialist panel, and the owner kept the second pass for the
    clinical paths (`PL-TDV9`). `tools/blind_review.py` reads this.
    """
    simulator = [path for path in paths if waits_on_read(path, tooling)]
    if not simulator:
        return 0
    second = any(
        path == entry or (entry.endswith("/") and path.startswith(entry))
        for path in simulator
        for entry in SECOND_PASS_PATHS
    )
    return 2 if second else 1


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
    copy until 2026-10-24, so that widening it would wait on a read. Since
    2026-10-19 an edit to this module waits on a read only when it edits a
    test pinning its answers or moves the module (`PL-9JHM`), so editing both
    copies together waited on none. What holds a widening now is
    `test_arm_holds_for_a_read_a_path_on_the_owners_read_list`, which pins
    `docs/MODEL.md` and the simulator's paths as held for a read (project
    owner, 2026-10-24, ratified, over restoring the copy that `PL-F6MM` kept;
    `PL-LGDV`, `PL-F9WM`).
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
class CommandCount:
    """A count that a configured command printed, or why it could not be read.

    The command in `blind_count_command` counts the blind review passes a
    branch owes. `count` is the number the command printed.
    `declined` says why it could not be read, so that "could not count" is
    never treated as "nothing owed".
    """

    count: int = 0
    declined: str = ""


@dataclass(frozen=True)
class OwnerRead:
    """A session's recorded judgment of whether the owner needs to read the branch.

    `commit` carries the `OWNER_READ` trailer, `needed` is its answer, and
    `why` is the reason the session gave, which the report repeats. `given`
    says the record is the owner's own go-ahead, and `why` is then the date
    and their words.
    """

    commit: str
    needed: bool
    why: str
    given: bool = False


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


def parse_owner_given(value: str) -> str | None:
    """The date and the owner's words from an `OWNER_READ` value recording their go-ahead.

    The form is `given - <date>, "<the owner's words>"`, with the date as
    `2026-11-11` and the words in double quotes. `None` for any other value. The
    date and the quoted words are required, because a go-ahead that cannot be
    traced to something the owner said cannot be audited.
    """
    word, dash, said = value.partition(" - ")
    if not dash or word.strip().lower() != READ_GIVEN:
        return None
    day, comma, words = said.strip().partition(", ")
    words = words.strip()
    try:
        date.fromisoformat(day.strip())
    except ValueError:
        return None
    quoted = len(words) > 2 and words.startswith('"') and words.endswith('"')
    if not comma or not quoted or not words[1:-1].strip():
        return None
    return f"{day.strip()}, {words}"


@dataclass(frozen=True)
class OwnerAsk:
    """What a hold for the owner's read asks him, from a session's `OWNER_ASK` record.

    `commit` carries the trailer, and `shown` is the ask as `parse_owner_ask`
    renders it: one line for each of its parts, joined by newlines.
    """

    commit: str
    shown: str


def parse_owner_ask(value: str) -> tuple[str, str]:
    """`(shown, "")` from an `OWNER_ASK` value, or `("", why)` where it cannot be read.

    `shown` has one line for each part of the ask, in the order
    `ASK_RECOMMEND_SHOWN` and its neighbours describe. The value needs a
    question ending in "?", at least two options that each say what they
    change, distinct labels, a recommendation naming one of them with its
    reason, and then `ASK_NAMED`'s fields in order, each with a value, of
    which `checked` may be left out. A review form, or a decision that ends at
    its recommendation, is refused with the fields to add (`PL-GG4V`). Whether
    a question's answer is obvious, whether it is one clause, and whether the
    reason names what the other options cost is judgment, so the printed
    instructions say it and this does not try.
    """
    fields = [field.strip() for field in value.split(ASK_SEPARATOR)]
    jargon = ASK_JARGON.search(value)
    if jargon:
        return "", (
            f"it names {jargon.group(0).strip()!r}, which the owner cannot read in a reply; "
            "say in plain words what it checked or changed"
        )
    question = fields[0]
    if question.partition(" -")[0].strip().lower() in ASK_OLD_REVIEW_WORDS:
        return "", (
            "it is in a review form, which gave the owner no options and no recommendation; "
            "ask it as a choice between the change and what it was chosen over, each with what it "
            "gains and gives up"
        )
    if not question.endswith("?"):
        return "", (
            "its first field is not a question ending in '?', and "
            f"{ASK_SEPARATOR.strip()!r} with a space either side separates its fields"
        )
    at = next(
        (
            place
            for place, field in enumerate(fields)
            if place and field.partition(" ")[0].lower() == ASK_RECOMMEND
        ),
        None,
    )
    if at is None:
        return "", f"it has no '{ASK_RECOMMEND} <option> - <why>' field after its options"
    options, named = fields[1:at], fields[at + 1 :]
    _, _, rest = fields[at].partition(" ")
    pick, dash, why = rest.partition(" - ")
    if not dash or not pick.strip() or not why.strip():
        return "", f"its recommendation is not '{ASK_RECOMMEND} <option> - <why>'"
    if len(options) < 2:
        return "", "a question needs at least two options"
    pairs = [option.partition(": ") for option in options]
    costed = [change.partition(ASK_COST) for _, _, change in pairs]
    if not all(label.strip() and colon for label, colon, _ in pairs) or not all(
        gain.strip() and sep and cost.strip() for gain, sep, cost in costed
    ):
        return "", (
            f"each option needs '<option>: <what it gets>{ASK_COST}<what it gives up>', so "
            "that the owner sees what every option costs, the recommended one included"
        )
    labels = [label.strip().lower() for label, _, _ in pairs]
    if len(set(labels)) < len(labels):
        return "", "two options share a label"
    if pick.strip().lower() not in labels:
        return "", f"it recommends {pick.strip()!r}, which is not one of its options"
    parts = [field.partition(" -") for field in named]
    words = tuple(word.strip().lower() for word, _, _ in parts)
    if words not in (ASK_NAMED, ASK_NAMED[:-1]) or not all(
        dash and said.strip() for _, dash, said in parts
    ):
        return "", (
            f"after its recommendation come {ASK_CONTEXT} - <what changed, or what the choice "
            f"is about> and {ASK_WHY} - <why the choice is the owner's>, then {ASK_CHECKED} - "
            "<what was already checked> if anything was"
        )
    said = [text.strip().rstrip(".") for _, _, text in parts]
    lines = [
        ASK_QUESTION_SHOWN.format(question=question),
        ASK_RECOMMEND_SHOWN.format(pick=pick.strip(), why=why.strip().rstrip(".")),
        ASK_CONTEXT_SHOWN.format(context=said[0]),
        *(
            ASK_OPTION_SHOWN.format(
                label=label.strip(), gain=gain.strip().rstrip("."), cost=cost.strip().rstrip(".")
            )
            for (label, _, _), (gain, _, cost) in zip(pairs, costed, strict=True)
        ),
        ASK_WHY_SHOWN.format(why=said[1]),
        *(ASK_CHECKED_SHOWN.format(checked=checked) for checked in said[2:]),
    ]
    return "\n".join(lines), ""


@dataclass(frozen=True)
class Verdict:
    """`arm`'s answer for `HEAD`, and what it rests on.

    - `claims`: the unreleased claims bound to this branch.
    - `read`: the simulator paths a merge would land.
    - `record`: the newest `OWNER_READ` record that covers them (or, with
      none, the branch).
    - `ask`: the newest `OWNER_ASK` record made since the branch's newest
      change outside the store.
    - `misasked`: why such a record did not parse.
    - `outside`: the paths a merge would land outside the store, the tooling
      and the records, which arm all the same and which the answer names.
    - `gate`: whether the branch would change this module.
    - `moved`: whether the branch brings the module in at a path the base
      does not hold it at.
    - `pinned`: the existing tests in `PINS` that pin this module's answers
      and that the branch would change or delete.
    - `switched_off`: when the owner switched the pull request's auto-merge
      off.
    - `blind_owed`: how many blind review passes the branch owes.
    - `blind_recorded`: how many passes the newest `BLIND_REVIEW` record says
      ran.
    - `blind_since`: the commit carrying that record.
    - `blind_declined`: why the passes owed could not be counted.
    - `behind`: how many of the base's commits the branch lacks.
    - `unpulled`: what the branch's copy on the remote holds that HEAD lacks,
      with what brings it in, or why that could not be read. The answer says
      it before anything else.
    - `unread`: why the answer is `unknown`, or what went unread beside a
      `hold` or a `landed`.
    - `merged`: the merged pull request a `landed` names, and what came after
      it.
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
    blind_owed: int = 0
    blind_recorded: int = 0
    blind_since: str = ""
    blind_declined: str = ""
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
        """The ask, one line per part, where something may be sent to the owner; None otherwise.

        This is what `bin/docket arm --owner-ask` prints, and what
        `.claude/hooks/owner_ask_guard.py` attaches to a thread's message that
        names the pull request (`PL-TLPH`, `PL-X4MD`).
        """
        return self.ask.shown if self.asks_owner and self.ask is not None else None

    @property
    def unjudged(self) -> bool:
        """Whether simulator paths change and no record says whether the owner must read them."""
        return bool(self.read) and self.record is None

    @property
    def unpassed(self) -> bool:
        """Whether it owes more blind review passes than its newest record says ran."""
        return not self.blind_declined and self.blind_owed > self.blind_recorded

    @property
    def blind_held(self) -> bool:
        """Whether missing blind review passes, or a count that failed, holds it."""
        return self.unpassed or bool(self.blind_declined)

    @property
    def needs_owner(self) -> bool:
        """Whether the pull request waits on the owner's read.

        It does for a change to a test pinning the gate's answers, for a move
        of the gate, and for a record saying needed. Any other change to the
        gate itself does not, since 2026-10-19 (`PL-9JHM`). A move does,
        because `PINS` is found from where the module is, so a module moved to
        another depth reads a test file that does not exist and finds no pin.

        A record of the owner's go-ahead releases all three, because each
        waits on the owner and they have answered (`PL-39Y1`).
        """
        if self.record is not None and self.record.given:
            return False
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
            if self.record is not None and self.record.given:
                said.append(
                    f"  The owner's go-ahead is recorded on {self.record.commit[:12]}: "
                    f"{self.record.why}. Quote it in the pull request body."
                )
            elif self.read and self.record is not None:
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
        if self.answer == NOT_HELD:
            return (
                f"not held - {self.branch} does not wait on the owner's read, so there is no "
                "ask to send them; `bin/docket arm` says whether it may be armed",
                *notes,
            )
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
                    f"{'it' if count == 1 else 'them'}, then push, never `git pull` and never "
                    "a forced push, and open a new pull request - `bin/docket branch` prints "
                    "the commands."
                )
            else:
                said.append(
                    f"  Everything {self.branch} holds is on {self.base}: restart it there before "
                    "the next commit, which would otherwise land nowhere, then push, never "
                    "`git pull` and never a forced push - `bin/docket branch` prints the "
                    "commands."
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
        if self.unpassed:
            said.append(BLIND_ASK)
        if self.blind_declined:
            said.append(BLIND_UNCOUNTED)
        if read and not self.claims:
            if self.misasked:
                said.append(f"  {self.misasked}")
            if self.ask is None:
                said.append(READ_ASK)
            else:
                said.append(ASK_LINE)
                said.extend(f"  {line}" for line in split_lines(self.ask.shown))
            said.append(GIVEN_ASK)
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
        if self.blind_declined:
            reasons.append(
                f"how many blind review passes it owes could not be counted - {self.blind_declined}"
            )
        elif self.unpassed:
            noun = "pass" if self.blind_owed == 1 else "passes"
            ran = (
                f"the {BLIND_REVIEW} record on {self.blind_since[:12]} records "
                f"{self.blind_recorded}"
                if self.blind_since
                else f"no {BLIND_REVIEW} record says any ran"
            )
            reasons.append(f"it owes {self.blind_owed} blind review {noun}, and {ran}")
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
    record_dir: str = "",
    fetch: bool = True,
    runner: Runner | None = None,
    newest: Callable[[str, str], PullRequestLookup] | None = None,
    auto_merge: Callable[[int], AutoMerge] | None = None,
    blind_count: Callable[[], CommandCount] | None = None,
    owner_ask: bool = False,
) -> Verdict:
    """Whether the pull request for `HEAD`'s branch may be armed, before or after it opens.

    Fetches first unless `fetch` is false, because `behind` read from a stale
    base is a confident wrong answer. A fetch that fails leaves every answer
    but `hold` unknown. `now` is the time against which the claims' leases
    are judged, as in `claims.holdings`, and must carry its offset.

    **HEAD is the pull request only while it holds the branch's copy on the
    remote.** Another writer can push commits that HEAD lacks, for example
    GitHub's *Update branch* or a second session. Everything read from HEAD is
    then read from a commit the pull request has moved past. Once, `arm` said
    `behind 1` of a pull request already level with its base, and armed one
    that landed a path outside the store (`PL-21KN`). So the remote's copy is
    read before anything else (`_unpulled`), from the remote's listing where
    the fetch succeeded. The listing is taken once and handed to `holdings`
    too, so a tracking ref for a branch the remote deleted is neither the copy
    nor a holder (`PL-MT3R`).

    **And its pull request may already have merged.** Where the branch
    carried only item files, nothing in the tree shows that (`PL-8BR0`).
    `newest` is the caller's way to ask the forge about the branch's newest
    pull request, given the branch and the default branch's name. Where that
    pull request has merged and HEAD still stands on the merge, as
    `vcs.carried_merge` confirms, the answer is `landed` at once. A forge that
    could not be asked counts as unread, since arming a pull request that has
    merged is what this check exists to stop.

    **And its auto-merge may have been switched off by the owner** (`PL-8TPV`).
    `auto_merge` asks the forge for the latest switch on an open pull request,
    given its number. A switch off holds the pull request unless an
    `AUTO_MERGE` record on a commit made since covers it. A forge that could
    not be asked counts as unread.

    **And its blind review passes may never have run** (`PL-HDRN`).
    `blind_count` counts the passes the branch owes, and is asked only where
    the change touches a simulator path. The newest `BLIND_REVIEW` record
    must record at least that many, and a count that could not be read holds
    the pull request too.

    **With `owner_ask`, it answers only what may be sent to the owner**
    (`PL-3D2F`). A hook asks that question before every Projects message
    that names a pull request (`.claude/hooks/owner_ask_guard.py`). The full
    answer took 2.2 s on a one-file branch and 28.4 s on one that changed 62
    simulator paths. Only `sendable`, `unasked` and an `unknown` answer are
    read from the verdict, so `_owner_ask_answer` runs only the stages those
    rest on.

    **Each step is a stage** (`PL-R4M6`): `_read_branch`, `_read_forge`,
    `_read_change`, `_read_reviews`, `_read_claims` and `_read_behind` each
    return what they read and what went unread, `_held` gathers them into one
    `hold` verdict, and `_settle` turns that into the answer. The full answer
    and the owner-ask answer compose the same stages, so a change to a step
    applies to both.
    """
    where = _read_branch(root, fetch=fetch, runner=runner)
    if isinstance(where, Verdict):
        return where
    if owner_ask:
        return _owner_ask_answer(
            root, where, items_dir=items_dir, record_dir=record_dir, now=now, newest=newest
        )
    forge = _Forge() if newest is None else _read_forge(root, where, newest, auto_merge)
    if forge.merged is not None:
        return Verdict(
            ALREADY_MERGED,
            branch=where.name,
            base=where.base,
            unpulled=where.unpulled,
            unread=(*where.unread, *forge.unread),
            merged=forge.merged,
        )
    change = _read_change(root, where, items_dir, record_dir)
    reviews = _read_reviews(root, where, change, blind_count)
    record, misread = _owner_read(
        root, where.run, where.base, change.on_list, worked=change.worked, tip=where.tip
    )
    ask, misasked = _owner_ask(root, where.run, where.base, change.worked, tip=where.tip)
    claims, unclaimed = _read_claims(root, where, now=now, items_dir=items_dir)
    behind, uncounted = _read_behind(root, where)
    unread = (
        *where.unread,
        *forge.unread,
        *change.unread,
        *reviews.unread,
        *misread,
        *unclaimed,
        *uncounted,
        *_silenced(where),
    )
    return _settle(
        _held(
            where,
            change,
            record=record,
            ask=ask,
            misasked=misasked,
            claims=claims,
            switched_off=forge.switched_off,
            reviews=reviews,
            behind=behind,
            unread=unread,
        )
    )


@dataclass(frozen=True)
class _Branch:
    """Where `HEAD`'s branch stands, which every later stage of `arm` reads from.

    `ran` is the caller's runner, or plain git once a fetch has moved the refs.
    `run` wraps it and remembers every call git did not answer, so the stages
    that share it report one partial read. `unread` holds the fetch's failure.
    `tip` is the commit every stage reads the branch at: `HEAD` for `arm`, and
    the remote's copy where `owner_ask_on` answers for a branch that is not
    checked out (`PL-52SV`).
    """

    name: str
    base: str
    remotes: frozenset[str]
    heads: RemoteHeads | None
    ran: Runner
    run: _Silences
    unpulled: str
    unread: tuple[str, ...]
    tip: str = "HEAD"


def _read_branch(root: Path, *, fetch: bool, runner: Runner | None) -> _Branch | Verdict:
    """Fetch, then find the branch, its base and its copy on the remote.

    Returns an `unknown` verdict where there is no branch to answer for: git
    did not answer, `HEAD` is detached, no base resolved, or `HEAD` is on the
    default branch.
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
    if name == _head_name(base, remotes):
        reason = f"HEAD is on {name}, the default branch, which opens no pull request of its own"
        return Verdict(UNKNOWN, branch=name, base=base, unread=(reason,))
    unpulled = _unpulled(root, run, heads, name, name)
    return _Branch(name, base, remotes, heads, ran, run, unpulled, tuple(unread))


@dataclass(frozen=True)
class _Forge:
    """What the forge said: the merge `HEAD` still stands on, and an owner's switch-off."""

    merged: MergedPullRequest | None = None
    switched_off: str = ""
    unread: tuple[str, ...] = ()


def _read_forge(
    root: Path,
    where: _Branch,
    newest: Callable[[str, str], PullRequestLookup],
    auto_merge: Callable[[int], AutoMerge] | None,
) -> _Forge:
    """Ask the forge whether the pull request merged, and whether its auto-merge was switched off.

    A merge returns at once, since nothing else changes the answer then. A
    switch off counts only where no commit since records it as the session's
    own (`AUTO_MERGE`).
    """
    pull, merged, unread = _newest_merge(
        root, where.ran, newest, where.name, where.base, where.remotes
    )
    if merged is not None:
        return _Forge(merged=merged, unread=unread)
    if pull is None or pull.state != PULL_OPEN or auto_merge is None:
        return _Forge(unread=unread)
    switch = auto_merge(pull.number)
    if switch.declined:
        said = (
            f"whether auto-merge on #{pull.number} was switched off could not be "
            f"asked - {switch.declined}"
        )
        return _Forge(unread=(*unread, said))
    if switch.state != AUTO_MERGE_OFF:
        return _Forge(unread=unread)
    owned, misread = _switched_off_here(root, where.run, where.base, switch.at, tip=where.tip)
    return _Forge(switched_off="" if owned else switch.at, unread=(*unread, *misread))


@dataclass(frozen=True)
class _Change:
    """The paths a squash of the branch would land, sorted by what each waits on.

    `on_list` waits on a read, `outside` arms on green beside the store, and
    `worked` is every path outside the store and the body records. `gate` says
    whether this module changed, `moved` whether it moved, and `pinned` names
    the existing tests of its answers that changed.
    """

    prefix: str
    on_list: tuple[str, ...] = ()
    outside: tuple[str, ...] = ()
    worked: tuple[str, ...] = ()
    gate: bool = False
    moved: bool = False
    pinned: tuple[str, ...] = ()
    unread: tuple[str, ...] = ()


def _read_change(root: Path, where: _Branch, items_dir: str, record_dir: str = "") -> _Change:
    """Read the net change `base...tip` and sort its paths.

    `worked` leaves out the store, the pull requests' body records and
    `record_dir`, the directory where `docket record` copies the guard
    refusals a branch met. A copy made after an `OWNER_ASK` record is not new
    work, so it must not end that record's cover (`PL-1XQP`).
    """
    run, base, tip = where.run, where.base, where.tip
    prefix = items_dir.strip("/") + "/"
    records = (prefix, RECORDS, record_dir.strip("/") + "/") if record_dir else (prefix, RECORDS)
    # Both sides of a rename, so a file moved into the store shows the deletion
    # it made outside it, which a rename would print as one path under the store.
    changed = run(changed_path_args("diff", "--name-only", f"{base}...{tip}", "--"), root)
    if not answered(changed):
        said = f"git would not diff {where.name} against {base}, so what a merge lands is unknown"
        return _Change(prefix, unread=(said,))
    paths = set(listed_paths(changed))
    worked = tuple(sorted(path for path in paths if not path.startswith(records)))
    # The gate is reported apart, and asked for directly rather than read
    # back out of what `arms_on_green` holds.
    gate = GATE in paths
    rest = paths - {GATE}
    moved = False
    if gate:
        fork = run(["merge-base", base, tip], root).strip()
        held = run(["ls-tree", "-z", "--name-only", fork, "--", GATE], root) if fork else ""
        moved = held.rstrip("\0") != GATE
    tooling, unread = _tests_of_the_tooling(sorted(rest), base, root, run, tip=tip)
    pinned: tuple[str, ...] = ()
    if PINS is not None and PINS in paths:
        pinned, unpinned = _pins_changed(base, root, run, tip=tip)
        unread = (*unread, *unpinned)
    on_list = tuple(sorted(path for path in rest if not arms_on_green(path, tooling)))
    outside = tuple(
        sorted(
            path
            for path in rest
            if arms_on_green(path, tooling) and outside_the_store(path, prefix)
        )
    )
    return _Change(prefix, on_list, outside, worked, gate, moved, pinned, tuple(unread))


@dataclass(frozen=True)
class _Reviews:
    """The blind review passes a simulator change owes, and what the record says ran."""

    blind_owed: int = 0
    blind_recorded: int = 0
    blind_since: str = ""
    blind_declined: str = ""
    unread: tuple[str, ...] = ()


def _read_reviews(
    root: Path, where: _Branch, change: _Change, blind_count: Callable[[], CommandCount] | None
) -> _Reviews:
    """Count the reviews owed, where the change reaches a path that waits on a read."""
    if not change.on_list:
        return _Reviews()
    run, span = where.run, [where.tip, f"^{where.base}"]
    unread: list[str] = []
    blind_owed = 0
    blind_recorded = 0
    blind_since = ""
    blind_declined = ""
    if blind_count is not None:
        blind = newest_blind_record(root, span, runner=run)
        if blind.record is None and blind.commit:
            unread.append(
                f"the {BLIND_REVIEW} record on {blind.commit[:12]} could not be read "
                f"({blind.misread}), so it covers nothing: {blind.value}"
            )
        if blind.declined:
            unread.append(f"the {BLIND_REVIEW} record could not be read: {blind.declined}")
        blind_since = blind.commit if blind.record is not None else ""
        blind_recorded = blind.record.passes if blind.record is not None else 0
        passes = blind_count()
        blind_declined = passes.declined
        blind_owed = 0 if blind_declined else passes.count
    return _Reviews(blind_owed, blind_recorded, blind_since, blind_declined, tuple(unread))


def _read_claims(
    root: Path, where: _Branch, *, now: datetime, items_dir: str
) -> tuple[tuple[Hold, ...], tuple[str, ...]]:
    """The unreleased claims bound to this branch, and the claim records that could not be read."""
    unread: list[str] = []
    read = holdings(root, now=now, items_dir=items_dir, remote=where.heads, runner=where.ran)
    if not read.known:
        unread.append(f"who holds what could not be read - {read.declined}")
    mine = where.name
    claims = tuple(
        hold
        for hold in read.holds
        if hold.state != RELEASED and _head_name(hold.ref, where.remotes) == mine
    )
    for ref in read.unreadable:
        if _head_name(ref, where.remotes) == mine:
            unread.append(
                f"{ref} could not be compared with {where.base}, so a claim on it was not read"
            )
    for line in read.malformed:
        # `<hash> on <ref>: Claim: <text>`, as `claims` writes it; a ref name
        # can hold neither a space nor a colon.
        at, _, _ = line.partition(": ")
        if _head_name(at.partition(" on ")[2], where.remotes) == mine:
            unread.append(f"a trailer on {mine} is not a claim record, so it was not read: {line}")
    return claims, tuple(unread)


def _read_behind(root: Path, where: _Branch) -> tuple[int, tuple[str, ...]]:
    """How many of the base's commits the branch lacks."""
    counted = whole_number(
        where.run(["rev-list", "--count", f"{where.tip}..{where.base}"], root).strip()
    )
    if counted is None:
        return 0, (f"git would not count {where.base}'s commits that {where.name} lacks",)
    return counted, ()


def _silenced(where: _Branch) -> tuple[str, ...]:
    """The calls git did not answer during the read, as one line, or nothing."""
    return (where.run.reason,) if where.run.reason else ()


def _held(
    where: _Branch,
    change: _Change,
    *,
    record: OwnerRead | None,
    ask: OwnerAsk | None,
    misasked: str,
    claims: tuple[Hold, ...],
    switched_off: str,
    reviews: _Reviews,
    behind: int,
    unread: tuple[str, ...],
) -> Verdict:
    """The `hold` verdict carrying everything read, which `_settle` turns into the answer."""
    return Verdict(
        HOLD,
        branch=where.name,
        base=where.base,
        items_dir=change.prefix.rstrip("/"),
        claims=claims,
        read=change.on_list,
        record=record,
        ask=ask,
        misasked=misasked,
        outside=change.outside,
        gate=change.gate,
        moved=change.moved,
        pinned=change.pinned,
        switched_off=switched_off,
        blind_owed=reviews.blind_owed,
        blind_recorded=reviews.blind_recorded,
        blind_since=reviews.blind_since,
        blind_declined=reviews.blind_declined,
        behind=behind,
        unpulled=where.unpulled,
        unread=unread,
    )


def _settle(found: Verdict) -> Verdict:
    """The answer from everything read: `hold`, then `unknown`, then `behind`, then `arm`."""
    if (
        found.claims
        or found.unjudged
        or found.needs_owner
        or found.switched_off
        or found.blind_held
    ):
        return found
    if found.unpulled or found.unread:
        return Verdict(
            UNKNOWN,
            branch=found.branch,
            base=found.base,
            unpulled=found.unpulled,
            unread=found.unread,
        )
    if found.behind:
        return Verdict(
            BEHIND,
            branch=found.branch,
            base=found.base,
            items_dir=found.items_dir,
            behind=found.behind,
        )
    return Verdict(
        ARM,
        branch=found.branch,
        base=found.base,
        items_dir=found.items_dir,
        read=found.read,
        record=found.record,
        outside=found.outside,
        gate=found.gate,
    )


def _owner_ask_answer(
    root: Path,
    where: _Branch,
    *,
    items_dir: str,
    record_dir: str = "",
    now: datetime,
    newest: Callable[[str, str], PullRequestLookup] | None,
) -> Verdict:
    """`arm --owner-ask`: only what may be sent to the owner (`PL-3D2F`).

    It reads the change and the `OWNER_READ` record first. Where nothing holds
    the pull request for the owner's read, it answers `not held` and reads no
    claim and no ask. Otherwise it reads the ask and the claims, and asks the
    forge only where the answer would go to the owner, because only a merge
    already made changes that answer. It never counts reviews, reads the
    auto-merge switch or counts commits behind, since those can only add a
    hold.
    """
    change = _read_change(root, where, items_dir, record_dir)
    record, misread = _owner_read(
        root, where.run, where.base, change.on_list, worked=change.worked, tip=where.tip
    )
    if not Verdict(HOLD, moved=change.moved, pinned=change.pinned, record=record).needs_owner:
        unread = (*where.unread, *change.unread, *misread, *_silenced(where))
        if where.unpulled or unread:
            return Verdict(
                UNKNOWN, branch=where.name, base=where.base, unpulled=where.unpulled, unread=unread
            )
        return Verdict(NOT_HELD, branch=where.name, base=where.base)
    ask, misasked = _owner_ask(root, where.run, where.base, change.worked, tip=where.tip)
    claims, unclaimed = _read_claims(root, where, now=now, items_dir=items_dir)
    found = _held(
        where,
        change,
        record=record,
        ask=ask,
        misasked=misasked,
        claims=claims,
        switched_off="",
        reviews=_Reviews(),
        behind=0,
        unread=(*where.unread, *change.unread, *misread, *unclaimed, *_silenced(where)),
    )
    if found.asks_owner and newest is not None:
        _, merged, unasked = _newest_merge(
            root, where.ran, newest, where.name, where.base, where.remotes
        )
        if merged is not None:
            return Verdict(
                ALREADY_MERGED,
                branch=where.name,
                base=where.base,
                unpulled=where.unpulled,
                unread=(*found.unread, *unasked),
                merged=merged,
            )
        if unasked:
            found = replace(found, unread=(*found.unread, *unasked))
    return _settle(found)


def owner_ask_on(
    root: Path,
    branch: str,
    *,
    items_dir: str,
    now: datetime,
    record_dir: str = "",
    runner: Runner | None = None,
) -> Verdict:
    """`arm --owner-ask` for `branch`'s copy on the remote, whichever branch is checked out.

    The coordinator's checkout is on no pull request's branch, so `arm`, which
    reads `HEAD`, cannot say whether another thread's pull request waits on
    the owner with no question recorded (`PL-52SV`). This answers it from the
    remote's copy of `branch`, through the same stages `arm --owner-ask` runs,
    so the two cannot disagree. It neither fetches nor asks the forge: the
    caller reads the refs once for every branch, and asks this only of a pull
    request it knows to be open.
    """
    ran = runner or _run_git
    run = _Silences(ran)
    remotes = _remotes(root, run)
    base = default_base(root, runner=run)
    if run.reason or not resolved(base):
        reason = run.reason or f"no default branch could be established to compare {branch} with"
        return Verdict(UNKNOWN, branch=branch, unread=(reason,))
    if branch == _head_name(base, remotes):
        return Verdict(NOT_HELD, branch=branch, base=base)
    tip = f"refs/remotes/{REMOTE}/{branch}"
    if not run(["rev-parse", "--verify", "--quiet", f"{tip}^{{commit}}"], root).strip():
        reason = run.reason or f"{tip} is not in this checkout, so {branch} could not be read"
        return Verdict(UNKNOWN, branch=branch, base=base, unread=(reason,))
    where = _Branch(branch, base, remotes, None, ran, run, "", (), tip=tip)
    return _owner_ask_answer(
        root, where, items_dir=items_dir, record_dir=record_dir, now=now, newest=None
    )


def merge_hold(
    root: Path,
    branch: str,
    *,
    items_dir: str,
    now: datetime,
    record_dir: str = "",
    runner: Runner | None = None,
) -> Verdict:
    """`arm`'s answer for `branch`'s copy on the remote, for a check that gates the merge.

    A session could arm a pull request that `arm` held, because only the
    session read the answer (`PL-39Y1`). A required check on GitHub asks this
    for every pull request, from a checkout of the default branch, so the
    rule it runs is the default branch's and not the pull request's. It runs
    the stages `arm` runs, through the remote's copy of `branch` as
    `owner_ask_on` reads it, so the two cannot disagree.

    Two things `arm` reads are left out. The forge is not asked, because
    whether the pull request already merged and whether its auto-merge was
    switched off are about arming. The blind review passes are not counted,
    because that count runs the project's own command on the branch's files,
    and a check that runs with the default branch's rights must not run what
    a pull request brought. The caller says
    so beside a pass. A `behind` answer is returned as it is: GitHub's own
    rule keeps a branch behind its base from merging.
    """
    ran = runner or _run_git
    run = _Silences(ran)
    remotes = _remotes(root, run)
    base = default_base(root, runner=run)
    if run.reason or not resolved(base):
        reason = run.reason or f"no default branch could be established to compare {branch} with"
        return Verdict(UNKNOWN, branch=branch, unread=(reason,))
    if branch == _head_name(base, remotes):
        reason = f"{branch} is the default branch, which opens no pull request of its own"
        return Verdict(UNKNOWN, branch=branch, base=base, unread=(reason,))
    tip = f"refs/remotes/{REMOTE}/{branch}"
    if not run(["rev-parse", "--verify", "--quiet", f"{tip}^{{commit}}"], root).strip():
        reason = run.reason or f"{tip} is not in this checkout, so {branch} could not be read"
        return Verdict(UNKNOWN, branch=branch, base=base, unread=(reason,))
    where = _Branch(branch, base, remotes, None, ran, run, "", (), tip=tip)
    change = _read_change(root, where, items_dir, record_dir)
    record, misread = _owner_read(
        root, where.run, where.base, change.on_list, worked=change.worked, tip=where.tip
    )
    ask, misasked = _owner_ask(root, where.run, where.base, change.worked, tip=where.tip)
    claims, unclaimed = _read_claims(root, where, now=now, items_dir=items_dir)
    behind, uncounted = _read_behind(root, where)
    unread = (*change.unread, *misread, *unclaimed, *uncounted, *_silenced(where))
    return _settle(
        _held(
            where,
            change,
            record=record,
            ask=ask,
            misasked=misasked,
            claims=claims,
            switched_off="",
            reviews=_Reviews(),
            behind=behind,
            unread=unread,
        )
    )


@dataclass(frozen=True)
class Unasked:
    """Open pull requests that wait on the owner's read with no question recorded (`PL-52SV`).

    `pulls` is each such branch with its pull request's number, or `None`
    where the forge named the branch without one. `unread` names each open
    pull request whose answer could not be read, so a gap is never reported
    as "none waits".
    """

    pulls: tuple[tuple[str, int | None], ...] = ()
    unread: tuple[str, ...] = ()


def unasked_pull_requests(
    root: Path,
    opened: Mapping[str, int | None],
    *,
    items_dir: str,
    now: datetime,
    record_dir: str = "",
    runner: Runner | None = None,
) -> Unasked:
    """Which of the open pull requests in `opened` wait on the owner with no question recorded.

    `opened` maps each branch with an open pull request to its number, as
    `docket flight` reads it from the forge. Each branch is answered by
    `owner_ask_on`, so a branch is listed exactly when `arm --owner-ask` run
    on it would exit with `NO_ASK`.
    """
    pulls: list[tuple[str, int | None]] = []
    unread: list[str] = []
    for branch in sorted(opened):
        verdict = owner_ask_on(
            root, branch, items_dir=items_dir, now=now, record_dir=record_dir, runner=runner
        )
        if verdict.unasked:
            pulls.append((branch, opened[branch]))
        elif verdict.answer == UNKNOWN:
            first = verdict.unread[0] if verdict.unread else "nothing it rests on could be read"
            unread.append(f"{branch}: {first}")
    return Unasked(tuple(pulls), tuple(unread))


def _newest_merge(
    root: Path,
    ran: Runner,
    newest: Callable[[str, str], PullRequestLookup],
    name: str,
    base: str,
    remotes: frozenset[str],
) -> tuple[NewestPullRequest | None, MergedPullRequest | None, tuple[str, ...]]:
    """The branch's newest pull request, the merge of it HEAD still stands on, and what went unread.

    The merge is `vcs.carried_merge`'s, and None where the pull request has
    not merged or HEAD has moved past the head it merged at.
    """
    asked = newest(name, _head_name(base, remotes))
    pull = asked.newest
    if asked.declined:
        return (
            None,
            None,
            (
                f"whether {name}'s pull request has already merged could not be asked - "
                f"{asked.declined}",
            ),
        )
    if pull is None:
        return None, None, ()
    probe = _Silences(ran)
    merged = carried_merge(pull, base, root, runner=probe)
    if probe.reason:
        return (
            pull,
            None,
            (
                f"git could not compare {name} with {pull.head[:12]}, the head "
                f"#{pull.number} merged at - {probe.reason}",
            ),
        )
    return pull, merged, ()


def _switched_off_here(
    root: Path, run: Runner, base: str, at: str, *, tip: str = "HEAD"
) -> tuple[bool, tuple[str, ...]]:
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
    for line in split_lines(run(["log", fmt, f"{base}..{tip}", "--"], root)):
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
    root: Path, run: Runner, base: str, paths: Sequence[str], *, tip: str = "HEAD"
) -> list[str] | None:
    """The revisions `git log` walks for a record made since the newest commit changing `paths`.

    With no `paths`, every commit of the branch. `None` when no commit of the
    branch changed them, so no record can be for them. A merge counts as a
    change only where it alters the branch's own change to `paths`, which
    `_merge_keeps_the_work` decides. So bringing the base in, which the
    owner's *Update branch* does, leaves a record standing, and a conflict
    resolved there by writing new lines does not.
    """
    span = [tip, f"^{base}"]
    if paths:
        for commit in split_lines(
            run(["log", "--format=%H", f"{base}..{tip}", "--", *paths], root)
        ):
            parents = run(["rev-parse", f"{commit}^@"], root).split()
            if len(parents) > 1 and _merge_keeps_the_work(root, run, commit, parents, paths):
                continue
            span.extend(f"^{parent}" for parent in parents)
            return span
        return None
    return span


def _merge_keeps_the_work(
    root: Path, run: Runner, merge: str, parents: Sequence[str], paths: Sequence[str]
) -> bool:
    """Whether `merge` leaves the branch's own change to `paths` exactly as it was.

    `parents[0]` is the branch's side and `parents[1]` the side brought in, as
    `git merge` and the forge's *Update branch* both write them. The branch's
    change before the merge is its first parent against the fork point, and
    after it is the merge against the side brought in. The two are compared
    without hunk line numbers, which the base's own edits shift. Where they
    match, the merge brought in no work of the branch's. Anything git did not
    answer, or a merge of more than two parents, counts as a change, so a
    record is dropped rather than stretched over work nobody judged.
    """
    if len(parents) != 2:
        return False
    fork = run(["merge-base", parents[0], parents[1]], root).strip()
    if not fork:
        return False
    before = _own_change(root, run, fork, parents[0], paths)
    after = _own_change(root, run, parents[1], merge, paths)
    return before is not None and before == after


def _own_change(
    root: Path, run: Runner, old: str, new: str, paths: Sequence[str]
) -> list[str] | None:
    """The lines of `git diff old new -- paths`, with no context and no hunk positions.

    `None` where git did not answer.
    """
    diff = run(
        ["diff", "-U0", "--no-color", "--no-ext-diff", "--no-renames", old, new, "--", *paths], root
    )
    if not answered(diff):
        return None
    return [line for line in split_lines(diff) if not line.startswith(("@@", "index "))]


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
    root: Path, run: Runner, base: str, paths: Sequence[str], *, tip: str = "HEAD"
) -> tuple[OwnerAsk | None, str]:
    """The newest `OWNER_ASK` record since the newest change to `paths`, or why it did not parse.

    `paths` are what the branch changes outside the store and the records, so
    an ask made before a later change to the work does not cover it, while
    the closure, `record` and claim commits that follow the work do not
    disturb it, and nor does a merge of the base that leaves the branch's own
    change as it was (`_since_change`).
    """
    span = _since_change(root, run, base, paths, tip=tip)
    if span is None:
        return None, ""
    commit, value = _newest_trailer(root, run, span, OWNER_ASK)
    if not commit:
        return None, ""
    shown, why = parse_owner_ask(value)
    if why:
        return None, f"The {OWNER_ASK} record on {commit[:12]} was not read: {why}."
    return OwnerAsk(commit=commit, shown=shown), ""


def _owner_read(
    root: Path,
    run: Runner,
    base: str,
    paths: Sequence[str],
    *,
    worked: Sequence[str] = (),
    tip: str = "HEAD",
) -> tuple[OwnerRead | None, tuple[str, ...]]:
    """The newest `OWNER_READ` record that covers `paths`, and what went unread.

    With `paths`, only a commit made since the newest one that changed them
    counts, so a judgment cannot cover a change made after it. A merge of the
    base that leaves the branch's own change to them as it was is not such a
    change, exactly as for the `OWNER_ASK` record: the judgment was about that
    change, and the merge brings in only work the base already holds. With
    none, any commit of the branch counts, since a `needed` record holds a
    branch whatever it changes. The newest commit carrying the trailer decides, and
    its last value where it carries several. A value in neither form is said
    and not read, so it covers nothing: a simulator change it was meant for
    still holds, and anything else is `unknown` rather than armed.

    A record of the owner's go-ahead covers the branch only where no commit
    since has changed `worked`, the paths outside the store and the records.
    The owner answered for the change they were shown. A go-ahead that an
    earlier commit carries is therefore read as a record saying needed, so the
    hold it released applies again (`PL-39Y1`).
    """
    span = _since_change(root, run, base, paths, tip=tip)
    if span is None:
        return None, ()
    commit, value = _newest_trailer(root, run, span, OWNER_READ)
    if not commit:
        return None, ()
    words = parse_owner_given(value)
    if words is not None:
        late = _since_change(root, run, base, worked, tip=tip)
        if late is not None and _newest_trailer(root, run, late, OWNER_READ)[0] == commit:
            return OwnerRead(commit=commit, needed=False, why=words, given=True), ()
        stale = (
            "the owner's go-ahead recorded there came before the branch's newest change "
            "outside the store, which they have not read"
        )
        return OwnerRead(commit=commit, needed=True, why=stale), ()
    parsed = parse_owner_read(value)
    if parsed is None:
        return None, (
            f"the {OWNER_READ} record on {commit[:12]} is not '{READ_NEEDED} - <why>', "
            f"'{READ_NOT_NEEDED} - <why>' or '{READ_GIVEN} - <date>, \"<the owner's words>\"', "
            f"so it was not read: {value}",
        )
    return OwnerRead(commit=commit, needed=parsed[0], why=parsed[1]), ()


def _pins_changed(
    base: str, root: Path, run: Runner, *, tip: str = "HEAD"
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The pinned tests in `PINS` the change edits or deletes, and why they went unread.

    The file is read at the merge base and at HEAD, the two sides
    `_tests_of_the_tooling` reads. A side git would not hand over, or one that
    will not parse here, leaves the answer unread, so `arm` never arms on a
    comparison it could not make.
    """
    fork = run(["merge-base", base, tip], root).strip()
    if not fork:
        return (), (
            f"git gave no merge base of {base} and {tip}, so whether the change edits a test "
            f"in {PINS} pinning the gate's answers was not read",
        )
    sides = [run(["show", f"{rev}:{PINS}"], root) for rev in (fork, tip)]
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
    paths: Sequence[str], base: str, root: Path, run: Runner, *, tip: str = "HEAD"
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
    fork = run(["merge-base", base, tip], root).strip()
    if not fork:
        one = len(tests) == 1
        which = "the test it changes" if one else f"the {len(tests)} tests it changes"
        return frozenset(), (
            f"git gave no merge base of {base} and {tip}, so what {which} under {TESTS} "
            f"import{'s' if one else ''} was not read, and {'it' if one else 'each'} waits on "
            "the read",
        )
    tooling: set[str] = set()
    unreadable: list[str] = []
    for path in tests:
        sides = [run(["show", f"{rev}:{path}"], root) for rev in (fork, tip)]
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
        if whole_number(own) is not None:
            said += f", and {name} has {_counted(own)} that copy lacks"
    return f"{said}, so HEAD is not what its pull request lands; {pull} and ask again"


def _counted(count: str) -> str:
    """`1 commit`, `2 commits`, or `commits` where git gave no count."""
    if whole_number(count) is None:
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
