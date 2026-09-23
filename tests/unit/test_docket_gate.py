"""The current debt gate's dispositions, held over this repository's real tree.

`bin/docket check` requires every open debt item to be placed by the current
gate's section or excused from it by `deferred-from:` (`PL-WD5Z`). That rule
is tested against fixtures with the rest of the package, whose tests read
nothing outside it; this is the one reading of the tree the package lives in,
which is the half `PL-36R4` was about - a rule can be right on every fixture
while the tree it guards owes forty-two dispositions.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docket.checks import analyze
from docket.config import load
from docket.roadmap import milestone_states
from docket.store import read_items

REPO = Path(__file__).resolve().parents[2]


def test_this_repository_records_a_disposition_for_every_open_debt_item() -> None:
    """The real tree, not only a fixture - moved here from `test_doc_check.py`.

    This asserts the tree is *clean*, not merely that the error is well formed,
    and the strictness is deliberate. `ROADMAP.md`'s presence rule leaves
    *which* disposition an item gets to judgment, but *that* one is recorded is
    exact and decidable, which is the line `CLAUDE.md` draws for when a check
    may fail hard.

    It does not penalise capture. `bin/docket new` writes `status: untriaged`
    with no `classes`, which the rule does not count as debt; only a *triaged*
    debt item trips it, and triage is the deliberate act where the disposition
    belongs - written with `bin/docket set <id> --deferred-from`, which the
    error names. `PL-33WM` is the evidence that the strictness earns its place:
    it caught a real gap within forty minutes of the rule landing.

    It also holds the gate to being *read*, so the assertion cannot pass by
    finding nothing to check: a roadmap this reader could not place a gate in
    would otherwise report every tree clean.
    """
    config = load(REPO)
    states = milestone_states((REPO / config.roadmap_file).read_text(encoding="utf-8"))
    report = analyze(read_items(REPO / config.items_dir), date.today(), config, milestones=states)

    assert states.gate is not None
    assert [e for e in report.errors if "neither places nor defers" in e] == []
    assert [e for e in report.errors if "deferred-from" in e] == []
