---
id: PL-NHQ6
title: The inflow check counts a safety- or science-classed simulator item as a P1 apparatus filing when it also extends a checking tool such as tools/contrast_check.py or tools/doc_check.py: 3 of the 8 in the week of 2026-10-19 and 6 of the 11 so far in the week of 2026-11-02, so the next release reports them as unexpected apparatus severity
priority: P2
effort: S
status: done
classes: defect
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, docs/items/PL-NHQ6-the-inflow-check-counts-a-safety-or-science.md, docs/items/PL-04KR-pre-register-the-apparatus-convergence.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus-only release-report fix with no effect on what a learner sees
added: 2026-11-03
closed: 2026-11-03
pr: 1979
payoff: a release cut counts only apparatus work as unexpected apparatus severity, so a safety-pinned simulator build that extends a checking tool no longer reads as a broken convergence prediction
verify: grep -q 'def test_a_crossing_item_s_p1_is_not_an_unexpected_band' subprojects/docket/tests/test_inflow.py
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

**Fixed 2026-11-03 on `#1979`, by a different rule from the one recommended above.** The count now leaves out every item outside the workflow lane, read from `Item.lane`, and an item whose band the owner set, read from `model.owner_set_priority`. It replaces `PL-00TR`'s test for instruction files.

- **Why the lane and not "names a path under `src/` or `docs/MODEL.md`".** `PL-04KR` registered "P1 workflow filings by week" and measured them in the workflow lane. That population gives its baseline of 0, 2, 1 and 0 exactly. The recommended rule would count `PL-0PJG`, `PL-BXB2` and `PL-V53R`, filed 2026-09-14 inside the fourth baseline week, so it would not reproduce a baseline that read 0 there.
- **The lane is already a record.** `docket.toml`'s `workflow_paths` decides it, so no new key was needed.
- **The cost.** Apparatus safety defects that also declare `pyproject.toml` or `docs/ARCHITECTURE.md` are not counted: `PL-0PJG`, `PL-BXB2`, `PL-V53R`, `PL-XMNC` and `PL-7FPD` over the whole store. `PL-7FPD`'s twin `PL-H57W` is workflow-lane and still counts.
- **The owner-set exemption is a judgment, not a measurement.** The baseline predates `owner-priority:`. An owner-set band records the owner's order rather than the severity of a finding. Over the store it drops `PL-JRVV` and the four `reader-tested-prose` items filed 2026-11-02.
- **Replay.** At the end of each week from 2026-09-28 to 11-02, one reported line changes: the week of 2026-10-19 counts 3, not 8. The open week of 2026-11-02 would have counted 11 at the next cut and now counts 1.

**Which branch closes what** (project owner, 2026-11-03, ratified, over closing `PL-P6KV` in both pull requests). Two sessions worked `PL-P6KV` at once. `#1977` closes it with its reading of the two misses. `#1979` closes this item with the counting fix and leaves `PL-P6KV` as `#1977` wrote it.

**What `#1979`'s reading added to `PL-P6KV`'s.**

- Without the one-source-of-truth inventory, re-entries were still 16 against 8, so that miss was real. The inventory counts as ordinary inflow because a sweep is recorded only as a `feature:`. Filed as `PL-CJGH`.
- 11 of the 29 re-entries were filed on the day the item they re-enter closed, which may count a finding made during the work as a fix that did not hold. Filed as `PL-BB16`.
- The cut printed the misses and nothing about what to do with them, which is why four cuts passed with no item. A cut that prints a miss now ends with the command to file its investigation, after checking `bin/docket feature convergence-visibility` for one already filed.

**What the lane does not answer.** It decides which filings the prediction is about, which is the population `PL-04KR` registered. It is not a record of which paths are the simulator proper, which this item's first brief asked for. An apparatus safety defect that also declares `pyproject.toml` or `docs/ARCHITECTURE.md` is a crossing item, so it goes uncounted. No item now asks for that record, because the prediction does not need it.
