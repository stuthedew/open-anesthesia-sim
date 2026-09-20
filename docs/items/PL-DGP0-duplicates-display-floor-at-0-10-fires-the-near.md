---
id: PL-DGP0
title: duplicates.DISPLAY_FLOOR at 0.10 fires the near-duplicate warning on 61% of filings where 0.15 fires on 26% for identical recall, so the advisory is one a session learns to skim
status: untriaged
feature: recurrence-signal
touches: subprojects/docket/src/docket/duplicates.py
added: 2026-09-20
---

**Problem.** duplicates.DISPLAY_FLOOR at 0.10 fires the near-duplicate warning on 61% of filings where 0.15 fires on 26% for identical recall, so the advisory is one a session learns to skim

**Why it matters.** `CLAUDE.md`: "A check that fires every run without changing
a decision is a defect in the check - it costs attention forever and trains a
session to skim the output where a real advisory also appears." At 0.10 this
prints on three filings in five, which is that failure.

**The floor is strictly dominated, which is what makes this cheap.** Measured
2026-09-20 over the six recorded duplicate clusters and all 321 open items
declaring a `touches` path, at `LIMIT = 3`:

| floor | pairs caught | clusters caught at 2nd filing | fires on | lines/firing |
| --- | --- | --- | --- | --- |
| 0.10 | 8 of 12 | 5 of 6 | 197/321 (61%) | 2.2 |
| 0.15 | 8 of 12 | 5 of 6 | 82/321 (26%) | 1.8 |
| 0.20 | 7 of 12 | 5 of 6 | 32/321 (10%) | 1.4 |

Raising 0.10 to 0.15 loses **no** pair and **no** cluster and removes 115 of
the 197 firings. It is not a recall/noise trade at all at this limit: the
candidates between 0.10 and 0.15 are all false. 0.20 is where recall starts to
cost, dropping `PL-BYMX`/`PL-KSCW` at 0.179.

Recall is counted per cluster at its *second* filing, because that is the
moment a duplicate diagnosis is still unpaid for; counting per pair credits a
cluster's later members as if catching them were worth the same.

**Done when** `DISPLAY_FLOOR` is 0.15, or the brief records a measurement that
refutes the table above.

**Provenance.** Measured on `claude/practical-cerf-nx84jg`, the branch that
yielded `PL-TZ7T` to `claude/recurrence-signal-feature-3hnynt` under `docket
show`'s ordering. The two implementations converged independently on the same
design - a `duplicates.py` keyed on shared `touches` with title similarity
ranking inside it - and differ here and in little else, so this is the one
finding the yielded branch carries that the holder's does not.
