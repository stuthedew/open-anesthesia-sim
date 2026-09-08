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
   this project's, from a formula read in a secondary source at the time this
   was written; the book has since been opened and the relation confirmed at
   the source (see the section added 2026-09-08 below), so this is a confirmed
   discrepancy to explain rather than a defect to fix.
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

## The relation is now read at the source, 2026-09-08 (`PL-7HDS`)

The book was reached by interlibrary loan, pages 55-60 and 82-84. **Page 59
gives the cardiac output for its worked prime dose as 2 kg^(3/4), "or 63.25
dl", for its 100-kg patient** - so 0.2 x M^(3/4) L/min, and da Silva, Mapleson
and Vickers' report of it was right. The reconstruction this brief performed
from their three printed unit doses was therefore unnecessary rather than
wrong, and it is left standing above because it is what made the reading safe
to act on before the book arrived.

**The exponent is fixed by the book's own arithmetic, not by reading a
superscript off a scan.** 2 x 100^(3/4) = 63.25 dl/min, which is the figure
page 59 prints; figure 4.1b's flow column totals 6.3 L/min for the same
patient; and table 5.6's Blood row of 1,891 ml is the minute arterial delivery
at CA = 65 ml/dl, lambda_B/G = 0.46 and Q = 63.25 dl/min. Three independent
figures, one exponent.

**Four things this changes about the decision, and one it does not.**

1. **The 4.84 L/min figure is no longer at one remove.** It is 0.2 x 70^(3/4)
   from a relation printed in the book, against the 5.0 stored here. The
   discrepancy this item was triaged P1 on is confirmed rather than inferred.
2. **The book is tier 2, established** - page 56 cites its volumes and flows
   onward to four references - so adopting the relation on its authority is the
   recorded-decision path `docs/MODEL.md` already admits and Davis and Mapleson
   already used, not a route the hierarchy forbids.
3. **The pages read do not say where the relation comes from.** Page 59 uses it
   in a worked example and cites nothing there; three-quarter-power scaling of
   metabolic rate and cardiac output long predates the book, and its derivation
   would be in a chapter outside the range supplied. So "the book is the
   authority for it" is not yet established even at tier 2, and this brief's
   existing point stands: adopting the relation wants a primary source of its
   own.
4. **The 100-kg basis is new and cuts toward adopting.** Every table in the
   book is for a 100-kg patient, chosen so organ weights read as per cent of
   body weight, and cardiac output is an allometric function of that mass. The
   upstream is a *normalized* parameter scheme throughout; the fixed 5.0 L/min
   and the fixed litres in `reference_adult.json` are Gas Man's form, not the
   book's. That makes `weight_kg` having no consumer a departure from the
   lineage rather than merely an idle field.

**What it does not change:** a weight-scaled cardiac output is still new
behavior and still outside `ROADMAP.md`'s v0.4.x step. The cheap branch of the
Done-when is now met in part - `docs/MODEL.md` and the data file both record
the 4.84 L/min discrepancy against the stored 5.0, sourced to the book rather
than to a report of it - so what is left for this item is the decision itself.

