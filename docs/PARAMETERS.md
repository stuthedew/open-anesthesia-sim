# Sources of the stored values

This document gives the source of each value the simulator stores: the
provenance table with each value's file and key, how each source was read,
and why each value was chosen over the alternatives. A separate document,
`docs/MODEL.md`, specifies the model those values enter.

The source text of this document carries hidden markers. Each one ties a figure
that restates a stored value to the data file that holds the value.
§ "The provenance table, and the markers over restated values" explains them.

## Parameter provenance

No scientific parameter may be added without:

- a full source citation;
- the value and unit used;
- the definition used by the source;
- the temperature or reference conditions when relevant;
- any conversion performed;
- the tissue-group mapping;
- a brief justification for selecting that source;
- the source's tier, as § "Source hierarchy: what may be cited as the
  authority for a value" defines it; and
- where the source is not a primary measurement, what the primary literature
  reports and how far that differs from the source's value.

The build checks part of two of these requirements. The provenance table
below must give each stored value, as § "The provenance table, and the markers
over restated values" describes, but the check reads the value and not its
unit. Each entry under `sources` in a data file must declare its source's tier,
as § "What the data-file format requires of a `sources` entry" describes. A
reviewer checks each unit and every other requirement.

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
   (0.686 ± 0.047 at 37 °C, n=19; *Anesth Analg* 1987;66(7):654-6) and
   Yasuda, Targ and Eger's human tissue:gas coefficients.
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
   worse during wash-in than during maintenance. `docs/MODEL.md` § "Gas Man in
   patients" gives the figures and the limits they set.

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
   § "The stored MAC" gives.

The second reason is the narrower of the two. It applies only where the source
entry cites the primary measurements with their values and records how far the
stored value differs from them, so that the reader can see what the choice
costs. For the three blood:gas coefficients, the stored values are 0.9% to
26.3% below the measured ones. § "The blood:gas coefficients" gives each
difference, the date of the decision, and the planned route to measured
coefficients for all three, which would remove this reason for them.

A stored value can name a source and state its tier while no measurement of
that quantity supports it, and in this simulator that is the ordinary case.
Where a primary measurement *is* available and simply has not been adopted,
the source entry says so in those words.

Three rules apply to an entry under `sources`:

1. Where the stored value is not a primary measurement, say in the entry's note
   which value the primary literature reports and by how much the two differ.
   Use words that a reader comparing against a textbook can act on.
2. Do not let a primary citation stand in for a primary value. Citing a
   measurement *alongside* a tier-3 number does not source that number. A file
   that looks sourced while its number came from somewhere else is worse than
   one that cites nothing, because it stops the reader checking.
3. Where no primary source has been adopted, record it as an open gap. "No
   primary source has been adopted for this value" is a legitimate provenance
   state for a simulator that is not a clinical tool, and one that can later be fixed. A
   tier-3 citation presented as settled is neither legitimate nor marked for
   fixing.

A check on every build enforces part of the second and third rules. For the
second, it checks that each entry declares which stored values rest on it, but
not that a source declared primary and adopted really is where the number came
from. It enforces the third rule only for a file that adopts no primary source
at all. In a file that adopts some, such as each agent file, it does not see
whether each value that rests on no primary source is recorded as a gap. No
check reads the note that the first rule asks for. A reviewer checks that note,
the truth of each declaration, and the third rule value by value.

**For developers.** § "What the data-file format requires of a `sources` entry"
names the field of a data file that records each of these, and the exact rules
its check enforces.
`test_the_stored_blood_gas_coefficients_sit_below_the_measured_ones_as_printed`
recomputes the range of blood:gas differences above, and each difference in
§ "The blood:gas coefficients", from the stored values and the measurements
that each agent file cites.

### Where each stored value comes from

#### Where this project stands

Of the 49 rows in the table of stored values below, 27 are tier 1, seven are
tier 2, 13 are tier 3, and two adopt no source of any tier. The 13 tier-3 rows
all come from Gas Man: the three blood:gas partition coefficients and ten of the
eleven parameters of the reference adult patient. The
blood:gas coefficients are the Gas Man set as published by De Wolf et al., and
the ten patient parameters come from the Gas Man default patient. The two rows
that adopt no source are the anesthesia machine values: a circuit volume that
departs deliberately from the published Gas Man figure, and a default fresh gas
flow with no published counterpart.

**Of all the stored values, MAC (`mac_at_age_40_percent`) is the only one
used as a divisor for a displayed concentration.** The liquid density is the
divisor for the displayed millilitres of liquid agent (§ "Agent amount"). The
three stored MAC values are Mapleson's 1996 meta-analytic MACs at age 40. MAC
divides every value shown in MAC multiples, so its tier affects a displayed
clinical value as well as a starting dial position. § "The stored MAC" states
what that costs, and `docs/MODEL.md` § "MAC multiples" records it. Two sources
are cited beside the MAC values but not adopted: De Wolf et al.'s Gas Man
values, which the agent files stored until 2026-11-14, and the age-related
iso-MAC charts built on Mapleson's analysis.

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
   for one (§ "Agent amount").
7. **Three MACs at age 40**, from Mapleson's 1996 meta-analysis. They are tier 2,
   adopted on 2026-11-14 on the project owner's decision (§ "The stored MAC").

**For developers.** The counts of stored-value rows in this subsection appear
at its head and in the list of the thirty-four rows that adopt a source other
than Gas Man. Recompute all of them with `python3 tools/source_tier_counts.py` rather than by hand. The
script counts the stored values that each source is the authority for (the
`authority_for` list of each `sources` entry), per data file and in total, and
names the source behind every row. Each data file gives the tier of every source
it lists. No check compares the counts in either place with the text, so they
can go stale silently. Whoever changes a count must check that the sentence
around it is still true.

#### The stored values, by data file and key

The following table records every stored value. Each value is
loaded from a versioned data file and validated against its schema, rather than
written into the program. That file records full citations, definitions and
reference conditions in its `sources` entries, and the table does not repeat
them.

Each row names the file and the exact key path that locates its value in that
file, so a row traces to one stored value, not to a file that happens to
contain a matching number. A check compares each row's key path and value with
its file, as § "The provenance table, and the markers over restated values"
describes. A row for a derived value states the stored value beside it. The tissue:blood coefficients
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

#### The blood:gas coefficients

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

#### The tissue:blood coefficients

**Dividing tissue:gas by blood:gas is the literature's own operation, and one
published table reproduces its results.** Eger and Saidman state the operation
in these words: "a tissue/blood partition coefficient for a given anesthetic is
calculated by dividing a tissue/gas partition coefficient by the blood/gas
partition coefficient for that anesthetic" (p. 1023). Yasuda, Targ and Eger
computed their own tissue:blood table the same way, as § "v0.2.0: isoflurane
and desflurane" records. Both papers were read in full text from the private reference corpus.
Eger and Saidman's p. 1023 was read on 2026-10-25. The full citation of Eger
and Saidman is in § "The evidence behind the known limitations".

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
the other. `docs/MODEL.md` § "The tissue:gas coefficients are carried as
exact" says how far other laboratories' coefficients differ from these.
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Baker's other set of coefficients is not a check on the division.** The
unbracketed figures are "Data from Fiserova-Bergerova and Diaz (26)", a 1986
paper. They come with their own blood:gas values, 0.6 for sevoflurane and 1.4
for isoflurane, and they differ from the derived rows by far more than
rounding. § "The evidence behind the known limitations" gives the differences.

The citations of Baker and Farmery 2011, Eger and Shafer 2005 and
Fiserova-Bergerova and Diaz 1986 were checked in PubMed on 2026-10-25 (PMIDs
23737195, 16115976 and 3721592). Only Baker and Farmery was read in full text,
and its full citation is in `docs/references/README.md`.

**For developers.** The tissue:blood coefficients are computed by properties of
the class for an agent's parameters (`AgentParameters`, in `core/parameters.py`). One test in
`tests/unit/test_parameters.py`, `test_derives_tissue_blood_coefficients`,
checks the division of tissue:gas by blood:gas, for sevoflurane.

#### The reference patient's parameters

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
is the largest of the five, and `docs/MODEL.md` § "The fat group's blood flow"
records it as well, because it changes the shape of a displayed curve and not only a number in a
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
`docs/MODEL.md` § "Blood flow to the tissue groups" gives, so the published set could not be stored as printed,
even if it were preferred. The difference changes the vessel-rich time constant
by 0.26%, below the resolution of anything a user reads off the curve. The
De Wolf entry in the reference patient's data file (`reference_adult.json`)
records the difference in full.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->

There is no "arterial blood-pool volume" row, because arterial blood has no
volume of its own in this model (see `docs/MODEL.md` § "What the model represents").

**For developers.** The reference patient's data file is
`src/anesthesia_sim/data/patients/reference_adult.json`. The patient weight
(`ReferenceAdultParameters.weight_kg`) is loaded and checked to be positive and
finite, and nothing else reads it.

Two checks each reject a set of flow fractions whose sum differs from 1.0 by
more than the tolerance in `docs/MODEL.md` § "Blood flow to the tissue groups"
(`FLOW_FRACTION_TOLERANCE`). One runs on the reference patient's data file
(`_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one`), and the other
runs when the patient's compartments are built (`PatientCompartments.__post_init__`).
The tolerance stays as it is, because one loose enough to admit De Wolf's 99.8%
would also admit a transcription error silently.
`test_the_perfusion_allowance_admits_rounding_and_refuses_a_transcription_error`
in `tests/unit/test_rounding.py` checks that the stored fractions pass and that
De Wolf's printed ones fail.

