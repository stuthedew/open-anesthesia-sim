---
id: PL-LT51
title: Obtain and read Lowe and Ernst's four upstream references for the reference patient's volumes and flows, starting with ICRP Committee II page 151
priority: P1
effort: M
status: done
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md, src/anesthesia_sim/data/patients/reference_adult.json
added: 2026-09-10
closed: 2026-09-10
not-delegable: No command can prove that a person opened a 1963 volume of the Journal of Applied Physiology. Reference 26 was read on 2026-09-10 because the project owner sent the page; references 9, 19 and 20 need the same, and PubMed holds no abstract and no PubMed Central text for any of the three, so nothing this container can run distinguishes a session that read them from one that did not. A `verify:` command here could only check that some sentence had been written into a file, which is the thing that must not be gameable on a provenance item.
---

**Problem.** Obtain and read Lowe and Ernst's four upstream references for the reference patient's volumes and flows, starting with ICRP Committee II page 151

`PL-8SDL` identified them from chapter 4's reference list on pages 64-65,
supplied 2026-09-10 as an interlibrary-loan scan. Identifying them was that
item; reading them is this one, and it is the last link the reference patient's
provenance chain has. Nothing beyond a PubMed record has been read of any of
them.

| # | Citation | Reachability, measured 2026-09-10 |
| --- | --- | --- |
| 9 | Mapleson WW. An electric analogue for uptake and exchange of inert gases and other agents. *J Appl Physiol* 1963;18:197-204. | PMID 13932730, `10.1152/jappl.1963.18.1.197`. Metadata only: no abstract, no PMC record. |
| 19 | Smith NT, Zwart A, Beneken JE. Interaction between the circulatory effects and the uptake and distribution of halothane: use of a multiple model. *Anesthesiology* 1972;37(1):47-58. | PMID 5050101, `10.1097/00000542-197207000-00008`. Metadata only. |
| 20 | Zwart A, Smith NT, Beneken JE. Multiple model approach to uptake and distribution of halothane: the use of an analog computer. *Comput Biomed Res* 1972;5(3):228-38. | PMID 5031801, `10.1016/0010-4809(72)90084-5`. Metadata only. |
| 26 | *Recommendations of the International Commission on Radiological Protection*, p. 151. Report of Committee II on Permissible Dose for Internal Radiation. Pergamon Press, Oxford, 1960. | Not indexed by PubMed. `www.icrp.org`, `journals.sagepub.com` and `doi.org` all returned nothing through the egress proxy. |

**Why it matters.** Every physiologic parameter in `reference_adult.json` is
tier 3 today with no primary measurement adopted for any of them, and this is
the last link in the only provenance chain the file has. If one of these four
measured the organ volumes and blood flows, the reference patient gains a
tier-1 source it has never had; if none did, `docs/MODEL.md`'s
`provenance_gap` should say in those terms that the chain is a compilation of
compilations. Reading reference 26 on 2026-09-10 answered half of that and
made the other half sharper - see the outcome below.

**Read reference 26 first, and it is the one worth an interlibrary loan.**
References 9, 19 and 20 are uptake-and-distribution models: a model consumes
organ volumes and blood flows and does not measure them, so the most any of
them can establish is where *it* got them, which is another link rather than an
answer. Reference 26 is the only one of the four that is not an anesthetic
model, and Lowe and Ernst cite it to a single page - 151 - which is the same
narrowing that made both earlier loans cheap enough to place.

**Do not assume what is on that page.** A 1960 radiological-protection report
is a plausible home for a standard set of organ masses, and "plausible from the
title" is exactly the reasoning `PL-6Q8N` removed when it deleted the Mapleson
lineage. The page is unread. If it turns out to tabulate organ masses, the
further question is whether the report *measured* them or collected them in
turn, which decides whether the reference patient finally has a tier-1 source
or whether the chain is a compilation of compilations - and `docs/MODEL.md`'s
`provenance_gap` should then say which, in those terms.

**Chapter 2's reference list is a second, smaller ask on the same trip.** Pages
17-21 give the derivation of Lowe's cardiac-output relation and attribute it to
"Guyton et al. (13)" and "Kleiber (14)", whose full citations are in chapter
2's own reference list - outside the pages supplied, and probably around pages
22-25. Brody 1945 needs no lookup: the figure 2.2 caption spells it out as
*Brody, S. Bioenergetics and Growth. Reinhold, New York, 1945.*

