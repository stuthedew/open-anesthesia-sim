---
id: PL-7R8S
title: docs/MODEL.md § Displayed precision judges the cost's significant figures against one SD of the density while every other agent amount, the liquid volume beside the cost included, is judged against a seventh of an SD, so the section applies two limits to figures with the same relative uncertainty
priority: P3
effort: S
status: needs-decision
classes: defect
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/unit/test_formatting.py
deferred-from: v0.7.0 - the inconsistency is in a reason only: the cost is shown coarser than the band requires, which claims nothing false, so no learner is misled while it waits
added: 2026-11-04
payoff: every agent amount and the cost beside it are judged against one limit, so the section gives no reason its own rule contradicts
verify: ! grep -qF 'At four it would be 0.010 %, finer than one SD' docs/MODEL.md
---

**Problem.** docs/MODEL.md § Displayed precision judges the cost's significant figures against one SD of the density while every other agent amount, the liquid volume beside the cost included, is judged against a seventh of an SD, so the section applies two limits to figures with the same relative uncertainty

**Checked 2026-11-04**, by the second blind review pass on `#2024`. The paragraph "A cost and a price per millilitre" refuses four significant figures for a cost because 0.010 % is "finer than one SD" of the density. Every other agent amount in the section is held to the readouts' band, which runs down to about a seventh of an SD. Four figures would be about 0.19 SD (0.010 % against sevoflurane's 0.053 %), inside that band. The volume beside the cost has the same relative uncertainty, and `PL-SP6H` judged its whole millilitre against the seventh. Above about 1,900 mL of sevoflurane the whole-millilitre volume is finer than one SD, so the two figures on one line are judged by different limits.

**Why it matters.** The section gives a reason that its own rule elsewhere contradicts. Nothing on screen is finer than the band: three figures are coarser than the band requires, which the one-sided bound allows.

**Decision needed.** Should a cost keep three significant figures, or show four, the finest the band admits? A learner sees the cost's last digit change.

- **A. Keep three figures**, and restate the reason as a choice inside the band: three figures put the price check's rounding, at most half a cent per dollar, below the cost's step. The learner sees no change.
- **B. Show four figures**, the finest count the band admits, as each agent amount shows the finest count derived for it. The cost is never finer than a cent, so only a cost of USD 10 or more changes: USD 12.3 would read USD 12.34.

**Recommendation: A.** It fixes the inconsistency in the reason without changing the display, and a cost at the reader's own price is read to a few figures, not to the cent on a long case.

**Done when.** The paragraph "A cost and a price per millilitre" judges the cost's count of figures against the same limit as the other agent amounts, in the form the owner chooses, and `test_the_cost_s_and_the_price_s_precisions_follow_from_the_density_and_the_cost` computes that limit.

**Generator check.** Stock of `PL-B6YV`'s fact. The paragraph dates from `PL-1P15`, before that head closed on 2026-11-02, so this is not a re-entry.
