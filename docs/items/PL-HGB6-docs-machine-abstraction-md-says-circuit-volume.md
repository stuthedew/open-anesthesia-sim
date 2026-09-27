---
id: PL-HGB6
title: docs/machine-abstraction.md says circuit_volume_l is apparatus-plus-circuit where the shipped profile says apparatus alone - re-scoped 2026-09-27: the assembled total is right, and the document's reasoning and two uses of apparatus were what was wrong
priority: P2
effort: S
status: done
classes: defect, docs, anticipated
feature: machine-profile-framework
touches: docs/machine-abstraction.md, ROADMAP.md, docs/items/PL-TBMX-circuit-volume-l-means-apparatus-plus-patient.md
added: 2026-09-20
closed: 2026-09-27
pr: 1206
payoff: the design document that governs the next machine profile argues circuit_volume_l's assembled-total meaning from evidence that supports it, never calls a with-circuit volume an apparatus volume, and records apparatus_volume_l as the other half of a split rather than a rename, so an author following it stores the with-circuit total the model's single circuit compartment needs
verify: grep -qF 'is the assembled total, apparatus plus patient circuit' docs/machine-abstraction.md && ! grep -qF '6.0 + 2.5 L' docs/machine-abstraction.md && ! grep -qF '3.3 L apparatus' docs/machine-abstraction.md && ! grep -qF 'indistinguishable on apparatus volume' docs/machine-abstraction.md
---

**Re-scoped 2026-09-27: the assembled total is right, and the design
document's reasoning was what was wrong** (project owner, 2026-09-27, ratified,
over building HGB6 as written; the machine-profile chain's first thread put the
choice on a card, recommending this option, and the owner picked "Re-scope +
TBMX" at 20:05Z). Where this section and the brief below disagree, this section
is the decision. The title was filed ending "so a profile author following the
design document would store an assembled total the code does not expect", and
was changed because that clause states the opposite of what the code needs.

**Why the brief was backwards.** The model has one well-mixed gas compartment
in front of the patient, so the inspiratory and expiratory limbs and the Y-piece
can only be inside $`V_C`$, and `circuit_volume_l` has to be the assembled
breathing system. The project's own documents already read it that way:
`docs/machine-survey.md` § "(a1) Apparatus gas volume" says "its $`V_C`$ is
apparatus *plus* patient circuit" and computes its $`\tau_C`$ column from Shin et
al.'s with-circuit totals, and `docs/MODEL.md` ("What real workstations hold")
compares the stored 6.0 L with the Primus's with-circuit 5.9 L. The data file's
"the apparatus alone" sits in its Targ et al. note, which refuses the measured
9.86 L because that system held a latex bag standing in for the lung, while its
corrugated limbs and Y-piece were part of the apparatus measured; there the
phrase means without the lung, not without the hoses. Built as written, a profile
author would store Shin et al.'s 2.1 L apparatus figure for a Perseus A500 and
get $`\tau_C`$ = 31.5 s at 4 L/min where 49.5 s is right, 36% short. That is
`PL-TBMX`'s finding, and `PL-TBMX` had been dropped on the same misreading.

**What the design document did get wrong, and what this item changed instead
of the three done-when clauses below:**

- **Its justification.** It reasoned from comparing "6.0 + 2.5 L" with Targ et
  al.'s 9.86 L, but the 2.5 L is the reference adult's alveolar compartment, so
  that comparison bears on counting a lung twice and says nothing about how the
  6.0 L divides between apparatus and patient circuit. The reference-profile
  paragraph now gives the three grounds that hold: the single compartment, what
  the Targ note's contrast actually excludes, and `docs/MODEL.md`'s comparison
  with a with-circuit total.
- **Two uses of "apparatus" for a with-circuit volume**, both in Question 5:
  the example archetype label "3.3 L apparatus", and the Perseus/Zeus comparison
  "indistinguishable on apparatus volume - 3.3 L against 3.2 L". The label now
  reads "3.3 L with patient circuit"; the comparison gives both pairs, 2.1 against
  2.0 L of apparatus and 3.3 against 3.2 L with the 1.2 L patient circuit.
- **The naming clause**, answered by recording `apparatus_volume_l` and
  `circuit_volume_l` as two quantities under the schema table: the machine's half
  of the planned split, against today's assembled $`V_C`$, with the split as the
  condition on which the second gives way to the first.
- **"Circuit volume" for the patient circuit**, in Question 6 and the
  reference-profile paragraph, now reads "patient-circuit volume", since one
  phrase carrying both meanings is what let the misreading happen.

Nothing under `src/` or in any data file changed, and no displayed value moves.
`PL-TBMX` was reopened as a `ready` `P1` in the same pull request to state the
meaning in the schema docstring, the data file and `docs/MODEL.md`, where a
profile author reads it, and joined v0.6.0's frozen gate list under the
exception that admits a `safety` finding whenever it is made; `ROADMAP.md`
records both, and corrects its v0.5.0 paragraph that called the refutation
sound. The `verify:` was rewritten with the scope: the commissioned `grep -qF 'is
the apparatus alone' docs/machine-abstraction.md` asked for the sentence this
re-scope refuses, and the new command asks for the assembled-total statement and
the absence of the three phrases above.

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
