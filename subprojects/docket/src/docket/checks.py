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
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

from .config import Config
from .model import EFFORTS, OPEN_STATUSES, PRIORITIES, STATUSES, Item
from .plan import OfferedReport
from .release import SEMVER_RE, version_key
from .store import ID_RE
from .vcs import ClosureReport, LostReport, PullRequestHistory
from .verify import LandedReport

REQUIRED_BRIEF = ("**Problem.**", "**Why it matters.**")
DONE_WHEN = "**Done when.**"

# A heading, as the item format writes one: `**` at the start of a line. Used
# to find where one section stops rather than to validate the heading itself,
# so bold text inside a paragraph does not end a section and a bold-opened
# paragraph does.
BRIEF_HEADING = re.compile(r"^\*\*", re.MULTILINE)


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


def brief_gaps(body: str, *, blocked: bool = False) -> tuple[list[str], list[str]]:
    """The required sections a brief lacks, as absent ones and empty ones.

    One author for the rule, because two had already drifted: `check` errored
    on the sections an item was missing while `triage` printed its own reading
    of the same three markers, and the README promises a reader those two
    cannot disagree. A blocked item is not asked for `**Done when.**` - it
    cannot state its closing condition until its blocker resolves.
    """
    required = list(REQUIRED_BRIEF) + ([] if blocked else [DONE_WHEN])
    found = {marker: _section_text(body, marker) for marker in required}
    return (
        [marker for marker, text in found.items() if text is None],
        [marker for marker, text in found.items() if text == ""],
    )


# A pull request number, as GitHub allocates them: a bare positive integer.
# Written without the `#` so that the field holds the number and nothing else,
# and so a typo like `pr: #71 (docket)` is refused rather than half-parsed.
PR_RE = re.compile(r"^[1-9][0-9]*$")


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
        return

    if item.status in OPEN_STATUSES:
        if item.priority not in PRIORITIES:
            report.errors.append(f"{where}: no priority; expected one of {', '.join(PRIORITIES)}")
        if item.effort not in EFFORTS:
            report.errors.append(f"{where}: no effort; expected one of {', '.join(EFFORTS)}")
        missing, empty = brief_gaps(item.body, blocked=item.status == "blocked")
        if missing:
            report.errors.append(f"{where}: brief is missing {', '.join(missing)}")
        if empty:
            report.errors.append(
                f"{where}: brief has nothing under {', '.join(empty)}; the heading "
                "is there and the section is not, which is what the brief exists "
                "to prevent"
            )

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
        report.errors.append(f"{where}: marked blocked but names no blocking item")
    if item.status == "needs-decision" and "**Decision needed.**" not in item.body:
        report.errors.append(
            f"{where}: marked needs-decision but states no decision to make; add a "
            "**Decision needed.** line so a later session can answer it"
        )
    if item.verify and "\n" in item.verify:
        report.errors.append(f"{where}: `verify` must be a single-line command")
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
    its work exists. A command shared with another open item is the second
    with certainty, so it is named separately - closing anything on that
    evidence would be acting on a command that proves nothing.

    A command that could not answer at all - killed at the limit, or not found
    by the shell - is reported under "not checked" rather than as an advisory,
    because there is no finding to report: the run looked and was stopped. The
    distinction is the same one `landed.declined` draws for a whole run, made
    per item, and it is what keeps `considered` honest. `PL-T940` carries the
    case that made it necessary: without a status of its own a killed command
    returned 1, which is what a failing test returns, so the item vanished
    from every finding while the report stayed clean.
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

    if not landed.passing:
        return
    one = len(landed.passing) == 1
    message = (
        f"{', '.join(landed.passing)} {'is' if one else 'are'} open but "
        f"{'its' if one else 'their'} `verify:` command already passes "
        f"({len(landed.passing)} of {landed.considered} checked): either the work landed "
        "and the item was never closed, or the command does not discriminate and "
        "proves nothing"
    )
    if landed.shared:
        message += (
            f". {', '.join(landed.shared)} share a command with another open item, "
            "which cannot prove any one of them done - give each its own"
        )
    report.advisories.append(message)


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
    only returns 5 for the one reason. What the finding does not settle is
    which repair it wants, and that is why it stays an advisory: a selector
    naming a test the work has yet to write is the recommended shape here and
    is behaving as intended, while one naming a test that will never exist is
    a specification that can never be met. Only the item's author can say
    which, so the sentence asks rather than tells.

    Reported against what is about to be offered rather than against the whole
    backlog, for the reason `_groom` states in the same words a few functions
    below: the recommended shape here is `-k` naming the test the work will
    add, so every unstarted item using it selects nothing until its work
    lands, and naming all of them fired on every run against eighteen of
    thirty-one open items. That is the advisory that cannot reach zero, and
    its cost is not the items it names but the next advisory, which gets read
    the same way.

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
        "that way after the work too - check that the name each selector matches is one "
        "the work will create, and replace the selectors where it is not"
    )