#### Where Gas Man's reference-patient values come from

**Nothing on the longest provenance chain behind the reference patient was
measured by anybody this document can name.** The chain runs Gas Man (tier 3)
→ Lowe and Ernst (tier 2) → ICRP Committee II (tier 2), a committee of the
International Commission on Radiological Protection.

**The Workbook attributes the values to Lowe and Ernst 1981.** The note
beneath the Gas Man Workbook's Model Parameters table (Appendix B, page 168)
reads: "Values for volume, flow and relative flow are taken from Lowe and
Ernst, 1981". The book is
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
Table 7, on the facing page 150, carries a count in parentheses. Under
§ "Source hierarchy: what may be cited as the authority for a value", a
consensus document that collects primary measurements without making one is
**tier 2**.

**The book's model patient weighs 100 kg, which is why the material arrives in
this project as fractions.** Page 56 picks that weight so that "the organ
weights can also be read as per cent of total body weight". So Lerou and
Booij's Table 6 of fractions is the book's own table divided by 100, not a
normalization they performed. Nothing in the book states a 70 kg parameter set.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

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
compartment is ordinary modelling. `docs/MODEL.md` § "The reference adult" already treats
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

`docs/MODEL.md` § "Blood flow to the tissue groups" quotes the assumption in
Mapleson's Appendix 1 on which this model's whole representation of perfusion
rests.

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

#### The cardiac-output relation in Lowe and Ernst

**The book's cardiac-output relation gives 4.84 L/min at 70 kg, against the
5.0 L/min stored here.** Page 59, read at the source, gives the cardiac output
for its worked prime dose as $`2M^{3/4}`$ dl/min, "or 63.25 dl" for the 100 kg
patient. That is 0.2 times body mass to the three-quarter power in L/min. The
stored 5.0 would need 73.1 kg. The worked value of 63.25 dl determines the
exponent on its own, without reading a superscript off a scan. The stored
cardiac output stays a fixed 5.0, and § "The evidence behind the known
limitations" gives the reasoning.
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
treated as a measured human cardiac output.** This matters in `docs/MODEL.md`
§ "The reference adult", the only place in that document that sets the figure
beside Cattermole et al.'s measured median.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

#### The venous pool

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

#### The circuit volume and the default fresh gas flow

**The circuit volume and the default fresh gas flow adopt no source of any
tier.** The reference patient adopts no primary source but does adopt tier-3
ones, so these two machine rows have the wider gap. Both describe the
apparatus in front of the patient, so they are stored in a third kind of
parameter file, `data/machines/reference_circle_system.json`.

**Circuit volume, 6.0 L.** The Workbook's own table on page 168 gives 8.0 L.
De Wolf et al. 2012 give the same 8 L in their Methods, for the simulations that
used the coefficients in their Table 1. The 6.0 L value came in with the first
circuit model on 2026-08-22, and no record gives a reason for choosing it. It
was kept rather than changed to 8.0 L, because the exact value is not critical
(project owner, 2026-09-01, `PL-4YY1`). The smaller volume changes how much of
the early rise in inspired concentration comes from the machine itself. At the
same flow, $`\tau_C = V_C/\dot V_F`$ is 90 s here and 120 s at 8.0 L, so the
apparatus lag is 25% shorter. That lag is the part of the inspired curve that a
user is most likely to attribute to uptake. So a run that reproduces a
published Gas Man trajectory has to set the circuit volume to 8.0 L explicitly,
and cannot assume that value. Like every circuit volume in this model, the
6.0 L is one total for the apparatus and the patient circuit together
(`docs/MODEL.md` § "Breathing circuit"). No source says how it divides between
the two.
<!-- derived: 90 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Default fresh gas flow, 4.0 L/min.** No published counterpart for this value
exists in any source this project has reached. The Workbook's parameter table
gives the circuit row a volume and no flow, and describes its interface
defaults without numbers. The two Gas Man simulation studies read here chose
flows for their own purposes (De Wolf et al. used 1 L/min, and Weber et al.
used 10 L/min for washout). The value is a **teaching default, not a clinical
recommendation** (project owner, 2026-09-20, ratified, over lowering it to
match contemporary low-flow practice). It is well inside the supported range of
flows. It puts the circuit time constant at 90 s: long enough for the machine
lag to show as a distinct phase of the early rise, and short enough to resolve
within the first minutes of a teaching run. The data file labels this a design
rationale, not a measurement. **The default is also the flow a run starts at
when a machine profile states none**, because no source the survey reached
gives a startup flow for any machine. The survey read no manufacturer's manual,
so a profile for a real machine should look for its startup flow there. The
authority for that fallback is this rationale, not a source.
The rationale applies to the stored 6.0 L circuit. A smaller circuit gives a
shorter lag at the same flow, as § "What real workstations hold" below
computes.
<!-- derived: 90 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 10 L/min -->

**The project holds one measured circle-system volume, and it bounds the
circuit-volume row rather than replacing it.** Targ, Yasuda and Eger measured a
conventional circle system by water filling at **9860 ml** (*Anesth Analg*
1989 Aug;69(2):218–25, PMID 2764290). The same study lies behind the
inert-circuit entry under `docs/MODEL.md` § "Absorption by the circuit". It was read in full text on
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
user would meet in the same department. The stored 6.0 L lies within 2% of
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
flow published by any machine in current clinical use, and no source it
reached gives one (`docs/machine-survey.md` § "(a2)"). It read no
manufacturer's manual. So the flow row still adopts no source. Kalmar et al. conclude
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

**For developers.** The anesthesia machine's data file is
`src/anesthesia_sim/data/machines/reference_circle_system.json`. The fallback
starting flow comes from a constant in `core/circuit.py`
(`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`). One test checks that fallback
(`test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`),
and another fails if the constant and the shipped machine file's value ever
differ (`test_the_flow_default_matches_the_shipped_machine_file`).

A design document records the decision not to fold gas-path layout into an
effective volume (`docs/machine-abstraction.md`), and the roadmap says when
that decision is revisited (`ROADMAP.md` planned-milestone item 39).

### v0.2.0: isoflurane and desflurane

Sevoflurane, isoflurane and desflurane share one set of equations, compartments and reference
adult patient (`docs/MODEL.md` § "Equations"). An agent enters those equations only through its four
partition coefficients: one blood:gas and three tissue:gas. Its other stored values, such as its
MAC and its vaporizer's maximum, set a control or convert a displayed amount, and the equations do
not use them (§ "Delivery-limit and MAC parameters", § "Agent amount"). All twelve coefficients
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

The argument from a shared source covers the partition coefficients only. The stored MAC values
come from a different source, Mapleson's 1996 meta-analysis, which gives all three agents' MACs at
one age. § "The stored MAC" says what that costs.

#### Where the tissue:gas coefficients come from

**Gas Man's Workbook says the nine tissue:gas coefficients come from Yasuda, Targ and Eger, and
the paper confirms it.** The note under the Workbook's page-168 parameter table reads "Values for
isoflurane, halothane, desflurane and sevoflurane are taken from Yasuda, Targ and Eger". That
note alone could not raise the coefficients' source grade, because a program's statement about its
own sources is not independent evidence (§ "Republication does not promote a value between tiers").
The Workbook's reference 45 is also the 1988 ASA annual-meeting abstract
`Anesthesiology 69:A615`, not Yasuda, Targ and Eger's 1989 *Anesthesia &
Analgesia* paper.

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
attribution. The same Workbook paragraph credits sevoflurane's values to Yasuda and, one sentence
later, to "the package insert and Abbott data". The comparison settles that contradiction: the
three stored sevoflurane values match this paper, not a package insert. A test recomputes the
figures in this paragraph from the table's rows
(`test_the_stored_tissue_coefficients_lie_as_close_to_yasudas_means_as_printed`).

**The vessel-rich coefficient is Yasuda's *brain* value.** Table 1 gives brain,
heart, liver and kidney separately (sevoflurane 1.15, 1.21, 1.25, 0.78;
*Anesth Analg* 1989;69(3):370-3).
Sevoflurane's stored 1.1 is 4.3% below its brain value and 0.2% above the
equal-weight mean of its four organ values, 1.0975, so sevoflurane alone does
not show whether Gas Man used the brain value or the mean. Isoflurane's stored
2.1 is 0.5% above its brain value, 2.09, and desflurane's stored 0.54 equals
its brain value (the table above). These two matches indicate that the
vessel-rich compartment uses the brain values, and a user reading its trace
is reading a brain trace. A test recomputes the percents and the mean in this
paragraph (`test_the_vessel_rich_coefficients_match_yasudas_brain_values_as_printed`).
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54 -->

**Yasuda's paper is not a source for the stored blood:gas values.** It measured
none. Its Table 2 tissue:blood figures are calculated "by dividing the
tissue/gas partition coefficient by the published values for the blood/gas
coefficients adjusted for age" (*Anesth Analg* 1989;69(3):370-3). So dividing
Table 1 by Table 2 should recover the age-adjusted blood:gas values that the
paper used, for patients whose mean age was 65.8 years. The
abstract gives Table 2's brain column: 1.70 for sevoflurane, 1.57 for isoflurane
and 1.29 for desflurane (PMID 2774233). Dividing the brain values above by them,
it recovers 0.676, 1.331 and 0.419. These are 4.1% and 2.4% above the stored
sevoflurane and isoflurane values and 0.3% below the stored desflurane value
(`test_yasudas_brain_column_recovers_the_blood_gas_coefficients_printed`).

