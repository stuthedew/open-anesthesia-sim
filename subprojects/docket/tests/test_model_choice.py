"""Tests for the `[models]` table: which model and effort each kind of work uses.

The table is one home for a fact that had several (`PL-0XDM`). So the tests
pin what a reader gets for each kind of work, and that a malformed table is
refused rather than read as if it said something.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docket.config import load
from docket.model import Item
from docket.model_choice import Choice, ModelTable, item_facts, parse
from docket.plan import choose_model, recommend


def _table(**extra: object) -> ModelTable:
    data: dict[str, object] = {"default": {"model": "model-a", "effort": "high"}}
    data.update(extra)
    return parse(data, "docket.toml")


def _item(
    *,
    classes: tuple[str, ...] = ("perf",),
    touches: tuple[str, ...] = ("a.py",),
    effort: str = "S",
    verify: str = "true",
) -> Item:
    return Item(
        identifier="PL-B7K2",
        title="Item PL-B7K2",
        priority="P2",
        effort=effort,
        status="ready",
        classes=classes,
        touches=touches,
        blocked_by=(),
        feature="speed",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
        verify=verify,
    )


def test_no_rule_holding_gives_the_default() -> None:
    assert _table().choose({"role": "worker"}) == Choice("model-a", "high", None)


def test_the_first_rule_that_holds_decides_and_a_key_it_leaves_out_falls_back() -> None:
    table = _table(
        rule=[
            {"match": {"area": "simulator"}, "effort": "max"},
            {"match": {"area": "interface"}, "model": "model-b", "effort": "medium"},
        ],
        areas={"simulator": ["src/core/"], "interface": ["src/app/"]},
    )
    both = {"area": frozenset({"simulator", "interface"})}
    assert table.choose(both) == Choice("model-a", "max", 1)
    assert table.choose({"area": frozenset({"interface"})}) == Choice("model-b", "medium", 2)
    assert table.choose({"area": frozenset()}) == Choice("model-a", "high", None)


def test_a_rule_holds_only_when_every_category_it_names_matches() -> None:
    table = _table(rule=[{"match": {"class": "science", "size": "L"}, "effort": "max"}])
    assert table.choose({"class": frozenset({"science"}), "size": "L"}).rule == 1
    assert table.choose({"class": frozenset({"science"}), "size": "M"}).rule is None
    # A category no reader passes never holds, so a misspelt one falls through.
    assert table.choose({"class": frozenset({"science"})}).rule is None


def test_an_area_is_reached_from_inside_it_and_from_a_directory_holding_it() -> None:
    table = _table(areas={"simulator": ["src/anesthesia_sim/core/", "docs/MODEL.md"]})
    assert table.areas_of(["src/anesthesia_sim/core/blood.py"]) == {"simulator"}
    assert table.areas_of(["src/"]) == {"simulator"}
    assert table.areas_of(["docs/MODEL.md.bak", "tools/x.py"]) == frozenset()


def test_an_item_gives_its_class_size_area_and_role() -> None:
    table = _table(areas={"simulator": ["src/core/"]})
    facts = item_facts(
        _item(classes=("science",), touches=("src/core/x.py",)), table, (), delegable=False
    )
    assert facts["class"] == {"science"}
    assert facts["size"] == "S"
    assert facts["area"] == {"simulator"}
    assert facts["role"] == "strongest"
    plain = item_facts(_item(), table, (), delegable=True)
    assert plain["role"] == "delegable"


def test_next_prints_the_table_s_choice_beside_the_flag() -> None:
    table = _table(rule=[{"match": {"role": "delegable"}, "model": "model-b"}])
    (rec,) = recommend([_item()], models=table, protected_paths=("src/",), gate_paths=("G.md",))
    assert "delegable - a cheaper model may take this, model-b at high effort" in rec.describe()
    assert choose_model(_item(), None, (), (), ()) is None


def test_the_project_table_loads_and_prices_its_default() -> None:
    """The project's own table parses, and its default model has a list price."""
    root = Path(__file__).resolve().parents[3]
    table = load(root).models
    assert table is not None
    assert table.price(table.choose({}).model) is not None


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({}, "default must name exactly"),
        ({"default": {"model": "model-a"}}, "default must name exactly"),
        ({"default": {"model": "model-a", "effort": "extreme"}}, "not one of low"),
        (
            {"default": {"model": "model-a", "effort": "high"}, "excluded": ["model-x"]},
            "no key named excluded",
        ),
        ({"default": {"model": "model-a", "effort": "high"}, "colour": 1}, "no key named colour"),
        (
            {"default": {"model": "model-a", "effort": "high"}, "rule": [{"match": {}}]},
            "naming at least one category",
        ),
        (
            {"default": {"model": "model-a", "effort": "high"}, "rule": [{"match": {"role": "x"}}]},
            "sets neither",
        ),
        (
            {
                "default": {"model": "model-a", "effort": "high"},
                "rule": [{"match": {"area": "nowhere"}, "effort": "max"}],
            },
            "does not name",
        ),
        (
            {
                "default": {"model": "model-a", "effort": "high"},
                "prices": {"model-a": {"input": 0, "output": 1}},
            },
            "positive number",
        ),
    ],
)
def test_a_malformed_table_is_refused(data: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse(data, "docket.toml")


def test_a_rule_may_name_any_model_and_prices_are_read() -> None:
    table = _table(
        rule=[{"match": {"feature": "speed"}, "model": "model-x"}],
        prices={"model-x": {"input": 10, "output": 50}},
    )
    assert table.choose({"feature": "speed"}).model == "model-x"
    assert table.price("model-x") == (10.0, 50.0)
    assert table.price("model-a") is None


def test_a_config_file_without_the_table_has_none(tmp_path: Path) -> None:
    (tmp_path / "docket.toml").write_text('[docket]\nitems_dir = "backlog"\n', encoding="utf-8")
    assert load(tmp_path).models is None
