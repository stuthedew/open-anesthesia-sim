# Sources of the stored values

This document gives the source of each value the simulator stores: the
provenance table with each value's file and key, how each source was read,
and why each value was chosen over the alternatives. A separate document,
`docs/MODEL.md`, specifies the model those values enter.

## Parameter provenance

No scientific parameter may be added without:

- a full source citation;
- the value and unit used;
- the definition used by the source;
- the temperature or reference conditions when relevant;
- any conversion performed;
- the tissue-group mapping;
- a brief justification for selecting that source;
- the source's tier in the hierarchy below; and
- where the source is not a primary measurement, what the primary literature
  reports and how far that differs from the source's value.

### Source hierarchy: what may be cited as the authority for a value

A citation records where a number was found, and does not on its own say
whether anything was measured there. This project ranks sources in three tiers.
Only a source in the first tier may be named as the authority for a stored
value on its own strength. A lower tier may be adopted only on a recorded
decision, under the rule set out after the three tiers.

1. **Primary measurement.** A study in this tier measured the quantity in the
   species, population and conditions that the model claims to represent, and
   reports the value, its dispersion and its reference conditions. Examples
   are Strum and Eger's sevoflurane blood:gas measurement
   (0.686 ± 0.047 at 37 °C, n=19) and Yasuda, Targ and Eger's human
   tissue:gas coefficients.
2. **Secondary synthesis.** A source in this tier is a review, textbook,
   monograph or consensus document that collects primary measurements without
   making one. It is a good way to find the primary source, and to record the
   figure the field usually quotes, such as the textbook blood:gas coefficient
   of 1.4 for isoflurane. It cannot by itself be the authority for a stored
   value, because the reader cannot see how it rounded values or chose between
   measurements that disagree.
3. **Reference implementation.** This tier holds another simulator's
   parameter set, the numbers that a working program was built to run on.
   Gas Man, a widely used teaching tool, is this project's reference
   implementation. Its parameter set is useful in two ways. The set defines
   Gas Man's behavior, so this simulator can be compared with it. The set is
   also complete and internally consistent, whereas the primary literature
   supplies scattered measurements made in different laboratories on
   different cohorts. **A parameter set is still not a source of
   measurements.** It is assembled to make a program behave. Nobody can
   recover from the program which measurement each number descends from, or
   what was adjusted to make the set consistent. **Gas Man's behavior has been
   compared with measurements in patients**, and the agreement is materially
   worse during wash-in than during maintenance. `docs/MODEL.md` § "Known limitations" gives
   the figures and the limits they set.

**A tier-2 or tier-3 source may be adopted, but never silently.** The ranking
says which tier a reader may trust without examining it. Nearly half of this
project's provenance table is tier-2 or tier-3 numbers (§ "Where this project
stands", below, gives the counts). The ranking forbids an adoption the reader
cannot see, so a stored value whose authority is not a primary measurement must
have three things recorded. Every such value has all three today:

- **The tier, on the source's own entry in the simulator's data files, with
  the stored values that rest on that source.**
- **Why no tier-1 source was adopted.** The reason is recorded on the source
  entry, or once for the whole data file where no tier-1 source was adopted
  for any value in it.
- **The date and whose decision it was**, where a lower tier was adopted in
  preference to an available primary source rather than for want of one. The
  three blood:gas coefficients are an example: the project owner decided on
  2026-09-03 to keep the Gas Man values and label them.

The bar for adopting a lower tier is higher than for citing a tier-1 source.
Only two reasons are allowed, and the work of finding a primary source is not
one of them:

1. **No primary measurement of *this quantity, in this population* exists or
   is reachable.** This applies to every parameter of the reference patient,
   including those with a primary citation beside them. Hudgel and Devadatta
   measured awake functional residual capacity, whereas the stored volume
   describes an anaesthetised lung. Cattermole et al. measured a different
   population. Janssen et al. report a muscle mass, whereas this model stores
   a volume. Each parameter's note says which of these cases applies, so its
   citation serves as a comparison and not as a source.
2. **The value belongs to a set whose internal consistency is part of what is
   being modelled**, and replacing it would mean mixing primary measurements
   from different laboratories and cohorts. This is the argument for tier 3
   given above. The three blood:gas coefficients are an example. Between them, Eger, Strum and Eger, Lerman et al., and
   Esper et al. 2015 measured all three in this population, so the first
   reason does not cover them. But placing one laboratory's blood:gas figure
   among Gas Man's tissue values would make the simulated curve a mix of two
   parameter sets with different origins. The same objection applies to
   dividing a Gas Man curve by a MAC taken from Mapleson. For the MAC, the
   project owner accepted that cost on 2026-11-14, for the reason that
   § "Delivery-limit and MAC parameters" gives.

The second reason is the narrower of the two. It applies only where the source
entry cites the primary measurements with their values and records how far the
stored value differs from them, so that the reader can see what the choice
costs. For the three blood:gas coefficients, the stored values are 0.9% to
26.3% below the measured ones. A later part of this section gives each
difference, the date of the decision, and the planned route to measured
coefficients for all three, which would remove this reason for them.

A stored value can name a source and state its tier while no measurement of
that quantity supports it, and in this simulator that is the ordinary case.
Where a primary measurement *is* available and simply has not been adopted,
the source entry says so in those words.

**Holding a source's full text does not change its tier.** The project owner
keeps the full texts in a private corpus, so that a claim can be checked
against the source itself. `docs/references/` holds no full text. It records
each source's full citation, in `docs/references/README.md`, and notes of the
values taken from it. Baker and Farmery's 2011 *Comprehensive
Physiology* review of inert gas transport in blood and tissues is the closest
published statement of what `docs/MODEL.md` specifies. For any individual number
in it, the review is still a tier-2 synthesis.

**Republication does not promote a value between tiers.** A peer-reviewed
paper that prints a reference implementation's parameter table is still a
tier-3 citation. Two of this project's three tier-3 citations are of that kind, and
neither measured a coefficient. Both are Gas Man simulation studies, and the
third citation is the Gas Man Workbook itself. Table 1
of De Wolf et al. 2012 is the parameter set that the authors fed to Gas Man,
and Weber et al. 2021 describe the product's standard 70 kg patient. The two
papers do not even agree on what Gas Man's set holds. Weber et al.'s Table 1
prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane and 1.1% isoflurane. De Wolf et
al. state 2.0% and 1.2%, which this simulator stored on De Wolf's authority
until 2026-11-14. Yet every partition coefficient the two print is the same.
<!-- not-restated: 70 kg -->

**For developers.** Each entry under `sources` in a data file must record its
tier in a `tier` field, and the project's checks reject a tier outside the fixed
list. The entry's `authority_for` field lists the stored values that rest on
it. Where the reason why no tier-1 source was adopted covers a whole file, it
goes in the file's `provenance_gap` field. Where a primary measurement is
available and has not been adopted, the entry's `adopted` field records that no
primary measurement backs the value. The field exists because of the ordinary
case described above.

Three rules apply to an entry under `sources`:

- Where the stored value is not a primary measurement, say in the entry's note
  which value the primary literature reports and by how much the two differ.
  Use words that a reader comparing against a textbook can act on.
- Do not let a primary citation stand in for a primary value. Citing a
  measurement *alongside* a tier-3 number does not source that number. A file
  that looks sourced while its number came from somewhere else is worse than
  one that cites nothing, because it stops the reader checking.
- Where no primary source has been adopted, record it as an open gap. "No
  primary source has been adopted for this value" is a legitimate provenance
  state for an educational simulator, and one that can later be fixed. A
  tier-3 citation presented as settled is neither legitimate nor marked for
  fixing.

Saying that a constant comes from Gas Man, or from a paper that reprints Gas
Man's table, presents a tier-3 source as though it were a measurement. Citing
De Wolf et al. 2012 or Weber et al. 2021 as though a value had been measured is
the same error.

#### Where each stored value comes from

**Where this project stands.** Of the 49 rows in the table of stored values
below, 27 are tier 1, seven are tier 2, 13 are tier 3, and two adopt no source
of any tier. The 13 tier-3 rows
all come from Gas Man: the three blood:gas partition coefficients and ten of the
eleven parameters of the reference adult patient. The
blood:gas coefficients are the Gas Man set as published by De Wolf et al., and
the ten patient parameters come from the Gas Man default patient. The two rows
that adopt no source are the anesthesia machine values: a circuit volume that
departs deliberately from the published Gas Man figure, and a default fresh gas
flow with no published counterpart.