Both full tables are on page 371 of the paper. Each prints its means to two or
three significant figures, so rounding alone can move a recovered value by up
to 1.8%. The heart, liver and kidney columns recover values close to the
brain's. Across those four organs, the value recovered is 4% to 5% above the
stored sevoflurane value, 2% to 4% above the stored isoflurane value, and
within 1% of the stored desflurane value. The muscle and fat columns recover
more, by more than rounding explains: 17% and 10% above the stored value for
sevoflurane, 16% and 10% for isoflurane, and 11% and 5% for desflurane. So the
tables do not give one blood:gas value for each agent, and the paper does not
say why its muscle and fat columns differ from the other four
(`test_yasudas_full_tables_recover_the_blood_gas_ranges_printed`).
<!-- not-restated: 1.8 % -->
<!-- not-restated: 5 % -->

#### Why the stored values were kept

**For the nine tissue:gas coefficients, the source grade changed and the stored values did not**
(project owner, 2026-09-13, `PL-FN5F`).

*Adopted.* The nine tissue:gas coefficients trace back to a primary human measurement. So for all
three agents, the recorded source of these coefficients is now Yasuda, Targ and Eger, at tier 1,
the grade for a primary measurement. De Wolf et al. stays the source for the three blood:gas
values, which this study did not measure.

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
source. `test_storing_yasudas_means_would_move_the_time_constants_as_printed`
recomputes the time-constant changes in the *Declined* paragraph above. The
reference adult patient's physiologic parameters are in
`data/patients/reference_adult.json`. Storing Yasuda's figures would require
recomputing every pinned reference state under `tests/reference/`, because
those states are this parameter set's solution. `tests/unit/test_parameters.py` checks each
stored coefficient against a literal. `tests/reference/test_multi_agent.py`
checks mass balance and equilibrium for isoflurane and desflurane, and that
desflurane's alveolar-to-circuit ratio is above isoflurane's after one minute. Before changing any of desflurane's
coefficients, read `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed".

### Delivery-limit and MAC parameters

This section specifies three of an agent's stored values that play no part in the model's
equations: its maximum delivered concentration, its MAC and its MAC-awake. A value that a clinician
could read or act on is safety-critical whether or not the model uses it. § "Agent amount" gives the
sources of the agent's molar mass and liquid density. `docs/INTERFACE.md` § "MAC-awake as a chart
reference" specifies how the chart draws the MAC-awake band.

#### The maximum delivered concentration

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

**For developers.** In the simulation code, the breathing circuit (`BreathingCircuit`) carries
the maximum delivered concentration for the agent in use. The circuit itself **must reject** any
delivered concentration above that maximum, at construction and at every later change, and must
not lower it to the maximum instead. `test_rejects_construction_above_the_vaporizer_maximum` and
`test_rejects_delivered_concentration_above_the_vaporizer_maximum` in `tests/unit/test_circuit.py`
check both refusals, and `test_accepts_a_delivered_concentration_of_zero` checks that zero is
accepted. The function that sets up the uptake simulation for an agent
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
`test_rejects_mac_percent_exceeding_max_delivered_concentration_percent` in
`tests/unit/test_parameters.py` checks it.

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

#### The stored MAC

The stored MAC (`mac_at_age_40_percent`) is each agent's MAC at age 40 from
Mapleson's 1996 meta-analysis (*Br J Anaesth* 1996;76(2):179-85): sevoflurane
1.80%, isoflurane 1.17% and desflurane 6.6%. The reference adult has no age, so
every run uses the MAC at age 40, and the display states that age beside the MAC. The stored MAC has two uses, and both are
presentation. First, it sets the dial's starting position, so that each new run
begins at a recognizable clinical anchor. Second, it is the divisor for the display
in MAC multiples: every displayed compartment value and the chart's second axis are
divided by it. The simulator refuses any agent whose own vaporizer cannot deliver
its 1 MAC, because every run starts the dial at 1 MAC.
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- provenance: data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->

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
3. With Mapleson's confidence limits of ±7-10% (PMID 8777094), no MAC source makes a
   comparison between agents exact. The display shows the MAC it divides by, with its age,
   instead of presenting the estimate as settled.

No planned milestone moves the MAC to a primary measurement. `ROADMAP.md`'s planned-milestone
item 30 makes the MAC follow the patient's age once age is an input, and item 31 plans a
primary-literature set of partition coefficients beside the stored one.

**For developers.** Because the stored MAC divides every displayed compartment value, a change to
it falls under the safety-critical standard in `CLAUDE.md`. The list of sources in each agent's file (`sources`)
records Mapleson 1996 as the adopted source, with its tier, and records De Wolf et al.'s value that
the file stored before and how far it differed.
`test_the_stored_mac_is_mapleson_1996_s_mac_at_age_40` in `tests/unit/test_parameters.py` checks
each stored MAC against the figure in Mapleson's abstract.


#### The MAC-awake fractions

Each agent stores its MAC-awake as a fraction of its MAC
(`mac_awake.fraction_of_mac`), with a standard deviation in the same unit
(`mac_awake.standard_deviation_fraction_of_mac`). The chart draws them as the
MAC-awake band, which `docs/INTERFACE.md` § "MAC-awake as a chart reference"
specifies. The sources are Katoh et al. 1993 for sevoflurane and isoflurane,
and Chortkoff et al. 1995 for desflurane (§ "Where this project stands"). This
subsection records how those sources were read, and why the stored values are
the ones the band needs.

**The trace that the band is read against decides which published MAC-awake
value is correct.** Katoh et al. determined sevoflurane and isoflurane MAC-awake
by a slow, equilibrated washout and by a fast one, and the two methods disagree.
Slow washout gave 0.34 of MAC for sevoflurane and 0.31 for isoflurane, against
0.22 for both by fast washout. Katoh attributes the disagreement to
end-tidal-to-arterial and arterial-to-cerebral anesthetic differences. This
model represents those differences as the gap between the alveolar and
vessel-rich traces. The stored values are the slow-washout ones, and they belong
against the vessel-rich trace.
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->

Katoh also estimated the brain concentration at awakening. That estimate is not
a measurement, because cerebral concentration cannot be sampled in these
patients. The abstract says the brain concentrations were "calculated with
end-tidal anesthetic concentrations", and the title calls them "predicted".
So they come from Katoh's own model of brain uptake (`PL-YDRT`), which treats
the brain as one well-mixed compartment perfused by arterial blood. Katoh's
equation 1 (p. 1013) is:

$$
\frac{dP_{Brain}}{dt} = \frac{CBF \cdot \lambda_{B/G} \cdot (P_{Art} - P_{Brain})}{V_{Brain} \cdot \lambda_{T/G}}
$$

This is the perfusion-limited form that `docs/MODEL.md` § "Tissue groups" uses for
each tissue group. Katoh's compartment is the brain alone, though, while this
model's vessel-rich group pools the brain with the heart, liver, kidney and
viscera.

Katoh computed every patient's flow and volume from the same formulas
(*Anesth Analg* 1993;77(5):1012-7). Cerebral
blood flow $`CBF`$ is 14.3% of a cardiac output set by a cardiac index of
3.5 L/min/m², so it scales with body surface area. Brain volume $`V_{Brain}`$
is 21 mL/kg, so it scales with body weight. The brain's time constant therefore
varied a little from patient to patient. The coefficients were the same for
everyone. The blood:gas coefficient $`\lambda_{B/G}`$ is 0.63 for sevoflurane
and 1.36 for isoflurane, and the brain:gas coefficient $`\lambda_{T/G}`$ is
1.15 and 2.09.

During fast washout, Katoh's calculated brain concentration at first eye opening
does not differ significantly from the slow-washout values, under either of two
estimates of the arterial partial pressure. Katoh did not measure that pressure.
Equation 2 sets it equal to the end-tidal value. Equation 3 (p. 1016) corrects
the end-tidal value for 20% dead-space gas, as
$`P_{Art} = (P_{ET} - 0.2\,P_I)/0.8`$. During fast washout, the calculated
brain concentration at first eye opening was 0.30 of MAC for sevoflurane and
0.26 for isoflurane under equation 2 (Table 1, p. 1014; PMID 8214700).
Under equation 3 it was 0.34 and 0.30 (Table 3, p. 1016). The abstract quotes
the equation 3 figures and calls them
"nearly equal to MAC-Awake obtained by slow alveolar washout". So the stored
values and the choice of the vessel-rich trace rest on a modelled estimate that
agrees with an equilibrated measurement. That is weaker evidence than a direct
measurement of the brain would be.

<!-- not-restated: 0.34 -->

**The MAC-awake fractions for isoflurane, sevoflurane and desflurane were not
determined by one method.** Katoh's slow-washout arm is *descending*. Chortkoff
and Song et al. both determined desflurane MAC-awake by *ascending* stepwise
equilibration. All of these are equilibrated determinations, not fast-washout
ones, so all three fractions belong against the vessel-rich trace. But ascending
and descending determinations are not interchangeable, and no descending-washout
MAC-awake for desflurane was found. The three fractions (0.31 isoflurane, 0.34
sevoflurane, 0.36 desflurane) sit in a narrow range. Each agent still carries
its own value rather than one fraction covering all three. Isoflurane and
sevoflurane were each measured in Katoh's slow-washout arm, and their fractions
differ. Desflurane's was determined by the other method, so a shared fraction
would mix ascending and descending determinations.
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->

<!-- provenance: data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36 -->

**MAC-awake is stored as a fraction of MAC, never as a percent of one
atmosphere.** Each source expresses MAC-awake as a ratio to MAC, and Katoh does so explicitly, "as a ratio to
age-adjusted MAC". A published *percent*, by contrast, is tied to whichever MAC
its own population was measured against. Desflurane shows the risk. Chortkoff's
MAC-awake of 2.60% is 36% of a MAC of about 7.25% (PMID 7574003), Rampil's
figure for ages 18-30 (PMID 2001020). The stored MAC is Mapleson's 6.6% at
age 40. Dividing 2.60% by 6.6% would give 0.394 instead of the published 0.36,
so the band would be drawn 9.4% too high and crossed too soon. Storing the fraction avoids that error. For
desflurane, storing the fraction allows an independent check. The band's centre
is 0.36 of the stored 6.6%, or 2.38%. Song et al. measured 2.17 ± 0.25% in the
non-jaundiced control arm, so the centre lies within one SD of that mean.
Rampil's MAC for ages 31-65, 6.0%, describes that arm's population, and 0.36 of
it is 2.16%, within 0.01 percentage points of Song's mean.

<!-- derived: 0.394 from data/agents/desflurane.json mac_at_age_40_percent = 6.6, mac_awake.fraction_of_mac = 0.36 -->
<!-- derived: 2.38 percent from data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36, mac_at_age_40_percent = 6.6 -->

**The comparison with Katoh's own MAC at age 40 shows the band slightly low**,
so it teaches a slightly late wake-up (`PL-P319`). Katoh's fractions are ratios to each patient's
age-adjusted MAC, which comes from two linear equations on p. 1013
(PMID 8214700). For isoflurane it is 1.43 − 0.0061 × age (yr) percent, and for sevoflurane
2.56 − 0.0156 × age (yr) percent. The paper cites four MAC studies for the
equations but does not say how the equations were derived from those studies.
At age 40 the equations give 1.94% for sevoflurane and 1.19% for isoflurane.
The stored MAC is 7.0% below Katoh's for sevoflurane and 1.3% below it for
isoflurane, so the band sits below Katoh's own age-40 awakening concentration
by the same proportions. The drawn centres are 0.612% sevoflurane and 0.363%
isoflurane, against 0.658% and 0.368% from Katoh's fractions times Katoh's
age-40 MAC. Both differences are much less than the standard deviation of
Katoh's fractions, 0.05 of MAC. Katoh's slow-washout patients themselves woke
at a mean end-tidal 0.63 ± 0.11% sevoflurane and 0.36 ± 0.08% isoflurane
(Table 1, p. 1014). Those figures are lower than the band mostly because the
patients were older, with mean ages of 45.9 and 45.1 years, so they are not a
like-for-like check of the band. The band is drawn on Mapleson's MAC at age 40,
the age the paragraph above uses for Katoh's equations.
<!-- not-restated: 0.36 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 7.0% from data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- derived: 1.3% from data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- derived: 0.612 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_at_age_40_percent = 1.8 -->
<!-- derived: 0.363 percent from data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31, mac_at_age_40_percent = 1.17 -->

**For developers.** Two tests in `tests/reference/test_parameter_source_figures.py`
recompute the arithmetic in the last two paragraphs.
`test_a_desflurane_percent_over_the_stored_mac_gives_the_figures_printed` recomputes
the desflurane figures from the stored MAC and MAC-awake fraction.
`test_katohs_mac_equations_at_age_40_give_the_figures_printed` recomputes Katoh's MAC
at age 40 and the band centres from the stored values.


## Agent amount

Every compartment stores its agent as an equivalent gas volume, in litres of
pure agent gas at one reference condition: **20 °C and 760 mmHg, dry**. At that
condition the ideal-gas molar volume is 24.055 L/mol
(`test_the_reference_molar_volume_is_codatas_at_0_celsius_scaled_to_20_celsius`).
The condition defines the unit only. It does not mean that any of the agent is physically at 20 °C and
760 mmHg. $`M_x`$ is the equivalent gas volume of the agent stored in
compartment $`x`$.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- derived: 24.055 L/mol from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The reference condition matters only when an amount is converted out of the
unit**, into moles, mass, or the millilitres of liquid that a vaporizer is filled
from. Every governing equation works with dimensionless fractions and physical
volumes, and every partition coefficient is a ratio. So the condition changes no
concentration curve, mass balance or displayed concentration, and no other
number under `docs/MODEL.md` § "Equations", which includes its conservation of
agent, or under `docs/INTERFACE.md` § "Minimum displayed outputs". The ideal-gas
molar volume is 25.450 L/mol at
37 °C, so declaring 37 °C instead would change each converted amount by a
factor of 1.058 (`test_the_agent_amount_section_prints_what_its_inputs_give`).
<!-- derived: 1.058 from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**Three reasons favour a 20 °C reference condition.**
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

1. **The published vapour-to-liquid constants are 20 °C constants.** The
   consumption literature quotes one number per agent, the vapour volume
   obtained from 1 mL of liquid. The table below gives Biro's. The same number
   can be derived from the liquid's measured density, its molar mass and the
   molar volume. At 20 °C the
   derivation reproduces all three within 0.7 %. At 37 °C it runs 5.1–6.2 %
   high (`test_the_agent_amount_section_prints_what_its_inputs_give`):

   | Agent | Liquid density at 20 °C, g/mL | Molar mass, g/mol | Derived mL vapour per mL liquid, 20 °C | Biro's constant | Derived, 37 °C |
   | --- | --- | --- | --- | --- | --- |
   | Sevoflurane | 1.5203 | 200.05 | 182.8 | 184 | 193.4 |
   | Isoflurane | 1.5019 | 184.49 | 195.8 | 195 | 207.2 |
   | Desflurane | 1.4651 | 168.04 | 209.7 | 210 | 221.9 |

   The densities are those of Laster, Fang and Eger (*Anesth Analg*
   1994;78(6):1152-3), measured in four 50-mL volumetric flasks at 20 °C, with a temperature coefficient of
   −0.00250 ± 0.00014 g/mL per °C over 0–25 °C. The molar masses are formula
   masses, which the ChEMBL chemistry database gives to two decimals.

   A model that declared 37 °C would either convert its 37 °C litres with 20 °C
   constants, or print consumption figures 5.5 % below the published ones.
   That 5.5 % is $`1 - 1/1.058`$, the same for every agent. For sevoflurane,
   1 L of vapour comes from 5.47 mL of liquid at 20 °C, and would come from
   5.17 mL at 37 °C.

2. **A consumption figure is converted from amounts of fresh gas, and fresh gas
   is at room temperature.** The delivered amount $`M_{\mathrm{delivered}}`$
   and the exhausted amount $`M_{\mathrm{exhausted}}`$ both accumulate from
   $`\dot V_F`$, the fresh gas flow at the common gas outlet. That flow is
   carrier gas plus the vapour that the vaporizer added. It is on the machine
   side of the patient, at operating-room temperature, not at 37 °C. A cost
   or waste figure is computed from those two amounts (`ROADMAP.md`
   "Planned milestones" item 28). Declaring 20 °C makes them exact. Declaring
   37 °C would leave them approximate, and would need a correction from room
   to body temperature on $`\dot V_F`$. That correction would change the
   governing equations, not just a label.

3. **Gas Man's own constants are 20 °C constants, and its litres carry no
   condition at all.** This model takes its partition coefficients, MACs and
   reference patient from Gas Man (`docs/PARAMETERS.md` § "Where this project stands"), so its amounts follow
   Gas Man's arithmetic. A different reference condition would make this
   model's litre and Gas Man's litre different quantities, although every
   parameter behind them is shared.

   Gas Man states a condition in one place only, the line
   `Volatility=209 Vapor/Liquid volume ratio (20'C)` in its settings file,
   `GASMAN.INI`. It states none for the litres of uptake and of delivered agent
   that it displays. This model likewise uses the condition only where vapour is
   converted to liquid. The 20 °C derivation reproduces all five of Gas Man's
   printed vapour-to-liquid constants within 0.35 %, and the 37 °C derivation
   runs 5.6–6.2 % high:

   | Agent | Gas Man | Derived, 20 °C | Derived, 37 °C |
   | --- | --- | --- | --- |
   | Halothane | 228 | 227.7 (−0.15 %) | 240.9 (+5.6 %) |
   | Enflurane | 198 | 198.6 (+0.29 %) | 210.1 (+6.1 %) |
   | Isoflurane | 196 | 195.8 (−0.09 %) | 207.2 (+5.7 %) |
   | Sevoflurane | 183 | 182.8 (−0.10 %) | 193.4 (+5.7 %) |
   | Desflurane | 209 | 209.7 (+0.35 %) | 221.9 (+6.2 %) |

   The table adds halothane and enflurane to the three agents this model
   carries, because Laster, Fang and Eger measured their densities in the same
   experiment.

<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.g_ml = 1.5019 -->
<!-- provenance: data/agents/desflurane.json liquid_density.g_ml = 1.4651 -->
<!-- provenance: data/agents/sevoflurane.json molar_mass_g_mol = 200.05 -->
<!-- provenance: data/agents/isoflurane.json molar_mass_g_mol = 184.49 -->
<!-- provenance: data/agents/desflurane.json molar_mass_g_mol = 168.04 -->
<!-- derived: 5.5 % from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- derived: 5.47 mL from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- provenance: data/agents/sevoflurane.json liquid_density.measured_at_celsius = 20 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.measured_at_celsius = 20 -->
<!-- provenance: data/agents/desflurane.json liquid_density.measured_at_celsius = 20 -->
<!-- derived: 182.8 from data/agents/sevoflurane.json liquid_density.g_ml = 1.5203, molar_mass_g_mol = 200.05 -->
<!-- derived: 195.8 from data/agents/isoflurane.json liquid_density.g_ml = 1.5019, molar_mass_g_mol = 184.49 -->
<!-- derived: 209.7 from data/agents/desflurane.json liquid_density.g_ml = 1.4651, molar_mass_g_mol = 168.04 -->

**For developers.** The code must use the one reference condition everywhere,
and must never add gas fractions, dissolved blood concentrations and tissue
concentrations directly. It works in litres. Two tests compute the figures in
this section. `test_the_reference_molar_volume_is_codatas_at_0_celsius_scaled_to_20_celsius`
checks the 24.055 L/mol against CODATA's molar volume at 0 °C.
`test_the_agent_amount_section_prints_what_its_inputs_give` recomputes the
25.450 L/mol and the factor of 1.058, both tables, the ranges stated beside
them, the 5.5 % and the sevoflurane example.

The sources for this section are listed below, with the route by which each
was read.

- Laster MJ, Fang Z, Eger EI II. *Specific gravities of desflurane, enflurane,
  halothane, isoflurane, and sevoflurane.* Anesth Analg 1994;78(6):1152-3.
  PMID 8198275, doi:10.1213/00000539-199406000-00022. Retrieved from PubMed
  and verified against the abstract on 2026-09-17, and again on 2026-10-26,
  when its densities were stored.
- ChEMBL database, release 34, compounds CHEMBL1200694 (sevoflurane),
  CHEMBL1256 (isoflurane) and CHEMBL1200733 (desflurane), for the molecular
  formulas and the molar masses. Read through a ChEMBL connector (an MCP
  server) on 2026-10-26. The database is tier 2 under `docs/PARAMETERS.md` § "Source hierarchy",
  because a molar mass is computed from the formula and the standard atomic
  weights, not measured on the agent.
- Mohr PJ, Newell DB, Taylor BN, Tiesinga E. *CODATA recommended values of the
  fundamental physical constants: 2022.* Rev Mod Phys 2025;97(2):025002.
  doi:10.1103/RevModPhys.97.025002. Table XXXII gives the gas constant as the
  product of the exact Avogadro and Boltzmann constants. Table XXXIII gives
  the standard atmosphere, 101 325 Pa exactly, and the molar volume of an
  ideal gas at 0 °C, which the tests use to check the 24.055 L/mol above.
  Read in full from arXiv:2409.03787v1 on 2026-10-26.
- Biro P. *Calculation of volatile anaesthetics consumption from agent
  concentration and fresh gas flow.* Acta Anaesthesiol Scand
  2014;58(8):968-72. PMID 25060161, doi:10.1111/aas.12374. Retrieved from
  PubMed and verified against the abstract on 2026-09-17. The abstract gives
  the four constants but does not state their temperature, so the
  reproduction above is what shows they are 20 °C constants.
  <!-- not-restated: 20 °C -->
- Philip JH. *Workbook for Gas Man*. Appendix C's `GASMAN.INI` listing is the
  source for the `Volatility` setting. Chapter 10's closed-circuit
  liquid-injection section (printed pp. 103-105) is the source for the five
  vapour-to-liquid constants. There the constants convert an *input*, the volume
  of liquid injected, rather than a displayed amount. Both were read from the
  project owner's private reference library on 2026-09-16. The reading notes are
  in `docs/references/README.md` § "Philip — *Workbook for Gas Man*". The
  workbook is tier 3 under `docs/PARAMETERS.md` § "Source hierarchy": it defines what Gas Man does,
  and it measures nothing.

## The evidence behind the known limitations

`docs/MODEL.md` § "Known limitations" states each limitation for a clinician.
This section keeps the evidence, the sources and the tests behind those
statements that the clinician's text leaves out, in the order of the
limitations.

### Desflurane's washout through the circle system

**For developers.** Four tests in
`tests/reference/test_published_wash_in_and_elimination.py` pin the figures of
`docs/MODEL.md` § "Elimination at five minutes: does not agree".
`test_desflurane_washout_at_the_default_fresh_gas_flow_regression_pin` pins
desflurane's washout at the default fresh gas flow, reading that flow from the
circuit's parameter file.
`test_desflurane_washout_at_a_high_flow_and_raised_ventilation_regression_pin`
pins it at 10 L/min of fresh gas and 8 L/min of alveolar ventilation.
`test_five_minute_elimination_ratio_regression_pin` pins the five-minute ratio
at 10 L/min, and
`test_five_minute_elimination_ratio_without_rebreathing_regression_pin` pins
it with the circuit removed.

<!-- not-restated: 10 L/min -->

### Cardiac output and flow distribution are fixed

**The anesthetic's effect on cardiac output and the perfusion fractions is
not modeled, because the human volunteer data do not describe a relationship
this model could represent.** Three studies measured healthy
volunteers who were anesthetized without surgery, each against their own awake
baseline:

- Weiskopf RB, Cahalan MK, Eger EI 2nd, Yasuda N, Rampil IJ, Ionescu P,
  Lockhart SH, Johnson BH, Freire B, Kelley S. *Cardiovascular actions of
  desflurane in normocarbic volunteers.* Anesth Analg 1991;73(2):143-56.
  PMID 1854029. Desflurane alone at 0.83, 1.24 and 1.66 MAC, in 12 men.
  **Cardiac index did not change**, although stroke volume index fell and
  filling pressure rose at every concentration. This is myocardial depression
  with cardiac output maintained.
- Cahalan MK, Weiskopf RB, Eger EI 2nd, Yasuda N, Ionescu P, Rampil IJ,
  Lockhart SH, Freire B, Peterson NA. *Hemodynamic effects of
  desflurane/nitrous oxide anesthesia in volunteers.* Anesth Analg
  1991;73(2):157-64. PMID 1854030, doi:10.1213/00000539-199108000-00008. The
  **same** volunteers, in the same crossover, with 60% nitrous oxide carrying
  0.5 MAC of the total. Cardiac index now fell dose-dependently.
- Malan TP Jr, DiNardo JA, Isner RJ, Frink EJ Jr, Goldberg M, Fenster PE,
  Brown EA, Depa R, Hammond LC, Mata H. *Cardiovascular effects of sevoflurane
  compared with those of isoflurane in volunteers.* Anesthesiology
  1995;83(5):918-28. PMID 7486177, doi:10.1097/00000542-199511000-00004.
  With sevoflurane, cardiac index fell at 1.0 and 1.5 MAC and **returned to
  baseline at 2.0 MAC** as systemic vascular resistance fell. Isoflurane
  behaved similarly. With both agents the depression diminished with
  prolonged administration, and with spontaneous rather than controlled
  ventilation.

Together these studies show that the *sign* of the cardiac-output change
depends on the carrier gas, that the dose-response **changes direction**, and
that the effect changes with time at a fixed dose and with the mode of
ventilation. This model has no second gas, no ventilation mode, no surgical
stimulus and no pharmacodynamic layer, so it could represent none of those
dependencies. It could represent only a $`Q(\text{dose})`$ that moves one way
with dose and does not change with time, which the studies above do not show.
Teaching one would be worse than holding the flow fixed and saying so. The
case for modeling regional flow is weaker still. The measurements this project
could find of how anesthesia redistributes flow between the vessel-rich,
muscle and fat groups are largely from animals. § "The fat group's blood
flow" below gives what the human record supports, even at rest.

`ROADMAP.md`'s planned-milestone item 35 carries an automatic coupling from the
agent to the flow as a possible future option that a user would turn on, with a run's default behaviour
unchanged. The evidence above favours an option, because an option can state
its own uncertainty where a model's default behaviour cannot.

### The fat group's blood flow

These are the figures behind the fat flows that `docs/MODEL.md` § "The fat
group's blood flow" gives from the two Yasuda 1991 papers.

The stored fraction implies 2.07 mL per 100 mL per minute: 0.06 of the
5.0 L/min default cardiac output, flowing into 14.5 L. Flow per unit of tissue
is the partition coefficient over the time constant, so the comparison needs
no fitted volume. This model's stored fat solubilities (fat:gas over
blood:gas) are 52 for sevoflurane, 54 for isoflurane and 31 for desflurane. At
those values, the fitted fat-group time constants of 2,120, 2,130, 1,340 and
2,090 minutes (Table 4 of each paper) give 2.5, 2.5, 2.3 and 2.6. Read as
evidence about the fat group's flow, the PET measurement puts the stored
figure at about twice the truth, and the washout fits put it at or a little
below the truth. `test_the_fitted_fat_time_constants_imply_the_flows_printed`
repeats this arithmetic.
<!-- derived: 2.07 from data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5.0, tissue_groups.fat.volume_l = 14.5 -->
<!-- derived: 52 for sevoflurane from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 54 for isoflurane from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 31 for desflurane from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->

