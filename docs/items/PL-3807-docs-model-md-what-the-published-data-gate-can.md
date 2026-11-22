---
id: PL-3807
title: docs/MODEL.md § 'What the published-data gate can and cannot resolve' counts the sign of the elimination disagreement as part of the published-data gate, but § 'Release gate' says the elimination comparison is not part of the release check; decide which elimination checks a release must pass (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-md-structure
milestone: v0.6.19
touches: docs/MODEL.md
added: 2026-11-05
closed: 2026-11-16
pr: 2168
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

**Done 2026-11-16.** The published-data bullet in `docs/MODEL.md` § "Release
gate" now requires every check of the published-data gate, for every agent and
cohort, names the sign of the elimination disagreement among them, and points
to § "What the published-data gate can and cannot resolve" for the list. It
points rather than restating the list, so the two sections cannot drift apart
again. The sentence about earlier versions now names the elimination
regression pins, which compare simulated elimination with the model's own
earlier output, so it cannot be read as covering the sign check. The developer
note under it said the comparison with earlier versions sits in the wash-in
module. It now says that the five-minute elimination pin is in the module of
the published-data gate, and that the late-washout tables are in a module of
their own (`tests/reference/test_late_washout_against_published_fits.py`, found
with `grep -rln`). Docs sweep: both sections, and the two test modules.