**Done when.** Each of the four resolves to a document somebody has opened, and
for each the file records whether it measured the reference patient's organ
volumes and blood flows, collected them, or cites them onward again - or
records that it could not be reached and by whom it was tried, which is the
shape `PL-7HDS` used.

## Reference 26 is read, 2026-09-10, and it is the end of the chain

**The project owner sent pages 150 and 151 of the report the same day this item
was filed.** Page 151 is what Lowe and Ernst cite, and it is exactly what the
citation implied it was:

> **Table 8. Organs of standard man.** Mass and effective radius of organs of
> the adult human body.

Three columns - **Mass, m (g)**; **Per cent of total body**; **Effective
radius, X (cm)** - and a total body of **70,000 g**. The rows read, in the
book's order: Muscle 30,000 g / 43%; Skin and subcutaneous tissue 6,100 / 8.7;
Fat 10,000 / 14; Skeleton without bone marrow 7,000 / 10, red marrow 1,500 /
2.1, yellow marrow 1,500 / 2.1; Blood 5,400 / 7.7; Gastrointestinal tract
2,000 / 2.9 (with the four GI contents listed separately and excluded from the
total); Liver 1,700 / 2.4; Brain 1,500 / 2.1; Lungs 1,000 / 1.4; Lymphoid
tissue 700 / 1.0; Kidneys 300 / 0.43; Heart 300 / 0.43; Spleen 150 / 0.21;
Urinary bladder 150 / 0.21; Pancreas 70 / 0.10; then salivary glands, testes,
spinal cord, eyes, thyroid, teeth, prostate, adrenals, thymus, ovaries,
hypophysis, pineal and parathyroids; and Miscellaneous (blood vessels,
cartilage, nerves, etc.) 390 / 0.56. Two footnotes: the total excludes the
contents of the gastrointestinal tract, and the mass of skin alone is taken to
be 2,000 grams.

**The single most consequential fact about the page: it has no blood flows.**
Mass and effective radius, and nothing else. Lowe and Ernst cite references 9,
19, 20 and 26 together for "normal physiologic organ volumes and blood flows",
and reference 26 can supply only the first half of that. **The perfusion
fractions - the half that sets every time constant in this model - are not in
it**, so they descend from references 9, 19 or 20, all three of which are
uptake-and-distribution models. That makes reading those three more valuable
than this item assumed, not less.

**The tier is 2, and it is decidable rather than a judgment.**
`docs/MODEL.md`'s hierarchy puts at tier 2 "a review, textbook, monograph or
**consensus document** that collects primary measurements without making one".
A "standard man" is a reference specification agreed by a committee - the
document's own title is *Report of Committee II* - and Table 8 carries no
per-row citation, no sample count and no dispersion, unlike Table 7 on the
facing page 150, whose tissue rows each carry a parenthesised count. So the
chain that starts at `reference_adult.json` **terminates at tier 2 and reaches
tier 1 nowhere**: Gas Man (tier 3) to Lowe and Ernst (tier 2) to ICRP
Committee II (tier 2). Nothing on this project's longest provenance chain was
ever measured by anybody it can name.

**What still could change that.** Whether ICRP Publication 2 cites sources for
Table 8 elsewhere in the report is unknown - page 151 shows none, and the
report's bibliography was not supplied. If it does, the chain has one more
link. That is a smaller ask than this item started as and it belongs here.

### How Lowe and Ernst's figure 4.1b sits against it

Lowe's table is for a 100 kg patient, so its kilogram column reads directly as
per cent of body weight and is comparable with ICRP's per-cent column. Four
rows correspond, and the correspondence is close enough to be an inheritance
rather than a coincidence:

| Lowe fig. 4.1b | % of body weight | ICRP Table 8 | % of total body |
| --- | --- | --- | --- |
| Brain | 2.1 | Brain | 2.1 |
| Kidney | 0.4 | Kidneys | 0.43 |
| Heart | 0.4 | Heart | 0.43 |
| Muscle | 42.6 | Muscle | 43 |

Five do not, and one of them matters:

| Lowe fig. 4.1b | % | ICRP Table 8 | % | difference |
| --- | --- | --- | --- | --- |
| Liver | 5.7 | Liver | 2.4 | +3.3 pp |
| Skin | 10.0 | Skin and subcutaneous | 8.7 | +1.3 pp |
| Adipose | 15.0 | Fat | 14 | +1.0 pp |
| Blood | 7.0 | Blood | 7.7 | -0.7 pp |
| Lung | 0.8 | Lungs | 1.4 | -0.6 pp |
| Bone | 12.0 | Skeleton, 10 without marrow and 14.2 with | 10 / 14.2 | -2.0 / +2.2 pp |

