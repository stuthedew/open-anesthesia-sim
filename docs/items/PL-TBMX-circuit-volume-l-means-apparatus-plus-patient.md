---
id: PL-TBMX
title: circuit_volume_l means apparatus plus patient circuit, so a real machine profile storing a published apparatus figure would understate the circuit time constant by about 40%
priority: P1
effort: S
status: dropped
classes: safety, anticipated
feature: machine-profile-framework
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/data/machines/reference_circle_system.json, docs/MODEL.md
added: 2026-09-20
closed: 2026-09-20
reason: Premise refuted the same day by the audit's own adversarial verifier and confirmed against the source: the shipped profile states 'This file's circuit_volume_l is the apparatus alone, with the patient modelled separately in data/patients/reference_adult.json', so a real profile storing a published apparatus figure is correct rather than wrong and no circuit time constant is understated. The 6.0 + 2.5 L sum this item reasoned from is apparatus plus the reference adult's ALVEOLAR compartment, not apparatus plus a patient breathing circuit. The genuine finding underneath it - that docs/machine-abstraction.md says the opposite of the data file about what the field means - is refiled as PL-HGB6, which resolves it the other way round.
payoff: stops the next machine profile shipping a circuit time constant about a third too short, built from a correctly-cited manufacturer apparatus figure that no check can tell from an assembled total
verify: grep -qF 'is the assembled total, apparatus plus patient circuit' docs/MODEL.md && grep -qF 'is the assembled total, apparatus plus patient circuit' src/anesthesia_sim/core/parameters.py
---

**Problem.** circuit_volume_l means apparatus plus patient circuit, so a real machine profile storing a published apparatus figure would understate the circuit time constant by about 40%

**Why it matters.** `circuit_volume_l` is the denominator of the only time
constant the breathing circuit has — `tau_C = V_C / VdotF`, the equation
`docs/MODEL.md` § "Governing equations" / "Breathing circuit" solves and
§ "Known limitations" quotes as *"the part of the inspired curve a learner is
most likely to attribute to uptake"*. `docs/machine-survey.md` § "(a1) Apparatus gas volume" calls
the same lag "the single most-taught point about a circle system". Nothing in
the tree states what the field's value is a volume *of*. Every apparatus figure
a real workstation publishes — and every one the survey collected — is the
machine including its absorber and **excluding** the disposable patient circuit,
while the model has one well-mixed circuit compartment and therefore needs the
assembled total. So the obvious act of a profile author, copying the
manufacturer's number into the field, silently drops the hoses and the Y-piece
and shortens the machine lag by about a third. That is a wrong clinical value
reached from a correctly-cited source, and no check in the tree can catch it:
`tools/doc_check.py`'s `check_provenance` asks whether every leaf number in
`data/**/*.json` has a row in `docs/MODEL.md`, never whether the number means
what the field means.

**The number, taken from the survey rather than re-derived.**
`docs/machine-survey.md` § "(a1) Apparatus gas volume" prints the apparatus
volume and the with-a-1.2 L-patient-circuit total side by side, both Shin et
al.'s, with the right-hand `tau_C` column computed at this project's own
4.0 L/min default. The apparatus-alone column below is the same arithmetic on
the left-hand figure:

| Profile author stores | `tau_C` they get | `tau_C` of the assembled system | Understated by |
| --- | --- | --- | --- |
| Perseus A500, 2.1 L | 31.5 s | 49.5 s (3.3 L) | 36% |
| Zeus IE, 2.0 L | 30 s | 48 s (3.2 L) | 37% |
| Primus, 4.7 L | 71 s | 89 s (5.9 L) | 20% |

The survey's own table states the 50 s and 48 s figures; only the left-hand
column is added here.

**Where the meaning is recorded today, and where it is not.** It is recorded in
exactly one place, and only for the one shipped profile:
`docs/machine-abstraction.md`'s paragraph "The reference profile is a breathing
system, not a machine, and stays one", which says that file's 6.0 L "is
apparatus-plus-circuit", that no source apportions it, and that "A profile built
from Shin et al.'s figures carries a true apparatus volume and takes its 1.2 L
circuit from the run." It is **not** recorded in the schema:
`_BreathingCircuitPayload` in `src/anesthesia_sim/core/parameters.py` declares
`circuit_volume_l: PositiveFinite` under a docstring that explains
`default_fresh_gas_flow_l_min` and `deliverable_fresh_gas_flow_range` at length
and says nothing about this field. Nor in the public frozen
`BreathingCircuitParameters`, whose other optional field carries a comment about
its meaning and this one carries none. Nor in
`reference_circle_system.json`'s own `sources` notes or `provenance_gap`, which
reason about the sum without ever stating the rule. Nor as a rule in
`docs/MODEL.md`, which describes the survey's composition in passing under "What
real workstations hold, and why that does not settle this row either" but states
no constraint a profile author is bound by. A profile author reads the schema
and the data file; the one document that carries the meaning is a design
document they have no reason to open.

