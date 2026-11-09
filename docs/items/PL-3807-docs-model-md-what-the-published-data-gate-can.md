---
id: PL-3807
title: docs/MODEL.md § 'What the published-data gate can and cannot resolve' counts the sign of the elimination disagreement as part of the published-data gate, but § 'Release gate' says the elimination comparison is not part of the release check; decide which elimination checks a release must pass (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
payoff: a reader of the release conditions sees every published-data check a release runs, including the direction of the elimination departure
verify: ! grep -qF 'simulated wash-in passes validation against published data' docs/MODEL.md
---

**Problem.** docs/MODEL.md § 'What the published-data gate can and cannot resolve' counts the sign of the elimination disagreement as part of the published-data gate, but § 'Release gate' says the elimination comparison is not part of the release check; decide which elimination checks a release must pass (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** § "What the published-data gate can and cannot
resolve" (line 10874) lists the gate's checks: the early wash-in points, the
30-minute wash-in band at every fresh gas flow, "the sign of the elimination
disagreement for each cohort", and both solubility orderings. § "Release gate"
(line 12470) names only "simulated wash-in passes validation against published
data for every agent and cohort". It then says "The comparison of simulated
elimination with earlier versions is not a condition of release", which is
about the regression pins, not the sign check. The sign check is part of
`tests/reference/test_published_wash_in_and_elimination.py`, which every
release's test run includes. So the two sections no longer contradict each
other outright, but the release gate leaves out a published-data check that
every release in fact runs.

**Why it matters.** A clinician reading § "Release gate" to learn what a
release proves about the model against measurements in people learns only
about wash-in. The elimination check, which fixes the direction in which the
model's recovery departs from human data, runs on every release but is not
listed.

**Done when.** The published-data bullet in § "Release gate" names the same
checks as § "What the published-data gate can and cannot resolve", including
the sign of the elimination disagreement, or points to that list. The sentence
about comparing elimination with earlier versions stays, worded so that it
cannot be read as covering the sign check.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.
