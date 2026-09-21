"""The item: what a unit of work is, and how it is written down.

One item, one file. That single decision is what the rest of this package
exists to exploit. A queue kept in one shared document has to serialize
every writer, because two people adding work touch the same lines and two
people allocating an id read the same counter; a queue kept as one file per
item has nothing to serialize, because adding work means adding a file and
nobody else's file moves.

The format is markdown with a small front-matter block. Front matter is what
a tool reads; the body below it is what a person reads. Keeping them in one
file - rather than a database plus a description somewhere else - means the
machine-readable state and the human-readable brief can never drift apart,
and both arrive in a `git diff` for review.

Standard library only, so a session-start hook can run in a bare checkout
with no virtualenv.
"""

from __future__ import annotations

import re
from collections.abc import Collection
from dataclasses import dataclass, field
from datetime import date
from pathlib import PurePosixPath

# Front matter is a `---` fenced block of `key: value` lines at the top of the
# file. Deliberately not YAML: a real YAML parser is a dependency, and the
# subset that is actually wanted here - scalars and comma-separated lists - is
# a dozen lines of parsing that cannot surprise anyone.
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
FIELD_RE = re.compile(r"^([a-z][a-z0-9-]*):[ \t]*(.*)$")

# An indented line under a field: YAML's continuation of the value above it.
# Indentation is required rather than assumed, so a line at column zero that is
# not a `key: value` line stays what it has always been - a line belonging to no
# field, passed over. All 67 continuation lines in this store are indented
# (measured 2026-09-21).
CONTINUATION_RE = re.compile(r"^[ \t]+\S")

# A continuation spelling a YAML block-sequence entry, `  - value`. The space
# after the dash is what makes it one; `-value` is an ordinary word.
BLOCK_ENTRY_RE = re.compile(r"^[ \t]+-([ \t]|$)")

PRIORITIES = ("P0", "P1", "P2", "P3")
EFFORTS = ("S", "M", "L")

# `untriaged` is the capture state: an idea recorded before anyone has decided
# what it is worth. It exists so that writing something down costs nothing at
# the moment it occurs - no priority to guess, no band to choose, no other
# file to touch. Triage is the act of filling in the rest.
#
# `done` and `dropped` are terminal. Neither deletes the file: an item that
# leaves the queue leaves a record of why, because a finding dropped without a
# recorded reason gets raised again by the next person who notices it.
OPEN_STATUSES = ("untriaged", "ready", "needs-decision", "blocked")
CLOSED_STATUSES = ("done", "dropped")
STATUSES = OPEN_STATUSES + CLOSED_STATUSES

# Classes whose subject matter is safety-critical, and so may not sit in the
# lower priority bands however small the task looks.
SAFETY_CLASSES = ("safety", "science")

# Work on the development process rather than on the product it builds. An
# item counts as process work only when every one of its classes is in this
# set, so a `science`-and-`infra` item is still science.
PROCESS_CLASSES = ("session-cost", "docs", "infra")

LIST_FIELDS = ("classes", "touches", "blocked-by", "root-cause-of", "recurrences")

# How many distinct items a `root-cause-of:` has to name before the claim is a
# generator rather than an ordinary item. Three is the project owner's own
# threshold - "the root cause of more than 2 PLs" - and it is a floor rather
# than a measurement: two items sharing a cause is a coincidence a session can
# work singly, while a mechanism standing under three is paid again by every
# session it stands through.
MIN_ROOT_CAUSE_ITEMS = 3

# The two verdicts `generator:` may carry. The count above decides whether a
# generator is *recorded*; this decides whether it *ranks* (project owner,
# 2026-09-21, ratified, over keeping the count for both and accepting that any
# three-item cluster outranks a `safety`-classed `P1`). `live` is a claim about
# future inflow - the store is still handing this mechanism new members, so
# every session it stands through pays it again - and `spent` says the
# mechanism can no longer produce one.
#
# Named for the state rather than for the consequence. "ranking" is the word
# `CLAUDE.md` uses of the tier, and a field called that would make the record
# and the ranking one sentence again - which is the conflation this field
# exists to undo.
GENERATOR_VERDICTS = ("live", "spent")

# How many recorded recurrences make a cluster the size that floor describes.
# Derived rather than chosen, because the item is itself the first filing: an
# item carrying two recurrences has been filed three times, which is the three
# items a generator is the root cause of. Written as three, the counter would
# have demanded a *fourth* filing - a stricter bar than the generator rule
# wearing its number, and the slug-rename cluster (`PL-LBR6` with `PL-5QLP` and
# `PL-QMC0`, recorded as a generator by hand) would never have surfaced
# (project owner, 2026-09-20, ratified, over the literal three the design first
# specified).
MIN_RECURRENCES = MIN_ROOT_CAUSE_ITEMS - 1

# The second kind of entry `blocked-by` accepts: a milestone version, written
# exactly as the roadmap's timeline writes it.
#
# One field with two kinds of entry, rather than a `blocked-on-milestone:`
# beside it. An item whose real dependency is a milestone being *scoped* had no
# honest state while only ids were accepted: `blocked` with the field emptied
# is a store error, `blocked` naming a closed item is false, and `ready` invites
# a session to start against a target shape nobody has decided. The alternative
# keeps id parsing simple at the cost of two fields meaning one thing and every
# reader of `blocked-by` having to know about the second; one field with two
# kinds of entry is the smaller vocabulary (`PL-W8XP`).
#
# The two are told apart syntactically, and can never collide: an id is
# `PL-`-prefixed and a milestone is `v`-prefixed. An entry matching neither is
# a typo rather than a third kind, and `checks.py` refuses it by name.
MILESTONE_BLOCKER_RE = re.compile(r"^v\d+\.\d+\.\d+$")

# Efforts a delegated item may carry. An `L` item is a milestone in disguise;
# nothing that large has a brief precise enough to be worked without judgment.
DELEGABLE_EFFORTS = ("S", "M")

# The two halves of a project, as `docket next` divides them so that two
# sessions can run at once without racing for the same item.
#
# `CROSSING` and `UNPLACED` are the honest answers to a question the paths
# cannot settle: an item reaching both halves belongs to whichever session can
# hold the whole change, and an item declaring no `touches` has told nobody
# anything. Neither is offered to a single-lane session, and neither is hidden
# - `next` names them, and the unfiltered ranking still offers them.
LANE_PRODUCT = "product"
LANE_WORKFLOW = "workflow"
LANE_CROSSING = "crossing"
LANE_UNPLACED = "unplaced"

#: The lanes a caller may ask `recommend` for. `CROSSING` and `UNPLACED` are
#: outcomes of the test rather than requests: asking for the work nobody can
#: place is asking for a queue, which `list` already answers.
SELECTABLE_LANES = (LANE_PRODUCT, LANE_WORKFLOW)


def _unquote(value: str) -> str:
    """A value written as a quoted YAML scalar, with its quotes removed.

    Quoting is the correct instinct everywhere else, so a session writing a
    title with a colon in it quotes the way YAML requires - and this format,
    which takes the rest of the line verbatim, kept the quote characters as the
    first and last characters of the title. 56 titles and 3 `verify:` commands
    in this store carry a pair (measured 2026-09-21). A quoted `verify:` is
    worse than untidy: it is handed to a shell, which reads the whole command
    as one quoted word and exits 127 having run nothing, which is `PL-MZH2`
    exactly - repaired by hand on one item then, and three more have arrived
    since (`PL-V6CR`).

    The pair has to be a *complete* scalar - closing at the last character and
    nowhere earlier - or the value is taken verbatim as it always was. That is
    not fussiness. `PL-XF5V`'s `payoff:` opens with a quoted phrase, `'are the
    generators dealt with' is answered by ...`, and a rule that stripped the
    ends of anything merely beginning and ending with a quote would rewrite it
    into a string nobody wrote.

    Two escapes are read, and no more. `''` inside a single-quoted scalar is
    YAML's spelling of one quote, and two titles here use it; inside a
    double-quoted scalar, a backslash before a quote or before another
    backslash escapes it. Every other backslash stays a backslash, because
    turning a backslash-n into a newline is inventing a character the file does
    not hold, and nothing in this store asks for it.
    """
    quote = value[:1]
    if quote not in ("'", '"'):
        return value
    out: list[str] = []
    index = 1
    while index < len(value):
        char = value[index]
        if char == quote:
            if quote == "'" and value[index + 1 : index + 2] == "'":
                out.append("'")
                index += 2
                continue
            return "".join(out) if index == len(value) - 1 else value
        if quote == '"' and char == "\\" and value[index + 1 : index + 2] in ('"', "\\"):
            out.append(value[index + 1])
            index += 2
            continue
        out.append(char)
        index += 1
    return value


