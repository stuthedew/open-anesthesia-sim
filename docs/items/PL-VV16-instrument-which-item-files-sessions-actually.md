---
id: PL-VV16
title: Instrument which item files sessions actually open, and whether citation edges are ever traversed
status: done
added: 2026-09-13
closed: 2026-09-13
priority: P2
effort: M
classes: infra
feature: worker-instructions
touches: .claude/hooks/item_read_log.py, .claude/settings.json, tools/item_reads.py, docket.toml, docs/ARCHITECTURE.md, tests/unit/test_item_read_log.py
verify: python3 tools/item_reads.py && grep -q 'item_read_log.py' .claude/settings.json
---

**Problem.** Every claim this project has made about `docs/items/` describes its
shape - 841 files, 70.8% terminal, 86.1% of items citing another, 2,773 edges.
None of them measures the store being *used*. The citation graph is counted at
authoring time; whether a session ever follows an edge is unknown.

**Why it matters.** Two of the larger design arguments about the store rest on
assuming it does. `PL-KM3X` (partition closed bodies out of the live store) was
dropped partly because the store is densely cross-referenced, and `PL-NB35` (a
bounded startup tier) assumes the rationale in those items is worth reaching.
Both are guesses about read behaviour that nothing observes. "No command reads a
closed item's body" is true and beside the point - commands were never the
reader in question.

**Done when.** A local, untracked log records which item files sessions open and
which ids they search for, and a summariser reports how many distinct items are
reached, what share of those are closed, and how many citation edges are
traversed within a session - with the sample size stated first, because the
failure mode here is a small sample read as a finding.

**Deliberately not decided.** Whether a low traversal count means the graph is
decorative, that sessions cannot find what they need, or that the sample is too
small. The tool prints the three readings and chooses between none of them.
