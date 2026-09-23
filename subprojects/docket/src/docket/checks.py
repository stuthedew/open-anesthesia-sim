"""What can be decided by reading the files, decided here.

The division of labour in this package is deliberate and it is the same one
that makes any checker worth having: everything mechanically decidable is
decided by code and never left to a person or a model to notice, and
everything requiring judgment is left alone. A tool that guessed at the
judgment half would produce output that looks authoritative and is not,
which is worse than no tool.

So this module answers questions like "is this id used twice", "does this
item claim a blocker that does not exist", "is a safety-classed item sitting
in a band it is not allowed to sit in". It does not answer "is this still
the right thing to work on next". It only detects the conditions that make
that question worth a person's time, and says so.

Errors mean the store is wrong and exit non-zero. Advisories mean a human
should look, and never fail a build.
"""

from __future__ import annotations

import re
import shlex
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .config import Config
from .instructions import Assertion
from .model import (
    CLOSED_STATUSES,
    EFFORTS,
    OPEN_STATUSES,
    PRIORITIES,
    STATUSES,
    Item,
    generator_defect_faults,
    generator_faults,
    recurrence_faults,
    root_cause_faults,
)
from .notes import Thread
from .plan import OfferedReport, promotable
from .release import NOTES_DIR, SEMVER_RE, notes_name, reference, unrecorded_milestones, version_key
from .roadmap import MilestoneStates
from .store import ID_PATTERN, ID_RE, filename_for
from .vcs import (
    DEFAULT_BRANCHES,
    ClosureReport,
    CutWindow,
    LostReport,
    PullRequestHistory,
    RecordReport,
)
from .verify import LandedReport, never_fails, reads_check_output, reenters_verify

REQUIRED_BRIEF = ("**Problem.**", "**Why it matters.**")
DONE_WHEN = "**Done when.**"

#: The class for an item whose work *is* the queue edit - a triage pass, a
#: stranded recovery, a docs sweep, a release-tag item. It carries an id, a
#: `touches` and a `verify:` like any other, and is excused the two brief
#: sections that argue for the work rather than describe it.
#:
#: The exemption is the whole point and the id is not part of it. Two
#: mechanisms need the id and neither is bookkeeping: `tools/branch_id_check.py`
#: refuses a branch in the agent namespace that no id names, and a diff
#: confined to `docs/items/` raises the in-flight mark only under a subject
#: leading with the item's own id - for a housekeeping item, because its own
#: `touches` stays inside the queue (`PL-7790`, `PL-3W3P`) - a queue-only
#: commit being otherwise deliberately unreadable as work (`PL-X3WZ`). What
#: the category cannot justify is making each pass restate why housekeeping is
#: worth doing: measured 2026-09-19 over the 22 items titled "Triage ...",
#: 1,127 lines of brief, 12 repeating the same rationale and 2 carrying a
#: finding a later session needs (`PL-TQFB`, project owner, 2026-09-19,
#: ratified, over pointing the requirement at a standing rationale and over
#: dropping the item altogether).
#:
#: It may not sit beside a debt class, which is what stops it becoming the way
#: to file a defect without a brief; `_check_item` refuses that pairing.
HOUSEKEEPING = "housekeeping"
DECISION_NEEDED = "**Decision needed.**"

#: What a status demands beyond what every triaged item owes, paired with the
#: rule as `bin/docket triage` states it. One table, read by the checks below and
#: by `render._triage_rules`, because a requirement enforced and never printed
#: costs a round trip on every pass that sets the status - the session writes the
#: edit, runs `make docket`, and finds out afterwards. `PL-F4JS` was the
#: `needs-decision` entry: enforced since the status existed, absent from the
#: rules block the `docket` skill calls complete, and found the expensive way.
#:
#: Only statuses a triage pass can set. `ready` has its own rule, printed
#: conditionally on `verify_required_from`, and `done` is not a triage outcome.
STATUS_REQUIREMENTS: tuple[tuple[str, str], ...] = (
    (
        "needs-decision",
        f"an item set to `needs-decision` needs a `{DECISION_NEEDED}` section saying "
        "what has to be decided, so a later session can answer it, and should mark a "
        "recommendation beside it - the question survives in the item, the reasoning "
        "behind an answer dies with the session that had it. Where none is owed, say "
        "so and why. `docket check` advises on a brief that marks neither.",
    ),
    (
        "blocked",
        "an item set to `blocked` needs a `blocked-by` naming the item or milestone "
        f"that would unblock it, and is exempt from `{DONE_WHEN}`.",
    ),
    (
        "dropped",
        "an item set to `dropped` needs a `reason` and a `closed` date - dropping an "
        "item closes it.",
    ),
)

# A heading, as the item format writes one: `**` at the start of a line. Used
# to find where one section stops rather than to validate the heading itself,
# so bold text inside a paragraph does not end a section and a bold-opened
# paragraph does.
BRIEF_HEADING = re.compile(r"^\*\*", re.MULTILINE)

# An item file's whole name, as `store.filename_for` writes one: the id, then a
# slug, then the suffix. This is what tells a `touches` entry that names *an
# item* from one that names the store directory itself - 48 of this store's 95
# entries under `docs/items/` on 2026-09-19 are the bare directory, written by
# release cuts that rewrite many briefs at once, and those claim nothing about
# any one item.
#
# Named apart from `vcs.ITEM_FILE_RE`, which is the same id capture without the
# suffix anchor: that one pulls an id out of a path git already reported, so it
# must match a prefix, and this one judges a string a person typed, so it must
# refuse everything that is not a whole filename. One name over two rules is
# how a reader imports the wrong one.
DECLARED_ITEM_RE = re.compile(rf"^({ID_PATTERN})-.+\.md$")

# What a dangling declaration costs, said once because both branches of the
# rule below end with it, and kept to one clause because it prints per
# instance: the reasoning is in `_check_touched_items`, where it is read once.
DANGLING_TOUCHES = (
    "a path no file holds reads as a path nobody touches to `docket concurrent`, "
    "the lane split and `docket verify`'s inside-`touches` audit"
)


def _emphasised(flat: str) -> Iterator[str]:
    """Every run of text under `**bold**` or `*italic*` emphasis, flattened text in.

    Tokenised by splitting rather than matched by a regex, because the obvious
    pattern - emphasis, anything, the word, anything, emphasis - matches the
    *gap between two emphasised spans* just as happily as it matches one span,
    so a brief saying "before recommending it" between two bold headings reads
    as having recommended. Splitting on the delimiter cannot do that: odd
    chunks are inside, even chunks are outside, and there is no third reading.
    """
    bold = flat.split("**")
    for index, chunk in enumerate(bold):
        if index % 2:
            yield chunk
            continue
        italic = chunk.split("*")
        for position, part in enumerate(italic):
            if position % 2:
                yield part


def _marks_recommendation(body: str) -> bool:
    """Whether a brief marks a recommendation where a reader can find one.

    Presence of a *marker*, never a judgment about the prose: whether the
    recommendation is any good, or whether one is owed at all, is the half
    `CLAUDE.md` forbids scripting. What this decides is the half that is
    decidable - did the author label it, so that somebody meeting the item
    cold can find the answer without reading the whole brief and inferring
    one. That is the failure this came from: `PL-KQHN`'s recommendation was
    reconstructed from a summary line naming two options and marking neither.

    Marked means the token under emphasis - `**Recommended**`, `**This is the
    recommendation.**`, `*Recommendation: not yet.*` - or the labelled form
    `Recommendation:`. One pattern serves both endings a brief may honestly
    reach, because `**No recommendation**, because the deciding number cannot
    be measured` marks the declination in the same breath as the word.

    Matched on the brief with its wrapping flattened. A marker falling across
    a line break is the same marker to a reader and a different string to a
    regex, and four of the eight briefs carrying one in this store wrap
    somewhere inside it.
    """
    flat = " ".join(body.split())
    if re.search(r"recommendation:", flat, re.IGNORECASE):
        return True
    return any(re.search(r"recommend", span, re.IGNORECASE) for span in _emphasised(flat))


def _section_text(body: str, marker: str) -> str | None:
    """What a brief holds under `marker`, or `None` when it holds no such heading.

    Presence of the literal marker used to be the whole test, and it was wrong
    in both directions: `**Why it matters, and why it is not new.**` is a
    better heading than the bare one and was rejected, while a heading with
    nothing under it was accepted. So a heading is matched by its opening
    words - everything up to the `.**` the constants above carry for the error
    message - and what follows it, up to the next heading-opened line, is what
    the item actually says. An empty string is a section with no text under
    it, which is a different failure from a missing one and reads as one.

    The first matching heading is the one judged, deliberately. The stub this
    check was written for - four headings echoing the format, above the real
    brief - would pass a rule that accepted any occurrence with text, which is
    the hole rather than the fix.

    Deciding whether a section has content, never whether the content is any
    good: `CLAUDE.md`'s line between what a tool may decide and what it may not.
    """
    heading = re.search(rf"^{re.escape(marker.removesuffix('.**'))}", body, re.MULTILINE)
    if heading is None:
        return None
    # Past the heading's own closing `**`, so that an elaborated heading is not
    # mistaken for the text under itself. A heading that never closes has
    # nothing under it by this reading, which is the answer that heading
    # deserves.
    close = body.find("**", heading.end())
    start = len(body) if close == -1 else close + 2
    end = BRIEF_HEADING.search(body, start)
    return body[start : end.start() if end else len(body)].strip()


def _stub_above_brief(body: str) -> str | None:
    """The empty template heading a real brief was written underneath, if there is one.

    `docket new` used to write four empty headings for a session to write over,
    and a session holding the brief appended it *below* them instead - eighteen
    of the thirty-two items at the triage pass of 2026-09-05, fifteen of those
    carrying a full brief under a dead stub. `_section_text` judges the first
    matching heading, so the stub wins and the item reads as having nothing
    under two required sections however good the brief beneath it is
    (queue item `PL-D188`).

    The shape is decidable: a required heading left empty, with a `**Problem.**`
    starting again below it, which is what a second brief begins with. Measured
    over all 657 items in the store it selected the six carrying the stub and
    nothing else. An elaborated heading is not a false positive - `**Why it
    matters more than a normal benchmark.**` opens a section of its own and
    leaves the plain one above it non-empty.

    It may fire on an `untriaged` item, where the brief checks deliberately do
    not, because it demands nothing that capture chose not to write: writing
    less can never trigger it. Only writing a brief and leaving the template
    above it can.
    """
    for marker in (*REQUIRED_BRIEF, DONE_WHEN):
        heading = re.search(rf"^{re.escape(marker.removesuffix('.**'))}", body, re.MULTILINE)
        if heading is None or _section_text(body, marker) != "":
            continue
        if re.search(r"^\*\*Problem", body[heading.end() :], re.MULTILINE):
            return marker
    return None


def stub_error(where: str, marker: str) -> str:
    """One wording for the shape, wherever it is reported."""
    return (
        f"{where}: the capture template is still above the brief written under it - "
        f"{marker} is empty and a second **Problem.** starts below it. Delete the "
        "template's headings; the brief beneath them is the item. Left in place, the "
        "empty heading is the one the checker reads, so an item with a full brief "
        "reports as having none"
    )


def brief_gaps(
    body: str, *, blocked: bool = False, housekeeping: bool = False
) -> tuple[list[str], list[str], str | None]:
    """The required sections a brief lacks: absent, empty, and a stub left above it.

    One author for the rule, because two had already drifted: `check` errored
    on the sections an item was missing while `triage` printed its own reading
    of the same three markers, and the README promises a reader those two
    cannot disagree. A blocked item is not asked for `**Done when.**` - it
    cannot state its closing condition until its blocker resolves. A `housekeeping`
    item is asked for `**Problem.**` and nothing else: see `HOUSEKEEPING`.

    A stub replaces the empty-heading list rather than adding to it. Both
    describe the same defect and only one of them describes it correctly:
    "brief has nothing under **Why it matters.**" is false of an item whose
    brief is two pages, and a reader who learns that line can be wrong stops
    reading it. Reporting one at a time loses nothing - delete the stub, and a
    section the brief genuinely omits is reported on the next run as missing.
    """
    if housekeeping:
        # `**Problem.**` alone, which `docket new` writes from the title. The
        # two that go are the two a housekeeping pass cannot answer without
        # restating the category: "why it matters" is the standing rule that
        # made the pass necessary, and "done when" is the `verify:` command in
        # prose. The command still has to be there - the exemption is the
        # argument, never the proof.
        required = [REQUIRED_BRIEF[0]]
    else:
        required = list(REQUIRED_BRIEF) + ([] if blocked else [DONE_WHEN])
    found = {marker: _section_text(body, marker) for marker in required}
    stub = _stub_above_brief(body)
    return (
        [marker for marker, text in found.items() if text is None],
        [] if stub else [marker for marker, text in found.items() if text == ""],
        stub,
    )


# A pull request number, as GitHub allocates them: a bare positive integer.
# Written without the `#` so that the field holds the number and nothing else,
# and so a typo like `pr: #71 (docket)` is refused rather than half-parsed.
PR_RE = re.compile(r"^[1-9][0-9]*$")

#: The shortest `falsifies:` fragment worth folding on. Long enough that the
#: tokens which would fold indiscriminately - `assert`, `== 0`, a bare name -
#: are refused, and short enough to leave a real subject writable: the shortest
#: sentence fragment that identified anything in this store was 24 characters
#: (`PL-C6XD`'s `Not 0.2.8: the roadmap gives that version`, 40), and the
#: longest pan-matching token worth refusing is `assert (` at 8. A round number
#: between the two, chosen to be argued with rather than derived - if a real
#: declaration is ever refused by it, the fragment wanted more context anyway.
FALSIFIES_MIN_LENGTH = 12


@dataclass(frozen=True)
class SettingsSource:
    """Which `docket.toml` a run resolved its settings from, and whether it was there.

    Two fields rather than one because both halves have to travel: a run that
    found no config needs to name the path it looked for, which is the whole
    of the diagnosis, and a `None` path would carry the fact and lose it.

    The path arrives already formatted for a reader - resolved, and made
    relative to the working directory where it can be. That is the caller's
    job rather than this module's, which reads no filesystem and knows no
    working directory.
    """

    path: Path
    found: bool


@dataclass
class Report:
    """Findings, split by whether a machine or a person has to resolve them.

    `declined` is neither: it is the checks that could not run here. A check
    that stays silent when it cannot answer is right to stay silent about the
    *items*, and wrong to let the run look complete - "no errors" and "not
    checked" are different results, and a reader who cannot tell them apart
    has been told the store is sound when nobody looked.
    """

    items: list[Item] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)
    declined: list[str] = field(default_factory=list)
    #: What running the items' own commands cost this run. Not a finding, and
    #: kept out of the three lists above for that reason: nothing here asks to
    #: be resolved. `_note_cost` says why it is reported at all.
    cost: str = ""
    #: Which settings governed this run. Not a finding either, and kept out of
    #: the three lists for the same reason `cost` is. `_note_settings` says why
    #: it is reported at all.
    settings: str = ""

    @property
    def open_items(self) -> list[Item]:
        return [item for item in self.items if item.is_open and not item.is_untriaged]

    @property
    def untriaged(self) -> list[Item]:
        return [item for item in self.items if item.is_untriaged]

    @property
    def counts(self) -> dict[str, int]:
        return {p: sum(1 for i in self.open_items if i.priority == p) for p in PRIORITIES}


def _where(item: Item) -> str:
    return f"{item.path or item.identifier}"


