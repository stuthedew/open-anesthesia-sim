"""`docket picks`: the what's-left list, held to the rules `PL-G2HP`'s brief decided."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from docket.cli import main
from docket.model import Item, parse_item
from docket.picks import BUILD, BUILD_REST, FEATURE, HEAD, LANE, MAX_LINES, Picks, picks
from docket.render import format_picks
from docket.roadmap import CLEAR, Wave, wave

WORKFLOW = ("tools",)

ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.3.0 — the foundation** | Shipped. | 2 M |
| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |

## Completed: v0.3.0 - the foundation

### Goal

Shipped.

### Required scope

Done (queue item PL-PQRS).

### Definition of done

Met.

### Explicitly out of scope for v0.3.0

Everything else.

## Next milestone: v0.4.0 - the teachable case

### Goal

Make the model teachable.
{gate}
### Required scope

{scope}

### Definition of done

The learner can run one case.

### Explicitly out of scope for v0.4.0

Nothing named.
"""

GATE = (
    "PL-G1G1",
    "PL-B1B1",
    "PL-B2B2",
    "PL-C1C1",
    "PL-C2C2",
    "PL-C3C3",
    "PL-C4C4",
    "PL-D1D1",
    "PL-S1S1",
)
SCOPE = (
    ("The layout model", "PL-F1F1"),
    ("Run identity", "PL-F2F2"),
    ("Persistence", "PL-F3F3"),
    ("Debt it clears", "PL-S1S1"),
)


def _text(
    identifier: str,
    *,
    feature: str = "",
    effort: str = "S",
    status: str = "ready",
    touches: Sequence[str] = ("a.py",),
    blocked_by: Sequence[str] = (),
    root_cause_of: Sequence[str] = (),
    generator: str = "",
) -> str:
    fields = [
        f"id: {identifier}",
        f"title: Item {identifier}",
        "priority: P2",
        f"effort: {effort}",
        f"status: {status}",
        "classes: defect",
        f"touches: {', '.join(touches)}",
        "added: 2026-09-01",
        f"payoff: {identifier} is done",
    ]
    fields += [f"feature: {feature}"] if feature else []
    fields += [f"blocked-by: {', '.join(blocked_by)}"] if blocked_by else []
    fields += [f"root-cause-of: {', '.join(root_cause_of)}"] if root_cause_of else []
    fields += [f"generator: {generator}"] if generator else []
    body = "**Problem.** P\n**Why it matters.** W\n**Done when.** D\n"
    return "---\n" + "\n".join(fields) + "\n---\n\n" + body


def _texts() -> dict[str, str]:
    """A gate of every shape the list sorts, and a scope two of whose entries can start."""
    found = [
        _text(
            "PL-G1G1",
            effort="M",
            root_cause_of=("PL-B1B1", "PL-C1C1", "PL-C2C2"),
            generator="live - still handed members",
        ),
        _text("PL-B1B1", feature="alpha"),
        _text("PL-B2B2", feature="alpha", effort="M", touches=("tools/x.py",)),
        _text("PL-C1C1", feature="beta"),
        _text("PL-C2C2", effort="M", status="needs-decision"),
        _text("PL-C3C3", touches=("tools/y.py",)),
        _text("PL-C4C4", effort="M", touches=("a.py", "tools/z.py")),
        _text("PL-D1D1", status="blocked", blocked_by=("PL-Z9Z9",)),
        _text("PL-Z9Z9"),
        _text("PL-S1S1"),
        _text("PL-F1F1", effort="L"),
        _text("PL-F2F2", status="blocked", blocked_by=("PL-F1F1",)),
        _text("PL-F3F3", status="blocked", blocked_by=("PL-F2F2",)),
    ]
    return {f"{text.split()[2]}-x.md": text for text in found}


def _store() -> list[Item]:
    return [parse_item(text, name) for name, text in _texts().items()]


def _roadmap(gate: Sequence[str] = GATE) -> str:
    frozen = (
        "\n### Debt gate: the frozen list\n\n**Frozen 2026-09-01.**\n\n"
        + "\n".join(f"- {identifier} (S) entry {identifier}" for identifier in gate)
        + "\n"
        if gate
        else ""
    )
    scope = "\n".join(f"- **{lead}** (queue item {i}). More prose." for lead, i in SCOPE)
    return ROADMAP.format(gate=frozen, scope=scope)


def _plan(items: list[Item], gate: Sequence[str] = GATE) -> Wave:
    return wave(
        _roadmap(gate),
        "0.3.0",
        frozenset(i.identifier for i in items if not i.is_open),
        frozenset(i.identifier for i in items),
        {i.identifier: i.blocked_by for i in items},
    )


def _picks(limit: int = MAX_LINES) -> tuple[list[Item], Picks]:
    items = _store()
    plan = _plan(items)
    assert plan.beat == CLEAR and plan.gate is not None
    return items, picks(items, plan, {"PL-C3C3"}, workflow_paths=WORKFLOW, limit=limit)


def test_picks_collapses_a_one_entry_feature_into_its_lanes_line() -> None:
    """A feature of two gets its line; one of one, and no feature, join their lane's line."""
    _, found = _picks()
    lines = found.lines
    kinds = [(line.kind, line.name) for line in lines]
    assert kinds == [
        (HEAD, "PL-G1G1"),
        (FEATURE, "alpha"),
        (LANE, "product"),
        (LANE, "workflow"),
        (LANE, "crossing"),
        (BUILD, "The layout model"),
        (BUILD, "Debt it clears"),
    ]
    by_name = {line.name: line for line in lines}
    assert [i.identifier for i in by_name["product"].items] == ["PL-C1C1", "PL-C2C2"]
    assert by_name["alpha"].lanes == (("product", 1), ("workflow", 1))
    assert by_name["crossing"].lanes == (("crossing", 1),)
    assert found.folded == ()


