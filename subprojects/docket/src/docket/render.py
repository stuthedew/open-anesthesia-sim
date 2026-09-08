"""Turning the store into the few lines a reader actually needs.

Every output here is sized against what it costs to read. The digest is
injected into a session's context and resent on every turn, so it is a
handful of lines and says nothing that cannot be acted on. The listing
replaces reading the store, so it carries exactly the fields a choice
between items turns on and no prose. Printing what a decision needs, rather
than the documents that contain it, is the cheapest optimization available
here and the one that compounds.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from datetime import UTC, date

from .checks import DONE_WHEN, REQUIRED_BRIEF, Report, brief_gaps
from .concurrency import undeclared
from .config import Config
from .model import (
    LANE_CROSSING,
    LANE_PRODUCT,
    LANE_UNPLACED,
    LANE_WORKFLOW,
    PRIORITIES,
    SELECTABLE_LANES,
    Item,
)
from .plan import Feature, Gate, effort_total, recommend, set_aside
from .release import PLANNED, RESERVED, Readiness, release_offer
from .roadmap import CLEAR, FREEZE, IMPLEMENT, RELEASE, STEP_SEPARATOR, Wave
from .trend import APPARATUS, BY_DAY, EFFORT_POINTS, LANES, PRODUCT_BUCKETS, QUEUE, Trend
from .vcs import (
    CURRENT,
    PULL,
    RESTART,
    REWRITTEN,
    BranchState,
    Carrier,
    CutsInFlight,
    FlightReport,
    OrphanedReport,
    Precedence,
    QueueEdit,
    RewriteReport,
    StrandedReport,
)


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _gloss(title: str, limit: int = 52) -> str:
    """A title short enough to sit inside a digest line and still identify the item.

    An id on its own identifies nothing - they are random by design - so a
    line naming one without a gloss makes the reader open a file to find out
    whether it matters.
    """
    if not title:
        return "no title"
    return title if len(title) <= limit else title[: limit - 1].rstrip() + "\u2026"


def _open_count(report: Report) -> int:
    """Every open item, the untriaged ones included.

    `Report.open_items` is the set that is a candidate for *work*, so it
    leaves out untriaged captures - which are candidates for a decision
    instead. That definition is right for `plan.py` and wrong for a number
    labelled "open": the two sets partition the open queue, so a count taken
    from `open_items` alone understates it by exactly the untriaged number
    printed beside it, and understates it most after a capture-heavy session
    (`PL-4WQS`).
    """
    return len(report.open_items) + len(report.untriaged)


def _counts(report: Report) -> str:
    """The band breakdown, with untriaged as the band-less remainder.

    The bands sum to the triaged count, not to `_open_count`, because an
    untriaged item carries no priority. Naming untriaged here is what keeps
    the breakdown summing to the total in front of it: dropped from this
    list, it reads as a band that does not exist, and printed outside the
    parentheses it reads as disjoint from the number it is part of.
    """
    counts = report.counts
    bands = ", ".join(f"{n} {p}" for p, n in counts.items())
    return f"{bands}, {len(report.untriaged)} untriaged"


def format_unread(flight: FlightReport) -> str:
    """The one line saying this answer is partial, or nothing when it is whole.

    Every command that reads the queue prints it, because every one of them
    ranks or marks against ids the checkout could prove and none of them can
    see the refs it could not. Silence there is the failure: a session is told
    an item is startable when the truth is that one ref went unread and might
    be carrying it, and the collision surfaces at push time instead.

    It is the ref's *commits* that went unread. Where such a ref is named for
    its item, `branches_in_flight` reports that id anyway - the branch name
    needs no history - so the sentence claims only what is actually missing.

    It says what went unread rather than what to do about it, for the reason
    `flight` reports rather than blocks - a ref beyond a truncated clone's
    horizon is the normal state of an agent session's container, and a tool
    that refused to answer there would refuse to answer at all.
    """
    if not flight.unreadable:
        return ""
    base = flight.base or "the default branch"
    them = "it" if len(flight.unreadable) == 1 else "them"
    return (
        f"{_plural(len(flight.unreadable), 'ref', 'refs')} could not be compared with {base} "
        f"on the history this checkout holds, so any item {'its' if them == 'it' else 'their'} "
        f"commits carry is missing here; `bin/docket flight` names {them}."
    )


def _marks(
    item: Item,
    in_flight: Collection[str],
    protected: tuple[str, ...] = (),
    gates: tuple[str, ...] = (),
) -> str:
    marks = [m for m in (item.effort, item.status) if m]
    if item.milestone:
        marks.append(item.milestone)
    if item.identifier in in_flight:
        marks.append("IN FLIGHT")
    if item.model_guidance is not None:
        marks.append(f"{item.model_guidance}, strongest model")
    elif item.delegability(protected, gates) is None:
        marks.append("delegable")
    return ", ".join(marks)


def format_list(
    report: Report,
    in_flight: FlightReport | None = None,
    protected_paths: tuple[str, ...] = (),
    gate_paths: tuple[str, ...] = (),
) -> str:
    """One line per open item: the queue without the briefs."""
    flight = in_flight or FlightReport()
    if not report.open_items and not report.untriaged:
        return ""

    lines = [f"Docket: {_open_count(report)} open - {_counts(report)}."]
    ordered = sorted(report.open_items, key=lambda i: i.sort_key())
    width = max((len(i.identifier) for i in ordered), default=0)
    for item in ordered:
        lines.append(
            f"{item.priority} {item.identifier:<{width}} {item.title} "
            f"({_marks(item, flight.ids, protected_paths, gate_paths)})"
        )

    if report.untriaged:
        lines.append("")
        lines.append(f"Untriaged ({_plural(len(report.untriaged), 'item', 'items')}):")
        for item in sorted(report.untriaged, key=lambda i: i.sort_key()):
            lines.append(f"   {item.identifier:<{width}} {item.title}")
    lines.append("Read an item's brief before starting it; this listing is for choosing.")
    if unread := format_unread(flight):
        lines.append(unread)
    return "\n".join(lines)


def format_delegable(
    report: Report,
    in_flight: FlightReport,
    protected_paths: tuple[str, ...],
    gate_paths: tuple[str, ...],
) -> str:
    """The worker's whole reading list: what may be worked, and what proves it.

    A separate answer from `next`, deliberately. `next` answers "what should
    *I* do now" - it ranks, limits, and explains itself, because a session
    picks one thing. A worker wants the opposite: everything it is allowed to
    touch, with each item's proof command beside it, so a batch can be started
    without opening a single file first.
    """
    candidates = [
        item
        for item in sorted(report.open_items, key=lambda i: i.sort_key())
        if item.delegability(protected_paths, gate_paths) is None
        and item.identifier not in in_flight.ids
    ]
    unread = format_unread(in_flight)
    if not candidates:
        return "\n".join(
            filter(
                None,
                (
                    "Nothing is delegable right now.",
                    "An item qualifies when it is ready, is not safety- or science-classed, "
                    "names a `verify:` command,",
                    "and declares `touches` outside both the protected paths and the "
                    "checks themselves. `docket list` shows what is open.",
                    unread,
                ),
            )
        )

    width = max(len(item.identifier) for item in candidates)
    lines = [f"{len(candidates)} item(s) may be worked by a cheaper model, best-first:", ""]
    for item in candidates:
        lines.append(f"  {item.priority} {item.identifier:<{width}} {item.title}")
        lines.append(f"  {'':<{width + 6}}verify: {item.verify}")
        lines.append("")
    lines.append("Read each item's brief before starting it, and follow docs/worker.md.")
    lines.append("Anything not listed here is not yours to take, whatever its priority.")
    if unread:
        lines.append(unread)
    return "\n".join(lines)


def _by_lane(
    report: Report, flight: FlightReport, plan: Wave | None, workflow_paths: tuple[str, ...]
) -> str:
    """Each lane's own pick, for the session that is one of a parallel pair.

    Ranked through `recommend` exactly as the `Top:` line above it is, and for
    the same reason: two lines in one block that ranked by different rules
    would contradict each other where a reader can see both at once.

    Empty when no boundary is declared, and when neither lane has anything
    startable - a line saying "product none, workflow none" costs a line of
    every session's context and answers nothing.
    """
    if not workflow_paths:
        return ""
    picks = {
        lane: recommend(
            list(report.items),
            flight.ids,
            limit=1,
            scope=plan.scope if plan is not None else None,
            lane=lane,
            workflow_paths=workflow_paths,
        )
        for lane in SELECTABLE_LANES
    }
    if not any(picks.values()):
        return ""
    named = ", ".join(
        f"{lane} {found[0].item.identifier}" if (found := picks[lane]) else f"{lane} none"
        for lane in SELECTABLE_LANES
    )
    held = set_aside(list(report.items), flight.ids, workflow_paths=workflow_paths)
    spanning = f"; {held.total} in neither lane" if held.total else ""
    return f"By lane, for a second session: {named}{spanning}."


def format_digest(
    report: Report,
    in_flight: FlightReport | None = None,
    ready: Readiness | None = None,
    plan: Wave | None = None,
    stranded: StrandedReport | None = None,
    workflow_paths: tuple[str, ...] = (),
    orphaned: OrphanedReport | None = None,
    cuts: CutsInFlight | None = None,
) -> str:
    """The few lines injected into session context at startup.

    The release line is here rather than left for someone to ask about,
    because nobody asks. Finished work sits unshipped until a person happens
    to wonder, and the store already knows when there is enough of it to be
    worth raising. The plan line is here for the same reason and a sharper
    one: the queue nags every session and the roadmap nags never, so "what
    next" gets answered from whatever ranks highest in the store - a question
    one level below the altitude that should decide it.

    Every line is resent on every turn of the session, so the plan gets one:
    the beat and the step, and `docket wave` for the rest.

    The stranded line is the one that only ever appears when it matters. An
    item on an unmerged branch is invisible to `list`, to `next`, and to every
    other line here, because all of them read the store in this checkout - so
    the digest is the only place a session can be told the queue it is reading
    is not all of it.

    The orphaned line is the same argument for everything that is not an item.
    A commit pushed to a branch after its pull request merged is merged by
    nothing, and unless it happened to touch `docs/items/` no check in this
    project noticed - so a session started from a default branch missing work
    everyone believed landed, and a rule the owner had asked for was quietly
    void (`PL-3D2M`). It appears only when a branch is genuinely split across
    the base, which on this repository is never in the ordinary case.

    The `Top:` line goes through `recommend` for the same reason `next` does,
    and one sharper: the two lines sit in one block of output, so ranking them
    by different rules made them contradict each other where a reader could
    see both at once. Sorting the store by priority alone opened every session
    with `PL-9Y42` - v0.4.0 science scope - two lines above a beat that said
    clear v0.2.8's gate, and left the reader to work out which of them knew
    about the plan (queue item PL-Q2BJ). Deriving the line from the `plan`
    already passed here is what makes that disagreement unrepresentable rather
    than merely fixed.

    Where the ranking still surfaces work the step excludes - because nothing
    it includes is startable - the line names the milestone that places the id
    instead of dropping it. That is `recommend`'s own rule: which section
    names an id is a fact, and whether the plan is wrong about it is a verdict
    this cannot support.

    The lane line exists because this is what a session reads *first* - before
    it would think to ask for a lane, and before the skill that would tell it
    to has loaded. `docket next` gained `product` and `workflow` so two
    simultaneous sessions never rank onto one item, and a digest that named a
    single `Top:` left the split inert until somebody remembered to type it
    (`PL-2NSX`). Both picks are named rather than one: the hook runs before
    anything has been said, so it cannot know which half this session is, and
    guessing would hand a session the other one's work.

    It costs one line in every digest, single-session ones included, which is
    why it carries "for a second session" rather than reading as an
    instruction, and why it is omitted entirely where no boundary is declared
    or neither lane has anything startable. Work spanning both halves is
    counted on the same line: a session that read only the two picks would
    otherwise take them for the whole queue.
    """
    flight = in_flight or FlightReport()
    if not report.items:
        return ""

    lines = [f"Docket: {_open_count(report)} open - {_counts(report)}."]
    for item in sorted(report.open_items, key=lambda i: i.sort_key()):
        if item.priority != "P0":
            continue
        lines.append(
            "  P0 (before feature work): "
            f"{item.identifier} {item.title} ({_marks(item, flight.ids)})"
        )

    picks = recommend(
        list(report.items), flight.ids, limit=1, scope=plan.scope if plan is not None else None
    )
    top = picks[0] if picks else None
    if top is not None and top.item.priority != "P0":
        marks = _marks(top.item, flight.ids)
        if top.scoped_to:
            marks += f", scoped to {top.scoped_to}, not this step"
        lines.append(f"  Top: {top.item.identifier} {top.item.title} ({marks})")

    if lane_line := _by_lane(report, flight, plan, workflow_paths):
        lines.append(f"  {lane_line}")

    if flight.ids:
        lines.append(
            f"  In flight on a branch: {', '.join(sorted(flight.ids))} - do not start these again."
        )
    if unread := format_unread(flight):
        lines.append(f"  {unread}")
    if stranded is not None and stranded.items:
        named = ", ".join(
            f"{item.identifier} ({_gloss(item.title)})" for item in stranded.items[:2]
        )
        rest = f", +{len(stranded.items) - 2} more" if len(stranded.items) > 2 else ""
        lines.append(
            f"  Only on a branch, not in this checkout: {named}{rest}. "
            "`bin/docket stranded` to recover."
        )
    if orphaned is not None and orphaned.branches:
        first = orphaned.branches[0]
        rest = f", +{len(orphaned.branches) - 1} more" if len(orphaned.branches) > 1 else ""
        outstanding = _plural(len(first.outstanding), "file", "files")
        lines.append(
            f"  Left on a branch after its pull request merged: {first.ref} "
            f"({outstanding}){rest}. `bin/docket stranded` to recover."
        )
    if report.untriaged:
        lines.append(
            f"  {_plural(len(report.untriaged), 'item', 'items')} untriaged; "
            "`bin/docket triage` to fold them into the queue."
        )
    if report.errors:
        lines.append(f"  {_plural(len(report.errors), 'error', 'errors')}; run `make docket`.")
    if report.advisories:
        lines.append(
            f"  Grooming due: {_plural(len(report.advisories), 'advisory', 'advisories')} "
            "(`make docket` to see them)."
        )
    if ready is not None and ready.is_worth_cutting:
        completes = (
            f", completing {', '.join(ready.completed_features)}"
            if ready.completed_features
            else ""
        )
        # The offer is where a duplicate release *starts*, so this is where
        # saying so is worth most: the second session never raises it, rather
        # than being refused after the owner has already approved one
        # (`PL-66FP`). The advice is replaced rather than appended - "offer
        # 0.3.9" and "0.3.9 is already being cut" in one line is two answers.
        held = [branch for branch in (cuts.branches if cuts else ()) if not branch.mine]
        advice = (
            "A release is already being cut on "
            + ", ".join(f"{branch.ref} (v{', v'.join(branch.versions)})" for branch in held)
            + "; do not offer another until it merges."
            if held
            else _release_advice(ready, plan)
        )
        lines.append(
            f"  Releasable: {len(ready.shippable)} finished item(s) since "
            f"{ready.current_version}{completes}. {advice}"
        )
    if plan is not None and plan.step is not None:
        position = (
            f"step {plan.step.ordinal} of {plan.total_steps}"
            if plan.step.ordinal is not None
            else "between numbered steps"
        )
        unparsed = " Timeline does not parse cleanly - check `wave`." if plan.problems else ""
        lines.append(
            f"Plan: {plan.version or 'unknown'}, {position} ({plan.step.label}). "
            f"Beat: {_beat_line(plan)}.{unparsed}"
        )
    lines.append(
        "`bin/docket status` shows the project by feature; `list` every item; `wave` the plan."
    )
    return "\n".join(lines)


def format_stranded(report: StrandedReport) -> str:
    """What exists only on a branch, with the command that brings each one back.

    Organized by item rather than by branch, because the loss is of an item and
    the recovery is of a file. The branches are still named in full - every one
    holding a copy, not just the first - so the other question this answers
    reads off the same output: a branch named nowhere below carries no item the
    default branch lacks, and deleting it loses no work the queue knows about.

    That is the only claim being made about *items*. What a branch carries
    outside `docs/items/` is `format_orphaned`'s question, and `cmd_stranded`
    prints both - the two together being what closes the asymmetry `PL-3D2M`
    found, where a dropped commit surfaced only if it happened to touch the
    store.

    **The unrefreshed-base caveat sits above the recovery command, not under
    it.** Every line here rests on the default branch not holding the item, so
    a stale base turns a merge into a finding - and the finding's recovery
    overwrites the merged copy with the older one, which is what happened on
    2026-09-05 (`PL-KBFN`). A reader who has already read `git checkout` has
    made the decision the caveat exists to inform.
    """
    if not report.known:
        return f"Stranded items not checked: {report.declined}."

    refs = _plural(report.refs_read, "branch ref", "branch refs")
    if not report.items:
        return "\n".join(
            [
                f"No item exists only on a branch, across the {refs} this checkout holds.",
                "A branch not fetched here was not read, so this is bounded by what has been.",
                *_stale_base(report),
            ]
        )

    lines = [
        f"{_plural(len(report.items), 'item exists', 'items exist')} only on a branch, "
        f"across the {refs} this checkout holds:",
        "",
        *_stale_base(report),
    ]
    if not report.fetched:
        lines.append("")
    for item in report.items:
        lines.append(f"{item.identifier}  {item.title or '(title unreadable)'}")
        lines.append(f"  only on: {', '.join(item.branches)}")
        lines.append(f"  recover: git checkout {item.branches[0]} -- {item.path}")
        lines.append("")
    lines.append(
        "A branch on live work will appear here and that is expected; the hole is a "
        "branch nobody will merge."
    )
    lines.append("Every other branch read carries no item the default branch lacks.")
    return "\n".join(lines)


def _stale_base(report: StrandedReport) -> list[str]:
    """The caveat a report read against an unrefreshed base owes, or nothing.

    In the negative only, for the reason `StrandedReport.fetched` gives: a
    quiet fetch prints nothing whether it reached the remote or not, so "we
    tried" is the strongest claim available and "we did not" is the only one
    worth a line.
    """
    if report.fetched:
        return []
    return [
        "Nothing refreshed the default branch for this answer, so an item merged "
        "since the last fetch reads as stranded here."
    ]


def format_orphaned(report: OrphanedReport) -> str:
    """Work left on a branch after its pull request merged, and how to recover it.

    Organized by branch rather than by file, the opposite of `format_stranded`,
    because the loss here is of a *push* - one commit that went nowhere - and
    the reader's first question is which branch to look at. The files under it
    are what that commit left behind.

    The landed side is stated rather than assumed, because it is the evidence:
    a branch appears here because the default branch holds some of what it
    introduced and not the rest, and a reader who cannot see that count cannot
    tell this from an ordinary branch in flight.
    """
    if not report.known:
        return f"Work left on a merged branch not checked: {report.declined}."

    # The count is of refs the default branch has *not* already taken whole,
    # which is a smaller number than `format_stranded` reports and a different
    # claim: a branch merged in full carries nothing to leave behind, so it is
    # excluded before this read begins rather than examined and cleared.
    refs = _plural(report.refs_read, "unmerged branch ref", "unmerged branch refs")
    if not report.branches:
        return f"No branch carries work its own pull request left behind, across the {refs} read."

    lines = [
        f"{_plural(len(report.branches), 'branch carries', 'branches carry')} work the "
        f"default branch does not hold, having already taken the rest of it:",
        "",
    ]
    for branch in report.branches:
        landed = _plural(len(branch.landed), "file", "files")
        lines.append(f"{branch.ref}  ({landed} of its work already landed)")
        # Each commit carries its own paths rather than the branch listing them
        # all after the last one, which read as though they belonged to it.
        for commit in branch.commits:
            lines.append(f"  {commit.commit[:9]}  {commit.subject}")
            for path in commit.paths:
                lines.append(f"    {path}")
        lines.append(f"  recover: git checkout {branch.ref} -- {branch.outstanding[0]}")
        lines.append("")
    lines.append(
        "A pull request merges the head it was opened against; a commit pushed to the "
        "branch afterwards is merged by nothing and reported by nothing else."
    )
    return "\n".join(lines)


def _since(last_commit: date | None, today: date) -> str:
    """How long a branch has been sitting, in the words the reader judges with."""
    if last_commit is None:
        return "no commit of its own this checkout can read"
    days = (today - last_commit).days
    if days <= 0:
        return "last commit today"
    return f"last commit {_plural(days, 'day', 'days')} ago"


def format_flight(report: FlightReport, today: date) -> str:
    """Which items are on a branch, how stale each branch is, and what went unread.

    The age is reported rather than thresholded, because "has an unmerged
    branch" and "is being worked right now" are different claims and no
    timeout tells them apart: a branch touched an hour ago is a live session,
    and the same branch three weeks on is work nobody will merge. Only the
    reader knows which, so both get the same line and the date decides it.

    **`FlightReport.editing` is deliberately not printed here.** Capturing a
    finding before a session ends is mandatory, so nearly every live branch has
    edited some item's file, and a section listing them would fire on almost
    every run while changing no answer to the question this command asks -
    which is `CLAUDE.md`'s definition of a check that should not exist. The
    weaker mark prints where it changes a decision instead: `triage`, which is
    about to write to one of those files, and `show`, which is about to start
    the item (`PL-N1JK`).
    """
    lines: list[str] = []
    if report.branches:
        lines.append(
            f"{_plural(len(report.branches), 'item is', 'items are')} on a branch "
            "the default branch has not taken:"
        )
        lines.append("")
        width = max(len(branch.name) for branch in report.branches)
        for branch in report.branches:
            lines.append(
                f"{branch.item_id}  {branch.name:<{width}}  {_since(branch.last_commit, today)}"
            )
        lines.append("")
        lines.append(
            "A live session and a branch nobody will merge look the same here; "
            "the age is what separates them."
        )
    else:
        lines.append("No branch carries an item id, in its name or at the front of a commit.")

    if report.unreadable:
        lines.append("")
        base = report.base or "the default branch"
        carried = "its commits carry" if len(report.unreadable) == 1 else "their commits carry"
        lines.append(
            f"{_plural(len(report.unreadable), 'ref cannot', 'refs cannot')} be compared with "
            f"{base} on the history this checkout holds, so what {carried} is unknown:"
        )
        lines.extend(f"  {name}" for name in report.unreadable)
    return "\n".join(lines)


def format_queue_edit(edit: QueueEdit, today: date) -> str:
    """That an item's file has already been edited, which is not that it is in flight.

    **The line exists to be different from `IN FLIGHT`, so it does not open
    with a mark.** Two sessions triaged one pair of items on 2026-09-06,
    fetched, checked and were each told correctly that nothing was in flight -
    a triage pass has no diff outside the queue, so `_annotates_only` withholds
    the claim and nothing else was reading the paths (`PL-N1JK`). What the
    second session needed was not "do not start this", which would have been
    false, but "the file you are about to write to has already been written
    to", which is true and is a different sentence.

    So it says what was observed and what follows, and it says the item is
    startable in as many words. A weaker signal worded like a stronger one is
    read as the stronger one, and the cost lands on the wrong side: an item
    nobody is working left unstarted because a capture commit touched its file.
    """
    return (
        f"  Its file is already edited on {edit.name} ({_since(edit.last_commit, today)}).\n"
        f"  Not work in flight - {edit.item_id} is startable - but a second edit to the\n"
        "  same file collides at merge, so land the smaller change first."
    )


def _staked(carrier: Carrier, today: date) -> str:
    """When a branch claimed the item, on one clock, and how long since it moved.

    Normalized to UTC rather than printed as git wrote it. Two sessions can be
    in two zones, and two timestamps a reader has to convert before comparing
    are two timestamps a reader will compare wrongly - which here would mean
    reading the wrong branch as the one that continues.
    """
    when = (
        "when it named the item could not be read"
        if carrier.staked is None
        else f"named it {carrier.staked.when.astimezone(UTC):%Y-%m-%d %H:%M} UTC"
    )
    return f"{when}; {_since(carrier.last_commit, today)}"


def format_precedence(order: Precedence, today: date) -> str:
    """Who is carrying an item, and - where more than one is - which session yields.

    **The verdict is printed rather than left to be worked out, and that is the
    whole reason this exists.** Two sessions that discover each other reason
    from the same evidence and can still reach opposite conclusions, and the
    expensive outcome is not both continuing but both standing down: the item
    is then unstarted and each session believes the other has it. A rule stated
    as prose cannot rule that out. One computed here, from an order over
    commits, can - so the answer arrives as an answer.

    The single-carrier cases are the common ones and they are one line each.
    The one worth the change is a carrier that is *this* branch: `show` used to
    tell a session re-reading its own item not to start it again, which is a
    false alarm at exactly the moment a session is most likely to look.
    """
    if not order.carriers:
        return ""
    item = order.item_id
    if len(order.carriers) == 1:
        only = order.carriers[0]
        if only.mine:
            return f"  IN FLIGHT on this branch ({only.ref}) - {item} is this session's own work."
        return (
            f"  IN FLIGHT on {only.ref} ({_since(only.last_commit, today)}) "
            f"- do not start {item} again."
        )

    lines = [
        f"  {item} is on {_plural(len(order.carriers), 'branch', 'branches')}. Whichever named "
        "it first holds it, and a",
        "  tie breaks on that commit's hash, so which session yields reads the same in",
        "  every checkout:",
        "",
    ]
    for position, carrier in enumerate(order.carriers):
        verdict = "holds it" if position == 0 else "yields  "
        here = " (this branch)" if carrier.mine else ""
        lines.append(f"    {verdict}  {carrier.ref}{here}")
        lines.append(f"                {_staked(carrier, today)}")
    lines.append("")
    if order.yields:
        lines.append("  This branch yields: stop, and hand over what you have already found.")
    elif order.mine is not None:
        lines.append(f"  This branch holds {item}; the others are the ones that yield.")
    else:
        lines.append(f"  This branch carries none of them - do not start {item} again.")
    if order.unreadable:
        # The order is over the refs that could be read, and a ref beyond a
        # truncated clone's horizon is the normal state of an agent's
        # container. Saying so is the same refusal to present a partial reading
        # as a complete one that `format_unread` makes for the rest.
        lines.append(
            f"  ({_plural(len(order.unreadable), 'ref', 'refs')} went unread, so this order "
            "is over what could be read.)"
        )
    return "\n".join(lines)


def format_branch_state(state: BranchState, flight: FlightReport | None = None) -> str:
    """Where the branch stands, what to run about it, and what moved while it sat.

    The recovery command is printed rather than run, and that is the whole
    posture: `git checkout -B` discards commits, so a check that fired
    unattended would be a worse failure than the staleness it cures. It reports
    and the reader decides, the way `flight` and `stranded` do.

    Two commands for the ordinary cases and no third. A branch behind with
    nothing of its own is restarted; a branch behind with work of its own
    merges the base in. Rebase is deliberately not offered: telling the two
    apart would mean guessing which commits are disposable, and a rebase of a
    pushed branch needs a force-push, which this project's squash-merge path is
    set up to avoid.

    The rewritten case is the exception, and it *replaces* that advice rather
    than adding to it. Both ordinary commands are destructive across a rewrite
    - a merge replays the base's own history against itself, and `checkout -B`
    discards the only copy of whatever the branch pushed into the rewrite's
    window - so the block names the commits held nowhere else and gives a
    recovery that keeps them. It is longer than every other line here on
    purpose: it prints only where the alternative is silent data loss.

    The ids are what make it worth re-running mid-session. "3 behind" says the
    base moved; naming what landed answers whether the thing this session was
    waiting on is in.
    """
    if state.declined:
        head = f"Branch: {state.branch or 'unknown'} - {state.declined}."
        return head if flight is None else "\n".join(filter(None, (head, _flight_lines(flight))))

    base, branch = state.base, state.branch
    lines: list[str] = []
    if state.disposition == CURRENT:
        lines.append(f"Branch: {branch}, current with {base} ({state.ahead} ahead).")
    elif state.disposition == PULL:
        lines.append(f"Branch: {branch} is {state.behind} behind {base}.")
        lines.append("  `git pull` before starting.")
    elif state.disposition == REWRITTEN and (rewrite := state.rewrite) is not None:
        lines.append(f"Branch: {branch} is {state.behind} behind {base} and {state.ahead} ahead.")
        lines.append(
            f"  That is a rewritten history, not divergence: {rewrite.duplicated} of this "
            f"branch's {rewrite.total} commits are already on {base} under different hashes."
        )
        lines.extend(_rewrite_recovery(rewrite, branch, base))
    elif state.disposition == RESTART:
        lines.append(f"Branch: {branch} is {state.behind} behind {base} with nothing of its own.")
        lines.append("  Its work is merged or it never had any. Restart it before editing:")
        lines.append(f"  git checkout main && git pull && git checkout -B {branch} {base}")
    else:
        lines.append(f"Branch: {branch} is {state.behind} behind {base} and {state.ahead} ahead.")
        lines.append(f"  Merge {base} before your first edit, not at push time:")
        lines.append(f"  git merge {base}")

    if state.landed:
        lines.append(f"  Landed on {base} since this branch forked: {', '.join(state.landed)}.")
    # Only where the base is a remote-tracking ref: a local base is not made
    # fresher by fetching, so the caveat would be describing a hazard that
    # cannot arise and teaching the reader to discount the ones that can.
    if not state.fetched and "/" in base:
        lines.append(f"  Read from the last fetch; nothing refreshed {base} for this answer.")
    if flight is not None and (extra := _flight_lines(flight)):
        lines.append(extra)
    return "\n".join(lines)


def _rewrite_recovery(rewrite: RewriteReport, branch: str, base: str) -> list[str]:
    """What is held only here, and how to keep it while moving onto the new history.

    The listing is the point. A count of commits at risk is a number a reader
    discounts; the subjects are what make it obvious that the branch holds a
    capture or a conflict resolution nothing else has, and the short hashes are
    what the recovery command needs.

    **Unbounded, unlike every other list this module prints.** Truncating it
    would truncate the `cherry-pick` line under it, and a recovery command that
    silently drops commits is the failure this whole report exists to prevent -
    it would look complete and lose exactly what it was printed to save. There
    is no shorter honest form either: no single git command lists the commits
    held only here, since telling them from the duplicated ones is what this
    module just spent a read working out. The block fires only where a history
    has been rewritten, so its length is not a cost anyone pays twice.
    """
    # Tags are the half a branch cleanup misses: they still point into the old
    # history, so a clone keeps whatever the rewrite removed reachable through
    # them, and `git fetch` alone will not move a tag that already exists.
    tags = "  git fetch --tags --force origin  # tags still point at the old history"
    if not rewrite.own:
        return [
            "  Nothing is held only here, so the branch can be moved across whole:",
            f"  git checkout -B {branch} {base}",
            tags,
        ]
    held = "it" if len(rewrite.own) == 1 else "them"
    lines = [
        f"  {_plural(len(rewrite.own), 'commit exists', 'commits exist')} only here, and "
        f"`git merge`, `git reset --hard` and `git checkout -B` each lose {held}:"
    ]
    lines.extend(f"    {short} {subject}" for short, subject in rewrite.own)
    lines.append(f"  Carry {held} onto the rewritten history rather than discarding {held}:")
    lines.append(f"  git checkout -B {branch}-rewritten {base}")
    lines.append(f"  git cherry-pick {' '.join(short for short, _ in rewrite.own)}")
    lines.append(tags)
    if rewrite.merges:
        lines.append(
            "  One of those is a merge commit: `cherry-pick -m 1` takes it, or redo the "
            "resolution by hand, because its parents no longer exist on the new history."
        )
    return lines


def _flight_lines(flight: FlightReport) -> str:
    """What is being worked elsewhere, for a reader asking whether to wait.

    The digest carries the same line, and carries it once per session; this one
    is read when a session asks again, which is the moment the digest's copy is
    most likely to be out of date.
    """
    lines = []
    if flight.ids:
        lines.append(f"  Still in flight on a branch: {', '.join(sorted(flight.ids))}.")
    if unread := format_unread(flight):
        lines.append(f"  {unread}")
    return "\n".join(lines)


def format_triage(report: Report, config: Config, flight: FlightReport | None = None) -> str:
    """Every untriaged item, what is unset on it, and the rules that bind the answer.

    A worklist and a constraint sheet, deliberately not a recommendation. What
    an item is worth, how big it is, and what it belongs with are judgments,
    and a tool that guessed at them would produce something that looks
    authoritative and is not. What *is* mechanical is which fields are still
    empty and which rules `docket check` will apply the moment the status
    changes - and that is exactly what a session otherwise reloads a 300-line
    skill to recall, and then finds out afterwards whether it recalled
    correctly.

    The constraints are read from the settings and the checker rather than
    restated here, so they cannot drift from what the checker will actually
    say.

    **Which branch already carries an item is mechanical too, and triage is
    the more exposed of the two entry points rather than the less.** Starting
    an item is preceded by `show`, which marks it; triage is reached straight
    from the session-start digest, which reports the untriaged *count* and
    nothing about who is holding those items. Two sessions triaged `PL-B0YN`
    and `PL-LXR3` on one afternoon and the merge discarded most of one answer,
    the reasoning behind it included (queue item PL-PRHN).

    It marks and does not refuse, for the reason `branches_in_flight` reports
    rather than blocks: the answer is bounded by what has been pushed and by
    the refs this checkout can read, so a lock built on it would sooner or
    later block the session whose own branch is the one holding the item,
    with no way to tell it apart. Triage is cheap to redo and expensive to
    have refused.

    **The mark that fires here is not the one `next` ranks on, and on a triage
    pass it is usually the only one there is.** A pass that only fills in
    fields writes nothing outside `docs/items/`, which is exactly the shape
    `branches_in_flight` refuses to read as work - so before `FlightReport`
    carried the file edits, two sessions triaging one item could each fetch,
    each run `show`, and each be told truthfully that nothing was in flight.
    Both marks print here and neither ranks anything (`PL-N1JK`).

    `format_unread` comes with the mark rather than as a nicety, exactly as it
    does under `show`: the marks are drawn from the refs this checkout could
    read, and silence about the ones it could not presents a partial reading
    as a complete one.
    """
    if not report.untriaged:
        return "Nothing is untriaged."

    flight = flight or FlightReport()
    # The branch name, not merely the fact of one: a session reading `IN FLIGHT
    # on claude/pl-lxr3-...` can tell another session's work from its own
    # without leaving the output, which is the whole difference between a
    # warning that is heeded and one that is trained out.
    carrying = {branch.item_id: branch.name for branch in flight.branches}
    # The weaker mark, for the case the stronger one cannot reach at all: a
    # triage pass writes nothing outside the queue, so `_annotates_only`
    # withholds its claim and two passes on one item are invisible to each
    # other however carefully each fetches (`PL-N1JK`).
    editing = {edit.item_id: edit.name for edit in flight.editing}
    lines = [f"{_plural(len(report.untriaged), 'item is', 'items are')} untriaged.", ""]
    for item in sorted(report.untriaged, key=lambda i: i.sort_key()):
        lines.append(f"{item.identifier}  {item.title}")
        if held_by := carrying.get(item.identifier):
            lines.append(f"  IN FLIGHT on {held_by} - triaging it here as well collides at merge.")
        elif edited_on := editing.get(item.identifier):
            lines.append(f"  Its file is already edited on {edited_on}.")
            lines.append(
                "  A capture or another triage pass, not work in flight - but a second answer"
            )
            lines.append("  here is a second resolution of the same file, so skip it.")
        lines.append(f"  unset: {_unset(item)}")
        missing, empty, stub = brief_gaps(item.body)
        if missing:
            lines.append(f"  brief still missing: {', '.join(missing)}")
        if empty:
            lines.append(f"  brief has nothing under: {', '.join(empty)}")
        if stub:
            lines.append(f"  the capture template is still above the brief: {stub} is empty")
            lines.append("  and a second **Problem.** starts below it - delete the template's")
            lines.append("  headings, and the brief beneath them is the item.")
        declared = _declared(item)
        if declared:
            lines.append(f"  declared: {declared}")
        lines.append("")
        lines.extend(
            f"    {line}" if line.strip() else "" for line in item.body.strip().splitlines()
        )
        lines.append("")

    lines.append("The rules these answers have to satisfy:")
    lines.extend(f"  - {rule}" for rule in _triage_rules(report, config))
    lines.append("")
    lines.append("What each item is worth, how big it is and what it belongs with are not")
    lines.append("computed here. This prints the rules; applying them is yours.")
    if unread := format_unread(flight):
        lines.append(unread)
    return "\n".join(lines)


def _unset(item: Item) -> str:
    """The fields triage exists to fill, marking the ones the checker requires."""
    fields = [
        ("priority", item.priority, True),
        ("effort", item.effort, True),
        ("classes", ", ".join(item.classes), False),
        ("touches", ", ".join(item.touches), False),
        ("feature", item.feature, False),
    ]
    names = [f"{name}*" if required else name for name, value, required in fields if not value]
    return (", ".join(names) + "   (* required by `docket check`)") if names else "nothing"


def _declared(item: Item) -> str:
    parts = []
    if item.classes:
        parts.append(f"classes {', '.join(item.classes)}")
    if item.touches:
        parts.append(f"touches {', '.join(item.touches)}")
    if item.feature:
        parts.append(f"feature {item.feature}")
    return "; ".join(parts)


def _triage_rules(report: Report, config: Config) -> list[str]:
    """The constraints, stated with the counts that make each one checkable."""
    counts = report.counts
    top = next((p for p in PRIORITIES if counts.get(p)), PRIORITIES[0])
    # Startable rather than every member of the band, because `checks.py` counts
    # it that way: a blocked item is not a choice a session can make
    # (`PL-P23D`). Two numbers for one rule is worse than either of them.
    startable = sum(1 for i in report.open_items if i.priority == top and i.status != "blocked")
    rules = [
        f"{'/'.join(config.safety_classes)} classes force P0 or P1; `docket check` "
        "rejects them at P2 or P3.",
        f"the top band is {top}, holding {startable} startable of the "
        f"{config.top_band_limit} a session can choose between at a glance.",
        f"process work ({', '.join(config.process_classes)}) does not enter the top "
        "band ahead of the product work already in it - an item counts as process "
        "work only when every one of its classes is in that set.",
    ]
    if config.protected_paths:
        rules.append(
            f"`touches` naming {', '.join(config.protected_paths)} makes the item "
            "non-delegable whatever proves it, so a cheaper model can never take it."
        )
        # Nested rather than a rule of its own: with no protected paths
        # nothing is delegable at all, and a project that has not opened the
        # lane does not need to be told what would close it again.
        if config.gate_paths:
            rules.append(
                f"`touches` naming {', '.join(config.gate_paths)} makes the item "
                "non-delegable for a second reason: `docket verify` fails any diff "
                "that edits the checks, so offering the work would mean refusing it "
                "once done."
            )
    if config.verify_required_from is not None:
        rules.append(
            "an item set to `ready` must name a `verify:` command, or record in "
            "`not-delegable` why no command can prove it. Run the command before "
            "writing it down."
        )
    rules.append(
        "a status past `untriaged` needs the full brief: "
        f"{', '.join((*REQUIRED_BRIEF, DONE_WHEN))}. A heading may continue past "
        "those words - `**Why it matters, and why it is not new.**` is the same "
        "section - but it needs text under it."
    )
    return rules


def format_gate(gate: Gate, debt_classes: tuple[str, ...]) -> str:
    """The debt owed before a milestone, as the two lists a gate record holds.

    Recording Gate 0 by hand meant reading every open item's classes and
    status, applying the rule, splitting the result by scope and typing the
    ids into the plan - a full pass over 48 items, repeated before every
    milestone. All of that is in the front matter, and none of it needs
    judgment. What still does is whether each item is really debt and whether
    the gate should open, which is why this prints two lists and no verdict.
    """
    if not gate.items:
        subject = f" carrying `{gate.feature}`" if gate.feature else ""
        return f"No open debt{subject}. Nothing to clear."

    lines = [
        f"{_plural(len(gate.items), 'open debt item', 'open debt items')}"
        + (f", against the `{gate.feature}` milestone." if gate.feature else ".")
    ]

    lines.append("")
    lines.append(
        f"Cleared before it begins - {len(gate.outside)} ({effort_total(gate.outside)}):"
        if gate.feature
        else f"Open debt - {len(gate.outside)} ({effort_total(gate.outside)}):"
    )
    lines.extend(_gate_lines(gate.outside))

    if gate.feature:
        lines.append("")
        lines.append(
            f"Cleared by the milestone itself - {len(gate.inside)} ({effort_total(gate.inside)}):"
        )
        lines.extend(_gate_lines(gate.inside))
        if not gate.inside:
            lines.append("  nothing carries that feature")

    lines.append("")
    lines.append(f"Debt is an open item classed {', '.join(debt_classes)}, or at needs-decision.")
    lines.append("Whether each of these is really debt, whether the gate should open, and")
    lines.append("what goes into the plan are not decided here. Recording it is a deliberate act.")
    return "\n".join(lines)


def _gate_lines(items: list[Item]) -> list[str]:
    if not items:
        return ["  nothing"]
    width = max(len(item.identifier) for item in items)
    lines = []
    for item in items:
        marks = ", ".join(item.classes) or "no classes"
        if item.status != "ready":
            marks = f"{item.status}, {marks}"
        lines.append(
            f"  {item.priority} {item.effort or '-'} {item.identifier:<{width}} "
            f"{item.title} ({marks})"
        )
    return lines


def format_check(report: Report) -> str:
    """The full report: everything wrong, and everything worth a second look."""
    headline = (
        f"docket: {_open_count(report)} open ({_counts(report)}), "
        f"{_plural(len(report.errors), 'error', 'errors')}, "
        f"{_plural(len(report.advisories), 'advisory', 'advisories')}"
    )
    # On the headline rather than only further down, because the headline is
    # what a reader takes away: "0 errors" from a run where a check never ran
    # says the store is sound when nobody looked.
    if report.declined:
        headline += f", {len(report.declined)} not checked"
    lines = [headline]
    # Under the headline rather than appended to it: this is what the run cost
    # rather than what it found, and the two want different attention. Absent
    # entirely where nothing ran, so a reader never sees a cost line whose
    # numbers came from a run that declined (`PL-9NKK`).
    if report.cost:
        lines.append(f"  {report.cost}")
    if report.errors:
        lines += ["", "Errors (the store is wrong; fix before committing):"]
        lines += [f"  {message}" for message in report.errors]
    if report.advisories:
        lines += ["", "Grooming advisories (judgment needed; nothing is failing):"]
        lines += [f"  {message}" for message in report.advisories]
    if report.declined:
        lines += ["", "Not checked (this checkout cannot answer; nothing is claimed):"]
        lines += [f"  {message}" for message in report.declined]

    silent = undeclared(report.open_items)
    if silent:
        lines += [
            "",
            f"{_plural(len(silent), 'item declares', 'items declare')} no `touches`, so "
            "concurrency cannot be reasoned about for them:",
            f"  {', '.join(i.identifier for i in silent)}",
        ]
    if not report.errors and not report.advisories and not report.declined:
        lines.append("No errors, nothing due for grooming.")
    return "\n".join(lines)


def format_priority_groups(items: list[Item]) -> str:
    """The queue grouped by band, for a human reading the whole thing."""
    lines: list[str] = []
    for priority in PRIORITIES:
        band = [i for i in items if i.priority == priority]
        if not band:
            continue
        lines.append(f"{priority} ({len(band)})")
        for item in sorted(band, key=lambda i: i.sort_key()):
            lines.append(f"  {item.identifier} {item.title}")
    return "\n".join(lines)


def format_status(
    report: Report,
    ready: Readiness | None = None,
    in_flight: FlightReport | None = None,
    plan: Wave | None = None,
) -> str:
    """The whole project at feature altitude, which is the altitude decisions happen at.

    `format_list` answers "which item", and that is the wrong question to open
    with. Nobody decides what to do next by reading twenty-three item titles;
    they decide by knowing which halves of the project are underway, which
    have not started, and what is urgent enough to ignore all of that. So this
    leads with features, names only the next item inside each, and keeps the
    individually-urgent work in a section of its own.
    """
    from .plan import features as group_features

    flight = in_flight or FlightReport()
    grouped = group_features(report.items)
    lines: list[str] = []

    underway = [f for f in grouped.values() if f.is_underway]
    not_started = [f for f in grouped.values() if f.open_items and not f.done]
    complete = [f for f in grouped.values() if f.is_complete]

    def next_in(feature: Feature) -> str:
        candidates = sorted(
            (i for i in feature.open_items if i.status != "blocked"), key=lambda i: i.sort_key()
        )
        if not candidates:
            return "all remaining work is blocked"
        item = candidates[0]
        mark = " [IN FLIGHT]" if item.identifier in flight.ids else ""
        return f"next: {item.identifier} {item.title} ({item.effort}){mark}"

    if underway:
        lines.append("Underway")
        for feature in sorted(underway, key=lambda f: -f.progress):
            lines.append(
                f"  {feature.name:<20} {len(feature.done)}/{len(feature.items)}  {next_in(feature)}"
            )
    if not_started:
        lines.append("")
        lines.append("Not started")
        for feature in sorted(not_started, key=lambda f: f.name):
            efforts = ", ".join(sorted({i.effort for i in feature.open_items if i.effort}))
            lines.append(f"  {feature.name:<20} 0/{len(feature.items)}  ({efforts})")

    loose = [
        i
        for i in report.open_items
        if not i.feature and i.status != "blocked" and i.identifier not in flight.ids
    ]
    if loose:
        lines.append("")
        lines.append("Outside any feature - picked on priority alone")
        for item in sorted(loose, key=lambda i: i.sort_key())[:5]:
            note = f" - {item.model_guidance}" if item.model_guidance else ""
            lines.append(f"  {item.priority} {item.identifier} {item.title} ({item.effort}{note})")

    if complete:
        lines.append("")
        lines.append(f"Finished: {', '.join(sorted(f.name for f in complete))}")

    if ready is not None and ready.shippable:
        lines.append("")
        done_note = (
            f", completing {', '.join(ready.completed_features)}"
            if ready.completed_features
            else ", completing no feature yet"
        )
        lines.append(
            f"Unreleased: {len(ready.shippable)} finished item(s) since "
            f"{ready.current_version}{done_note}."
        )
        offer = release_offer(ready, plan)
        if offer.kind == RESERVED:
            lines.append(
                f"  Not {offer.version}: the roadmap gives that version to "
                f'"{offer.milestone}", which is unfinished. `docket wave` for what is due.'
            )
        else:
            lines.append(f"  Next version would be {offer.version}.")
    if unread := format_unread(flight):
        lines.append("")
        lines.append(unread)
    return "\n".join(lines)


def format_wave(plan: Wave) -> str:
    """Where the project stands on the cadence, and nothing about whether it should.

    Five lines at most, because this is read at the top of a session beside
    the digest, not studied. Each one states a fact with the file it came from
    behind it; none of them says whether the plan is still the right plan.
    """
    lines = [f"Version   {plan.version or 'unknown'}"]

    if plan.step is None:
        lines.append("Step      the timeline names no step after this version")
    else:
        position = (
            f"step {plan.step.ordinal} of {plan.total_steps}"
            if plan.step.ordinal is not None
            else f"between numbered steps ({STEP_SEPARATOR} on the timeline)"
        )
        lines.append(f"Step      {position}: {plan.step.label}")
    if plan.next_step is not None:
        lines.append(f"Next      {plan.next_step.label}")

    gate = plan.gate
    if gate is not None:
        entries = _plural(len(gate.entries), "entry", "entries")
        ids = _plural(len(gate.ids), "id", "ids")
        lines.append(f'Gate      recorded under "{gate.milestone.title}" ({entries}, {ids})')
        lines.append(f"          {len(gate.cleared)} cleared, {len(gate.outstanding)} open")
        if gate.outstanding:
            open_ids = [identifier for entry in gate.outstanding for identifier in entry.ids]
            lines.append(f"          {', '.join(open_ids)}")
        if gate.unknown_ids:
            lines.append(
                f"          not in the store, so not countable: {', '.join(gate.unknown_ids)}"
            )

    lines.append(f"Beat      {_beat_line(plan)}")
    if plan.problems:
        lines.append("")
        lines.append("The timeline table does not parse cleanly, so the step above may be wrong:")
        lines.extend(f"  {problem}" for problem in plan.problems)
    return "\n".join(lines)


def _release_advice(ready: Readiness, plan: Wave | None) -> str:
    """The digest's release sentence, once the roadmap has had its say.

    The mood of it is the point. `Readiness` is advisory by its own docstring,
    but this is the only line in the digest that tells a session to do
    anything - so where the plan disagrees it stops instructing rather than
    instructing more quietly, and hands the reader on to the beat printed
    directly beneath it.
    """
    offer = release_offer(ready, plan)
    if offer.kind == RESERVED:
        return (
            f"No release to offer: the roadmap gives {offer.version} to "
            f'"{offer.milestone}", which is unfinished - the beat below is what is due.'
        )
    if offer.kind == PLANNED:
        return (
            f"Offer {offer.version} before taking new work - the version the plan names, "
            f"not the {ready.suggested_version} a bump arrives at."
        )
    return f"Offer {offer.version} before taking new work."


def _beat_line(plan: Wave) -> str:
    """The beat, said as an instruction, with the count that makes it checkable."""
    if plan.beat == CLEAR and plan.gate is not None:
        remaining = _plural(len(plan.gate.outstanding), "entry", "entries")
        return f"clear the gate - {remaining} of {len(plan.gate.entries)} still open"
    if plan.beat == RELEASE:
        return f"release {plan.subject} - its gate is clear"
    if plan.beat == IMPLEMENT:
        return f"implement {plan.subject} - its gate is clear"
    if plan.beat == FREEZE:
        return f"freeze and record {plan.subject}'s debt list in its section"
    if plan.subject:
        return f"scope {plan.subject} here, which freezes its gate"
    return "scope the next milestone; the timeline names none after this version"


# One set of widths for the header and for every row, so the two cannot drift
# apart. A misaligned column here is not cosmetic: the reader is comparing
# three measures across three periods, which is exactly the reading a shifted
# column breaks.
_LABEL, _PAIR, _CROSS, _UNPLACED, _PCT, _WEIGHTED, _CHURN = 19, 9, 4, 4, 5, 9, 16


def _pct(share: float | None) -> str:
    """A share as whole percent, or a dash where there was nothing to divide."""
    return "-" if share is None else f"{share * 100:.0f}%"


def _lane_counts(counts: Mapping[str, int]) -> str:
    """Every lane named, including the ones at zero.

    A lane omitted for having nothing in it reads as a lane that does not
    exist, and the two easiest to drop - `crossing` and `unplaced` - are the
    ones a reader most needs told about, since neither `docket next product`
    nor `docket next workflow` will offer them.
    """
    return ", ".join(f"{counts.get(lane, 0)} {lane}" for lane in LANES)


def format_trend(report: Trend) -> str:
    """How the balance has moved, on three measures at once and with no verdict.

    The three are printed side by side rather than reduced to a headline,
    because each is wrong in a way the others are not - `trend.py`'s module
    docstring carries which. A single number here would be the tool guessing at
    the judgment half, which is the one thing it must not do.
    """
    if not report.periods:
        return "Nothing closed and no history to read: there is no trend yet."

    churn_width = _CHURN + _PCT if report.has_churn else 0
    lines = [
        f"{'':{_LABEL}}{'closed items':>{_PAIR + _CROSS + _UNPLACED + _PCT}}"
        f"{'weighted':>{_WEIGHTED + _PCT}}"
        + (f"{'churn (no queue)':>{churn_width}}" if report.has_churn else ""),
        f"{'period':<{_LABEL}}{'wf/prod':>{_PAIR}}{'+x':>{_CROSS}}{'+u':>{_UNPLACED}}"
        f"{'wf%':>{_PCT}}{'wf/prod':>{_WEIGHTED}}{'wf%':>{_PCT}}"
        + (f"{'appar./product':>{_CHURN}}{'wf%':>{_PCT}}" if report.has_churn else ""),
    ]
    for period in report.periods:
        closed, weighted = period.closed, period.weighted
        row = (
            f"{period.label:<{_LABEL}}"
            f"{f'{closed.get(LANE_WORKFLOW, 0)}/{closed.get(LANE_PRODUCT, 0)}':>{_PAIR}}"
            f"{closed.get(LANE_CROSSING, 0):>{_CROSS}}{closed.get(LANE_UNPLACED, 0):>{_UNPLACED}}"
            f"{_pct(period.closed_share):>{_PCT}}"
            f"{f'{weighted.get(LANE_WORKFLOW, 0)}/{weighted.get(LANE_PRODUCT, 0)}':>{_WEIGHTED}}"
            f"{_pct(period.weighted_share):>{_PCT}}"
        )
        if report.has_churn:
            pair = f"{period.apparatus_lines}/{period.product_lines}"
            row += f"{pair:>{_CHURN}}{_pct(period.churn_share):>{_PCT}}"
        lines.append(row)

    window = "day" if report.by == BY_DAY else "7-day period"
    ladder = ", ".join(f"{size}={points}" for size, points in EFFORT_POINTS.items())
    lines += [
        "",
        f"One row per {window}, anchored at the first day of the history. Three measures,",
        "because no one of them is honest alone:",
        "  wf/prod  items closed, by the lane their `touches` place them in.",
        "  +x       crossing: reaches both halves, so neither lane offers it.",
        "  +u       unplaced: declares no `touches`, so nothing can place it.",
        f"  weighted the same closures at {ladder} - a convention for reading past item",
        "           counts, not a measurement; an unsized item counts as one.",
    ]
    if report.has_churn:
        lines += [
            "  churn    lines added plus deleted, merges excluded. Read from what changed",
            "           rather than from what an item declared, so it still answers where",
            f"           `touches` is missing. {QUEUE.capitalize()} churn is left out of the",
            "           share: the store is inside workflow_paths, so every capture made",
            f"           while doing something else would count as {APPARATUS} work.",
            f"           Product churn is {', '.join(PRODUCT_BUCKETS)} together.",
        ]
    else:
        lines.append("  churn    not shown: git could not be read in this checkout.")

    lines += [
        "",
        f"{'Open now':<{_LABEL}}{_lane_counts(report.open_lanes)}",
        f"{report.top_band_name + ' band':<{_LABEL}}{_lane_counts(report.top_band)}",
    ]
    return "\n".join(lines)