def _check_item(item: Item, report: Report, config: Config) -> None:
    """Validate one item against the format, according to its status.

    Requirements scale with how far the item has been triaged. An untriaged
    capture needs almost nothing, because demanding a priority and a full
    brief at the moment an idea occurs is how ideas stop being written down.
    Everything past that point is a commitment to do work, and is held to the
    standard that lets someone else pick it up cold.
    """
    where = _where(item)

    if not item.identifier:
        report.errors.append(f"{where}: no `id` field")
    elif not ID_RE.match(item.identifier):
        report.errors.append(f"{where}: id '{item.identifier}' is not a valid item id")
    if not item.title:
        report.errors.append(f"{where}: no `title` field")
    if item.unknown_fields:
        report.errors.append(
            f"{where}: unrecognized field(s) {', '.join(item.unknown_fields)}; "
            "a misspelled field is silently ignored, so it is rejected here"
        )
    if item.duplicate_fields:
        report.errors.append(
            f"{where}: front-matter key(s) {', '.join(item.duplicate_fields)} appear more "
            "than once; the parser keeps the last and drops the rest, so the surviving "
            "value is decided by line order rather than by anyone. Two branches inserting "
            "the same field at different positions merge cleanly into this - delete the "
            "wrong line by hand after checking which value is right"
        )
    if item.block_list_fields:
        report.errors.append(
            f"{where}: {', '.join(item.block_list_fields)} written as a YAML block list; "
            "this format spells a list as one comma-separated line, so the indented "
            "entries are read by nothing and the field arrives empty at every check that "
            "asks for it - an empty `classes:` is what lets a safety-classed item sit in "
            "the bottom band. Put the entries on the field's own line, comma-separated"
        )
    if not item.status:
        report.errors.append(f"{where}: no `status`; expected one of {', '.join(STATUSES)}")
        return
    if item.status not in STATUSES:
        report.errors.append(f"{where}: status '{item.status}' is not one of {', '.join(STATUSES)}")
        return
    # `milestone:` means one thing: the release an item shipped in. `docket
    # release` stamps it on the work it is shipping, so work that is not
    # finished cannot carry one. The other meaning it used to be hand-written
    # for - "scoped to this release" - belongs to `ROADMAP.md`'s gate
    # subsection, which `docket wave` reads and which is the only thing that
    # decides membership.
    if item.milestone and item.status != "done":
        report.errors.append(
            f"{where}: `milestone: {item.milestone}` on a '{item.status}' item, "
            "which cannot have shipped; `milestone` records the release an item "
            "went out in and is stamped by `docket release`. Membership of a "
            "release being planned is recorded in the roadmap's gate list, not here"
        )
    # Required only while an item is open. Items closed before this format
    # existed have no recorded capture date and cannot acquire one, and the
    # date has no use once the work is finished.
    if item.added is None and item.is_open:
        report.errors.append(f"{where}: no `added` date, or it is not YYYY-MM-DD")

    if item.is_untriaged:
        if not item.body.strip():
            report.errors.append(
                f"{where}: no body; a title alone cannot be triaged by someone "
                "who was not there when it was captured"
            )
        elif stub := _stub_above_brief(item.body):
            report.errors.append(stub_error(where, stub))
        return

    if item.status in OPEN_STATUSES:
        if item.priority not in PRIORITIES:
            report.errors.append(f"{where}: no priority; expected one of {', '.join(PRIORITIES)}")
        if item.effort not in EFFORTS:
            report.errors.append(f"{where}: no effort; expected one of {', '.join(EFFORTS)}")
        missing, empty, stub = brief_gaps(
            item.body, blocked=item.status == "blocked", housekeeping=HOUSEKEEPING in item.classes
        )
        if missing:
            report.errors.append(f"{where}: brief is missing {', '.join(missing)}")
        if empty:
            report.errors.append(
                f"{where}: brief has nothing under {', '.join(empty)}; the heading "
                "is there and the section is not, which is what the brief exists "
                "to prevent"
            )
        if stub:
            report.errors.append(stub_error(where, stub))

    # The `verify:` gate sits at `ready` rather than at capture, and the
    # placement is the whole of the rule. Demanding a command at the moment an
    # idea occurs is the same tax as demanding a priority, and the block above
    # exists to refuse it. `ready` is where the item has stopped being an idea
    # and become a commitment to do work, which is the first point at which
    # "what would prove this done" is answerable at all.
    #
    # `not-delegable` satisfies the requirement in place of a command, because
    # some work genuinely has no check that can run beforehand - proving a
    # release-time fix means cutting a release - and an item saying so is
    # better specified than one carrying a command invented to satisfy a
    # checker. What is refused is silence.
    if item.status == "ready" and _verify_required(item, config):
        if not item.verify and not item.not_delegable:
            report.errors.append(
                f"{where}: is ready but names no `verify:` command; give the command "
                "that would prove it done, or record in `not-delegable` why no command can"
            )

    # `payoff:` sits at the same status as the gate above, and the placement
    # carries the same argument: an idea being captured owes nothing, and
    # `ready` is where the item has become a commitment to do work and "what
    # does closing this buy?" has an answer.
    #
    # No escape hatch, unlike `not-delegable` above. Some work genuinely has
    # no command that can run beforehand; no work has no consequence, and an
    # item nobody can say that much about is a finding about the item rather
    # than a case for an exemption.
    #
    # Presence and nothing else. Whether the line states a *consequence* or
    # merely restates the title is exactly the judgment this project refuses
    # to script: a checker guessing at it would be authoritative and wrong,
    # which is worse than no checker. No length floor either - the one
    # `falsifies` carries exists because a short fragment folds assertions it
    # was never meant to, a concrete harm, where a thin payoff harms only the
    # reader who is looking straight at it.
    if item.status == "ready" and _payoff_required(item, config):
        if not item.payoff:
            report.errors.append(
                f"{where}: is ready but names no `payoff:`; give one plain-language line of "
                "what closing it buys - the consequence, not a restatement of the title"
            )

    # The same requirement at the other end of the item's life, and this half
    # is what reaches the set the gate above grandfathers. An item captured
    # before `verify_required_from` is exempt at `ready` and stays exempt
    # however long it sits there, so the only thing asking for its command was
    # a grooming advisory - which works if somebody reads it. Closing the item
    # is the moment the work exists and what proved it is known, so it is the
    # first moment the command can be written *having been run*, which is the
    # objection that earned the grandfathering in the first place (`PL-J49T`).
    #
    # An error rather than an advisory because nothing here needs judgment.
    # Whether the field is present is decidable; only what it should say is
    # not, and this refuses silence without guessing at the sentence.
    # `dropped` is excluded: an item that will not be done carries a `reason`,
    # not a command for work nobody did.
    if item.status == "done" and _verify_required_at_close(item, config):
        if not item.verify and not item.not_delegable:
            report.errors.append(
                f"{where}: is done but names no `verify:` command; give the command "
                "that proved it, or record in `not-delegable` why no command can"
            )

    # What the command may *be*, once it is present - the decidable half of the
    # contract `PL-6TP8` settled, which until now was carried only by a table in
    # the `docket` skill. Open items only: a closed command is a record of what
    # was run on a tree that no longer exists, and rewriting one replaces the
    # command that proved the work with one that never ran it.
    if (
        item.status not in CLOSED_STATUSES
        and item.verify
        and _verify_prerequisite_refused(item, config)
    ):
        redundant = _redundant_pytest_clause(item.verify, config.collected_test_paths)
        if redundant is not None:
            report.errors.append(
                f"{where}: its `verify:` runs `{redundant}` beside a separate "
                "discriminating clause, so it proves the tree twice - "
                f"`{config.check_command}` already collects that target, and every "
                "consumer of the field runs it. Record the discriminator alone"
            )

    # The first obligation that contract puts on a command, made mechanical
    # (`PL-Q8RQ`): its failure before the work is an ordinary exit 1, never
    # pytest's 5. A `-k` over the collected trees can give only 0 or 5, and a
    # substring can be satisfied by another item's test; `_k_selector_clause`
    # has the reasoning and what it leaves alone.
    if (
        item.status not in CLOSED_STATUSES
        and item.verify
        and _verify_k_selector_refused(item, config)
    ):
        selector = _k_selector_clause(item.verify, config.collected_test_paths)
        if selector is not None:
            report.errors.append(
                f"{where}: its `verify:` clause `{selector}` narrows a pytest run with "
                "`-k`, so it can never fail the ordinary way the field needs - over a "
                f"tree `{config.check_command}` collects it selects tests that command "
                "already proves (exit 0) or selects none (exit 5, which reads as a "
                "correct failure until any test anywhere comes to carry the substring). "
                "Record a `grep -q` for the `def` of the test the work adds instead"
            )

    # A safety class forces the top band, because that is where work able to
    # reach a wrong clinical value belongs. `blocked` earns a narrow exception:
    # a blocked item is not in the set `next` chooses from, so its band is a
    # claim about work nobody can start, and forcing one buys nothing at the
    # price of the failure this rule exists to prevent - an item quietly
    # re-classed out of `safety` to satisfy the checker, which corrupts the
    # class for every other reader of it and leaves the correction to someone's
    # memory. Unblocking re-fires this, which is the point: the band is decided
    # when the work becomes workable, by the checker rather than by recall.
    #
    # The exception is only for work whose safety concern does not exist yet -
    # the feature it guards has not been built. A blocked item where something
    # is already wrong is the opposite case: the blocker is only sequencing, so
    # the band still stands, and `_outranks_its_blocker` below drags the blocker
    # up to meet it rather than letting a live defect park at P3 behind
    # something nobody will pick.
    #
    # Which case it is cannot be decided from the store, so it is claimed, not
    # inferred - and the claim fails closed. `anticipated` must be present to
    # earn the exemption; absence, omission, or a misspelling of it all leave
    # the strict rule in force. Inferring the exemption from a *missing* class
    # would have made forgetting to write one the way to obtain it, which is
    # the wrong default for the one class where a wrong default is expensive.
    # Before the pin reads `classes`, establish that it can. Every use of the
    # field below is a membership test against a configured list, so a class
    # outside the vocabulary is not an unknown label - it is a label that
    # silently satisfies no rule. The pin is the expensive one: `classes:
    # safey` leaves safety-critical work seatable at P3 with nothing said.
    unknown = tuple(c for c in item.classes if c not in config.vocabulary())
    if unknown:
        report.errors.append(
            f"{where}: class '{', '.join(unknown)}' is not in the declared vocabulary "
            f"({', '.join(sorted(config.vocabulary()))}); a class the tool does not know "
            "matches no rule, so a misspelled `safety` seats safety-critical work in a "
            "band that is meant to exclude it"
        )
    # `housekeeping` buys an exemption from two brief sections, so the one
    # thing it may never do is carry work that owes a brief. A debt class is
    # exactly that work - `ROADMAP.md`'s gate counts it, a session picks it up
    # cold, and "why it matters" is the sentence that tells them whether it is
    # still real. Refused rather than reported, because the two readings of
    # `classes: housekeeping, defect` are "a pass that also fixed something",
    # which should be two items, and "a defect dodging its brief", which is the
    # abuse; neither is a state to leave standing.
    dodged = tuple(c for c in item.classes if c in config.debt_classes)
    if HOUSEKEEPING in item.classes and dodged:
        report.errors.append(
            f"{where}: class '{HOUSEKEEPING}' sits beside '{', '.join(dodged)}'; "
            f"'{HOUSEKEEPING}' excuses an item the brief sections that argue for the "
            "work, and debt is the work that most needs them. Split the finding out as "
            "its own item, or drop the `housekeeping` class and write the brief"
        )
    safety = tuple(c for c in item.classes if c in config.safety_classes)
    exempt = item.status == "blocked" and "anticipated" in item.classes
    if safety and not exempt and item.priority in ("P2", "P3"):
        blocked_hint = (
            "; if the concern does not exist until a later feature is built, class it "
            "`anticipated` and the band waits with it"
            if item.status == "blocked"
            else ""
        )
        report.errors.append(
            f"{where}: class '{', '.join(safety)}' sits at {item.priority}; "
            f"safety-critical work starts at P0 or P1{blocked_hint}"
        )
    if item.status == "blocked" and not item.blocked_by:
        report.errors.append(f"{where}: marked blocked but names no blocking item or milestone")
    if item.status == "needs-decision" and not _section_text(item.body, DECISION_NEEDED):
        report.errors.append(
            f"{where}: marked needs-decision but states no decision to make; add a "
            f"{DECISION_NEEDED} line so a later session can answer it"
        )
    if item.verify and "\n" in item.verify:
        report.errors.append(f"{where}: `verify` must be a single-line command")
    # An error rather than an advisory because nothing here needs judgment:
    # whether the command names `docket verify` is decidable, and there is no
    # reading of it that is worth keeping. Running another item's command
    # proves nothing about this one, and running this one's re-enters the
    # command doing the running.
    if item.verify and reenters_verify(item.verify):
        report.errors.append(
            f"{where}: its `verify:` command runs `docket verify`, which is the "
            "command that executes an item's `verify:` field - so running it would "
            "run this line again, one level per run, until the process table gives "
            f"out. Prove the item another way: read the store (`grep` over "
            f"{config.items_dir}), or pair a command that passes today with a "
            "`grep` for what the work adds."
        )
    # Beside the refusal above and for the same reason: the question is
    # decidable from the field, so the tier that runs the command has nothing to
    # add. `--verify` found this one on `PL-4W2L`'s branch, where three items
    # carried `verify: true` - but only after the push, and only in CI, because
    # `make check` runs `docket check` bare. Both halves of what CI printed that
    # day are answered here now: this one, and the shared command below
    # (`PL-J3WK`).
    if item.verify and never_fails(item.verify):
        report.errors.append(
            f"{where}: its `verify:` command is `{item.verify.strip()}`, which exits 0 "
            "against every tree there has ever been, so it specifies nothing and "
            "`docket verify` would ACCEPT a branch that did none of the work. Name "
            "something only the work creates, and run the command and see it fail "
            "before recording it"
        )
    # An advisory rather than an error, unlike the refusal above: whether a
    # shell line reads a command's output is a judgment, and the exit-status
    # form beside it is bounded at one level; since `PL-6TP8` the `grep` is
    # written alone, with no health check ahead of it.
    if item.verify and (shape := reads_check_output(item.verify)):
        report.advisories.append(
            f"{_where(item)}: its `verify:` command runs `docket check` and {shape}. "
            "A nested run is told not to replay the open items' commands, so it never "
            "prints the landed advisory - a `grep` for that answer matches nothing "
            "whether the work is done or not, and an inverted one passes on the "
            "strength of it. Write a `grep` for what the work adds instead, with "
            "nothing ahead of it."
        )
    # `verify` folds every removed assertion containing this substring, so a
    # fragment short enough to appear in assertions it was never about folds
    # them too - `assert` itself would fold the lot. A length floor is the
    # exact half of that: whether the fragment is long enough to name one
    # subject is decidable, while whether it names the *right* one is the
    # judgment, and is left to the reader of the lines `verify` prints.
    if item.falsifies and len(item.falsifies) < FALSIFIES_MIN_LENGTH:
        report.errors.append(
            f"{where}: `falsifies` is '{item.falsifies}', {len(item.falsifies)} characters; "
            f"it holds at least {FALSIFIES_MIN_LENGTH} - enough of the assertion to name the "
            "one subject this item makes untrue, since `docket verify` folds every removed "
            "assertion containing it"
        )
    if item.not_delegable and item.not_delegable.lower() in ("no", "yes", "true", "false"):
        report.errors.append(
            f"{where}: `not-delegable` holds the reason the item is withheld, not a "
            "boolean; write why a cheaper model must not take it"
        )
    if item.verify and not item.touches and item.status in OPEN_STATUSES:
        report.errors.append(
            f"{where}: names a `verify` command but declares no `touches`; a check "
            "with no declared scope cannot bound what the work may change"
        )
    # The `pr`-on-a-closure rule is not here: it needs to know whether the
    # closure has landed, which is a git question. `_check_closures` has it.
    if item.pr and not PR_RE.match(item.pr):
        report.errors.append(
            f"{where}: `pr` is '{item.pr}'; it holds a pull request number and "
            "nothing else, written without the `#`"
        )
    if item.status == "dropped" and not item.reason:
        report.errors.append(
            f"{where}: marked dropped but records no `reason`; an item closed without "
            "one gets re-raised by the next person who notices it"
        )
    if item.status in ("done", "dropped") and item.closed is None:
        report.errors.append(f"{where}: marked {item.status} but records no `closed` date")


def _verify_required(item: Item, config: Config) -> bool:
    """Whether the `verify:` rule applies to this item at all.

    Anchored to the item's capture date rather than to the moment it reached
    `ready`, because capture is the only date the file records. That leaks: an
    item captured before the cutover and triaged after it escapes the rule.
    The leak is bounded and shrinking - it can only cover items already in the
    store when the rule was adopted - and the alternative, a second date field
    written by hand at triage, is a field that can be wrong.
    """
    if config.verify_required_from is None:
        return False
    return item.added is not None and item.added >= config.verify_required_from


def _payoff_required(item: Item, config: Config) -> bool:
    """Whether the `payoff:` rule applies to this item at all.

    Anchored to the capture date, and it leaks in the same bounded way
    `_verify_required` leaks: an item captured before the cutover and triaged
    after it escapes the rule. The alternative is a second date written by
    hand at triage, which is a field that can be wrong, and the leak can only
    ever cover items already in the store when the rule was adopted.

    The set it grandfathers is closed at whatever the store held on the day
    the rule began working, which is why the date a project records here is
    the day *after* it is set rather than the same day. Backfilling that set
    was refused for `verify:` and is refused here for the cheaper half of the
    same reason: a sentence written for an item nobody has started is written
    away from the only context that makes it accurate.
    """
    if config.payoff_required_from is None:
        return False
    return item.added is not None and item.added >= config.payoff_required_from


