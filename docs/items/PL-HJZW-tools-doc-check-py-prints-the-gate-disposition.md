---
id: PL-HJZW
title: tools/doc_check.py prints the gate-disposition failure under 'Advisories (judgment needed)' while tests/unit/test_doc_check.py makes it a hard make check failure, so a session that reads the advisory label as optional pushes a red branch
priority: P2
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-19
payoff: stops a triage pass reading 'advisory' as optional and pushing a branch that fails CI on an assertion it never saw
verify: grep -q 'def test_a_missing_disposition_is_reported_as_an_error' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py prints the gate-disposition failure under 'Advisories (judgment needed)' while tests/unit/test_doc_check.py makes it a hard make check failure, so a session that reads the advisory label as optional pushes a red branch

**Confirmed against the tree 2026-09-20**, both halves:

- `tools/doc_check.py`'s `check_gate_dispositions` appends to
  `report.advisories`, and its own docstring says "this reports the silence and
  decides nothing, which is why it is an advisory rather than an error".
- `tests/unit/test_doc_check.py::test_this_repository_records_a_disposition_for_every_open_debt_item`
  runs `doc_check.analyze` over the real tree and asserts that no advisory
  containing `records no disposition` survives. `make check` runs `pytest`, so
  that assertion is a hard failure.

**Why it matters.** The two disagree about severity, and the label a session
reads first is the wrong one. `doc_check.py` prints the line under
"Advisories (judgment needed)", which this project's own convention says is a
signal needing context rather than a rule - `CLAUDE.md` reserves hard failure
for exact rules and calls an advisory nobody acts on a candidate for retirement.
So a session that triages a debt item, runs `python3 tools/doc_check.py check`,
reads one advisory and decides the judgment can wait has followed the
documentation exactly, and pushes a branch that fails CI on an assertion it
never saw.

The cost falls on the pass most likely to trip it. Triage is what creates the
advisory - classing an item is what makes it debt - so a triage session is the
one that meets this, and it meets it at the end, after the queue edits are
written.

The disagreement is not that either half is wrong about the rule.
`check_gate_dispositions` is right that *which* disposition an item gets is
judgment; the test is right that *whether* one is recorded is exact. What is
missing is that the printed output says which of the two it is.

**Done when.** A missing gate disposition is reported at one severity in both
places - either printed as an error by `tools/doc_check.py`, or printed with
the test's own words saying it will fail `make check` - so a session cannot
read the label as optional and be wrong.
