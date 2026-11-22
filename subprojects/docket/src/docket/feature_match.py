"""Which feature an item's words point to, and which features read alike.

A feature groups items so that `docket feature <name>` can say when a goal is
finished. Two failures undo that: a session filing an item guesses a new name
where an existing feature already fits, and over time two names come to hold
one goal. The registry describes each feature, and this module ranks features
by how much of their vocabulary a title shares, so a session can be shown the
likeliest ones and decide (`PL-LRWK`).

**It suggests and never decides.** This module's score was measured on
2026-11-22 over this repository's store. Hiding each of 399 randomly chosen
items in turn, it ranked the item's own feature first for 48%, in the top three
for 71% and in the top five for 79%. For 58 feature merges chosen by hand, it
ranked the chosen target in the top three for 43 and the top five for 51. Good enough to put
the right name in front of a session most of the time, and wrong too often to
act on alone. Duplicate bug-report studies draw the same line: text similarity
ranks candidates well for a person to confirm, and decides less well (Runeson
et al., ICSE 2007, doi:10.1109/ICSE.2007.32; Laney et al., COMPSAC 2025,
arXiv:2504.14797). `PL-LRWK` carries the measurement.

**A feature's words** are the content words of every item title it holds, its
name split at hyphens, and its registry description. Each word is weighted by
how rare it is across features (inverse document frequency), so a word every
feature uses counts for nothing. Words are read by `duplicates.content_words`,
the reader `docket new` already uses for titles.

**Two open items with no feature are paired only where both declare a path
outside the store.** Title against title across the whole store is the key
`duplicates` measured and refused: it finds the items meant to recur, such as
the dated triage passes, before anything else. A shared path selects and the
title only orders the selection, as it does there.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .config import Config
from .duplicates import content_words, shared_declared, similarity
from .model import Item

#: How many features a capture with no `--feature` is shown. The measurement
#: in the module docstring is a top-three one: 71%, against 48% for one name.
SUGGESTIONS = 3

#: How many lines each list in `feature --similar` prints. Each is ranked, so
#: the first lines are the strongest, and a longer list spends attention on
#: pairs that the 58 hand-chosen merges show are rarely right below this rank.
LISTED = 15


@dataclass(frozen=True)
class Match:
    """One feature, and how strongly a title or another feature points to it."""

    name: str
    score: float


def _words(name: str, titles: Sequence[str], description: str) -> Counter[str]:
    words: Counter[str] = Counter()
    for title in titles:
        words.update(content_words(title))
    words.update(content_words(name.replace("-", " ")))
    words.update(content_words(description))
    return words


def profiles(items: Sequence[Item], config: Config) -> dict[str, Counter[str]]:
    """Each feature's words, for every feature an item carries that is still in use.

    A retired name is left out: it is not a feature to join. Where a registry
    is kept, only its listed names are profiled, so a misspelt feature on one
    item is not offered to the next.
    """
    titles: dict[str, list[str]] = {}
    for item in items:
        if item.feature:
            titles.setdefault(item.feature, []).append(item.title)
    retired = set(config.retired_features)
    listed = {name for name, _ in config.feature_descriptions}
    return {
        name: _words(name, group, config.describe_feature(name))
        for name, group in sorted(titles.items())
        if name not in retired and (not listed or name in listed)
    }


def _rarity(groups: Mapping[str, Counter[str]]) -> dict[str, float]:
    """Each word's inverse document frequency, counting a feature as one document.

    Smoothed as log(1 + N/n), so a word in every feature still counts a
    little and a store holding one feature can still be ranked.
    """
    counts: Counter[str] = Counter()
    for words in groups.values():
        counts.update(words.keys())
    total = len(groups)
    return {word: math.log(1 + total / seen) for word, seen in counts.items()}


def suggest(
    title: str, groups: Mapping[str, Counter[str]], limit: int = SUGGESTIONS
) -> list[Match]:
    """The features whose words a new title shares most, strongest first.

    The score sums the weight of each title word a feature holds, and divides
    by the square root of the feature's size, so a feature holding hundreds of
    items does not win every title on volume. That is the score the module
    docstring measured. A feature sharing no word is not offered.
    """
    query = content_words(title)
    rarity = _rarity(groups)
    scored = []
    for name, words in groups.items():
        weight = sum((1 + math.log(words[word])) * rarity[word] for word in query if word in words)
        if weight > 0:
            scored.append(Match(name, weight / math.sqrt(sum(words.values()) + 1)))
    scored.sort(key=lambda match: (-match.score, match.name))
    return scored[:limit]


def _vector(words: Counter[str], rarity: Mapping[str, float]) -> dict[str, float]:
    weights = {word: (1 + math.log(count)) * rarity[word] for word, count in words.items()}
    length = math.sqrt(sum(value * value for value in weights.values())) or 1.0
    return {word: value / length for word, value in weights.items()}


def similar_features(
    groups: Mapping[str, Counter[str]], limit: int = LISTED
) -> list[tuple[str, str, float]]:
    """The pairs of features whose words overlap most, as cosine similarity, strongest first."""
    rarity = _rarity(groups)
    vectors = {name: _vector(words, rarity) for name, words in groups.items()}
    names = sorted(vectors)
    pairs = []
    for index, one in enumerate(names):
        for other in names[index + 1 :]:
            left, right = vectors[one], vectors[other]
            score = sum(value * right.get(word, 0.0) for word, value in left.items())
            if score > 0:
                pairs.append((one, other, score))
    pairs.sort(key=lambda pair: (-pair[2], pair[0], pair[1]))
    return pairs[:limit]


def unfeatured_matches(
    items: Sequence[Item], groups: Mapping[str, Counter[str]], limit: int = LISTED
) -> list[tuple[Item, Match]]:
    """Each open item with no feature, beside the feature its title points to most."""
    found = []
    for item in items:
        if item.is_open and not item.feature:
            best = suggest(item.title, groups, limit=1)
            if best:
                found.append((item, best[0]))
    found.sort(key=lambda pair: (-pair[1].score, pair[0].identifier))
    return found[:limit]


def unfeatured_pairs(
    items: Sequence[Item], items_dir: str, limit: int = LISTED
) -> list[tuple[Item, Item, tuple[str, ...]]]:
    """Pairs of open items with no feature that declare a path in common, closest titles first.

    These are the candidates for a feature nobody has named yet. The module
    docstring says why a shared path selects them and the title only orders.
    """
    loose = [item for item in items if item.is_open and not item.feature and item.touches]
    pairs = []
    for index, one in enumerate(loose):
        for other in loose[index + 1 :]:
            shared = shared_declared(one.touches, other, items_dir=items_dir)
            if shared:
                pairs.append((one, other, shared, similarity(one.title, other.title)))
    pairs.sort(key=lambda pair: (-pair[3], pair[0].identifier, pair[1].identifier))
    return [(one, other, shared) for one, other, shared, _ in pairs[:limit]]


def lone_features(items: Sequence[Item], config: Config) -> list[Item]:
    """The open items that are the only item their feature holds.

    A feature exists to group work, so one holding a single item either has a
    sibling filed elsewhere or should not be a feature yet. Retired names are
    left to the check that refuses them.
    """
    counts = Counter(item.feature for item in items if item.feature)
    retired = set(config.retired_features)
    return sorted(
        (
            item
            for item in items
            if item.feature
            and item.is_open
            and counts[item.feature] == 1
            and item.feature not in retired
        ),
        key=lambda item: item.identifier,
    )
