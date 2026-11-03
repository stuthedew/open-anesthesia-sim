---
id: PL-P6KV
title: PL-04KR's predictions broke twice more for the week of 2026-10-19 to 10-25 and no item investigates either: 8 P1 apparatus filings outside the generator tier, and 29 re-entries against 8 the week before; releases v0.6.11 to v0.6.14 printed both
priority: P2
effort: S
status: done
classes: infra
feature: convergence-visibility
touches: docs/items/PL-P6KV-pl-04kr-s-predictions-broke-twice-more-for-the.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus-only reading of a release report, with no effect on what a learner sees
added: 2026-11-03
closed: 2026-11-03
pr: 1977
payoff: the two misses four releases printed for the week of 2026-10-19 are read, so the next cut's misses are not stacked on an unread one
verify: grep -q 'Verdict, read 2026-11-03: no unfound generator' docs/items/PL-P6KV-pl-04kr-s-predictions-broke-twice-more-for-the.md
---

**Problem.** PL-04KR's predictions broke twice more for the week of 2026-10-19 to 10-25 and no item investigates either: 8 P1 apparatus filings outside the generator tier, and 29 re-entries against 8 the week before; releases v0.6.11 to v0.6.14 printed both

**Why it matters.** `PL-04KR`'s predictions exist so that apparatus inflow that stops falling is investigated and not re-argued. Four releases printed two misses for this week and nobody read them.

**Done when.** The two misses are read against the store, the brief says whether an unfound generator is behind either, and any defect the reading finds is filed or fixed.

**Generator check.** One-off. A missed reading, not a misread fact. The counting gap it found is `PL-NHQ6`.

**Verdict, read 2026-11-03: no unfound generator behind either miss.** Every cluster of three or more items has its cause recorded, every item in the week is closed, and both counts fell the week after: 4 re-entries and 1 counted `P1` in the week of 2026-10-26. The reading below lists each filing by `docket.inflow`'s own rules.

**The 8 `P1` filings outside the generator tier.**

- 3 are simulator items whose `P1` is their `safety` class: `PL-M85T`, `PL-RNYV` and `PL-S79P`. They count only because each extended a checking tool. Filed as `PL-NHQ6`.
- 2 came from the owner's defect review begun 2026-10-19 (feature `defect-review-2026-10`): `PL-6VJ3`, the resident instructions grown from about 37,000 to 90,700 characters, and `PL-QQGZ`, CI's quality run grown from about 2 to 8.7 minutes.
- 1 is `PL-JRVV`, which the owner set to `P1` on 2026-10-20. It addresses the same resident-instruction growth as `PL-6VJ3`.
- 2 re-enter `PL-CZXN`, which removed verify's check for a removed assertion because it refused correct rewrites: `PL-7FPD` and `PL-H57W` closed the gaps it left. `PL-D59R` (2026-10-26) followed in the same route, so that line has three members. All three are closed.

**The 29 re-entries.**

- 13 are in `one-source-of-truth`. They are the sweep the owner asked for on 2026-10-19 ("fix this structurally everywhere"). Each names an earlier fix that a sweep found incomplete. `PL-N4FP` is their recorded head, and it extended the second-copy check.
- 5 follow the review hold's ask wording: `PL-TLPH`, then `PL-YV90`, `PL-XR8B`, `PL-YGR6` and `PL-646J`. `PL-TLPH` is their recorded head. The line continued in November and `PL-ZCF9` closed it on 2026-11-03 as a recorded head.
- 3 are the `PL-CZXN` line above: `PL-CZXN` itself, `PL-7FPD` and `PL-H57W`.
- 3 are in `worker-runs`, each against a different earlier fix: `PL-44R1`, `PL-WJJ8` and `PL-W5JR`.
- 2 follow `bin/docket new`'s recurrence record: `PL-PNSV` and `PL-TBX9`. `PL-8MRM` closed the line on 2026-10-27.
- 3 are single: `PL-LL9F`, `PL-3G9M` and `PL-YL5R`.

**The current week will miss again.** Two days into the week of 2026-11-02 the count stands at 11 `P1` filings. Six are the counting gap in `PL-NHQ6`. Five are `reader-tested-prose`, which the owner asked for after judging `docs/MODEL.md`'s prose on 2026-11-02, four of them at an owner-set `P1`.
