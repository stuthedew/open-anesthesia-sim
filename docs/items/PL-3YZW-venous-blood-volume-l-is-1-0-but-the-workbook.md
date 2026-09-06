---
id: PL-3YZW
title: venous_blood_volume_l is 1.0 but the Workbook table it cites has no such value - its Blood row reads 5.00 L
priority: P1
effort: M
status: blocked
classes: science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
blocked-by: PL-8ZJQ
added: 2026-09-06
---

**Problem.** `src/anesthesia_sim/data/patients/reference_adult.json` stores
`venous_blood_volume_l = 1.0` and cites the Gas Man Workbook for it. The
Workbook's Model Parameters table was read at the source on 2026-09-06
(Appendix B, page 168, copy supplied by the project owner) and **it contains no
1.0 L figure**. Its `Blood` row reads `5.00` under Volume - a blood volume for
the whole subject, not this model's venous mixing pool. The table supplies
seven of this file's eleven values exactly; this is one of the four it does not
supply, and the only one of those four that looks like it should be there.

**Why it matters.** A stored value whose cited source does not contain it has
no provenance at all, and until this reading the file asserted that the
Workbook was the source of every value in it. That is now corrected in the
file, but the correction states a gap rather than closing it: nothing in the
tree says where 1.0 L came from.

It is not a large error in behaviour - `V_v` sets only the mixed-venous time
constant `V_v / Q`, which is 12 s at 1.0 L and would be 60 s at 5.0 L - but the
difference is visible on the mixed-venous trace during the first minute of any
simulation, and "which number did we mean" is exactly the question a provenance
record exists to answer.

**Three readings, and the third is the likeliest.** That the value was taken
from a different Gas Man version or screen than the appendix table; that it was
chosen independently as a mixing volume and the Workbook citation was attached
to the file wholesale; or that Gas Man's own venous pool is a fraction of the
5.00 L blood volume and 1.0 L is that fraction. The Workbook chapters supplied
do not settle it: the sections held cover the parameter table and the interface
defaults, not the internal structure of the blood compartment.

**Where.**

- `src/anesthesia_sim/data/patients/reference_adult.json` - the first `sources`
  note, which records the gap.
- `docs/MODEL.md` - the provenance table's "Venous blood-pool volume" row, and
  the "Venous blood" section that defines what the value is for.

**Related.** `PL-BD94` asks whether the key's *name* misleads. This item asks
where its *value* came from. They would sensibly be worked together.

**Done when.** Either the origin of 1.0 L is established and recorded, or the
file states that the value is a modelling choice this project cannot trace to
its cited source - and the provenance table row says the same.

**Blocked on `PL-8ZJQ`** (Davis and Mapleson 1981 gives a published, quantified
blood-pool structure), re-pointed 2026-09-06 from `PL-7HDS` (read Lowe and
Ernst 1981). The original block rested on the book being the only untried
upstream for a stored volume. `#417` read Lowe and Ernst at one remove and
established otherwise: the volumes that reading can account for are the
vessel-rich pair, not this one, and the candidate lineage for a venous mixing
pool is Davis and Mapleson's *Br J Anaesth* 1981 structure - a journal article,
reachable where the monograph is not. `PL-8ZJQ` carries that source and says to
work the two together, so this waits on it rather than on the book.

The second branch of the Done-when stays written and stays insufficient:
`PL-6Q8N` recorded the gap in the file's first `sources` note - "the table's
Blood row reads 5.00 L ... and no 1.0 L figure appears" - and in `docs/MODEL.md`
§ "Parameter provenance". What is left is the first branch, and `PL-8ZJQ` also
names the question to answer before any value changes: whether the stored pool
is doing an arterial compartment's job under a venous name.