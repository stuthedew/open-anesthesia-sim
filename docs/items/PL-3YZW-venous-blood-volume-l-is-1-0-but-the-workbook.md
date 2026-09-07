---
id: PL-3YZW
title: venous_blood_volume_l is 1.0 but the Workbook table it cites has no such value - its Blood row reads 5.00 L
priority: P1
effort: M
status: done
classes: science
feature: model-spec-accuracy
milestone: v0.4.7
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-07
pr: 418
not-delegable: The outcome is a provenance judgment recorded in prose - whether 1.0 L was traced, or recorded as untraceable to its cited source - and a command could only check that some sentence exists in the data file, which is the thing that must not be gameable on a provenance item. Same argument as PL-7HDS and PL-8ZJQ.
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

**Settled 2026-09-07, on the second branch of the Done-when, by reading a
primary source at last.** The project owner supplied Davis and Mapleson (*Br J
Anaesth* 1981;53:399-405) and it was read at the source. Three things follow,
and the first is the one that closes this item.

- **The stored 1.0 L is not in that paper either**, so it is recorded, in the
  data file's new `sources` entry and in `docs/MODEL.md` § "Parameter
  provenance", as a modelling choice this project cannot trace to any cited
  source. That is what this item asked for, and the provenance passage now says
  the same as the file.
- **A published counterpart for the same object now exists**, which is new since
  this item was filed: Davis and Mapleson state that for models of inhaled
  anaesthetics the venous pools may be combined into 1222 ml, 23.6% of a
  5189 ml total blood volume, against an arterial pool of 799 ml. Whether to
  adopt it is `PL-8ZJQ`'s decision, not this item's - this one asked where 1.0 L
  came from, and the answer is still nowhere anybody can name.
- **The related question, whether the key's name misleads, is still `PL-BD94`'s**
  and is untouched by this.

**And the positive answer, asked for by the project owner the same day: it came
from here.** The value entered the repository on 2026-08-22 in `875ba08`, "Build
v0.1.0 sevo patient simulation", the tenth commit, written into the data file
under the citation "Gas Man Workbook and Laboratory Manual. Default Options:
Patient Defaults" - whose note read "The default 70 kg patient uses alveolar
volume 2.5 L, venous volume 1.0 L, alveolar ventilation 4 L/min, cardiac output
5 L/min, tissue volumes 6/33/14.5 L, and flow percentages 76/18/6". `PL-XTMB`
read that section at the source: Appendix E, page 183, which describes the
interface controls and carries no number. Every other value in that sentence is
in the Appendix B table or is an interface default. **1.0 L inherited a citation
its neighbours had earned.**

All four sources ever cited for it have now been read and none contains it: the
Workbook at the source (`PL-XTMB`), Meybohm et al. 2021 at full text from PMC
(2026-09-07 - it states no venous volume and describes Gas Man as a
four-compartment model with no blood compartment in the list, though its tables
could not be retrieved), Lowe and Ernst at one remove (`PL-7HDS`), and Davis and
Mapleson 1981 at the source. So the item closes on a stronger finding than its
Done-when asked for: not "we cannot trace it", but "we have read everything it
was ever traced to, and it is ours".
