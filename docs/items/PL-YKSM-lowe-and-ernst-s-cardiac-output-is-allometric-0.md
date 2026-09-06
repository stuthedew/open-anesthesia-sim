---
id: PL-YKSM
title: Lowe and Ernst's cardiac output is allometric (0.2 x M^0.75 = 4.84 L/min at 70 kg), not the stored fixed 5.0, and weight_kg is still read by no equation
priority: P1
effort: M
status: needs-decision
classes: science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-06
---

**Problem.** `default_cardiac_output_l_min` is stored as a fixed 5.0, and
`weight_kg` is stored as 70.0 and read by no equation in `src/` - the reference
patient's own `sources` note says so in those words, calling the weight "a
labelling convention rather than a measurement". Reading Lowe and Ernst 1981
through a source that used it (`PL-7HDS`) turned up a published relation that
would give the weight a job and replace the constant: da Silva, Mapleson and
Vickers state that Lowe's unit dose is computed with a cardiac output
"estimated from 0.2 x M^(3/4)", where M is body mass in kg, and cite Lowe and
Ernst 1981 for it.

At M = 70 kg that relation gives **4.84 L/min**, not 5.0. The reading of the
relation is checked rather than assumed: the paper's three printed unit doses
for a 70-kg 40-year-old - halothane 0.94 ml, enflurane 1.86 ml, isoflurane
1.00 ml - reproduce to 0.944, 1.856 and 1.001 ml from D = 2 x 1.3 x (MAC/100)
x Q x lambda / r with Q = 4.84, using the MAC, blood:gas and vapour:liquid
values the paper states. Reproducing all three from the same Q is what
establishes that 0.2 x M^(3/4) is being read correctly out of a PDF whose
equation glyphs are mangled.

**Why it matters.** Three separate things, and they are worth keeping apart.

1. **A stored value and its cited lineage do not reconcile.** The Gas Man
   Workbook's flow column sums to 5.00 L/min and the Workbook says its volumes
   and flows are taken from Lowe and Ernst; Lowe and Ernst's own cardiac-output
   relation, as reported by Mapleson's group, gives 4.84 L/min at the 70 kg this
   file claims to represent. 5.00 L/min needs M = 73.1 kg. That arithmetic is
   this project's, from a formula read in a secondary source, and the book has
   still not been opened - so this is a discrepancy to explain, not yet a defect
   to fix.
2. **`weight_kg` has no consumer.** A stored parameter no equation reads is a
   value a reader can change with no effect, which the safety-critical standard
   treats as a presentation failure in waiting. An allometric cardiac output is
   the obvious consumer, and it is the one the cited lineage already implies.
3. **Weight-varying physiology is on the roadmap anyway.** Any patient other
   than the reference adult needs a rule for how cardiac output scales, and
   picking one late means picking it under pressure.

**Where.** `src/anesthesia_sim/data/patients/reference_adult.json`
(`weight_kg`, `default_cardiac_output_l_min`, and the Workbook `sources` note
that records both); `docs/MODEL.md` - "Parameter provenance", and "Known
limitations" if the fixed value stays.

**Decision needed.** Whether to adopt weight-scaled cardiac output at all, and
if so on what authority. Three-quarter-power allometric scaling of cardiac
output is a standard form rather than Lowe and Ernst's invention, so adopting
it would want a primary source of its own - `docs/MODEL.md`'s source hierarchy
does not admit "da Silva et al. say Lowe and Ernst say" as the authority for a
stored value, and would not admit the book either if it turns out to have
collected the relation rather than measured it. The cheap alternative is to
change nothing and record in "Known limitations" that the stored 5.0 does not
reconcile with the lineage the file cites, which is honest and costs one
paragraph.

This is also out of the current milestone: `ROADMAP.md`'s v0.4.x step is "the
code is the model", and a weight-scaled cardiac output is new behavior.

**Done when.** Either the relation is adopted with its own sourcing and
`weight_kg` acquires a consumer, or the file records why the fixed 5.0 is kept
and states the 4.84 L/min discrepancy where a reader of the stored value will
meet it.

**Triaged `science`, P1, on the discrepancy rather than on the feature.** What
pins the band is that a stored clinical parameter and the lineage its own
`sources` note cites do not reconcile - 5.00 L/min against 4.84 L/min at the
70 kg the file claims to represent - which is a provenance defect in a value a
reader can act on, and it stands whatever the decision turns out to be.
Adopting weight-scaled cardiac output is new behavior and out of the v0.4.x
step, as the brief says; the cheap branch of its Done-when - recording the
discrepancy where a reader of the stored value will meet it - is in scope now
and needs no roadmap change.
