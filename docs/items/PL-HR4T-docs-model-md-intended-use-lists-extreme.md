---
id: PL-HR4T
title: docs/MODEL.md § 'Intended use' lists extreme-preserving decimation as an interface safety feature, but § 'Interface boundary' says the chart evaluates the run at column instants and selects no recorded extremes; one is stale (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
payoff: the safety-class section names the chart feature the safety argument actually rests on, so a reviewer checks the right code
verify: ! grep -qF 'extreme-preserving decimation is a safety feature' docs/MODEL.md
reenters: PL-4FBP
---

**Problem.** docs/MODEL.md § 'Intended use' lists extreme-preserving decimation as an interface safety feature, but § 'Interface boundary' says the chart evaluates the run at column instants and selects no recorded extremes; one is stale (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, `grep -n -i 'decimat' docs/MODEL.md` finds the stale sentence in § "Software safety classification: Class C, for the whole application": "The extreme-preserving decimation is a safety feature of the interface." § "Interface boundary" says the opposite: the M4 method of selecting recorded extremes "is not used", and "The run is evaluated at the drawn instants instead." The code agrees with § "Interface boundary": the comment in `src/anesthesia_sim/app/chart_frame.py` records min/max envelope decimation as the algorithm that `PL-GS3R` replaced.

**Why it matters.** The safety-class section names the parts of the interface that carry clinical meaning, so that no one splits them into a lower class. It names a feature that no longer exists, and leaves out the feature that replaced it: evaluating the run at each drawn instant, with every control change drawn. A reviewer who trusts the list would look for the decimation, not find it, and could not tell which part of the chart code the safety argument depends on.

**Done when.** § "Software safety classification" names the chart's current safety feature, that the run is evaluated at each drawn instant and every control change is a drawn instant (§ "Interface boundary"), in place of the extreme-preserving decimation. No sentence in `docs/MODEL.md` describes decimation as current behaviour.

**Generator check.** `PL-4FBP`'s fact: the link between a document sentence and the tree fact it restates, here a sentence about the interface that `PL-GS3R` changed without updating it. `PL-4FBP` closed on 2026-09-19, so this is an instance filed after its head closed, recorded as `reenters: PL-4FBP`.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/MODEL.md` § "Software safety classification: Class C, for the whole application" already listed "the extreme-preserving decimation" among the interface's safety features, though `PL-GS3R` had replaced decimation on 2026-09-14. The problem belongs on v0.7.0's frozen list, and the deferral is removed.

**Disposition under PL-BLN0 (2026-11-09).** PL-BLN0 is the head over the
sentences that went stale when the code they restated changed. It binds every
paragraph of `docs/ARCHITECTURE.md` and of the last chapter of
`docs/interface-provenance.md` to the code it describes, and leaves the free
prose of `docs/MODEL.md` outside that binding, for the reason its brief gives.
This item's sentence is in that free prose, so it stays its own documentation
fix.