def _front_matter_pairs(text: str) -> tuple[list[tuple[str, str]], tuple[str, ...], str] | None:
    """Every field of the front matter, in file order, with the body.

    Pairs rather than a dict, because a dict is exactly where a repeated key
    stops being visible. `parse_front_matter` collapses them for callers that
    want the fields; `repeated_front_matter_keys` reads the same list to find
    the ones a collapse would have hidden. `None` when there is no front
    matter at all, which the callers report differently.

    **A line that is not a `key: value` line is not passed over.** It continues
    the value above it. Skipping it was one decision and it produced three
    separately-briefed defects (`PL-9HD1`): a multi-line value truncated at its
    first line by every reader and then deleted outright by the next write
    (`PL-5B39`), a `touches:` written as a YAML block list parsing to empty so
    the item reached no lane (`PL-FX0K`), and a value quoted the way YAML
    requires keeping its quote characters (`PL-V6CR`).

    Continuations are folded into the value with a single space, which is what
    YAML does to a plain scalar and what the 12 hand-wrapped `reason:` fields
    in this store mean. Folding is a faithful read rather than a guess, and it
    is what makes `render_item` safe on them: the value comes back on one line,
    where it used to come back 9 lines shorter.

    The middle element names the *list* fields written as a block list, which
    are refused instead. A list has one spelling here - one comma-separated
    line - and teaching the reader a second is a second thing every reader of
    an item has to know (`PL-FX0K`). Refused only for `LIST_FIELDS`, because
    that is where the ambiguity is: an indented `- ...` under a prose field is
    prose, and folds like any other continuation.
    """
    match = FRONT_MATTER_RE.match(text)
    if match is None:
        return None

    collected: list[tuple[str, str, list[str]]] = []
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        field_match = FIELD_RE.match(line)
        if field_match is not None:
            collected.append((field_match.group(1), field_match.group(2).strip(), []))
        elif collected and CONTINUATION_RE.match(line):
            collected[-1][2].append(line)

    pairs: list[tuple[str, str]] = []
    block_lists: list[str] = []
    for key, head, continuations in collected:
        if key in LIST_FIELDS and any(BLOCK_ENTRY_RE.match(line) for line in continuations):
            block_lists.append(key)
            pairs.append((key, ""))
            continue
        parts = [part for part in (head, *(line.strip() for line in continuations)) if part]
        pairs.append((key, _unquote(" ".join(parts))))
    return pairs, tuple(sorted(set(block_lists))), match.group(2)


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Split a document into its front-matter fields and its body.

    A file with no front matter yields no fields rather than an error; the
    caller decides whether that is a malformed item or simply not one.

    A repeated key collapses to its last occurrence here, which is what a dict
    can express. That is a lossy answer rather than a wrong one, and
    `parse_item` pairs it with `repeated_front_matter_keys` so the loss is
    reported instead of taken. Do not "fix" this by keeping the first instead:
    either choice picks a winner, and picking one silently is the defect
    (`PL-BR4G`). A list field written as a block list arrives empty for the
    same reason and is reported the same way, by `block_list_keys`.
    """
    parsed = _front_matter_pairs(text)
    if parsed is None:
        return {}, text
    pairs, _block_lists, body = parsed
    return dict(pairs), body


def repeated_front_matter_keys(text: str) -> tuple[str, ...]:
    """Front-matter keys the file spells more than once, sorted.

    The store is one file per item precisely so that two branches adding work
    cannot conflict, and that property has a sharp edge: two branches editing
    the *same* item, inserting the same field at different line positions,
    also do not conflict. Git merges both lines, the dict keeps whichever came
    last, and every check downstream reads a value nobody chose. Observed on
    `main` 2026-09-02 with two `pr:` lines that happened to agree.
    """
    parsed = _front_matter_pairs(text)
    if parsed is None:
        return ()
    pairs, _block_lists, _body = parsed
    seen: set[str] = set()
    repeated: set[str] = set()
    for key, _value in pairs:
        if key in seen:
            repeated.add(key)
        seen.add(key)
    return tuple(sorted(repeated))


def block_list_keys(text: str) -> tuple[str, ...]:
    """List fields the file writes as a YAML block list, sorted.

    The dangerous third of the cluster `PL-9HD1` groups, and the only one of
    the three that reaches the safety pin. `touches:` written this way parsed
    to an empty tuple and the item was offered to no lane; `classes:` written
    this way is worse, because `checks.py` seats a `safety`- or
    `science`-classed item at `P0` or `P1` only when it can see the class - so
    work a clinician could be misled by would sit in the bottom band with
    `bin/docket check` reporting zero errors. That is `PL-MVC2` arriving
    through the parser instead of through a misspelling, and `known_classes`
    cannot catch it, because there is no class there to reject (`PL-FX0K`).

    Recorded rather than read. Nothing here learns the block form: `checks.py`
    names the field and the repair, which is what an ambiguous field is owed -
    guessing at one is how a validation failure becomes a silently wrong queue
    position.
    """
    parsed = _front_matter_pairs(text)
    if parsed is None:
        return ()
    _pairs, block_lists, _body = parsed
    return block_lists


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@dataclass(frozen=True)
class Item:
    """One unit of work, as stored in one file.

    Every field a tool branches on lives in the front matter, and every field
    a person needs to start the work cold lives in the body. The split is the
    point: `touches` is there so the conflict graph can be computed without a
    model reading prose, and the brief is there so the work can be picked up
    by someone who was not present when it was written down.
    """

    identifier: str
    title: str
    priority: str
    effort: str
    status: str
    classes: tuple[str, ...]
    touches: tuple[str, ...]
    blocked_by: tuple[str, ...]
    feature: str
    milestone: str
    added: date | None
    closed: date | None
    commit: str
    reason: str
    body: str
    #: The pull request that carried the work, as a bare number. Recorded
    #: beside `commit` rather than instead of it, because the two answer
    #: different questions: `commit` names the branch commit, which a
    #: squash-merge discards, while the number is known before the merge and
    #: outlives it. Defaulted empty like the fields below, so an item written
    #: before the field existed still parses.
    pr: str = ""
    #: One plain-language line of what closing this item buys - faster, fewer
    #: bugs reaching `main`, a check that stops lying, a release that stops
    #: needing a person to remember a step. The consequence, never a
    #: restatement of the title: a title is written for the session that will
    #: implement the item and so names a mechanism, which is a string the
    #: project owner cannot weigh (2026-09-19).
    #:
    #: Stored rather than composed on demand, because a session offering an
    #: item otherwise rebuilds the sentence from the brief at full context, in
    #: every session that offers it. Nothing can infer it: the brief argues
    #: the case in the same mechanism vocabulary the title uses, and which
    #: consequence matters to a reader is judgment. So `checks.py` holds this
    #: field to *presence* and nothing else - see `_payoff_required`.
    payoff: str = ""
    #: The command that proves this item done. Defaulted empty rather than
    #: required, so an item written before the field existed - or captured
    #: without one - is simply not delegable, which is the safe reading.
    verify: str = ""
    #: The reason a qualifying item is withheld from delegation. Presence is
    #: the switch; there is deliberately no field that grants delegability.
    not_delegable: str = ""
    #: Enough of an assertion to name the one subject this item's work makes
    #: untrue. Not *weakened* - falsified: the string the assertion pins is
    #: what the item was commissioned to delete, so no arrangement of the
    #: tests keeps it. `verify` folds a matching removal out of its "no
    #: existing assertion removed" check and prints what it folded, which is
    #: the only route that check has ever had for a correct close-out
    #: (`PL-K82G`).
    #:
    #: A substring rather than the exact line, because an exact line breaks on
    #: reformatting and on the commas a real assertion carries; one subject
    #: rather than a list, because an item falsifying several unrelated
    #: assertions is doing several things. `checks.py` refuses a fragment too
    #: short to name anything.
    #:
    #: `verify` reads this field from the *base's* copy of the item, never
    #: from the branch's - the declaration is worth something only as the
    #: reviewer's text, written before the work. Editing it here changes what
    #: a later branch is measured against, and nothing about the branch that
    #: writes it.
    falsifies: str = ""
    #: The items this one is the root cause of - three or more of them, or it
    #: is an ordinary item. `CLAUDE.md` makes a mechanism causing three or more
    #: items a *generator*, which ranks above everything but `P0`, and this
    #: field is what makes that a recorded fact rather than the next session's
    #: inference. Nothing can infer it: a ratio over a `touches` path measures
    #: how busy a file is, and citation is not causation - 33 items in this
    #: store are cited by more than two others, and promoting all of them would
    #: mean nothing (`PL-VX5H`). So the session that identifies a generator
    #: writes it down, and `tools/generator_check.py` surfaces candidates for
    #: that judgment without making it.
    #:
    #: Resolution and the three-item floor live in `root_cause_faults`, which
    #: `checks.py` and `plan.py` both read, so the checker and the ranking
    #: cannot disagree about what counts as a claim.
    root_cause_of: tuple[str, ...] = ()
    #: Whether the mechanism `root_cause_of` records is still being handed new
    #: members, as `live - why` or `spent - why`. The count above decides
    #: whether a generator is *recorded*; this decides whether it *ranks*
    #: (project owner, 2026-09-21, ratified, over keeping the count for both
    #: and accepting that any three-item cluster outranks a `safety`-classed
    #: `P1`). The tier is the only rank above such an item, so what sits in it
    #: has to be scarce: a mechanism paid again by every session it stands
    #: through earns that, and one that can no longer produce a member does
    #: not, however much damage its existing three did.
    #:
    #: **A verdict and a reason, because both states are recorded ones.**
    #: `impairs_generators` is a one-sided claim - present is a claim, absent
    #: is silence - and that shape cannot carry this, where `spent` is an
    #: assertion a reader may want to overturn rather than the absence of one.
    #: So the verdict is an exact word from `GENERATOR_VERDICTS`, which is
    #: decidable, and the reason beside it is the judgment, which is not. The
    #: refused alternative was reading the verdict out of the item's own prose:
    #: `CLAUDE.md` refuses to script the judgment half, and a tool inferring
    #: "still generating" from a brief would be guessing at exactly that half
    #: while looking authoritative.
    #:
    #: **Recording it does not rank it; claiming `live` does.** An item with a
    #: sound `root_cause_of` and no verdict at all is recorded and unranked.
    #: `docket check` is a separate command, so a store is routinely ranked
    #: before it is validated - the argument `root_cause_faults` already makes
    #: about a mistyped id - and the unvalidated state therefore has to be the
    #: one that cannot buy a promotion over a `safety`-classed `P1`. Absent,
    #: the field fails toward the ordinary band, where the item is still
    #: visible in `docket generators` and the checker says what is missing.
    #:
    #: Soundness lives in `generator_faults`, read by both `checks.py` and
    #: `plan.py`, so the checker and the ranking cannot disagree about what a
    #: verdict is - the arrangement `root_cause_faults` and
    #: `generator_defect_faults` both already have.
    generator: str = ""
    #: Every time a session filed a capture that `bin/docket new` matched to
    #: this item, as `DATE PL-XXXX` entries - the date of the filing and the id
    #: of the capture that matched. A re-filing is not only waste: it is
    #: evidence that the defect *fired again*, a session hit it, had no idea an
    #: item existed, and paid the diagnosis a second time. `CLAUDE.md`'s
    #: generator rule ranks on exactly that property - "every session it stands
    #: through pays it again" - and what was missing is that the evidence had to
    #: be *asserted* by a session that happened to notice. `PL-STC4` documents
    #: its own duplication three times in its own prose and nothing was promoted
    #: until a session read the cluster by hand, five captures later.
    #:
    #: **It surfaces a candidate; it never promotes one.** `README.md` calls
    #: `root-cause-of:` "the one place in the store where a typo would buy a
    #: promotion", so letting a title-similarity heuristic write that field - or
    #: rank as though it had - would reintroduce the hazard `docket check`'s
    #: validation closes, on a match that is a judgment about prose. The count
    #: is recorded as auditable fact, both ids are named so a reader can open
    #: both briefs, and a session confirming the cluster writes `root-cause-of:`
    #: by hand as it always has.
    #:
    #: **Two branches appending on the same day conflict, and that is the right
    #: trade.** This is the one field a second session can edit on an item
    #: neither of them is working, so two captures matched to one item in the
    #: same window put two versions of one line in front of a merge. The
    #: resolution is always to keep both entries, and the alternative - an index
    #: or a manifest beside the items - is `docs/dead-ends.md`'s first rejected
    #: design, for a conflict surface spanning the whole store rather than one
    #: line of one item.
    #:
    #: **`priority:` could not have carried it** (project owner, 2026-09-20,
    #: ratified, over counting repeat filings and raising the band). `checks.py`
    #: pins `P1` to `safety` and `science`, and `CLAUDE.md` forbids promoting
    #: process work into that band to move it up the order - and every item this
    #: counter fires on is workflow work. The generator tier is the lever that
    #: exists and already means what a recurrence count measures.
    recurrences: tuple[str, ...] = ()
    #: Why this item is a defect in the machinery that identifies and ranks
    #: generators - the sibling entrance to the tier `root_cause_of` opens.
    #: A generator earns that tier because three items stand on it; a defect
    #: in the machinery earns it one level up, because while identification is
    #: broken a generator is not recorded, and an unrecorded generator is
    #: ranked by nothing. The suppressed cost is invisible in a way the
    #: generator's is not: nothing in a store says a generator went unfound
    #: (project owner, 2026-09-19).
    #:
    #: Prose, never a boolean, for the reason `not_delegable` is prose: the
    #: field lifts an item above every band but `P0`, so a reader is owed
    #: which function is impaired rather than an unexplained promotion.
    #:
    #: Soundness lives in `generator_defect_faults`, read by both `checks.py`
    #: and `plan.py`, so the checker and the ranking cannot disagree about
    #: what a claim is - the same arrangement `root_cause_faults` already has.
    impairs_generators: str = ""
    #: The item file's name inside the store directory - `PL-K7QX-do-it.md`,
    #: never `docs/items/PL-K7QX-do-it.md`. A repository path is that name
    #: joined to the store directory, which is what `verify.front_matter_check`
    #: does; built without the join, the `git show` it feeds asks for a path no
    #: ref holds, and the miss is indistinguishable from a clean comparison
    #: (`PL-20PT`).
    path: str = ""
    unknown_fields: tuple[str, ...] = field(default_factory=tuple)
    duplicate_fields: tuple[str, ...] = field(default_factory=tuple)
    #: List fields the file spells as a YAML block list, which this format does
    #: not read. Reported alongside the value like the two above, rather than
    #: guessed at: the entries a block list holds are the one thing a reader
    #: here must not invent, because an empty `classes:` is what defeats the
    #: safety pin (`PL-FX0K`).
    block_list_fields: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_open(self) -> bool:
        return self.status in OPEN_STATUSES

    @property
    def is_untriaged(self) -> bool:
        return self.status == "untriaged"

    @property
    def blocking_milestones(self) -> tuple[str, ...]:
        """The `blocked-by` entries naming a roadmap milestone, as written.

        A milestone blocker clears when the milestone is *scoped* - when it has
        the four subsections `ROADMAP.md` requires of it - rather than when it
        ships. What such an item waits on is the decision the scoping round
        makes, not the release: `PL-B9PY` could not be designed until v0.5.0
        settled what a side-by-side comparison renders, and could be the moment
        it did, four releases before v0.5.0 goes out.
        """
        return tuple(e for e in self.blocked_by if MILESTONE_BLOCKER_RE.match(e) is not None)

    @property
    def blocking_items(self) -> tuple[str, ...]:
        """The `blocked-by` entries naming a queue item.

        Every reader asking "which *items* must close first" wants this rather
        than the raw field, which may also carry milestones.

        Defined as the complement of `blocking_milestones` rather than by
        matching the id grammar, so that the partition is fail-closed: an entry
        of neither shape - a typo, or a syntax a later version invents - stays
        here and is refused by name in `checks.py`, where an unrecognised
        blocker is already an error. Recognising ids positively would let such
        an entry fall out of both halves and be silently ignored, which on a
        field that decides what may be started is the wrong way to fail.
        """
        milestones = set(self.blocking_milestones)
        return tuple(e for e in self.blocked_by if e not in milestones)

    @property
    def is_process_work(self) -> bool:
        """Whether this improves how the project is developed, not the product."""
        return bool(self.classes) and all(c in PROCESS_CLASSES for c in self.classes)

    def lane(self, workflow_paths: tuple[str, ...]) -> str:
        """Which half of the project this work sits in, from its declared paths.

        Decided from `touches` rather than from `classes`, and the difference
        is not academic. `classes` describes what *kind* of work an item is -
        a defect, a refactor - which is orthogonal to what it edits: a bug in
        this package and a bug in the simulator are both `defect`. Measured
        against this store on 2026-09-04, the `classes` reading placed 33 of
        145 open items on the wrong side, eighteen of them workflow defects
        that a simulator session would then have been offered. `touches` is
        already declared on 142 of those 145, already validated, and already
        the field the conflict graph and the delegation guard read.

        Four answers, and the two that are not a side are deliberate:

        - `LANE_WORKFLOW` - every declared path is workflow apparatus.
        - `LANE_PRODUCT` - no declared path is.
        - `LANE_CROSSING` - some are and some are not, so the change cannot be
          made whole by a session confined to either side.
        - `LANE_UNPLACED` - nothing is declared, so this cannot be answered.

        Empty `workflow_paths` returns `LANE_UNPLACED` for everything, which
        fails closed: a project that has not drawn the boundary gets no lane
        rather than a lane drawn by the tool on its behalf.
        """
        if not workflow_paths or not self.touches:
            return LANE_UNPLACED
        inside = [is_under(path, workflow_paths) for path in self.touches]
        if all(inside):
            return LANE_WORKFLOW
        if not any(inside):
            return LANE_PRODUCT
        return LANE_CROSSING

    @property
    def safety_classes(self) -> tuple[str, ...]:
        return tuple(c for c in self.classes if c in SAFETY_CLASSES)

    @property
    def model_guidance(self) -> str | None:
        """Whether this item is reasoning-heavy enough to warrant the strongest model.

        Safety- or science-classed work, and any item whose next step is an
        unresolved design decision, is not routine execution. Encoded here
        rather than left to each session to remember, so the recommendation
        does not depend on someone re-deriving the rule.
        """
        if self.safety_classes:
            return f"{'/'.join(self.safety_classes)}-tagged"
        if self.status == "needs-decision":
            return "open design decision"
        return None

    def delegability(
        self, protected_paths: tuple[str, ...], gate_paths: tuple[str, ...]
    ) -> str | None:
        """Why this item may *not* be handed to a cheaper model, or None if it may.

        Derived, never stored, and that asymmetry is the whole safeguard. There
        is no `delegable: yes` to set, so no session - least of all a worker
        tidying front matter on its way past - can mark its own work eligible.
        The only writable control is `not-delegable`, which withholds an item
        that would otherwise qualify. Delegability can be taken away by hand
        and never granted by hand.

        A returned string is the reason, phrased to be printed. `None` means
        every condition below is met:

        - the work is startable at all (`ready`, so not blocked and not
          awaiting a decision);
        - `model_guidance` is silent, which excludes safety- and
          science-classed work and open design decisions by the rule that
          already existed rather than by a second one written here;
        - a `verify:` command exists, because without one "done" is a
          judgment and there is nothing for a reviewer to trust instead;
        - `touches` is declared and wholly outside the protected paths, so the
          diff's blast radius is known before the work starts;
        - `touches` is also outside the gate paths, because `verify` fails any
          diff that edits them and an item offered here would be refused
          after the work was done rather than before it was started;
        - the effort is one a precise brief can actually cover.

        The two path lists are read differently when *empty*, and the
        difference is not an oversight. `protected_paths` has no default, so
        empty means a project has never said which of its files produce
        consequential output, and the safe reading of silence is to offer
        nothing. `gate_paths` ships with a real default, so empty can only be
        a project that cleared it deliberately - and one that has told
        `verify` to stop auditing its checks has not asked this to start.
        """
        if self.not_delegable:
            return f"withheld: {self.not_delegable}"
        if not protected_paths:
            return "no protected paths configured"
        if self.status != "ready":
            return f"status is {self.status or 'unset'}, not ready"
        guidance = self.model_guidance
        if guidance is not None:
            return guidance
        if not self.verify:
            return "no `verify:` command"
        if not self.touches:
            return "declares no `touches`"
        protected = [path for path in self.touches if is_under(path, protected_paths)]
        if protected:
            return f"touches protected path(s) {', '.join(protected)}"
        # Reported after the protected paths and phrased differently, because
        # the two prohibitions differ in kind: one guards a clinical value and
        # the other guards the measurement. A reader who cannot tell them
        # apart learns to read neither.
        gates = [path for path in self.touches if is_under(path, gate_paths)]
        if gates:
            return f"touches the checks themselves: {', '.join(gates)}"
        if self.effort not in DELEGABLE_EFFORTS:
            return f"effort {self.effort or 'unset'} is not {' or '.join(DELEGABLE_EFFORTS)}"
        return None

    def sort_key(self) -> tuple[int, int, str]:
        """Order for display: priority band, then effort, then id.

        Untriaged items sort after everything triaged, because they are not
        yet candidates for work - they are candidates for a decision.
        """
        band = PRIORITIES.index(self.priority) if self.priority in PRIORITIES else len(PRIORITIES)
        if self.is_untriaged:
            band = len(PRIORITIES) + 1
        effort = EFFORTS.index(self.effort) if self.effort in EFFORTS else len(EFFORTS)
        return (band, effort, self.identifier)


def root_cause_faults(item: Item, known: Collection[str]) -> tuple[str, ...]:
    """Why an item's `root-cause-of:` is not a generator claim, or `()`.

    One predicate with two readers, which is the point of writing it here
    rather than in either of them. `checks.py` turns each fault into an error;
    `plan.py` ranks a claim only when this returns nothing. A second copy of
    the rule would be a second chance for the checker and the ranking to
    disagree about what a claim is - on a field whose whole purpose is to lift
    an item above every band but `P0`.

    Ranking on the field's mere presence would be the wrong way to fail.
    `docket check` is a separate command, so a store is routinely ranked
    before it is validated: a field naming two ids, or naming an id that does
    not resolve, would otherwise outrank a `safety`-classed `P1` until
    somebody happened to run the checker.

    An item carrying no field at all has made no claim and has no faults. That
    is not the same answer as a sound claim, and `is_generator` is where the
    two are told apart.

    Counted over *distinct* ids, with the item's own removed: three entries
    spelling one id name one item, and a floor a repetition defeats is not a
    floor.
    """
    if not item.root_cause_of:
        return ()

    faults: list[str] = []
    named = list(dict.fromkeys(item.root_cause_of))
    if item.identifier and item.identifier in named:
        faults.append("lists itself among the items it is the root cause of")
        named = [i for i in named if i != item.identifier]

    missing = [i for i in named if i not in known]
    if missing:
        faults.append(f"names {', '.join(missing)}, which no item in this store carries")

    # Reported over what is *written* rather than over what resolved, so a
    # typo and a short list stay two findings with two repairs. A field naming
    # `PL-A, PL-NOPE` is both, and saying only "resolves to one item" would
    # hide the typo behind a count.
    if len(named) < MIN_ROOT_CAUSE_ITEMS:
        faults.append(
            f"names {len(named)} item(s); a generator is the root cause of at least "
            f"{MIN_ROOT_CAUSE_ITEMS}, and below that it is an ordinary item"
        )
    return tuple(faults)


def is_generator(item: Item, known: Collection[str]) -> bool:
    """Whether this item carries a sound, resolvable generator claim.

    The question `recommend` asks before lifting an item above every band but
    `P0`. Presence and soundness are deliberately one test here: an unsound
    claim ranks as an ordinary item, and `docket check` is what tells somebody
    it was unsound.
    """
    return bool(item.root_cause_of) and not root_cause_faults(item, known)


def split_generator_verdict(value: str) -> tuple[str, str]:
    """A `generator:` value as its verdict and its reason, neither validated.

    The verdict is the leading run of letters, so `live - why`, `live: why`,
    `spent, why` and `live` all read the same way; whatever separator follows
    it is stripped off the reason. Forgiving about punctuation and exact about
    vocabulary, which is the split this field needs: the word is the decidable
    half and the sentence after it is the judgment, and a reader who wrote a
    colon where the README wrote a dash has made no mistake worth an error.

    Returns `("", "")` for an empty value, which is the same answer as an
    absent field - `generator_faults` is where a field present-but-empty is
    told apart from one that was never written, since only it knows whether
    the item makes a generator claim at all.
    """
    text = value.strip()
    verdict = ""
    for char in text:
        if not char.isalpha():
            break
        verdict += char
    return verdict.lower(), text[len(verdict) :].strip(" -\u2013\u2014:,;").strip()


def generator_faults(item: Item, known: Collection[str]) -> tuple[str, ...]:
    """Why an item's recurrence verdict is not usable, or `()`.

    The third predicate built this way, and for the third time the reason is
    that `checks.py` and `plan.py` must not drift about what a claim is on a
    field that decides whether an item outranks a `safety`-classed `P1`.

    **Only where a verdict could still move something.** A closed item is
    never startable, so `recommend` never ranks one and a verdict written onto
    it is read by nothing - which is `generator_candidates`' own test for the
    window `root-cause-of:` acts in, arriving here. Demanding one anyway would
    mean backfilling every head this project has already closed with a
    retrospective judgment about a mechanism that session did not diagnose,
    which invents the audit fact rather than recording it.

    **An absent verdict on an open generator is a fault, not a default.** The
    ranking already fails safe without it - `ranks_as_generator` refuses to
    rank what does not claim `live` - so this is not what protects the tier.
    What it catches is the quiet half the two checks beside it catch: the
    session that recorded a live generator and believes it is now ranked,
    where nothing else in the project would ever say it is not.

    A verdict without a `root-cause-of:` is faulted from the other end. It
    judges the recurrence of a cluster the item does not record, so the reader
    is told which field is missing rather than left with a line that ranks
    nothing and looks like it should.
    """
    verdict, reason = split_generator_verdict(item.generator)
    sound_claim = is_generator(item, known)

    if not item.generator:
        if sound_claim and item.status not in CLOSED_STATUSES:
            return (
                "is absent, so this generator is recorded and unranked; write "
                f"`{GENERATOR_VERDICTS[0]}` with the evidence the store is still handing "
                f"this mechanism new members, or `{GENERATOR_VERDICTS[1]}` with why it "
                "can no longer produce one",
            )
        return ()

    faults: list[str] = []
    if not item.root_cause_of:
        faults.append(
            "judges the recurrence of a cluster this item does not record; write the "
            "`root-cause-of:` naming the items the mechanism explains, or drop this field"
        )
    if verdict not in GENERATOR_VERDICTS:
        shown = f"`{verdict}`" if verdict else "no verdict"
        faults.append(
            f"opens with {shown}; it has to open with one of "
            f"{', '.join(f'`{v}`' for v in GENERATOR_VERDICTS)}, which is the half of this "
            "field a tool may read"
        )
    elif not reason:
        faults.append(
            f"states `{verdict}` and no reason; the verdict decides whether this outranks "
            "every band, so a reader is owed what the mechanism is still doing - or has "
            "stopped doing - rather than an unexplained rank"
        )
    return tuple(faults)


def ranks_as_generator(item: Item, known: Collection[str]) -> bool:
    """Whether this item's generator claim earns the tier, not merely the record.

    Two tests, and `CLAUDE.md` puts them on different axes: the count decides
    whether a generator is *recorded* - `is_generator`, three or more items
    standing on one mechanism - and the recurrence verdict decides whether it
    *ranks* above every band but `P0`. A cluster whose mechanism is spent is
    recorded all the same, for the audit, and ranks on its own band.

    Opt-in rather than opt-out, so a claim nobody has qualified ranks nothing.
    `docket check` runs separately from `next`, and the field it validates is
    the one the README calls the place where a typo would buy a promotion; the
    unvalidated reading therefore has to be the conservative one. The cost is
    that a live generator whose verdict was never written waits on its band
    until the checker is run, which is recoverable and loud. The cost the
    other way is a spent cluster outranking a `safety`-classed `P1`, which is
    the outcome the ratified decision exists to remove.
    """
    return is_generator(item, known) and split_generator_verdict(item.generator)[0] == "live"


def generators_explaining(identifier: str, items: Collection[Item]) -> tuple[Item, ...]:
    """The items whose sound `root-cause-of:` names this one - the reverse edge.

    The field is recorded on the head alone, so both readers it had asked the
    forward question: `checks.py` whether a claim is valid, `plan.py` whether
    to rank one above its band. A session reaching a *member* by name - the way
    the project owner usually starts an item - asked nothing and was told
    nothing, and worked it as an ordinary item while the generator above it was
    still being decided, which is the one-at-a-time patching the field exists
    to stop (`PL-C97K`).

    Soundness is the same test the other two use, and for the same reason: a
    claim `plan.py` refuses to rank and `docket check` reports as an error must
    not be announced anywhere as an explanation. Three readers, one definition
    of what a claim is. It also settles the self-listing case without a guard
    of its own - a head naming itself is faulted, so it is not a generator and
    no item is ever reported as explaining itself.

    `known` spans every item, the closed ones included, exactly as
    `plan.recommend` builds it: a root cause still explains an item that has
    since closed, so the edge must not decay as its cluster is worked.

    Ordered by id rather than by the store's iteration order, so that the
    answer does not depend on how the files happen to be named.
    """
    known = {item.identifier for item in items if item.identifier}
    return tuple(
        sorted(
            (
                head
                for head in items
                if identifier in head.root_cause_of and is_generator(head, known)
            ),
            key=lambda head: head.identifier,
        )
    )


def generator_defect_faults(item: Item, generator_paths: tuple[str, ...]) -> tuple[str, ...]:
    """Why an item's `impairs-generators:` is not a machinery claim, or `()`.

    The second entrance to the generator tier, and it is built like the first.
    `checks.py` turns each fault into an error; `plan.py` ranks a claim only
    when this returns nothing. One predicate with two readers, so the checker
    and the ranking cannot drift on a field whose whole purpose is to lift an
    item above every band but `P0`.

    **Why `touches` refutes a claim and cannot make one.** The machinery is a
    few functions living inside files that do many other things. Measured
    against this project's store on 2026-09-19, 36 of 322 open items declare
    one of those files for unrelated reasons, so deriving the claim from the
    path would promote 36 items and mean nothing - which is the objection
    `tools/generator_check.py` already records against citation density at 33.
    So the claim is the declaring session's judgment, recorded in prose, and
    the path test is only the cheap falsifier: it rejects a claim on an item
    that never goes near the machinery. Exactly the division
    `root_cause_faults` draws with its three-item floor, which also refutes a
    claim without ever establishing one.

    An item carrying no field has made no claim and has no faults, which is
    not the same answer as a sound claim; `impairs_generators_soundly` is
    where the two are told apart.
    """
    if not item.impairs_generators:
        return ()

    faults: list[str] = []
    if item.impairs_generators.strip().lower() in ("no", "yes", "true", "false"):
        faults.append(
            "holds the reason the machinery is impaired, not a boolean; write which "
            "function of generator identification or ranking this defect breaks"
        )
    # Reported separately from the path test below, because an undeclared
    # `generator_paths` is the project's omission and a `touches` that misses
    # it is the item's. One repair is a config edit and the other is an item
    # edit, and a single message would send a reader to the wrong file.
    if not generator_paths:
        faults.append(
            "cannot be placed: this project declares no `generator_paths`, so no item "
            "can be shown to touch the machinery and every such claim is unsound"
        )
    elif not item.touches:
        faults.append(
            "declares no `touches`, so nothing places the defect inside the machinery; "
            "name the file the impaired function lives in"
        )
    elif not any(is_under(path, generator_paths) for path in item.touches):
        faults.append(
            f"declares {', '.join(item.touches)}, none of which is inside "
            f"`generator_paths` ({', '.join(generator_paths)})"
        )
    return tuple(faults)


def impairs_generators_soundly(item: Item, generator_paths: tuple[str, ...]) -> bool:
    """Whether this item carries a sound claim to be a generator-machinery defect.

    The second question `recommend` asks before lifting an item onto the
    generator tier. Presence and soundness are one test here for the reason
    they are one in `is_generator`: an unsound claim ranks as an ordinary
    item, and `docket check` is what tells somebody it was unsound.
    """
    return bool(item.impairs_generators) and not generator_defect_faults(item, generator_paths)


def covers(one: str, other: str) -> bool:
    """Whether two declared paths can reach the same file.

    A directory covers everything beneath it, so an item declaring
    `src/anesthesia_sim/app/` reaches the same files as one declaring a single
    view module inside it, and a capture declaring `subprojects/docket/tests`
    reaches the module an existing item names there.

    Symmetric, which is what separates it from `is_under`: that asks whether
    one path falls inside a fixed set of roots - the delegation and lane
    partitions - and this asks whether two declarations, neither of them a
    root, could meet. Both live here so that the two path comparisons this
    package makes sit in one file rather than giving a session two places to
    get a trailing slash wrong.
    """
    first, second = PurePosixPath(one.strip("/")), PurePosixPath(other.strip("/"))
    return first == second or first in second.parents or second in first.parents


#: The word that turns a recorded filing into a withdrawn one, written between
#: the entry and the withdrawal that disowns it: `2026-09-20 PL-S8JT withdrawn
#: 2026-09-21 PL-34BG`. Spelt out rather than punctuated so that the file says
#: what it means to somebody reading the markdown with no tool in front of them.
WITHDRAWN_MARKER = "withdrawn"


@dataclass(frozen=True)
class Recurrence:
    """One filing `bin/docket new` matched to this item, as recorded.

    Both halves are kept because both are what makes the count auditable
    rather than a score. The date says when the defect fired again, which is
    the property the generator tier ranks on; the id names the capture, so a
    reader can open that brief beside this one and decide for themselves
    whether the two are one problem - the judgment this mechanism refuses to
    make.

    `raw` survives a reading that failed, so a malformed entry can be reported
    in the words it was written in rather than dropped.

    `withdrawn` and `withdrawn_by` carry a match a session later judged wrong:
    the date it was disowned, and the item whose brief says why. The entry is
    annotated rather than deleted, so a withdrawal is as visible as the write
    it undoes - a deleted entry leaves a file that reads as though the match
    was never made, which is a quieter record than the one that was there
    before (`PL-34BG`). Both are `None`/`""` on a live entry, and a tail that
    does not read exactly as `withdrawn DATE PL-XXXX` leaves them that way for
    `recurrence_faults` to report: a botched hand edit then counts as a live
    filing and raises an error, rather than silently cancelling one.
    """

    when: date | None
    identifier: str
    raw: str
    withdrawn: date | None = None
    withdrawn_by: str = ""


def recurrences_of(item: Item) -> tuple[Recurrence, ...]:
    """The recorded recurrences, parsed, malformed entries included.

    An entry that does not read as `DATE PL-XXXX` comes back with whatever
    could be recovered from it rather than being skipped, because a count that
    silently drops what it cannot read is a count that says a defect fired
    fewer times than it did - the failure the apparatus standard's floor names
    exactly. `recurrence_faults` is what reports it.
    """
    found: list[Recurrence] = []
    for entry in item.recurrences:
        parts = entry.split()
        when = _parse_date(parts[0]) if parts else None
        identifier = parts[1] if len(parts) > 1 else ""
        disowned, by = _withdrawal(parts[2:])
        found.append(
            Recurrence(
                when=when, identifier=identifier, raw=entry, withdrawn=disowned, withdrawn_by=by
            )
        )
    return tuple(found)


def _withdrawal(tail: list[str]) -> tuple[date | None, str]:
    """The `withdrawn DATE PL-XXXX` suffix of an entry, or `(None, "")` for anything else.

    Exact, and deliberately unforgiving: a tail this cannot read leaves the
    entry live rather than half-withdrawn, which is the direction that fails
    loudly. `recurrence_faults` reports the same tail as an error, so the
    reading and the complaint agree.
    """
    if len(tail) != 3 or tail[0] != WITHDRAWN_MARKER:
        return None, ""
    when = _parse_date(tail[1])
    return (when, tail[2]) if when is not None and tail[2] else (None, "")


def live_recurrences(item: Item) -> tuple[Recurrence, ...]:
    """The filings still standing: every recorded entry but the withdrawn ones.

    What every count, signal and display reads. A withdrawn entry is the record
    of a match that was made and then disowned, not evidence that the defect
    fired again, so it has to stay in the file and out of the arithmetic both.
    `recurrences_of` is the raw field, for a reader that wants those too.
    """
    return tuple(found for found in recurrences_of(item) if found.withdrawn is None)


def recurrence_count(item: Item) -> int:
    """How many distinct captures this item has absorbed.

    Distinct, and for the reason `root_cause_faults` counts distinct ids: one
    capture recorded twice names one filing, and a floor a repetition defeats
    is not a floor. An entry naming no id counts for nothing, since it names
    no filing that can be read, and a withdrawn one counts for nothing because
    the match it records has been disowned.
    """
    return len({found.identifier for found in live_recurrences(item) if found.identifier})


def recurrence_faults(item: Item, known: Collection[str]) -> tuple[str, ...]:
    """Why a `recurrences:` entry cannot be read as a filing, or `()`.

    Written like `root_cause_faults` and read by `checks.py` the same way,
    though it defends against a weaker hazard: this field surfaces a candidate
    and never promotes one, so a bad entry cannot mis-rank anything. What it
    can do is make the count wrong in the quiet direction - an entry nobody can
    resolve is a filing the store cannot show you - and nothing else in the
    project would ever say so.

    The field is tool-written, so every fault here is a hand edit that went
    wrong, which is why these are exact rules and so errors rather than
    advisories.

    A withdrawal is held to the same exactness, and it is the half where a
    quiet failure costs most: an entry whose `withdrawn` tail cannot be read
    still counts as a live filing, so a mis-typed withdrawal leaves the store
    asserting a match somebody has already disowned. Both halves of the tail
    are checked - that it reads at all, and that the item it cites for the
    reasoning exists to be read.
    """
    if not item.recurrences:
        return ()

    faults: list[str] = []
    unreadable = [f.raw for f in recurrences_of(item) if f.when is None or not f.identifier]
    if unreadable:
        faults.append(
            f"records {', '.join(repr(entry) for entry in unreadable)}, which does not read "
            "as `DATE PL-XXXX` - the date the capture was filed, then its id"
        )

    unwithdrawable = [
        f.raw
        for f in recurrences_of(item)
        if f.withdrawn is None and len(f.raw.split()) > 2 and f.when is not None and f.identifier
    ]
    if unwithdrawable:
        faults.append(
            f"records {', '.join(repr(entry) for entry in unwithdrawable)}, whose tail does not "
            f"read as `{WITHDRAWN_MARKER} DATE PL-XXXX` - the date the match was withdrawn, then "
            "the item whose brief says why. An entry nothing can read as withdrawn is one that "
            "still counts"
        )

    named = list(dict.fromkeys(f.identifier for f in recurrences_of(item) if f.identifier))
    if item.identifier and item.identifier in named:
        faults.append("names itself among the captures that recurred onto it")

    missing = [i for i in named if i != item.identifier and i not in known]
    if missing:
        faults.append(f"names {', '.join(missing)}, which no item in this store carries")

    disowned = list(dict.fromkeys(f.withdrawn_by for f in recurrences_of(item) if f.withdrawn_by))
    unknown = [i for i in disowned if i not in known]
    if unknown:
        faults.append(
            f"is withdrawn by {', '.join(unknown)}, which no item in this store carries - a "
            "withdrawal is auditable only through the brief it cites"
        )
    return tuple(faults)


def is_under(path: str, roots: tuple[str, ...]) -> bool:
    """Whether one declared path falls inside any of `roots`.

    Compared as `/`-separated path prefixes rather than as strings, so that
    `core/` covers `core/blood.py` while `docs/MODEL.md` does not also cover a
    hypothetical `docs/MODEL.md.bak`. Matching by bare string prefix would
    silently include the wrong things and, worse, silently fail to include the
    right ones.

    Shared by the two path partitions this package draws - what delegation may
    not modify, and which half of the project an item belongs to - because a
    second copy of this comparison is a second chance to get the trailing
    slash wrong in only one of them.
    """
    candidate = path.strip().strip("/")
    for root in roots:
        target = root.strip().strip("/")
        if not target:
            continue
        if candidate == target or candidate.startswith(target + "/"):
            return True
    return False


def parse_item(text: str, path: str = "") -> Item:
    """Read one item file.

    Missing fields come back empty rather than defaulted. Nothing here
    substitutes a plausible value for an absent one: an item with no priority
    is an item with no priority, and `checks.py` decides whether that is
    allowed for its status. Guessing would turn a validation failure into a
    silently wrong queue position.
    """
    fields, body = parse_front_matter(text)
    known = {
        "id",
        "title",
        "priority",
        "effort",
        "status",
        "classes",
        "touches",
        "blocked-by",
        "feature",
        "milestone",
        "added",
        "closed",
        "commit",
        "pr",
        "reason",
        "payoff",
        "verify",
        "not-delegable",
        "falsifies",
        "root-cause-of",
        "generator",
        "impairs-generators",
        "recurrences",
    }
    return Item(
        identifier=fields.get("id", ""),
        title=fields.get("title", ""),
        priority=fields.get("priority", ""),
        effort=fields.get("effort", ""),
        status=fields.get("status", ""),
        classes=_split_list(fields.get("classes", "")),
        touches=_split_list(fields.get("touches", "")),
        blocked_by=_split_list(fields.get("blocked-by", "")),
        feature=fields.get("feature", ""),
        milestone=fields.get("milestone", ""),
        added=_parse_date(fields.get("added", "")),
        closed=_parse_date(fields.get("closed", "")),
        commit=fields.get("commit", ""),
        pr=fields.get("pr", ""),
        reason=fields.get("reason", ""),
        payoff=fields.get("payoff", ""),
        verify=fields.get("verify", ""),
        not_delegable=fields.get("not-delegable", ""),
        falsifies=fields.get("falsifies", ""),
        root_cause_of=_split_list(fields.get("root-cause-of", "")),
        generator=fields.get("generator", ""),
        impairs_generators=fields.get("impairs-generators", ""),
        recurrences=_split_list(fields.get("recurrences", "")),
        body=body,
        path=path,
        unknown_fields=tuple(sorted(set(fields) - known)),
        duplicate_fields=repeated_front_matter_keys(text),
        block_list_fields=block_list_keys(text),
    )


#: Every front-matter key, in the order a writer emits them. Data rather than
#: a literal inside `render_item`, because two writers now depend on it: that
#: one, which rewrites a whole file, and `with_front_matter_field`, which puts
#: a single line into a file it otherwise leaves byte-for-byte alone. A second
#: copy of this sequence would be a second chance for the two to disagree
#: about where a field belongs, and the disagreement would surface as a diff
#: rather than as an error (`PL-7K8Y`).
FIELD_ORDER = (
    "id",
    "title",
    "priority",
    "effort",
    "status",
    "classes",
    "feature",
    "milestone",
    "touches",
    "blocked-by",
    "added",
    "closed",
    "commit",
    "pr",
    "reason",
    "payoff",
    "verify",
    "not-delegable",
    "falsifies",
    "root-cause-of",
    "generator",
    "impairs-generators",
    "recurrences",
)

#: Written even when empty. A file carrying neither is not an item, and one
#: rendered without them reads back as a different, emptier item rather than
#: as a malformed file anything would report.
ALWAYS_RENDERED = ("id", "title")


def _front_matter_values(item: Item) -> dict[str, str]:
    """Each front-matter key's value as a string, ready to be written."""
    return {
        "id": item.identifier,
        "title": item.title,
        "priority": item.priority,
        "effort": item.effort,
        "status": item.status,
        "classes": ", ".join(item.classes),
        "feature": item.feature,
        "milestone": item.milestone,
        "touches": ", ".join(item.touches),
        "blocked-by": ", ".join(item.blocked_by),
        "added": item.added.isoformat() if item.added else "",
        "closed": item.closed.isoformat() if item.closed else "",
        "commit": item.commit,
        "pr": item.pr,
        "reason": item.reason,
        "payoff": item.payoff,
        "verify": item.verify,
        "not-delegable": item.not_delegable,
        "falsifies": item.falsifies,
        "root-cause-of": ", ".join(item.root_cause_of),
        "generator": item.generator,
        "impairs-generators": item.impairs_generators,
        "recurrences": ", ".join(item.recurrences),
    }


