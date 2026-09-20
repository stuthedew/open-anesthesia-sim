"""Whether this capture has already been filed, asked at the moment of filing.

`CLAUDE.md`'s capture rule is deliberately unconditional - "Do not ask whether
to record it" - because the alternative is losing findings. The cost it accepts
is that one defect gets diagnosed several times by sessions that cannot know
the first diagnosis exists, and that cost is paid at the only moment it is
cheap to catch: `bin/docket new` holds the title, the store and a session's
attention, and used to say nothing. Five captures of one defect across two days
is what it cost (`PL-TZ7T`).

**The key is the declared path, and the title only orders what the path
selected.** That is measured rather than assumed, and the obvious design is the
refuted one. Scoring title against title over the 1,362-item store catches 0 of
13 known duplicate pairs at any threshold that flags fewer than 768 pairs, and
the only clusters title similarity does find are the items *meant* to recur -
sixteen "Triage the N captures on DATE", three groups of release cuts and tags.
It fires hardest on exactly the set where firing is wrong. Nine of the same 13
pairs share a declared `touches` path, so shared path selects and title ranks
inside that selection, which puts the true duplicate in the top 3 for 8 of 9
(`PL-TZ7T` carries the table).

**It warns and never refuses.** The capture rule may not be made conditional on
a similarity score: a near-duplicate that is genuinely a second instance is a
legitimate filing, and a session stopped from writing an idea down is the
failure this whole mechanism is downstream of.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import CLOSED_STATUSES, Item, covers

#: Tokens carried by so many titles in a work queue that counting them would
#: measure grammar rather than subject. Deliberately short: a long list starts
#: deciding which *domain* words matter, which is the judgment this scoring
#: does not have and must not appear to have.
STOP_WORDS = frozenset(
    "the and are was were for with that this from its it is be been as at by of to in on an a or"
    " not but so than then when where which who whom whose will would can could should".split()
)

#: The shortest token worth counting. Two characters is `PL`, `py`, `is` - the
#: fragments an id or an extension leaves behind when a title is split on
#: punctuation, and never a word that distinguishes one defect from another.
MIN_WORD = 3

#: How similar two titles must be for a candidate to be worth printing, after
#: the shared path has already selected it. Measured against this store on
#: 2026-09-20 rather than chosen: the nine known duplicate pairs that share a
#: path score 0.133 to 0.244 against each other, so this floor suppresses none
#: of them, and it cuts the captures that print anything at all from 323 of 325
#: to 179 and the lines printed from 2.89 to 1.07.
#:
#: **The number that would make it wrong, and the count.** Raising it to 0.15
#: would cut firing further - to 74 of 325 - and is refused because it
#: suppresses 2 of the 9 measured true pairs, at 0.133 and 0.143. Lowering it
#: to zero is not the conservative choice it looks like: at that setting 323 of
#: 325 captures print three items each, which is a warning that fires every run
#: without changing a decision, and `CLAUDE.md` calls that a defect in the
#: check rather than coverage.
DISPLAY_FLOOR = 0.10

#: How many candidates to print. The measurement above is a top-3 measurement -
#: 8 of 9 - so printing fewer discards recall this key was chosen for, and
#: printing more spends a session's attention on ranks the evidence says are
#: usually wrong.
LIMIT = 3


@dataclass(frozen=True)
class Candidate:
    """One open item this capture may already have been filed as.

    `shared` and `score` are kept apart because they are different kinds of
    evidence and only one of them is a reason. The shared path is a fact about
    two declarations and is what selected this item; the score is a similarity
    over prose, which orders the selection and establishes nothing on its own.
    A reader deciding whether these are one defect reads the briefs, and this
    names which two to open.
    """

    item: Item
    shared: tuple[str, ...]
    score: float


def content_words(title: str) -> frozenset[str]:
    """The tokens of a title that carry its subject.

    Split on anything that is not alphanumeric, so an id, a path and a
    hyphenated phrase all come apart the same way, then drop the fragments too
    short to distinguish anything and the grammar.
    """
    words: set[str] = set()
    token = ""
    for character in title.lower():
        if character.isalnum():
            token += character
            continue
        if len(token) >= MIN_WORD and token not in STOP_WORDS:
            words.add(token)
        token = ""
    if len(token) >= MIN_WORD and token not in STOP_WORDS:
        words.add(token)
    return frozenset(words)


def similarity(one: str, other: str) -> float:
    """How much subject two titles share, as Jaccard overlap of content words.

    Jaccard rather than a count of shared words because titles in this store
    range from eight words to forty, and an unnormalised count would rank the
    longest title first for every capture regardless of subject.

    **This orders; it does not select.** A score here is meaningful only
    between two items already known to declare a common path - compared across
    the store it is the refuted key, and it would find the recurring-by-design
    items first.
    """
    left, right = content_words(one), content_words(other)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def shared_declared(paths: tuple[str, ...], item: Item) -> tuple[str, ...]:
    """Every declared path a capture and an existing item could both reach.

    A directory covers what is beneath it, so a capture declaring
    `subprojects/docket/tests` shares with an item declaring one test module
    inside it - the same reading `concurrency` gives the contention question,
    from the same comparison, so the two cannot drift apart on a trailing
    slash.
    """
    found = {
        min(left, right, key=len) for left in paths for right in item.touches if covers(left, right)
    }
    return tuple(sorted(found))


def near_duplicates(
    title: str,
    paths: tuple[str, ...],
    items: list[Item],
    *,
    limit: int = LIMIT,
    floor: float = DISPLAY_FLOOR,
) -> tuple[Candidate, ...]:
    """The open items this capture may be a second filing of, closest title first.

    Args:
        title: The capture being filed.
        paths: What the capture is expected to reach - its `--touches`, or what
            the working tree says the session is changing (`PL-THLT`). Empty
            means the search cannot run; see below.
        items: The store. Closed items are dropped here rather than by the
            caller, because a triage pass or a release cut is `done` within
            hours and those are exactly the titles that recur by design.
        limit: How many to return.
        floor: The similarity a candidate must clear to be worth printing.

    Returns:
        Candidates, highest score first, ties broken on the number of shared
        paths and then on the id so that two sessions filing the same title get
        the same answer.

    **No paths means no answer, and deliberately not a title-only search.**
    Falling back to scoring titles across the store is the key the measurement
    refuted: it would find the sixteen triage passes and none of the thirteen
    real duplicates, and it would do it on every capture made outside a git
    checkout. Returning nothing is the honest reading - the command then
    behaves as it did before this existed - and `PL-THLT` is what stops the
    common case reaching it, by supplying the paths from the working tree when
    the capture declares none.
    """
    if not paths:
        return ()

    scored: list[Candidate] = []
    for item in items:
        if item.status in CLOSED_STATUSES or not item.touches:
            continue
        shared = shared_declared(paths, item)
        if not shared:
            continue
        score = similarity(title, item.title)
        if score <= floor:
            continue
        scored.append(Candidate(item=item, shared=shared, score=score))

    scored.sort(key=lambda found: (-found.score, -len(found.shared), found.item.identifier))
    return tuple(scored[:limit])