### Intertissue diffusion: the missing fourth compartment

**Two cautions keep the missing intertissue route a limitation rather than a missing parameter.** The
first is that the route and its size rest on different evidence. The route has
been measured outside Eger's group. In two dogs after 80 minutes of halothane,
perirenal fat sampled against the kidney held 20 and 35 times the
concentration of fat sampled far from it. Its tension was "comparable to the
arterial tension instead of to the very low tension to be expected if the fat
had received halothane only from its own blood supply" (Allott et al.,
*Br J Anaesth* 1976;48:289). Eger and Saidman cite that as the direct demonstration (their ref 8),
though they call their own group's washout fits "the most convincing
evidence" (p. 1025). The size has not been measured that way. Their
"approximately 30% of the anesthetic taken up" and their time constants of 200
to 400 minutes (p. 1025) cite Carpenter et al. and the two Yasuda papers.
Eger is an author of every one of those papers, so the figures restate the
fits rather than confirm them. Allott et al.'s own case for lean tissue losing
agent to fat "depends almost entirely on the improved fit to femoral venous
tensions" (p. 290). And a fit establishes a time constant, not which tissue
holds it. The Yasuda authors write that intertissue diffusion is what "we
believe provides the explanation for the fourth compartment" (*Anesth Analg*
p. 323). Hendrickx and De Wolf quote Hull as saying that assigning a tissue to
a fitted compartment is "ill-founded because parameters of the fit to the
uptake data contain no information that might support such assumptions". They
add that compartment parameters relate to cardiac output and demographics in
no straightforward way, and conclude that correlating them with tissue volumes
and blood flows "should be done with care, if at all" (*Modern Anesthetics*,
pp. 165–66).

