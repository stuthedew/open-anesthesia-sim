"""Whether an idea about to be captured is one the store already carries.

`CLAUDE.md`'s capture rule is deliberately unconditional - "Do not ask whether
to record it" - because the alternative is losing findings. The cost it accepts
is that the same defect gets diagnosed more than once by sessions that have no
way to know the first diagnosis exists, and that cost is real: `PL-LBR6` sat
`ready` for six days with the `docket record` rename diagnosed and a `verify:`
command written against it, while `PL-5QLP` and `PL-QMC0` were filed as fresh
discoveries of the same mechanism. Five occurrences are on record.

`bin/docket new` is the only moment the duplicate is cheap to catch: it has the
title, the store and a session's attention. Every later mechanism costs more -
`feature:` grouping needs somebody to already know the items are one problem,
and the backlog sweep that found the first cluster read 145,000 tokens across
twelve agents.

**This warns; it never refuses.** The capture rule may not be made conditional
on a similarity score, and a near-duplicate that is genuinely a second instance
is a legitimate filing. So the reader decides and the item is written either
way.

**The key is the shared path, and title similarity only ranks.** Measured over
the 1,362-item store on 2026-09-20, title similarity alone is useless: it caught
0 of 13 known duplicate pairs at any threshold that flagged fewer than 768
pairs store-wide, because each session describes the same defect from the angle
that bit it - "reads prose as code", "reads every added line regardless of file
type", "greps every added line for the three marker substrings". Those score
0.121-0.276 against each other. Worse, the clusters title similarity *does*
find at a usable threshold are the items meant to recur: sixteen "Triage the N
captures on DATE", and three groups of release cuts and tags. It fires on
exactly the wrong set.

Shared `touches` selects, and then title similarity ranks within that set.
`PL-TZ7T` carries the original table, which counted a bare shared path and
found nine of thirteen. Counting a declared *directory* as covering the files
beneath it - the same rule `bin/docket concurrent` already applies, and the one
used here - all twelve of the recorded pairs share a path, and the true partner
ranks in the top three for eight of them. What the constants below are set
against is a per-cluster count rather than either of those.

Two consequences the design takes from the same measurement. **Only open items
are scored**, which drops the recurring-by-design clusters for free - a triage
pass or a release cut is `done` within hours - while still catching the real
thing there, `PL-Z0C7` being a second session cutting `v0.4.31` while `PL-R5VS`
was open. And **candidate paths are an argument rather than a field read**, so
that a capture carrying no `touches` of its own can be given paths inferred
from the working tree without this module learning what a working tree is
(`PL-THLT`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .concurrency import covers
from .model import Item

#: Title words carrying no signal about which defect is being described. Kept
#: short on purpose: every word removed here is one the ranking can no longer
#: use, and the vocabulary that separates two briefs about `verify` is ordinary
#: English - "reads", "line", "prose". Only words that appear in roughly any
#: sentence are listed, so the list is closed-class function words and nothing
#: else. Domain words a reader might think are noise - "new", "item", "docket" -
#: are deliberately absent.
STOPWORDS = frozenset(
    """
    a an and are as at be been but by can cannot could did do does for from had
    has have how if in into is it its may might must no not of on or should so
    than that the their them then there these they this to too was were what
    when where which while who whose will with without would
    """.split()
)

#: How many candidates a filing prints, and the floor one must clear to be
#: printed at all. Measured together on 2026-09-20 over this store, against the
#: six recorded duplicate clusters and all 321 open items that declare a path:
#:
#: | floor | limit | clusters caught at the 2nd filing | fires on | lines |
#: | --- | --- | --- | --- | --- |
#: | 0.10 | 5 | 5 of 6 | 61% of filings | 3.0 |
#: | 0.15 | 3 | 5 of 6 | 26% of filings | 1.8 |
#: | 0.20 | 3 | 5 of 6 | 10% of filings | 1.4 |
#:
#: The second row is chosen, and the first is what it is chosen over. Loosening
#: to 0.10/5 buys exactly one additional filing - `PL-QMC0`, the *third* member
#: of a cluster whose second member the tighter setting already flagged - and
#: pays 2.3 times the fire rate for it. That is the wrong trade twice over: by
#: the third filing the cluster is already surfaced and grouped, and an advisory
#: firing on three filings in five is one a session learns to skim, which
#: `CLAUDE.md` calls a defect in the check rather than extra coverage. Recall is
#: therefore measured per cluster at its *second* filing - the moment a
#: duplicate diagnosis is still unpaid for - and not per pair, which counts the
#: same cluster's later members as if catching them were worth the same.
#:
#: The one cluster missed at every setting is `PL-BYMX`/`PL-SH9Q` (rank 6,
#: similarity 0.200), which is also the only cluster of the six never confirmed
#: to be one mechanism.
DEFAULT_LIMIT = 3

#: The similarity a candidate must reach to be worth printing. With no floor at
#: all this fires on 100% of filings that declare a path, because 23 open items
#: declare `cli.py` alone and any of them will rank somewhere.
MIN_SIMILARITY = 0.15

_WORD_RE = re.compile(r"[a-z0-9]+")


def content_words(title: str) -> frozenset[str]:
    """The words of a title that say what it is about.

    Case and punctuation are dropped, so `verify`, `Verify` and `verify's`
    are one word; single characters and closed-class function words are
    dropped as carrying no signal about which defect is described.
    """
    words = _WORD_RE.findall(title.lower())
    return frozenset(word for word in words if len(word) > 1 and word not in STOPWORDS)


def similarity(one: str, other: str) -> float:
    """How far two titles overlap, as Jaccard over their content words.

    Jaccard rather than a raw count of shared words so that a long title
    cannot outrank a short one merely by having more words to share. Two
    titles with no content words at all score 0 rather than dividing by zero.
    """
    left, right = content_words(one), content_words(other)
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


@dataclass(frozen=True)
class Match:
    """One open item a filing may be a second diagnosis of.

    `paths` is why this item is a candidate at all and `score` is only why it
    sorts where it does - keeping both means a reader can see that the
    evidence is the shared file rather than the wording.
    """

    item: Item
    score: float
    paths: tuple[str, ...]


def _shared(declared: tuple[str, ...], candidates: tuple[str, ...]) -> tuple[str, ...]:
    """Every declared path the two sets could both reach.

    Directory coverage counts, on `concurrency.covers`, so an item declaring
    `subprojects/docket/` is a candidate against one naming a module inside
    it. One spelling of "these paths overlap" for the whole package: two would
    drift, and this one is already the answer `bin/docket concurrent` gives.
    """
    found = {left for left in declared for right in candidates if covers(left, right)}
    return tuple(sorted(found))


def near_duplicates(
    title: str,
    paths: tuple[str, ...],
    items: list[Item],
    limit: int = DEFAULT_LIMIT,
    floor: float = MIN_SIMILARITY,
) -> list[Match]:
    """The open items a filing of this title and these paths may duplicate.

    Selection is the shared path and ranking is the title, per the measurement
    in the module docstring. Ties break on the identifier so that two runs over
    one store print the same order - the store is read from a directory listing
    and nothing else here would fix the order.

    With no candidate paths there is no key, so the answer is empty rather than
    a title-only search: title similarity was measured and refused.
    """
    if not paths:
        return []
    matches = [
        Match(item=item, score=similarity(title, item.title), paths=shared)
        for item in items
        if item.is_open and (shared := _shared(item.touches, paths))
    ]
    ranked = [match for match in matches if match.score >= floor]
    ranked.sort(key=lambda match: (-match.score, match.item.identifier))
    return ranked[:limit]
