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

from .model import CLOSED_STATUSES, Item, covers, live_recurrences

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
#: the shared path has already selected it. Measured rather than chosen, and
#: re-measured once: `PL-DGP0`, filed by the branch that yielded `PL-TZ7T`, is
#: why it is 0.15 and not the 0.10 this shipped with.
#:
#: **The number that would make it wrong, and the count** (2026-09-20, through
#: this function at `LIMIT`, over the 18 pairs of the five recorded duplicate
#: clusters and all 321 open items declaring a path, each probed as a simulated
#: capture):
#:
#: | floor | pairs caught | clusters reaching the threshold | fires on |
#: | --- | --- | --- | --- |
#: | 0.10 | 13 of 18 | 2 of 5 | 178/321 (55%) |
#: | 0.15 | 11 of 18 | 2 of 5 | 70/321 (22%) |
#: | 0.20 | 7 of 18 | 2 of 5 | 24/321 (7%) |
#:
#: 0.15 loses two *pairs* - `PL-5MFL`/`PL-4FD2` at 0.147 and
#: `PL-5QLP`/`PL-QMC0` at 0.143 - and loses no *cluster*: every one is still
#: caught at its second filing, and the same two still reach `MIN_RECURRENCES`.
#: Pair recall is the wrong measure of this mechanism, which is what made 0.10
#: look necessary. What it exists to do is surface a cluster, and a cluster's
#: later pairs are redundant once `anchor` has one member accumulating.
#:
#: The 60% cut in firing is the whole of what is bought, and it is not cosmetic:
#: `CLAUDE.md` calls a check that fires every run without changing a decision a
#: defect in the check, because it trains a session to skim the output where a
#: real advisory also appears. 0.20 is refused - it still holds those two
#: clusters, and `PL-BYMX`/`PL-KSCW` at 0.184 is the next thing to go.
#:
#: **This is threshold-dependent, which is the trap.** At the literal three the
#: design first specified, 0.15 surfaced *nothing* and 0.10 surfaced one
#: cluster, so the floor genuinely mattered. Deriving `MIN_RECURRENCES` from the
#: generator floor is what made the higher floor free. Re-measure both together
#: if either moves.
DISPLAY_FLOOR = 0.15

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


def anchor(candidates: tuple[Candidate, ...]) -> Candidate | None:
    """Which of the printed candidates a recurrence is recorded onto.

    The top-ranked one, except that a candidate already carrying recurrences
    wins over a higher-scoring one that carries none. Both are matches the
    search already selected and printed; this only decides which of them the
    evidence accumulates on.

    **Without it the counter never fires, which is measured rather than
    argued.** Replaying the two real clusters through the search as if it had
    existed when they were filed - each member arriving in filing order against
    the rest of the store - the top-ranked candidate is a different item almost
    every time, because each new capture is most similar to the *previous*
    capture rather than to the diagnosis at the head of the cluster. The five
    suppression-check filings spread as 2 + 1 + 1 and peak at two; anchoring
    them collects 3 on `PL-5MFL` and crosses the threshold. A cluster whose
    evidence is split three ways is a cluster nothing surfaces, which is the
    state this mechanism exists to end.

    **What it cannot do is invent a cluster.** Every candidate here already
    shares a declared path and already cleared `DISPLAY_FLOOR`, so the
    preference reorders a shortlist and never extends it. The effect is
    bounded at three items by `LIMIT`, and each entry names the capture it came
    from, so a reader who thinks the anchor is wrong can see exactly which
    filings were attributed to it.

    **Withdrawn entries are not evidence and do not attract more of it.** A
    reader who disowns a match is saying this item is not where that filing
    belonged, so counting the disowned entry would send the next capture to the
    same wrong place - the one way a single bad match could compound into a
    cluster (`PL-34BG`).
    """
    if not candidates:
        return None
    return min(candidates, key=lambda found: (-len(live_recurrences(found.item)), -found.score))