def render_item(item: Item) -> str:
    """Write one item file.

    Fields are emitted in a fixed order and empty ones are omitted, so that
    rewriting a file the tool has already written is a no-op. A round trip
    that reorders keys would put noise in every diff and make review harder,
    which is the opposite of why the state is kept in git at all.

    That no-op holds only for a file this function wrote. A hand-typed one
    whose keys are in some other order comes back reordered, and a value
    spread over continuation lines comes back on one line - both correct
    renderings, and both a removal in the diff. Where the caller is adding a
    field rather than rewriting the item, `with_front_matter_field` is the
    writer that has no such effect.

    The one-line form now keeps every character of the value, which is the
    whole of what `PL-5B39` was: `_front_matter_pairs` folded nothing, so this
    emitted the first line of a multi-line value and deleted the rest of the
    file's copy on the way past - 9 of `PL-9HDH`'s 10 `reason:` lines, at exit
    0. A reflow is a diff to read; that was a deletion nothing reported.
    """
    values = _front_matter_values(item)
    lines = [
        f"{name}: {values[name]}" for name in FIELD_ORDER if values[name] or name in ALWAYS_RENDERED
    ]
    body = item.body if item.body.endswith("\n") else item.body + "\n"
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body.lstrip("\n")


def with_front_matter_field(text: str, name: str, value: str, *, append: bool = False) -> str:
    """Add one front-matter field to an item file, changing nothing else in it.

    `render_item` is the wrong writer for this, and the reason is what
    `PL-7K8Y` cost. It renders from the parsed `Item`, so it normalises the
    whole block on the way past: a hand-typed key order comes back canonical,
    and a value continued over indented lines comes back on one. Both are
    removals in the diff, and `verify.sanctioned_queue_edit` classifies a
    queue edit as the `pr` backfill the close-out is told to make only when
    the diff removes nothing at all. So `bin/docket record`, following the
    skill exactly, produced a `REJECT` on any item whose block was not already
    canonical - and because the classifier reads the per-commit diffs rather
    than the net tree, putting the order back in a later commit left both the
    removal and its undo on the branch. Rebuilding the history was the only
    remedy.

    Inserting a line settles it at the source instead of teaching the
    classifier to forgive a removal, which is the narrower of the two fixes
    the item weighed: "no removed lines" stays exact, and exact is what makes
    the exemption safe to grant. It also reaches further than key order for
    free - the continuation lines of a multi-line value survive an insert
    without anything having to know they are there, and 12 item files in this
    store carry one.

    The field goes after the last key already present that `FIELD_ORDER` puts
    before it, so on a file this package wrote the result is byte-identical to
    `render_item`'s and on any other one it is a pure addition. A key the
    order does not name, and the continuation lines of a value, are passed
    over rather than inserted between.

    `append` is for a list field that grows one entry at a time -
    `recurrences:`, which `bin/docket new` extends on every matched filing. It
    adds `, value` to the end of the field's existing line and is otherwise
    this same insert, so a second, third and tenth entry are as byte-faithful
    as the first. Without it the only way to extend a field was to re-render
    the file, which is exactly what `PL-7K8Y` cost: `sanctioned_queue_edit`
    forgives a queue edit that removes nothing, and a re-render removes every
    line it normalises on the way past.

    Raises `ValueError` where the field is already present and `append` was not
    asked for, where the file spells the field more than once so that no single
    line is the one to extend, or where there is no front matter to add it to.
    Each means the caller asked for something this cannot express, and each is
    a bug rather than a state to paper over: `cmd_record` establishes that the
    field is absent before it writes, and `docket check` reports a doubled key.
    """
    if name not in FIELD_ORDER:
        raise ValueError(f"`{name}` is not a front-matter field")
    match = FRONT_MATTER_RE.match(text)
    if match is None:
        raise ValueError("the file has no front matter to add a field to")
    # `split("\n")` rather than `splitlines()`, which is the exact inverse of
    # the join the offset below assumes. `splitlines()` also breaks on `\x0b`
    # and `\u2028`, either of which would put the insertion point somewhere
    # other than where the line index says - and the whole worth of this
    # function is that every other byte is left where it was.
    lines = match.group(1).split("\n")
    present = [
        index
        for index, line in enumerate(lines)
        if (field := FIELD_RE.match(line)) and field.group(1) == name
    ]
    if present and not append:
        raise ValueError(f"the item already records `{name}`")
    if len(present) > 1:
        raise ValueError(f"the item spells `{name}` {len(present)} times")
    if present:
        # Past the continuation lines of the existing value, so a field spread
        # over several lines grows at its end rather than in the middle of
        # itself. 12 item files in this store carry a multi-line value.
        last = present[0]
        while (
            last + 1 < len(lines)
            and lines[last + 1].strip()
            and FIELD_RE.match(lines[last + 1]) is None
        ):
            last += 1
        head = "\n".join(lines[: last + 1])
        return (
            text[: match.start(1) + len(head)] + f", {value}" + text[match.start(1) + len(head) :]
        )

    rank = FIELD_ORDER.index(name)
    insert_at, precedes = 0, False
    for index, line in enumerate(lines):
        field = FIELD_RE.match(line)
        if field is not None:
            key = field.group(1)
            precedes = key in FIELD_ORDER and FIELD_ORDER.index(key) < rank
        if precedes:
            insert_at = index + 1

    # Spliced at an offset into the original text rather than rebuilt from the
    # parts, so that "changes nothing else" is a property of the operation
    # instead of a claim about the reconstruction. Rebuilding has to restate
    # the fence and the separator, and a file whose `---` carries no trailing
    # newline comes back with one - a removal, which is the whole defect.
    head = "\n".join(lines[:insert_at])
    at = match.start(1) + (len(head) + 1 if insert_at else 0)
    return text[:at] + f"{name}: {value}\n" + text[at:]


