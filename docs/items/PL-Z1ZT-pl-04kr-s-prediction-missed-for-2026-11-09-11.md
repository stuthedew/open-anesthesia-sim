---
id: PL-Z1ZT
title: PL-04KR's prediction missed for 2026-11-09..11-15, as v0.6.19's cut reported: 4 P1 apparatus filings in the workflow lane whose band no rank or owner set, where none was expected; the count may include a sweep's filings, because the cut ran on a shallow clone
priority: P2
effort: S
status: done
classes: infra
feature: convergence-visibility
touches: docs/items/PL-Z1ZT-pl-04kr-s-prediction-missed-for-2026-11-09-11.md
added: 2026-11-22
closed: 2026-11-23
pr: 2301
payoff: the miss the v0.6.19 cut printed for the week of 2026-11-09 is read, so the next cut's misses are not stacked on an unread one
verify: grep -qF '**Verdict, read 2026-11-23' docs/items/PL-Z1ZT-pl-04kr-s-prediction-missed-for-2026-11-09-11.md
---

**Problem.** PL-04KR's prediction missed for 2026-11-09..11-15, as v0.6.19's cut reported: 4 P1 apparatus filings in the workflow lane whose band no rank or owner set, where none was expected; the count may include a sweep's filings, because the cut ran on a shallow clone

**Why it matters.** `PL-04KR`'s predictions exist so that apparatus inflow that stops falling is investigated. An unread miss lies under the next cut's misses.

**Done when.** The brief names the four counted filings, says whether a sweep's filings inflated the count, and says whether an unfound generator is behind them, in a paragraph that opens `**Verdict`.

**Generator check.** One-off. This is a missed reading, not a misread fact.

**Verdict, read 2026-11-23: four bands each earned by its own rule or set by the owner's request, no sweep in the count, and no generator behind them.**

1. **No sweep inflated the count.** The tag `v0.6.19` was replayed in a full checkout with its own copy of `docket`, and git answered which item's work filed each item. The week of 2026-11-09 to 11-15 had 60 filings that no head explained, 2 filed by a head and 0 by a sweep. The same four `P1` filings count on `main` at `8f5723b3`.
2. **`PL-KH7Y`** (require the merge-hold check on `main`). Until it was required, a pull request the arming rule held could still merge. `CLAUDE.md` § "What this project is" names a gap in a safety-floor guard as an apparatus finding that stops a product session, so `P1` is the band its own rules give it.
3. **`PL-RTYG`** (the merge-hold check ran on Python 3.11 and could not parse a product test). The check refused correct work, the second of the three findings that section names.
4. **`PL-4J4H`** (a Projects thread started above its checkout ran with no guard hooks). Another gap in a safety-floor guard. It carries `reenters: PL-CR81`, the earlier fix for threads that load no hooks. Two filings re-enter that line, fewer than the three that make a generator, and its durable fix, `PL-XFDQ` (load the hooks through a plugin), waits on the owner.
5. **`PL-N2VQ`** (copy edit pull request titles and bodies again). Its title records the owner's request of 2026-11-10, so its band is the owner's order, but no `owner-priority:` was written. The copy editor it changed was removed on 2026-11-13 in #2149, so it can file nothing more.
6. **No generator.** `PL-KH7Y` and `PL-RTYG` are two defects in one new check, the merge-hold check that `PL-39Y1` added on 2026-11-11. Two items are below the three a generator needs, and nothing has re-entered that check since.
