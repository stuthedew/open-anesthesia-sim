"""Whether this capture has already been filed, asked at the moment of filing.

`CLAUDE.md`'s capture rule is deliberately unconditional - "Do not ask whether
to record it" - because the alternative is losing findings. The cost it accepts
is that one defect gets diagnosed several times by sessions that cannot know
the first diagnosis exists, and that cost is paid at the only moment it is
cheap to catch: `bin/docket new` holds the title, the store and a session's
attention, and used to say nothing. Five captures of one defect across two days
is what it cost (`PL-TZ7T`).

**The key is a subject both declarations name, and the title only orders what
a subject selected.** That is measured rather than assumed, and the obvious
design is the refuted one. Scoring title against title over the 1,362-item
store catches 0 of 13 known duplicate pairs at any threshold that flags fewer
than 768 pairs, and the only clusters title similarity does find are the items
*meant* to recur - sixteen "Triage the N captures on DATE", three groups of
release cuts and tags. It fires hardest on exactly the set where firing is
wrong. Nine of the same 13 pairs share a declared `touches` path, so a shared
subject selects and title ranks inside that selection, which puts the true
duplicate in the top 3 for 8 of 9 (`PL-TZ7T` carries the table).

**A subject is one of three things, and the store directory is none of them.**
`PL-TZ7T`'s key was a shared declared path alone, and in its first two weeks
four duplicates fell through it by four different gaps (`PL-0HLS`):

- **A path outside the store**, declared or read off the working tree
  (`PL-THLT`), compared with `covers`.
- **One item's file.** A candidate declaring an item's file is about that item,
  and so is a capture naming it, by its file in the working tree or by its id
  in the title. The title is all a capture made on a clean tree has, and the
  housekeeping recipe makes its captures there (`PL-9VPH`: `PL-4CPP` named
  `PL-54V0`, whose file `PL-BYN2` declared).
- **The feature**, which a capture carries before triage writes `touches` and
  which survives a file move (`PL-TS7L`: `PL-YZ17` and `PL-5F76` declared no
  `touches` and one feature; `PL-6SV4`: `PL-VYK1` still declared the file its
  section had moved out of).
- **Not the store directory.** Every capturing branch changes it and every
  release cut declares it, so two items sharing it share nothing about a
  mechanism (`PL-SV0D`: it recorded `PL-DHGC` on `PL-JLBD`).

**The feature selects and is never counted.** A recurrence is evidence that a
defect fired again, and two items one feature groups were grouped on purpose:
probing each open item as a capture on 2026-10-12, the 20 that gained a
candidate on the feature alone each gained a sibling - one cut made across
`src/` and `tests/`, a check beside its instances - and none a second filing.
So `anchor` records on a path or an item only, and the feature shows a reader
where the capture's group already stands.

**Ids are read from the capture's title only**, and only against the item
files candidates declare. Reading them from both titles is `PL-85NT`'s refuted
referent key: on the same probes it showed a candidate for 16 titles with
nothing else to search on, where this shows none.

**What it cost, measured 2026-10-12** against the path-only key on the same
store: the same 7 of `PL-TZ7T`'s 13 pairs in the top three at today's floor,
either way round, and a candidate shown for 61 of the 303 open items probed
with their own fields, against 42, every one of the 19 added by the feature.
`PL-0HLS` carries the tables, and the bound on what no key can see.

**It warns and never refuses.** The capture rule may not be made conditional on
a similarity score: a near-duplicate that is genuinely a second instance is a
legitimate filing, and a session stopped from writing an idea down is the
failure this whole mechanism is downstream of.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .config import Config
from .model import CLOSED_STATUSES, Item, covers, is_under, live_recurrences
from .store import ID_PATTERN, declared_item_file

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
#:
#: Re-read under `PL-0HLS`'s key on 2026-10-12, over the 303 open items probed
#: with their own fields: 61 show a candidate (20%), against 42 (14%) for the
#: path-only key on the same store, so still under the 22% this was chosen at.
DISPLAY_FLOOR = 0.15

#: How many candidates to print. The measurement above is a top-3 measurement -
#: 8 of 9 - so printing fewer discards recall this key was chosen for, and
#: printing more spends a session's attention on ranks the evidence says are
#: usually wrong.
LIMIT = 3

#: An id written anywhere in a capture's title, in the grammar `store` exports.
_TITLE_ID = re.compile(ID_PATTERN)


@dataclass(frozen=True)
class Candidate:
    """One open item this capture may already have been filed as.

    The subjects and the score are kept apart because they are different kinds
    of evidence and only the subjects are reasons. `shared`, `named` and
    `feature` are facts about two declarations and are what selected this item:
    the paths outside the store both reach, the items whose file this one
    declares and the capture names, and the feature both carry. The score is a
    similarity over prose, which orders the selection and establishes nothing
    on its own. A reader deciding whether these are one defect reads the
    briefs, and this names which two to open.
    """

    item: Item
    shared: tuple[str, ...]
    score: float
    named: tuple[str, ...] = ()
    feature: str = ""

    @property
    def counted(self) -> bool:
        """Whether a filing matched here may be recorded as a recurrence.

        On a path or an item, never on the feature alone; the module docstring
        says why.
        """
        return bool(self.shared or self.named)


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


def shared_declared(paths: tuple[str, ...], item: Item, *, items_dir: str) -> tuple[str, ...]:
    """Every declared path outside the store a capture and an existing item could both reach.

    A directory covers what is beneath it, so a capture declaring
    `subprojects/docket/tests` shares with an item declaring one test module
    inside it - the same reading `concurrency` gives the contention question,
    from the same comparison, so the two cannot drift apart on a trailing
    slash.

    A path inside the store is compared on neither side. The directory is what
    every capturing branch changes, and one item's file is compared by its id
    in `near_duplicates` rather than as a path, so a slug that has drifted
    still names its item.
    """
    store = (items_dir,)
    found = {
        min(left, right, key=len)
        for left in paths
        for right in item.touches
        if not is_under(left, store) and not is_under(right, store) and covers(left, right)
    }
    return tuple(sorted(found))


def declared_items(entries: tuple[str, ...], items_dir: str) -> frozenset[str]:
    """The ids of the items whose files `entries` name inside the store."""
    found = (declared_item_file(entry, items_dir) for entry in entries)
    return frozenset(named[0] for named in found if named is not None)


def named_items(title: str, paths: tuple[str, ...], items_dir: str) -> frozenset[str]:
    """The items a capture is about by name: ids in its title, and item files among its paths.

    The title is read for ids and for nothing else. Its words select nothing,
    which is the refuted key, and an id is not a word: it is the one thing a
    capture made on a clean tree can name precisely, and a housekeeping title
    names the item it is about.
    """
    return frozenset(_TITLE_ID.findall(title)) | declared_items(paths, items_dir)


def near_duplicates(
    title: str,
    paths: tuple[str, ...],
    items: list[Item],
    *,
    feature: str = "",
    items_dir: str = Config.items_dir,
    limit: int = LIMIT,
    floor: float = DISPLAY_FLOOR,
) -> tuple[Candidate, ...]:
    """The open items this capture may be a second filing of, closest title first.

    Args:
        title: The capture being filed. The ids in it name items; its words
            only order.
        paths: What the capture is expected to reach - its `--touches`, or what
            the working tree says the session is changing (`PL-THLT`).
        items: The store. Closed items are dropped here rather than by the
            caller, because a triage pass or a release cut is `done` within
            hours and those are exactly the titles that recur by design. An
            open item declaring no `touches` is a candidate like any other,
            since capture leaves the field unset until triage (`PL-TS7L`).
        feature: The capture's `--feature`, or nothing.
        items_dir: The store, as a `touches` entry spells it - the directory
            that is no subject, and the prefix an item's file is read under.
        limit: How many to return.
        floor: The similarity a candidate must clear to be worth printing.

    Returns:
        Candidates, highest score first, ties broken on the number of paths
        and items shared and then on the id, so that two sessions filing the
        same title get the same answer.

    **No subject means no answer, and deliberately not a title-only search.**
    Falling back to scoring titles across the store is the key the measurement
    refuted: it would find the sixteen triage passes and none of the thirteen
    real duplicates. A capture with no path outside the store, no item named
    and no feature gets nothing - the command then behaves as it did before
    this existed - and `PL-THLT` is what stops the common case reaching it, by
    supplying the paths from the working tree when the capture declares none.
    """
    named = named_items(title, paths, items_dir)
    scored: list[Candidate] = []
    for item in items:
        if item.status in CLOSED_STATUSES:
            continue
        shared = shared_declared(paths, item, items_dir=items_dir)
        reached = tuple(sorted(named & declared_items(item.touches, items_dir)))
        grouped = feature if feature and item.feature == feature else ""
        if not (shared or reached or grouped):
            continue
        score = similarity(title, item.title)
        if score <= floor:
            continue
        scored.append(
            Candidate(item=item, shared=shared, score=score, named=reached, feature=grouped)
        )

    scored.sort(
        key=lambda found: (
            -found.score,
            -len(found.shared) - len(found.named),
            found.item.identifier,
        )
    )
    return tuple(scored[:limit])


def anchor(candidates: tuple[Candidate, ...]) -> Candidate | None:
    """Which of the printed candidates a recurrence is recorded onto, if any.

    The top-ranked one sharing a path or an item, except that one already
    carrying recurrences wins over a higher-scoring one that carries none. Both
    are matches the search already selected and printed; this only decides
    which of them the evidence accumulates on. A candidate the feature alone
    selected is never one, and a shortlist of only those records nothing: two
    items one feature groups were grouped on purpose, so a capture landing
    beside them is evidence of the group and not of a defect firing again
    (`PL-0HLS`).

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

    **What it cannot do is invent a cluster.** Every candidate it can pick
    already shares a path or an item and already cleared `DISPLAY_FLOOR`, so the
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
    counted = [found for found in candidates if found.counted]
    if not counted:
        return None
    return min(counted, key=lambda found: (-len(live_recurrences(found.item)), -found.score))