**Of all the stored values, MAC (`mac_at_age_40_percent`) is the only one
used as a divisor for a displayed concentration.** The liquid density is the
divisor for the displayed millilitres of liquid agent (`docs/MODEL.md` § "Agent
amount"). The three stored MAC values are Mapleson's 1996 meta-analytic MACs at
age 40. MAC divides every value shown in MAC multiples, so its tier affects a
displayed clinical value as well as a starting dial position. § "Delivery-limit
and MAC parameters" states what that costs, and `docs/MODEL.md` § "Known
limitations" records it. Two sources are cited beside the MAC values but not
adopted: De Wolf et al.'s Gas Man values, which the agent files stored until
2026-11-14, and the age-related iso-MAC charts built on Mapleson's analysis.

**The thirty-four rows that adopt a source other than Gas Man are of seven kinds.**

1. **All nine tissue:gas partition coefficients**, three per agent, from Yasuda,
   Targ and Eger 1989. They are human autopsy measurements at 37 °C, adopted as
   primary on 2026-09-13 after the stored values were checked against that
   paper's Table 1. § "v0.2.0: isoflurane and desflurane" says how they were
   checked, and why the published figures were *not* substituted for the stored
   ones.
2. **The eleventh reference-patient parameter, the venous pool volume**
   (`venous_pool_volume_l`), from Davis and Mapleson 1981. It is tier 2, adopted
   on 2026-09-07 on the project owner's decision.
3. **Three vaporizer maxima.** Each is the calibrated maximum of a device
   rather than a physiologic quantity, and each cites a primary source: the
   Dräger Vapor 2000 specification for sevoflurane, and published
   vaporizer-performance measurements for isoflurane (Kelly and Kong 2011)
   and desflurane (Johnston et al. 1994, on the Tec 6).
4. **Six MAC-awake rows**, a fraction and a standard deviation for each agent.
   They are adopted primary measurements: Katoh et al. 1993 for sevoflurane
   and isoflurane, and Chortkoff et al. 1995 for desflurane.
5. **Nine liquid-density rows**, a density, its standard deviation and its
   measurement temperature for each agent. They are Laster, Fang and Eger
   1994's primary measurements at 20 °C, adopted on 2026-10-26.
   <!-- provenance: data/agents/sevoflurane.json liquid_density.measured_at_celsius = 20 -->
   <!-- provenance: data/agents/isoflurane.json liquid_density.measured_at_celsius = 20 -->
   <!-- provenance: data/agents/desflurane.json liquid_density.measured_at_celsius = 20 -->
6. **Three molar masses**, ChEMBL's formula masses, adopted the same day. They
   are tier 2 because a molar mass is computed from the molecular formula and the
   standard atomic weights, not measured on the agent, so no tier-1 source exists
   for one (`docs/MODEL.md` § "Agent amount").
7. **Three MACs at age 40**, from Mapleson's 1996 meta-analysis. They are tier 2,
   adopted on 2026-11-14 on the project owner's decision (§ "Delivery-limit and
   MAC parameters").

**Each agent's data file cites primary blood:gas measurements beside its tier-3
blood:gas value, and marks each one as not adopted.** The sources are Strum and
Eger for sevoflurane, Eger for desflurane, Lerman et al. 1984 for isoflurane,
and Esper et al. 2015 for all three. Each entry records the measured value and
how far the stored number differs from it. Against the older measurements the
stored values are sevoflurane −5.2%, isoflurane −11.0% and desflurane −0.9%.
Esper et al. 2015 measured all three agents in 120 surgical patients at 37 °C.
Only its abstract was read. Against its means the stored values are sevoflurane
−12.2%, isoflurane −10.3% and desflurane −26.3%, so desflurane has the widest
gap in the project, about 3.8 of Esper's standard deviations.

The Gas Man study that prints this parameter set notes the gap in its own
footnote: its blood/gas coefficients "differ from them observed by Esper et al."
(Weber et al. 2021, Table 1). `docs/VERIFICATION.md` § "The early wash-in curve against the published
figures" records what Esper's desflurane value would do in this model. The Gas
Man values were kept and labelled on 2026-09-03, rather than moved to the
textbook 1.4 or to Lerman's measured 1.46 for isoflurane. The route to primary
values for all three agents is a planned milestone (`ROADMAP.md`
planned-milestone item 31).

**The reference patient's data file still adopts no primary source for any of
its eleven parameters, and records that in those words.** A measurement cited
beside a tier-3 number does not source it, which is the second of the three
rules below. So none of the five comparisons in the next paragraph changes or
promotes a stored value.

**Five of the eleven patient parameters have a measurement cited beside them
and explicitly not adopted.** For each, the patient's data file gives the
measured value, its reference conditions, and how far the stored number sits
from it. Hudgel and Devadatta measured FRC by helium dilution in ten healthy
men. Read with Wahba's review of the roughly 20 percent reduction under general
anaesthesia, that measurement brackets the lung gas volume. Cattermole et al.'s
686 subjects in the 50–75 kg band give a median cardiac output of 5.51 L/min,
and the stored value is 9.3 percent below it. Janssen et al.'s whole-body MRI
gives a skeletal-muscle mass. Its apparent agreement with the stored muscle
volume is a coincidence, since those men averaged about 86 kg rather than 70.
Heinonen et al.'s PET measurement of resting adipose perfusion is about half
what the stored fat flow fraction implies. Frayn and Karpe's review supplies the
muscle comparison. It also shows that the fat gap concerns the absolute flow,
not the muscle-to-fat ratio, which the stored fractions get right. The fat gap
is the largest of the five, and `docs/MODEL.md` § "Known limitations" records it as well,
because it changes the shape of a displayed curve and not only a number in a
file.

**The other six patient parameters have no comparison, and their data file says
why for each**, so that a missing comparison is not taken for an oversight. Two
are not measurements. The reference weight is a label that no equation uses. The
venous pool is a well-mixed volume that sets the 14.7-second mixed-venous time
constant. It is not the physiologic venous blood volume, which is several times
larger. One, the default alveolar ventilation, is a convention: Gas Man's
program default. The remaining three each combine several tissues into one
group: the vessel-rich volume and flow fraction, and the fat volume. No single
measurement exists of what this model means by each of them.

**Nothing on the longest provenance chain behind the reference patient was
measured by anybody this document can name.** The chain runs Gas Man (tier 3)
→ Lowe and Ernst (tier 2) → ICRP Committee II (tier 2), a committee of the
International Commission on Radiological Protection.

**The lineage is Lowe and Ernst's, not Mapleson's.** The note beneath the Gas
Man Workbook's Model Parameters table (Appendix B, page 168) reads: "Values for
volume, flow and relative flow are taken from Lowe and Ernst, 1981". The book is
*The Quantitative Practice of Anesthesia: Use of Closed Circuit*, Williams &
Wilkins. The Workbook attributes nothing to Mapleson.

**The Workbook's Model Parameters table gives seven of the patient's eleven
values.** Alveolar volume, the three tissue volumes and the three flow fractions
are in the table and equal what is stored. Cardiac output appears only as the
sum of the flow column. Reference weight and alveolar ventilation are not in the
table. **The venous pool's 1.0 L is not in the table at all**: its `Blood` row
reads 5.00 L. Page 183's "Patient default options" describes the interface
controls and carries no numbers.

**The Workbook's Appendix C gives three of the four values that its Model
Parameters table does not supply.** Appendix C, "Gas Man System Defaults", pages
171–72, was read on 2026-09-15 from the private corpus. It prints the program's
defaults file, `GASMAN.INI`, verbatim. Its `[Volumes]` block gives `CKT=8.0`,
`ALV=2.5`, `VRG=6.0`, `MUS=33.0`, `FAT=14.5` and `VEN=1.0`. `[Ratio]` gives
`76`, `18`, `6`. `[Defaults]` gives `VA=4` and `CO=5`. So alveolar ventilation
is stated as a number, cardiac output does not rest on a column sum, and the
venous pool's 1.0 L is in the Workbook after all. Only the reference weight
(`weight_kg`) is in neither appendix. The Workbook's prose states it, together
with the 4 L/min alveolar ventilation, in Chapter 13, page 127.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**None of the Workbook pages above promotes a value to a higher tier.** Their
values are one program's defaults written down more than once, tier 3 each time.
The stored venous pool no longer uses Gas Man's value at all.

**Pages 55–60 and 82–84 of Lowe and Ernst were read at the source**, on
2026-09-08, from an interlibrary-loan scan. Two papers that use the book had
cited it at pages 57 and 83: Lerou and Booij's system model (*Br J Anaesth*
2001;86:12–28) and Couto da Silva, Mapleson and Vickers' study of Lowe's method
(*Br J Anaesth* 1997;79:103–12). Both were read at full text on 2026-09-06. This
repository does not hold the scan, because it is under publisher copyright and
the repository is public. The scan's own record gives the author as Lowe, Harry
J., so his initials are `HJ`, and the Workbook's `HF` is a misprint.

**Lowe and Ernst collects its volumes and flows and cites them onward to four
references, so it is tier 2, a secondary synthesis.** On page 56 it says of
figure 4.1b, the table in which the volumes and flows are printed: "The figure
models a 100-kg patient with normal physiologic organ volumes and blood flows
(9, 19, 20, 26)." Chapter 4's own narrative names three of those references:
Mapleson, Smith et al. and Zwart et al. The reference patient's only provenance
chain goes on past Lowe and Ernst, and still ends in nobody's measurement.

**All four references behind Lowe and Ernst have been identified, and three of
them, references 9, 19 and 20, are uptake-and-distribution models.** Chapter 4's
reference list, on pages 64–65, was read on 2026-09-10 from a second
interlibrary-loan scan, and each reference was matched to its PubMed record.
PubMed holds no abstract and no PubMed Central text for any of the three journal
papers.