def _recommendation_required(item: Item, config: Config) -> bool:
    """Whether the marked-recommendation rule reaches this item by date.

    Anchored to the capture date, and it leaks the way `_payoff_required`
    leaks - an item captured before the cutover and triaged to
    `needs-decision` after it escapes this half. Here the leak costs less than
    it does there, because the offered set in `_groom` covers the same items
    from the other end: what the date misses, the moment somebody is about to
    act on the question catches.

    The two halves are not redundant, though, and neither substitutes for the
    other. The date reaches the session *writing* the item, which is the only
    session that still holds the reasoning and therefore the only one that can
    record it rather than reconstruct it. The offered set reaches a session
    that can, at best, say the recommendation was never written down.
    """
    if config.recommendation_required_from is None:
        return False
    return item.added is not None and item.added >= config.recommendation_required_from


def _verify_required_at_close(item: Item, config: Config) -> bool:
    """Whether the closing `verify:` rule applies to this item.

    Anchored to `closed:` rather than `added:`, which is the whole difference
    from `_verify_required` and the reason this one can reach the items that
    predate `verify_required_from`. Those are exempt at `ready` by design - a
    command written for an item nobody has started cannot be run before it is
    written - and closing one is exactly when that objection lapses.

    An item already closed before this cutover is untouched, deliberately.
    Backfilling a command onto work that has merged would mean writing one
    with nothing left to run it against, which is the same failure the
    grandfathering avoids, one end of the item's life later.
    """
    if config.verify_required_at_close_from is None:
        return False
    return item.closed is not None and item.closed >= config.verify_required_at_close_from


#: Options that make a pytest run select something narrower than the files
#: named on its command line. Any of them, and the clause is no longer a whole
#: file's suite proved twice, so the rule below leaves it alone. `--cov` is
#: here because a coverage threshold is the one shape the `docket` skill
#: prescribes pytest for. A `-k` discriminates nothing either, and
#: `_k_selector_clause` refuses it on its own account.
_PYTEST_SELECTORS = ("-k", "-m", "--cov", "--deselect", "--lf", "--ff")

#: Options that consume the token after them, so that token is a value rather
#: than a path to run. `--x=y` spellings consume nothing and need none of
#: this. The selectors among them matter only to `_k_selector_clause`, which
#: reads the paths past a `-k` where `_pytest_targets` returns at it.
_PYTEST_VALUE_OPTIONS = frozenset(
    {
        "-k",
        "-m",
        "--deselect",
        "-n",
        "-p",
        "-o",
        "-c",
        "-r",
        "--dist",
        "--maxfail",
        "--durations",
        "--rootdir",
        "--ignore",
    }
)

#: Shell operators after which a clause's exit status is no longer the pytest
#: run's own: a pipeline answers with its last command's, `||` replaces a
#: failure, and `;` or `&` discards it.
_STATUS_REPLACED = frozenset({"|", "|&", "||", ";", "&"})


def _after_pytest(tokens: Sequence[str]) -> list[str] | None:
    """The tokens following the pytest executable, or `None` if nothing runs it."""
    for index, token in enumerate(tokens):
        if token == "pytest" or token.endswith("/pytest"):
            return list(tokens[index + 1 :])
    return None


def _run_targets(arguments: Sequence[str]) -> list[str]:
    """The paths among a pytest run's arguments, past every option and its value."""
    targets: list[str] = []
    skip = False
    for token in arguments:
        if skip:
            skip = False
            continue
        if token in _PYTEST_VALUE_OPTIONS:
            skip = True
            continue
        if not token.startswith("-"):
            targets.append(token)
    return targets


def _inside(target: str, collected: Sequence[str]) -> bool:
    """Whether a pytest target lies in one of the trees `check_command` collects."""
    return any(target == root or target.startswith(f"{root}/") for root in collected)


def _pytest_targets(clause: str) -> list[str] | None:
    """The paths a pytest clause runs, or `None` if it is not one to read.

    `None` covers three cases that are all "this is not a redundant health
    check": the clause does not invoke pytest at all, its arguments cannot be
    split (an unbalanced quote, which the format check elsewhere reports), or
    it carries a selector, which makes the run something narrower than a
    proof that a file's suite is green.

    An empty list is the meaningful answer rather than a missing one: a bare
    `pytest` with no path runs the whole suite, which is exactly what
    `check_command` runs.
    """
    try:
        rest = _after_pytest(shlex.split(clause))
    except ValueError:
        return None
    if rest is None:
        return None
    if any(token.startswith(_PYTEST_SELECTORS) for token in rest) or any(
        "::" in token for token in rest
    ):
        return None
    return _run_targets(rest)


def _redundant_pytest_clause(command: str, collected: Sequence[str]) -> str | None:
    """The clause that re-runs tests `check_command` already collects, if any.

    The shape `PL-6TP8` retired, reduced to the half that needs no judgment.
    A `verify:` command records the discriminator and nothing else, because
    every consumer that needs the tree proven runs `check_command` itself -
    `docket verify` as a line of its own report, `docs/worker.md` after the
    command, CI ahead of the replay. So a pytest run over a tree that command
    already collects proves the same thing twice, and `PL-FZ58` measured what
    the second proof costs: three test files carrying 59% of a whole-store
    replay's serial time, each re-run once per item whose command named it.

    What makes it decidable is the *other* clause. Which half of a paired
    command is the prerequisite is normally a question about the item's work -
    an item whose work is making `doc_check` pass has `doc_check.py check` as
    its discriminator, not as a preamble - and guessing at that is scripting
    the judgment. Here the author has already answered it: a separate,
    non-pytest clause is present, so the pytest run is not what discriminates,
    whatever the item turns out to be about. A command whose only clause is
    the pytest run says the opposite and is left alone.

    Split on `&&` alone, which is what every command in this store uses and
    the only separator that carries the "and then" this reads.
    """
    if not collected:
        return None
    clauses = [clause.strip() for clause in command.split("&&")]
    if len(clauses) < 2:
        return None
    pytest_clauses = [clause for clause in clauses if _pytest_targets(clause) is not None]
    if not pytest_clauses or len(pytest_clauses) == len(clauses):
        return None
    for clause in pytest_clauses:
        targets = _pytest_targets(clause) or []
        if all(_inside(target, collected) for target in targets):
            return clause
    return None


