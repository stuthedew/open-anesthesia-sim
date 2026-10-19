---
id: PL-CLVM
title: The early wash-in comparison states desflurane's worst early point as +2.10 SD in test_published_wash_in_and_elimination.py's docstring table and docs/MODEL.md, but as +2.11 SD in the comment above the regression band's ceiling
priority: P3
effort: S
status: done
classes: defect, docs
touches: tests/reference/test_published_wash_in_and_elimination.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1683
payoff: The stated reason for desflurane's early wash-in ceiling quotes the same value the table and docs/MODEL.md give
verify: ! grep -qF 'The worst point was +2.11 SD' tests/reference/test_published_wash_in_and_elimination.py
---

**Problem.** The early wash-in comparison states desflurane's worst early point as +2.10 SD in test_published_wash_in_and_elimination.py's docstring table and docs/MODEL.md, but as +2.11 SD in the comment above the regression band's ceiling

**Where.** `tests/reference/test_published_wash_in_and_elimination.py` has the
table row "+2.10 SD at 10 min" in the early wash-in test's docstring, and the
same row in `docs/MODEL.md`'s early wash-in table. The comment that opens
"The top of that regression band" says the worst point was +2.11 SD when the
comparison was first run. One of them is rounded differently or stale. The
fix reruns the comparison at the shipped defaults and states one value in all
three places. It is in `docs/MODEL.md`, on the clinical floor, so it is filed
rather than fixed in place.

**Found by** the `PL-PRCS` design round's trial review of #1526's prose,
2026-10-18.

**Measured 2026-10-19** at the shipped defaults: desflurane's 10-minute point
sits at +2.0998 SD (`_clamped_wash_in("desflurane")` and
`distance_in_standard_deviations`, from a scratch script importing the test
module). So the docstring table and `docs/MODEL.md` are right at +2.10 SD, and
the comment above `EARLY_WASH_IN_DISAGREEMENT_CEILING_SD` is the stale one.
`docs/MODEL.md` does not need to change.

**Why it matters.** The comment is the stated reason for the 2.5 SD ceiling. A
reader who checks the reasoning finds two values for one point and cannot tell
which is current.

**Done when.** The comment above `EARLY_WASH_IN_DISAGREEMENT_CEILING_SD` gives
+2.10 SD, or says the value is in the docstring table instead of repeating it.

**Fixed 2026-10-19.** Measured again at the shipped defaults:
`_clamped_wash_in("desflurane").ratios[10]` is 0.88200, which is +2.0998 SD
from the published point. The comment above
`EARLY_WASH_IN_DISAGREEMENT_CEILING_SD` now gives +2.10 SD, as the docstring
table and `docs/MODEL.md` already did.