The second caution is that § "The fat group's blood flow" above leaves the direction
of the fat group's own error unsettled. On its PET reading, the fat group
already holds too much agent, which acts against this omission. On its washout
reading, the fat group holds about what the fitted fat group would. Nothing
here measures whether the two cancel, and neither may be read as correcting
the other.

**Nothing in `ROADMAP.md` plans a fourth tissue compartment, and the one paper
here that approximated the route warns against the shortcut.** Allott et al.
fitted their dogs' data by giving fat more of the cardiac output, or by giving
lean tissue a higher solubility (Table I, p. 281). They warn that such mimicry
is "bound to fail to varying degrees in other circumstances". In recovery,
"metabolism will still remove halothane from the circulation … whereas extra
fat perfusion will eventually return halothane to the circulation". And with a
low fat/lean partition coefficient "the tension gradients for diffusion will be
less". Each circumstance might be matched by a distortion of its own, but "the
only general solution is to build a more elaborate model which incorporates
direct representations of metabolism (which would be straightforward) and
intercompartment diffusion (which would be more complex)" (p. 290).

The time constants in the last column of the table in `docs/MODEL.md` § "Intertissue diffusion: the missing fourth compartment", the ratios and the crossing
times were computed on 2026-09-26 from the published means in that table and this
model's parameters as stored then. None of the sources below is the authority
for a stored value:

