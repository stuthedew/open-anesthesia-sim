---
id: PL-NHQ6
title: The inflow check counts a safety- or science-classed simulator item as a P1 apparatus filing when it also extends a checking tool such as tools/contrast_check.py or tools/doc_check.py: 3 of the 8 in the week of 2026-10-19 and 6 of the 11 so far in the week of 2026-11-02, so the next release reports them as unexpected apparatus severity
priority: P2
effort: S
status: ready
classes: defect
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, docket.toml, docs/items/PL-NHQ6-the-inflow-check-counts-a-safety-or-science.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus-only release-report fix with no effect on what a learner sees
added: 2026-11-03
payoff: a release cut counts only apparatus work as unexpected apparatus severity, so a safety-pinned simulator build that extends a checking tool no longer reads as a broken convergence prediction
verify: grep -q 'def test_a_class_pinned_simulator_item_that_extends_a_tool_is_not_counted' subprojects/docket/tests/test_inflow.py
reenters: PL-00TR
---

**Problem.** The inflow check counts a safety- or science-classed simulator item as a P1 apparatus filing when it also extends a checking tool such as tools/contrast_check.py or tools/doc_check.py: 3 of the 8 in the week of 2026-10-19 and 6 of the 11 so far in the week of 2026-11-02, so the next release reports them as unexpected apparatus severity

**Generator check.** A re-entry of `PL-00TR`. Both misread one fact: which filings the `P1` prediction is about. That is two items, not yet a generator. `PL-2T7X` misread a different fact, what the new-paths number measures.

**Found 2026-11-03 under `PL-P6KV`.** `PL-00TR` exempted a `safety`- or `science`-classed item from the count of unexpected `P1` apparatus filings only when every apparatus path it names is an instruction file. A simulator item that also extends a checking tool still counts, though its `P1` comes from the class pin and not from anything in the apparatus.

- Week of 2026-10-19: `PL-M85T` (core defaults, `tools/literal_home_check.py`), `PL-RNYV` and `PL-S79P` (the schematic, `tools/contrast_check.py`).
- Week of 2026-11-02, two days in: `PL-19W8`, `PL-5C1H`, `PL-H94Q`, `PL-JP7P`, `PL-MCQ5` and `PL-TCD3` (MODEL.md claims, `tools/doc_check.py`).
- Over the whole store, 23 class-pinned items are counted. 16 are of this kind.

**Recommended rule, and its measured cost.** Exempt a class-pinned item that names a path under `src/` or `docs/MODEL.md`. Over the store this drops 18 or 19 simulator items and keeps all 7 apparatus safety defects (`PL-P909`, `PL-YHF1`, `PL-0PJG`, `PL-BXB2`, `PL-V53R`, `PL-7FPD`, `PL-H57W`). It wrongly drops `PL-TCD3`, a defect in the MODEL.md claims check that also edits MODEL.md. Both weeks above still break the prediction under it: 5 counted instead of 8, and 5 instead of 11.

- `docket.toml`'s `product_paths` is not the right list. It includes `pyproject.toml` and `docs/ARCHITECTURE.md`, so keying on it would also drop `PL-7FPD`, `PL-0PJG`, `PL-BXB2` and `PL-V53R`.
- So the fix needs a record of the simulator proper, either a new key or a narrower existing one, read from one place. That design is why this was filed and not fixed alongside `PL-P6KV`.

**Why it matters.** Each release cut prints these as a broken convergence prediction. That costs an investigation, as `PL-P6KV` was, and it hides the genuine apparatus `P1`s among simulator builds.

**Done when.** The count of unexpected `P1` apparatus filings leaves out a class-pinned simulator item that extends a checking tool, reads which paths are the simulator from one record, and the item records the replay over every complete week.