def test_picks_counts_sizes_decisions_and_flight_and_names_the_next_pick() -> None:
    _, found = _picks()
    by_name = {line.name: line for line in found.lines}
    product, workflow = by_name["product"], by_name["workflow"]
    assert (product.awaiting, product.in_flight) == (1, 0)
    # The decision is counted and never offered; work in flight is neither.
    assert product.pick is not None and product.pick.item.identifier == "PL-C1C1"
    assert (workflow.in_flight, workflow.pick) == (1, None)
    text = format_picks(found)
    assert "product lane, one-item features and items carrying none - 2 open (product): " in text
    assert "1 M, 1 S; 1 awaiting a decision" in text
    assert "alpha - 2 open (product 1, workflow 1): 1 M, 1 S" in text
    assert "next: nothing here can start now" in text
    assert "       payoff: PL-C1C1 is done" in text


def test_picks_leads_with_a_live_head_and_lists_it_once() -> None:
    _, found = _picks()
    lines = found.lines
    named = [i.identifier for line in lines for i in line.items]
    assert named.count("PL-G1G1") == 1 and lines[0].kind == HEAD
    assert found.led == ("PL-G1G1",)


def test_picks_offers_startable_scope_entries_with_what_waits_on_them() -> None:
    """Entry 1 holds two of the scope's three others, one directly; blocked entries are absent."""
    _, found = _picks()
    builds = [line for line in found.lines if line.kind == BUILD]
    assert [(b.entry, [i.identifier for i in b.items]) for b in builds] == [
        (1, ["PL-F1F1"]),
        (4, ["PL-S1S1"]),
    ]
    layout = builds[0]
    assert (layout.waiting_on_it, layout.waiting_directly, layout.scope_others) == (2, 1, 3)
    text = format_picks(found)
    assert "the roadmap clears the gate first, with 7 entries still open" in text
    assert "build entry 1, The layout model - 1 startable (product): 1 L; 2 of the" in text
    assert "none of the scope's 3 other open items waits on it" in text
    # What the gate cannot clear is counted, never offered.
    assert "Not offered: 1 the milestone clears itself and 1 blocked outside the gate" in text


def test_picks_keeps_to_its_cap_folding_features_and_collapsing_build_entries() -> None:
    _, found = _picks(limit=5)
    lines = found.lines
    assert [line.kind for line in lines] == [HEAD, LANE, LANE, LANE, BUILD_REST]
    assert lines[-1].entries == (1, 4)
    assert found.folded == (("alpha", 2),)
    by_name = {line.name: line for line in lines}
    assert {"PL-B1B1", "PL-C1C1"} <= {i.identifier for i in by_name["product"].items}
    assert "Folded into their lane lines to keep to 8: alpha (2)." in format_picks(found)


def test_picks_refuses_a_plan_with_no_gate() -> None:
    items = _store()
    plan = _plan(items, gate=())
    assert plan.gate is None
    with pytest.raises(ValueError, match="no gate"):
        picks(items, plan, set(), workflow_paths=WORKFLOW)


def _project(tmp_path: Path, roadmap: str | None) -> Path:
    store = tmp_path / "items"
    store.mkdir()
    for name, text in _texts().items():
        (store / name).write_text(text, encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.3.0"\n', encoding="utf-8")
    if roadmap is not None:
        (tmp_path / "ROADMAP.md").write_text(roadmap, encoding="utf-8")
    return store


@pytest.mark.parametrize(
    ("roadmap", "said"),
    [
        (None, "no ROADMAP.md to read"),
        (_roadmap(gate=()), "the plan records no gate to list"),
        (_roadmap(gate=(*GATE, "PL-X9X9")), "the gate names ids the store does not hold"),
    ],
)
def test_picks_fails_visibly_where_there_is_no_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], roadmap: str | None, said: str
) -> None:
    store = _project(tmp_path, roadmap)
    assert main(["picks", "--items", str(store), "--no-git"]) == 1
    assert said in capsys.readouterr().out


def test_picks_prints_the_list_from_the_command(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _project(tmp_path, _roadmap())
    assert main(["picks", "--items", str(store), "--no-git"]) == 0
    out = capsys.readouterr().out
    assert "  1. PL-G1G1, a live generator head" in out
    assert "build entry 1, The layout model" in out


def test_picks_names_a_gate_entry_the_plan_walker_declines(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A gate entry the walker declines is named, and the list exits 1 (`PL-GMR6`).

    The walker declines an entry carried on from the margin rather than reading
    it short, and `wave` names the entry and exits 1. This list printed what it
    read at exit 0 and said nothing, so a count it gave could be short with no
    sign of it.
    """
    roadmap = _roadmap().replace(
        "- PL-B2B2 (S) entry PL-B2B2", "- PL-B2B2 (S) entry **wrapped**\nPL-B2B2 lazily"
    )
    store = _project(tmp_path, roadmap)

    assert main(["picks", "--items", str(store), "--no-git"]) == 1
    out = capsys.readouterr().out
    assert "A list the plan is read from was not read whole" in out
    assert "carries on the entry above it without an indent" in out
    assert main(["wave", "--items", str(store), "--no-git"]) == 1
