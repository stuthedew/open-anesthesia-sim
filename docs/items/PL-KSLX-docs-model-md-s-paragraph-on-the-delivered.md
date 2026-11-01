---
id: PL-KSLX
title: docs/MODEL.md's paragraph on the delivered-concentration control says its recorded changes carry the unit 'fraction of 1 atm', but control_record.CONTROL_INPUT_UNITS records 'percent of 1 atm' since PL-NJPB, so the specification names the wrong unit for every recorded dial change (found closing PL-000W)
priority: P1
effort: S
status: untriaged
classes: defect, safety
feature: stale-source-claims
touches: docs/MODEL.md
deferred-from: v0.7.0 - captured after the gate froze; the wrong unit is in the specification's prose, and every displayed and recorded value already uses percent
added: 2026-10-31
reenters: PL-4FBP
---

**Problem.** docs/MODEL.md's paragraph on the delivered-concentration control says its recorded changes carry the unit 'fraction of 1 atm', but control_record.CONTROL_INPUT_UNITS records 'percent of 1 atm' since PL-NJPB, so the specification names the wrong unit for every recorded dial change (found closing PL-000W)

**Evidence.** `docs/MODEL.md`, in the paragraph that opens "The
delivered-concentration control is where that assumption does the most work",
says `ControlInput.DELIVERED`'s recorded changes "carry the unit *fraction of 1
atm*". Run on 2026-10-31, `CONTROL_INPUT_UNITS[ControlInput.DELIVERED]` in
`app/control_record.py` returns `'percent of 1 atm'`. `PL-NJPB` changed the
recorded value to the percent dialled. The interface formats every value
correctly, so the error is in the specification only.

**Done when.** The paragraph names the unit `CONTROL_INPUT_UNITS` records,
`percent of 1 atm`.

**Generator check.** One-off. The fact is the recorded unit of the delivered
control. `PL-NJPB` changed it, and this is a sentence its docs sweep missed.
No live head's `misread:` names the recorded unit of a control.

**Checked 2026-11-01:** the generator check above is revised. The fact is
`PL-4FBP`'s: a value the code holds once, `CONTROL_INPUT_UNITS` in
`app/control_record.py`, restated in `docs/MODEL.md` prose instead of cited.
`PL-FM15` gave `PL-D1LR` the same answer, and said clause 1 of `PL-4FBP`
covers the case. So this item records `reenters: PL-4FBP`. It is the first
filing to re-enter `PL-4FBP` after `PL-FM15`'s no-successor answer of
2026-10-31. Three such filings reopen that answer.
