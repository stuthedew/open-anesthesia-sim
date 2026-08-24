"""Tests for work selection.

The rule under test is the one that stops a project accumulating fifteen
features at five percent each: finishing something already started outranks
starting something new of equal priority.
"""

from __future__ import annotations

from datetime import date

from docket.model import Item
from docket.plan import features, recommend


def _item(
    identifier: str,
    *,
    priority: str = "P2",
    status: str = "ready",
    feature: str = "",
    effort: str = "S",
    classes: tuple[str, ...] = ("perf",),
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort=effort,
        status=status,
        classes=classes,
        touches=("a.py",),
        blocked_by=(),
        feature=feature,
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="abc1234" if status == "done" else "",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
    )


def test_features_group_their_items() -> None:
    grouped = features([_item("PL-1111", feature="alpha"), _item("PL-2222", feature="alpha")])

    assert list(grouped) == ["alpha"]
    assert len(grouped["alpha"].items) == 2


def test_a_feature_is_underway_only_when_partly_done() -> None:
    started = features(
        [_item("PL-1111", feature="a", status="done"), _item("PL-2222", feature="a")]
    )
    untouched = features([_item("PL-3333", feature="b")])

    assert started["a"].is_underway
    assert not untouched["b"].is_underway


def test_p0_outranks_everything() -> None:
    picks = recommend(
        [
            _item("PL-1111", priority="P2", feature="a", status="done"),
            _item("PL-2222", priority="P2", feature="a"),
            _item("PL-3333", priority="P0"),
        ]
    )

    assert picks[0].item.identifier == "PL-3333"
    assert "P0" in picks[0].reason


def test_finishing_a_started_feature_beats_equal_priority_new_work() -> None:
    items = [
        _item("PL-1111", priority="P2", feature="alpha", status="done"),
        _item("PL-2222", priority="P2", feature="alpha"),
        _item("PL-3333", priority="P2"),
    ]
    picks = recommend(items)

    assert picks[0].item.identifier == "PL-2222"
    assert "Finishes 'alpha'" in picks[0].reason


def test_priority_still_wins_over_feature_progress() -> None:
    """Finishing things matters, but not more than the band does."""
    items = [
        _item("PL-1111", priority="P3", feature="alpha", status="done"),
        _item("PL-2222", priority="P3", feature="alpha"),
        _item("PL-3333", priority="P1"),
    ]

    assert recommend(items)[0].item.identifier == "PL-3333"


def test_work_already_in_flight_is_excluded() -> None:
    """Recommending what someone is doing is worse than recommending nothing."""
    items = [_item("PL-1111", priority="P1"), _item("PL-2222", priority="P2")]
    picks = recommend(items, in_flight={"PL-1111"})

    assert [p.item.identifier for p in picks] == ["PL-2222"]


def test_blocked_and_untriaged_work_is_never_recommended() -> None:
    items = [_item("PL-1111", status="blocked"), _item("PL-2222", status="untriaged")]

    assert recommend(items) == []


def test_effort_filters_to_what_fits_the_time_available() -> None:
    items = [
        _item("PL-1111", priority="P1", effort="L"),
        _item("PL-2222", priority="P2", effort="S"),
    ]

    assert [p.item.identifier for p in recommend(items, effort="S")] == ["PL-2222"]


def test_a_recommendation_says_which_model_the_work_warrants() -> None:
    (pick,) = recommend([_item("PL-1111", classes=("safety",), priority="P1")], limit=1)

    assert "strongest model" in pick.describe()


def test_nothing_startable_yields_no_recommendations() -> None:
    assert recommend([]) == []
