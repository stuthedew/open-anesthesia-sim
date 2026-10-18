---
id: PL-21Z5
title: docket check does not hold a no-successor: id to an item: an id naming no item, the item itself, or a closed item that is not done is accepted with 0 errors, so a typo either answers nothing or answers the wrong re-entered line (found reviewing PL-C4F0)
status: untriaged
feature: generator-heads
added: 2026-10-18
---

**Problem.** docket check does not hold a no-successor: id to an item: an id naming no item, the item itself, or a closed item that is not done is accepted with 0 errors, so a typo either answers nothing or answers the wrong re-entered line (found reviewing PL-C4F0)

Found by the review of `PL-C4F0` on 2026-10-18. `checks.py` holds `reenters:`
ids through `model.reentry_faults`, and nothing does the same for
`no-successor:`. Reproduced: `no-successor: PL-NOPE, PL-V9L3, PL-4097` on an
item passes `bin/docket check` with 0 errors. Left out of `PL-C4F0` because
`checks.py` was declared by another thread's open work that day.