def _check_slow_commands(report: Report, landed: LandedReport | None) -> None:
    """Say when one item's `verify:` command is what this check spends its time on.

    The other findings here are about whether a command *proves* anything. This
    one is about what it costs, and it exists because nothing else says. Since
    the commands began running concurrently the wall clock is set by the
    slowest single member rather than by how many there are (`PL-LXR3`), so one
    heavy command is worth more attention than twenty light ones - and the
    figure moves in one step, on the day somebody writes it. Measured on this
    store: 10.1 s with none, 59.1 s with one full-suite `pytest --cov`, 62.6 s
    with two.

    That cost is then paid by every `make check` in every later session, while
    the only person placed to reconsider the command is the one who wrote it,
    in the session that wrote it. This is the sentence that reaches them.

    An advisory rather than an error, because the answer is a judgment: some
    commands are worth their cost and a coverage item's genuinely cannot be
    narrowed - coverage of a module is the union of everything that exercises
    it, so it is a full-suite run by necessity (`PL-5TN8`). Accepting a known
    cost is a valid outcome; not knowing it is what this removes.

    It names every command over the line rather than only the worst, because
    two heavy commands overlap in the pool and narrowing one of them changes
    nothing - the floor is wherever the second one is.

    Reported against the whole run rather than scoped to what `next` will
    offer, unlike `_check_selects_nothing`. The reasoning there was that its
    finding held for eighteen of thirty-one open items and so could never reach
    zero; this one held for none of forty-six on a healthy store, and the
    threshold is set against that measurement to keep it that way. An advisory
    that fires only when something arrived is one that still gets read.
    """
    if landed is None or not landed.known or not landed.slow:
        return
    one = len(landed.slow) == 1
    named = ", ".join(f"{command.identifier} ({command.seconds:.0f}s)" for command in landed.slow)
    report.advisories.append(
        f"{named} {'is' if one else 'are'} what this check waits for: "
        f"{'that command' if one else 'those commands'} against a {landed.typical:.1f}s "
        f"median and {landed.elapsed:.0f}s for the whole run. A pool cannot finish before "
        f"its slowest member, so {'this' if one else 'each of these'} sets the floor for "
        "every `make check` until the item closes - narrow the command if it can be "
        "narrowed, or accept the cost knowing what it is"
    )


def _check_references(report: Report) -> None:
    """Hold every cross-reference to an item that exists."""
    known = {item.identifier for item in report.items if item.identifier}
    for item in report.items:
        for blocker in item.blocked_by:
            if blocker == item.identifier:
                report.errors.append(f"{_where(item)}: lists itself as a blocker")
            elif blocker not in known:
                report.errors.append(f"{_where(item)}: blocked by {blocker}, which is not an item")

    _outranks_its_blocker(report, known_items={i.identifier: i for i in report.items})

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
        for identifier in item.blocked_by:
            blocker = known_items.get(identifier)
            if blocker is None or not blocker.is_open or blocker.priority not in PRIORITIES:
                continue
            if PRIORITIES.index(item.priority) < PRIORITIES.index(blocker.priority):
                report.errors.append(
                    f"{_where(item)}: is {item.priority} but waits on {identifier} at "
                    f"{blocker.priority}; raise {identifier} to {item.priority} or above, "
                    "because nothing here can start before it does"
                )


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
                f"but #{number} is recoverable from its merge commit; "
                f"write `pr: {number}` into the item so the file carries it too"
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


def _groom(report: Report, today: date, config: Config, offered: frozenset[str] | None) -> None:
    """Detect the conditions that make a grooming pass worth someone's time."""
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

    resolved = {i.identifier for i in report.items if i.status in ("done", "dropped")}
    for item in report.items:
        if item.status == "blocked" and item.blocked_by and set(item.blocked_by) <= resolved:
            report.advisories.append(
                f"{item.identifier}: every blocker has closed; it is ready to promote"
            )

    top = _top_band(report)
    if not top:
        return
    band = top[0].priority
    if len(top) > config.top_band_limit:
        report.advisories.append(
            f"{band}: {len(top)} items, past the {config.top_band_limit} a session can choose "
            "between at a glance; demote what is not genuinely next"
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
    lost: LostReport | None = None,
    version: str | None = None,
) -> Report:
    """Validate and groom in one pass.

    `history`, `offered`, `landed` and `closures` are the inputs that cannot be
    read from the store, so they are passed in rather than fetched here: this
    module stays pure and testable, and the caller decides whether asking git,
    ranking the queue or running the items' own commands is worth it. Omitting
    any of them skips the check that needs it rather than failing it.

    `offered` is the ids `next` would suggest. It is supplied by the three
    commands that put advisories in front of a person - `check`, `digest` and
    `next` - and by nothing else, so no command reports a count another
    command would contradict. Like the other three it can decline: the ranking
    reads what is in flight, and a checkout that could not walk every ref has
    settled which items come next only as far as the refs it could read.
    """
    settings = config or Config()
    ids = offered.ids if offered is not None else None
    report = Report(items=list(items))
    for item in report.items:
        _check_item(item, report, settings)
    _check_references(report)
    _check_feature_spellings(report)
    _check_milestones(report, version)
    _check_provenance(report, history)
    _check_landed(report, landed)
    _check_selects_nothing(report, landed, ids)
    _check_slow_commands(report, landed)
    _check_closures(report, closures)
    _check_lost(report, lost)
    _groom(report, today, settings, ids)
    # Said once, for both advisories above that read `offered`, and said even
    # where neither fired: an unread ref might carry the item that would have
    # been named, so silence there is the same partial answer as a wrong name.
    if offered is not None and offered.declined:
        report.declined.append(
            f"whether the grooming advisories name the items `next` will really "
            f"offer: {offered.declined}"
        )
    return report
