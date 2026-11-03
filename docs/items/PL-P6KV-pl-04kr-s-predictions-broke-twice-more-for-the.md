---
id: PL-P6KV
title: PL-04KR's predictions broke twice more for the week of 2026-10-19 to 10-25 and no item investigates either: 8 P1 apparatus filings outside the generator tier, and 29 re-entries against 8 the week before; releases v0.6.11 to v0.6.14 printed both
priority: P2
effort: M
status: done
classes: defect
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, docs/items/PL-P6KV-pl-04kr-s-predictions-broke-twice-more-for-the.md, docs/items/PL-04KR-pre-register-the-apparatus-convergence.md
added: 2026-11-03
closed: 2026-11-03
payoff: a release cut stops reporting a broken P1 prediction for product or owner-ranked work, and a real miss tells the session cutting it to file the investigation
verify: grep -q 'def test_an_owner_set_p1_is_not_an_unexpected_band' subprojects/docket/tests/test_inflow.py
---

**Problem.** PL-04KR's predictions broke twice more for the week of 2026-10-19 to 10-25 and no item investigates either: 8 P1 apparatus filings outside the generator tier, and 29 re-entries against 8 the week before; releases v0.6.11 to v0.6.14 printed both

**Why it matters.** `PL-04KR` names a broken prediction as its trigger to investigate a possible unfound generator. Four cuts printed these two misses, and nobody filed an item until 2026-11-03, so a mechanism could have kept producing for two weeks with nothing saying so.

**Done when.** Each miss carries a verdict on whether it points at an unfound generator. Any fault in how a miss is counted is fixed in `docket.inflow`. A cut that prints a miss says how to file its investigation.

**Generator check.** One-off. The `P1` miss misread the same fact as `PL-00TR`: which filings' bands record an apparatus severity. That makes two instances, and this fix replaces `PL-00TR`'s narrow test with a read of `Item.lane`, so a third does not need its own rule. The re-entry miss is the prediction working, as the verdict below says.

**Verdict, measured 2026-11-03** over the store on this branch with `docket.store.read_items`, `docket.inflow` and `Item.lane`. Neither miss points at an unfound generator. The `P1` miss was mostly a counting fault, now fixed. The re-entry miss was real and pointed at the owner-ask guard 10 days before `PL-ZCF9` recorded it as a generator.

1. **Five of the eight `P1` filings carried a band that records something other than apparatus severity.** `PL-M85T`, `PL-RNYV` and `PL-S79P` edit the simulator as well as an apparatus file, so their `safety` class pins them to `P1`. `PL-00TR` excluded such items only when every apparatus path was an instruction file, and these three declared a tool or an apparatus test instead. `PL-7FPD` declares `pyproject.toml` beside its tools, so it is a crossing item too. `PL-JRVV`'s `owner-priority:` records that the owner set its `P1`.
2. **`PL-04KR`'s baseline counted workflow-lane filings.** Counting workflow-lane `P0` and `P1` filings over today's store, with no exemption, gives 0, 2, 1 and 0 for the weeks from 2026-08-24, which is the baseline exactly. The count therefore now reads only workflow-lane filings, and leaves out an owner-set band as it leaves out the generator tier.
3. **The three that still count are real and closed.** `PL-H57W` (with its crossing twin `PL-7FPD`) found that `PL-CZXN`'s mutation check stopped measuring weakened core tests. `PL-QQGZ` found CI's quality run had grown to about 8.7 minutes. `PL-6VJ3` found the resident instructions had grown to 90,700 characters. The 2026-10 defect review the owner asked for found the last two. All three closed by 2026-10-25.
4. **The 29 re-entries fall into known lines.** 13 belong to the one-source-of-truth inventory (`PL-K88Z`), the sweep the owner asked for on 2026-10-19, which found copies that the fact-home check's earlier fixes missed. 5 belong to the review-hold and owner-ask guard line (`PL-9JHM`, `PL-TLPH`, `PL-XR8B`, `PL-YGR6`, `PL-YV90`, then `PL-646J`). `PL-ZCF9` recorded that line as a live generator on 2026-11-02, and `#1973` fixed it on 11-03. 2 re-enter `PL-CZXN`, 2 the recurrence signal, and 3 the worker runs. The other 4 are single filings.
5. **Without the sweep, re-entry still rose, 16 against 8.** So the miss was real. The inventory counts as ordinary inflow because a sweep is recorded only as a `feature:`, and `docket.inflow` breaks out only a head's `root-cause-of:` members. Breaking it out would not have changed this verdict, so a field to record it is filed rather than built.
6. **11 of the 29 were filed on the day the item they re-enter closed.** `PL-04KR` separated a finding filed while the work was being done from a fix that did not hold. A re-entry filed the same day may be the first kind, which would inflate the count. That needs its own measurement, and it is filed.

**What changed.** `docket.inflow._unexpected_band` replaces `_pinned_by_class`. Replayed over the store at the end of each week from 2026-09-28 to 11-02, it changes one line: the week of 2026-10-19 reports 3 `P1` filings, not 8. The week of 2026-11-02, still open, would have reported 11 at the next cut and now counts 1. A cut that prints a miss now ends with the command to file its investigation, after checking `bin/docket feature convergence-visibility` for one already filed.