**What makes it not live today.** Two independent things, and both are about to
change. First, one profile ships, and its stored 6.0 L is already correct under
the meaning this item pins: `reference_circle_system.json`'s Targ entry compares
`circuit_volume_l` plus the reference patient's 2.5 L alveolar volume — 8.5 L —
against the measured 9.86 L, rather than comparing 6.0 against it, so the file
already treats its own figure as a declared sum. This item therefore changes no
stored value and no displayed number. Second, a second profile is unreachable
anyway: `load_reference_circle_system_parameters()` in
`src/anesthesia_sim/core/parameters.py` hardcodes the one filename, so a file
dropped into `data/machines/` is ignored by the runtime.

**What would make it live.** A second profile, authored from a manufacturer's
technical data or from Shin et al., reaching a run — which is `PL-2FZ9` (load a
machine profile by id, the item that makes a second profile loadable at all).
At that moment the field is populated by someone reading a technical-data table,
and the conflation costs a displayed curve. The gap between `PL-2FZ9` landing
and this landing is the whole of the exposure, which is why this ranks above the
rest of the framework work rather than below it.

**Recommended fix: pin the meaning, do not split the field.** Three edits, all
prose, no behavior change:

1. `_BreathingCircuitPayload`'s docstring gains a paragraph saying
   `circuit_volume_l` is the assembled total, apparatus plus patient circuit,
   and that a manufacturer's apparatus-alone figure must have a patient-circuit
   volume added before it is stored — naming the 1.2 L the survey's own totals
   were computed with, and where it came from.
2. `reference_circle_system.json`'s `provenance_gap` states the same rule for
   its own 6.0 L, so the author of the *next* file meets it in the file they
   are copying.
3. `docs/MODEL.md` states it as a rule in the breathing-circuit material rather
   than as a remark about the survey, since `docs/MODEL.md` is the authoritative
   specification and the only one of the three a reviewer is obliged to read.

**Why the expensive half can be deferred.** The expensive fix is
`docs/machine-abstraction.md`'s own design: split the field into an
`apparatus_volume_l` the machine owns and a patient-circuit volume the run
owns, summed at construction. That is the right end state and it is not urgent,
because it buys nothing this pinning does not once the meaning is unambiguous —
a profile author who knows to add the circuit stores a correct total either way.
It costs a run-level opening-conditions surface the tree does not have
(`PL-QW19`, the required `default_fresh_gas_flow_l_min`, is the same seam at its
cheap end), a migration of the one shipped profile whose sum no source
apportions, and a change to every construction path. Deferring is safe in the
direction that matters: the pinned meaning is exactly what the split would have
to preserve, so nothing written under this item is thrown away by it.

**What would falsify this.** Any of: a surveyed manufacturer figure that turns
out to *include* the patient circuit, which would make the composition ambiguous
rather than unstated and change what the sentence must say; a decision to give
the model a separate patient-circuit compartment, which removes the sum
entirely; or `apparatus_volume_l` landing first, which makes a rule about a
single field moot. None is on the roadmap today. If the survey's 1.2 L turns out
to be the wrong addend for a machine whose tubing set differs, that narrows the
recommended sentence rather than refuting the item — the hazard is a field with
no stated composition, not the particular number.

**Not in scope.** The stored 6.0 L does not change; `docs/machine-abstraction.md`
already decided that the reference profile keeps its figure as a declared sum
and that real machines are added beside it rather than by retrofitting it. No
`apparatus_volume_l` field, no run-level patient-circuit input, no loader
change, no second profile, no new validation. Nothing displayed moves, which is
what makes this cheap to review.

**Done when.** `circuit_volume_l`'s composition — the assembled total, apparatus
plus patient circuit, never a manufacturer's apparatus-alone figure — is stated
in `_BreathingCircuitPayload`'s docstring, in `reference_circle_system.json`'s
own notes, and as a rule in `docs/MODEL.md`; each statement names what a profile
author must add to a published apparatus figure and where that addend comes
from; no stored value has changed; and `make check` is green. The `verify:`
command greps `docs/MODEL.md` and `src/anesthesia_sim/core/parameters.py`
for the shared phrase **"is the assembled total, apparatus plus patient
circuit"**, so write the sentence around that clause in both.
