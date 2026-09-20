---
id: PL-DGP0
title: duplicates.DISPLAY_FLOOR at 0.10 fires the near-duplicate warning on 61% of filings where 0.15 fires on 26% for identical recall, so the advisory is one a session learns to skim
priority: P2
effort: S
status: done
classes: defect
feature: recurrence-signal
touches: subprojects/docket/src/docket/duplicates.py, subprojects/docket/tests/test_duplicates.py
added: 2026-09-20
closed: 2026-09-20
payoff: cuts the near-duplicate warning from firing on 55% of filings to 22% with no cluster lost, so it stays an advisory a session reads instead of one it learns to skim
verify: grep -q 'DISPLAY_FLOOR = 0.15' subprojects/docket/src/docket/duplicates.py
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

**Re-measured on the holding branch 2026-09-20, and adopted - with the table
corrected in one respect.** Run through the shipped `near_duplicates` at
`LIMIT`, over the 18 pairs of the five recorded clusters and all 321 open items
declaring a path, each probed as a simulated capture and excluded from its own
candidate set:

| floor | pairs caught | clusters caught at 2nd filing | clusters reaching the threshold | fires on |
| --- | --- | --- | --- | --- |
| 0.10 | 13 of 18 | 5 of 5 | 2 of 5 | 178/321 (55%) |
| 0.15 | 11 of 18 | 5 of 5 | 2 of 5 | 70/321 (22%) |
| 0.20 | 7 of 18 | 5 of 5 | 2 of 5 | 24/321 (7%) |

**"Identical recall" is right about clusters and wrong about pairs.** 0.15 does
lose two real pairs - `PL-5MFL`/`PL-4FD2` at 0.147 and `PL-5QLP`/`PL-QMC0` at
0.143 - so the candidates between 0.10 and 0.15 are not all false. It loses no
cluster, which is the measure that matters: every cluster is still caught when
it first repeats, and `duplicates.anchor` accumulates from there, so a cluster's
later pairs are redundant. The brief's own per-cluster metric was the better one
and its per-pair row overstated the case.

**Why the holder's original 0.10 was sound at the time, and is not now.** This
is threshold-dependent. At the literal three the design first specified, 0.15
surfaced *nothing* and 0.10 surfaced one cluster - so the floor genuinely
mattered and pair recall was the right thing to protect. Correcting
`MIN_RECURRENCES` to two, in the same branch, is what makes the higher floor
free. `DISPLAY_FLOOR`'s docstring now carries the table and says to re-measure
both together if either moves.

0.20 is refused: it holds the same clusters today, and `PL-BYMX`/`PL-KSCW` at
0.184 is the next thing to go, which is too little margin for a constant nobody
will re-measure.

**Provenance kept.** Recovered from `origin/claude/practical-cerf-nx84jg` with
`git checkout`; that branch yielded `PL-TZ7T` under `docket show`'s ordering and
this is the finding its reconnaissance bought.
