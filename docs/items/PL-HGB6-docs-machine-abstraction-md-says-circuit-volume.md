---
id: PL-HGB6
title: docs/machine-abstraction.md says circuit_volume_l is apparatus-plus-circuit where the shipped profile says apparatus alone, so a profile author following the design document would store an assembled total the code does not expect
priority: P2
effort: S
status: ready
classes: defect, docs, anticipated
feature: machine-profile-framework
touches: docs/machine-abstraction.md
added: 2026-09-20
payoff: stops the design document that governs the next machine profile being wrong about the one field that sets the circuit time constant, so an author following it cannot store an assembled total the code reads as apparatus alone
verify: grep -qF 'is the apparatus alone' docs/machine-abstraction.md
---

**Problem.** docs/machine-abstraction.md says circuit_volume_l is apparatus-plus-circuit where the shipped profile says apparatus alone, so a profile author following the design document would store an assembled total the code does not expect

**Where this came from.** `PL-TBMX` was filed on 2026-09-20 asserting the
opposite - that `circuit_volume_l` is apparatus-plus-circuit and a real profile
would therefore understate the circuit time constant by about 40%. That premise
was refuted the same day by the re-scoping audit's own adversarial verifier and
confirmed against the source; `PL-TBMX` is `dropped` and carries the refutation.
This item is the finding that survived it, resolved the other way round.

**The contradiction, in both documents' own words.**

`src/anesthesia_sim/data/machines/reference_circle_system.json`, in its Targ et
al. entry: *"This file's `circuit_volume_l` is the apparatus alone, with the
patient modelled separately in `data/patients/reference_adult.json`, so adopting
9.86 L would count a lung twice: once inside the circuit and again as the 2.5 L
alveolar compartment."*

`docs/machine-abstraction.md`, under "The reference profile is a breathing
system, not a machine, and stays one": *"Its `circuit_volume_l` of 6.0 L is
apparatus-plus-circuit - its own provenance notes reason about the sum,
comparing 6.0 + 2.5 L against Targ et al.'s measured 9.86 L"*.

**The design document misread its own source.** The 2.5 L it treats as a patient
breathing circuit is the reference adult's *alveolar compartment* - the lung -
which is exactly what the data file's note says must not be counted twice. A
disposable patient circuit is roughly 1.2 L and appears in neither number.

**Why it matters.** `docs/machine-abstraction.md` is the document that governs
how the next machine profile is written, and it is wrong about the meaning of the
one field that sets the circuit time constant. An author following it would store
an assembled total where `core/` expects apparatus alone, and nothing would catch
it: the value would be correctly cited, schema-valid, and wrong. tau_C = V_C /
(V_F + V_A) is the most-taught single number about a circle system, so the error
reaches a learner as a wrong rate of rise rather than as a crash.

It is prospective rather than live. There is one profile, its stored 6.0 L is
correct under the data file's own reading, and no displayed value is affected -
which is why this is `anticipated` and not a `P1`.

**The second half: the field name also differs.** The design's schema table names
`apparatus_volume_l` where the tree ships `circuit_volume_l`. Left alone, that is
a rename or a recorded divergence the moment a second profile is written. It is
in scope here because it is the same sentence's problem.

**Done when.** `docs/machine-abstraction.md` states that `circuit_volume_l` is
the apparatus alone, agreeing with the data file and with `core/`; the "6.0 + 2.5
L" reasoning is corrected to say what the 2.5 L actually is; and the
`apparatus_volume_l` / `circuit_volume_l` naming divergence is either reconciled
or recorded with its condition.

**Explicitly not this item.** Changing the stored 6.0 L, splitting the field,
adding a run-level patient-circuit input, or writing anything into
`docs/MODEL.md` asserting an assembled total - the last is what `PL-TBMX` would
have done and is a false statement about the tree.
