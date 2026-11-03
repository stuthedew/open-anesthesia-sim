---
id: PL-Y3PV
title: Backfill feature: onto 60 closed defect items whose title names the mechanism of a feature that already exists
priority: P3
effort: S
status: ready
classes: housekeeping
touches: docs/items
added: 2026-11-03
payoff: the defects-by-feature report counts 60 closed defects under the feature that already names their mechanism, so its no-feature row falls from 160 to 100
verify: grep -q '^feature: bash-guard-bound$' docs/items/PL-0X0G-*.md && grep -q '^feature: api-credit-runs$' docs/items/PL-29DJ-*.md && grep -q '^feature: reader-checks$' docs/items/PL-GZXY-*.md && grep -q '^feature: line-ends$' docs/items/PL-139L-*.md && grep -q '^feature: front-matter-round-trip$' docs/items/PL-5B39-*.md && grep -q '^feature: prose-renders-as-written$' docs/items/PL-DSMK-*.md && grep -q '^feature: effort-trial$' docs/items/PL-8MZ9-*.md
---

**Problem.** 160 defect items carry no `feature:`, and the defects-by-feature
report shows them as its largest row. All 160 are closed. The triage procedure
asks for a feature only "when it belongs", and in 60 of them one plainly did:
the title describes the mechanism that an existing feature's other members
describe. The project owner approved writing those 60 on 2026-11-03.

**Evidence.** A session read every unfeatured defect title on 2026-11-03 and
sorted them. 60 clearly fit an existing feature and are listed below. 63 more
might fit one and are left blank, because a wrong feature inflates that
feature's count. The other 37 have no matching feature and are left blank too.
That includes two themes with no feature: checks that assume the machine they
were written on, and what a failed simulator step leaves behind. Both are fully
closed, so a new feature would have nothing left to complete. No rule in
`docket.toml`'s `[models]` table matches on `feature`, so this changes reports
and model routing not at all.

The 60, by the feature each receives:

- `bash-guard-bound`: PL-0X0G, PL-9RSP, PL-K9QL, PL-KQ4Q, PL-TRMN, PL-R17X, PL-P95F
- `api-credit-runs`: PL-29DJ, PL-4N0K, PL-KFJY, PL-NQ0M, PL-15TY, PL-44SP, PL-BT70
- `worker-runs`: PL-TSH9
- `reader-checks`: PL-GZXY, PL-HD96, PL-GSJ6, PL-HR4V, PL-HSB3, PL-5M36
- `gate-parity-conditions`: PL-RW3T, PL-ZXM1
- `line-ends`: PL-139L, PL-PQ0R, PL-K1D6, PL-PK4B
- `front-matter-round-trip`: PL-5B39, PL-9HD1, PL-V6CR, PL-G8ZN
- `prose-renders-as-written`: PL-DSMK, PL-PRSF, PL-CQC9, PL-TH9V
- `recurrence-signal`: PL-34BG, PL-SV0D
- `verify-false-reject`: PL-VHVJ, PL-D59R
- `verify-command-health`: PL-RR1N
- `owner-ask-by-state`: PL-F7ZW
- `owner-ask-refusals`: PL-VHMS
- `effort-trial`: PL-8MZ9
- `remote-ref-deletion`: PL-TL6T
- `skill-routing`: PL-3XP7
- `one-id-grammar`: PL-ZJ6X, PL-R77L
- `host-reachability`: PL-BSYZ
- `required-check-trigger-reading`: PL-NWSK
- `recommendation-rationale`: PL-M21Q
- `test-effectiveness-measurement`: PL-H57W, PL-LBNN
- `floating-point-domain`: PL-B26Y
- `model-spec-accuracy`: PL-1QL6, PL-CLVM
- `stranded-report-fidelity`: PL-X3NY, PL-8JQQ
- `stranded-recovery`: PL-K2C8
- `generator-identification`: PL-K5CX
- `git-silence-channel`: PL-PWH6

**Generator check.** One-off. This is a backfill of a field triage left blank,
and no mechanism is misreading a fact.
