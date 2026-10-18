---
id: PL-00TR
title: docket inflow counts a safety- or science-classed product item as an unexpected P1 apparatus filing when it also declares a .claude/rules/ file, so release reported PL-HQF5 and PL-4RL2 as a missed PL-04KR prediction for the week to 2026-10-18
priority: P3
effort: S
status: done
classes: defect, infra
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/tests/test_inflow.py
deferred-from: v0.6.0 - a counting fix in the apparatus's release alarm, which changes nothing a learner sees
added: 2026-10-18
closed: 2026-10-18
pr: 1594
payoff: A cut reports a missed apparatus prediction only when the apparatus missed it
verify: grep -q 'def test_a_class_pinned_p1_on_a_rule_file_is_not_an_unexpected_band' subprojects/docket/tests/test_inflow.py
recurrences: 2026-10-18 PL-L94N withdrawn 2026-10-18 PL-L94N
---

**Problem.** docket inflow counts a safety- or science-classed product item as an unexpected P1 apparatus filing when it also declares a .claude/rules/ file, so release reported PL-HQF5 and PL-4RL2 as a missed PL-04KR prediction for the week to 2026-10-18

**Found 2026-10-18 while closing `PL-04KR`.** `docket inflow` counts an item
as an apparatus filing when any declared path is under `workflow_paths`,
whatever its lane (`PL-4NZ7`). `missed` then counts that filing against
`PL-04KR`'s prediction that no apparatus filing outside the generator tier
reaches `P1`. Read on 2026-10-19's terms, the week of 2026-10-12 to 10-18
reports two such filings. Both are simulator work:

- `PL-HQF5` is a `safety`-classed defect in tissue blood flow. Its only
  apparatus path is `.claude/rules/core-domain.md`.
- `PL-4RL2` is a `science`-classed citation fix. Its only apparatus path is
  `.claude/rules/sources-and-docstrings.md`.

Each is `P1` because `docket check` pins `safety` and `science` work to `P1`,
not because of anything in the apparatus. The prediction was written about
`P1` workflow-lane filings ("P1 workflow filings by week 0, 2, 1, 0"), and a
class-pinned band says nothing about whether apparatus fixes are holding. So a
cut can report a broken prediction that nothing in the apparatus broke.

**Why it matters.** The alarm exists so a cut speaks only when the trend is not the expected one. A false miss teaches the reader to discount the next real one.

**Where.** `subprojects/docket/src/docket/inflow.py`, the `severe` count in
`analyze`, which already leaves out the generator tier for the same kind of
reason (`_generator_tier`). Whether to leave out class-pinned bands, or to
count `severe` over the workflow lane only, is the design choice. The second
keeps a crossing item that is a real apparatus defect out of the count too, so
the first is likelier to be right.

**Done when.** A `P1` that `docket check` pinned by class, on an item whose
apparatus paths are only rule files, does not count as an unexpected `P1`
apparatus filing, and a test pins it.

**Generator check.** The fact misread is which band a filing holds for an
apparatus reason, as against a band `docket check` pinned by class. No head's
`misread:` states it, and no other item misreads it, so this is a one-off.
