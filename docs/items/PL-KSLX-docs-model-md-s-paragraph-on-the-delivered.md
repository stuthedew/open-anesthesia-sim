---
id: PL-KSLX
title: docs/MODEL.md's paragraph on the delivered-concentration control says its recorded changes carry the unit 'fraction of 1 atm', but control_record.CONTROL_INPUT_UNITS records 'percent of 1 atm' since PL-NJPB, so the specification names the wrong unit for every recorded dial change (found closing PL-000W)
priority: P1
effort: S
status: done
classes: defect, safety
feature: stale-source-claims
touches: docs/MODEL.md
deferred-from: v0.7.0 - captured after the gate froze; the wrong unit is in the specification's prose, and every displayed and recorded value already uses percent
added: 2026-10-31
closed: 2026-11-01
pr: 1915
payoff: docs/MODEL.md names the unit that every recorded change of the delivered dial carries, percent of 1 atm, so a reader of the specification cannot read a recorded 2 as 200%
verify: ! grep -qF 'carry the unit *fraction of 1 atm*' docs/MODEL.md && grep -qF 'carry the unit *percent of 1 atm*' docs/MODEL.md && ! grep -qF 'fraction of one atmosphere. It is displayed as a percent' docs/MODEL.md
---

**Problem.** docs/MODEL.md's paragraph on the delivered-concentration control says its recorded changes carry the unit 'fraction of 1 atm', but control_record.CONTROL_INPUT_UNITS records 'percent of 1 atm' since PL-NJPB, so the specification names the wrong unit for every recorded dial change (found closing PL-000W)

**Evidence.** `docs/MODEL.md`, in the paragraph that opens "The
delivered-concentration control is where that assumption does the most work",
says `ControlInput.DELIVERED`'s recorded changes "carry the unit *fraction of 1
atm*". Run on 2026-10-31, `CONTROL_INPUT_UNITS[ControlInput.DELIVERED]` in
`app/control_record.py` returns `'percent of 1 atm'`. `PL-NJPB` changed the
recorded value to the percent dialled. The interface formats every value
correctly, so the error is in the specification only.

**Why it matters.** `docs/MODEL.md` is the authoritative specification. A
reader who trusts the sentence reads every recorded change of the delivered
dial as a fraction, so a recorded 2 would be taken for 200% of one atmosphere
rather than 2%. Nothing displayed is wrong today, but planned item 9's save and
load format, or any other reader built from the specification, would be.

**Done when.** The paragraph names the unit `CONTROL_INPUT_UNITS` records,
`percent of 1 atm`.

**Checked 2026-11-01:** a second sentence states the same stale fact. § on
recorded runs says "So the delivered dial is stored as a fraction of one
atmosphere", in the paragraph that opens "Recorded values are the model's, not
the interface's". `PL-NJPB` made it the percent as well. It is one fact in two
places, so this item corrects both, and its `verify:` checks both.

**Generator check.** One-off. The fact is the recorded unit of the delivered
control. `PL-NJPB` changed it, and this is a sentence its docs sweep missed.
No live head's `misread:` names the recorded unit of a control.