**The liver gap has an obvious candidate and it is this project's arithmetic,
not the book's.** Liver 1,700 g plus gastrointestinal tract 2,000 plus spleen
150 plus pancreas 70 is 3,920 g, **5.60% of 70 kg against Lowe's 5.7%** - the
hepatoportal compartment an uptake model lumps together because the splanchnic
bed drains through the liver. It is 0.10 pp from Lowe's row and no other
grouping of Table 8 comes as close. **The book does not say this**, page 151
does not say it, and it convicts nobody: Lowe may have taken the row from
somewhere else entirely.

**Why it is worth recording anyway.** `tissue_groups.vessel_rich.volume_l` is
stored as 6.0 L, and `PL-7HDS` established that Lowe's kidney + heart + brain +
liver at 8.6% of body weight is the *only* grouping of his ten compartments
reproducing both that volume and the stored 0.76 perfusion fraction. On ICRP's
own rows the same four organs are **5.36%, which is 3.75 L at 70 kg** - 38%
below what is stored. The stored value therefore rests on a lumping decision
made one link up, and that decision is now visible where before it was not.
**Nothing here is a defect finding and no stored value should move on it**:
lumping the splanchnic bed into the liver compartment is ordinary and defensible
modelling, `docs/MODEL.md` records the vessel-rich group as a lumped
compartment, and no stored value is sourced to ICRP.

### What remains

References 9, 19 and 20, which are now the only route to the perfusion
fractions, and ICRP Publication 2's bibliography if it carries one for Table 8.

## References 19 and 20 are read, 2026-09-10, and neither measured anything

**The project owner supplied both as PDFs.** Read at full text: reference 20 in
full from its text layer, reference 19 from page images (it is a scan with no
text layer) — pages 47–50, which carry the whole Methods section and Tables
1–3, and pages 57–58, which carry the end of the Discussion and the reference
list. Neither is held in this repository.

**Reference 20 defers to reference 19 for its parameters, in one sentence.**
Its Appendix, page 236: "Tables 1–3 give the data which were used for the
model. These tables are the same as used by N. Ty Smith in his article,
'Interaction Between the Circulatory Effects and the Uptake and Distribution of
Halothane', submitted to *Anesthesiology* in 1971, **where he gives the
rationals for our choice**." So there is one parameter set behind both papers,
and reference 19 is where to look for its provenance.

**Reference 19 calls its volumes assumed, and cites nothing for them.** Page
48, in these words: "Table 1 gives some of the miscellaneous data used in the
model. **Table 2 lists the assumed blood volumes, tissue volumes, and partition
coefficients.**" Table 2 carries four footnotes, all of them definitions of what
each compartment contains, and no source. Nothing in the Methods attributes
them.

**Its flows are compiled, and two of them were adjusted to make the sum
work.** Page 50: "The values for the halothane-induced changes in AP, CO, and
regional flows are listed in table 3. **Several sources, most of which can be
found in a recent review, were used to compile these data.** Human data were
used when possible." The recent review is the authors' own — reference 3, Smith
NT and Smith PC, *Circulatory effects of modern inhalation anesthetic agents*,
in Heffter's Handbook of Experimental Pharmacology, Springer, 1972. The awake
cardiac output has its own citation, reference 4: **Milnor WR, "Normal
circulatory function", in *Medical Physiology*, 12th edition, ed. Mountcastle,
CV Mosby, 1968, page 124** — a physiology textbook chapter.

And the compilation did not balance: "The calculated flows were then added and
compared with the independently-determined total flow for 2 per cent. The match
was surprisingly close: total cardiac output was 3,480 ml/min, while the sum of
the regional flows was 3,290 ml/min. **The discrepancy was compensated for by
adjusting the values for skin and skeletal muscle flows.**" That is a parameter
set assembled to make a model cohere, stated plainly by its authors, and it is
the clearest illustration this chain has produced of why
`docs/MODEL.md`'s tier 3 exists.

**So both are tier 2 at best, and the volumes half of reference 19 has no tier
at all** — a stated assumption is not a source. Neither can be promoted, and
neither is a candidate for adoption.

### They are also not the origin of Lowe's figure 4.1b

