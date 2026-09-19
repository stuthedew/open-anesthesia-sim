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

from collections.abc import Collection, Mapping, Sequence
from datetime import UTC, date

from .checks import DONE_WHEN, HOUSEKEEPING, REQUIRED_BRIEF, STATUS_REQUIREMENTS, Report, brief_gaps
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
from .notes import Thread
from .plan import (
    PLACEMENT_MARKS,
    Feature,
    Gate,
    effort_total,
    placement_clause,
    placement_mark,
    recommend,
    set_aside,
)
from .release import PLANNED, RESERVED, Readiness, ReleaseOffer, release_offer
from .roadmap import CLEAR, FREEZE, IMPLEMENT, RELEASE, STEP_SEPARATOR, Scope, Wave
from .trend import APPARATUS, BY_DAY, EFFORT_POINTS, LANES, PRODUCT_BUCKETS, QUEUE, Trend
from .vcs import (
    CURRENT,
    LANDED,
    PULL,
    RESTART,
    REWRITTEN,
    BranchState,
    Carrier,
    CutsInFlight,
    FilingCommit,
    FilingReport,
    FlightReport,
    GitProfile,
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


def open_count(report: Report) -> int:
    """Every open item, the untriaged ones included.

    `Report.open_items` is the set that is a candidate for *work*, so it
    leaves out untriaged captures - which are candidates for a decision
    instead. That definition is right for `plan.py` and wrong for a number
    labelled "open": the two sets partition the open queue, so a count taken
    from `open_items` alone understates it by exactly the untriaged number
    printed beside it, and understates it most after a capture-heavy session
    (`PL-4WQS`).

    Public, and called from `cli.py` as well as from the three views here,
    because that is the whole of what `PL-ZWBK` was: `cmd_next` computed its
    own count from `open_items` and so printed a smaller number than `status`,
    `list` and the digest for one store. A count labelled "open" has one
    meaning in this tool, and it lives here rather than at each call site.
    """
    return len(report.open_items) + len(report.untriaged)


def _counts(report: Report) -> str:
    """The band breakdown, with untriaged as the band-less remainder.

    The bands sum to the triaged count, not to `open_count`, because an
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
    said = []
    # The whole-read decline first: a ref beyond a truncated clone's horizon is
    # ordinary, and git failing to answer is not, so the rarer fact leads
    # (`PL-Q9Z1`).
    if flight.declined:
        said.append(
            f"This reading is partial - {flight.declined} - so an item it does not "
            "mark may still be in flight."
        )
    if flight.unreadable:
        base = flight.base or "the default branch"
        them = "it" if len(flight.unreadable) == 1 else "them"
        said.append(
            f"{_plural(len(flight.unreadable), 'ref', 'refs')} could not be compared with {base} "
            f"on the history this checkout holds, so any item {'its' if them == 'it' else 'their'} "
            f"commits carry is missing here; `bin/docket flight` names {them}."
        )
    return " ".join(said)


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

    lines = [f"Docket: {open_count(report)} open - {_counts(report)}."]
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
    report: Report,
    flight: FlightReport,
    plan: Wave | None,
    workflow_paths: tuple[str, ...],
    generator_paths: tuple[str, ...] = (),
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
            generator_paths=generator_paths,
        )
        for lane in SELECTABLE_LANES
    }
    if not any(picks.values()):
        return ""
    scope = plan.scope if plan is not None else None

    def named_pick(lane: str) -> str:
        """`workflow PL-XZD0 (P2, not on the gate)` - the id, and why it ranked.

        The band and the gate relation, and deliberately not the title: this
        line is resident in every session's context, and two titles written
        for the session that will implement them would cost that context
        without answering the question the line is read for. The `Top:` line
        above already carries one title in full.

        A bare id was what this printed until `PL-Z27P`, which made the digest
        the first of two places naming a workflow item to the project owner
        with nothing saying why - "I don't know why it's selected"
        (2026-09-19). The id alone cannot distinguish a `P1` on the debt gate
        from a `P3` the roadmap places nowhere.
        """
        found = picks[lane]
        if not found:
            return f"{lane} none"
        item = found[0].item
        clause = placement_clause(scope, item.identifier)
        marks = f"{item.priority}, {clause}" if clause else item.priority
        return f"{lane} {item.identifier} ({marks})"

    named = ", ".join(named_pick(lane) for lane in SELECTABLE_LANES)
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
    generator_paths: tuple[str, ...] = (),
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

    lines = [f"Docket: {open_count(report)} open - {_counts(report)}."]
    for item in sorted(report.open_items, key=lambda i: i.sort_key()):
        if item.priority != "P0":
            continue
        lines.append(
            "  P0 (before feature work): "
            f"{item.identifier} {item.title} ({_marks(item, flight.ids)})"
        )

    picks = recommend(
        list(report.items),
        flight.ids,
        limit=1,
        scope=plan.scope if plan is not None else None,
        generator_paths=generator_paths,
    )
    top = picks[0] if picks else None
    if top is not None and top.item.priority != "P0":
        marks = _marks(top.item, flight.ids)
        # The one line every session reads before it has run anything. A
        # generator outranks every band but `P0`, so without this the digest
        # opens with a `P2` leading a queue that has `P1`s in it and nothing
        # saying the ranking meant it - which reads as a bug in `recommend`.
        if top.generator:
            marks += f", root cause of {top.generator} items - ranked above every band but P0"
        if top.impairs_generators:
            marks += ", defect in the generator machinery - ranked above every band but P0"
        if top.scoped_to:
            marks += f", scoped to {top.scoped_to}, not this step"
        lines.append(f"  Top: {top.item.identifier} {top.item.title} ({marks})")

    if lane_line := _by_lane(report, flight, plan, workflow_paths, generator_paths):
        lines.append(f"  {lane_line}")

    if flight.ids:
        # **Split on whether the default branch holds the item, because the
        # two halves want opposite advice** (`PL-3CTW`). A claim on an item the
        # base has no copy of is a capture commit's, nine times in ten, and the
        # item is in no session's store to be started - so refusing it refuses
        # work nobody was offered, about the branch the `stranded` line
        # directly below is telling the reader to recover it from. Neither
        # claim is withdrawn: that was measured at three widths and refused at
        # every one, per `Branch.on_base`.
        landed = sorted(branch.item_id for branch in flight.branches if branch.on_base)
        filed = sorted(branch.item_id for branch in flight.branches if not branch.on_base)
        if landed:
            lines.append(
                f"  In flight on a branch: {', '.join(landed)} - do not start these again."
            )
        if filed:
            lines.append(
                f"  Filed on a branch, not yet on {flight.base or 'the default branch'}: "
                f"{', '.join(filed)} - no copy here to start from; `bin/docket stranded` "
                "recovers it from the branch that claims it."
            )
    if unread := format_unread(flight):
        lines.append(f"  {unread}")
    if flight.unattributed:
        # Printed here, not only in `flight`, and with nothing suppressing it:
        # on 2026-09-14 no ref in this repository is unattributed and
        # `tools/branch_id_check.py` is what keeps it that way, so the steady
        # state is silence and a line means a ref genuinely nobody can name
        # (`PL-B73C`).
        lines.append(
            f"  Unlanded and attributable to no item: {', '.join(sorted(flight.unattributed))}. "
            "Nothing names it, so no guard here can see it - file an item or delete the branch."
        )
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
        if plan.stale:
            unparsed += " The plan's numbering is behind the project - check `wave`."
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
    if not report.known and not report.items:
        return f"Stranded items not checked: {report.declined}."

    # A partial read that still found something reports both. Printing only the
    # refusal would throw away a real finding, and printing only the finding
    # would present a partial reading as a complete one - and here the missing
    # half is items that exist on a branch and nowhere else (`PL-Q9Z1`).
    partial = [f"This reading is partial: {report.declined}.", ""] if report.declined else []

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
        *partial,
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
    if not report.known and not report.branches:
        return f"Work left on a merged branch not checked: {report.declined}."
    partial = [f"This reading is partial: {report.declined}.", ""] if report.declined else []

    # The count is of refs the default branch has *not* already taken whole,
    # which is a smaller number than `format_stranded` reports and a different
    # claim: a branch merged in full carries nothing to leave behind, so it is
    # excluded before this read begins rather than examined and cleared.
    refs = _plural(report.refs_read, "unmerged branch ref", "unmerged branch refs")
    if not report.branches:
        clear = f"No branch carries work its own pull request left behind, across the {refs} read."
        return "\n".join([clear, *_rewritten_lines(report)]) if report.rewritten else clear

    lines = [
        *partial,
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
    lines.extend(_rewritten_lines(report))
    return "\n".join(lines)


def _rewritten_lines(report: OrphanedReport) -> list[str]:
    """The refs this report set aside for sitting on duplicated history.

    Stated separately from the branches above and never folded in with them,
    because the two want opposite actions from a reader. A branch listed above
    has work to recover; one listed here matches the same content evidence for a
    reason that evidence cannot see - a rewrite changes every commit hash and no
    file - so what it needs is a look at the pull request rather than the
    deletion recipe, which on pre-rewrite history removes the only copy of the
    commits the ref carries (`PL-Y31G`).
    """
    if not report.rewritten:
        return []
    matched = _plural(len(report.rewritten), "branch ref matches", "branch refs match")
    return [
        "",
        f"{matched} that shape but diverges from the default branch by duplicated "
        "history, so file content cannot say whether it merged:",
        "",
        *report.rewritten,
        "",
        "Confirm against the pull request before deleting either ref: a branch left on "
        "pre-rewrite history holds the only copy of its own commits. `bin/docket branch` "
        "reports the rewrite and how to re-point the tags.",
    ]


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

    **`FlightReport.unattributed` is printed, and that is the opposite call for
    the opposite reason** (`PL-B73C`). A ref nobody can name fires on no run at
    all in the steady state - `tools/branch_id_check.py` refuses a `claude/*`
    branch of one's own that names none - so it is not an advisory firing every
    run, it is one firing only when something has escaped every guard this
    repository has. That is the reading the whole report is silent about
    otherwise: read perfectly well, and attributable to nothing.
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
            # `filed there` rather than a second table: the fact belongs to the
            # row it qualifies, and a reader scanning for their own id meets it
            # without being sent anywhere (`PL-3CTW`).
            mark = "" if branch.on_base else "  filed there"
            lines.append(
                f"{branch.item_id}  {branch.name:<{width}}  "
                f"{_since(branch.last_commit, today)}{mark}"
            )
        lines.append("")
        lines.append(
            "A live session and a branch nobody will merge look the same here; "
            "the age is what separates them."
        )
        if any(not branch.on_base for branch in report.branches):
            lines.append(
                "An item marked `filed there` is not in this checkout's queue at all: that "
                "branch holds the only copy, and `bin/docket stranded` recovers it."
            )
    else:
        # Stated as the conclusion rather than as a fact about subjects
        # (`PL-VYSP`): a capture leads with an id and claims nothing, and a
        # claim the base has since taken or closed is removed above, so "no
        # commit leads with an id" was false whenever either existed.
        lines.append(
            "No branch claims an item. No branch carries an item id in its name, and no "
            "commit subject claims one that the default branch has not already taken or "
            "closed."
        )

    if report.unattributed:
        lines.append("")
        lines.append(
            f"{_plural(len(report.unattributed), 'ref carries', 'refs carry')} no item id, in "
            "the name or at the front of any commit, so no guard in this repository can see "
            f"{'it' if len(report.unattributed) == 1 else 'them'}:"
        )
        lines.extend(f"  {name}" for name in report.unattributed)

    if report.declined:
        lines.append("")
        lines.append(f"This reading is partial: {report.declined}.")
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


def format_generators(heads: Sequence[Item]) -> str:
    """That a generator above this item explains it, and what a session owes that.

    `root-cause-of:` is recorded on the head alone, so `show` on a *member*
    said nothing about it: a session handed a member's id - the way the
    project owner usually starts one - worked it as an ordinary item while the
    generator above it was still being decided (`PL-C97K`).

    **The consequence is what the line is for, not the edge.** `CLAUDE.md`
    pulls a root cause rather than queueing it, so the head's decision can
    re-scope or drop the member underneath it; a pointer that stopped at
    naming the head would read as provenance - interesting, and not a reason
    to go and read something before starting.

    How many items each head names is printed because it is the size of the
    cluster this one belongs to, which is what separates a small regrouping
    above from a re-scoping of two dozen items. Counted over distinct ids, as
    `root_cause_faults` counts them, so the number here and the number the
    checker holds the claim to cannot differ.

    The head's status comes with it for the same reason: a head still open is
    a decision pending, and a head already `done` or `dropped` asks the
    opposite question - whether this member still reproduces at all.
    """
    head_word = "a generator" if len(heads) == 1 else f"{len(heads)} generators"
    closing = (
        "Read it before starting: its decision can re-scope or drop this item."
        if len(heads) == 1
        else "Read them before starting: their decisions can re-scope or drop this item."
    )
    lines = [f"  Explained by {head_word} - a root cause is fixed at its head, not here:"]
    for head in heads:
        named = _plural(len(set(head.root_cause_of)), "item", "items")
        lines.append(
            f"    {head.identifier} ({head.status}) root cause of {named} - {_gloss(head.title)}"
        )
    lines.append(f"    {closing}")
    return "\n".join(lines)


def format_notes_threads(threads: Sequence[Thread], identifier: str, notes_path: str) -> str:
    """Which notes threads concern this item, as a pointer rather than a summary.

    A file:line for each, so the read is one jump rather than a scan, and the
    title so a session can skip a thread it already knows. Nothing about what
    the thread says: whether it is still true is the judgment this deliberately
    leaves with the reader, and a generated precis of a stale thread would be
    read as current (`PL-7QKY`).

    Threads the heading names are what the thread is *about*; the rest mention
    the id in passing and are marked as such, because a session with a budget
    should be able to tell which pointer is the one to follow.
    """
    lines = [f"  notes: {len(threads)} thread(s) in {notes_path} name {identifier}"]
    for thread in threads:
        about = "about" if identifier in thread.about else "mentions"
        lines.append(f"    {notes_path}:{thread.line} ({about}) {thread.title}")
    lines.append("    Whether a thread is still true is not something this can tell you.")
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
    if order.declined:
        # Louder than the unreadable line below, because this one breaks the
        # guarantee the order rests on: two sessions can only compute the same
        # answer from the same evidence, and a silence gives them different
        # evidence (`PL-Q9Z1`).
        lines.append(
            f"  (This ordering is partial - {order.declined} - so the other session "
            "may be computing a different one. Do not stand down on it.)"
        )
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
    elif state.disposition == LANDED:
        lines.append(f"Branch: {branch} is {state.behind} behind {base} and {state.ahead} ahead.")
        lines.append(
            f"  Those commits are not work {base} is waiting for: it already holds a whole "
            "commit of this branch, so its pull request merged."
        )
        lines.append("  Nothing merges a merged pull request again, so do NOT merge and push.")
        lines.append("  Restart on the merged base and carry anything of your own forward:")
        lines.append(f"  git fetch origin main && git checkout -B {branch} {base}")
        lines.append(f"  Check what only this branch holds first: git diff {base}...HEAD")
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


def format_triage(
    report: Report,
    config: Config,
    flight: FlightReport | None = None,
    filed: FilingReport | None = None,
) -> str:
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
    filed = filed or FilingReport()
    filings = filed.filings if filed.known else {}
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
        if filing := filings.get(item.identifier):
            lines.extend(_filed_with_work(filing))
        lines.append(f"  unset: {_unset(item)}")
        missing, empty, stub = brief_gaps(item.body, housekeeping=HOUSEKEEPING in item.classes)
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
    if filed.declined:
        lines.append("")
        lines.append(
            f"Not checked: which commit filed each item - {filed.declined}. So no item "
            "below carries the mark that its filing commit also changed code."
        )
    return "\n".join(lines)


def _filed_with_work(filing: FilingCommit) -> list[str]:
    """Point at the commit that filed this item, where that commit also changed code.

    **A pointer, never a verdict**, and the wording carries that on its face:
    it says what the commit changed and asks for a read, rather than saying the
    item has landed. `PL-SWP3` measured every key that would license the
    stronger sentence and none survived - whether such a commit *finished* the
    item it filed is a relation between intent and diff, so the reader is the
    only thing here that can decide it.

    Three paths at most. `PL-YNYK`'s filing commit changed 25, and a wall of
    them buries the two rows on the list that are worth opening.
    """
    where = f"{filing.commit[:7]}"
    if (number := filing.pull_request) is not None:
        where += f" (#{number})"
    shown = ", ".join(filing.paths[:3])
    if len(filing.paths) > 3:
        shown += f", and {len(filing.paths) - 3} more"
    return [
        f"  Filed by {where}, which also changed {shown}.",
        "  That commit both filed this item and changed code, so its work may already",
        "  be on the default branch - read the diff before triaging this as live work.",
    ]


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
    if HOUSEKEEPING in config.vocabulary():
        rules.append(
            f"an item classed `{HOUSEKEEPING}` - a pass whose work *is* the queue "
            f"edit - needs {REQUIRED_BRIEF[0]} only, and still needs its `verify:`. "
            "It may not carry a debt class as well. Stated here because this is "
            "where the cost is paid: the exemption is no use to a session that "
            "meets it after writing the brief."
        )
    # Last, and from `checks.py`'s own table rather than restated here: these
    # fire only for the status the pass chooses, so they read as the conditions
    # on the choice just after the rules that apply to every item (`PL-F4JS`).
    rules.extend(rule for _, rule in STATUS_REQUIREMENTS)
    return rules


def progress_mark(item: Item) -> str:
    """The checkbox a progress listing draws for one item.

    Three marks rather than two, because the two figures printed above such a
    listing are counted by two different rules: the numerator is `status ==
    "done"` and the "N left" is `is_open`, and a `dropped` item is in neither. It
    was drawn `[ ]`, so `bin/docket feature teachable-case` printed "18/28 done
    (9 left)" above ten empty boxes, and a reader counting them to check the
    number got the wrong answer with no way to tell which of the two was lying
    (`PL-VFVW`).

    With `[-]` for dropped, counting reproduces both figures and the total is the
    denominator: `[x]` is the numerator, `[ ]` is what is left, every line is a
    member.
    """
    if item.status == "done":
        return "x"
    if item.is_open:
        return " "
    return "-"


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
        f"docket: {open_count(report)} open ({_counts(report)}), "
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
    scope = plan.scope if plan is not None else None
    # First-use order, so the legend reads in the order the marks are met.
    used: dict[str, None] = {}

    def placed(identifier: str) -> str:
        """The plan's mark for one id, recorded so the legend can define it."""
        mark = placement_mark(scope, identifier)
        if not mark:
            return ""
        used.setdefault(mark, None)
        return f" {mark}"

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
        return (
            f"next: {item.identifier}{placed(item.identifier)} {item.title} ({item.effort}){mark}"
        )

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
            lines.append(
                f"  {item.priority} {item.identifier}{placed(item.identifier)} "
                f"{item.title} ({item.effort}{note})"
            )

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
            lines.append(f"  {_reserved_refusal(offer, '`docket wave` for what is due')}")
        else:
            lines.append(f"  Next version would be {offer.version}.")
    if unread := format_unread(flight):
        lines.append("")
        lines.append(unread)
    return "\n".join(_plan_header(scope, tuple(used)) + lines)


def _plan_header(scope: Scope | None, used: tuple[str, ...]) -> list[str]:
    """Which step the survey below belongs to, and what its marks mean.

    Two lines, and the second is why the first exists. `format_status` is what
    the queue skill tells a session to lead with, and it ranked `numerical-domain`
    beside `delegation` with nothing saying which of them the current step
    included - a survey that cannot be read against the plan without running a
    second command (`PL-BZCM`).

    The legend defines only the marks actually drawn, plus the blank. Defining
    the blank is the load-bearing half: an unmarked row would otherwise be
    indistinguishable from one nobody looked at, which is the silence `PL-J790`
    named in `docket next`'s reason lines and fixed there with a sentence. A
    sentence per row does not fit two dozen of them, so the legend carries it
    once instead.
    """
    if scope is None or not scope.anchor:
        return []
    # The anchor and the row the project stands on are two facts, and the
    # header called the anchor "the step the project is on" while `wave` named
    # another row as the step - the same session read both, minutes apart, and
    # `docket next` had already been taught the distinction (`PL-B5DW`). So the
    # row is named apart from the anchor whenever `Scope` carries it.
    if scope.clearing:
        beat = f"clearing the debt gate recorded under {scope.anchor}"
    elif scope.step_label:
        beat = f"{scope.anchor}, the milestone due next"
    else:
        beat = f"{scope.anchor}, the step the project is on"
    if scope.step_label:
        beat += f"; the project stands on {scope.step_label}"
    glosses = [
        f"{mark} {PLACEMENT_MARKS.get(mark, 'placed by that later milestone')}" for mark in used
    ]
    glosses.append("unmarked, no section of the roadmap places the id")
    return [f"Plan: {beat}.", f"      {'; '.join(glosses)}.", ""]


def format_wave(plan: Wave) -> str:
    """Where the project stands on the cadence, and nothing about whether it should.

    A labelled line per fact and no more, because this is read at the top of a
    session beside the digest, not studied. Each one states a fact with the
    file it came from behind it; none of them says whether the plan is still
    the right plan.
    """
    lines = [f"Version   {plan.version or 'unknown'}"]
    if plan.reserved:
        # Versions without their milestone names, which is the whole payload
        # here: the question this line answers is "which numbers are spoken
        # for", and the name of the one a bump actually collides with is
        # already printed by the refusal that sends a reader to this command.
        # Six names would not fit a line, and the set is what was missing -
        # `reserved` did not occur in this module at all, so a session could
        # read the guard's verdict on one version and nothing about the rest
        # (`PL-C6XD`).
        #
        # A number's absence from this list is not a statement that it is
        # cuttable, and nothing here says otherwise: this reports where the
        # plan has spent its numbers, never whether a cut should take a free
        # one. Stepping over a reservation drops the skipped milestone's
        # section out of the train's unreleased set; whether a cut may do that
        # is a judgment for the reader and `PL-SYG4`'s open question, and the
        # stale block at the foot of this output is what reports it done.
        spent = ", ".join("{}.{}.{}".format(*entry.version) for entry in plan.reserved)
        lines.append(f"Reserved  {spent} - spent by ROADMAP.md, nearest first")

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
        counted = f"{len(gate.cleared)} cleared, {len(gate.outstanding)} open"
        # The three sets are disjoint by construction, so the split adds back up
        # to the open count and a reader can check it without being told to.
        aside = []
        if gate.self_cleared:
            aside.append(f"{len(gate.self_cleared)} the milestone clears itself")
        # Two verdicts where there was one, and the wording is the deliverable:
        # an entry the plan sequences ahead of the gate needs nothing from
        # anybody, an entry waiting on work placed later or nowhere is excused
        # until somebody decides otherwise, and printed as one line the second
        # hid behind the first (`PL-7CSP`). Neither is counted as clearable.
        if gate.sequenced_ahead:
            aside.append(f"{len(gate.sequenced_ahead)} sequenced ahead of it")
        if gate.waiting_outside:
            aside.append(f"{len(gate.waiting_outside)} waiting on work outside it")
        if aside:
            counted += f" - {len(gate.clearable)} this gate can clear, " + ", ".join(aside)
        lines.append(f"          {counted}")
        if gate.clearable:
            open_ids = [identifier for entry in gate.clearable for identifier in entry.ids]
            lines.append(f"          {', '.join(open_ids)}")
        if gate.self_cleared:
            own = [identifier for entry in gate.self_cleared for identifier in entry.ids]
            lines.append(f"          cleared by the milestone itself: {', '.join(own)}")
        by_row: dict[str, list[str]] = {}
        for sequenced in gate.sequenced_ahead:
            by_row.setdefault(sequenced.row, []).extend(sequenced.entry.ids)
        for row, waiting_on_row in by_row.items():
            lines.append(
                f"          sequenced ahead of the gate, on {row}: {', '.join(waiting_on_row)}"
            )
        if gate.waiting_outside:
            held = [identifier for entry in gate.waiting_outside for identifier in entry.ids]
            lines.append(f"          blocked outside the gate: {', '.join(held)}")
        if gate.unknown_ids:
            lines.append(
                f"          not in the store, so not countable: {', '.join(gate.unknown_ids)}"
            )

    lines.extend(_scope_lines(plan))
    lines.append(f"Beat      {_beat_line(plan)}")
    if plan.problems:
        lines.append("")
        lines.append("The timeline table does not parse cleanly, so the step above may be wrong:")
        lines.extend(f"  {problem}" for problem in plan.problems)
    if plan.stale:
        lines.append("")
        lines.append("The plan and the project disagree, so the beat above rests on a stale plan:")
        lines.extend(f"  {statement}" for statement in plan.stale)
    return "\n".join(lines)


def _scope_lines(plan: Wave) -> list[str]:
    """The gated milestone's own `Required scope`, counted - once the gate is clear.

    Withheld while the gate is open, deliberately. `format_wave`'s budget is a
    few lines read beside the digest rather than studied, and while the beat is
    `clear` the gate block above already says what is due; the scope is work the
    step has not reached, which `docket next` marks per item. Once the gate
    clears, the scope *is* the remaining question - `implement` or `release`
    turns on nothing else - and this is the count that makes the beat checkable,
    the same job the gate's own split does above it (`PL-KD98`).
    """
    own = plan.own_scope
    if own is None or not own.ids or plan.beat not in (IMPLEMENT, RELEASE):
        return []
    lines = [
        f"Scope     the Required scope of {own.milestone.label} "
        f"({_plural(len(own.ids), 'id', 'ids')})",
        f"          {len(own.closed)} closed, {len(own.outstanding)} open",
    ]
    if own.outstanding:
        lines.append(f"          {', '.join(own.outstanding)}")
    if own.unknown_ids:
        lines.append(f"          not in the store, so not countable: {', '.join(own.unknown_ids)}")
    return lines


def _reserved_refusal(offer: ReleaseOffer, pointer: str) -> str:
    """The one sentence both release surfaces say when the plan owns the number.

    `format_status` and `_release_advice` each branched on `offer.kind` and
    each wrote their own refusal, so a change to either left the other saying
    the old thing - one verdict with two independent readers, which is the
    shape `PL-VFD8` had just been through one layer down inside the guard
    itself (`PL-C6XD`).

    The pointer is the argument because it is the only part either surface is
    entitled to differ on. The digest prints the beat directly beneath this
    line and can say so; the survey does not, so it names the command that
    would print it. Sending the digest's reader to `docket wave` for what is
    already on the next line would be prose restating what a command prints,
    which is the bloat `.claude/rules/apparatus-standard.md` cuts.
    """
    return (
        f'No release to offer: the roadmap gives {offer.version} to "{offer.milestone}", '
        f"which is unfinished - {pointer}."
    )


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
        return _reserved_refusal(offer, "the beat below is what is due")
    if offer.kind == PLANNED:
        return (
            f"Offer {offer.version} before taking new work - the version the plan names, "
            f"not the {ready.suggested_version} a bump arrives at."
        )
    return f"Offer {offer.version} before taking new work."


def _beat_line(plan: Wave) -> str:
    """The beat, said as an instruction, with the count that makes it checkable."""
    if plan.beat == CLEAR and plan.gate is not None:
        remaining = _plural(len(plan.gate.clearable), "entry", "entries")
        line = f"clear the gate - {remaining} of {len(plan.gate.entries)} still open"
        aside = []
        if plan.gate.self_cleared:
            aside.append(f"{len(plan.gate.self_cleared)} the milestone clears itself")
        if plan.gate.sequenced_ahead:
            aside.append(f"{len(plan.gate.sequenced_ahead)} sequenced ahead of it")
        if plan.gate.waiting_outside:
            aside.append(f"{len(plan.gate.waiting_outside)} blocked outside it")
        if aside:
            line += " here, " + ", ".join(aside)
        return line
    if plan.beat == RELEASE:
        # Three arrangements reach this beat and they are released for
        # different reasons, so the clause has to say which. A gate shipping as
        # its own earlier version, or a milestone whose frozen list is its whole
        # content, is released because the gate cleared; a milestone with a
        # scope of its own is released because that scope closed too, and
        # saying only "its gate is clear" of it would name the smaller half of
        # what the reader is being asked to act on (`PL-KD98`).
        cleared = _gate_clause(plan)
        if plan.own_scope is not None and plan.own_scope.is_complete:
            closed = _plural(len(plan.own_scope.ids), "Required scope id", "Required scope ids")
            return f"release {plan.subject} - {cleared} and all {closed} have closed"
        return f"release {plan.subject} - {cleared}"
    if plan.beat == IMPLEMENT:
        cleared = _gate_clause(plan)
        if plan.own_scope is not None and plan.own_scope.ids:
            left = len(plan.own_scope.outstanding) + len(plan.own_scope.unknown_ids)
            return (
                f"implement {plan.subject} - {cleared}, "
                f"{len(plan.own_scope.closed)} of {len(plan.own_scope.ids)} "
                f"Required scope ids closed and {left} still open"
            )
        return f"implement {plan.subject} - {cleared}"
    if plan.beat == FREEZE:
        return f"freeze and record {plan.subject}'s debt list in its section"
    if plan.subject:
        return f"scope {plan.subject} here, which freezes its gate"
    return "scope the next milestone; the timeline names none after this version"


def _gate_clause(plan: Wave) -> str:
    """Whose gate cleared, where the beat's milestone is not the one that recorded it.

    A section-bearing `—` row between a clear gate and the milestone that
    recorded it is the beat's work while its scope is open, and it takes no gate
    of its own - the Qt port sits between Gate 1 and v0.5.0 exactly so
    (`PL-FWJF`). "Its gate is clear" of such a row would name a gate it does not
    have, so the clause says which milestone's gate it was.
    """
    gate = plan.gate
    if (
        gate is not None
        and plan.milestone is not None
        and plan.milestone.version != gate.milestone.version
    ):
        return f"the timeline puts it before {gate.milestone.label}, whose gate is clear"
    return "its gate is clear"


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


def format_git_profile(profile: GitProfile) -> str:
    """What a command asked git, next to the ref set it asked about.

    **The ref set is not an extra, and printing the counts without it is the
    defect this exists to remove** (`PL-XD3C`). Two machines were once compared
    at 220 git calls against 1,107, and three different scaling laws were fitted
    to that ratio and refuted in one sitting - because the two counts had been
    taken against different ref sets, hours apart, while other sessions pushed
    branches. A count is a measurement only beside its input, so the input is
    printed with it and two machines can be compared by subtracting their
    columns instead of dividing their totals.

    `asked` is what the module wanted to know and `ran` is what reached git;
    they differ by what the memo answered. `procs` counts the subprocesses
    actually created, which is below `ran` by every blob the `cat-file` batch
    served.
    """
    walk = profile.walk
    # `asked` is what this command would have spawned before the memo and the
    # blob batch existed - every read was one process - so a single profiled run
    # carries its own before-and-after and neither number has to be taken on a
    # different commit, a different machine, or a different ref set.
    saved = profile.asked - profile.processes
    share = f" ({100 * saved // profile.asked}% fewer)" if profile.asked else ""
    lines = [
        f"git: {profile.asked} asked, {profile.ran} ran, {profile.processes} processes, "
        f"{profile.seconds:.2f}s",
        f"  {saved} fewer processes than one-per-read{share}: the memo answered "
        f"{profile.saved}, the blob batch folded {profile.ran - profile.processes}",
        f"  {'sub':<14}{'asked':>7}{'ran':>6}{'distinct':>10}{'seconds':>9}",
    ]
    for cost in profile.by_subcommand:
        lines.append(
            f"  {cost.subcommand:<14}{cost.asked:>7}{cost.ran:>6}"
            f"{cost.distinct:>10}{cost.seconds:>8.2f}s"
        )
    if walk.declined:
        lines.append(f"  ref set: not read - {walk.declined}")
        return "\n".join(lines)
    lines += [
        "",
        f"  ref set: {walk.listed} refs, {walk.merged} merged, {walk.unmerged} unmerged, "
        f"carrying {walk.commits} commits and {walk.item_edits} item-file edits",
    ]
    lines += [
        f"    {name:<52}{ahead:>5} commits{edits:>5} items" for name, ahead, edits in walk.refs
    ]
    return "\n".join(lines)
