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

from collections.abc import Collection, Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, timedelta

from .checks import DONE_WHEN, HOUSEKEEPING, REQUIRED_BRIEF, STATUS_REQUIREMENTS, Report, brief_gaps
from .claims import CLAIM, DISPOSITION, LEASE_TERM, LIVE, NAMED, Hold, Holdings, Unclaimed
from .concurrency import undeclared
from .config import Config
from .duplicates import Candidate
from .model import (
    CLOSED_STATUSES,
    LANE_CROSSING,
    LANE_PRODUCT,
    LANE_UNPLACED,
    LANE_WORKFLOW,
    MIN_RECURRENCES,
    PRIORITIES,
    SELECTABLE_LANES,
    Item,
    live_recurrences,
    recurrence_count,
    recurrences_of,
    split_deferred_from,
    split_generator_verdict,
)
from .notes import Thread
from .plan import (
    HELD,
    PLACEMENT_MARKS,
    Cluster,
    Feature,
    Gate,
    Overlap,
    Standing,
    effort_total,
    placement_clause,
    placement_mark,
    recommend,
    recurring,
    set_aside,
)
from .release import (
    NOTES_DIR,
    PLANNED,
    RESERVED,
    Readiness,
    ReleaseOffer,
    notes_name,
    release_offer,
)
from .roadmap import CLEAR, FREEZE, IMPLEMENT, RELEASE, STEP_SEPARATOR, GateStatus, Scope, Wave
from .trend import APPARATUS, BY_DAY, EFFORT_POINTS, LANES, PRODUCT_BUCKETS, QUEUE, Trend
from .vcs import (
    CURRENT,
    LANDED,
    PULL,
    RESTART,
    REWRITTEN,
    BranchState,
    CutsInFlight,
    FilingCommit,
    FilingReport,
    FlightReport,
    GitProfile,
    OpenPullRequests,
    OrphanedReport,
    QueueEdit,
    RewriteReport,
    SettledReport,
    SinceFiled,
    StrandedReport,
    TouchedPath,
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
    its item, `claims.holdings` holds that id by the name anyway - a name
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
    lines = [f"By lane, for a second session: {named}{spanning}."]
    # Each pick's payoff below the line rather than inside it, and the id
    # repeated because two picks are named above. This is the offer the
    # project owner has no other way to judge - a workflow item's title
    # describes a mechanism they have no opinion about, where a simulator
    # item's describes something they do - so leaving the field out of the
    # one place that names the workflow pick would miss the case it was
    # built for. A pick with no payoff adds no line.
    for lane in SELECTABLE_LANES:
        found = picks[lane]
        if found and found[0].item.payoff:
            lines.append(f"    {found[0].item.identifier} payoff: {found[0].item.payoff}")
    return "\n".join(lines)


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
    protected_paths: tuple[str, ...] = (),
    gate_paths: tuple[str, ...] = (),
    now: datetime | None = None,
    read: Holdings | None = None,
    interrupted: str = "",
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

    `read` adds each in-flight id's state and kind (`held_as`, `PL-N162`),
    because five triage passes' status dispositions otherwise read exactly
    like a session's claim.

    `interrupted` names a release whose cut stopped before its notes, and
    replaces the release sentence with `_interrupted_cut`'s (`PL-1BS2`).
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
            f"{item.identifier} {item.title} "
            f"({_marks(item, flight.ids, protected_paths, gate_paths)})"
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
        marks = _marks(top.item, flight.ids, protected_paths, gate_paths)
        # The one line every session reads before it has run anything. A
        # generator outranks every band but `P0`, so without this the digest
        # opens with a `P2` leading a queue that has `P1`s in it and nothing
        # saying the ranking meant it - which reads as a bug in `recommend`.
        if top.generator:
            marks += f", root cause of {top.generator} items - ranked above every band but P0"
        if top.impairs_generators:
            marks += ", defect in the generator machinery - ranked above every band but P0"
        if top.unblocks:
            marks += (
                f", unblocks generator {', '.join(top.unblocks)} - ranked above every band but P0"
            )
        if top.unblocks_defects:
            marks += (
                f", unblocks machinery defect {', '.join(top.unblocks_defects)}"
                " - ranked above every band but P0"
            )
        if top.scoped_to:
            marks += f", scoped to {top.scoped_to}, not this step"
        lines.append(f"  Top: {top.item.identifier} {top.item.title} ({marks})")
        # The one item every session is shown before it has run anything, so
        # it is the highest-value place in the store for this line and the
        # only one worth a second line of resident context. Printed only
        # where the item carries one, so a store that has not adopted the
        # field pays nothing.
        if top.item.payoff:
            lines.append(f"    payoff: {top.item.payoff}")

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
        landed = sorted(
            (branch for branch in flight.branches if branch.on_base),
            key=lambda branch: branch.item_id,
        )
        filed = sorted(branch.item_id for branch in flight.branches if not branch.on_base)
        if landed:
            # **What the branches hold and how long each has sat, not an order**
            # (`PL-7TVT`). This line ended "do not start these again", which
            # presumes a session behind every branch, and a branch outlives its
            # session: PR `#757`'s three items read that way for 25 minutes
            # after its session was archived. An age is what the refs can back,
            # so the line carries one per item, and names the command that adds
            # the pull request - which the digest does not ask the forge for,
            # because it runs on every session start and must answer offline.
            if now is None:
                named = ", ".join(
                    f"{branch.item_id}{held_as(branch.item_id, read)}" for branch in landed
                )
                lines.append(
                    f"  In flight on a branch: {named}. A branch outlives its session, so this "
                    "is not proof anybody is on one; `bin/docket flight` has each one's age "
                    "and pull request."
                )
            else:
                named = ", ".join(
                    f"{branch.item_id} {_digest_age(branch.last_commit, now)}"
                    f"{held_as(branch.item_id, read)}"
                    for branch in landed
                )
                lines.append(
                    f"  In flight on a branch, by time since its last commit: {named}. A branch "
                    "outlives its session, so an age is not proof anybody is on it; "
                    "`bin/docket flight` adds each one's pull request."
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
    # Silent until a defect has been filed three times, which is the only state
    # it says anything about - so it costs nothing on the turns it is not true,
    # and on the turn it is, it is the one line naming evidence no session
    # asserted (`PL-X5JR`). Passed the flight ids because a promotion only
    # moves a queue position, and an item already on a branch has no position
    # left to move (`PL-CJ5R`).
    repeats = recurring(report.items, flight.ids)
    if repeats:
        named = ", ".join(f"{item.identifier} ({recurrence_count(item)})" for item in repeats[:3])
        rest = f", +{len(repeats) - 3} more" if len(repeats) > 3 else ""
        lines.append(
            f"  Filed more than once, never promoted for it: {named}{rest}. "
            "A generator tier candidate a reader confirms; `bin/docket show <id>`."
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
    if interrupted:
        lines.append(f"  Releasable: {_interrupted_cut(report, ready, interrupted)}")
    elif ready is not None and ready.is_worth_cutting:
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
        #
        # A holder with no versions has claimed the release train and cut
        # nothing yet, which is the same answer arriving earlier (`PL-331V`).
        held = [branch for branch in (cuts.branches if cuts else ()) if not branch.mine]
        cutting = ", ".join(
            f"{branch.ref} (v{', v'.join(branch.versions)})" for branch in held if branch.versions
        )
        said = [f"A release is already being cut on {cutting}"] if cutting else []
        said.extend(
            f"{branch.item} holds the release train, nothing cut yet ({branch.ref})"
            for branch in held
            if not branch.versions
        )
        advice = (
            "; ".join(said) + "; do not offer another until it merges."
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
            # The short form of `format_wave`'s own heading over the same
            # statements, and the same words, because `Wave.stale` carries five
            # kinds and only four are a numbering behind the project: the
            # fifth is a section no timeline row bears, where the plan places
            # nothing rather than placing it late (`PL-DK8Y`). A reader told
            # the numbering is behind goes and reads the timeline's numbers,
            # which is the wrong file for that one.
            unparsed += (
                " The plan and the project disagree, so the beat rests on a"
                " stale plan - check `wave`."
            )
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
    reads off the same output: a branch named nowhere below carries no item
    missing from both the default branch and this checkout's store.

    **Both halves of that predicate are printed, in the finding case and the
    empty one** (`PL-Z6M3`). `vcs.stranded` leaves out what the store holds so
    that a session is not told about its own capture, and that also silences
    the session that has just recovered a stranded item: its checkout now holds
    the item while the default branch still lacks it. A sentence naming only
    the default branch told that session the hole was closed.

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

    **The second section is handed a diff and never a checkout**, and that is
    the whole difference between the two. An item reported above is one the
    default branch does not hold, so restoring the branch's copy overwrites
    nothing; an item reported below is one it *does* hold, so the same command
    would discard whatever the base has recorded on it since - which is what
    `PL-THPB` was offered and `PL-XLQ5` was actually dealt (`PL-MBTZ`,
    `PL-KSCW`).
    """
    if not report.known and not report.items and not report.edits:
        return f"Stranded items not checked: {report.declined}."

    # A partial read that still found something reports both. Printing only the
    # refusal would throw away a real finding, and printing only the finding
    # would present a partial reading as a complete one - and here the missing
    # half is items that exist on a branch and nowhere else (`PL-Q9Z1`).
    partial = [f"This reading is partial: {report.declined}.", ""] if report.declined else []

    refs = _plural(report.refs_read, "branch ref", "branch refs")
    if not report.items:
        lines = [
            *partial,
            "No item exists only on a branch and outside this checkout's store, "
            f"across the {refs} this checkout holds.",
            "An item in this checkout's store is not listed even where the default branch "
            "lacks it, and a branch not fetched here was not read, so this is bounded by both.",
            *_stale_base(report),
        ]
        return "\n".join([*lines, *_edited_lines(report)])

    lines = [
        *partial,
        f"{_plural(len(report.items), 'item exists', 'items exist')} only on a branch "
        f"and outside this checkout's store, across the {refs} this checkout holds:",
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
    lines.append(
        "Every other branch read carries no item missing from both the default branch "
        "and this checkout's store."
    )
    return "\n".join([*lines, *_edited_lines(report)])


def _edited_lines(report: StrandedReport) -> list[str]:
    """Items the default branch holds whose branch copy is ahead of it, or nothing.

    Its own section rather than more rows above, because the reader has to do
    something different with it. Above, the recovery is a file the base does
    not have; here it is a *diff*, and the reader decides what of it to carry
    across - a section appended to a brief is usually wanted whole, a field
    edited on both sides is a merge nobody should make from a command line.
    No `git checkout` is printed at all, which is the point of the separation
    (`PL-KSCW`, `PL-MBTZ`).

    The diff names both blobs rather than a pathspec, because a retitle
    renames the file: `git diff <base> <ref> -- <path>` compares the ref's copy
    against nothing at all when the base holds the item under its old name.

    Silence about the branch's liveness, deliberately, the same way the
    section above is silent: a live session editing its own item and an
    abandoned branch holding the only copy of a finding look identical here,
    and no timeout tells them apart. The session's own copy is the one case
    that is answered - `stranded` drops an edit whose blob `HEAD` also holds,
    so what remains is somebody else's.
    """
    if not report.edits:
        return []
    held = _plural(len(report.edits), "item", "items")
    lines = ["", f"{held} the default branch holds, edited only on a branch:", ""]
    for edit in report.edits:
        lines.append(f"{edit.identifier}  {edit.title or '(title unreadable)'}")
        lines.append(f"  edited on: {', '.join(edit.branches)}")
        lines.append(
            f"  read: git diff {report.base}:{edit.base_path} {edit.branches[0]}:{edit.path}"
        )
        lines.append("")
    lines.append(
        "A diff rather than a recovery command: the default branch holds a copy of its own, "
        "and restoring the branch's over it discards whatever landed since."
    )
    return lines


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
        # The commits, replayed, rather than a checkout of their files: a
        # checkout writes the branch's whole copy over whatever the base has
        # changed in that file since, which is a silent revert (`PL-GHHW`).
        # A cherry-pick applies only the change, and stops on a conflict.
        # Oldest first, since they are listed newest first.
        picks = " ".join(commit.commit[:9] for commit in reversed(branch.commits))
        lines.append(f"  recover: git cherry-pick {picks}")
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


#: How far a commit may be dated past this clock's "now" and still read as
#: just made. Two machines' clocks disagree by seconds, and a session's own
#: commit read back a moment later should not be reported as a clock fault.
_CLOCK_SLACK = timedelta(minutes=1)


def _age(last_commit: datetime, now: datetime) -> str | None:
    """How long ago a commit was made, in the one unit its size calls for.

    **Elapsed time, not calendar days** (`PL-3QM9`). Subtracting two dates
    counted the midnights crossed rather than the time passed, so a branch
    committed 55 minutes ago read "1 day ago" from 00:00 onward - wrong in the
    direction that reads a live session as abandoned, and worst for the
    freshest branches, which are the ones a reader most needs to place.

    The unit grows with the age because the question changes with it: in the
    first hour a session is live or it is not and minutes are what separate
    the two, while nobody deciding about a week-old branch needs its hours.
    Each is rounded down, which reports a branch as younger than it is rather
    than older - the direction every reading here fails in, since a live
    session taken for abandoned work is the costly mistake.

    `None` for a commit dated after `now` by more than two clocks disagree,
    which no age describes.
    """
    elapsed = now - last_commit
    if elapsed < -_CLOCK_SLACK:
        return None
    minutes = max(elapsed, timedelta(0)) // timedelta(minutes=1)
    if minutes < 1:
        return "under a minute"
    if minutes < 60:
        return _plural(minutes, "minute", "minutes")
    if minutes < 24 * 60:
        return _plural(minutes // 60, "hour", "hours")
    return _plural(minutes // (24 * 60), "day", "days")


def _since(last_commit: datetime | None, now: datetime) -> str:
    """How long a branch has been sitting, in the words the reader judges with."""
    if last_commit is None:
        return "no commit of its own this checkout can read"
    age = _age(last_commit, now)
    if age is None:
        return "last commit dated later than now - one of the two clocks is wrong"
    return f"last commit {age} ago"


def _review(name: str, reviews: OpenPullRequests | None) -> str:
    """A row's pull-request clause, or nothing where the forge was not asked."""
    if reviews is None or not reviews.asked:
        return ""
    if name not in reviews.numbers:
        return "  no pull request open"
    number = reviews.numbers[name]
    return "  pull request open" if number is None else f"  pull request #{number} open"


def _digest_age(last_commit: datetime | None, now: datetime) -> str:
    """An age short enough to sit beside an id in the digest's one line."""
    if last_commit is None:
        return "(no commit read)"
    return _age(last_commit, now) or "(dated ahead of this clock)"


def format_flight(
    report: FlightReport,
    now: datetime,
    settled: SettledReport | None = None,
    reviews: OpenPullRequests | None = None,
    read: Holdings | None = None,
    unclaimed: Unclaimed | None = None,
) -> str:
    """Which items are on a branch, how long each has sat, and what went unread.

    The age is reported rather than thresholded, because "has an unmerged
    branch" and "is being worked right now" are different claims and no
    timeout tells them apart: a branch touched an hour ago is a live session,
    and the same branch three weeks on is work nobody will merge. Only the
    reader knows which, so both get the same line and the age decides it.

    **So the age is elapsed time, and the row carries the one fact that
    separates part of what the age cannot** (`PL-3QM9`, `PL-7TVT`). An age cut
    to the day read a branch committed 55 minutes ago as a day old across
    midnight, and even measured to the minute it cannot fire in the first hour,
    because a branch outlives its session: PR `#757` sat green for 25 minutes
    after its session was archived while its items read as somebody's work.
    `reviews` adds whether a pull request is open on each row's branch, which
    says the work is written and waiting on review whatever became of the
    session. What it cannot say - whether a young branch with none open still
    has a session behind it - is said in those words, and the closing line no
    longer tells the reader what to conclude from an age, which is the
    instruction the evidence never supported.

    **Except where the branch itself has answered it** (`PL-Q664`). A ref whose
    every held item is closed in its own copy, with no pull request open on
    it, is not a case the age decides - nobody is working it and nobody is
    reviewing it, and leaving such a row in the list above under "the age is
    what separates them" is how finished work sat unnoticed for three hours.
    `settled` is that reading, and its rows move out of the list rather than
    printing twice: two lines about one branch invite the reading that they are
    two branches, which is the mistake `FlightReport.editing` is kept disjoint
    from `branches` to avoid.

    It says what it knows and no more. "Nothing here is being worked" is the
    claim the two facts support; whether the work is correct, reviewed or ready
    is not, and this deliberately does not say so in any form a hurried reader
    could take for a merge recommendation.

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

    **`read` adds what the claim record knows and a row has no field for**
    (`PL-N162`, to `PL-MB2W`'s spec). Each row's state and kind - a claim, an
    old-rule `legacy claim`, a `status disposition` or a `branch name` - since
    "held" meant four different things once dispositions and names joined
    claims, and a status disposition is a decision about an item rather than
    somebody working it. Then the claims that lapsed on items the base holds
    open, which hold nothing and which `next` therefore offers: a session
    about to start one should know whose work it may be continuing. Then
    `legacy refs: N`, printed at zero too, because zero is the reading
    `PL-CH3Z` waits for before it deletes the old rule - on a whole read only
    (`_legacy_line`). `unclaimed` is the
    `unclaimed:` rows, one per work branch that claims nothing
    (`claims.claims_nothing`), and the design's pre-registered 1-in-20
    threshold for a weak hold is counted from them, so they print wherever one
    exists and nowhere else.
    """
    lines: list[str] = []
    finished = {entry.name for entry in settled.branches} if settled else set()
    live = [branch for branch in report.branches if branch.name not in finished]
    held = read.holding() if read is not None else {}
    if live:
        lines.append(
            f"{_plural(len(live), 'item is', 'items are')} on a branch "
            "the default branch has not taken:"
        )
        lines.append("")
        width = max(len(branch.name) for branch in live)
        ages = {branch.name: _since(branch.last_commit, now) for branch in live}
        age_width = max(len(age) for age in ages.values())
        kinds = _hold_columns([held.get(branch.item_id) for branch in live], read)
        for branch, kind in zip(live, kinds, strict=True):
            # `filed there` rather than a second table: the fact belongs to the
            # row it qualifies, and a reader scanning for their own id meets it
            # without being sent anywhere (`PL-3CTW`).
            mark = "" if branch.on_base else "  filed there"
            row = (
                f"{branch.item_id}  {branch.name:<{width}}  {kind}"
                f"{ages[branch.name]:<{age_width}}{_review(branch.name, reviews)}{mark}"
            )
            lines.append(row.rstrip())
        lines.append("")
        lines.append(
            "A branch outlives its session, so no row here says anybody is still on it: "
            "the age is how long it has sat."
        )
        if reviews is not None and reviews.asked:
            lines.append(
                "With a pull request open, the work is written and waits on review. With "
                "none, a branch minutes old is usually a session still working - but one "
                "whose session has ended reads the same until its age grows, and nothing "
                "a checkout can read tells the two apart sooner."
            )
        else:
            lines.append(
                "Whether a pull request is open for any of them could not be read here, so "
                "work waiting on review reads the same as work still being written."
            )
        if any(not branch.on_base for branch in live):
            lines.append(
                "An item marked `filed there` is not in this checkout's queue at all: that "
                "branch holds the only copy, and `bin/docket stranded` recovers it."
            )
    elif not report.branches:
        # Stated as the conclusion rather than as a fact about subjects
        # (`PL-VYSP`): a capture leads with an id and claims nothing, and a
        # claim the base has since taken or closed is removed above, so "no
        # commit leads with an id" was false whenever either existed. Since
        # `PL-N162` a hold is a claim, a status move or a name, and a subject
        # claims only on a commit made before the record.
        lines.append(
            "No branch holds an item. No branch carries an item id in its name, records a live "
            "claim on one or moves one's status, and no commit made before the claim record "
            "leads with one the default branch has not already taken or closed."
        )
    else:
        # Every claim there was is in the section below, which explains itself.
        # Repeating "no branch claims an item" here would contradict it.
        lines.append("No branch is carrying an item anybody is still working.")

    if settled and settled.branches:
        lines.append("")
        lines.extend(_format_settled(settled, now))

    if read is not None:
        lines.extend(_format_lapsed(read, now))
        lines.append("")
        lines.append(_legacy_line(read))
    if unclaimed is not None:
        lines.extend(_format_unclaimed(unclaimed, read, now))

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


def _kind(hold: Hold) -> str:
    """A hold's kind in the reader's words, `legacy` where the old rule read it."""
    kind = _HOLD_KINDS.get(hold.kind, hold.kind)
    return f"legacy {kind}" if hold.legacy else kind


def held_as(key: str, read: Holdings | None) -> str:
    """` (live claim)`: the state and kind of what holds `key`, for a list of ids, or `""`.

    The digest and `next` list held items by id alone, and "held" is four
    things since dispositions and names joined claims (`PL-N162`): a status
    disposition is a decision about an item, not somebody working it. Nothing
    where there is no read or no live hold behind the id, rather than a guess.
    """
    hold = read.holding().get(key) if read is not None else None
    return f" ({hold.state} {_kind(hold)})" if hold is not None else ""


def format_excluded(ids: Iterable[str], read: Holdings | None) -> str:
    """`next`'s line naming the items it left out as in flight, each with its hold."""
    return "Excluded, already in flight: " + ", ".join(
        f"{key}{held_as(key, read)}" for key in sorted(ids)
    )


def _hold_columns(holds: Sequence[Hold | None], read: Holdings | None) -> list[str]:
    """Each row's state and kind columns, padded to one width, or nothing without a read.

    A row with no hold behind it - a report and a read that disagree, which
    one invocation's cache rules out - gets blank columns rather than a guess.
    """
    if read is None:
        return ["" for _ in holds]
    states = [hold.state if hold else "" for hold in holds]
    kinds = [_kind(hold) if hold else "" for hold in holds]
    state_width = max((len(state) for state in states), default=0)
    kind_width = max((len(kind) for kind in kinds), default=0)
    return [
        f"{state:<{state_width}}  {kind:<{kind_width}}  "
        for state, kind in zip(states, kinds, strict=True)
    ]


def _format_lapsed(read: Holdings, now: datetime) -> list[str]:
    """The claims past their lease on items the base holds open, as rows like the live ones.

    Only open items (`Holdings.lapsed_open`): a claim on an item the base has
    closed is spent, and one on an item the base lacks is nobody's to start.
    And only items nothing holds live: a lapsed claim stays beside the plain
    claim a later session makes over it until its branch goes, and there
    `next` offers nothing.
    Said to hold nothing, because it does not - `next` offers the item and
    `claim` passes it without `--over` - and `show` is where what taking it
    involves is printed.
    """
    # An item something else holds live is left out: its row is above, `next`
    # does not offer it, and `show` prints the live claim rather than this one,
    # which is the rule slice 3 gave `show` - so the heading stays true.
    held = read.ids
    lapsed = tuple(hold for hold in read.lapsed_open() if hold.key not in held)
    if not lapsed:
        return []
    width = max(len(hold.ref) for hold in lapsed)
    kinds = _hold_columns(lapsed, read)
    lines = [
        "",
        f"{_plural(len(lapsed), 'claim has', 'claims have')} lapsed on "
        f"{'an item' if len(lapsed) == 1 else 'items'} the default branch holds open. A lapsed "
        "claim holds nothing, so `next` offers the item; "
        "`bin/docket show <ID>` says whose work it may continue:",
        "",
    ]
    for hold, kind in zip(lapsed, kinds, strict=True):
        lines.append(
            f"{hold.key}  {hold.ref:<{width}}  {kind}{_since(read.last.get(hold.ref), now)}"
        )
    return lines


def _legacy_line(read: Holdings) -> str:
    """`legacy refs: N`, the count `PL-CH3Z` waits to read as zero.

    **Zero is a conclusion only on a whole read.** `PL-CH3Z` deletes the old
    rule once this prints 0, and a read git declined holds nothing, while a
    ref whose history went unread - any truncated clone - contributes no
    hold whatever its subjects say. Either would print the go-ahead over refs
    that may still hold by the old rule, so a partial read prints the count as
    a floor and names what it could not see, and never the conclusion.
    """
    count = len(read.legacy_refs)
    if not read.known:
        return (
            f"legacy refs: unknown - git did not answer ({read.declined}), so whether any ref "
            "still holds an item by the old rule is not read here, and this is not the reading "
            "`PL-CH3Z` waits for."
        )
    if read.unreadable:
        unread = len(read.unreadable)
        return (
            f"legacy refs: at least {count} - {_plural(unread, 'ref', 'refs')} went unread and "
            f"may hold by the old rule as well ({', '.join(read.unreadable)}), so this is not "
            "the reading `PL-CH3Z` waits for; a full clone reads the whole count."
        )
    if not count:
        return (
            "legacy refs: 0 - no ref holds an item by a commit made before the claim record, "
            "so nothing here still needs the old rule (`PL-CH3Z` removes it)."
        )
    return (
        f"legacy refs: {count} - {_plural(count, 'ref holds', 'refs hold')} an item by a commit "
        "made before the claim record, read by the old rule from its subject. `PL-CH3Z` "
        "removes that rule once this reads 0."
    )


def _format_unclaimed(found: Unclaimed, read: Holdings | None, now: datetime) -> list[str]:
    """The `unclaimed:` rows: work branches that claim nothing (`claims.claims_nothing`).

    `PL-MB2W`'s third "Forgetful session" catch, and the same question
    `tools/branch_id_check.py` refuses in CI. The rows are the count the
    design's pre-registered 1-in-20 threshold reads, so each branch is one row
    and the heading says what it means rather than what to do about a session
    this checkout cannot see. A branch git did not answer about is named
    apart, since it may be either.
    """
    lines: list[str] = []
    if found.branches:
        count = len(found.branches)
        last = read.last if read is not None else {}
        width = max(len(ref) for ref in found.branches)
        lines.extend(
            [
                "",
                f"{_plural(count, 'work branch claims', 'work branches claim')} nothing: "
                f"{'it changes' if count == 1 else 'each changes'} files outside the queue in "
                "commits made under the claim record, and records no claim of its own:",
                "",
            ]
        )
        lines.extend(
            f"unclaimed: {ref:<{width}}  {_since(last.get(ref), now)}" for ref in found.branches
        )
    if found.unasked:
        lines.append("")
        lines.append(
            f"Whether {_plural(len(found.unasked), 'branch claims', 'branches claim')} nothing "
            f"is unknown - git did not answer which of "
            f"{'its' if len(found.unasked) == 1 else 'their'} commits are work: "
            f"{', '.join(found.unasked)}."
        )
    return lines


def _format_settled(settled: SettledReport, now: datetime) -> list[str]:
    """The branches nothing is left on, and exactly how much that claim covers.

    Two headings rather than one, because the two readings prove different
    amounts and a reader deciding what to do about a branch needs to know
    which they have. Where the forge answered, the row means every item closed
    *and* no pull request open. Where it did not, it means the first alone -
    and a branch waiting on review is then indistinguishable from one nobody
    opened, which is said in those words rather than left to be inferred from
    a missing clause.

    Neither heading tells the reader to merge anything, and the closing line
    says so outright. What these rows establish is that nobody is working
    here; whether the work is finished, correct or reviewed is a judgment
    nothing in this checkout can make.
    """
    count = len(settled.branches)
    carries, them = ("it carries", "it") if count == 1 else ("they carry", "them")
    heading = f"On {_plural(count, 'branch', 'branches')} every item {carries} is already closed"
    if settled.asked:
        heading += f", and no pull request is open for {them}"
    lines = [f"{heading}:", ""]
    whose = "the branch's own copy" if count == 1 else "the branches' own copies"
    width = max(len(entry.name) for entry in settled.branches)
    for entry in settled.branches:
        lines.append(
            f"  {entry.name:<{width}}  {', '.join(entry.item_ids)}  "
            f"{_since(entry.last_commit, now)}"
        )
    lines.append("")
    lines.append(f"Nothing here is being worked: every item {carries} is closed in {whose}.")
    if not settled.asked:
        lines.append(
            f"Whether a pull request is open for {them} could not be read here, so a branch "
            "waiting on review looks the same as one nobody opened."
        )
    lines.append(
        "That is not a verdict on the work. Nothing here says it is reviewed, correct or "
        "ready; it says only that no session is on it. Read the branch and decide what it "
        "needs - `bin/docket stranded` recovers an item that exists only there."
    )
    return lines


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
        # The fact the member misread, beside the head that states it: the
        # member is read to be started, and this is the line that says whether
        # it is one more instance of a record some reader already lacked
        # (`PL-5MYR`).
        if head.misread:
            lines.append(f"      misread: {head.misread}")
    lines.append(f"    {closing}")
    return "\n".join(lines)


def _drain_phrase(cluster: Cluster) -> str:
    """How far this cluster has drained since its head closed, in one clause.

    The trend, which the present split cannot carry: "58 of 99 open" was
    derived twice in two days and it was the *unchanged* that made the answer
    worth having (project owner, 2026-09-21). Measured against the head's own
    close date, which is already in the store, so nothing new is recorded to
    get it.

    Three readings a single number could not keep apart, so each is named.
    What closed *after* the head is drain. What closed *on the head's date*
    cannot be ordered against it at all - `closed:` is a date and not a
    timestamp, and 32 of this store's 99 member closures are that case - so it
    is reported beside the drain rather than folded into it, and only where it
    changes how "none closed since" should be read. What closed *before* is
    not drain at all, and is named only when it would otherwise stop the
    numbers on the line reconciling.

    An open head has no reference date, which is not hypothetical: a generator
    is recorded when it is identified, and `CLAUDE.md` lets a session end by
    handing it to a fresh one.
    """
    if cluster.is_drained:
        last = max((i.closed for i in cluster.members if i.closed), default=None)
        return f"drained {last.isoformat()}" if last else "drained"
    left = f"{len(cluster.open_items)} open"
    if cluster.head.closed is None:
        return f"{left} - head still open, so nothing dates the drain yet"
    since = len(cluster.closed_since_head)
    moved = f"{since} closed since" if since else "none closed since"
    phrase = f"{left} - {moved} the head closed {cluster.head.closed.isoformat()}"
    footnotes = []
    if with_head := len(cluster.closed_with_head):
        footnotes.append(f"{with_head} closed on that date")
    if before := len(cluster.closed_before_head):
        footnotes.append(f"{before} closed before it")
    return f"{phrase} ({', '.join(footnotes)})" if footnotes else phrase


def _verdict_phrase(head: Item, standing: Standing | None) -> str:
    """Whether this head still ranks, as a trailing clause, or `""`.

    Only for an **open** head, which is the only one the answer can move.
    `recommend` ranks from the startable set, so a closed head is on no tier
    whatever its verdict says, and printing `spent` beside one would offer a
    reader a distinction that decides nothing - the noise `CLAUDE.md` retires a
    check for producing. Every head this project has recorded is closed, so
    that is the common case rather than the edge.

    The distinction it does carry is one the drain figures cannot. Drain is how
    much of the damage is repaired; the verdict is whether more is still
    arriving, and a cluster can be fully drained with its mechanism running or
    wholly open with it spent. Only the second decides the rank, so a report
    showing the first alone would let a recorded generator read as a ranked one
    - which is the conflation `PL-T7QR` closed.

    A live head at `blocked` is not on the tier itself: its rank passes to the
    open items it waits on, or reaches nothing, and `docket show` says which.
    This line said "so on the tier" of `PL-MB2W` while `show` said it was
    not ranked (`PL-4RK2`), and of four untriaged heads `next` offered nowhere
    (`PL-Q4DF`) - so where a live head stands is `standing`, the caller's
    reading of `plan.tier_standings`, rather than a status tested here.
    """
    if head.status in CLOSED_STATUSES:
        return ""
    verdict, _ = split_generator_verdict(head.generator)
    if verdict == "live" and standing is not None and standing.why == "blocked":
        return (
            "; still generating, but blocked, so not on the tier itself"
            " - `docket show` says what carries its rank"
        )
    if verdict == "live" and standing is not None and standing.why == "untriaged":
        return "; still generating, but untriaged, so ranked nowhere until triage seats it"
    if verdict == "live":
        return "; still generating, so on the tier"
    if verdict == "spent":
        return "; spent, so it ranks on its band"
    return "; no recurrence verdict, so recorded but unranked"


def format_drain(cluster: Cluster) -> str:
    """One cluster's state in one line, for `show` on the head itself.

    A line rather than the member list, because `show` on a head is read to
    start the head, and what it was missing was the one fact its own status
    contradicts: the cause is closed and the repairs are not. `docket
    generators <id>` is where the members are.
    """
    return (
        f"{_plural(len(cluster.members), 'item', 'items')}, {_drain_phrase(cluster)}"
        f"; `docket generators {cluster.head.identifier}` lists them"
    )


def format_clusters(
    clusters: Mapping[str, Cluster],
    unsound: Sequence[Item] = (),
    defects: Sequence[Item] = (),
    overlaps: Sequence[Overlap] = (),
    *,
    standings: Mapping[str, Standing],
) -> str:
    """Every generator against how much of its cluster is still open.

    The question this answers is the project owner's recurring one - "are the
    generators dealt with?" - which had no command behind it and was answered
    twice in two days by a throwaway script over the whole store, both times
    with the same figures (`PL-XF5V`). `CLAUDE.md` builds deterministic tooling
    for exactly that recurrence.

    **Ordered by what is still open, largest first**, because the reader is
    sizing outstanding work rather than auditing the list. A drained cluster is
    printed too, and last: four of this project's eleven are drained, and
    "these are finished" is half of the answer to whether the generators are
    dealt with.

    Two sets sit outside the clusters and are named rather than omitted, per
    `.claude/rules/apparatus-standard.md`'s floor. An unsound `root-cause-of:`
    is ranked by nothing and counted here by nothing, so a reader would see
    neither the cluster nor its absence; and an `impairs-generators:` item
    ranks on the generator tier while having no members to drain, which is the
    discrepancy that made `PL-XF5V`'s brief say twelve heads over a table of
    eleven.

    An **open** head also carries its recurrence verdict, because from
    `PL-T7QR` being recorded here and ranking above every band are two
    different facts and this is the table where the first is audited. A closed
    head carries none: it is startable by nothing, so its verdict moves no
    ranking and the clause would decide nothing.

    **Under each head, the fact its members misread rather than its title**
    (`PL-5MYR`): the title names the reader and the `misread:` line names the
    record, which is the half a comparison needs. A head that states none says
    so and falls back to its title. The pairs of heads whose member lists
    overlap follow the list - decidable, and a hint rather than a verdict,
    since two heads can share a record over disjoint members.
    """
    if not clusters:
        lines = ["no item carries a sound `root-cause-of:`, so no generator is recorded"]
        return "\n".join(lines + _outside_clusters(unsound, defects, standings))

    members = {i.identifier for c in clusters.values() for i in c.members}
    still_open = {i.identifier for c in clusters.values() for i in c.open_items}
    drained = [c for c in clusters.values() if c.is_drained]
    lines = [
        f"{_plural(len(clusters), 'generator', 'generators')}, {len(drained)} drained"
        f" - {_plural(len(members), 'distinct member', 'distinct members')},"
        f" {len(still_open)} still open",
        "",
    ]
    ordered = sorted(
        clusters.values(), key=lambda c: (-len(c.open_items), -len(c.members), c.head.identifier)
    )
    for cluster in ordered:
        lines.append(
            f"  {cluster.head.identifier} "
            f"{_plural(len(cluster.members), 'member', 'members')}, {_drain_phrase(cluster)}"
            f"{_verdict_phrase(cluster.head, standings.get(cluster.head.identifier))}"
        )
        lines.append(f"      {_misread_or_title(cluster.head)}")
    lines.extend(_format_overlaps(overlaps))
    lines.extend(_outside_clusters(unsound, defects, standings, heads=clusters.keys()))
    return "\n".join(lines)


def _misread_or_title(head: Item) -> str:
    """The fact a head's members misread, or its title marked as the stand-in."""
    if head.misread:
        return head.misread
    return f"[no misread:] {_gloss(head.title, 48)}"


def _format_overlaps(overlaps: Sequence[Overlap]) -> list[str]:
    """The pairs of heads whose clusters touch, as lines under a heading, or none.

    Worded as what it is - two lists sharing an id, or one head naming the
    other - because the intersection is not the comparison: it missed two of
    the five shared records `PL-T7Y1`'s audit found, whose members were
    disjoint (`PL-5MYR`). The heading sends the reader to the two `misread:`
    lines, which is where the judgment is made.
    """
    if not overlaps:
        return []
    lines = [
        "",
        f"  {_plural(len(overlaps), 'pair of heads overlaps', 'pairs of heads overlap')} - "
        "a fact about the two lists, not a verdict that they share a record; read both "
        "`misread:` lines:",
    ]
    for pair in overlaps:
        one, other = pair.first.identifier, pair.second.identifier
        clauses = []
        if pair.shared:
            clauses.append(f"{one} and {other} share {', '.join(pair.shared)}")
        if pair.first_names_second:
            clauses.append(f"{one} names {other}")
        if pair.second_names_first:
            clauses.append(f"{other} names {one}")
        lines.append(f"    {'; '.join(clauses)}")
    return lines


def format_misread(
    clusters: Mapping[str, Cluster], overlaps: Sequence[Overlap] = (), unsound: Sequence[Item] = ()
) -> str:
    """What each head's members misread, sorted by the fact - `docket generators --misread`.

    The list triage and grooming compare a capture against, and the one a
    session reads to compare heads with each other: one line per head, sorted
    by the stated fact so that two heads naming one record sit together, which
    is the comparison nobody was making (`PL-5MYR`). Sorted case-insensitively
    because the order is for a reader's eye, then by id so it is stable.

    A head stating nothing is listed last rather than left out, for the
    apparatus floor: a head missing from this list is a head a capture is
    never compared against, and omitting it silently would hand over a partial
    reading as the whole one. `docket check` names each as an error. An item
    whose `root-cause-of:` is unsound is on no list here, being no head, and
    is named after it for the same reason, as `format_clusters` names it.
    """
    if not clusters:
        lines = ["no item carries a sound `root-cause-of:`, so no generator is recorded"]
        return "\n".join(lines + _outside_clusters(unsound, ()))
    heads = [cluster.head for cluster in clusters.values()]
    stated = sorted(
        (head for head in heads if head.misread),
        key=lambda head: (head.misread.casefold(), head.identifier),
    )
    missing = sorted((head for head in heads if not head.misread), key=lambda h: h.identifier)
    labels = {head.identifier: f"{head.identifier} ({head.status})" for head in heads}
    width = max(len(label) for label in labels.values())
    lines = [
        f"What the members of each of {_plural(len(heads), 'head', 'heads')} misread, sorted "
        "by the fact so heads stating one fact sit together:",
        "",
    ]
    for head in stated:
        lines.append(f"  {labels[head.identifier]:<{width}}  {head.misread}")
    for head in missing:
        lines.append(f"  {labels[head.identifier]:<{width}}  [no misread:] - docket check names it")
    lines.extend(_format_overlaps(overlaps))
    lines.extend(_outside_clusters(unsound, ()))
    return "\n".join(lines)


def _outside_clusters(
    unsound: Sequence[Item],
    defects: Sequence[Item],
    standings: Mapping[str, Standing] | None = None,
    heads: Collection[str] = (),
) -> list[str]:
    """The generator-tier items no cluster count reaches, so the total is honest.

    A machinery defect that is also a head is in the table above, members and
    all, so it is left out here: `PL-Q4DF` itself was listed as naming no
    members while its `root-cause-of:` named three. Which of the rest rank is
    `standings`' answer rather than a status tested here, since a blocked or
    untriaged one ranks nowhere itself and this line called it ranked (`PL-Q4DF`).
    """
    lines: list[str] = []
    if unsound:
        named = ", ".join(i.identifier for i in unsound)
        lines.append("")
        lines.append(
            f"  {_plural(len(unsound), 'item carries', 'items carry')} a `root-cause-of:` that is "
            f"not a sound claim, so it is ranked and counted as an ordinary item: {named}"
        )
        lines.append("      `docket check` says what is wrong with each.")
    # Split by status because only the open ones rank: a closed item is on no
    # tier whatever its claim says, and this line called a done one ranked
    # while printing `(done)` beside it (`PL-BBT8`). The closed ones stay
    # named, as a drained cluster does above, since they are the half of "are
    # the generators dealt with?" that is.
    tier = standings or {}
    outside = [i for i in defects if i.identifier not in heads]
    ranking = [i for i in outside if i.identifier in tier and tier[i.identifier].state == HELD]
    waiting = [i for i in outside if i.identifier in tier and tier[i.identifier].state != HELD]
    closed = [i for i in outside if i.status in CLOSED_STATUSES]
    if ranking:
        named = ", ".join(f"{i.identifier} ({i.status})" for i in ranking)
        lines.append("")
        lines.append(
            f"  {_plural(len(ranking), 'item ranks', 'items rank')} on the generator tier by "
            f"`impairs-generators:` and {'names' if len(ranking) == 1 else 'name'} no members, "
            f"so none is a cluster above: {named}"
        )
    if waiting:
        named = ", ".join(f"{i.identifier} ({i.status})" for i in waiting)
        lines.append("")
        lines.append(
            f"  {_plural(len(waiting), 'item carries', 'items carry')} a sound "
            f"`impairs-generators:`, {'names' if len(waiting) == 1 else 'name'} no members, and "
            f"{'ranks' if len(waiting) == 1 else 'rank'} nowhere itself, being blocked or "
            f"untriaged - `docket show` says where the rank stands: {named}"
        )
    if closed:
        named = ", ".join(f"{i.identifier} ({i.status})" for i in closed)
        lines.append("")
        lines.append(
            f"  {_plural(len(closed), 'closed item carries', 'closed items carry')} a sound "
            f"`impairs-generators:` and {'ranks' if len(closed) == 1 else 'rank'} on no tier, "
            f"being closed: {named}"
        )
    return lines


def format_cluster(cluster: Cluster) -> str:
    """One generator's members, drawn the way `feature` draws a feature's.

    Same three marks and the same two figures above them, so the reconciliation
    `progress_mark` documents holds here too: `[x]` is the numerator, `[ ]` is
    what is left, and every member is a line (`PL-VFVW`).

    The split by the head's close date is printed in full here, where the
    summary carries only the drain. `closed before` is the bucket that is not
    drain at all - a head is recorded once a mechanism is seen under three
    items, which can be after some were worked singly - and folding it into
    the same number would overstate what the fix achieved.
    """
    head = cluster.head
    left = f"{len(cluster.open_items)} left" if cluster.open_items else "drained"
    lines = [
        f"{head.identifier} ({head.status}) root cause of "
        f"{_plural(len(cluster.members), 'item', 'items')}: "
        f"{len(cluster.done)}/{len(cluster.members)} done ({left})",
        f"  {_gloss(head.title, 72)}",
    ]
    if head.misread:
        lines.append(f"  misread: {head.misread}")
    lines.append(f"  {_drain_phrase(cluster)}")
    for item in cluster.members:
        lines.append(f"  [{progress_mark(item)}] {item.identifier} {item.title}")
    return "\n".join(lines)


def format_near_duplicates(
    candidates: Sequence[Candidate], identifier: str, *, declared: bool = True
) -> str:
    """The open items a capture may be a second filing of, under the capture's own line.

    Printed after the item is written rather than instead of writing it. The
    capture rule is unconditional, so this is a warning and never a gate, and
    the order says so: the id and path come first, exactly as they did before
    this existed, and a session that stops reading has still captured its
    finding.

    **What each line claims is what it can support.** The shared path is a fact
    about two declarations and is named; the ranking that ordered them is not,
    so no line gives a score or calls the match a duplicate. What the reader is
    asked to do is open two briefs, which is the judgment this cannot make -
    whether two items are one defect is a reading of prose, and
    `subprojects/docket/README.md` already refuses to let a similarity score buy
    a promotion (`PL-X5JR`).

    The status comes with each id for the reason it does on a generator head: an
    item at `ready` with a brief already written is a diagnosis this session can
    read instead of repeating, while one still `untriaged` is another session's
    capture of the same moment.
    """
    if not candidates:
        return ""
    named = _plural(len(candidates), "open item declares", "open items declare")
    # Where the paths came from, because the two are different claims. A
    # `--touches` is what the session said this capture is about; the working
    # tree is what it happened to be changing, which is a good guess and is not
    # the same thing - and a reader who is not told cannot weigh a wrong match
    # (`PL-THLT`).
    key = "a path this capture reaches" if declared else "a path this branch is changing"
    lines = [f"  Possibly filed already - {named} {key}:"]
    for candidate in candidates:
        item = candidate.item
        lines.append(f"    {item.identifier} ({item.status}) - {_gloss(item.title)}")
        lines.append(f"      shares {', '.join(candidate.shared)}")
    lines.append("    Read those briefs before writing this one. If it is the same problem,")
    lines.append(
        f"    group them: bin/docket set {identifier} --feature <name>, and the same on each."
    )
    return "\n".join(lines)


def format_recurrences(item: Item) -> str:
    """The filings this item absorbed, as a pointer to briefs rather than a count.

    A count alone says a cluster exists and gives a reader no way to check it,
    which is the partial answer the apparatus standard's floor refuses. The ids
    are what make the claim auditable: open both briefs, and either they are
    one mechanism - in which case `root-cause-of:` is the field to write - or
    the title match was wrong and the entry says exactly which filing to
    disbelieve.

    The threshold is named only once it is reached. Below it there is nothing
    to act on, and printing "1 of 3" on every item that has ever been filed
    twice is a progress bar toward a promotion nothing has earned.

    A withdrawn match is printed too, under its own heading and outside the
    count. It is the record of a match that was made and then disowned, and
    leaving it unprinted would make the withdrawal the one event in this
    mechanism's life that no command will show you - which is the asymmetry
    `PL-34BG` was filed about, arriving from the other side.
    """
    filings = [found for found in live_recurrences(item) if found.identifier]
    withdrawn = [found for found in recurrences_of(item) if found.withdrawn and found.identifier]
    if not filings and not withdrawn:
        return ""
    lines = []
    if filings:
        lines.append(f"  Filed again {_plural(len(filings), 'time', 'times')} since, as:")
        for found in filings:
            when = found.when.isoformat() if found.when else "an unreadable date"
            lines.append(f"    {found.identifier} on {when}")
        if recurrence_count(item) >= MIN_RECURRENCES:
            lines.append(
                "    That is the generator threshold. Read them against this brief: one "
                "mechanism means `docket set <id> --root-cause-of <ids> --generator "
                "<verdict> --misread <fact>`, which is a judgment nothing here makes for you."
            )
    if withdrawn:
        lines.append("  Matched and withdrawn, counting for nothing:")
        for found in withdrawn:
            when = found.withdrawn.isoformat() if found.withdrawn else ""
            lines.append(f"    {found.identifier}, withdrawn {when} - why, in {found.withdrawn_by}")
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


def format_queue_edit(edit: QueueEdit, now: datetime, *, startable: bool) -> str:
    """That an item's file has already been edited, which is not that it is in flight.

    **The line exists to be different from `IN FLIGHT`, so it does not open
    with a mark.** Two sessions triaged one pair of items on 2026-09-06,
    fetched, checked and were each told correctly that nothing was in flight -
    a triage pass has no diff outside the queue, so `_annotates_only` withheld
    the claim and nothing else was reading the paths (`PL-N1JK`). What the
    second session needed was not "do not start this", which would have been
    false, but "the file you are about to write to has already been written
    to", which is true and is a different sentence.

    So it says what was observed and what follows, and where the item can be
    started it says so in as many words. A weaker signal worded like a
    stronger one is read as the stronger one, and the cost lands on the wrong
    side: an item nobody is working left unstarted because a capture commit
    touched its file.

    **`startable` is the caller's, read from the item's status, because the
    edit cannot say it** (`PL-9F8B`). A branch edits a closed or blocked
    item's file as readily as a ready one's, and the line called `PL-6T44`
    (`done`) and `PL-MB2W` (`blocked`) startable alike. Where the status does
    not allow a start, the line says nothing about starting at all: the
    collision is still true, and it is the only thing this line knows.
    """
    edited = f"  Its file is already edited on {edit.name} ({_since(edit.last_commit, now)}).\n"
    if not startable:
        return (
            f"{edited}  Not work in flight - but a second edit to the same file collides\n"
            "  at merge, so land the smaller change first."
        )
    return (
        f"{edited}  Not work in flight - {edit.item_id} is startable - but a second edit to the\n"
        "  same file collides at merge, so land the smaller change first."
    )


def format_since_filed(report: SinceFiled, today: date, recheck_after_days: int) -> str:
    """How long an open item has waited, what its declared paths went through, and what now.

    Facts, never a verdict (`PL-TQN2`). Each path says whether it is in the
    tree and how many commits changed it since filing; whether the problem
    went with a deleted file or only moved is the start mode's to decide,
    because a script that guessed would print its guess as authoritatively as
    its facts. The one instruction is the re-confirm line, and it fires on the
    item being opened rather than as an advisory over the whole store: 79 open
    items were past the line on 2026-09-23, and a list that long on every
    `check` is one sessions learn to skim.
    """
    age = (today - report.filed).days
    when = (
        "today" if age == 0 else f"{_plural(age, 'day', 'days')} ago" if age > 0 else "after today"
    )
    head = f"  filed {report.filed.isoformat()}, {when}"
    if not report.paths:
        lines = [f"{head} - it declares no touches, so there is no path to compare"]
    elif report.known:
        lines = [f"{head} - since then, counting commits on or after that date (UTC):"]
    else:
        lines = [f"{head} - commits since then not read: {report.declined}"]
    lines.extend(f"    {entry.path} - {_touched(entry)}" for entry in report.paths)
    if age > recheck_after_days:
        lines.append(
            f"  RE-CONFIRM before starting: filed more than {recheck_after_days} days ago, so check"
            " the brief below still holds against the tree - work it, rewrite it, or drop it"
            " with the reason"
        )
    return "\n".join(lines)


def _touched(entry: TouchedPath) -> str:
    """One declared path's facts, worded so a missing file reads as a question."""
    if entry.commits is None:
        return "in the tree" if entry.exists else "not in the tree"
    if entry.exists:
        return (
            f"changed by {_plural(entry.commits, 'commit', 'commits')}"
            if entry.commits
            else "unchanged"
        )
    if entry.deleted:
        return "gone - a commit since then deleted it"
    if entry.commits:
        return f"not in the tree, after {_plural(entry.commits, 'commit', 'commits')} since then"
    return "not in the tree, and untouched since - a file the work creates, or one gone before"


#: What each kind of hold is called where `show` prints it.
_HOLD_KINDS = {CLAIM: "claim", DISPOSITION: "status disposition", NAMED: "branch name"}


def _hold_detail(hold: Hold, last: datetime | None, now: datetime, *, aged: bool = True) -> str:
    """A hold's kind and state, when it was made, and how long its branch has sat.

    On one clock, UTC, rather than as git wrote it: two sessions can be in two
    zones, and two timestamps a reader has to convert before comparing are two
    a reader will compare wrongly - which here would mean reading the wrong
    branch as the one that continues. `legacy` is said because such a claim
    was read from a commit subject by the old rule rather than recorded.
    `aged` false leaves the branch's age off, for a caller saying when instead.
    """
    kind = _kind(hold)
    if hold.kind == NAMED and not hold.commit:
        made = "its commits went unread here"
    else:
        verb = {DISPOSITION: "moved to", NAMED: "first commit"}.get(hold.kind, "made")
        status = f" `{hold.status}`" if hold.kind == DISPOSITION else ""
        made = f"{verb}{status} {hold.since.astimezone(UTC):%Y-%m-%d %H:%M} UTC"
    session = f", session {hold.session}" if hold.session else ""
    age = f"; {_since(last, now)}" if aged else ""
    return f"{hold.state} {kind}, {made}{session}{age}"


def _on_head(hold: Hold, read: Holdings) -> bool:
    """Whether a hold is on the branch `HEAD` is on, whoever made it."""
    return bool(read.head) and hold.ref == read.head


def _ours(hold: Hold, read: Holdings) -> bool:
    """Whether a hold is this checkout's: its session made it, or it is on this branch.

    Both count, because `claim` answers by branch: a claim another session made
    on the branch this one is standing on is this branch's claim, and telling
    the reader to yield to it would be telling a branch to yield to itself.
    """
    return hold.mine or _on_head(hold, read)


def _one_claim(group: Sequence[Hold], item: str, read: Holdings, now: datetime) -> list[str]:
    """The mark for an item one claim holds, however many branches reach its commit."""
    only = next((hold for hold in group if _ours(hold, read)), group[0])
    lines = [f"    {_hold_detail(only, read.last.get(only.ref), now)}"]
    if len(group) > 1:
        lines.append(_reached_by(group, only))
    if only.mine and _on_head(only, read):
        return [
            f"  IN FLIGHT on this branch ({only.ref}) - {item} is this session's own work.",
            *lines,
        ]
    if _on_head(only, read):
        return [
            f"  IN FLIGHT on this branch ({only.ref}) - claimed by another session, not this one.",
            *lines,
            f"  The claim is this branch's, so the work here is {item}'s and `bin/docket claim`",
            "  here writes nothing new. Where that session is still running, two sessions are",
            "  now on one branch.",
        ]
    if only.mine:
        return [
            f"  IN FLIGHT on {only.ref} - {item} is this session's own claim, made on that branch.",
            *lines,
        ]
    # The ref on a line of its own: a harness-named ref runs to fifty
    # characters, and the sentences after it should not wrap around it.
    return [
        f"  IN FLIGHT on {only.ref}",
        *lines,
        f"  That branch has claimed {item}, so starting it here would redo its work.",
        "  A branch outlives its session, so this does not say anybody is still on it;",
        "  `bin/docket flight` adds whether a pull request is open.",
    ]


def _reached_by(group: Sequence[Hold], shown: Hold) -> str:
    """The other branches one claim commit is on, said as the one claim it is."""
    others = ", ".join(hold.ref for hold in group if hold is not shown)
    return f"    the same claim commit is on {others} too, through a merge: one claim, not two"


def _live_claims(order: Sequence[Hold], item: str, read: Holdings, now: datetime) -> list[str]:
    """Who has claimed an item, and - where more than one branch has - which session yields.

    **The verdict is printed rather than left to be worked out, and that is the
    whole reason this exists.** Two sessions that discover each other reason
    from the same evidence and can still reach opposite conclusions, and the
    expensive outcome is not both continuing but both standing down: the item
    is then unstarted and each session believes the other has it. A rule stated
    as prose cannot rule that out. `Holdings.order` is one order over claim
    commits, the same in every checkout, and a branch yields only where a claim
    that is not its own stands ahead of one that is - so the first never
    yields, a session is never told to yield to itself, and one carrying none
    of the claims has nothing to hand over.

    **One claim commit is one claim, whichever branches reach it.** A claim
    read by the old rules counts for every branch whose walk reaches its
    commit, so a branch that merged another's carries the same claim, and an
    order over the two would tell each checkout its own branch holds it.
    Grouped by commit, as `vcs.precedence` grouped them, it is one holder and
    no verdict - the handoff it usually is.

    **It says what the branch holds, not that somebody is holding it**
    (`PL-7TVT`). A branch outlives its session: PR `#757`'s items read as held
    for 25 minutes after its session was archived. A live claim proves the item
    was taken on that branch within the lease, so starting it elsewhere redoes
    it - true of a live session, of a pull request waiting on review and of an
    abandoned branch alike, which is the one instruction the evidence supports.
    """
    groups: dict[str, list[Hold]] = {}
    for hold in order:
        groups.setdefault(hold.commit, []).append(hold)
    claims = list(groups.values())
    if len(claims) == 1:
        return _one_claim(claims[0], item, read, now)

    lines = [
        f"  {item} is claimed on {_plural(len(claims), 'branch', 'branches')}. Whichever claimed "
        "it first holds it,",
        "  a tie breaks on the claim commit's hash and a takeover stands where the claim it",
        "  names stood, so which session yields reads the same in every checkout:",
        "",
    ]
    ours = next(
        (
            position
            for position, group in enumerate(claims)
            if any(_ours(hold, read) for hold in group)
        ),
        None,
    )
    for position, group in enumerate(claims):
        shown = next((hold for hold in group if _ours(hold, read)), group[0])
        verdict = "holds it" if position == 0 else "yields  "
        here = (
            " (this branch)" if _on_head(shown, read) else " (this session)" if shown.mine else ""
        )
        lines.append(f"    {verdict}  {shown.ref}{here}")
        lines.append(f"              {_hold_detail(shown, read.last.get(shown.ref), now)}")
        if len(group) > 1:
            lines.append(f"          {_reached_by(group, shown).strip()}")
    lines.append("")
    if ours == 0:
        lines.append(f"  This branch holds {item}; the others are the ones that yield.")
    elif ours is not None:
        lines.append("  This branch yields: stop, and hand over what you have already found.")
    else:
        lines.append(
            f"  This branch claims none of them, and {item}'s work is on theirs - starting it "
            "here would redo it."
        )
    if read.declined:
        # Louder than the unreadable line below, because this one breaks the
        # guarantee the order rests on: two sessions can only compute the same
        # answer from the same evidence, and a silence gives them different
        # evidence (`PL-Q9Z1`).
        lines.append(
            f"  (This ordering is partial - {read.declined} - so the other session "
            "may be computing a different one. Do not stand down on it.)"
        )
    if read.unreadable:
        # The order is over the refs that could be read, and a ref beyond a
        # truncated clone's horizon is the normal state of an agent's
        # container. Saying so is the same refusal to present a partial reading
        # as a complete one that `format_unread` makes for the rest.
        lines.append(
            f"  ({_plural(len(read.unreadable), 'ref', 'refs')} went unread, so this order "
            "is over what could be read.)"
        )
    return lines


def _other_hold(hold: Hold, item: str, read: Holdings, now: datetime) -> list[str]:
    """A status disposition or a branch name holding an item nothing has claimed.

    **A disposition is not described as somebody working the item, because it
    is not one** (`PL-N162`). A triage pass readying an item, or a grooming
    pass blocking or dropping it, moves its status on that branch and `next`
    stops offering it - the refuter's repro was one queue-only commit taking
    an item from `untriaged` to `ready`. Before this, `show` said nothing about
    it at all. So the line says what the branch decided, and what follows for
    a session about to start: that copy lands over this one, and may say the
    item is not to be started.

    A name is the older reading (`PL-TZ3R`): a branch named for its item was
    always taken to carry it, and still is where the branch has recorded no
    claim on it, with the caveat that nothing recorded so.
    """
    detail = f"    {_hold_detail(hold, read.last.get(hold.ref), now)}"
    if hold.kind == DISPOSITION:
        if _ours(hold, read):
            return [
                f"  STATUS HELD on this branch ({hold.ref}) - its copy moves {item} to "
                f"`{hold.status}`.",
                detail,
            ]
        return [
            f"  STATUS HELD on {hold.ref}",
            detail,
            f"  That branch moved {item}'s status - a triage or grooming pass, or a close-out -",
            "  which is a decision about the item, not somebody working it. Read that copy",
            "  before starting: it lands over this one, and `next` does not offer the item",
            "  while it holds.",
        ]
    if _ours(hold, read):
        return [
            f"  IN FLIGHT on this branch ({hold.ref}), by its name - {item} is this session's "
            "own work.",
            detail,
            f"  Nothing records the claim; `bin/docket claim {item}` does.",
        ]
    return [
        f"  IN FLIGHT on {hold.ref}, by its name",
        detail,
        f"  That branch is named for {item} and records no claim on it, so its work is",
        f"  presumably {item}'s and starting it here may redo it. A branch outlives its",
        "  session, so this does not say anybody is still on it; `bin/docket flight` adds",
        "  whether a pull request is open.",
    ]


def _lapsed_claim(hold: Hold, item: str, read: Holdings, now: datetime) -> list[str]:
    """A claim past its lease on an item the base still holds open, and nothing live on it.

    **A lapsed claim holds nothing, so the line says the item is free** rather
    than gating it (`PL-N162`'s review). `claim` refuses only on a live claim,
    and the lease is what answers a claim wrongly lapsed, by being lengthened;
    the evidence `get_session` gives is for getting past a *live* claim whose
    session is gone, which is `claim`'s own refusal to say. `--over` is offered
    as what it adds here - the record of where the work came from, which also
    ends this line - and not as a condition.
    """
    lapsed = hold.renewed + LEASE_TERM
    detail = (
        f"    {_hold_detail(hold, None, now, aged=False)}; lapsed "
        f"{lapsed.astimezone(UTC):%Y-%m-%d %H:%M} UTC, {LEASE_TERM.days} days after the last "
        "commit that renewed it"
    )
    if _ours(hold, read):
        return [
            f"  LAPSED on this branch ({hold.ref}) - its claim on {item} no longer holds it.",
            detail,
            f"  `bin/docket claim {item}` claims it again, from now.",
        ]
    return [
        f"  LAPSED on {hold.ref}",
        detail,
        f"  That claim holds nothing, so `bin/docket claim {item}` takes the item. Taking it",
        "  over instead records where the work came from, and ends this line:",
        f'    bin/docket claim {item} --over {hold.ref} --reason "..."',
    ]


def format_holds(read: Holdings, item_id: str, now: datetime) -> str:
    """Which branches hold an item, by what kind of hold and in what state, for `show`.

    The item's live claims, in `Holdings.order`, where there are any - and
    then nothing else, since a disposition or a name never orders against a
    claim and a lapsed claim is not what stands in the way. Where nothing
    claims it, the status disposition or branch name holding it instead, one
    mark per branch and the disposition first, as `Holdings.flight` prefers
    it; then any lapsed claim on it while the base holds it open, which
    `claim` would pass. Empty where nothing holds the item, so the caller's
    weaker mark - the file already edited - can speak.
    """
    key = item_id.upper()
    if order := read.order(key):
        return "\n".join(_live_claims(order, item_id, read, now))
    lines: list[str] = []
    marked: set[str] = set()
    for hold in (*read.dispositions, *read.named):
        if hold.key == key and hold.state == LIVE and hold.ref not in marked:
            marked.add(hold.ref)
            lines.extend(_other_hold(hold, item_id, read, now))
    for hold in read.lapsed_open():
        if hold.key == key:
            lines.extend(_lapsed_claim(hold, item_id, read, now))
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

    It marks and does not refuse, for the reason `flight` reports rather than
    blocks: the answer is bounded by what has been pushed and by
    the refs this checkout can read, so a lock built on it would sooner or
    later block the session whose own branch is the one holding the item,
    with no way to tell it apart. Triage is cheap to redo and expensive to
    have refused.

    **The mark that fires here is not the one `next` ranks on, and on a triage
    pass it is usually the only one there is.** A pass that only fills in
    fields writes nothing outside `docs/items/` and records no claim - so
    before `FlightReport` carried the file edits, two sessions triaging one
    item could each fetch,
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
    # triage pass records no claim, so two passes on one item are invisible to
    # each other however carefully each fetches (`PL-N1JK`).
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
    if config.payoff_required_from is not None:
        # Stated here rather than in `_unset`, which is where `verify:` is not
        # stated either: both gates fire at `ready` rather than at capture, so
        # listing them beside `priority` would mark as missing a field the item
        # does not yet owe. What a triage pass needs is the warning before it
        # writes `--status ready`, which is this list.
        rules.append(
            "an item set to `ready` must carry a `payoff:` - one plain-language line of "
            "what closing it buys, in consequence terms rather than a restatement of the "
            "title. There is no `not-delegable` equivalent: every item has a consequence."
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
    """Every open debt item in the store, as the two lists a freeze starts from.

    Recording Gate 0 by hand meant reading every open item's classes and
    status, applying the rule, splitting the result by scope and typing the
    ids into the plan - a full pass over 48 items, repeated before every
    milestone. All of that is in the front matter, and none of it needs
    judgment. What still does is whether each item is really debt and whether
    the gate should open, which is why this prints two lists and no verdict.

    Each list is named for what it tests - whether an item carries the feature -
    and never for what the roadmap's rule decides. Which debt a milestone clears
    itself is whether its `Required scope` names the id, which `format_wave`
    reports over the frozen list, and the two sets differ in both directions.
    This printed its feature split as "Cleared by the milestone itself" until
    `PL-RFHH`, the phrase `format_wave` prints for the rule, so a reader of
    either took one answer for both and `PL-YVP7` was filed on the wrong one.
    """
    if not gate.items:
        # Every open debt item, so an empty store is the only way to get here:
        # naming the feature would say there is debt that does not carry it.
        return "No open debt in the store. Nothing to clear."

    lines = [
        f"{_plural(len(gate.items), 'open debt item', 'open debt items')} in the store"
        + (f", split by whether each carries `{gate.feature}`." if gate.feature else ".")
    ]

    lines.append("")
    lines.append(
        f"Not carrying `{gate.feature}` - {len(gate.outside)} ({effort_total(gate.outside)}):"
        if gate.feature
        else f"Open debt - {len(gate.outside)} ({effort_total(gate.outside)}):"
    )
    lines.extend(_gate_lines(gate.outside))

    if gate.feature:
        lines.append("")
        lines.append(
            f"Carrying `{gate.feature}` - {len(gate.inside)} ({effort_total(gate.inside)}):"
        )
        lines.extend(_gate_lines(gate.inside))
        if not gate.inside:
            lines.append("  nothing carries that feature")

    lines.append("")
    lines.append(f"Debt is an open item classed {', '.join(debt_classes)}, or at needs-decision.")
    lines.append("This reads the whole store, on a frozen list or not. `bin/docket wave` reads the")
    lines.append("frozen list, and counts as the milestone's own what its Required scope names -")
    lines.append("the roadmap's rule, which is not the feature: the two can differ both ways.")
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
    # First of the two run lines, because it is context for the headline above
    # it rather than for the findings below: a count read under library
    # defaults is a different claim from the same count read under the store's
    # own policy, and a reader who cannot see which has been told the store is
    # broken (`PL-K5PW`).
    if report.settings:
        lines.append(f"  {report.settings}")
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
    interrupted: str = "",
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

    if interrupted:
        lines.append("")
        lines.append(f"Unreleased: {_interrupted_cut(report, ready, interrupted)}")
    elif ready is not None and ready.shippable:
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


def format_wave(plan: Wave, items: Mapping[str, Item] | None = None) -> str:
    """Where the project stands on the cadence, and nothing about whether it should.

    A labelled line per fact and no more, because this is read at the top of a
    session beside the digest, not studied. Each one states a fact with the
    file it came from behind it; none of them says whether the plan is still
    the right plan.

    `items` is the store by id, which the deferral lines join against; without
    it every deferral reads as not in the store, which is what was given.
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
        lines.append(
            f'Gate      frozen list recorded under "{gate.milestone.title}" ({entries}, {ids})'
        )
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
            cost = _outside_cost(gate)
            waiting = [f"{cost} outside it"] if cost else []
            waiting += [_scope_cost(gate)] if gate.scope_items else []
            aside.append(
                f"{len(gate.waiting_outside)} waiting on "
                + (", and on ".join(waiting) or "work outside it")
            )
        if aside:
            counted += f" - {len(gate.clearable)} this gate can clear, " + ", ".join(aside)
        lines.append(f"          {counted}")
        if gate.clearable:
            open_ids = [identifier for entry in gate.clearable for identifier in entry.ids]
            lines.append(f"          {', '.join(open_ids)}")
        if gate.self_cleared:
            own = [identifier for entry in gate.self_cleared for identifier in entry.ids]
            # The test named beside the answer, because `format_gate` splits by
            # `feature` and the two differ in both directions (`PL-RFHH`).
            lines.append(
                "          named in its Required scope, so cleared by the milestone itself: "
                + ", ".join(own)
            )
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
            # The ids under the count above, so the reader can go and look at
            # what the gate is actually waiting for rather than take a number
            # for it. Milestones are named in that count and not repeated here:
            # a version is not a file anybody can open (`PL-FCM3`).
            if gate.outside_items:
                lines.append(f"          what they wait on: {', '.join(gate.outside_items)}")
            if gate.scope_items:
                scope = ", ".join(gate.scope_items)
                lines.append(f"          and in the milestone's Required scope: {scope}")
        if gate.unknown_ids:
            lines.append(
                f"          not in the store, so not countable: {', '.join(gate.unknown_ids)}"
            )

    lines.extend(_deferral_lines(plan, items or {}))
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


def _deferral_lines(plan: Wave, items: Mapping[str, Item]) -> list[str]:
    """Each item the gate defers, with its state and release from the store.

    A deferral is never withdrawn once written - that permanence is what "the
    gate is a snapshot" means - so the list alone cannot say which deferred
    items are still outstanding and which shipped. `ROADMAP.md` used to answer
    that with a release name written by hand beside each closed entry, which
    copied the `milestone:` field `docket release` stamps and was missed on 36
    of 84 closed entries (`PL-B60Q`). The store already holds both halves, so
    they are printed from it: an open item's status, a shipped item's release,
    a dropped item's date, and an item done but not yet cut says so rather than
    naming a release it has not had.

    The deferrals are the items whose `deferred-from:` names this gate's
    version, open and closed alike (`PL-WD5Z`). They were the leading ids of
    entries under a `ROADMAP.md` subsection headed `Declined`, `Deferred` or
    `Sequenced` until the disposition moved onto the item, so nothing here can
    now disagree with what `docket check` counts as disposed. Oldest capture
    first, which is the order the subsections recorded them in.
    """
    gate = plan.gate
    if gate is None:
        return []
    version = "v{}.{}.{}".format(*gate.milestone.version)
    deferred = sorted(
        (item for item in items.values() if split_deferred_from(item.deferred_from)[0] == version),
        key=lambda item: (item.added or date.min, item.identifier),
    )
    if not deferred:
        return []
    still_open: list[str] = []
    shipped: list[str] = []
    unreleased: list[str] = []
    dropped: list[str] = []
    for item in deferred:
        if item.is_open:
            still_open.append(f"{item.identifier} {item.status}")
        elif item.status == "done" and item.milestone:
            shipped.append(f"{item.identifier} in {item.milestone}")
        elif item.status == "done":
            unreleased.append(item.identifier)
        else:
            dropped.append(
                f"{item.identifier} on {item.closed}" if item.closed else item.identifier
            )

    closed = len(shipped) + len(unreleased) + len(dropped)
    lines = [
        f"Deferred  by `deferred-from: {version}`, off the frozen list of "
        f"{gate.milestone.label} ({_plural(len(deferred), 'item', 'items')})",
        f"          {closed} closed, {len(still_open)} open",
    ]
    for label, named in (
        ("open", still_open),
        ("shipped", shipped),
        ("done, not yet released", unreleased),
        ("dropped", dropped),
    ):
        if named:
            lines.append(f"          {label}: {', '.join(named)}")
    return lines


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


def _interrupted_cut(report: Report, ready: Readiness | None, version: str) -> str:
    """The release sentence while a cut is unfinished, for the digest and `status` alike.

    `readiness` leaves an interrupted cut's stamps out by its own contract, so
    what it counts is only the remainder the stopped run never reached: a
    twenty-item cut stopped after fifteen reads as an ordinary offer of five,
    with nothing saying why (`PL-1BS2`). The version and the notes it never
    wrote are named instead, with the command that finishes the cut - the
    same one `bin/docket release` prints when refusing another number over it.
    """
    stamped = sum(1 for item in report.items if item.milestone.strip() == version)
    total = stamped + (len(ready.shippable) if ready is not None else 0)
    return (
        f"a cut of {version} was interrupted: {stamped} item(s) carry "
        f"`milestone: {version}` and {NOTES_DIR}/{notes_name(version)} was never written. "
        f"Finish it before offering another - `make release VERSION={version.lstrip('v')}` "
        f"cuts all {total}."
    )


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


def _outside_cost(gate: GateStatus) -> str:
    """What the entries waiting outside the gate are waiting on, counted.

    Empty when the walk found nothing, which `gate_status` cannot produce - an
    entry reaches `waiting_outside` only by waiting on something - so the
    callers' fallbacks are a formatter declining to state a number it was not
    given, rather than a case to design around.
    """
    parts = []
    if gate.outside_milestones:
        parts.append(", ".join(gate.outside_milestones))
    if gate.outside_items:
        parts.append(_plural(len(gate.outside_items), "open item", "open items"))
    return " and ".join(parts)


def _scope_cost(gate: GateStatus) -> str:
    """The open items those entries wait on that the milestone's own scope names.

    Said apart from `_outside_cost`, because that work is the milestone's and
    implementing it clears it: folded into the outside count, it doubled what
    v0.6.0's gate waited on outside the milestone (`PL-FD5Q`).
    """
    count = _plural(len(gate.scope_items), "open item", "open items")
    return f"{count} the milestone's Required scope names"


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
            # Sized here as well as in the gate block above, because the digest
            # every session opens with prints this line and no other: unsized,
            # it put the whole cost of the milestone at the open-entry count
            # and nothing said otherwise (`PL-FCM3`).
            blocked = f"{len(plan.gate.waiting_outside)} blocked outside it"
            by = [_outside_cost(plan.gate)]
            by += [_scope_cost(plan.gate)] if plan.gate.scope_items else []
            joined = ", and by ".join(cost for cost in by if cost)
            aside.append(f"{blocked} by {joined}" if joined else blocked)
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
    # The sum is named as a sum and the distinct count printed beside it: a
    # figure a reader divides a per-edit rate by has to say which of the two it
    # is, since they part as soon as two refs edit one file (`PL-3BYK`).
    lines += [
        "",
        f"  ref set: {walk.listed} refs, {walk.merged} merged, {walk.unmerged} unmerged, "
        f"carrying {walk.commits} commits and {walk.item_edits} item-file edits summed per "
        f"ref, {_plural(walk.item_files, 'distinct item file', 'distinct item files')}",
    ]
    lines += [
        f"    {name:<52}{ahead:>5} commits{edits:>5} items" for name, ahead, edits in walk.refs
    ]
    return "\n".join(lines)
