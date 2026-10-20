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

import pytest
from docket.checks import analyze
from docket.config import load
from docket.roadmap import baseline_train, milestone_states
from docket.store import read_items

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.reads_item_store
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
    would otherwise report every tree clean. Between milestones there is
    genuinely no gate. A milestone has shipped and the next one is not scoped
    yet, so no section ahead of the baseline records a frozen list, as after
    v0.6.0 shipped on 2026-10-20 with v0.7.0 unscoped. So the read is held to
    finding the baseline's release train, and a missing gate is accepted only
    where that train holds no section that records one.
    """
    config = load(REPO)
    text = (REPO / config.roadmap_file).read_text(encoding="utf-8")
    states = milestone_states(text)
    report = analyze(read_items(REPO / config.items_dir), date.today(), config, milestones=states)
    train = baseline_train(text)

    assert train is not None, "the roadmap's version table marks no single row current"
    assert (states.gate is None) == (not any(s.records_a_gate for s in train.ahead))
    assert [e for e in report.errors if "neither places nor defers" in e] == []
    assert [e for e in report.errors if "deferred-from" in e] == []