def with_front_matter_value(text: str, name: str, value: str) -> str:
    """Replace one front-matter field's value, leaving every other byte as it was.

    The fourth writer, and the one the other three cannot be: `write_item` and
    `rewrite_item` re-render the whole block, and `with_front_matter_field`
    only ever adds - by design, since `sanctioned_queue_edit` reads a removal
    as tampering and a re-render removes every line it normalises on the way
    past (`PL-7K8Y`).

    A withdrawal has to edit a line that is already there, so it cannot be an
    insert; what it can be is an edit whose diff is *one* line, which is what
    this buys. That diff is deliberately not exempt from the close-out audit -
    unlike the append `bin/docket new` makes, a withdrawal is a deliberate act
    with something to gain, so the item doing it declares the file it touches
    like any other work (`PL-34BG`).

    Raises `ValueError` where the field is absent, where the file spells it
    more than once so that no single line is the one to replace, or where there
    is no front matter at all. Each is a caller asking for something this
    cannot express: `cmd_withdraw` establishes the field is there before it
    writes, and `docket check` reports a doubled key.
    """
    if name not in FIELD_ORDER:
        raise ValueError(f"`{name}` is not a front-matter field")
    match = FRONT_MATTER_RE.match(text)
    if match is None:
        raise ValueError("the file has no front matter to change a field in")
    # `split("\n")` for the reason `with_front_matter_field` splits that way:
    # it is the exact inverse of the join the offsets below assume.
    lines = match.group(1).split("\n")
    present = [
        index
        for index, line in enumerate(lines)
        if (field := FIELD_RE.match(line)) and field.group(1) == name
    ]
    if not present:
        raise ValueError(f"the item records no `{name}` to change")
    if len(present) > 1:
        raise ValueError(f"the item spells `{name}` {len(present)} times")
    # Through the continuation lines of the existing value, so a field spread
    # over several lines is replaced whole rather than left with an orphaned
    # tail. Collapsing it onto one line is a removal in the diff, and an
    # honest one: the value really did change.
    first = last = present[0]
    while (
        last + 1 < len(lines)
        and lines[last + 1].strip()
        and FIELD_RE.match(lines[last + 1]) is None
    ):
        last += 1
    before = "\n".join(lines[:first])
    through = "\n".join(lines[: last + 1])
    start = match.start(1) + (len(before) + 1 if first else 0)
    return text[:start] + f"{name}: {value}" + text[match.start(1) + len(through) :]
