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
from .store import ID_RE
from .vcs import PullRequestHistory

REQUIRED_BRIEF = ("**Problem.**", "**Why it matters.**")

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
    if not item.status:
        report.errors.append(f"{where}: no `status`; expected one of {', '.join(STATUSES)}")
        return
    if item.status not in STATUSES:
        report.errors.append(f"{where}: status '{item.status}' is not one of {', '.join(STATUSES)}")
        return
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
        missing = [marker for marker in REQUIRED_BRIEF if marker not in item.body]
        if item.status != "blocked" and "**Done when.**" not in item.body:
            missing.append("**Done when.**")
        if missing:
            report.errors.append(f"{where}: brief is missing {', '.join(missing)}")

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

    safety = tuple(c for c in item.classes if c in config.safety_classes)
    if safety and item.priority in ("P2", "P3"):
        report.errors.append(
            f"{where}: class '{', '.join(safety)}' sits at {item.priority}; "
            "safety-critical work starts at P0 or P1"
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
    # `pr` rather than `commit`, because the pull request number is the half of
    # an item's provenance that survives however the work reaches the default
    # branch. `commit` stays legal and is still checked for shape where it
    # appears; it is simply no longer what makes a closure traceable.
    if item.status == "done" and not item.pr:
        report.errors.append(
            f"{where}: marked done but records no `pr`; without it there is no way "
            "back from the closure to the work that made it"
        )
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


def _check_references(report: Report) -> None:
    """Hold every cross-reference to an item that exists."""
    known = {item.identifier for item in report.items if item.identifier}
    for item in report.items:
        for blocker in item.blocked_by:
            if blocker == item.identifier:
                report.errors.append(f"{_where(item)}: lists itself as a blocker")
            elif blocker not in known:
                report.errors.append(f"{_where(item)}: blocked by {blocker}, which is not an item")

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


def _groom(report: Report, today: date, config: Config) -> None:
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
    unspecified = [
        item
        for item in report.open_items
        if config.verify_required_from is not None
        and item.status == "ready"
        and not item.verify
        and not item.not_delegable
        and not _verify_required(item, config)
    ]
    if unspecified:
        report.advisories.append(
            f"{len(unspecified)} ready item(s) predate the `verify:` requirement "
            f"({config.verify_required_from}) and name no command that would prove them "
            "done; each one is work no reviewer can accept without reading the diff"
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


def analyze(
    items: list[Item],
    today: date,
    config: Config | None = None,
    history: PullRequestHistory | None = None,
) -> Report:
    """Validate and groom in one pass.

    `history` is the one input that cannot be read from the store, so it is
    passed in rather than fetched here: this module stays pure and testable,
    and the caller decides whether asking git is worth it. Omitting it - which
    every caller but `check` does - skips the provenance check rather than
    failing it.
    """
    settings = config or Config()
    report = Report(items=list(items))
    for item in report.items:
        _check_item(item, report, settings)
    _check_references(report)
    _check_provenance(report, history)
    _groom(report, today, settings)
    return report
