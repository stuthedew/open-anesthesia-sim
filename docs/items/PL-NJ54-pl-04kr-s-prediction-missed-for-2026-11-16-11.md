---
id: PL-NJ54
title: PL-04KR's prediction missed for 2026-11-16..11-22, as v0.6.22's cut reported: 1 P1 apparatus filing in the workflow lane whose band no rank or owner set, where none was expected; the P1 items added that week that touch only workflow files are PL-LPCB (document check's section citations) and PL-7YHK (reader rows moved out of the resident writing rule), so find which one it is and why it was P1
priority: P2
effort: S
status: done
classes: infra
feature: convergence-visibility
touches: docs/items/PL-NJ54-pl-04kr-s-prediction-missed-for-2026-11-16-11.md
added: 2026-11-23
closed: 2026-11-23
pr: 2301
filed-pr: 2278
payoff: the miss the v0.6.22 cut printed for the week of 2026-11-16 is read, so the next cut's misses are not stacked on an unread one
verify: grep -qF '**Verdict, read 2026-11-23' docs/items/PL-NJ54-pl-04kr-s-prediction-missed-for-2026-11-16-11.md
---

**Problem.** PL-04KR's prediction missed for 2026-11-16..11-22, as v0.6.22's cut reported: 1 P1 apparatus filing in the workflow lane whose band no rank or owner set, where none was expected; the P1 items added that week that touch only workflow files are PL-LPCB (document check's section citations) and PL-7YHK (reader rows moved out of the resident writing rule), so find which one it is and why it was P1

**Why it matters.** `PL-04KR`'s predictions exist so that apparatus inflow that stops falling is investigated. An unread miss lies under the next cut's misses.

**Done when.** The brief names the counted filing, says why its band is `P1`, and says whether an unfound generator is behind it, in a paragraph that opens `**Verdict`.

**Generator check.** One-off. This is a missed reading, not a misread fact.

**Verdict, read 2026-11-23: the filing is `PL-7YHK`, its band came from the owner-ordered work it unblocked, and no generator is behind it.**

1. **Which filing.** `_unexpected_band` from `subprojects/docket/src/docket/inflow.py`, run over the filings of 2026-11-16 to 11-22 both at `v0.6.22` and on `main` at `8f5723b3`, names one item: `PL-7YHK` (move the reader rows for each document out of the resident plain-writing rule). `PL-LPCB` is not counted, because its `touches` also name files under `src/anesthesia_sim/`, so it is not a workflow-lane item.
2. **Why `P1`.** `PL-7YHK` was filed and closed inside pull request #2204, the one that built `PL-6PPZ` (move the model's verification sections to `docs/VERIFICATION.md`). `PL-6PPZ` carries `owner-priority: P1, 2026-11-11, ratified`. Adding the new document to the instructions loaded at launch would have taken them past `RESIDENT_CAP`, so `make check` would have refused `PL-6PPZ` until the reader rows moved. `PL-7YHK`'s band is the band of the owner-ordered work it unblocked. It records an order, not how severe an apparatus defect was. The prediction leaves out an owner-set band only where the item's own `owner-priority:` names it, so this rider counts.
3. **No generator.** `PL-7YHK`'s own generator check says the cap worked as intended: it turned one more resident document into a routing decision. Nothing else filed that week reached `P1` in the workflow lane. With `PL-MR85`, `PL-LY24` and `PL-8FT2` marked as sweeps under `PL-K3QM`, the week reads 30 ordinary filings, 0 re-entries and 9 new paths, the lowest counts since the week of 2026-10-26 (`bin/docket inflow`, 2026-11-23).