- Yasuda et al., *Anesth Analg* 1991;72(3):316-24, on sevoflurane and
  isoflurane. **Full text**, from the private reference corpus: the
  compartment assumptions on p. 319, the interpretation on p. 320, Tables 1,
  2 and 4 on p. 321, Table 5 on p. 322, and the volume and muscle remarks on
  p. 323. Seven volunteers, with 30 minutes' administration and six to seven
  days' elimination.
- Yasuda et al., *Anesthesiology* 1991;74(3):489-98, on desflurane,
  isoflurane and halothane. **Full text**, a scan with no text layer, read as
  page images from the private reference corpus: the interpretation on
  p. 493, Table 1 on p. 494, Table 2 on p. 495, Tables 4 and 5 on p. 496.
  Eight volunteers, with 30 minutes' administration and five to seven days'
  elimination. The full citations of both Yasuda papers are in
  `docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics
  papers".
- Carpenter RL, Eger EI 2nd, Johnson BH, Unadkat JD, Sheiner LB.
  *Pharmacokinetics of inhaled anesthetics in humans: measurements during and
  after the simultaneous administration of enflurane, halothane, isoflurane,
  methoxyflurane, and nitrous oxide.* Anesth Analg 1986;65(6):575-82. PMID
  3706798; PubMed records no DOI. **Abstract read**, through PubMed: nine
  patients, 2 hours' administration. The abstract does not name intertissue
  diffusion. The Yasuda papers credit that reading to this paper, whose full
  text has not been read.
- Eger EI 2nd, Saidman LJ. *Illustrations of inhaled anesthetic uptake,
  including intertissue diffusion to and from fat.* Anesth Analg
  2005;100(4):1020-33. PMID 15781517, doi:10.1213/01.ANE.0000146961.70058.A1.
  **Full text**, from the private reference corpus: the brain drawn apart on
  p. 1022, Table 3 on p. 1024, the lean-tissue losses, the evidence and the
  30% share on p. 1025, and recovery on p. 1032. PubMed classifies it as a
  review, so it is tier 2 under `docs/PARAMETERS.md` § "Source hierarchy". Its figures need more
  caution than most reviews' do, because the paper says they "illustrate
  concepts but are not necessarily precise (quantitative) reflections of the
  kinetics" (p. 1020).
- Allott PR, Steward A, Mapleson WW. *Pharmacokinetics of halothane in the
  dog: comparison of theory and measurement in individuals.* Br J Anaesth
  1976;48(4):279-95. PMID 1275995, doi:10.1093/bja/48.4.279. **Full text**,
  from the private reference corpus: the design on p. 279, Table I on p. 281,
  and the discussion on pp. 289-90. Seven dogs were given 1% halothane for
  80 minutes. The perirenal-fat samples are from two further dogs of another
  series (p. 289). The paper is Eger and Saidman's ref 8, and it has no author
  in common with their refs 3-7.
- Perl W, Rackow H, Salanitre E, Wolf GL, Epstein RM. *Intertissue diffusion
  effect for inert fat-soluble gases.* J Appl Physiol 1965;20(4):621-7. PMID
  5838712, doi:10.1152/jappl.1965.20.4.621. The Workbook lists it as reference
  32 and prints the year as 1964. It is also Eger and Saidman's ref 9, which
  they credit with suggesting the effect "40 yr ago" (p. 1025). Allott et al.
  credit a 1963 chapter of Perl's with first suggesting it "on theoretical
  grounds" (p. 289). PubMed returns "[Abstract not available]". Neither text
  has been read, so nothing is taken from either.
- Philip JH. *Workbook for Gas Man®*, Appendix B, pp. 169-70, and Hendrickx
  and De Wolf's chapter in *Modern Anesthetics* (2008), pp. 163 and 165-66.
  Both were read from the private reference corpus. The Workbook is tier 3
  and the chapter is tier 2. Their full citations are in
  `docs/references/README.md` § "Philip — *Workbook for Gas Man*" and
  `docs/references/README.md` § "Schüttler & Schwilden 2008 — *Modern
  Anesthetics*".

### The tissue:gas coefficients are carried as exact

A third published set of tissue coefficients agrees less well. Baker and Farmery's 2011 review
prints tissue:blood coefficients from Fiserova-Bergerova and Diaz 1986 beside
the set that matches this model (*Compr Physiol* 2011;1:572, Table 2). On the tissue:blood scale,
that set puts sevoflurane's fat coefficient at 71.7, 37% above this model's
52.3, and isoflurane's muscle coefficient at 1.71, 51% below this model's
3.46. Its vessel-rich figures are 28% above this model's for both agents. The
set's own blood:gas values, 0.6 for sevoflurane and 1.4 for isoflurane, move
these gaps in opposite directions for the two agents, so the tissue:gas scale
that this model stores gives the fairer comparison. On that scale the set's
sevoflurane fat coefficient is 27% above this model's and its isoflurane
muscle coefficient 47% below. Its vessel-rich coefficient is 18% above for
sevoflurane and 38% above for isoflurane. The set may not be a measurement.
According to its PubMed abstract, the 1986 paper measured coefficients only
for water-soluble solvents such as acetone and the alcohols. It then fitted
equations that predict any substance's tissue coefficients from its blood:gas
and fat:gas values. Baker does not say which of the anesthetic figures were
measured and which predicted. The set has no desflurane values.
<!-- not-restated: 18 % -->

Every stored tissue:gas coefficient lies within one standard deviation of its
cited measurement. A user should read the muscle and fat traces as one
well-measured parameter set, not the only set the literature supports.
Yasuda, Targ and Eger's p. 373, Eger and Saidman's Table 1, Baker and
Farmery's Table 2 and Hendrickx and De Wolf's p. 165 were read in full text.
Fiserova-Bergerova and Diaz 1986 was read as its PubMed abstract only (PMID
3721592), and the 1984 paper not at all. The full Yasuda, Targ and Eger
citation is in `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not
changed".

### One 70 kg adult
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

The cardiac output is kept at a fixed 5.0 L/min, rather than scaled with the
patient's weight, for a structural reason. A time constant is
$`V_i \lambda_{i:b} / Q_i`$, and this model stores compartment volumes as
fixed litres. So scaling only the flow would make every time constant
proportional to $`M^{-3/4}`$: a heavier patient would equilibrate *faster* and
a lighter one more slowly. That is an artifact of scaling one half of a
coupled pair. At the shipped sevoflurane coefficients, a 20 kg child under a
weight-scaled cardiac output alone would equilibrate about 2.6 times more
slowly than the reference adult, which is the opposite of the direction in
which paediatric inhalational uptake runs. (Salanitre and Rackow's
*Anesthesiology* 1969;30(4):388–94 study of pulmonary exchange in infants and
children is the classic reference for that direction. Its PubMed record was
retrieved, but its text has not been read, so no figure is taken from it.)
Half of the scaling is therefore worse than none of it. Adopting the relation
for the one patient that exists would have lengthened every time constant by
3.30% and changed nothing else.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

