---
id: PL-JS6P
title: Add a doc_check rule that ties each number docs/MODEL.md and README.md restate to its home in a data file or in code, and fails when they disagree
priority: P2
effort: M
status: ready
classes: defect, docs
feature: one-source-of-truth
touches: tools/doc_check.py, docs/MODEL.md, README.md, tests/unit/test_doc_check.py
blocked-by: v0.6.0, PL-K88Z
deferred-from: v0.6.0 - placed on ROADMAP.md's v0.6.x one-source-of-truth row, built after v0.6.0 ships (project owner, 2026-10-19, ratified, PL-2LB5)
added: 2026-10-19
payoff: a number in the authoritative specification can no longer disagree with the data file it restates
verify: grep -q 'def test_a_restated_number_that_disagrees_with_its_home_fails' tests/unit/test_doc_check.py
---

**Problem.** Add a doc_check rule that ties each number docs/MODEL.md and README.md restate to its home in a data file or in code, and fails when they disagree

**Why it matters.** Step 3 of `PL-2LB5` (the one-source-of-truth design round). `docs/MODEL.md` is the authoritative specification, so a number there that disagrees with the shipped data file is a safety-relevant error that no check catches today. The rule is checked, not generated, so the specification stays hand-written and reviewable (decided in `PL-2LB5`).

**Done when.** `tools/doc_check.py` fails when a number `docs/MODEL.md` or `README.md` ties to a home differs from that home's value, its baseline of untied numbers can only shrink, and the baseline is at zero.

**Generator check.** Not a re-entry: it is a step of `PL-2LB5` (the one-source-of-truth design round), which widens the closed `PL-4S6C` at the project owner's ask, and no open generator head names this shape.