- **9.** Mapleson, W.W. An electrical analogue for the uptake and exchange of
  inert gases and other agents. *J Appl Physiol* 18:197, 1963. — PMID 13932730,
  [10.1152/jappl.1963.18.1.197](https://doi.org/10.1152/jappl.1963.18.1.197),
  18:197–204. PubMed titles it "An **electric** analogue for uptake and exchange
  of inert gases and other agents", without the book's *the*.
- **19.** Smith, N.T., Zwart, A., and Beneken, J.W. Interaction between the
  circulatory effects and the uptake and distribution of halothane: Use of a
  multiple model. *Anesthesiology* 37:47, 1972. — PMID 5050101,
  [10.1097/00000542-197207000-00008](https://doi.org/10.1097/00000542-197207000-00008),
  37(1):47–58. PubMed indexes the third author as Beneken **J E**.
- **20.** Zwart, A., Smith, N.T., and Beneken, J.W. Multiple model approach to
  uptake and distribution of halothane: The use of an analog computer. *Comput
  Biomed Res* 5:228, 1972. — PMID 5031801,
  [10.1016/0010-4809(72)90084-5](https://doi.org/10.1016/0010-4809(72)90084-5),
  5(3):228–38. PubMed gives Beneken **J E** again, so `JE` is the reading taken
  here. The grounds are the same as for reading Lowe's initials as `HJ`: two
  independent records against one.
- **26.** *Recommendations of the International Commission on Radiological
  Protection*, p. 151. Report of Committee II on Permissible Dose for Internal
  Radiation. Pergamon Press, Oxford, 1960. — Not indexed by PubMed, which does
  not cover monographs. It could not be reached from this project's build
  machine on 2026-09-10: `www.icrp.org`, `journals.sagepub.com` and `doi.org`
  each returned nothing.

A model takes organ volumes and blood flows as inputs and does not measure
them, so none of references 9, 19 and 20 can be where the values in figure 4.1b
were measured. Reference 26 is the only one of the four that is not an
anesthetic model. It is cited to a single page, and that page ends the chain.

**The chain from Gas Man through Lowe and Ernst to the ICRP report ends at
tier 2, and never reaches tier 1.** Page 151 of the ICRP report was read on
2026-09-10. It carries **Table 8, "Organs of standard man — Mass and effective
radius of organs of the adult human body"**, tabulated for a total body of
70,000 g. A "standard man" is a reference specification agreed by a committee,
and the document's own title is *Report of Committee II*. The table gives no
citation, sample count or dispersion for any row, while each tissue row of
Table 7, on the facing page 150, carries a count in parentheses. Under the
hierarchy at the head of this section, a consensus document that collects
primary measurements without making one is **tier 2**.

**Four of the ten rows in Lowe's figure 4.1b correspond to ICRP's Table 8
closely enough to be an inheritance.** The comparison is at 100 kg, where his
kilogram column can be treated as per cent of body weight: brain 2.1 against
2.1, kidney 0.4 against 0.43, heart 0.4 against 0.43, and muscle 42.6 against
43. Five rows do not correspond: skin 10.0 against 8.7, adipose 15.0 against 14,
blood 7.0 against 7.7, lung 0.8 against 1.4, and bone 12.0 against a skeleton of
10 without marrow or 14.2 with marrow. **The liver is the outlier that matters:
5.7 against 2.4.**
<!-- not-restated: 2.1, 2.4 -->

**The gap in the liver row has a candidate explanation, from this project's
arithmetic rather than from the book.** Liver 1,700 g plus gastrointestinal
tract 2,000 g plus spleen 150 g plus pancreas 70 g is 3,920 g. That is **5.60%
of 70 kg against Lowe's 5.7%**. This group of organs is the hepatoportal
compartment, which an uptake model lumps together because the splanchnic bed
drains through the liver. No other grouping of Table 8 comes as close. Neither
document says that this is what happened, and the match is no evidence against
either author.
<!-- not-restated: 70 kg -->

**The stored vessel-rich volume rests on a lumping decision made one link up the
chain.** The vessel-rich volume (`tissue_groups.vessel_rich.volume_l`) is stored
as 6.0 L. The only grouping of Lowe's compartments that reproduces both that
volume and the stored 0.76 perfusion fraction is kidney + heart + brain + liver,
at 8.6% of body weight. On ICRP's own rows those four organs are **5.36%, which
is 3.75 L at 70 kg**, 38% below what is stored. **No stored value changes
because of this, and none should.** Lumping the splanchnic bed into the liver
compartment is ordinary modelling. `docs/MODEL.md` § "Tissue compartments" already treats
the vessel-rich group as one lumped tissue. Nothing here is sourced to ICRP.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**ICRP's Table 8 has no blood flows.** It gives mass and effective radius, and
nothing else. Yet Lowe and Ernst cite all four references together for "organ
volumes *and blood flows*". So reference 26 cannot be the origin of any of the
perfusion fractions, which set every time constant this model computes. The
fractions must come from reference 9, 19 or 20, and all three of those are models.

**References 19 and 20 measured nothing.** Both were read in full text on
2026-09-10. They share one parameter set. Reference 20's Appendix says its
tables "are the same as used by N. Ty Smith in his article … where he gives the
rationals for our choice", so the provenance lies in reference 19. Reference 19
says that the table this chain would need "lists the **assumed** blood volumes,
tissue volumes, and partition coefficients", and it gives no source for any of
these values. Its *flows* are compiled from "several sources, most of which can
be found in a recent review", which is the authors' own handbook chapter. The
awake cardiac output of 5,800 ml/min is taken from Milnor's chapter in *Medical
Physiology*, 12th edition. The compiled flows did not balance, and the authors
made them balance. Total cardiac output was 3,480 ml/min, against regional flows
summing to 3,290 ml/min, and "the discrepancy was compensated for by adjusting
the values for skin and skeletal muscle flows". **A stated assumption is not a
source, and an adjusted sum is not a measurement.** So neither paper can be
promoted to a higher tier, and neither is a candidate for adoption.

**References 19 and 20 are not the origin of figure 4.1b.** Reference 19
models a 75 kg man in twelve compartments: arterial, brain grey, brain white,
heart, well-perfused organs, poorly-perfused tissue, fat and fatty marrow,
splanchnic, skeletal muscle, skin shunt, vena cava, and lung. Lowe has ten rows
for a 100 kg patient, and the numbers do not correspond. The vessel-rich
equivalent in reference 19 is 64.0% of cardiac output, against Lowe's 76%. Its
fat is 16.3% of body mass, against Lowe's 15.0%.

**The perfusion fractions therefore still have no identified origin.**
References 19 and 20 give different flows for different compartments. Reference
20 names Mapleson 1963, reference 9, only as the source of the model
*concept*. The paragraphs below record what reading it found.

**For developers.** The reference patient's data file is
`src/anesthesia_sim/data/patients/reference_adult.json`, and the anesthesia
machine's is `src/anesthesia_sim/data/machines/reference_circle_system.json`.

The counts of stored-value rows in this section appear at its head and in the
list of the thirty-one rows that adopt a source other than Gas Man. Recompute
all of them with `python3 tools/source_tier_counts.py` rather than by hand. The
script counts the stored values that each source is the authority for (the
`authority_for` list of each `sources` entry), per data file and in total, and
names the source behind every row. Each data file gives the tier of every source
it lists. No check compares the counts in either place with the text, so they
can go stale silently. Whoever changes a count must check that the sentence
around it is still true.

**Mapleson 1963, Lowe and Ernst's reference 9, closes the chain of sources.
Their references 19 and 20 are its Table 1, lumped and relabelled, and most of
its volumes come from their reference 26, an ICRP report.** Mapleson 1963 was
read on 2026-09-10. His Appendix 1 opens:
"*Tissue volumes and blood supplies.* With the following exceptions the volumes
in Table 1 are those for the 'standard man' of the International Commission on
Radiological Protection (I.C.R.P.) (23)…". His reference 23 is that report at
**page 151**, which is Lowe and Ernst's reference 26. So Lowe and Ernst very
likely took the ICRP citation from Mapleson's own reference list. When Table 1
is lumped as Smith's own footnotes describe, it reproduces **all nine rows** of
references 19 and 20. Those nine rows sum to 58.04 litres, against Mapleson's
own 58.04.

**Mapleson's Table 1 is the most honestly sourced document in this chain, and
it still measures nothing.** Its volumes are ICRP's, except for six that he
names one by one. Grey and white matter come from Pittinger et al. The marrows
and bone cortex come from Ellis. He derived skin nutritive himself from forearm
geometry. The arterial-to-venous blood ratio is "taken to be as in dogs". Lung
parenchyma comes from Cander and Forster. The air in the lungs comes from "the
average of all measurements in Dittmer and Grebe in which the average age was
over 20", which "gives a functional residual capacity of 2.5 liters". His flows
are compiled from about twenty sources, with a note on every row. Some rows
come from animals: adrenals from dogs and fatty marrow from goats. One row is
called an *Estimate*. And one row is neither sourced nor estimated: **"Skin
shunt: Values chosen merely to complete cardiac output"**. That row is 1,290 of
6,480 ml/min, which is **19.9% of the total** and the second-largest flow in
the table.
<!-- not-restated: 2.5 liters -->

This model's whole representation of perfusion comes from one assumption in
Mapleson's Appendix 1: "it has been thought legitimate to assume that **the
blood flow to any region is a fixed fraction of the total cardiac output** from
20 to 70 years of age."

**The perfusion fractions this model runs on have no identified origin in any
reference the book names for them.** Reference 26 has no flows at all, and the
other three do not match. Figure 4.1b's flow column cannot be reproduced from
any of the four. On Mapleson's own rows, kidney + heart + brain + liver is 3,820
of 6,480 ml/min, which is **59.0%**. Every well-perfused organ together is
**63.0%**. Lowe has **76%**, and Smith and Zwart have 64.0%. Muscle plus skin
nutritive is 10.2%, against Lowe's 13%. Fat plus fatty marrow is 4.0%, against
Lowe's 5%. **This finding covers only the four documents that have been read.**
An origin may still exist: the book prints more than one table, and Gas Man may
lump differently.
<!-- not-restated: 5 % -->

**Three stored values also appear in those tables, but none of them comes from
there.** They are an alveolar ventilation of 4 l/min, a functional residual
capacity of 2.5 l in reference 20's table only, and a skeletal muscle tissue
volume of 33 litres. Two of the three figures in those tables descend from
Mapleson, and one is a coincidence. The 2.5 L is Mapleson's functional residual
capacity. It is a mean of published human measurements, cited to Dittmer and
Grebe's *Handbook of Respiration*, and not a round number somebody chose. It is
still not the stored value's source. Mapleson's row is FRC plus half the tidal
volume, whereas this model stores an alveolar gas volume. The stored value also
reaches this project through Gas Man. Gas Man's upstream source is Lowe and
Ernst, who state no alveolar gas volume at all. The 33 is Mapleson's muscle 30
plus skin nutritive 3, which is exactly how Smith prints it. It is *not* the
stored 33.0, because Lowe's muscle row is 29.8 L at 70 kg and reproduces the
stored value under no grouping. Alveolar ventilation of 4 l/min stays a
coincidence, because Mapleson gives a formula, not a figure. **No stored value
changes because of these findings.**
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

Mapleson 1963 is one of the four documents read, but that does not make
Mapleson the *Workbook's* source. The Workbook attributes nothing to Mapleson.
Lowe and Ernst cite him for a table they collected, two links further up the
chain.

**The book's model patient weighs 100 kg, which is why the material arrives in
this project as fractions.** Page 56 picks that weight so that "the organ
weights can also be read as per cent of total body weight". So Lerou and
Booij's Table 6 of fractions is the book's own table divided by 100, not a
normalization they performed. Nothing in the book states a 70 kg parameter set.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The book's cardiac-output relation gives 4.84 L/min at 70 kg, against the
5.0 L/min stored here.** Page 59, read at the source, gives the cardiac output
for its worked prime dose as $`2M^{3/4}`$ dl/min, "or 63.25 dl" for the 100 kg
patient. That is 0.2 times body mass to the three-quarter power in L/min. The
stored 5.0 would need 73.1 kg. The worked value of 63.25 dl determines the
exponent on its own, without reading a superscript off a scan. The stored
cardiac output stays a fixed 5.0, and `docs/MODEL.md` § "Known limitations" gives the
reasoning.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

**The cardiac-output relation is derived, not measured, and pages 17–19 show
how.** Page 59 states $`2M^{3/4}`$ without citing anything. Chapter 2 builds the
relation in three steps, and neither of its two constants is a cardiac-output
measurement:

- **Figure 2.2, page 17** plots oxygen consumption against body weight for
  mammals from 0.03 kg to 8,000 kg. The plot is linear on log–log axes, and the
  slope is given as "approximately 10 kg^(3/4)". The figure is reproduced by
  permission from *Brody, S. Bioenergetics and Growth. Reinhold, New York,
  1945*. It is an interspecies metabolic allometry, not a human study.
- **Page 17** takes the arteriovenous oxygen content difference as "about 5 ml
  of O₂/dl of blood", attributed to Guyton et al. (the chapter's reference 13).
  Guyton et al. are also credited with concluding that kg^(3/4) "is probably a
  better index of cardiac output than any other parameter, including surface
  area". Chapter 2's reference list is outside the pages read, so that
  citation is unresolved.
- **Figure 2.4, page 19** does the arithmetic. kg^(3/4) × 10 gives O₂ use in
  ml/min. O₂ use ÷ 5 gives cardiac output in dl/min, and the figure annotates
  that divisor as "(a–v)DO₂ = 5 ml/dl". The figure also draws the two steps
  combined, kg^(3/4) × 2 → $`\dot{Q}`$ in dl/min, which is page 59's constant.

<!-- not-restated: 2.4 -->

So $`0.2M^{3/4}`$ is Brody's mammalian metabolic allometry divided by an
arteriovenous difference that is assumed constant across mammals. **4.84 L/min
at 70 kg is therefore a derived interspecies extrapolation and must not be
treated as a measured human cardiac output.** This matters in `docs/MODEL.md` § "Known
limitations", the only place in that document that sets the figure beside
Cattermole et al.'s measured median.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**Checked against the book itself, the Workbook's attribution survives for
three of the seven values and fails for four.** The seven are the volume and
perfusion fraction of the vessel-rich, muscle and fat groups, and the alveolar
gas volume. The vessel-rich pair reproduces exactly and *uniquely*. Kidney,
heart, brain and liver are 8.6% of body weight at 76% of cardiac output. That
is 6.02 L at 70 kg against the stored 6.0, and 0.76 against the stored 0.76.
Of all 1023 non-empty groupings of the book's ten compartments, no other
matches both values to within half a percentage point. The same search finds
**no** grouping for the stored muscle pair (33.0 L at 0.18, against the book's
muscle row at 29.8 L and 0.130), and none for the stored fat pair (14.5 L at
0.06, against adipose at 10.5 L and 0.050). The alveolar gas volume is the
third value that survives, and it survives in a negative sense. The book states
no alveolar gas volume at all. It lumps the circuit and the patient's FRC into
a single ventilatory volume of "about 100 dl". So the Workbook cannot have
taken 2.5 L from it.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.perfusion_fraction = 0.18 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- not-restated: 0.050 -->

**For the four muscle and fat values, the book's split of cardiac output
survives, but the values do not.** The book's five non-vessel-rich compartments
take 13 + 3 + 2 + 1 + 5 = 24% of cardiac output, and the stored muscle and fat
fractions sum to exactly 0.24. Their volumes do not follow: 83.6% of body
weight is 58.5 L at 70 kg, against the stored 47.5 L. So Gas Man appears to
have kept the book's 76/24 flow split, and to have redistributed the 24 across
two compartments where the book has five, over a smaller tissue volume. That
arithmetic is this project's, and it does not prove the Workbook wrong. Gas Man
may lump differently, or may work from a page outside the range supplied. The
data file carries the figures and the detail for each value.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**Nothing is promoted or adopted because of any of it.** All seven values stay
tier 3, with the Workbook as their adopted authority, and Lowe and Ernst stays
cited and not adopted. Learning where Gas Man's numbers came from is not
evidence that they were measured. For the four that do not reproduce, there is
nothing here to adopt. For the ones that do, adopting would mean naming as the
authority a compilation, not a measurement. What the reading
gains is an attribution checked against the document itself, and a known tier
for the next link in the chain.

**The venous pool has a published counterpart, and it replaced Gas Man's
1.0 L.** Davis and Mapleson's paper (*Br J Anaesth* 1981;53:399–405) was read
at the source on 2026-09-07. It describes a standard man of 70 kg with a total
blood volume of 5189 ml and a cardiac output of 6480 ml/min. Page 400 states
that **for models of inhaled anaesthetics** the two venous pools may be
combined, "in which case it would be marginally more accurate to make the
arterial pool 799 ml (15.4% of the total blood volume) and the combined venous
pool 1222 ml (23.6%)". That combined pool is the same object as $`V_v`$ here:
one well-mixed venous pool that carries tissue return. Their Appendix derives
it from the ICRP (1975) blood distribution rather than measuring it, so it is
tier 2. **It was adopted on 2026-09-07, on the project owner's decision**, and
is stored as 1.222 L (`venous_pool_volume_l`). It is called a pool because
"venous blood volume" would suggest the physiologic venous blood volume, which
this is not. At the stored 5.0 L/min cardiac output, the mixed-venous time
constant is 14.7 s, against 12.0 s at Gas Man's 1.0 L. That 1.0 L is a program
default, tier 3. Appendix C's `GASMAN.INI` listing, on page 172, reads
`[Volumes] … VEN=1.0`. Davis and Mapleson's 1222 ml is tier 2 and is the same
object this model has, so the stored pool is a considered replacement for that
default. Nothing argues for restoring 1.0 L.
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->
<!-- not-restated: 70 kg -->

**The larger pool leaves the wash-in comparison unchanged and moves elimination
further from published data.** The 30-minute $`F_A/F_I`$ wash-in distances
from the published cohort means move by 0.01 SD or less (+0.16, +0.31, +0.79, +0.38 SD
at the stored pool). The pool has long since equilibrated by then. So the
published wash-in comparison cannot discriminate between the two values. The
5-minute $`F_A/F_{A0}`$ elimination ratios move **0.11 to 0.13 published SD
further from** their cohort means in each agent's first cohort: sevoflurane
+3.67 to +3.79, isoflurane +4.02 to +4.15, and desflurane +1.02 to +1.13. They move because a larger pool returns
more agent to the lungs. `docs/VERIFICATION.md` § "Published wash-in and elimination validation test"
already attributes a shift in the same direction to this model's rebreathing
circuit rather than to tissue return. This shift is between a thirtieth and a tenth of
the gap it adds to.
<!-- not-restated: 0.31 -->

**Gas Man's 1.0 L is not an arterial compartment under a venous name.** Lerou
and Booij's arterial fraction of 0.2 gives 0.98 L at their 4.9 L total,
within 2% of Gas Man's 1.0 L, which suggested that reading. Davis and
Mapleson's own arterial pool for an inhaled-anaesthetic model is 799 ml, which
is 15.4% rather than 20%. So that coincidence does not survive the primary
source. Their venous pool is the closer structural match, and the time
constants nearly agree: 1222/6480 = 11.3 s, against Gas Man's 1.0/5.0 =
12.0 s. That near agreement is a property of the time constant rather than of
the volume. It is not evidence of a shared lineage, because nothing documents
Gas Man as having taken anything from this paper.

The following table records every stored value. Each value is
loaded from a versioned data file and validated against its schema, rather than
written into the program. That file records full citations, definitions and
reference conditions in its `sources` entries, and the table does not repeat
them.

Each row names the file and the exact key path that locates its value in that
file, so a row traces to one stored value, not to a file that happens to
contain a matching number. A check compares each row's key path and value with
its file, as `docs/MODEL.md` § "How this document is held to the tree" describes. A row for a
derived value states the stored value beside it. The tissue:blood coefficients
are computed from the tissue:gas and blood:gas values when a file is loaded, so
their rows name the key path of the stored tissue:gas value and show the
division.

| Parameter | Selected value | Unit | Source (data file · key path) |
| --- | ---: | --- | --- |
| Blood:gas partition coefficient (sevoflurane) | 0.65 | dimensionless | `data/agents/sevoflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient (sevoflurane) | 1.6923 (= 1.1 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient (sevoflurane) | 3.6923 (= 2.4 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient (sevoflurane) | 52.3077 (= 34.0 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.fat` |
| Blood:gas partition coefficient (isoflurane) | 1.3 | dimensionless | `data/agents/isoflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient (isoflurane) | 1.6154 (= 2.1 / 1.3) | dimensionless | `data/agents/isoflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient (isoflurane) | 3.4615 (= 4.5 / 1.3) | dimensionless | `data/agents/isoflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient (isoflurane) | 53.8462 (= 70.0 / 1.3) | dimensionless | `data/agents/isoflurane.json` · `tissue_gas_partition_coefficients.fat` |
| Blood:gas partition coefficient (desflurane) | 0.42 | dimensionless | `data/agents/desflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient (desflurane) | 1.2857 (= 0.54 / 0.42) | dimensionless | `data/agents/desflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient (desflurane) | 2.3095 (= 0.97 / 0.42) | dimensionless | `data/agents/desflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient (desflurane) | 30.9524 (= 13.0 / 0.42) | dimensionless | `data/agents/desflurane.json` · `tissue_gas_partition_coefficients.fat` |
| Reference patient weight | 70.0 | kg | `data/patients/reference_adult.json` · `weight_kg` |
| Alveolar gas volume | 2.5 | L | `data/patients/reference_adult.json` · `alveolar_gas_volume_l` |
| Venous blood-pool volume | 1.222 | L | `data/patients/reference_adult.json` · `venous_pool_volume_l` |
| Vessel-rich tissue volume | 6.0 | L | `data/patients/reference_adult.json` · `tissue_groups.vessel_rich.volume_l` |
| Muscle tissue volume | 33.0 | L | `data/patients/reference_adult.json` · `tissue_groups.muscle.volume_l` |
| Fat tissue volume | 14.5 | L | `data/patients/reference_adult.json` · `tissue_groups.fat.volume_l` |
| Vessel-rich flow fraction | 0.76 | dimensionless | `data/patients/reference_adult.json` · `tissue_groups.vessel_rich.perfusion_fraction` |
| Muscle flow fraction | 0.18 | dimensionless | `data/patients/reference_adult.json` · `tissue_groups.muscle.perfusion_fraction` |
| Fat flow fraction | 0.06 | dimensionless | `data/patients/reference_adult.json` · `tissue_groups.fat.perfusion_fraction` |
| Default alveolar ventilation | 4.0 | L/min | `data/patients/reference_adult.json` · `default_alveolar_ventilation_l_min` |
| Default cardiac output | 5.0 | L/min | `data/patients/reference_adult.json` · `default_cardiac_output_l_min` |
| Breathing-circuit volume | 6.0 | L | `data/machines/reference_circle_system.json` · `circuit_volume_l` |
| Default fresh gas flow | 4.0 | L/min | `data/machines/reference_circle_system.json` · `default_fresh_gas_flow_l_min` |
| Maximum delivered concentration (sevoflurane) | 8.0 | percent | `data/agents/sevoflurane.json` · `max_delivered_concentration_percent` |
| Maximum delivered concentration (isoflurane) | 5.0 | percent | `data/agents/isoflurane.json` · `max_delivered_concentration_percent` |
| Maximum delivered concentration (desflurane) | 18.0 | percent | `data/agents/desflurane.json` · `max_delivered_concentration_percent` |
| 1 MAC at age 40 (sevoflurane) | 1.8 | percent | `data/agents/sevoflurane.json` · `mac_at_age_40_percent` |
| 1 MAC at age 40 (isoflurane) | 1.17 | percent | `data/agents/isoflurane.json` · `mac_at_age_40_percent` |
| 1 MAC at age 40 (desflurane) | 6.6 | percent | `data/agents/desflurane.json` · `mac_at_age_40_percent` |
| MAC-awake (sevoflurane) | 0.34 | fraction of 1 MAC | `data/agents/sevoflurane.json` · `mac_awake.fraction_of_mac` |
| MAC-awake standard deviation (sevoflurane) | 0.05 | fraction of 1 MAC | `data/agents/sevoflurane.json` · `mac_awake.standard_deviation_fraction_of_mac` |
| MAC-awake (isoflurane) | 0.31 | fraction of 1 MAC | `data/agents/isoflurane.json` · `mac_awake.fraction_of_mac` |
| MAC-awake standard deviation (isoflurane) | 0.05 | fraction of 1 MAC | `data/agents/isoflurane.json` · `mac_awake.standard_deviation_fraction_of_mac` |
| MAC-awake (desflurane) | 0.36 | fraction of 1 MAC | `data/agents/desflurane.json` · `mac_awake.fraction_of_mac` |
| MAC-awake standard deviation (desflurane) | 0.063 | fraction of 1 MAC | `data/agents/desflurane.json` · `mac_awake.standard_deviation_fraction_of_mac` |
| Molar mass (sevoflurane) | 200.05 | g/mol | `data/agents/sevoflurane.json` · `molar_mass_g_mol` |
| Molar mass (isoflurane) | 184.49 | g/mol | `data/agents/isoflurane.json` · `molar_mass_g_mol` |
| Molar mass (desflurane) | 168.04 | g/mol | `data/agents/desflurane.json` · `molar_mass_g_mol` |
| Liquid density at 20 °C (sevoflurane) | 1.5203 | g/mL | `data/agents/sevoflurane.json` · `liquid_density.g_ml` |
| Liquid density at 20 °C (isoflurane) | 1.5019 | g/mL | `data/agents/isoflurane.json` · `liquid_density.g_ml` |
| Liquid density at 20 °C (desflurane) | 1.4651 | g/mL | `data/agents/desflurane.json` · `liquid_density.g_ml` |
| Liquid density standard deviation (sevoflurane) | 0.0008 | g/mL | `data/agents/sevoflurane.json` · `liquid_density.standard_deviation_g_ml` |
| Liquid density standard deviation (isoflurane) | 0.0006 | g/mL | `data/agents/isoflurane.json` · `liquid_density.standard_deviation_g_ml` |
| Liquid density standard deviation (desflurane) | 0.0004 | g/mL | `data/agents/desflurane.json` · `liquid_density.standard_deviation_g_ml` |
| Liquid density measurement temperature (sevoflurane) | 20.0 | °C | `data/agents/sevoflurane.json` · `liquid_density.measured_at_celsius` |
| Liquid density measurement temperature (isoflurane) | 20.0 | °C | `data/agents/isoflurane.json` · `liquid_density.measured_at_celsius` |
| Liquid density measurement temperature (desflurane) | 20.0 | °C | `data/agents/desflurane.json` · `liquid_density.measured_at_celsius` |

The reference patient weight identifies which patient the volumes and flows
describe, and no equation in this model uses it. The compartment volumes and
flows are the source's absolute values for a 70 kg adult, not quantities scaled
from a weight, so changing the weight alone would not rescale them. The litres
are Gas Man's form of the data. The Workbook names Lowe and Ernst as its
source, and that book prints the same material as per cent of a 100 kg body,
with cardiac output an allometric function of mass.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The vessel-rich flow fraction is 0.76 here and 75.8% in one of the two
reachable publications of the same parameter set.** Weber et al. 2021's Table 2
prints 76.00%. The stored value comes from the
Workbook's own page-168 table, which gives the vessel-rich relative flow as
0.76 (read at the source on 2026-09-06). The twelve partition coefficients come
from De Wolf et al. 2012. Their Table 1 prints 75.8, and 75.8 + 18 + 6 = 99.8.
The model requires the flow fractions to sum to 1 within the tolerance that
`docs/MODEL.md` § "Tissue groups" gives, so the published set could not be stored as printed,
even if it were preferred. The difference changes the vessel-rich time constant
by 0.26%, below the resolution of anything a learner reads off the curve. The
De Wolf entry in the reference patient's data file (`reference_adult.json`)
records the difference in full.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->

There is no "arterial blood-pool volume" row, because arterial blood has no
volume of its own in this model (see `docs/MODEL.md` § "Model boundary").

**The circuit volume and the default fresh gas flow adopt no source of any
tier.** The reference patient adopts no primary source but does adopt tier-3
ones, so these two machine rows have the wider gap. Both describe the
apparatus in front of the patient, so they are stored in a third kind of
parameter file, `data/machines/reference_circle_system.json`.

- **Circuit volume, 6.0 L.** The Workbook's own table on page 168 gives 8.0 L.
  De Wolf et al. 2012 give the same 8 L in their Methods, for the simulations that
  used the coefficients in their Table 1. The 6.0 L value came in with the first
  circuit model on 2026-08-22, and no record gives a reason for choosing it. The
  project owner ruled on 2026-09-01 that the exact value is not critical, so 6.0 L
  was kept and not changed to 8.0 L. The smaller volume changes how much of the
  early rise in inspired concentration comes from the machine itself. At the same
  flow, $`\tau_C = V_C/\dot V_F`$ is 90 s here and 120 s at 8.0 L, so the
  apparatus lag is 25% shorter. That lag is the part of the inspired curve that a
  learner is most likely to attribute to uptake. So a run that reproduces a
  published Gas Man trajectory has to set the circuit volume to 8.0 L explicitly,
  and cannot assume that value. Like every circuit volume in this model, the
  6.0 L is one total for the apparatus and the patient circuit together
  (`docs/MODEL.md` § "Breathing circuit"). No source says how it divides between the two.
  <!-- derived: 90 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
- **Default fresh gas flow, 4.0 L/min.** No published counterpart for this
  value exists in any source this project has reached. The Workbook's
  parameter table gives the circuit row a volume and no flow, and describes
  its interface defaults without numbers. The two Gas Man simulation studies
  read here chose flows for their own purposes (De Wolf et al. used 1 L/min,
  and Weber et al. used 10 L/min for washout). The value is a **teaching
  default, not a clinical recommendation** (project owner, 2026-09-20,
  ratified, over lowering it to match contemporary low-flow practice). It is
  well inside the supported range of flows. It puts the circuit time constant
  at 90 s: long enough for the machine lag to show as a distinct phase of the
  early rise, and short enough to resolve within the first minutes of a
  teaching run. The data file labels this a design rationale, not a
  measurement. **The default is also the flow a run starts at when a machine
  profile states none**, because no surveyed machine publishes a startup flow.
  The authority for that fallback is this rationale, not a source. The
  rationale applies to the stored 6.0 L circuit. A smaller circuit gives a
  shorter lag at the same flow, as § "What real workstations hold" below
  computes.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 10 L/min -->

**The project holds one measured circle-system volume, and it bounds the
circuit-volume row rather than replacing it.** Targ, Yasuda and Eger measured a
conventional circle system by water filling at **9860 ml** (*Anesth Analg*
1989 Aug;69(2):218–25, PMID 2764290). The same study lies behind the
inert-circuit entry under `docs/MODEL.md` § "Known limitations". It was read in full text on
2026-09-13 from the private reference corpus. The value is not adopted, because
the measured system included a latex reservoir bag at the Y-piece **standing in
for the patient's lungs**. Adopting 9.86 L as the circuit volume would
therefore put a lung inside the circuit, and then model it again as the 2.5 L
alveolar compartment. The bag cannot be subtracted, because the paper states no
bag volume, and a latex bag full of water distends past whatever it holds as a
gas reservoir.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

What the measurement supplies instead is a **bound and an ordering**. A real
conventional circle system has an assembled volume of at most 9.86 L, apparatus
and patient circuit together. That bound leaves both the stored 6.0 L and the
Workbook's 8.0 L admissible. It also puts the three figures in one order,
6.0 L, 8.0 L and 9.86 L, of which only the last was measured. At 4.0 L/min the
implied circuit time constants are 90 s, 120 s and 148 s.
<!-- derived: 148 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Compare the measured 9.86 L with the model's circuit and lung together, not
with the circuit alone.** Targ measured an assembled system *plus* a lung. This
model's corresponding total is $`V_C + V_A`$ = 6.0 + 2.5 = 8.5 L, which is
13.8% below the measured 9.86 L. Comparing the circuit alone, 6.0 against 9.86,
would show 39% below. The study itself invites the comparison with circuit and
lung together. Its Figures 3 and 5 draw the ideal wash-in and washout as
$`100[1 - e^{-(\dot V/V_S)t}]`$ with $`V_S`$ = 9.86 L. So its own time
constant is total system volume over inflow, the same $`V/\dot V_F`$ that this
document uses. The 9.86 L is compared, not adopted, because a latex bag is not
a lung, and that apparatus had no patient taking up agent.
<!-- derived: 8.5 L from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- derived: 8.5 L from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

**What real workstations hold, and why that does not settle the circuit-volume
row either.** The project's survey of machines in current clinical use
(`docs/machine-survey.md`) covers the variables that affect a number this model
computes. The assembled volumes it gives sit below both figures above. Shin et
al. print apparatus volumes of 4.7 L for a Dräger Primus, 2.1 L for a Perseus
A500 and 2.0 L for a Zeus IE. Each includes the absorber and excludes the
disposable patient circuit. Adding the 1.2 L circuit that they computed their
totals with gives 5.9, 3.3 and 3.2 L. At the default flow, the circuit time
constant therefore runs from 89 s on the oldest of the three machines to about
50 s on the newest. That is a factor of about 1.8 across machines that a
learner would meet in the same department. The stored 6.0 L lies within 2% of
the Primus's assembled 5.9 L. The match is a coincidence: the stored value
predates the survey, and was kept under the project owner's ruling of
2026-09-01.
<!-- derived: 89 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Volume is not the whole of the difference between machines**, as the survey
found. Fukuda et al. moved the fresh gas inlet from beside the absorber to
beside the patient (*J Anesth* 2006;20(4):268–73, read from its abstract).
During low-flow anesthesia on two decoupling-style machines, the
inspired/delivered ratio rose significantly for sevoflurane, and for isoflurane
on the one machine where it was compared. A third machine showed no significant
change. That ratio, $`F_I/F_D`$, is what the circuit equation in `docs/MODEL.md` § "Breathing circuit" computes,
and this model does not represent where the inlet sits. The abstract does not
say whether moving the inlet changed the circuit's volume, so it does not show
on its own that volume was not the cause. Shin et al. show a difference that
volume does not explain. In their test-lung study the Perseus A500 and the
Zeus IE in its fresh gas mode come to nearly the same circuit volume, 3.3 and
3.2 L, and their times to target still differed significantly. Those volumes
are Dräger's stated apparatus volumes plus Shin et al.'s 1.2 L patient circuit,
not measurements. A future per-machine circuit volume (`circuit_volume_l`) will
therefore reproduce only part of the difference between machines, and must not
be described as reproducing all of it. The model will not fold the rest into an
effective volume either, because that would attribute to volume a difference
that volume did not cause. The survey
sets out the consequence for modelling several machines.

**A search for a published source of the default fresh gas flow found a
recommendation, not a convention.** The survey looked for a startup fresh gas
flow published by any machine in current clinical use, and found none
(`docs/machine-survey.md` § "(a2)"). So the flow row still adopts no source,
and no published startup convention appears to exist. Kalmar et al. conclude
that *"routine clinical practice using what historically is called 'low flow
anaesthesia' (e.g. 2 L/min FGF) should be abandoned"* in favour of automated
minimal-flow delivery (*J Clin Monit Comput* 2022;36(6):1601–1610,
PMID 34978655). The paper was read in full text on 2026-09-20 from PubMed
Central, PMC9637609, where the quoted sentence closes the abstract. The
conclusion is the recommendation of a single-centre retrospective study, not a
measurement of what flows are used. But the study's own comparator is a fixed
2 L/min group that it calls conventional low flow, and that flow already sits
below this model's 4.0.

**The 4.0 L/min default makes no claim about clinical practice**, because
no source this project holds supports one. Under the project's safety-critical
standard, a correct number with a wrong provenance is still a presentation
failure. A different default would not remove the problem, because an
unlabelled default teaches a norm whatever value it has. A default of
0.5 L/min would have no source either. It would also put the apparatus lag at
**12 minutes**, longer than the demonstration that the default flow exists to
make.
<!-- derived: 12 minutes from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

**Two papers cited alongside Kalmar et al. in the survey do not bear on
practice, and the survey says so.** Candries et al. randomised flows of
0.2 to 6 L/min in 28 patients, as the protocol of a Gas Man validation study.
Hoffmann et al. ran 0.3 to 6 L/min *in vitro* into a test lung, and describe
those settings as reflecting clinical conditions. That range contains 4, 5 and
6 L/min. A study's chosen flow range is not a report of practice. Treating it
as one is the same error that the De Wolf entry guards against for its 1 L/min
elsewhere in this section.

**Dividing tissue:gas by blood:gas is the literature's own operation, and one
published table reproduces its results.** Eger and Saidman state the operation
in these words: "a tissue/blood partition coefficient for a given anesthetic is
calculated by dividing a tissue/gas partition coefficient by the blood/gas
partition coefficient for that anesthetic" (p. 1023). Yasuda, Targ and Eger
computed their own tissue:blood table the same way, as the next subsection
records. Both papers were read in full text from the private reference corpus.
Eger and Saidman's p. 1023 was read on 2026-10-25. The full citation of Eger
and Saidman is in `docs/MODEL.md` § "Known limitations".

Baker and Farmery's 2011 review publishes the results as well as the
operation. Its Table 2 (p. 572) prints two sets of tissue:blood coefficients
for the vessel-rich, muscle and fat groups. The set that matches the derived
rows is the one in brackets, which the table's footnote d attributes to Eger
and Shafer's 2005 tutorial. Desflurane has only that set. The table was read in
full text from the private reference corpus on 2026-10-25. In each cell below,
the first figure is the derived value from the parameter table above, and the
second is Baker's bracketed figure:

| | vessel-rich | muscle | fat |
| --- | ---: | ---: | ---: |
| sevoflurane | 1.6923 vs 1.69 | 3.6923 vs 3.69 | 52.3077 vs 52.3 |
| isoflurane | 1.6154 vs 1.62 | 3.4615 vs 3.46 | 53.8462 vs 53.8 |
| desflurane | 1.2857 vs 1.29 | 2.3095 vs 2.31 | 30.9524 vs 30.9 |

<!-- derived: 1.6923 from data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 3.6923 from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 52.3077 from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 1.6154 from data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 3.4615 from data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 53.8462 from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 1.2857 from data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 2.3095 from data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 30.9524 from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13, blood_gas_partition_coefficient = 0.42 -->

Baker's bracketed blood:gas values are the three that the agent files store:
0.65 for sevoflurane, 1.3 for isoflurane and 0.42 for desflurane. Eight of the
nine tissue:blood figures are the derived value rounded to Baker's printed
precision. Desflurane's fat coefficient is the exception: 30.9524 rounds to
31.0, and Baker prints 30.9. The difference is 0.05, or 0.17%, in the last
printed digit. That is too small to come from a different operation, and Baker
does not say how the figures were rounded.
<!-- not-restated: 0.05 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 30.9524 from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13, blood_gas_partition_coefficient = 0.42 -->

**The agreement with Baker's table checks that the division is the right
operation and was done correctly, not that the coefficients are right.** It
shows that the stored tissue:gas values, divided by the stored blood:gas
values, give the coefficients as the literature publishes them, which confirms
the operation and its arithmetic. It is not a second measurement. Eger and
Shafer's tutorial ran its simulations in Gas Man, according to its abstract.
The stored tissue:gas values are Gas Man's figures for Yasuda, Targ and Eger's
measurements, and the stored blood:gas values are De Wolf et al.'s. In all
seven cells where Gas Man's figure differs from Yasuda's mean, Baker's
bracketed figure follows Gas Man's. Isoflurane fat is the clearest: 53.8 is
70.0 divided by 1.3, where Yasuda's 64.2 would give 49.4. So the match is one
parameter set divided twice, not two sources agreeing. Eger and Shafer's paper
is not held here, so it is not known which of the two took its figures from
the other. A reader should take the table as evidence that the division is the
right operation, and not as evidence that the coefficients are right.
`docs/MODEL.md` § "Known limitations" says how far other laboratories' coefficients differ
from these.
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Baker's other set of coefficients is not a check on the division.** The
unbracketed figures are "Data from Fiserova-Bergerova and Diaz (26)", a 1986
paper. They come with their own blood:gas values, 0.6 for sevoflurane and 1.4
for isoflurane, and they differ from the derived rows by far more than
rounding. `docs/MODEL.md` § "Known limitations" gives the differences.

The citations of Baker and Farmery 2011, Eger and Shafer 2005 and
Fiserova-Bergerova and Diaz 1986 were checked in PubMed on 2026-10-25 (PMIDs
23737195, 16115976 and 3721592). Only Baker and Farmery was read in full text,
and its full citation is in `docs/references/README.md`.

**For developers.** The patient weight (`ReferenceAdultParameters.weight_kg`) is
loaded and checked to be positive and finite, and nothing else reads it.

Two checks each reject a set of flow fractions whose sum differs from 1.0 by
more than the tolerance in `docs/MODEL.md` § "Tissue groups" (`FLOW_FRACTION_TOLERANCE`). One
runs on the reference patient's data file
(`_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one`), and the other
runs when the patient's compartments are built (`PatientCompartments.__post_init__`).
The tolerance stays as it is, because one loose enough to admit De Wolf's 99.8%
would also admit a transcription error silently.

The fallback starting flow comes from a constant in `core/circuit.py`
(`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`). One test checks that fallback
(`test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`),
and another fails if the constant and the shipped machine file's value ever
differ (`test_the_flow_default_matches_the_shipped_machine_file`).

A design document records the decision not to fold gas-path layout into an
effective volume (`docs/machine-abstraction.md`), and the roadmap says when
that decision is revisited (`ROADMAP.md` planned-milestone item 39).

The tissue:blood coefficients are computed by properties of the class for an
agent's parameters (`AgentParameters`, in `core/parameters.py`). One test in
`tests/unit/test_parameters.py`, `test_derives_tissue_blood_coefficients`,
checks the division of tissue:gas by blood:gas, for sevoflurane.

### v0.2.0: isoflurane and desflurane

Sevoflurane, isoflurane and desflurane share one set of equations, compartments and reference
adult patient (`docs/MODEL.md` § "Governing equations"). An agent enters those equations only through its four
partition coefficients: one blood:gas and three tissue:gas. Its other stored values, such as its
MAC and its vaporizer's maximum, set a control or convert a displayed amount, and the equations do
not use them (§ "Delivery-limit and MAC parameters", `docs/MODEL.md` § "Agent amount"). All twelve coefficients
come from one table, so the three agents' values can be compared directly. The table is De Wolf
et al. 2012, Table 1, from the paper already cited for sevoflurane.

Desflurane is markedly less soluble than sevoflurane, which is itself less soluble than
isoflurane (blood:gas 0.42 < 0.65 < 1.3). Because the equations are shared, lower solubility
only makes the agent equilibrate faster.

<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**The nine tissue:gas coefficients of sevoflurane, isoflurane and desflurane all come from one
study.** In De Wolf's table, they are the Gas Man simulation program's figures for the human
measurements of Yasuda, Targ and Eger 1989. That study measured all three agents' tissue:gas
coefficients side by side in the same specimens, in *one laboratory, with one technique and one
cohort*. Any systematic error in that technique therefore affects every agent alike. When values
are shown as multiples of MAC to compare agents, an error that all three share cannot make one
agent look different from another.

The three blood:gas values can be compared only because they come from one published table. They
are Gas Man's set, at tier 3 of the source grades in § "Source hierarchy".

The argument from a shared source covers the partition coefficients only. The stored MAC values
come from a different source, Mapleson's 1996 meta-analysis, which gives all three agents' MACs at
one age. § "Delivery-limit and MAC parameters" says what that costs.

**Gas Man's Workbook says the nine tissue:gas coefficients come from Yasuda, Targ and Eger, and
the paper confirms it.** The note under the Workbook's page-168 parameter table reads "Values for
isoflurane, halothane, desflurane and sevoflurane are taken from Yasuda, Targ and Eger". That
note alone could not raise the coefficients' source grade, because a program's statement about its
own sources is not independent evidence (§ "Republication does not promote a value between tiers").
The note had two further weaknesses. The Workbook's reference 45 is the 1988 ASA annual-meeting
abstract `Anesthesiology 69:A615`, not Yasuda, Targ and Eger's 1989 *Anesthesia & Analgesia*
paper. And the same Workbook paragraph credits sevoflurane's values to Yasuda and, one sentence
later, to "the package insert and Abbott data".

So the 1989 paper itself was read in full on 2026-09-13. Its Table 1 reports tissue:**gas**
coefficients, the quantity that the model stores. They come from 14 autopsy specimens, 6 to 10
per tissue, with a mean age of 65.8 ± 14.4 yr, equilibrated at 37 °C. In the table below, each
cell gives the stored value, then the paper's mean ± SD, then the difference in SDs.

| | vessel-rich (Yasuda's brain) | muscle | fat |
| --- | ---: | ---: | ---: |
| sevoflurane | 1.1 vs 1.15 ± 0.07 (−0.71 SD) | 2.4 vs 2.38 ± 1.03 (+0.02 SD) | 34.0 vs 34.0 ± 6.0 (exact) |
| isoflurane | 2.1 vs 2.09 ± 0.10 (+0.10 SD) | 4.5 vs 4.40 ± 1.97 (+0.05 SD) | 70.0 vs 64.2 ± 12.3 (+0.47 SD) |
| desflurane | 0.54 vs 0.54 ± 0.02 (exact) | 0.97 vs 0.94 ± 0.35 (+0.09 SD) | 13.0 vs 12.0 ± 2.0 (+0.50 SD) |

<!-- not-restated: 0.05 -->

<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4 -->
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13 -->

All nine stored values lie within 0.71 SD of the measured mean. Two match it exactly. Two more lie
within 1% of it: isoflurane vessel-rich (+0.5%) and sevoflurane muscle (+0.8%). The other five
differ from it by 2.3% to 9.0%, the most for isoflurane fat, which lies above the mean. Values from
another source could not match this closely by chance, so the comparison confirms the Workbook's
attribution. For sevoflurane, it also settles the Workbook's contradiction: the three stored values
match this paper, not a package insert.

Two further points matter for the model:

- **The vessel-rich coefficient is Yasuda's *brain* value.** Table 1 gives
  brain, heart, liver and kidney separately (sevoflurane 1.15, 1.21, 1.25,
  0.78). Sevoflurane's stored 1.1 is 4.3% below its brain value and 0.2% above
  the equal-weight mean of its four organ values, 1.0975, so sevoflurane alone
  does not show whether Gas Man used the brain value or the mean. Isoflurane's
  stored 2.1 is 0.5% above its brain value, 2.09, and desflurane's stored 0.54
  equals its brain value (the table above). These two matches indicate that
  the vessel-rich compartment uses the brain values, and a learner reading its
  trace is reading a brain trace.
  <!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
  <!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1 -->
  <!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54 -->
- **Yasuda's paper is not a source for the stored blood:gas values.** It
  measured none. Its Table 2 tissue:blood figures are calculated "by dividing
  the tissue/gas partition coefficient by the published values for the
  blood/gas coefficients adjusted for age". So Table 1 ÷ Table 2 recovers the
  age-adjusted blood:gas of the 65.8-year-old cohort. Those recovered values
  are 4.9–9.4% above the three round figures stored here.

**For the nine tissue:gas coefficients, the source grade changed and the stored values did not**
(project owner, 2026-09-13). These were two separate decisions.

*Adopted.* The nine tissue:gas coefficients trace back to a primary human measurement. So for all
three agents, the recorded source of these coefficients is now Yasuda, Targ and Eger, at tier 1,
the grade for a primary measurement. De Wolf et al. stays the source for the three blood:gas
values, which this study did not measure. Only the recorded source and grade changed. No number
did.

*Declined.* Storing Yasuda's published figures instead of Gas Man's for the nine coefficients
would change seven of the nine stored values, and the time constant of each compartment they
belong to. Three changes are large. Sevoflurane's vessel-rich time constant would move +4.5%
(coefficient 1.15 instead of 1.1), isoflurane's fat −8.3% (64.2 instead of 70.0), and
desflurane's fat −7.7% (12.0 instead of 13.0). The other four move by 3.1% or less. The accuracy
gained would be smaller than the error the model already makes by lumping brain, heart, liver,
kidney and viscera into one vessel-rich compartment. A lumped compartment cannot use a difference
of 0.05 in a brain measurement. So the Gas Man values are kept.
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13 -->
<!-- not-restated: 0.05 -->

**Desflurane's tissue coefficients were checked against a published measurement and kept.**
Desflurane's elimination at five minutes is the only comparison where the model misses a human
measurement by washing out too fast. That result is most sensitive to the vessel-rich
coefficient, which makes that coefficient the obvious suspect. It is not the cause.
`docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed" gives the reasoning.

**For developers.** Each agent's partition coefficients are in
`data/agents/*.json`, whose `tier` and `adopted` fields record each value's
source. The reference adult patient's physiologic parameters are in
`data/patients/reference_adult.json`. Storing Yasuda's figures would require
recomputing every pinned reference state under `tests/reference/`, because
those states are this parameter set's solution. `tests/unit/test_parameters.py` checks each
stored coefficient against a literal. `tests/reference/test_multi_agent.py`
checks mass balance and equilibrium for isoflurane and desflurane, and that
desflurane's alveolar-to-circuit ratio is above isoflurane's after one minute. Before changing any of desflurane's
coefficients, read `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed".

### Delivery-limit and MAC parameters

This section specifies two of an agent's stored values that play no part in the model's
equations: its maximum delivered concentration and its MAC. A value that a clinician could read or
act on is safety-critical whether or not the model uses it. `docs/MODEL.md` § "Agent amount" specifies the
agent's molar mass and liquid density, and `docs/INTERFACE.md` § "MAC-awake as a chart reference"
specifies its MAC-awake.

The maximum delivered concentration (`max_delivered_concentration_percent`) is the highest
concentration that the agent's real vaporizer can deliver: sevoflurane 8%, isoflurane 5% and
desflurane 18%. It sets the top of the delivered-concentration dial, so that the simulator offers
no dial position that the matching real device lacks. It is a device limit, not a physiologic or
safety limit, and it says nothing about whether a concentration is appropriate for a patient.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json max_delivered_concentration_percent = 5 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

The simulator **must reject** any delivered concentration above the maximum, when a run is set up
and at every later change. It must not lower the value to the maximum instead, because it would
then simulate, display and chart a dial position that was never requested. On screen, that
position looks exactly like one that was requested. Zero is always accepted, because zero is the
vaporizer turned off, which is how washout begins.

**The maximum delivered concentration describes a vaporizer, although it is stored with the
agent.** Each agent's value is the calibrated dial maximum of the vaporizers that its source
names: the Dräger Vapor 2000 and Datex-Ohmeda Sevotec 5 for sevoflurane, the Penlon Sigma Delta
and Datex-Ohmeda Isotec 5 for isoflurane, and the Tec 6 for desflurane. So desflurane's figure
says how far a Tec 6 dial turns. Another desflurane vaporizer, or an injector that delivers into
the circle, is not bound by it.

**These vaporizers work in two different ways.** The sevoflurane and isoflurane vaporizers are
variable-bypass vaporizers: the dial splits the fresh gas between a bypass and a chamber in which
the gas flows over the liquid agent and leaves saturated with vapour. The Tec 6 is not a
variable-bypass vaporizer. Dosch and Tharp call it a gas–vapour blender, which heats desflurane
and adds pure vapour to the fresh gas (`docs/MODEL.md` § "Known limitations" gives their full
citation). Johnston et al. 1994, the source of desflurane's maximum, describe it in their abstract
as "an electrically heated, pressurized, electromechanically coupled dual-circuit blender". The two
designs behave differently away from sea level (`docs/MODEL.md` § "Known limitations"). The model fixes
ambient pressure at one atmosphere, 760 mmHg (`docs/MODEL.md` § "Assumptions"), so it does not need to know which
design each maximum comes from.

The stored MAC (`mac_at_age_40_percent`) is each agent's MAC at age 40 from
Mapleson's 1996 meta-analysis: sevoflurane 1.80%, isoflurane 1.17% and desflurane
6.6%. The reference adult has no age, so every run uses the MAC at age 40, and the
display states that age beside the MAC. The stored MAC has two uses, and both are
presentation. First, it sets the dial's starting position, so that each new run
begins at a recognizable clinical anchor. Second, it is the divisor for the display
in MAC multiples: every displayed compartment value and the chart's second axis are
divided by it. The simulator refuses any agent whose own vaporizer cannot deliver
its 1 MAC, because every run starts the dial at 1 MAC.
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- provenance: data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->

No governing equation reads the stored MAC. The simulation code (`core/`) reads it
in two places: to refuse an agent whose MAC is above its vaporizer maximum, and to
give a run its MAC, which sets the dial's opening position. Specifically, the model
does **not**:

- compute MAC-hours or adjust the MAC for a patient's age, or sum MAC fractions
  across agents;
- model an effect-site compartment or any depth-of-anesthesia endpoint; or
- imply that an alveolar concentration equal to the stored MAC corresponds to any particular
  clinical state in a particular patient.

Presenting a single-agent alveolar concentration as if it indicated anesthetic depth would be
exactly the plausible but wrong clinical inference that the project's safety standard forbids. So
the display shows a *ratio to* 1 MAC, written `×MAC`, and never a depth
(`docs/INTERFACE.md` § "MAC multiples as a display unit").

**The stored MAC carries clinical weight.** An error in it would shift every value shown in MAC
multiples, not only a run's starting point.

**The stored MACs are Mapleson's age-40 values, graded tier 2** (project owner, 2026-11-14, over
keeping De Wolf et al.'s Gas Man values). Mapleson's meta-analysis fits a regression of MAC on age
to the published MAC literature. It gives each agent's MAC at age 40 with 95% confidence limits of
about ±7% (±10% for desflurane). The table compares the stored values with them.

| Agent | Stored MAC at age 40 | Mapleson age-40 | Gap |
| --- | --- | --- | --- |
| Sevoflurane | 1.80% | 1.80% | none |
| Isoflurane | 1.17% | 1.17% | none |
| Desflurane | 6.6% | 6.6% | none |
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- provenance: data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->

Three points decide how far a displayed MAC multiple can be trusted:

1. Mapleson 1996 is a meta-analysis. It fits a regression to published studies and measures
   nothing, so § "Source hierarchy" grades it **tier 2**. A MAC at a stated age is a regression
   over many studies, so no single primary measurement is the value. Mapleson's is the one source
   that gives every shipped agent's MAC at the same stated age, with confidence limits, and it
   gives the equation for the fall in MAC with age.
2. The partition coefficients come from the Gas Man set and from Yasuda, Targ and Eger, and the
   MAC comes from Mapleson. So each displayed multiple is a ratio between values from different
   sources. Comparing agents in MAC multiples is what the display exists for, and that comparison
   now rests on one MAC source for every agent.
3. With confidence limits of ±7-10%, no MAC source makes a comparison between agents exact. The
   display shows the MAC it divides by, with its age, instead of presenting the estimate as
   settled.

No planned milestone moves the MAC to a primary measurement. `ROADMAP.md`'s planned-milestone
item 30 makes the MAC follow the patient's age once age is an input, and item 31 plans a
primary-literature set of partition coefficients beside the stored one.

**For developers.** In the simulation code, the breathing circuit (`BreathingCircuit`) carries
the maximum delivered concentration for the agent in use. The circuit itself **must reject** any
delivered concentration above that maximum, at construction and at every later change, and must
not lower it to the maximum instead. The function that sets up the uptake simulation for an agent
(`AgentUptakeSystem.for_agent()`) gives the circuit that maximum and sets the dial's starting
position from the run's MAC. So the simulation code, not the controller, makes the starting
position agent-specific.

One function builds a run's MAC from the agent and the patient (`mac_for_patient()` in
`core/mac.py`). It returns a `PatientMac`, which holds the MAC in percent and the age it is stated
for. The uptake system, the controller and the display all take the MAC from that function or from
the snapshot fields it fills (`agent_mac_percent` and `agent_mac_age_years`), so no reader divides
by a MAC that another reader did not use.

Every agent file **must** declare a MAC (`mac_at_age_40_percent`) that its own vaporizer can
deliver. A cross-field check in `core/parameters.py` rejects an agent file that does not
(`_AgentPayload._mac_at_age_40_must_not_exceed_vaporizer_max()`). This MAC check runs after every
field is populated, so the order in which the fields are declared cannot defeat it.

Because the stored MAC divides every displayed compartment value, a change to it falls under the
safety-critical standard in `CLAUDE.md`. The list of sources in each agent's file (`sources`)
records Mapleson 1996 as the adopted source, with its tier, and records De Wolf et al.'s value that
the file stored before and how far it differed.

The maximum is stored with the agent for two reasons:

- The reference breathing system in `data/machines/reference_circle_system.json` is not a
  machine and names no vaporizer, so a per-machine entry would only repeat the agent file's
  number.
- The MAC check needs the maximum and the MAC in the same file.

When a machine profile mounts a vaporizer whose maximum differs from the agent file's, the
maximum moves to the profile's per-agent limit, which `docs/machine-abstraction.md` names
`agent_limits`. Two things move with it:

- The MAC check moves to wherever the machine and the agent are paired. Otherwise a machine
  whose limit is below an agent's MAC would reject the run at construction.
- The code in `AgentUptakeSystem.for_agent()` that reads the maximum moves.

The controller reads the maximum from the circuit, and the interface draws its dial from that
value, so the dial follows the move.

Until a profile mounts such a vaporizer, the circuit and the dial read the same number from the
same file.