### Amounts held in the body, and dry alveoli

**For developers.** `test_the_reference_condition_gap_is_the_ratio_of_molar_volumes`
computes the molar volumes at 37 °C and 20 °C from the constants in
`core/liquid_agent.py`, and the 5.8 % and 5.5 % from their ratio.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- derived: 5.8 % from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- derived: 5.5 % from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**For developers.** `test_the_humidification_dilution_follows_from_the_water_vapour_pressure`
computes the 713 mmHg, the 6.2 % and the 6.6 % from 47 mmHg and one
atmosphere.
<!-- not-restated: 6.6 % -->

**The 47 mmHg is computed.** The saturation pressure of water at 37.0 °C is
47.12 mmHg on the IAPWS-95 formulation (Wagner W, Pruß A. *The IAPWS
Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance
for General and Scientific Use.* J Phys Chem Ref Data 2002;31(2):387–535,
doi:10.1063/1.1461829). The formulation's saturation equation reproduces both
the triple-point pressure and the normal boiling point to better than one
part in a million. The conventional 47 of the alveolar gas equation is that
value rounded, and the two agree to 0.3 %. This project stores no such value,
because no equation here reads it.

**Applying the factor would break the validation, as a measurement shows.**
The governing equations are linear in $`F_I`$, the property that "Published
wash-in and elimination validation test" also rests on. So applying the factor
to the inspired term multiplies every computed $`F_A/F_I`$ by exactly 713/760.
$`F_A/F_I`$ is the one quantity this model is validated against, and the
validation does not survive the factor. At the shipped defaults, the modeled
$`F_A/F_I`$ for each of the four published wash-in cohorts lies within one
standard deviation of the published mean. With the factor, all four fall
outside it:

| Cohort | Modeled $`F_A/F_I`$ | Now | With the factor | Then |
| --- | --- | --- | --- | --- |
| Sevoflurane, Anesth Analg 1991;72:316-24 | 0.8528 | +0.16 SD | 0.7999 | −2.78 SD |
| Isoflurane, Anesth Analg 1991;72:316-24 | 0.7414 | +0.31 SD | 0.6954 | −1.39 SD |
| Desflurane, Anesthesiology 1991;74:489-98 | 0.9079 | +0.79 SD | 0.8516 | −4.84 SD |
| Isoflurane, Anesthesiology 1991;74:489-98 | 0.7414 | +0.38 SD | 0.6954 | −1.15 SD |

<!-- not-restated: 0.31 -->

These figures were computed on 2026-09-19, at the parameters stored then,
against the published means and standard deviations. The table's factor is
712.88/760, from the computed 47.12 mmHg.

### Altitude

