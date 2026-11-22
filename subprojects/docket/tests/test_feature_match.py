"""Ranking features by the words items share with them (`PL-LRWK`)."""

from __future__ import annotations

from datetime import date

from docket.config import Config
from docket.feature_match import (
    lone_features,
    profiles,
    similar_features,
    suggest,
    unfeatured_matches,
    unfeatured_pairs,
)
from docket.model import Item


def _item(identifier: str, title: str, feature: str = "", **overrides: object) -> Item:
    base: dict[str, object] = dict(
        identifier=identifier,
        title=title,
        priority="P2",
        effort="S",
        status="ready",
        classes=("perf",),
        touches=(),
        blocked_by=(),
        feature=feature,
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body="",
    )
    base.update(overrides)
    return Item(**base)  # type: ignore[arg-type]


REGISTRY = Config(
    features_file="features.toml",
    feature_descriptions=(
        ("chart-readout", "The concentration chart's axes and notices."),
        ("vaporizer-controls", "The vaporizer dial."),
        ("chart-axes", "Ticks and labels on the chart's axes."),
        ("stale", "A feature nobody uses."),
    ),
    retired_features=("dev-tooling",),
)

STORE = [
    _item("PL-A1A1", "The chart axis tick labels are cut at the plot edge", "chart-readout"),
    _item("PL-A1A2", "The chart's off-scale notice names the axis in MAC only", "chart-readout"),
    _item(
        "PL-B1B1", "The vaporizer dial moves in steps the device cannot set", "vaporizer-controls"
    ),
    _item("PL-B1B2", "The vaporizer dial's label lags its value", "vaporizer-controls"),
    _item("PL-C1C1", "The chart's axis labels overlap the tick marks", "chart-axes"),
    _item("PL-D1D1", "Retired chart work", "dev-tooling"),
]


def test_a_title_is_offered_the_features_whose_words_it_shares_strongest_first() -> None:
    """The point of the ranking: the chart title is offered chart features, not the dial."""
    groups = profiles(STORE, REGISTRY)

    names = [match.name for match in suggest("The chart axis label is clipped", groups)]

    assert set(names[:2]) == {"chart-axes", "chart-readout"}
    assert suggest("Nothing in common here", groups) == []


def test_retired_and_unlisted_names_are_never_offered() -> None:
    """A retired name is not one to join, and a misspelt one must not spread."""
    store = [*STORE, _item("PL-E1E1", "Chart axis typo group", "chart-axis")]

    groups = profiles(store, REGISTRY)

    assert "dev-tooling" not in groups
    assert "chart-axis" not in groups
    assert set(groups) == {"chart-readout", "vaporizer-controls", "chart-axes"}


def test_the_closest_features_are_paired_and_unrelated_ones_are_not() -> None:
    pairs = similar_features(profiles(STORE, REGISTRY))

    assert {pairs[0][0], pairs[0][1]} == {"chart-axes", "chart-readout"}


def test_open_items_with_no_feature_are_matched_and_paired_only_on_a_shared_path() -> None:
    """Title against title alone is the key `duplicates` refused, so a path selects."""
    loose = [
        _item("PL-F1F1", "The chart axis ticks are cut", touches=("app/chart.py",)),
        _item("PL-F1F2", "Chart axis labels overlap", touches=("app/chart.py",)),
        _item("PL-F1F3", "Chart axis labels overlap again", touches=("app/dial.py",)),
        _item("PL-F1F4", "Closed chart axis work", status="done", closed=date(2026, 8, 2)),
    ]
    store = [*STORE, *loose]
    groups = profiles(store, REGISTRY)

    matched = {item.identifier for item, _ in unfeatured_matches(store, groups)}
    pairs = unfeatured_pairs(store, "docs/items")

    assert matched == {"PL-F1F1", "PL-F1F2", "PL-F1F3"}
    assert [(one.identifier, other.identifier, shared) for one, other, shared in pairs] == [
        ("PL-F1F1", "PL-F1F2", ("app/chart.py",))
    ]


def test_an_open_item_alone_in_its_feature_is_named() -> None:
    lone = lone_features(STORE, REGISTRY)

    assert [item.identifier for item in lone] == ["PL-C1C1"]
