---
id: PL-QBKQ
title: The only measured conventional circle-system volume this project holds is 9.86 L including a simulated lung, against a stored 6.0 L and Gas Man's published 8.0 L
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.22
touches: src/anesthesia_sim/data/machines/reference_circle_system.json, docs/MODEL.md
added: 2026-09-13
closed: 2026-09-13
pr: 550
verify: python3 tools/doc_check.py check && grep -q '2764290' src/anesthesia_sim/data/machines/reference_circle_system.json
---

**Problem.** `src/anesthesia_sim/data/machines/reference_circle_system.json`'s
`provenance_gap` says, as `PL-4YY1` left it: "WHAT WOULD CLOSE THIS GAP is a
published circle-system internal volume measured on real apparatus ... neither
has been sought yet." One has since arrived, and the file does not know.

**The measurement.** Targ AG, Yasuda N, Eger EI II. Anesth Analg 1989
Aug;69(2):218-25, PMID 2764290, read at full text 2026-09-13 from the private
reference corpus. Methods: "The total volume of the system, as measured by
water filling, was 9860 ml", for three corrugated polyethylene tubes, a
polypropylene Y-piece and elbow, a soda-lime absorber with inspiratory and
expiratory valves, a rubber bellows in a ventilator, and a latex reservoir bag
attached at the Y-piece elbow to simulate the patient's lungs.

**It does not close the gap, and saying why is the work.** That 9.86 L includes
the simulated lung, so it is not this project's `circuit_volume_l`, which is
the apparatus alone with the patient modelled separately. Subtracting a
reservoir bag would be a guess: the paper states no bag volume. What the figure
does establish is an upper bound on a real conventional circle system's
apparatus volume, measured rather than adopted - and it sits above Gas Man's
published 8.0 L, which sits above this project's 6.0 L. Three figures in one
order, only one of them measured, and none of them measuring quite the same
thing.

**Why it matters.** `tau_C = V_C / VdotF` is 90 s at the stored 6.0 L and 4
L/min, 120 s at 8.0 L, and 148 s at 9.86 L. The apparatus lag a learner sees is
the quantity these differ on, and the project owner has ruled the value
non-critical - so this is provenance work, not a value change.

**Where.** `src/anesthesia_sim/data/machines/reference_circle_system.json` -
the `provenance_gap` and a new `sources` entry; `docs/MODEL.md`'s two machine
provenance rows and the prose under them.

**Done when.** The file cites the measurement, states what it includes and why
that keeps it from being adopted, and no longer claims none has been sought.
**Seated at P1 on the `PL-Q5NS` reading**, not on the value. Nothing displayed
changes and the project owner has ruled `circuit_volume_l` non-critical. What
makes it `science` is that the file currently tells a reader something untrue
about the state of the evidence - "neither has been sought yet" - and a reader
consults a `provenance_gap` precisely to judge how well-founded a value is.
`PL-Q5NS` (`docs/MODEL.md`'s Known limitations omits lung tissue and pulmonary
blood) closed at `P1` with `science, docs` for the same shape: the
specification understating what is known. `docket check` pins the band once the
class is right, so the band here follows the class rather than the urgency.