**No altitude correction factor is stored, and the $`1/P`$ form in `docs/MODEL.md` § "Altitude" must
not become one.** $`\%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$ is the
dilute-vapour limit of the flow-splitting physics. The fuller form is
$`F \approx k\,\mathrm{SVP}/(P - \mathrm{SVP})`$, where SVP is the saturated
vapour pressure, and it reduces to $`k\,\mathrm{SVP}/P`$ only where
$`\mathrm{SVP} \ll P`$. Isoflurane's saturated vapour pressure is about
240 mmHg at 20 °C, which is not small against 760. Carrying the denominator
through gives a delivered partial pressure that *overshoots* rather than holds
steady: on that arithmetic alone, about 16% high at 585 mmHg, where the
$`1/P`$ form predicts a flat line
(`test_the_variable_bypass_overshoot_at_altitude_follows_from_the_fuller_form`).
The Tec 6's response rests on its manufacturer's instruction and on Andrews and
Johnston's description of its mechanism, both quoted in `docs/MODEL.md` § "Altitude". How large the
variable-bypass response is, and whether its dial needs correcting, is less
settled. Dosch and Tharp call the effect of altitude on vaporizer performance
"controversial". They write that "Some sources state that variable bypass types
need not be adjusted for moderate changes in barometric pressure, but the Tec 6
must be dialed up beyond the desired dose at higher altitudes. Other sources
disagree." They also report that Dorsch and Dorsch's *Understanding Anesthesia
Equipment* (5th edition, 2008) says to consult the operator's manual for each
model. That textbook could not be read for this document, so its advice is
cited only as Dosch and Tharp report it. The size of the
variable-bypass compensation is approximate, so no number is stored for it. An implementation of ambient pressure should
derive the variable-bypass case from each agent's saturated vapour pressure
rather than from the $`1/P`$ shortcut, and would owe each agent's SVP a source
of its own. None is stored today.
<!-- not-restated: 20 °C -->

**Sources for the altitude notes above.** None of them is the authority for a stored
value. Two of the six are **owner-attested**: they were read from the project
owner's copies, and no other reader can check them. The six are these:

- Weiskopf RB, Sampson D, Moore MA. The desflurane (Tec 6) vaporizer: design,
  design considerations and performance evaluation. *Br J Anaesth*
  1994;72:474–479. Primary, and the authority for every figure attributed to
  it here: the 22.8 °C boiling point, the 39 °C sump, the 1460 mmHg that the
  sump fixes and why that pressure was chosen, and the ±15% relative (or
  ±0.5% absolute) output accuracy. Read in full text. It states the 1460 mmHg
  twice, once for the sump and once for the regulator that reduces it to the
  fresh-gas pressure. It says nothing about ambient pressure or altitude, so
  it is not the source for that behaviour.
- Andrews JJ, Johnston RV. The new Tec6 desflurane vaporizer. *Anesth Analg*
  1993;76:1338–1341. Primary. It is the source of the flow-ratio mechanism
  quoted in `docs/MODEL.md` § "Altitude", which appears in the abstract.
- James MF, White JF. Anesthetic considerations at moderate altitude. *Anesth
  Analg* 1984;63:1097–1105. Primary. It is the source of the case for
  reasoning in partial pressures rather than percentages at altitude, and of
  the MAPP proposal. It predates desflurane, so it covers the variable-bypass
  class only.
- Datex-Ohmeda. *Tec 6 Plus Vaporizer* specification sheet AN3307-A/1100,
  © 2000 Datex-Ohmeda Division, Instrumentarium Corp. A manufacturer
  statement, quoted in `docs/MODEL.md` § "Altitude". It also gives a 1–18% concentration range, whose upper
  end is the 18% that this model stores as desflurane's maximum delivered
  concentration. Read in full.
  **Owner-attested.**
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth
  Crit Care Pain* 2011;11:199–203. **Tier 2** under `docs/PARAMETERS.md` § "Source hierarchy". It
  is a secondary synthesis, taken here for the shape of the explanation and
  the worked example, and never as the authority for a number. Its "Altitude"
  section describes both classes side by side. Read in full.
  **Owner-attested.**
- Dosch MP, Tharp D. *The Anesthesia Gas Machine*, chapter 5, "Processing:
  Vaporizers". University of Detroit Mercy, revised February 2026.
  https://healthprofessions.udmercy.edu/academics/na/agm/05. **Tier 2** under
  `docs/PARAMETERS.md` § "Source hierarchy": a teaching text that draws on other sources. It is the
  source of the two class names and of how each class works, as
  `docs/MODEL.md` § "The agents" states them, and of the disagreement
  about altitude quoted above. It is never the authority for a number. Read in
  full at that address.

<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

Any reader can reach the three journal articles above through their DOI or
PMID, and Dosch and Tharp's chapter at its address. `docs/references/` cannot
hold copies of the two owner-attested sources, because the repository is
public (`docs/references/README.md` § "Redistribution"). So three things rest
on the owner's copies alone: the passage quoted from Datex-Ohmeda, the 1–18% range
beside it, and the worked example attributed to Boumphrey and Marshall.
Nothing stored depends on any of them. A reader who wants to verify one has to
reach the document itself.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**Sources for the ambient pressures in `docs/MODEL.md` § "Altitude".** Each
was read as its PubMed abstract on 2026-11-22.

- Hernández-Zenteno RJ, Pérez-Padilla R, Vázquez JC. Normal breathing during
  sleep at an altitude of 2240 meters. *Arch Med Res* 2002;33(5):489-94.
  doi:10.1016/s0188-4409(02)00398-3. The abstract gives Mexico City "a mean
  barometric pressure of 585 mmHg" at 2240 m.
- Banchero N, Gimenez M, Rostami A, Eby SH. Effects of simulated altitude on
  O2 transport in dogs. *Respir Physiol* 1976;27(3):305-21.
  doi:10.1016/0034-5687(76)90060-8. Its measurements were made "in Denver at
  a PB of 635 mm Hg". The subjects were dogs, but the figure is the
  laboratory's ambient pressure.

### The tests and code behind this section

**For developers.** The inert circuit is `BreathingCircuit`. The directional
checks in `tests/reference/test_sevo_patient.py` assert that a higher cardiac
output slows the rise of $`F_A`$. The MAC-multiple display divides by each
agent's tier-2 `mac_at_age_40_percent`, and the Datex-Ohmeda 1–18% range is desflurane's
`max_delivered_concentration_percent`. `reference_adult.json` carries both
fat-flow comparisons. Its Heinonen et al. note gives both figures and the
volume-to-mass conversion between them, and says
that fat depots differ. The default cardiac output is
`default_cardiac_output_l_min`, and no equation reads `weight_kg`. The
reference-condition gap leaves the relative residual, which the mass-balance
tolerance bounds, untouched.
`core/liquid_agent.py` is where an amount leaves the unit. It converts a
delivered or exhausted amount exactly and reads a store 5.8 % high
(`test_the_reference_condition_gap_is_the_ratio_of_molar_volumes`), and its
docstring says so. The humidification table was computed with
`_wash_in_ratio` in `tests/reference/test_published_wash_in_and_elimination.py`,
against the published means and standard deviations that the module itself
holds.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**For developers.** `docs/MODEL.md` § "Known limitations" is written for a
clinician and names no test. The paragraphs above name the tests behind most of
its figures. These tests compute the rest:

1. `test_the_muscle_group_equilibrates_in_the_minutes_printed`: the muscle
   group's 85 to 135 minutes, in `docs/MODEL.md` § "Intertissue diffusion: the missing fourth
   compartment".
2. `test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours`:
   the hours over which the missing fourth compartment is the largest term of
   the washout, in the same section.
3. `test_the_stored_set_differs_from_yasudas_means_by_the_percents_printed` and
   `test_yasudas_fat_spreads_are_the_percents_printed`: how far the stored
   coefficients sit from Yasuda, Targ and Eger's means, and how widely their fat
   measurements spread, in `docs/MODEL.md` § "The tissue:gas coefficients are carried as
   exact".

4. `test_the_omitted_lung_store_is_the_share_of_the_fast_pool_printed` and
   `test_the_omitted_lung_store_lowers_the_wash_in_by_the_amounts_printed`:
   the lung store's share of each agent's fast pool, and how much it would
   lower $`F_A/F_I`$ at one and at 30 minutes, in `docs/MODEL.md` § "Lung
   tissue and pulmonary blood".
5. `test_the_fourth_compartment_and_the_fat_group_fill_as_printed`: the model's
   fat time constants in the table, and the fat fractions, partial-pressure
   ratios and uptake ratios, in `docs/MODEL.md` § "Intertissue diffusion: the
   missing fourth compartment".

The ambient pressures of Denver and Mexico City are cited in § "Altitude".

## The provenance table, and the markers over restated values

`tools/doc_check.py` (run by `make check` and CI) checks the provenance table
in § "Where each stored value comes from" against the data files in both
directions. Every row must name a key that the file
contains and state the value stored there, and every numeric parameter in every
data file must have exactly one row. The function that does this,
`check_provenance`, confirms that a documented key exists and holds the stated
value, never that the value is right or which tier its source has.

Both directions start from a data file, so that check cannot see a constant
that never entered one, such as a field default on a `core/` dataclass.
`test_every_constant_a_core_dataclass_defaults_to_is_a_value_the_provenance_table_selects`
looks for such a constant. It reads every numeric field default on a `core/`
dataclass through `dataclasses.fields()`, including one written as a named
constant, and requires each to appear in the provenance table's Selected-value column.
It skips zero and a field's full scale (1, or 100 for a percent), which carry
no scientific content. It matches values, not names, so it can miss a
constant: a new one equal to a value the table already selects passes, and 6.0
is selected for both the circuit and the vessel-rich tissue.

The provenance table is not the only place these values appear. Some prose restates one:
the reference adult's alveolar volume and ventilation, and each agent's
blood:gas coefficient, vaporizer maximum and MAC. Each such sentence carries a
hidden marker, an HTML comment that names the file and key it restates:

```text
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
```

`doc_check.py` checks both sides of that link: the key against the data file,
and the stated value against the paragraph the marker sits under. So neither
the file nor the sentence can change without the other. Without the markers,
editing a data file would force an update to the provenance table but leave the prose
around it quietly wrong.

Some figures are *derived* from several stored values, and no file holds
them. Such a figure carries a `derived:` marker that names its inputs instead.
One figure may carry several of these markers where its inputs span more than
one file:

```text
<!-- derived: 20.7 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5 -->
```

When an input changes, the checker reports that the figure must be recomputed
and names the figure. It never recomputes the figure itself. The rounding and
the units are matters of judgment, and a plausible wrong number in this
document is worse than none.

**Rewording a marked sentence is expected to fail the check.** The failure
asks for the marker to be moved or updated with the sentence.

A marker can also name a constant in code, such as the simulation step. It is
written as the module's path under the package, followed by the constant's
name:

```text
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->
```

**A figure that equals a stored value must carry a marker.**
`doc_check.py` finds each figure in this document, in `docs/INTERFACE.md` and in
`README.md` that equals a stored value, in that value's unit. The stored values are every
number in a parameter data file, and every public constant in the package
whose name ends in a unit, such as `_S` or `_L_MIN`. A figure that restates
its value carries a `provenance:` or `derived:` marker. A figure that only
coincides with one carries a `not-restated:` marker that lists it:

```text
<!-- not-restated: 2 %, 0.05 -->
```

The check never decides which kind a figure is. `2.5` appears in this document
as an alveolar volume in litres, a flow in litres per minute and a distance in
standard deviations, and `2%` is sevoflurane's MAC in one sentence and a dial setting in
the next. Binding a figure to a key by its value would be confidently wrong
where a reader trusts most. So the writer says which kind it is, and the check
enforces only that somebody did. A marker covers only the values it names, in
their units, so a marker for the 6 L circuit does not clear desflurane's 6%
MAC in the same paragraph. The check reads:
<!-- not-restated: 6 L -->

- a unit written as a word, such as "seconds", and a time in milliseconds,
  minutes or hours, which it converts to seconds;
- a unit in lower case, such as "l/min";
- each number in a list joined by slashes, such as "6/33/14.5 L", with the
  list's unit;
- in math, a symbol given a number with `=` or `\approx`, such as
  $`V_A = 2.5`$ L or $`V_A = 2.5\,\mathrm{L}`$, where the number ends the span
  or comes before a comma, a semicolon or `\quad`.
<!-- not-restated: 6 L, 33 L, 14.5 L, 2.5 L -->

It reads no other number in math, because most are exponents and coefficients
that only happen to equal a stored value, and it skips a math span split
across two lines. A marker under a list covers the whole list, because a
marker cannot sit inside a list item. A `not-restated:` marker fails if its
paragraph no longer contains a figure it lists, so the declaration cannot
outlive its sentence. A number that equals no stored value, such as a
flow-sweep point or a worked example, needs no marker.

## What the data-file format requires of a `sources` entry

**The second and third of the rules for a `sources` entry in
§ "Source hierarchy: what may be cited as the authority for a value" are part
of the data-file format, and `make check` enforces them.** Each family of data
file (agent, patient and machine) has its own `schema_version`, checked against
that family's supported versions in `src/anesthesia_sim/core/parameters.py`, so
a format change affects only its own family. Agent files must be version 4,
because they also hold `molar_mass_g_mol` and `liquid_density`
(§ "Agent amount"). Patient and machine files must be version 3. Each
`sources` entry carries three required fields, and a file may carry one
optional top-level field:

- `tier`, on each `sources` entry: `primary`, `secondary` or
  `reference-implementation`. It says which of the three tiers in `docs/PARAMETERS.md` § "Source
  hierarchy" the *document* belongs to.
- `adopted`, on each `sources` entry: whether this file names that source as
  the authority for a value it stores.
- `authority_for`, on each `sources` entry: the dotted key
  paths of the stored values that rest on this source, spelled as the
  provenance table spells them. The list is empty exactly when `adopted` is
  false. The per-row counts under `docs/PARAMETERS.md` § "Where this project stands" are computed from it.
- `provenance_gap`, optional and top level: why no primary source has been
  adopted, in a file where none has been.

`tools/doc_check.py`'s `check_source_tiers` enforces these as exact rules:

- Every entry declares a tier from the closed vocabulary, an `adopted` flag
  and an `authority_for` list.
- That list is non-empty exactly when the entry is adopted.
- Each path in the list is a stored value of the same file, and no stored
  value is named by two entries.
- A file with no entry that is both `primary` and `adopted` records a
  non-empty `provenance_gap`.

Each rule is an error that stops the build, not a warning, because none of
them needs judgment to decide. `src/anesthesia_sim/core/parameters.py` also
checks the vocabulary and the `authority_for` rules when it loads a file, so a
bad entry fails as soon as the file is read.

**`tier` and `adopted` are two fields because one field alone would decide
nothing.** Every agent file cites primary measurements that it has explicitly
*not* adopted, and so does the reference patient, which cites five. A check
that read the tier alone would report all five of this project's parameter data files as
primary-sourced, although the reference patient adopts no primary source and
many of the table's rows are tier 3 (`docs/PARAMETERS.md` § "Where this project stands" gives
the counts). That is the failure the second rule for a `sources` entry exists to prevent, so
the check reads the adoption and not the citation list. Today each agent file
declares four adopted primary sources: for the tissue:gas coefficients, the
vaporizer maximum, `mac_awake` and the liquid density. `src/anesthesia_sim/data/patients/reference_adult.json` declares
none and records the gap.

**What the check does not decide is whether a citation labelled `primary`
really is one.** That needs somebody who has read the paper. A tool that
guessed, from the author, the journal or a product name in the title, would
look authoritative and be wrong. The tool checks that a claim was made and is
well-formed, and a reviewer checks that the claim is true.
