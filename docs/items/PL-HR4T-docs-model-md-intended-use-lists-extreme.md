---
id: PL-HR4T
title: docs/MODEL.md § 'Intended use' lists extreme-preserving decimation as an interface safety feature, but § 'Interface boundary' says the chart evaluates the run at column instants and selects no recorded extremes; one is stale (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
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