The compartment sets do not correspond. Reference 19 models **a 75 kg man in
12 compartments**: arterial, brain grey, brain white, heart, well-perfused
organs (kidneys, adrenals, thyroid), poorly-perfused tissue (red marrow,
nonfatty subcutaneous), fat and fatty marrow, splanchnic (organs drained by
portal and hepatic circulations), skeletal muscle (muscle and skin nutritive),
skin shunt, vena cava, lung. Lowe's figure 4.1b is **ten rows for a 100 kg
patient**: lung, kidney, heart, brain, liver, muscle, skin, bone, connective
tissue, adipose.

Nor do the numbers. Reference 19's awake cardiac output is 5.800 L/min, and its
vessel-rich equivalent — brain 0.750 plus heart 0.250 plus well-perfused organs
1.280 plus splanchnic 1.430 — is 3.710 L/min, **64.0% of cardiac output against
Lowe's 76%**. Its fat tissue volume is 12.2 L at 75 kg, 16.3% of body mass,
against Lowe's adipose 15.0%.

**That leaves reference 9 as the only unread one of the four, and the flows
still have no identified origin.** Reference 26 gives masses and no flows;
references 19 and 20 give a different set of flows for a different set of
compartments. Mapleson 1963 is the last candidate, and reference 20's own text
names him as the source of the model *concept* ("The concept of the model is
the same as Mapleson (5) describes"), which is not the same as a source for
these figures.

### Three numeric coincidences with stored values, recorded and not acted on

They are recorded because a later session will otherwise find them again and
have to re-derive whether they mean anything; they are **not** treated as
sources, and `PL-ZD67` carries the question they pose.

| Stored | Value | Where it also appears |
| --- | --- | --- |
| `default_alveolar_ventilation_l_min` | 4.0 | Reference 19's Table 1 and reference 20's Table 1, "Alveolar ventilation 4 l/min" |
| `alveolar_gas_volume_l` | 2.5 | Reference 20's Table 1, "Functional residual capacity 2.5 l" — reference 19's Table 1 does not carry the row |
| `tissue_groups.muscle.volume_l` | 33.0 | Reference 19's Table 2, "Skeletal muscle 33" tissue litres, for a **75 kg** man |

**Why they are worth a second look and still not evidence.** The first two are
the two parameters `PL-7HDS` established Lowe and Ernst cannot supply — page 58
lumps the circuit and the patient's functional residual capacity into one
ventilatory volume of "about 100 dl" and states no alveolar gas volume, and
alveolar ventilation is an interface default the Workbook states no number for.
Finding both in a document Lowe and Ernst cite is the strongest lead this
project has had on either.

**Against that**: 2.5 L and 4 L/min are textbook round numbers for an
anaesthetised adult and would be unsurprising in any model of the period; the
muscle figure is at 75 kg where this file stores 70; there is no evidence Gas
Man read either paper, its stated upstream being Lowe and Ernst; and this
project has already recorded one 33.0 coincidence, against Janssen et al.'s
measured skeletal muscle mass, in exactly these terms. A third 33 makes the
number look more like a convention than like a lineage.

## Reference 9 is read, 2026-09-10, and it closes this item

**The project owner supplied Mapleson 1963 the same day.** Read at full text
from its text layer, with Table 1 and Appendix 1 checked against the page
images. All four references are now read.

**Two of the four are the same document, one link apart.** Mapleson's Appendix
1 opens: "*Tissue volumes and blood supplies.* **With the following exceptions
the volumes in Table 1 are those for the 'standard man' of the International
Commission on Radiological Protection (I.C.R.P.) (23)**, expressed in liters on
the assumption that the specific gravity of all tissues is unity." His
reference 23 is *Recommendations of the International Commission on
Radiological Protection, Report of Committee II. London: Pergamon, 1959,*
**p. 151** — the same page Lowe and Ernst cite as their reference 26. The four
references collapse to two documents, and Lowe and Ernst very likely took the
ICRP citation from Mapleson's own reference list.

**Table 1 is titled "Volumes and blood supplies of different body regions for a
standard man", and its footnote fixes the patient**: "Standard man = 70 kg body
wt., 1.83 m² surface area, 30-39 years." Total volume 70.0 litres excluding the
air in the lungs; total blood flow 6,480 ml/min; total blood in equilibrium
with tissue 5,400 ml. Twenty rows, from adrenals to air in lungs.

### The volumes: ICRP, with six exceptions Mapleson names one by one

- **Grey and white matter** — Pittinger et al., assuming equal volumes of each.
- **Red marrow, fatty marrow, bone cortex** — Ellis.
- **Skin nutritive** — the one he derives himself, and he shows his working:
  "I.C.R.P. give 2 kg, Shohl 4.8 kg, and Spector 4 kg. Skin forms 8.6% of the
  forearm: assuming an average forearm radius of 3.7 cm and that the skin is of
  equal thickness over 1.83 m², the skin volume = 3 liters."
- **Arterial and venous blood** — "the ratio of arterial to venous blood volume
  is taken to be as in dogs".
- **Lung parenchymal tissue** — Cander and Forster.
- **Air in the lungs** — "Average of all measurements in Dittmer and Grebe in
  which the average age was over 20 gives a **functional residual capacity of
  2.5 liters**." Table 1's row reads "2.5 + half tidal vol."

### The flows: about twenty sources, some animal, some estimated, one invented

Every row carries its own note. Kidneys are the mean of Goldring et al. and
Davies and Shock omitting those over 70; heart is Rowe; liver plus portal is a
mean of published values for which age and flow per m² are given; muscle rests
on radioactive-krypton uptake, whole-body nitrogen clearance and forearm
plethysmography with adrenaline iontophoresis; adrenals are **dogs**, fatty
marrow is **goats**; "other small glands and organs" is, in the paper's own
word, an **Estimate**.

And one row is neither measured nor estimated. **Skin shunt: "Values chosen
merely to complete cardiac output"**, with the note adding that the results
still fall inside published ranges of spontaneous variation. It is 1,290 of the
6,480 ml/min — **19.9% of the total**, the second-largest flow in the table.

**One assumption in that appendix is the origin of how this project represents
perfusion at all**: "it has been thought legitimate to assume that **the blood
flow to any region is a fixed fraction of the total cardiac output** from 20 to
70 years of age."

### Smith and Zwart's "assumed" table is this table, lumped

Their Table 2 gives no source and calls itself assumed. Under their own
lumping footnotes it reproduces Mapleson's Table 1 exactly, in **nine of nine
rows**: brain grey 0.75, brain white 0.75, heart 0.30, well-perfused organs
0.34 (kidneys + adrenals + thyroid), poorly-perfused tissue 6.2 (red marrow +
nonfat subcutaneous), fat and fatty marrow 12.2, splanchnic 3.9, skeletal
muscle 33 (muscle 30 + skin nutritive 3), lung 0.6. Their nine sum to 58.04
litres; Mapleson's total less bone cortex, other small glands and the two blood
rows is 58.04.

**Their header calls it "a 75 kg Man" and Mapleson's standard man is 70 kg.**
The volumes are Mapleson's unchanged; only the label moved. Their cardiac
output of 5,800 ml/min is separately cited to Milnor for a 75-kg man, so the
table mixes a 70-kg volume set with a 75-kg flow — an inconsistency inside
reference 19, recorded here because this chain has already been bent once by a
misprint.

### And Lowe's flow fractions match none of the four

This is the finding that matters most, and it is negative. On Mapleson's own
rows, kidney + heart + brain + liver is 3,820 of 6,480 ml/min = **59.0%**, and
widening it to every well-perfused organ gives **63.0%** — against **Lowe's
76%**, and Smith and Zwart's 64.0%. Muscle plus skin nutritive is 10.2% against
Lowe's 13%; fat plus fatty marrow is 4.0% against Lowe's 5%.

So figure 4.1b's flow column is not ICRP's (it has none), not Mapleson's, and
not Smith and Zwart's. **The perfusion fractions this model runs on have no
identified origin in any of the four references the book names for them**, and
that is now established rather than outstanding, which is what closes this item.

### Done when, answered

Each of the four resolves to a document somebody has opened, and for each the
record says what it did:

| # | What it did with the reference patient's volumes and flows |
| --- | --- |
| 9 Mapleson 1963 | Took the volumes from reference 26 with six named exceptions; compiled the flows from about twenty sources including animal data and estimates, one row chosen to close cardiac output. Measured nothing itself. |
| 19 Smith et al. 1972 | Reproduced Mapleson's Table 1, lumped to twelve compartments, calling it assumed and citing nobody. |
| 20 Zwart et al. 1972 | Reproduced reference 19's tables and says so. |
| 26 ICRP Committee II 1960 | Supplied the organ masses, as a committee reference specification. No blood flows at all. |

**`PL-ZD67` closes with this item**, its own test having been the one that
settled it.