def _shell_tokens(clause: str) -> list[str] | None:
    """A clause's words with its shell operators split out as words of their own.

    `shlex.split` leaves `x|grep` as one word, so an unspaced pipe would read
    as part of a pytest argument; this is what lets `_k_selector_clause` see
    that the status is another command's. `None` for an unbalanced quote.
    """
    lexer = shlex.shlex(clause, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return None


def _k_selector_clause(command: str, collected: Sequence[str]) -> str | None:
    """The clause that narrows a pytest run with `-k` and answers with its status, if any.

    `PL-6TP8`'s first obligation on a command, made mechanical (`PL-Q8RQ`): its
    failure before the work is an evaluation - an ordinary exit 1 - and never
    pytest's 5. Over a tree `check_command` collects, a `-k` run cannot be one.
    Every test there passes or that command is red, so the run selects tests it
    already proves (0) or selects none (5, or 4 for a path the work has yet to
    create). Non-zero, so it reads as a command correctly failing, and it goes
    on reading that way until any test anywhere comes to carry the substring:
    `PL-S5YM`'s `-k covered` began passing when an unrelated merge added one,
    and three sessions diagnosed the red `main` that followed inside four
    minutes (`PL-99YZ`).

    Refused wherever it stands in the `&&` chain, because position decides only
    which half of the contract the clause breaks. Ahead of another clause, its
    5 is the command's answer before the work and nothing behind it runs.
    Behind one that fails first, it runs only once that clause passes, and
    then re-proves what `check_command` proves - the prerequisite shape
    `_redundant_pytest_clause` refuses, which leaves any run carrying `-k` to
    this rule. `PL-W4XQ` was recorded in the first shape on that rule's first
    day for exactly that reason.

    Three runs are left alone, each because the reading above stops being true.
    A run whose status an operator replaces - piped into a `grep` of its
    output, as `PL-205P`'s was - answers with the other command's status. A run
    carrying a coverage option can fail on a threshold, which `check_command`
    does not measure. And a run over a tree `check_command` does not collect
    may select a test that is failing today, so it can be an evaluation after
    all; that is the condition that would falsify the rule, and why the trees
    are declared rather than assumed.

    `-m` narrows the same way and would fail the same way, but no command in
    this store has ever carried one, so this reads `-k` alone rather than a
    shape nobody writes. Clauses are split on `&&` as `_redundant_pytest_clause`
    splits them.
    """
    if not collected:
        return None
    for clause in (part.strip() for part in command.split("&&")):
        tokens = _shell_tokens(clause)
        arguments = _after_pytest(tokens) if tokens is not None else None
        if arguments is None or _STATUS_REPLACED.intersection(arguments):
            continue
        if not any(token.startswith("-k") for token in arguments):
            continue
        if any(token.startswith("--cov") for token in arguments):
            continue
        if all(_inside(target, collected) for target in _run_targets(arguments)):
            return clause
    return None


def _verify_k_selector_refused(item: Item, config: Config) -> bool:
    """Whether the `-k` rule applies to this item: captured on or after its cutover.

    Anchored and grandfathered as `_verify_prerequisite_refused` is, for the
    same reason - the commands already recorded are a closed set that drains as
    each item is started - and leaking in the same bounded way. A date of its
    own because the two rules close different sets: `PL-W4XQ` was captured on
    the prerequisite rule's first day carrying a `-k`, which that rule does not
    read, so sharing its date would refuse it the moment this landed.
    """
    if config.verify_k_selector_refused_from is None:
        return False
    return item.added is not None and item.added >= config.verify_k_selector_refused_from


def _verify_prerequisite_refused(item: Item, config: Config) -> bool:
    """Whether the shape rule applies to this item at all.

    Anchored to the capture date, and grandfathering the commands already
    recorded, for the reason `PL-6TP8` chose repair-as-started over a
    one-pass strip: removing a clause from an item nobody has started writes
    into a file against every branch in flight, and the bill falls as the
    queue turns over anyway. The set this exempts is closed - nothing can
    join it, since the test is the capture date - which is the property that
    makes the grandfathering drain rather than persist.

    It leaks in the same bounded way `_verify_required` does: an item
    captured before the cutover can still have a command written after it.
    The alternative is a second date written by hand when the command is
    recorded, which is a field that can be wrong.
    """
    if config.verify_prerequisite_refused_from is None:
        return False
    return item.added is not None and item.added >= config.verify_prerequisite_refused_from


def _check_milestones(report: Report, version: str | None) -> None:
    """Refuse a `milestone:` naming a release that has not been cut.

    The other half of the rule `_check_item` enforces, and the half that
    caught the real case. A release stamps the items it ships and bumps the
    version in the same run, so a stamp naming a version above the project's
    current one is a release that has not happened - written by hand, or left
    behind by a run that failed before it could bump.

    Silence is what makes it worth failing on rather than noting.
    `release.unreleased` selects finished work with **no** milestone, so a
    stamped item is invisible to the release that actually ships it: it is
    left out of the generated notes, and a tag makes that permanent. Ten items
    were in exactly that state when this check was written, every one of them
    scoped to the release they were omitted from.

    A version that cannot be compared is not judged. `None` is a caller that
    did not ask; an empty string is a project with no version file, which
    `read_version` treats as a legitimate state; and a milestone or version
    outside `major.minor.patch` is a naming scheme this rule cannot read.
    """
    if not version or SEMVER_RE.match(version.strip()) is None:
        return
    current = version_key(version)
    for item in report.items:
        if not item.milestone or SEMVER_RE.match(item.milestone.strip()) is None:
            continue
        if version_key(item.milestone) > current:
            report.errors.append(
                f"{_where(item)}: `milestone: {item.milestone}` names a release "
                f"later than the current version ({version}), so it has not been "
                "cut; `docket release` stamps this field when the release goes "
                "out, and until then a stamped item is left out of that release's "
                "own notes"
            )


def _named(identifiers: list[str], limit: int = 8) -> str:
    """List ids for a reader, and stop before the list stops being readable."""
    shown = ", ".join(identifiers[:limit])
    rest = len(identifiers) - limit
    return f"{shown} and {rest} more" if rest > 0 else shown


def _check_release_notes(
    report: Report, notes: dict[str, frozenset[str]] | None, version: str | None
) -> None:
    """Hold each release's notes to the items stamped with its milestone.

    One release is recorded in two places - the `milestone:` on every item it
    shipped, and the notes file naming them - written by one command in one
    run, and until now nothing compared them. So an interruption between the
    two halves left them disagreeing with nothing to say so: a cut of v0.4.15
    stamped 26 items and died, and the re-run read those as already shipped,
    cut the remaining 7 under the same name and exited 0. Only the two printed
    counts, 33 from the dry run and 7 from the cut, distinguished it from a
    correct 7-item release, and a person read them side by side (`PL-1MKQ`).

    Both directions are errors, and the first is the dangerous one. Work
    stamped with a release whose notes do not name it is shipped work with no
    record - and a tag makes that permanent. Notes naming work that carries no
    stamp is the milder inverse, but it is the same file pair disagreeing and
    it is equally decidable.

    Reported per release rather than per item. The inconsistency is a property
    of the release - "this shipped 33 items and its notes name 7" - and saying
    it 26 times would bury the number that matters.

    Measured before it was made an error: across 37 releases and 231 items,
    36 agree exactly and the 37th is v0.2.2, which shipped before
    `docs/releases/` existed and is below the floor `unrecorded_milestones`
    derives. So this costs nothing on a healthy store, which is the test a
    check has to pass to earn a place in every run.

    `None` is a caller that did not ask, which is every command but `check`.
    """
    if notes is None:
        return
    stamped_by_name: dict[str, list[Item]] = {}
    for item in report.items:
        if item.milestone:
            stamped_by_name.setdefault(item.milestone.strip(), []).append(item)

    for name in unrecorded_milestones(report.items, notes, version or ""):
        stamped = sorted(item.identifier for item in stamped_by_name[name])
        report.errors.append(
            f"{len(stamped)} item(s) carry `milestone: {name}` but "
            f"{NOTES_DIR}/{notes_name(name)} was never written, so that release has no "
            f"record of what it shipped: {_named(stamped)}. That is what an interrupted "
            f"`docket release` leaves; re-run the cut of {name}, which picks the stamped "
            "items back up rather than shipping only the remainder"
        )

    for name, named in sorted(notes.items(), key=lambda pair: version_key(pair[0])):
        carried = {item.identifier for item in stamped_by_name.get(name, [])}
        if missing := sorted(carried - named):
            report.errors.append(
                f"{NOTES_DIR}/{notes_name(name)} does not name {len(missing)} item(s) "
                f"stamped `milestone: {name}`, so {name} shipped work its own notes have "
                f"no record of: {_named(missing)}"
            )
        if unstamped := sorted(named - carried):
            report.errors.append(
                f"{NOTES_DIR}/{notes_name(name)} names {len(unstamped)} item(s) that do "
                f"not carry `milestone: {name}`, so the notes and the store disagree about "
                f"what {name} shipped: {_named(unstamped)}"
            )


def _check_notes_references(
    report: Report, unreferenced: dict[str, tuple[str, ...]] | None
) -> None:
    """Released bullets whose route back to the change the store can supply.

    The third thing a release's notes and the store can disagree about, after
    which items shipped and whether they were stamped. A bullet records where
    its change landed so a reader can go and see it; a bullet without one names
    an item and stops, and the reader's next move is a hand search of the
    history.

    **Advisory, and decidable, which is normally an error's combination.** The
    exception is what the reader would do about it: `docket record` writes
    these, `make fix` runs it, and the repair is an append that cannot be got
    wrong. An error here would go red on a tree whose repair is one command
    nobody has run yet - and, worse, on a cut made from the shallow clone that
    is the normal state of an agent session, where the number was unreachable
    at the moment the notes were written and no amount of refusing produces it.

    **Only what the store can actually supply is counted**, which is what stops
    this becoming the advisory nobody reads (`CLAUDE.md` § "A check earns its
    place every run"). A bullet whose item records neither a number nor a
    commit is not a repair anyone is declining to make; it is provenance that
    does not exist, and `_check_closures` is where that is already reported
    against the item. So a store with nothing to add reports nothing, and every
    line printed here has a command behind it.

    Measured 2026-09-21, before the cut backfilled anything: 128 bullets across
    22 of this project's 40 releases, every one of them recoverable from a `pr`
    the store already held (`PL-W7WL`, filed four times from four cuts because
    nothing compared these two files on this axis).
    """
    if unreferenced is None:  # a caller that did not ask; every command but `check`
        return
    by_id = {item.identifier: item for item in report.items}
    for name, identifiers in sorted(unreferenced.items(), key=lambda pair: version_key(pair[0])):
        recoverable = sorted(
            identifier
            for identifier in identifiers
            if (item := by_id.get(identifier)) is not None and reference(item)
        )
        if not recoverable:
            continue
        report.advisories.append(
            f"{NOTES_DIR}/{notes_name(name)} names {len(recoverable)} item(s) without "
            f"saying where the change landed, and the store can say: {_named(recoverable)}. "
            f"`docket record` appends what each item already records, leaving the titles "
            f"as they shipped"
        )


def _check_cut_window(
    report: Report, window: CutWindow | None, notes: dict[str, frozenset[str]] | None
) -> None:
    """What the base took while this checkout's release cut sat unmerged.

    **Report, do not act** - which is the decision `PL-028F` asked for, and it
    was taken on two findings rather than on cost.

    The alternative was to re-stamp at merge, so the notes and the tag span
    agree by construction. That has no trigger in this repository: `PL-N5WZ`
    established that a push made with `GITHUB_TOKEN` starts no workflow, so a
    job fired by the merge can never satisfy `main`'s required status checks,
    and the same wall the merge-time `pr:` write hit stands here. Every variant
    that does land needs a person at the merge, which is this with extra
    machinery.

    And the judgment genuinely belongs to the person. Absorbing a newcomer
    means the release narrative describes work this session did not do, which
    `PL-028F` rejected on sight as the "recommend first, research afterwards"
    failure; letting it go to the next release is often right. Nothing here can
    decide that, and `CLAUDE.md` is explicit that a tool guessing the judgment
    half is worse than no tool.

    **An advisory rather than an error**, because both dispositions are
    legitimate and because `landed` is subject-derived: `CutWindow` says why
    that is the right accuracy here and the wrong accuracy for anything acting
    on its own. It fires only on a checkout carrying an unmerged cut, which is
    one session in a release, so it costs nothing on every other run - the test
    `CLAUDE.md` requires a check to pass to keep its place.

    The remedy it names already exists: re-running the cut of the same version
    reclaims what it stamped and folds the newcomers in, which is the property
    `unreleased`'s `resuming` argument was built for.
    """
    if window is None or not window.version:
        return
    if window.declined:
        report.advisories.append(
            f"the release being cut here could not be compared against {DEFAULT_BRANCHES[0]}, "
            f"because {window.declined}; anything that merged while this cut has been open is "
            "inside the tag's span and named in no notes"
        )
        return
    named = (notes or {}).get(window.version, frozenset())
    stamped = {
        item.identifier
        for item in report.items
        if item.milestone.strip().lstrip("v") == window.version
    }
    strangers = sorted(set(window.landed) - named - stamped)
    if not strangers:
        return
    report.advisories.append(
        f"v{window.version} is cut here and not yet merged, and the base has taken "
        f"{_named(strangers)} since - work inside the tag's span that "
        f"{NOTES_DIR}/{notes_name(window.version)} does not name, because the tag goes on the "
        "merge commit. Either absorb it - merge the base in and re-run "
        f"`make release VERSION={window.version}`, which reclaims what this cut already "
        "stamped - or let it go to the next release, which is often right. Read from commit "
        "subjects, so an id here may be in-progress work rather than a closure"
    )


def _check_provenance(report: Report, history: PullRequestHistory | None) -> None:
    """Hold every recorded pull request to one the default branch has actually seen.

    Three things stop this from being a plain set membership test, and all
    three are about refusing to answer rather than answering wrongly.

    A `history` that declined - most often a shallow clone, which is the normal
    shape of an agent session's container - is recorded as a check that did not
    run, and no item is judged. Reporting from a truncated history would mark
    the oldest and best-established provenance in the store as broken, and
    doing it silently would let that run read as a pass.

    A `history` of `None` is a caller that did not ask, which every command but
    `check` is: no git read, and nothing to report about one.

    Last, the high-water mark. An item is closed on the branch that carries it,
    so its pull request has not merged at the moment `check` first sees the
    number. Numbers above the highest one on the default branch are
    therefore not-yet-merged rather than wrong, and are passed over. What is
    left is the case worth failing on: a number in the range the default
    branch covers that no commit there names, which is a typo or an invention
    and is provenance that leads nowhere.
    """
    if history is None:
        return
    if not history.known:
        report.declined.append(f"recorded pull requests: {history.declined}")
        return
    if not history.numbers:
        return
    high_water = max(history.numbers)
    for item in report.items:
        if not item.pr or not PR_RE.match(item.pr):
            continue
        number = int(item.pr)
        if number <= high_water and number not in history.numbers:
            report.errors.append(
                f"{_where(item)}: records pull request #{number}, which no commit on "
                "the default branch names; the work it points at cannot be found"
            )


def _check_landed(report: Report, landed: LandedReport | None) -> None:
    """Say when an open item's own evidence of doneness already holds.

    An item is closed by hand, so nothing notices work that merges without its
    `status` being set. It keeps its place in `next`, `wave` and `gate` count
    it open, and a session picks it up and re-derives what is already on
    `main` before finding out.

    An advisory rather than an error, and it names candidates rather than
    reaching a verdict, because a passing command is consistent with two
    findings this cannot tell apart: the work landed, or the command does not
    discriminate and would have passed before the work too. Both want a
    person; neither is the checker's to decide. Measured against this store on
    2026-09-01 the second was every one of the eight it named, which is the
    reason the wording leads with the possibility rather than the conclusion.

    Both readings do close, which is what keeps this from becoming an advisory
    that fires forever and is skimmed past: the first is discharged by setting
    `status: done`, the second by giving the item a command that fails until
    its work exists.

    The two cases where the second reading is certain *before* anything runs are
    no longer reported from here. A command shared with another open item, and
    one that cannot fail at all, are both decidable by reading the store, so
    `_check_shared_verify` and `_check_item` refuse them on a bare `docket
    check` - the gate a session runs before it pushes. Reported here as well
    they would be a second sentence about a defect the run had already refused,
    and only for the subset that happened to pass (`PL-J3WK`).

    A blocked item is the case where only one of the two readings survives, and
    it is worded separately for that reason (`PL-RC0M`). Work nobody can start
    has not landed, so a passing command there can only mean the command does
    not discriminate - and telling that session to "close it" would send it at
    the one repair that is certainly wrong. Blocked items reach this at all
    only on a run narrowed to what a branch changed, so the finding arrives
    where somebody is already editing the item rather than on a sweep of the
    whole store.

    A command that could not answer at all - killed at the limit, or not found
    by the shell - is reported under "not checked" rather than as an advisory,
    because there is no finding to report: the run looked and was stopped. The
    distinction is the same one `landed.declined` draws for a whole run, made
    per item, and it is what keeps `considered` honest. `PL-T940` carries the
    case that made it necessary: without a status of its own a killed command
    returned 1, which is what a failing test returns, so the item vanished
    from every finding while the report stayed clean.

    A command that reads past the tree is the one case where neither reading is
    safe to assert, and it is an advisory for that reason (`PL-205P`). Its exit
    status is a fact about the world at the moment it ran, so it can flip with
    no commit behind it: `PL-8GQW`'s `git ls-remote --tags origin v0.4.30`
    failed correctly when `#730` filed it, and began passing the moment the
    project owner pushed the tag - reddening `main` across six commits by five
    unrelated sessions while the repository had not changed. No branch could
    have shown it, because no branch changed anything. `ROADMAP.md` settled the
    same question at the other end of that window - a release whose tag has not
    been pushed yet is an advisory "rather than an error: failing it would turn
    `make check` red on every release branch" - and this is that window seen
    from the far side.

    This is the replay's clause of the `verify:` contract (`PL-6TP8`,
    `subprojects/docket/README.md` § "What a `verify:` exit status proves, and to whom"): exit 0
    is the finding, the never-evaluated statuses are refusals, and a plain
    failure is not read as evidence that the item is open.
    """
    if landed is None:  # a caller that did not ask; every command but `check`
        return
    if not landed.known:
        report.declined.append(f"open items' own `verify:` commands: {landed.declined}")
        return

    # Ahead of the `passing` guard below, because these are owed whether or not
    # anything passed. An item whose command could not answer is not a finding
    # about the item - it is this run saying it has nothing to say about it -
    # so it belongs under "not checked" beside the runs that declined whole,
    # and it must not be reachable only when some other item happens to pass.
    if landed.timed_out:
        one = len(landed.timed_out) == 1
        report.declined.append(
            f"{', '.join(landed.timed_out)}: `verify:` command killed at the "
            f"{landed.limit:g}s limit, so nothing is claimed about "
            f"{'it' if one else 'them'} - the command is either too slow for a "
            "check that runs on every `make check`, or it hangs"
        )
    if landed.unavailable:
        one = len(landed.unavailable) == 1
        report.declined.append(
            f"{', '.join(landed.unavailable)}: `verify:` command was not found by the "
            f"shell, so nothing is claimed about {'it' if one else 'them'} - "
            f"{'its' if one else 'their'} toolchain is missing here, or the command is "
            "misspelled"
        )

    # An error rather than an advisory since `PL-71P4`, and the ordering is what
    # made that affordable: `PL-L9JS` repaired the seven items that passed on a
    # clean tree first, so the rule needed no cutover date, no grandfathered set
    # and no second dated policy beside `verify_required_from`. Both states it
    # reports are actionable and neither may sit - a command that passes without
    # its work is the delegation gate open, and one whose work landed is an item
    # that should have closed. The transient case, a session that ran the work
    # before editing its item, resolves in the same commit the skill already
    # requires: `status: done` travels with the work.
    # Before the two findings below and subtracted from both. A command that
    # reads the remote answers about the world rather than about this commit,
    # so neither the error's "close it" nor the blocked clause's "the command
    # does not discriminate" is safe to assert: the item may simply be open
    # because the work it records landed somewhere no commit can show. It is
    # still worth saying - these are exactly the items nobody remembers to
    # close - so it is an advisory, which prints on every `docket check` a
    # session runs, rather than an error on a default-branch run that by
    # `PL-205P`'s own measurement nobody watches. `ROADMAP.md` decided the
    # same question on the other side of the same window: the tag a release
    # has not yet been given is an advisory "rather than an error: failing it
    # would turn `make check` red on every release branch".
    if landed.external:
        one = len(landed.external) == 1
        report.advisories.append(
            f"{', '.join(landed.external)} {'is' if one else 'are'} open and "
            f"{'its' if one else 'their'} `verify:` command now passes, but that "
            f"command reads past the tree, so {'it' if one else 'they'} can have "
            f"flipped with no commit behind {'it' if one else 'them'} - the work is "
            f"the project owner's and the remote is where it shows. Close "
            f"{'it' if one else 'them'} if the work is done; nothing here fails until "
            f"you do"
        )

    if landed.blocked:
        one = len(landed.blocked) == 1
        report.errors.append(
            f"{', '.join(landed.blocked)} {'is' if one else 'are'} blocked but "
            f"{'its' if one else 'their'} `verify:` command already passes. An item "
            "nobody can start has not had its work land, so the only reading left is "
            "that the command does not discriminate and `docket verify` would ACCEPT a "
            "branch that did none of it: rewrite it to name something only the work "
            "creates, and run it and see it fail before recording it"
        )

    # Everything below is the two-reading finding, so the blocked ids are taken
    # out of it rather than reported twice under a question one of them has
    # already answered.
    named = set(landed.blocked) | set(landed.external)
    startable = tuple(identifier for identifier in landed.passing if identifier not in named)
    if not startable:
        return
    one = len(startable) == 1
    message = (
        f"{', '.join(startable)} {'is' if one else 'are'} open but "
        f"{'its' if one else 'their'} `verify:` command already passes "
        f"({len(startable)} of {landed.considered} checked). Either the work landed "
        "and the item was never closed - close it - or the command does not "
        "discriminate and proves nothing, in which case `docket verify` would ACCEPT a "
        "branch that did none of the work: rewrite it to name something only the work "
        "creates, and run it and see it fail before recording it"
    )
    report.errors.append(message)


def _check_selects_nothing(
    report: Report, landed: LandedReport | None, offered: frozenset[str] | None
) -> None:
    """Say when an item about to be offered has a `verify:` command that selects no test.

    The counterpart to the check above, and the harder of the two to see. That
    one is about a command that returns 0 when it should not; this is about a
    command that returns non-zero for the wrong reason. `-k` matched no test
    name, so pytest deselected the file, collected nothing and exited 5 - and
    5 is not 0, so every reader of an exit status, this module's own
    already-passes check included, takes it for a command that correctly
    fails. The item then looks exactly like one whose work is still to do, and
    goes on looking like it after the work as well, unless a test name happens
    to match. `PL-D2GW` carried one for its whole life; nothing noticed.

    A verdict rather than a candidate, unlike the already-passes advisory,
    because `verify.selects_no_test` reads pytest's own exit code and pytest
    only returns 5 for the one reason. It once stopped short of the repair,
    because a `-k` naming the test the work had yet to write was the shape the
    `docket` skill recommended, so only the item's author could say whether a
    selector was behaving as intended. That ended with `PL-6TP8`, whose
    contract makes the failure before the work an ordinary exit 1, and
    `_k_selector_clause` now refuses the `-k` itself on anything captured from
    its cutover. What this reaches is the set that cutover grandfathers, and
    the repair for each is the same `grep`, so the sentence names it. It stays
    an advisory because those commands are repaired as their items are
    started, and an error here would force the one-pass repair that refuses.

    Reported against what is about to be offered rather than against the whole
    backlog, for the reason `_groom` states in the same words a few functions
    below: when this was written the recommended shape was `-k` naming the
    test the work would add, so every unstarted item using it selected nothing
    until its work landed, and naming all of them fired on every run against
    eighteen of thirty-one open items. That is the advisory that cannot reach
    zero, and its cost is not the items it names but the next advisory, which
    gets read the same way.

    Narrowing rather than softening. The moment an item is offered is the
    first moment its selector can be held against work somebody is about to
    do; before that there is nobody to act on it. The store-wide total rides
    along in the sentence so the scale of the finding is not lost - it is what
    `PL-5QKT` measured and the reason this check exists.

    A caller that supplied no `offered` names nothing: an advisory that
    depends on ranking the queue is not owed by one that did not ask for a
    ranking.

    A declined run says so once, in `_check_landed`: it is one execution of
    one set of commands, and two lines reporting the same refusal would read
    as two checks having failed to run.

    Pytest's 5 is one of the three never-evaluated statuses the `verify:`
    contract lets a consumer name (`PL-6TP8`); `_check_landed` reports the
    other two as not checked.
    """
    if landed is None or not landed.known or not landed.vacuous:
        return
    due = [identifier for identifier in landed.vacuous if identifier in (offered or frozenset())]
    if not due:
        return
    one = len(due) == 1
    report.advisories.append(
        f"{', '.join(due)} {'is' if one else 'are'} next to be offered and "
        f"{'its' if one else 'their'} `verify:` command selects no test "
        f"({len(due)} of {len(landed.vacuous)} open item(s) "
        f"whose command selects nothing, {landed.considered} checked): "
        "pytest collected nothing and exited 5, "
        "which is not 0, so the command reads as one that correctly fails and will read "
        "that way after the work too - replace the selector with a `grep -q` for the "
        "`def` of the test the work adds, as each item is started"
    )


def _note_settings(report: Report, source: SettingsSource | None) -> None:
    """Name the settings this run was governed by, every run, as a fact.

    `_note_cost`'s argument below, applied to policy rather than to runtime: not
    a finding, nobody is asked to act on it, and it earns its line because a
    *change* in it is the signal.

    Here that change is a class of bug this project has already had. `_load`
    resolves settings from the root of the repository holding the store, so
    that `--items` pointed at another project's queue is not answered under
    this project's policy. Resolving it from the store's *parent* instead put
    the whole store on package defaults - no `known_classes`, no
    `workflow_paths`, `top_band_limit` at 5 rather than 12 - and `PL-P757`
    fixed that. What makes it worth a permanent line is how it was found: it
    was the quietest of the three failures that one derivation caused, noticed
    only incidentally while the two louder ones were being repaired, because
    nothing a run printed said which policy it had been read under
    (`PL-K5PW`, filed twice).

    Refusing such a run would be wrong - reading another project's store under
    its own defaults is correct and a real use - so what was missing was never
    a guard but the one fact about a run nobody could see.

    Named on the run that found its config as well as on the run that did not,
    because silence is ambiguous: a reader who sees no line cannot tell a
    config that was found from a version of this command that does not report
    one, and it is the *difference* between two runs' lines that carries the
    diagnosis. One short line, scanned rather than acted on, in the category
    the open-item counts beside it are in.
    """
    if source is None:
        return
    if source.found:
        report.settings = f"settings: {source.path}"
        return
    report.settings = (
        f"settings: no {source.path}, so library defaults govern this run rather than "
        "this project's - a finding below may be this store read under the wrong "
        "policy rather than a store that is wrong"
    )


def _note_cost(report: Report, landed: LandedReport | None) -> None:
    """Say what running the items' own commands cost, every run, as a fact.

    Deliberately not an advisory. `CLAUDE.md` holds that a check firing every
    run without changing a decision is a defect in the check, and that is
    right - but it is a rule about findings, which demand judgment and go
    stale as a class. This is the same category as the open-item counts beside
    it: a number the reader scans, nobody is asked to act on, and which is
    worth its line only because a *change* in it is the signal.

    That change is what this exists to expose. Two comments in `verify.py`
    carried these figures by hand and both went stale inside a fortnight, and
    the reason neither was caught is that the run reported nothing about
    itself: on a healthy store `docket check` printed no cost at all, so the
    pool going from 10.1s to 28.8s and the serial total from 34.9s to 175.5s
    were invisible to every session that paid them (`PL-9NKK`). A figure
    nobody can see cannot be noticed to have moved.

    `serial` is on the line for the same reason and is the more important
    half. Concurrency holds `elapsed` roughly flat while the queue grows, so
    the number a session feels is the one that hides the growth; the serial
    total is what the store actually asks for and it climbs with every item
    triaged to `ready`.

    The worst command is given against `limit` rather than alone, because that
    margin is the whole question `LANDED_TIMEOUT` is set to answer, and it is
    the one a bare duration cannot be read for. It names the command whatever
    the rest of the pool looks like, which is now the whole of the project's
    answer on cost: an advisory beside this one named a command 30x above the
    pool's median, and it was retired 2026-09-19 because a store whose typical
    `verify:` is a test-file run has no such outlier to find. Measured that
    day, the ratio fired on zero of thirteen real branch scopes and on nothing
    in a whole store holding a 67.4 s command - and the silence was right,
    because 1458 s of serial work over eight workers is a 182 s floor against
    204 s elapsed, so the queue is what the run waits for rather than any one
    command. `verify.py`'s constants block carries the count (`PL-G6J5`).

    Which leaves this line carrying the signal alone, and it is built for that:
    `serial` is where a store that is uniformly heavy shows up, and the margin
    between `slowest` and `limit` is where a single command closing on the
    timeout does.

    Silent where the run declined, where no caller asked, and where the store
    holds no command to run - printing zeros would be this module's own
    cardinal error, an empty result rendered as a measured one.
    """
    if landed is None or not landed.known:
        return
    # A scoped run says so even when it found nothing to run, which is the one
    # case with no cost to report and the one where silence misleads: a reader
    # who is not told the run was narrowed reads an absent line as a whole
    # store with no commands in it (`PL-SDHR`).
    if landed.slowest is None:
        if landed.scope:
            report.cost = f"verify: no command to run in {landed.scope}"
        return
    one = landed.considered == 1
    scope = f", scoped to {landed.scope}" if landed.scope else ""
    report.cost = (
        f"verify: {landed.considered} {'command' if one else 'commands'} in "
        f"{landed.elapsed:.1f}s ({landed.serial:.1f}s serially){scope}; slowest "
        f"{landed.slowest.identifier} {landed.slowest.seconds:.1f}s "
        f"against a {landed.limit:g}s limit"
    )


def _check_references(report: Report, milestones: MilestoneStates | None = None) -> None:
    """Hold every cross-reference to an item, or a milestone, that exists.

    `blocked-by` carries two kinds of entry since `PL-W8XP`, and both are held
    to something real: an id must name an item in this store, a `vX.Y.Z` must
    name a milestone the roadmap places. The second check is what keeps a
    milestone blocker from being a way to park an item forever - a typo would
    otherwise read as a dependency on something that is never going to be
    scoped, which is indistinguishable from a live block and never fires.

    Without a readable roadmap the milestone half declines rather than
    guessing, and `analyze` says so: refusing an entry no file was read to
    check would fail a bare checkout for the roadmap's absence.
    """
    known = {item.identifier for item in report.items if item.identifier}
    for item in report.items:
        for blocker in item.blocking_items:
            if blocker == item.identifier:
                report.errors.append(f"{_where(item)}: lists itself as a blocker")
            elif blocker not in known:
                near_miss = (
                    " (a milestone blocker is written `vX.Y.Z`, in full)"
                    if blocker.startswith("v")
                    else ""
                )
                report.errors.append(
                    f"{_where(item)}: blocked by {blocker}, which is not an item{near_miss}"
                )
        if milestones is None:
            continue
        for version in item.blocking_milestones:
            if not milestones.is_known(version):
                report.errors.append(
                    f"{_where(item)}: blocked by {version}, which the roadmap places "
                    "nowhere; a milestone blocker names a milestone on the timeline or "
                    "with a section of its own"
                )

    _check_root_causes(report, known)
    _check_generator_verdicts(report, known)
    _check_recurrences(report, known)

    known_items = {i.identifier: i for i in report.items}
    _outranks_its_blocker(report, known_items)
    _ready_with_an_open_blocker(report, known_items)
    _check_prose_dependencies(report, known_items)

    duplicates = [
        identifier
        for identifier, count in Counter(
            item.identifier for item in report.items if item.identifier
        ).items()
        if count > 1
    ]
    for identifier in sorted(duplicates):
        paths = ", ".join(sorted(i.path for i in report.items if i.identifier == identifier))
        report.errors.append(f"{identifier}: used by more than one file ({paths})")


def _check_root_causes(report: Report, known: set[str]) -> None:
    """Hold a `root-cause-of:` to naming real items, and enough of them.

    This is the one field in the store where a typo buys a promotion: a sound
    claim ranks its item above every band but `P0`, ahead of a `safety`-classed
    `P1`, which the project owner was asked about and confirmed. So the ids it
    names are held to existing, exactly as `blocked-by`'s are.

    The failure this catches is quiet rather than loud. `plan.py` refuses to
    rank an unsound claim - it reads the same `root_cause_faults`, so the two
    cannot drift - which means a mistyped id does not mis-rank anything. It
    does something worse: the session that recorded the generator believes the
    mechanism is now ranked, and nothing else in the project would ever say it
    is not. This is what says it.

    Errors rather than advisories, on both halves. Whether a mechanism really
    causes three items is judgment and is not checked anywhere; whether the ids
    exist and whether there are three of them are exact rules, which is what
    `CLAUDE.md` reserves hard failure for.
    """
    for item in report.items:
        faults = root_cause_faults(item, known)
        if not faults:
            continue
        report.errors.append(
            f"{_where(item)}: `root-cause-of:` {'; '.join(faults)}. `docket next` "
            f"ranks a sound claim above every band but P0 and ignores an unsound one, "
            f"so this generator is recorded and unranked until the field is repaired"
        )


def _check_generator_verdicts(report: Report, known: set[str]) -> None:
    """Hold a recorded generator to saying whether its mechanism is still running.

    The check beside this one holds a `root-cause-of:` to naming three real
    items, which is what decides the claim is *recorded*. This holds the
    separate question that decides whether it *ranks* above every band but
    `P0` (project owner, 2026-09-21, ratified): is the store still handing this
    mechanism new members, or is it spent?

    It fails the same quiet way as the two around it, and that is the whole
    reason it is an error rather than an advisory. `plan.py` refuses to rank a
    claim carrying no verdict - it reads the same `generator_faults`, so the
    two cannot drift - so an absent verdict mis-ranks nothing. What it does is
    leave the session that recorded a live generator believing the mechanism is
    now ranked above every safety item in the queue, with nothing else in the
    project ever saying it is not. This is what says it.

    The decidable half only, as everywhere else here: whether the field opens
    with a word from the vocabulary, whether a reason follows it, whether a
    verdict has a cluster to be about. Whether a mechanism is *really* spent is
    judgment, is checked nowhere, and is what the reason beside the verdict is
    for.
    """
    for item in report.items:
        faults = generator_faults(item, known)
        if not faults:
            continue
        report.errors.append(
            f"{_where(item)}: `generator:` {'; '.join(faults)}. The count decides whether a "
            f"generator is recorded and this decides whether it ranks, so until the field "
            f"is repaired `docket next` offers this on its band like any other item"
        )


def _check_recurrences(report: Report, known: set[str]) -> None:
    """Hold a `recurrences:` entry to being readable as a filing.

    Weaker in consequence than the two generator checks around it and worth the
    same treatment. This field surfaces a promotion candidate and never promotes
    one, so a bad entry cannot mis-rank anything - what it can do is make the
    count wrong in the quiet direction, since `recurrence_count` can only count
    the entries it can read. An item filed four times whose third entry is
    unreadable sits one short of the threshold and nothing says why.

    The field is written by `bin/docket new` and by nothing else, so every
    fault here is a hand edit that went wrong. Exact rules, and so errors: the
    judgment half - whether the two items are really one defect - is what this
    whole mechanism refuses to decide, and is not checked anywhere.
    """
    for item in report.items:
        faults = recurrence_faults(item, known)
        if not faults:
            continue
        report.errors.append(
            f"{_where(item)}: `recurrences:` {'; '.join(faults)}. The count is what "
            f"surfaces this item as a generator-tier candidate, so an entry nothing can "
            f"read is a filing the store will not show you"
        )


def _check_generator_defects(report: Report, config: Config) -> None:
    """Hold an `impairs-generators:` to reaching the machinery it claims to break.

    The tier's other entrance, and it fails the same quiet way as the first.
    `plan.py` refuses to rank an unsound claim - it reads the same
    `generator_defect_faults`, so the two cannot drift - so a bad field
    mis-ranks nothing. What it does instead is leave the session that recorded
    the defect believing it is now ranked above every band, with nothing in the
    project ever saying otherwise. This is what says it.

    Errors rather than advisories, because both halves are exact rules.
    Whether a defect really impairs generator identification is judgment and is
    checked nowhere; whether the field holds a reason rather than a boolean,
    and whether the item's `touches` reaches a declared `generator_path`, are
    decidable - which is what `CLAUDE.md` reserves hard failure for.
    """
    for item in report.items:
        faults = generator_defect_faults(item, config.generator_paths)
        if not faults:
            continue
        report.errors.append(
            f"{_where(item)}: `impairs-generators:` {'; '.join(faults)}. `docket next` "
            f"ranks a sound claim on the generator tier, above every band but P0, and "
            f"ignores an unsound one, so this defect is recorded and unranked until the "
            f"field is repaired"
        )


def _declared_item_file(entry: str, items_dir: str) -> tuple[str, str] | None:
    """The (id, filename) a `touches` entry names inside the store, or `None`.

    `None` for every entry that is not a claim about one item's file: a path
    outside the store, the store directory itself, a subdirectory, anything
    inside it that no id leads. Decided from the name rather than by asking
    the filesystem, which keeps `analyze` pure - and the id is also the more
    useful half, since it is what lets the error below say where the item
    actually lives instead of only that the path is wrong.
    """
    prefix = items_dir.strip().strip("/")
    candidate = entry.strip().strip("/")
    if not candidate.startswith(f"{prefix}/"):
        return None
    name = candidate[len(prefix) + 1 :]
    match = DECLARED_ITEM_RE.match(name)
    return None if match is None else (match.group(1), name)


def _declarers(report: Report, items_dir: str) -> dict[str, list[str]]:
    """Which items name each item file in their `touches`, keyed by filename.

    Read by both halves of `PL-Y5JX` - the error that holds a declaration to
    naming a file some item lives in, and the stale-slug advisory that has to
    say when the rename it proposes would break one. One function, so the two
    cannot come to different views of what a declaration is.
    """
    declared: dict[str, list[str]] = {}
    for item in report.items:
        for entry in item.touches:
            named = _declared_item_file(entry, items_dir)
            if named is not None:
                declared.setdefault(named[1], []).append(item.identifier)
    return {name: sorted(set(ids)) for name, ids in declared.items()}


def _check_touched_items(report: Report, config: Config) -> None:
    """Hold a `touches` entry naming an item file to naming one that exists.

    Naming another item's file in `touches` is legitimate and correct - an
    item whose work is editing two briefs has to declare both - and it is the
    one entry a rename can invalidate from outside the item. The store names a
    file from its title, so any command that re-renders a retitled brief moves
    it, and a declaration written when the title was one thing then points at
    nothing. Two sat on `origin/main` that way on 2026-09-19 with `make check`
    passing: `PL-3V6C` naming `PL-XQRK`, moved by the `v0.4.28` cut, and
    `PL-GNXG` naming `PL-J3ZK` (`PL-Y5JX`).

    An error rather than an advisory, on the failure rather than the remedy.
    Whether a declared item file exists is exactly decidable, which is what
    `CLAUDE.md` reserves hard failure for, and the repair is a one-line edit to
    the declaring item with no other branch to check first - unlike the rename
    in `_check_filenames` below, whose remedy is what keeps it advisory.

    The `PL-YTDN` pass is why this is code and not a line in a skill. That
    pass renamed the drifted files, searched the store by hand for the
    declarations naming them, and repaired two - editing the very `touches`
    line that carried `PL-3V6C`'s already-dangling entry for `PL-XQRK`
    without seeing it. A hand search run by a session being careful about
    exactly this missed the instance sitting beside the one it repaired.
    """
    lives_in = {item.identifier: item.path for item in report.items if item.identifier}
    unknown_home: set[str] = set()
    for item in report.items:
        for entry in item.touches:
            named = _declared_item_file(entry, config.items_dir)
            if named is None:
                continue
            identifier, name = named
            if identifier not in lives_in:
                report.errors.append(
                    f"{_where(item)}: `touches` names {entry}, and this store holds no "
                    f"{identifier}; {DANGLING_TOUCHES}"
                )
            elif not lives_in[identifier]:
                unknown_home.add(identifier)
            elif lives_in[identifier] != name:
                report.errors.append(
                    f"{_where(item)}: `touches` names {entry}, which no item lives in - "
                    f"{identifier} is in {config.items_dir}/{lives_in[identifier]}; "
                    f"{DANGLING_TOUCHES}"
                )
    if unknown_home:
        report.declined.append(
            f"whether the `touches` entries naming {', '.join(sorted(unknown_home))} name "
            "the file each lives in: those items were built in memory and carry no filename"
        )


def _check_filenames(report: Report, config: Config) -> None:
    """Report an item file whose name no longer matches the slug its title makes.

    The store names a file from its title, so the two can only disagree after
    a title is edited in place - and nothing then says so. `PL-3D2M` sat on
    `origin/main` under the slug of a title it no longer had, with `make
    check` passing, until an unrelated `bin/docket record` run happened to
    re-render the file and rename it (`PL-3833`). The filename is how a
    session finds an item by hand, so a stale slug sends it to the wrong
    mental model of what the item is about.

    An advisory rather than an error, and the reason is the remedy rather
    than the rule. Deriving the slug and comparing it is exactly decidable,
    which is what `CLAUDE.md` reserves hard failure for; renaming the file is
    not, because the session that would do it has to know who else is holding
    that file first. A rename arriving as a side effect of an unrelated
    command is how `PL-36R4` became a rename-against-edit conflict for
    whoever merged second, on 2026-09-08, and an error here would force
    exactly that: nine files on this store carry drift today, so `make check`
    would fail until someone renamed all nine in one pass, against whatever
    branches were open at the time.

    Named in one line rather than one per file. Nine advisory lines is the
    disease `PL-CW14` describes in the same function - an advisory nobody can
    clear in the moment, printed often enough to train a session to skim the
    one below it.

    Declines on an item carrying no path: those are built in memory rather
    than read from disk, and there is no filename to disagree with.

    **And it says when the rename it proposes would break a declaration.**
    Another item's `touches` may name the file by full path, which is
    legitimate - `PL-3V6C`'s whole deliverable was editing two briefs - so
    without this the advisory is an instruction to break a declaration, issued
    to a reader with no reason to look (`PL-Y5JX`). `_check_touched_items`
    above catches the break afterwards; naming it here is what lets a session
    repair both halves in the one commit, which is the difference between a
    clean rename and a `make check` that fails on the next branch.
    """
    drifted = [
        item
        for item in report.items
        if item.path and item.identifier and item.path != filename_for(item)
    ]
    if not drifted:
        return
    one = len(drifted) == 1
    in_order = sorted(drifted, key=lambda i: i.identifier)
    declared = _declarers(report, config.items_dir)
    coupled = [
        f"{item.identifier} (by {', '.join(declared[item.path])})"
        for item in in_order
        if item.path in declared
    ]
    report.advisories.append(
        f"{len(drifted)} item file{'' if one else 's'} carr{'ies' if one else 'y'} a slug "
        f"{'its' if one else 'their'} title no longer generates "
        f"({', '.join(item.identifier for item in in_order)}); "
        "rename with `git mv` to the name `docket` would write, and check first that no open "
        "branch is editing the file - a rename against someone else's edit conflicts"
        + (
            f". Another item's `touches` declares {'; '.join(coupled)}, so repair those "
            "entries in the same commit or the rename leaves them naming nothing"
            if coupled
            else ""
        )
    )


def _outranks_its_blocker(report: Report, known_items: dict[str, Item]) -> None:
    """Refuse an item that ranks above the work it is waiting on.

    A blocked item cannot be started, so its band is a promise about when it
    will be - and that promise is only as good as the blocker's. A P1 waiting
    on a P3 says the queue will reach it soon while ranking the one thing in
    the way below fifty other items, which is not a schedule but a hiding
    place. It is the mechanism by which a live safety defect goes quiet: it
    keeps its band, passes every other rule, and never comes up.

    The fix is always the same and always the blocker's - raise it to meet what
    it holds up - so the error names that rather than offering a choice.
    Lowering the blocked item instead is available and is not suggested, since
    on a safety item that is the re-classing this checker exists to prevent.

    Only open blockers are compared: a closed one holds nothing up, and a done
    item's priority is often cleared outright.
    """
    for item in report.items:
        if item.status != "blocked" or item.priority not in PRIORITIES:
            continue
        # Items only: a milestone has no band to be outranked by.
        for identifier in item.blocking_items:
            blocker = known_items.get(identifier)
            if blocker is None or not blocker.is_open or blocker.priority not in PRIORITIES:
                continue
            if PRIORITIES.index(item.priority) < PRIORITIES.index(blocker.priority):
                report.errors.append(
                    f"{_where(item)}: is {item.priority} but waits on {identifier} at "
                    f"{blocker.priority}; raise {identifier} to {item.priority} or above, "
                    "because nothing here can start before it does"
                )


# The phrases by which a brief states that *this* item waits on another. Each
# is a declaration rather than a narration, which is what makes the direction
# readable: "depends on X" says this comes second, and no measured instance of
# one of these says the reverse.
#
# `after` and `before` were both measured and both left out, for opposite
# reasons. `before X` and `follows X` mean this one goes *first*, so every one
# of the four hits they had in this store named the edge backwards - an
# advisory telling an item to declare a blocker it actually blocks is a wrong
# answer stated in the tool's own voice, which is the failure mode this module
# exists to avoid. `after X` points the right way but does not distinguish a
# prerequisite from a narration: "Do this after `PL-GS5X`" and "Amended
# 2026-09-03, after `PL-WB0X` merged" are the same shape, and the store held
# roughly eight of the second against three of the first. The second cannot be
# cleared except by rewriting prose that is already correct, which is the
# advisory-that-cannot-reach-zero this check was required not to become
# (`PL-H7XN`, `PL-G049`).
PREREQUISITE_CUES = (
    r"depend(?:s|ent|ing)?\s+(?:up)?on",
    r"block(?:ed|s|ing)?\s+on",
    r"blocked\s+by",
    r"wait(?:s|ing)?\s+(?:on|for)",
    r"requires?",
)

# The cue, then the id within the same clause. `(?:\.?\*\*)?` lets the item
# format's own `**Depends on.**` heading count as one cue rather than as a cue
# followed by a sentence break - and the gap still refuses `.`, so
# `**Depends on.** Nothing. \`PL-2SVR\`` stays silent, which is the answer that
# item deserves. The other excluded characters are clause boundaries: without
# them the window jumps a semicolon or a closing bracket into an unrelated
# mention, which was where the false positives came from.
PROSE_DEPENDENCY = re.compile(
    rf"\b(?:{'|'.join(PREREQUISITE_CUES)})\b(?:\.?\*\*)?[^.\n;:()\"|—]{{0,40}}?`?({ID_PATTERN})`?",
    re.IGNORECASE,
)

# A *second* blocker written as a continuation of the first - "blocked on A and
# on B" - which the cue-then-id form above reads only the first half of. It is a
# separate pattern rather than another entry in the cue list because "and on" is
# ordinary English: unanchored it fires on "reports on `PL-A` and on `PL-B`",
# which states no prerequisite at all. So a continuation counts only inside a
# paragraph that already carries a real cue, which `_cued_paragraphs` supplies.
#
# `PL-GGCN` is what this cost. `PL-VZL0` names `PL-GS5X` and `PL-X2XX` off one
# cue, declares only the first, and nothing fired - the first id was skipped as
# declared and the second matched no cue - so an open prerequisite of a v0.4.1
# item stayed invisible to `docket next` while the check reported clean.
PROSE_DEPENDENCY_CONTINUATION = re.compile(
    rf"\band\s+(?:(?:up)?on|by)\b(?:\.?\*\*)?[^.\n;:()\"|—]{{0,40}}?`?({ID_PATTERN})`?",
    re.IGNORECASE,
)


def _ready_with_an_open_blocker(report: Report, known_items: dict[str, Item]) -> None:
    """Refuse `ready` on an item that says it is waiting for something open.

    `ready` asserts the work can be started now and `blocked-by` asserts it
    cannot, so an item carrying both is a plain contradiction. The ranking
    reads only the status - `plan.py` filters on `status != "blocked"` and
    never opens `blocked_by`, which `concurrency.py` alone consumes - so the
    edge can be declared, every other check pass, and `docket next` still
    offer the item ahead of the work it says it waits on. Silently, which is
    the property `CLAUDE.md` names as earning attention (`PL-KBD0`).

    This is `PL-ZBRB`'s defect displaced by one step rather than fixed: that
    advisory made an undeclared prose prerequisite visible, and this is the
    state an author reaches after acting on it and stopping one field early.
    `PL-ZBRB`'s message has to name both fields to work around it, which is a
    message doing a checker's job.

    **`needs-decision` is deliberately not reached**, though it can hold the
    same contradiction. Forcing it to `blocked` would take it out of
    `bin/docket gate`, which counts that status as debt somebody can go and
    resolve - so the item would leave the gate by being renamed rather than by
    being answered, and a pending decision would go quiet. Its declared edge
    staying invisible to the ranking is the smaller harm of the two, and is
    accepted here rather than overlooked.

    Items only, never milestones. `blocking_items` is the fail-closed half of
    the field, and a milestone blocker clears when a scoping round happens
    rather than when an item closes, which `_groom` already reads the roadmap
    to decide.

    An unknown blocker is left alone: `_check_references` already errors on it
    by name, and a second error here would say the fix is a status change when
    it is a typo.
    """

    for item in report.items:
        if item.status != "ready":
            continue
        open_blockers = [
            identifier
            for identifier in item.blocking_items
            if (blocker := known_items.get(identifier)) is not None and blocker.is_open
        ]
        if not open_blockers:
            continue
        one = len(open_blockers) == 1
        report.errors.append(
            f"{_where(item)}: sits at `ready` while {', '.join(open_blockers)} "
            f"{'is' if one else 'are'} still open; `ready` says the work can be started "
            f"now, so set `status: blocked`, or drop the {'edge' if one else 'edges'} if "
            "it no longer holds"
        )


def _check_prose_dependencies(report: Report, known_items: dict[str, Item]) -> None:
    """An item that states a prerequisite in prose and never declares it.

    `blocked-by` is what the ranking reads; the body is what a person reads.
    When they disagree the body is invisible, and the failure is silent in the
    way `CLAUDE.md` singles out: `docket next` ranks on front matter and never
    opens a brief, so it states a sound-looking reason for an order the brief
    contradicts, and the session that trusts it either finds the dependency on
    reading the item - the cheap outcome - or does not, and redoes the work.
    Every instance so far cost a person to find it (`PL-9K7K`, `PL-THVN`,
    `PL-5WFS`, `PL-SN2C`), which is the recurring cost this replaces.

    Only *open* blockers fire. Most in-body mentions name work that has since
    closed, which is history rather than a defect, and firing on those would
    make the advisory unreadable inside a week.

    An advisory and never an error, because only half of this is decidable.
    Whether the id is declared is a fact; whether the sentence really states a
    prerequisite - and whether `blocked` is the right word for it - is judgment,
    and is left where judgment belongs. Either answer clears it: declare the
    edge, or reword a sentence that was not claiming one.

    The message names `status: blocked` alongside the edge because `blocked-by`
    on its own changes nothing here: `plan` filters on `status`, so an item can
    carry the edge, satisfy this check, and still be offered ahead of the work
    it waits on. Naming only the field this check reads would be a fix that
    does not fix what it claims to - the same silent wrong answer, moved one
    step along. Three items are in that state today; `PL-KBD0` is whether the
    checker should hold the two fields together.

    What it cannot see, which is most of the problem:

    - **A dependency neither brief mentions.** `PL-011` -> `PL-W3DD` was
      visible only to someone who knew that re-keying the record invalidates a
      memory measurement. No regex reaches that, and a clean run here is not
      evidence the store's dependency graph is complete.
    - **Sequencing written with `after`,** for the reason the cue list gives
      above: the phrasing that states it is the phrasing that narrates it.
    - **A sentence about some third item's dependency.** "then `PL-SN2C`,
      which depends on `PL-VM40`" is a true sentence in a brief that owns
      neither edge; the subject of the verb is not something a regex settles.

    A fourth used to belong here and no longer does: a second blocker written
    as "and on B" after the cue that introduced A. `PROSE_DEPENDENCY` stops at
    the first id, so the compound form - the natural way to state two
    prerequisites - was the one shape the check could not see, and it reported
    clean over a real open edge (`PL-GGCN`). `PROSE_DEPENDENCY_CONTINUATION`
    covers it, anchored to a paragraph that already carries a cue.

    So this reports what it matched and claims nothing about what it did not.
    """
    for item in report.items:
        if not item.is_open:
            continue
        seen: set[str] = set()
        for match in _prerequisite_matches(item.body):
            other = match.group(1)
            blocker = known_items.get(other)
            if blocker is None or other == item.identifier or not blocker.is_open:
                continue
            if other in item.blocking_items or other in seen:
                continue
            seen.add(other)
            report.advisories.append(
                f"{_where(item)}: names {other} as a prerequisite in prose and does not list "
                f'it in `blocked-by` - "{_sentence(item.body, match)}". Declare the edge and '
                "set `status: blocked`, which is the half `docket next` reads, or reword the "
                "sentence if it is not a prerequisite"
            )


def _prerequisite_matches(body: str) -> list[re.Match[str]]:
    """Every id the body states a prerequisite on, in the order they appear.

    Two patterns, because a brief states the second blocker differently from
    the first: `PROSE_DEPENDENCY` reads "blocked on A", and
    `PROSE_DEPENDENCY_CONTINUATION` reads the "and on B" that follows it. The
    continuation is admitted only where a cue already fired in the same
    paragraph, which is what keeps "and on" from matching ordinary prose.

    Ordered by position so the advisories for one item read in the order a
    person meets them in the file.
    """
    cued = _cued_paragraphs(body)
    matches = list(PROSE_DEPENDENCY.finditer(body))
    matches += [
        match
        for match in PROSE_DEPENDENCY_CONTINUATION.finditer(body)
        if any(start <= match.start() < end for start, end in cued)
    ]
    return sorted(matches, key=lambda match: match.start())


def _cued_paragraphs(body: str) -> list[tuple[int, int]]:
    """The blank-line-delimited blocks in which a prerequisite cue fired.

    The paragraph rather than the line, because the item format wraps at 80
    columns: `PL-VZL0` puts "Blocked on `PL-GS5X`" on one line and "and on
    `PL-X2XX`" on the next, so a line-scoped anchor would miss exactly the case
    this exists for. The paragraph rather than the whole body, because a brief
    that states one real dependency should not thereby license every "and on"
    in the rest of the file.
    """
    bounds: list[tuple[int, int]] = []
    for match in PROSE_DEPENDENCY.finditer(body):
        opened = body.rfind("\n\n", 0, match.start())
        start = 0 if opened < 0 else opened + 2
        closed = body.find("\n\n", match.start())
        bounds.append((start, len(body) if closed < 0 else closed))
    return bounds


def _sentence(body: str, match: re.Match[str]) -> str:
    """The line a match sits on, collapsed to one line and bounded for a message.

    The line rather than a parsed sentence: the item format writes prose
    wrapped at 80 columns with bold headings inside it, so `.` is not a
    reliable sentence boundary here - `**Depends on.**` carries one - while the
    line reliably carries enough of the claim for a reader to judge it without
    opening the file.
    """
    start = body.rfind("\n", 0, match.start()) + 1
    end = body.find("\n", match.end())
    line = " ".join(body[start : end if end != -1 else len(body)].split())
    return line if len(line) <= 110 else line[:109] + "…"


def _check_closures(report: Report, closures: ClosureReport | None) -> None:
    """Hold a closure to its `pr`, but only once the closure has landed.

    The number does not exist until the pull request is open, so an item
    cannot be closed in the same commit as the work it closes *and* carry it.
    Requiring it unconditionally forced the closure into a second push, and a
    merge arriving inside that window took the work and left the closure on
    the branch: `main` had the fix while the queue still called the item open
    and a debt gate still counted it (`PL-D2GW`, then `PL-P5S0`). The window
    was 100 seconds wide the once it was measured, and it is open on every
    item.

    So the rule moves to where the number is certainly available. An item that
    reads `done` on the default base has had its pull request, and an empty
    `pr` there is a real gap in the provenance. One that reads `done` only in
    the working tree is a closure still in flight, which is now the expected
    shape rather than an error - and is what lets the closure travel in the
    same commit as its work, which is what closes the window rather than
    moving it.

    `commit` stays legal and is still checked for shape where it appears; it
    is simply not what makes a closure traceable across a squash-merge.

    What is left splits again, on whether the provenance is actually lost.
    The number does not exist until the work is pushed and the pull request
    opened, so a closure committed with its work - which is what closes the
    window above - cannot carry it, and every merge would land red. Where the
    merge commit's own subject names the number, nothing is lost: it is the
    same parse this module already trusts for the provenance history, and the
    way back exists in git. That is a transcription still owed, which is an
    advisory naming the number to write.

    That advisory names a command rather than a line to type, and the
    difference is the whole of `PL-N5WZ`. `docket record` writes every number
    this same reading has already derived, so the field costs no commit of its
    own - it rides whatever the session was about to commit anyway. Retyping
    the number by hand is what cost a commit and usually a pull request after
    every merge that closed anything, and what let two sessions open `#229` and
    `#230` for one identical insertion (`PL-QTSB`).

    Where no commit on the base names one, the answer depends on whether the
    checkout could have seen it. Only a complete history makes "no commit
    names a number" mean the way back is gone; a truncated one makes it mean
    the commit is out of reach, which is not the same claim and must not be
    reported as one. `main` went red twice on that conflation (`PL-99Y4`):
    CI checked out at `fetch-depth: 1`, so a closure stayed an advisory on its
    own merge commit and became an error one merge later, when nothing about
    the provenance had changed. So the error is reserved for a checkout that
    says outright it is complete, and truncation - or a git that will not say -
    declines with the ids, which is this module's standing answer to a question
    the tree cannot support.
    """
    if closures is None:  # a caller that did not ask; every command but `check`
        return
    if not closures.known:
        report.declined.append(f"closures recording no `pr`: {closures.declined}")
        return
    derived = closures.numbers
    unreadable: list[str] = []
    for item in report.items:
        if item.status != "done" or item.pr or item.identifier not in closures.landed:
            continue
        number = derived.get(item.identifier)
        if number is not None:
            report.advisories.append(
                f"{item.identifier}: marked done on `{closures.base}` and records no `pr`, "
                f"but #{number} is recoverable from its merge commit; `docket record` "
                f"writes it - and every other number the base is owed - in one pass. Let "
                f"it ride the commit you are already making rather than composing one"
            )
        elif closures.shallow is False:
            report.errors.append(
                f"{_where(item)}: marked done on `{closures.base}` but records no `pr`; "
                "without it there is no way back from the closure to the work that made it"
            )
        else:
            unreadable.append(item.identifier)

    if unreadable:
        depth = (
            "the checkout is a shallow clone"
            if closures.shallow
            else "git cannot say whether this checkout is complete"
        )
        report.declined.append(
            f"whether {', '.join(sorted(unreadable))} lost provenance by recording no `pr`: "
            f"{depth}, so the merge commit naming each number can lie outside it and its "
            f"absence proves nothing; a full-history checkout answers"
        )


def _check_records(report: Report, records: RecordReport | None) -> None:
    """Hold a closed item's `verify:` to the command that was actually run.

    **The decision this enforces.** A closed item's command records what proved
    the work; it is not a live assertion about the tree. That is not a
    preference between two readings - it is the only one the field can bear.
    Measured over this store, 14 of the 179 closed items carrying a command no
    longer resolve, and not one of the 14 is a defect: each is later work
    correctly consuming the state its predecessor established. Four are
    `grep '^blocked-by: PL-...'` against an item file, which pass exactly while
    the blocker is unresolved and are written in the expectation of stopping.
    A field whose commands are designed to become false cannot be read as a
    standing claim.

    **So the hazard is the repair, not the rot.** A session meeting a dead
    command helpfully re-points it at whatever covers the ground now - and the
    item then names a command that never ran against the work it claims to
    prove. That is the failure `CLAUDE.md` names for tooling: output that looks
    authoritative and is not, arrived at from a true record rather than an
    absent one. Nothing else here stops it, because every other reading of
    `verify:` asks about *open* items.

    **An error rather than an advisory, because the rule is exact.** Whether
    the field differs from the base's is decidable without judgment, and the
    reading is one-sided: `_changed_items` returns nothing where it cannot
    resolve a merge base, so this under-reports on a truncated checkout and
    never accuses a branch of an edit it did not make.

    The escape hatch needs no flag and is deliberately visible. An item that is
    genuinely not done is reopened, and a reopened item is not `done` in the
    working tree, so the field is writable again the moment its status admits
    the work is not finished.
    """
    if records is None:  # a caller that did not ask; every command but `check`
        return
    if not records.known:
        report.declined.append(
            f"whether a closed item's recorded `verify:` was rewritten here: {records.declined}"
        )
        return
    recorded = records.commands
    for item in report.items:
        if item.status != "done":
            continue
        was = recorded.get(item.identifier)
        if was is None or was == item.verify:
            continue
        if not was:
            report.errors.append(
                f"{_where(item)}: closed on `{records.base}` recording no `verify:`, and this "
                f"branch adds `{item.verify}`. The work has merged, so there is nothing left "
                "to run the command against and it records nothing about what proved the "
                "item; leave the field empty and put the correction in the body"
            )
        else:
            report.errors.append(
                f"{_where(item)}: closed on `{records.base}` recording `verify: {was}`, and "
                f"this branch changes it to `{item.verify}`. A closed item's command is the "
                "record of what was run, not a live command - re-pointing one replaces the "
                "command that proved the work with one that never ran it. Restore the "
                "recorded command; where the item is genuinely not done, reopen it and the "
                "field is writable again"
            )
    _check_landing_records(report, records)


def _check_landing_records(report: Report, records: RecordReport) -> None:
    """Hold a closed item's `closed:` and `milestone:` to what the base recorded.

    **The same argument as `verify:`, one field over** (`PL-JSRH`). `closed:` is
    when the work landed and `milestone:` is which release shipped it. Both are
    written once, by the branch that closed the item; both are read back long
    afterwards - `closed:` by `docket gate`, deciding which side of a freeze an
    item falls on, and `milestone:` by `docket release` and `wave`, deciding
    whose notes it belongs in - and neither had anything stopping a branch
    rewriting it. `pr:` is the fourth field of the set and was already covered
    from the other side, since `docket record` refuses to overwrite a different
    number, which is what made the gap in these two visible.

    **The severities differ, and that is the judgment this item existed to
    make.** A rewritten `milestone:` moves an item between releases, so two sets
    of release notes are wrong and nothing says so; `docket release` writes the
    field and no hand-edit of it is a repair, so the rule is exact and it is an
    error. A mistyped `closed:` date is different in kind: correcting one is a
    legitimate repair, and the field is a date a human typed rather than a value
    a tool dictated. So that is reported and not refused - the reader is told
    what changed and decides, which is what `CLAUDE.md` asks of a signal needing
    context.

    Both readings are one-sided in the same direction `verify:`'s is:
    `_changed_items` returns nothing where it cannot resolve a merge base, so a
    truncated checkout under-reports and never accuses a branch of an edit it
    did not make. The escape hatch is the same too, and needs no flag: reopen the
    item and it is no longer `done` here, so the fields are writable again.
    """
    landed = records.landings
    for item in report.items:
        if item.status != "done":
            continue
        was = landed.get(item.identifier)
        if was is None:
            continue
        if was.milestone and was.milestone != item.milestone:
            report.errors.append(
                f"{_where(item)}: closed on `{records.base}` recording "
                f"`milestone: {was.milestone}`, and this branch changes it to "
                f"`{item.milestone or '(nothing)'}`. Which release shipped an item is a record "
                f"`docket release` wrote - moving it makes the notes for two releases wrong and "
                "nothing else reports it. Restore the recorded milestone; where the item is "
                "genuinely not done, reopen it and the field is writable again"
            )
        if was.closed and was.closed != item.closed:
            report.advisories.append(
                f"{_where(item)}: closed on `{records.base}` recording "
                f"`closed: {was.closed.isoformat()}`, and this branch changes it to "
                f"`{item.closed.isoformat() if item.closed else '(nothing)'}`. That date is what "
                "`docket gate` reads to decide which side of a debt-gate freeze the item falls "
                "on. Correcting a mistyped date is a legitimate repair, so this is reported "
                "rather than refused - confirm it is one"
            )


#: How many threads a stale-thread advisory names before it stops being one
#: line a reader takes in, and how much of each heading it prints. Lower than
#: `_named`'s eight ids because a heading is a sentence rather than a token,
#: and clipped for the same reason: the line number beside it is what the
#: reader navigates by, so the words are there to be recognized rather than
#: reproduced. An advisory nobody finishes reading is `PL-CW14` again.
STALE_THREADS_NAMED = 5
STALE_HEADING_CHARS = 60


def _clipped(title: str, limit: int = STALE_HEADING_CHARS) -> str:
    """The heading, cut at a word boundary where it runs past the limit."""
    if len(title) <= limit:
        return title
    cut = title[:limit].rsplit(" ", 1)[0]
    return f"{cut or title[:limit]}..."


def _check_stale_open_threads(
    report: Report, threads: tuple[Thread, ...] | None, config: Config
) -> None:
    """Name a notes-file thread the file itself calls open, whose items have all closed.

    Two clauses, and the advisory needs both. The heading's own leading word
    has to say the thread is open, and every `PL-` id the section cites -
    heading and body alike - has to resolve to an item that is `done` or
    `dropped`. Measured on this repository 2026-09-21, the second clause alone
    named 16 of 26 sections, most of them correct content that other rules
    cite; both clauses named 4, of which 3 were already filed one at a time as
    separate items. That ratio is the whole argument for the pair.

    **A section citing no id is never named.** Direction with no item is one of
    the three things a notes file is for, and a check that fires on it is
    firing on the file working as intended.

    **An advisory, and it can never be an error.** The fourth section the pair
    names on this repository - "what makes desflurane wash out too fast" - has
    all three of its items closed and is genuinely still open, because what is
    left is a published value nothing here can settle. That false fire is
    permanent rather than tunable, which is what keeps this out of
    `make check`'s failure path and out of a close-out check: a permanent false
    fire at every close-out trains a reader to skim the block a real advisory
    shares.

    **It stays silent where it cannot answer.** An id resolving to no item at
    all leaves the thread unnamed: an unreadable citation is not evidence that
    a thread is spent, and claiming otherwise would be the apparatus handing
    over a partial reading as a complete one.
    """
    if not threads:
        return
    status = {item.identifier: item.status for item in report.items}
    stale = [
        thread
        for thread in threads
        if thread.declares_open
        and thread.cites
        and all(status.get(cited) in CLOSED_STATUSES for cited in thread.cites)
    ]
    if not stale:
        return
    # Joined on `;` rather than `,` because these headings carry commas of
    # their own, and the line number goes beside each one: that is what the
    # reader navigates by, and the heading is there to be recognized.
    shown = "; ".join(f'"{_clipped(t.title)}" (line {t.line})' for t in stale[:STALE_THREADS_NAMED])
    rest = len(stale) - STALE_THREADS_NAMED
    if rest > 0:
        shown = f"{shown}; and {rest} more"
    where = config.notes_file or "the notes file"
    report.advisories.append(
        f"{where}: {len(stale)} thread(s) the heading calls open, whose every cited item has "
        f"closed - {shown}; delete what is finished, once its outcome is recorded somewhere "
        "that maintains itself, and re-head what outlived its items"
    )


#: How many dated assertions the staleness advisory names, and how much of
#: each line it prints. Five for `STALE_THREADS_NAMED`'s reason - one line a
#: reader takes in - and the cap is also what keeps the advisory actionable
#: however large the instruction set grows: the count in the message says how
#: many there are, and these are the ones to start on.
STALE_ASSERTIONS_NAMED = 5
STALE_ASSERTION_CHARS = 70


def _check_stale_instructions(
    report: Report, assertions: tuple[Assertion, ...] | None, config: Config, today: date
) -> None:
    """Name the dated assertions in the instruction set that are due for re-checking.

    The instruction set asserts facts about a world that changes and nothing
    expires any of them. `PL-BSYZ` stated an egress refusal measured on one
    day as a standing fact, so it would have gone on telling sessions not to
    retry `doi.org` the moment the policy opened; `PL-GDB0` records three
    current-state facts written as permanent rules in a single session. Both
    were caught by the project owner rather than by any gate, and
    `.claude/rules/expert-review.md` says why no gate will catch the judgment
    half: "It fails quietly. A wrongly permanent sentence trips no check and
    never can, because altitude is judgment rather than a fact about the
    tree."

    **So only the decidable half is here.** Which assertions are due is
    arithmetic on dates; whether an aged one is still true is left to the
    reader, per `CLAUDE.md` § "Prefer deterministic tooling" - do not script
    the judgment.

    **An advisory, on a grooming pass, and never an error.** A reader met here
    already has hygiene in hand and the files open. On `make check`, which is
    edit-triggered, this would fire on every run of a session that is nowhere
    near an instruction file, which is the defect `CLAUDE.md` retires a check
    for.

    **It can reach zero, which is the constraint that shaped it.** A raw age
    list cannot, since every assertion ages and the report would name more of
    them every day - and the cost of an advisory that cannot reach zero is not
    the entries it names but the next advisory, which gets read the same way.
    The threshold is what bounds the set; re-verifying a line and writing
    today onto it is what empties it. `instructions.py` reads the *newest*
    date on a line for exactly that reason, so "(project owner, 2026-08-31;
    re-verified 2026-12-05)" discharges a record without falsifying the record.

    **Known limitation, recorded so it is not rediscovered as a defect.** Age
    is a proxy for staleness, not staleness. A dated record does not go stale;
    a measured environmental fact does, and this cannot tell them apart. Early
    precision will be mediocre, and the right narrowing is to be learned from
    the first firing rather than guessed now. Neither `PL-BSYZ` nor `PL-GDB0`
    would have been caught here - both were filed within days. This targets
    the assertion that quietly goes wrong at month eighteen, not the fast
    failure somebody notices.

    **It stays silent where it cannot answer.** A project naming no
    instruction paths, or a caller supplying none, leaves the audit unraised
    rather than computed against an empty parse.
    """
    if not assertions:
        return
    stale = sorted(
        (row for row in assertions if row.age(today) > config.instruction_stale_days),
        key=lambda row: (row.when, row.file, row.line),
    )
    if not stale:
        return
    # Oldest first, which is the order they are worth reading in: the one
    # least recently confirmed is the one likeliest to have gone wrong, and
    # the cap below takes the head of this list rather than a sample of it.
    shown = "; ".join(
        f"{row.file}:{row.line} ({row.when.isoformat()}, {row.age(today)} days) "
        f'"{_clipped(row.text, STALE_ASSERTION_CHARS)}"'
        for row in stale[:STALE_ASSERTIONS_NAMED]
    )
    rest = len(stale) - STALE_ASSERTIONS_NAMED
    if rest > 0:
        shown = f"{shown}; and {rest} more"
    report.advisories.append(
        f"{len(stale)} dated assertion(s) in the instruction set have gone "
        f"{config.instruction_stale_days} days without being re-checked, oldest first - "
        f"{shown}; read each against the world it describes and write today's date onto the "
        "line. A measured fact is re-measured and re-dated; a record of what was decided "
        "keeps its own date and gains a re-verification one, so neither has to be falsified "
        "to clear it. Where the claim has stopped being true, the edit is the point of the "
        "advisory - age is only the proxy, and whether the sentence still holds is yours"
    )


def _groom(
    report: Report,
    today: date,
    config: Config,
    offered: frozenset[str] | None,
    milestones: MilestoneStates | None = None,
    threads: tuple[Thread, ...] | None = None,
    assertions: tuple[Assertion, ...] | None = None,
) -> None:
    """Detect the conditions that make a grooming pass worth someone's time."""
    # Grooming rather than close-out, and that placement is the decision
    # (`PL-DG84`, ratified 2026-09-21): this fires on a pass that is already
    # about hygiene, where a reader has the file open and the judgment in
    # hand, instead of on every close-out, where one permanent false fire
    # costs the whole advisory block its reader.
    _check_stale_open_threads(report, threads, config)
    _check_stale_instructions(report, assertions, config, today)
    stale = [
        item
        for item in report.untriaged
        if item.added is not None and (today - item.added).days > config.untriaged_stale_days
    ]
    if stale:
        report.advisories.append(
            f"{len(stale)} untriaged item(s) captured more than {config.untriaged_stale_days} days "
            f"ago ({', '.join(i.identifier for i in stale)}); triage or drop them"
        )

    # Only worth saying where the rule is in force: a project that has not
    # adopted it is not carrying a backlog against it.
    #
    # Reported against what is about to be offered, not against the whole
    # backlog. Naming all of it fired on every run and could be discharged by
    # nothing short of a campaign, so it was an advisory that could not reach
    # zero - and the cost of one of those is not the items it names but the
    # next advisory, which gets read the same way. `docket check`'s advisories
    # are the only channel grooming has.
    #
    # Narrowing it here rather than burning the backlog down also puts the
    # command where it can be run before it is written. Every command this
    # store has ever carried that was written away from the work was wrong, so
    # a command invented for an item nobody has started is not a gap closed
    # but a false claim opened. The moment an item is offered is the first
    # moment there is something to run.
    unspecified = [
        item
        for item in report.open_items
        if config.verify_required_from is not None
        and item.status == "ready"
        and not item.verify
        and not item.not_delegable
        and not _verify_required(item, config)
    ]
    due = [item for item in unspecified if item.identifier in (offered or frozenset())]
    if due:
        one = len(due) == 1
        report.advisories.append(
            f"{', '.join(item.identifier for item in due)} "
            f"{'is' if one else 'are'} next to be offered and {'names' if one else 'name'} "
            f"no `verify:` command ({len(due)} of {len(unspecified)} ready item(s) predating "
            f"the requirement, {config.verify_required_from}); give the command when you "
            "start it, having run it first"
        )

    # The same shape for `payoff:`, and a separate advisory rather than a
    # clause on the one above: the two ask for different things from whoever
    # reads them - a command that has been run, and a sentence about
    # consequence - and an item can owe either without owing both.
    #
    # Narrowed to what is about to be offered for the reason the `verify:`
    # advisory is: naming the whole grandfathered backlog is an advisory that
    # cannot reach zero without a campaign, and the cost of one of those is
    # not the items it names but the next advisory, which gets read the same
    # way. The moment an item is offered is also when the sentence is worth
    # most, since that is the moment somebody is being asked to weigh it.
    unstated = [
        item
        for item in report.open_items
        if config.payoff_required_from is not None
        and item.status == "ready"
        and not item.payoff
        and not _payoff_required(item, config)
    ]
    owing = [item for item in unstated if item.identifier in (offered or frozenset())]
    if owing:
        one = len(owing) == 1
        report.advisories.append(
            f"{', '.join(item.identifier for item in owing)} "
            f"{'is' if one else 'are'} next to be offered and {'names' if one else 'name'} "
            f"no `payoff:` ({len(owing)} of {len(unstated)} ready item(s) predating the "
            f"requirement, {config.payoff_required_from}); write the line as you start it - "
            "one plain-language sentence of what closing it buys"
        )

    # The other half of a `needs-decision` item, and the half that does not
    # survive on its own. The question is written into the store; the
    # recommendation that would let the owner answer it in one read is written
    # into the reply that posed it, and a reply dies with its session while the
    # item persists. So the longer an item waits the likelier the
    # recommendation is gone when the answer arrives, which is backwards -
    # waiting is what the status is for. `PL-KQHN`'s answer had to be
    # reconstructed from a harness-written summary line naming two options and
    # marking neither, and a decision of record about the release train rested
    # on a reading of another model's compressed prose.
    #
    # Two populations, because they reach different sessions and only the
    # first is prevention. Captured on or after the cutover means a session is
    # writing the item now, and the advisory reaches it while it still holds
    # the reasoning. Predating the cutover, it is reached only as it is about
    # to be offered - the `verify:` and `payoff:` narrowing, taken for the
    # reason those two take it: 37 of the 45 open `needs-decision` items
    # marked nothing on 2026-09-20, and naming all of them would be an
    # advisory that cannot reach zero without a campaign, whose cost is not
    # the items it names but the next advisory, which gets read the same way.
    #
    # An advisory and never an error. A brief may honestly decline to
    # recommend - `PL-PFK1` declines because the deciding number cannot be
    # measured retroactively - and a check that refuses correct content is the
    # defect `CLAUDE.md` retires a check for.
    unmarked = [
        item
        for item in report.open_items
        if config.recommendation_required_from is not None
        and item.status == "needs-decision"
        and not _marks_recommendation(item.body)
    ]
    reached = [
        item
        for item in unmarked
        if _recommendation_required(item, config) or item.identifier in (offered or frozenset())
    ]
    if reached:
        one = len(reached) == 1
        report.advisories.append(
            f"{', '.join(item.identifier for item in reached)} "
            f"{'is at' if one else 'are at'} `needs-decision` and "
            f"{'marks' if one else 'mark'} no recommendation "
            f"({len(reached)} of {len(unmarked)} such item(s)); write the one you would "
            "give into the brief, not only into the reply - the question outlives the "
            "session that posed it and the reasoning behind an answer does not. Where a "
            "recommendation is already in the prose, mark it so it can be found; where "
            "none is owed, say that and why"
        )

    # The item-blocker half is `plan.promotable`, which `docket next` also
    # reads so that it can name these ids at the moment a session is choosing.
    # Derived once and shared rather than computed twice: an advisory saying an
    # item may now be started, beside a ranking that disagrees, is the silent
    # wrong answer `.claude/rules/apparatus-standard.md` makes the floor
    # (`PL-6T44`). Membership is tested inside the existing walk so the
    # advisories still appear in store order.
    ready_now = {item.identifier for item in promotable(report.items)}
    resolved = {i.identifier for i in report.items if i.status in ("done", "dropped")}
    for item in report.items:
        if item.identifier in ready_now:
            report.advisories.append(
                f"{item.identifier}: every blocker has closed; it is ready to promote"
            )
            continue
        versions = item.blocking_milestones
        if item.status != "blocked" or not versions:
            continue
        if not set(item.blocking_items) <= resolved:
            continue
        # A milestone blocker needs the roadmap to answer, and an unreadable
        # one declines: this advisory says an item may now be started, and
        # saying that on evidence nobody read is the way it does harm.
        if milestones is None:
            continue
        if not all(milestones.is_cleared(version) for version in versions):
            continue
        # Scoped is not the same as shipped, and for one shape of item the
        # difference is the whole answer. An item the milestone's own
        # `Required scope` names ships *with* it: scoping cleared the blocker
        # and could never have unblocked the item, because what it waits for
        # is the milestone landing. Advising that such an item is ready to
        # promote is the opposite of the truth, and it is advice that repeats
        # on every run until the milestone ships - which is exactly what
        # `CLAUDE.md`'s "a check earns its place every run" refuses.
        #
        # Narrow deliberately. A scoped, unshipped milestone that does *not*
        # name the item leaves the original advisory correct: that item was
        # waiting on the scoping round, and the scoping round has happened.
        # Read from the roadmap rather than from a new field, because the
        # roadmap already says it (`PL-L09X`).
        if any(milestones.ships_with(version, item.identifier) for version in versions):
            continue
        # Said separately because the word is different, and the difference is
        # the point. An item blocker *closes*; a milestone blocker clears when
        # the milestone is scoped, which is the decision the item was waiting
        # on rather than the release it will ship in.
        one = len(versions) == 1
        report.advisories.append(
            f"{item.identifier}: {', '.join(versions)} "
            f"{'is' if one else 'are'} scoped and every other blocker has closed; "
            "it is ready to promote"
        )

    top = _top_band(report)
    if not top:
        return
    band = top[0].priority
    # Blocked items sit in the band and cannot answer "what next": a session
    # cannot start one, and the limit is about how many choices it must weigh at
    # a glance. Counting them also made the advisory reachable without anyone
    # over-prioritizing, because `_check_blocked_band` requires a blocker to sit
    # at or above the band of what it blocks - so gating one safety item on a
    # feature item raises that feature item into the band, and the count grows
    # by an item no class pinned there and nobody can act on (`PL-P23D`).
    startable = [item for item in top if item.status != "blocked"]
    if len(startable) > config.top_band_limit:
        held = len(top) - len(startable)
        note = f", and {held} more blocked and not counted" if held else ""
        # Split the band by what may actually be moved. The same checker
        # refuses to seat a `safety`- or `science`-classed item below the top
        # band, so "demote what is not genuinely next" prescribes an action
        # `docket check` would then reject as an error - and on this store
        # that was twelve of the thirteen items making the band overfull
        # (`PL-CW14`). Reporting the split is not the same as exempting the
        # pinned items from the count: `docket.toml`'s `top_band_limit`
        # comment considered that and rejected it, because a band that grows
        # to twenty safety items is a real problem a session should be told
        # about. The count stands; only the remedy is narrowed to what is
        # available.
        pinned = [i for i in startable if set(i.classes) & set(config.safety_classes)]
        demotable = len(startable) - len(pinned)
        if demotable:
            one = demotable == 1
            remedy = (
                f"{len(pinned)} are pinned there by a {' or '.join(config.safety_classes)} "
                f"class, {demotable} {'is' if one else 'are'} demotable; demote what is not "
                "genuinely next"
            )
        else:
            # Nothing is demotable, so say what the number means instead of
            # prescribing an action nobody can take. A band that is entirely
            # class-pinned is large because that much safety work is open,
            # which is the debt gate's own signal and reads as one.
            remedy = (
                f"all {len(startable)} are pinned there by a "
                f"{' or '.join(config.safety_classes)} class, so the band is large because "
                "that much safety-critical work is open rather than because anything is "
                "over-prioritized"
            )
        report.advisories.append(
            f"{band}: {len(startable)} startable items{note}, past the "
            f"{config.top_band_limit} a session can choose between at a glance; {remedy}"
        )
    undecided = [i for i in top if i.status == "needs-decision"]
    if len(undecided) > len(top) - len(undecided):
        report.advisories.append(
            f"{band}: {len(undecided)} of {len(top)} items are needs-decision; "
            "schedule the decisions, they are the work"
        )
    process = [i for i in top if i.classes and all(c in config.process_classes for c in i.classes)]
    if process and len(process) > len(top) - len(process):
        report.advisories.append(
            f"{band}: process work ({', '.join(i.identifier for i in process)}) outnumbers "
            "the product work beside it; demote it, the product's correctness ranks above "
            "the workflow that builds it"
        )


def _top_band(report: Report) -> list[Item]:
    """The highest-priority band that has anything in it."""
    for priority in PRIORITIES:
        band = [item for item in report.open_items if item.priority == priority]
        if band:
            return band
    return []


def _check_lost(report: Report, lost: LostReport | None) -> None:
    """An item file the history holds and the tree does not.

    An error rather than an advisory, and the only git-derived check here that
    is one. Everything else this module asks git about is provenance - a
    recorded number, a stale mark - where being wrong costs a lookup. This is
    the capture rule itself: `CLAUDE.md` guarantees that a finding raised in a
    session is not lost, and a merge resolution that removes an item file
    breaks that guarantee silently, in the one place nobody reviews. `PL-P0QT`
    records the instance that prompted it.

    A loss found in a truncated clone is still a loss, so the items are always
    reported. Only a *clean* answer from one is qualified: there the check saw
    part of the history and cannot claim the rest.
    """
    if lost is None:
        return
    if lost.declined:
        report.declined.append(f"items a merge removed: {lost.declined}")
        return
    for item in lost.items:
        report.errors.append(
            f"{item.path}: {item.identifier} is in {lost.ref}'s history and absent from its "
            f"tree, with no `dropped` record left behind - no commit deletes it, so a merge "
            f"resolution did. Recover it with `git cat-file -p {item.blob}`"
        )
    if lost.truncated and not lost.items:
        report.declined.append(
            "items a merge removed: this clone's history is truncated, so the walk read only "
            "the commits it holds"
        )


def _check_shared_verify(report: Report) -> None:
    """One `verify:` command recorded against two or more open items.

    A command proves an item done by failing until that item's work exists. Two
    open items recording the same command cannot both be in that relation to it:
    whichever is worked first makes it pass, and from then on the command
    accepts a branch that did none of the other's work. So this is the
    non-discriminating reading of a passing command arrived at *with certainty*,
    and it is reached by counting the store rather than by running anything.

    It used to be reached only by running something. `already_passing` computed
    the same count, but over the subset that had just passed, so the finding
    needed the replay to produce it - which was CI only then, since `make check`
    ran `docket check` bare. Three items triaged with one command on 2026-09-20
    passed every local gate and turned CI red after review had started, and the
    two sentences CI printed that day are the two rules that now run here
    (`PL-J3WK`, `PL-4W2L`).

    Exact string equality, and deliberately no normalization. Collapsing runs of
    whitespace would be right for the words of a shell line and wrong inside a
    quoted argument, where `grep -q 'a  b'` and `grep -q 'a b'` read different
    files - so a rule that normalized would report two different commands as one
    and do it as a hard failure. Exactness costs the case nobody writes and
    keeps the rule decidable.

    Items whose command cannot fail at all are left out: `_check_item` has
    already told each of them to write a command that discriminates, and the
    sharing is a consequence of the placeholder rather than a second defect.
    The subtraction is the one `_check_landed` makes between its own findings,
    applied across two checks.
    """
    commands: dict[str, list[str]] = {}
    for item in report.items:
        if item.status in OPEN_STATUSES and item.verify and not never_fails(item.verify):
            commands.setdefault(item.verify, []).append(item.identifier)
    for command, identifiers in commands.items():
        if len(identifiers) > 1:
            report.errors.append(
                f"{', '.join(sorted(identifiers))} are open and record the same "
                f"`verify:` command, `{command}` - whichever is worked first makes it "
                "pass, so it cannot prove any one of them done and `docket verify` "
                "would ACCEPT a branch that did none of the others' work. Give each "
                "one a command naming something only its own work creates"
            )


def _normalized_feature(name: str) -> str:
    """A feature name with the differences that are never meaningful removed."""
    return name.strip().lower().replace("_", "-").replace(" ", "-")


def _check_feature_spellings(report: Report) -> None:
    """Two spellings of one feature name, which split the group `next` ranks by.

    `docket next` prefers work in a feature already underway, nearest-finishing
    first, so a group split in two makes that ranking wrong in a way that reads
    as a correct answer: the half nobody can see counts as unstarted work.

    Only mechanical variants are decided here - case, and `_` or a space where
    `-` was meant. Whether `docket` and `dev-tooling` are the same group is the
    judgment half and is left alone; a tool guessing at that would merge two
    features somebody meant to keep apart. `PL-MVC2` carries the reasoning and
    the measurement.
    """
    spellings: dict[str, set[str]] = {}
    for item in report.items:
        if item.feature:
            spellings.setdefault(_normalized_feature(item.feature), set()).add(item.feature)
    for variants in spellings.values():
        if len(variants) > 1:
            names = ", ".join(sorted(variants))
            report.errors.append(
                f"feature '{names}' is spelled {len(variants)} ways that differ only in case "
                "or separator; `docket next` groups on the literal string, so this is one "
                "feature the ranking sees as several - settle on one spelling"
            )


def analyze(
    items: list[Item],
    today: date,
    config: Config | None = None,
    history: PullRequestHistory | None = None,
    offered: OfferedReport | None = None,
    landed: LandedReport | None = None,
    closures: ClosureReport | None = None,
    records: RecordReport | None = None,
    lost: LostReport | None = None,
    version: str | None = None,
    milestones: MilestoneStates | None = None,
    notes: dict[str, frozenset[str]] | None = None,
    window: CutWindow | None = None,
    unreferenced: dict[str, tuple[str, ...]] | None = None,
    threads: tuple[Thread, ...] | None = None,
    assertions: tuple[Assertion, ...] | None = None,
    settings_source: SettingsSource | None = None,
) -> Report:
    """Validate and groom in one pass.

    `history`, `offered`, `landed`, `closures` and `records` are the inputs that
    cannot be read from the store, so they are passed in rather than fetched
    here: this module stays pure and testable, and the caller decides whether
    asking git, ranking the queue or running the items' own commands is worth
    it. Omitting any of them skips the check that needs it rather than failing
    it.

    `offered` is the ids `next` would suggest. It is supplied by the three
    commands that put advisories in front of a person - `check`, `digest` and
    `next` - and by nothing else, so no command reports a count another
    command would contradict. Like the other three it can decline: the ranking
    reads what is in flight, and a checkout that could not walk every ref has
    settled which items come next only as far as the refs it could read.

    `milestones` is the roadmap's answer to the two questions a `blocked-by:
    vX.Y.Z` asks - whether that milestone exists, and whether it has been
    scoped. Omitting it leaves both halves unjudged rather than guessed, which
    is what a bare checkout with no roadmap gets.

    `notes` is what each cut release's notes file says it shipped, which is
    the other half of a record the store holds one half of. Like the rest, a
    caller that does not supply it leaves the comparison unmade.

    `window` is what the default branch took while a release cut on this
    checkout sat unmerged - the seam between the notes, which are written at
    the cut, and the tag, which goes on the merge.

    `unreferenced` is which released bullets say where nothing landed. It is
    read from the same files as `notes` and passed separately rather than
    folded into it, because the two answer different questions about them and
    a caller that wants one does not always want the other.

    `threads` is the project's running cross-session log split at its `##`
    headings - `notes_file`, not the release notes `notes` carries. Passed in
    for the reason the rest are: this module reads no filesystem. A caller
    that does not supply it, or a project that configures no notes file,
    leaves the stale-thread advisory unraised rather than guessed at.

    `assertions` is the dated lines of the project's instruction set, read
    from `instruction_paths`. Passed in for the reason the rest are: this
    module reads no filesystem. A caller that does not supply it, or a project
    that names no instruction paths, leaves the staleness advisory unraised
    rather than reporting that nothing has aged.

    `settings_source` is which `docket.toml` the caller resolved `config` from,
    and whether it was there. It is the one input that says nothing about the
    store and everything about the reading of it, which is why it cannot be
    derived here: `config` arrives already applied, and a `Config` holding
    library defaults is indistinguishable from a project that wrote those
    values down. A caller that does not supply it leaves the reading unnamed.
    """
    settings = config or Config()
    ids = offered.ids if offered is not None else None
    report = Report(items=list(items))
    for item in report.items:
        _check_item(item, report, settings)
    _check_references(report, milestones)
    _check_generator_defects(report, settings)
    _check_feature_spellings(report)
    _check_shared_verify(report)
    _check_touched_items(report, settings)
    _check_filenames(report, settings)
    _check_milestones(report, version)
    _check_release_notes(report, notes, version)
    _check_notes_references(report, unreferenced)
    _check_cut_window(report, window, notes)
    _check_provenance(report, history)
    _check_landed(report, landed)
    _check_selects_nothing(report, landed, ids)
    _note_settings(report, settings_source)
    _note_cost(report, landed)
    _check_closures(report, closures)
    _check_records(report, records)
    _check_lost(report, lost)
    _groom(report, today, settings, ids, milestones, threads, assertions)
    # Said once, for both advisories above that read `offered`, and said even
    # where neither fired: an unread ref might carry the item that would have
    # been named, so silence there is the same partial answer as a wrong name.
    if offered is not None and offered.declined:
        report.declined.append(
            f"whether the grooming advisories name the items `next` will really "
            f"offer: {offered.declined}"
        )
    if milestones is None:
        waiting = sorted(item.identifier for item in report.items if item.blocking_milestones)
        if waiting:
            report.declined.append(
                f"whether the milestones {', '.join(waiting)} wait on exist and have "
                "been scoped: no roadmap was read"
            )
    return report
