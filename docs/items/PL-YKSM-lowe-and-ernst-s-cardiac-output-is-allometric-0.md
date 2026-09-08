---
id: PL-YKSM
title: Lowe and Ernst's cardiac output is allometric (0.2 x M^0.75 = 4.84 L/min at 70 kg), not the stored fixed 5.0, and weight_kg is still read by no equation
priority: P1
effort: M
status: done
classes: science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-08
pr: 470
verify: python3 tools/doc_check.py check && grep -qF '2.6 times more slowly' docs/MODEL.md
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

## Recommendation, 2026-09-08: keep the fixed 5.0 and record why

Offered so the deciding session does not re-derive it. **The decision is still
the project owner's** and this item stays `needs-decision`; nothing below has
been implemented.

**1. Adopting would move the stored value away from the only primary
measurement this file cites.** Cattermole et al. 2017 (PMID 28320891, already a
`sources` entry here, read at full text 2026-09-06) measured a cardiac-output
median of 5.51 L/min in the 50.0-74.9 kg band, n = 686. The stored 5.0 L/min is
9.3% below that median; Lowe's 4.84 L/min is 12.2% below it. So the change
being contemplated is one that makes the stored value *worse* against the
reachable measurement, in exchange for agreement with a lineage that is
tier 2 and cites its own numbers onward.

**2. The within-adult evidence for a 0.75 exponent on cardiac output
specifically is weaker than for clearance.** Haemodynamic convention is body
surface area, i.e. cardiac index in L/min/m2. The one within-human fit of the
exponent reachable from a session, Rowland et al. 2000 (PMID 10982700, Pediatr
Cardiol 2000;21(5):429-32, doi:10.1007/s002460010102 - retrieved from PubMed
and read at abstract depth only, 2026-09-08), fitted maximal cardiac output
against body mass at an exponent of **0.55**, not 0.75, and found the BSA ratio
standard (exponent 1.0) appropriate. That is 24 premenarcheal girls at maximal
exercise, so it does not settle resting adults and must not be cited as though
it did.

**THIS PARAGRAPH READ DIFFERENTLY UNTIL LATER THE SAME DAY, AND WAS WRONG.** It
said the 3/4 power is interspecies allometry that humans are not scaled by,
which overstates the case against; section 4 of the analysis below is the
correction, and within humans 3/4-power scaling is mainstream in anaesthetic
pharmacokinetics. What survives is only the narrower claim above, about cardiac
output rather than about clearance.

**3. The book is not established as the authority for the relation.** Page 59
uses 2 kg^(3/4) in a worked example and cites nothing there; the derivation is
in a chapter outside the pages supplied. So even the recorded-decision path
would be adopting a relation whose provenance inside its own source is unread.

**4. It is out of milestone**, as this brief already says.

**So: take the cheap branch.** Record that the fixed 5.0 is kept, and why -
that its cited lineage would give 4.84 L/min at 70 kg, and that the value is
kept because the reachable human measurement sits above both and the 3/4 power
is a cross-species law. The 4.84 discrepancy is already recorded in
`docs/MODEL.md` and in the data file's Lowe and Ernst entry (`PL-7HDS`), so
what is left is the "why it is kept" half, which is one paragraph in "Known
limitations" plus a line on the `default_cardiac_output_l_min` provenance.

**What that leaves open, and where it belongs.** `weight_kg` still has no
consumer, which is the part of this item that is a real hazard rather than a
provenance note. The recommendation is not to close that with Lowe's relation
but at the weight-varying-physiology milestone, where a scaling rule can be
chosen for humans on its own evidence - BSA-indexed cardiac output being the
obvious candidate - rather than inherited from a closed-circuit dosing method.
Until then the honest statement is the one the file already makes: the weight
is a labelling convention that no equation reads.

## What the decision costs and buys, measured, 2026-09-08

Written after the project owner asked for the trade-off explicitly. The
recommendation above is unchanged; its second reason is corrected in place and
a stronger one is added here.

### 1. What adopting would change today: one number, and 3.32% everywhere

Only one patient file exists (`reference_adult.json`), and `weight_kg` is read
by nothing outside `core/parameters.py`. Cardiac output is also already a
**live control** - `ControlKind.CARDIAC_OUTPUT`, settable at run time over 0.0
to 10.0 L/min and preserved across a reset - so `default_cardiac_output_l_min`
is the value that control *starts* at, not a constant the learner is held to.

Adopting today therefore moves 5.0 to 4.8401 L/min and nothing else. Every time
constant is proportional to $`1/Q`$, so all of them lengthen by exactly the
same 3.32%. Measured 2026-09-08 against the shipped sevoflurane coefficients:

| Quantity | at Q = 5.00 | at Q = 4.84 |
| --- | ---: | ---: |
| Vessel-rich time constant | 2.7 min | 2.8 min |
| Muscle time constant | 135.4 min | 139.9 min |
| Fat time constant | 2528.2 min | 2612.1 min |
| Venous mixing $`V_v/Q`$ | 14.66 s | 15.15 s |

Nothing qualitative moves: no curve changes shape, and no ordering changes.

### 2. The strongest argument against is structural rather than evidential

$`\tau_i = V_i \lambda_{i:b} / Q_i`$. This model stores compartment volumes as
**fixed litres**, so under a weight-scaled cardiac output alone the volumes go
as $`M^0`$ while the flows go as $`M^{0.75}`$, making
$`\tau \propto M^{-0.75}`$. **A heavier patient would equilibrate faster** - at
100 kg against 70 kg, 23.5% faster - which is backwards from the clinical
observation every text teaches, that larger and fatter patients equilibrate
more slowly.

Lowe and Ernst's own scheme does not have this problem, because it scales
both: volumes are fixed fractions of body mass ($`M^1`$) and cardiac output
goes as $`M^{0.75}`$, giving $`\tau \propto M^{0.25}`$. Measured:

| Scheme | Q, 100 kg vs 70 kg | Time constants | Direction |
| --- | ---: | ---: | --- |
| Fixed volumes, fixed Q (today) | x1.000 | x1.000 | weight does nothing |
| Fixed volumes, $`Q \propto M^{0.75}`$ | x1.307 | x0.765 | **faster - wrong** |
| $`V \propto M`$, $`Q \propto M^{0.75}`$ | x1.307 | x1.093 | slower - right |

So the relation is **only safe as half of a package**: adopting the flow law on
its own would be worse than either endpoint. That is a property of this model's
structure rather than a judgment about the literature, and it is the reason to
decline that survives whatever the sources turn out to say.

### 3. What adopting would buy, stated at full strength

- **It completes the lineage's own scheme.** The pairing above - volume
  exponent 1, flow exponent 0.75 - is exactly what Lowe and Ernst use. Gas
  Man's fixed litres beside a fixed 5.00 L/min is what broke the coherence,
  not the book.
- **`weight_kg` acquires a consumer.** A stored parameter a reader can change
  with no effect is what `CLAUDE.md`'s safety-critical standard calls a
  presentation failure in waiting, and this is the obvious consumer.
- **The rule is needed anyway** for any patient other than the reference adult,
  and choosing it late means choosing it under pressure.
- **It is a teachable fact**: cardiac output rises with size but falls per
  kilogram, which is the same shape as the metabolic-rate argument Lowe's whole
  method rests on.

### 4. The correction: 3/4-power scaling within humans is mainstream in anaesthetic PK

The recommendation's second reason originally called the 3/4 power interspecies
allometry that humans are not scaled by. That is wrong as written, and it
excluded the strongest pro-adoption authority. Anderson and Holford,
*Mechanism-based concepts of size and maturity in pharmacokinetics* (Annu Rev
Pharmacol Toxicol 2008;48:303-32, PMID 17914927,
doi:10.1146/annurev.pharmtox.48.113006.094708 - retrieved from PubMed and read
at abstract depth only, 2026-09-08), state in terms: "Size is the primary
covariate and can be referenced to a 70-kg person with allometry using a
coefficient of 0.75 for clearance and 1 for volume." The first author writes
from a department of anaesthesiology, and this is the standard basis for the
paediatric anaesthetic pharmacokinetic models in routine use.

The honest statement is therefore not that 0.75 is foreign to human modelling.
It is that 0.75 is established for **clearance**, that Lowe applies it to
cardiac output, that the reachable within-human fit for cardiac output
specifically is lower, and that this model cannot take the flow half without
the volume half.

### 5. Provenance, which the pending interlibrary loan may move

Page 59 uses 2 kg^(3/4) in a worked example and cites nothing there. A second
loan request covering pages 17-21 was placed by the project owner on
2026-09-08; if the derivation is there with a source of its own, the relation
stops being an unattributed line inside a tier-2 compilation, which is a real
input to this decision. Waiting for it costs nothing, because nothing consumes
the value today.

### So, concretely

Keep 5.0 and record why. If the answer is instead to scale, **adopt both laws
together or neither** - volumes proportional to body mass, or to fat-free mass
which the obesity pharmacokinetic literature generally prefers over total
weight, and cardiac output to its three-quarter power - at the weight-varying
physiology milestone and with a validation target, rather than as a lone change
to one stored default.

## Decided 2026-09-08: the fixed 5.0 is kept

**The project owner's decision**, taken on the recommendation and the analysis
above. The relation is not adopted, no stored value moves, and `weight_kg`
stays a labelling convention that no equation reads.

**What was recorded, which is the Done-when's second branch.**

- `docs/MODEL.md`, "Known limitations": a new entry stating that cardiac output
  does not scale with the patient, giving both published figures either side of
  the stored value (Lowe and Ernst's 4.84 L/min at 70 kg, Cattermole et al.'s
  measured 5.51 L/min median), the structural reason the fixed value is kept,
  and the 20 kg child worked out at about 2.6 times more slowly. It closes with
  what a reader should take from it: this model describes one 70 kg adult, and
  no field in the interface makes it a paediatric or weight-varying model.
- `src/anesthesia_sim/data/patients/reference_adult.json`: the decision is on
  the Cattermole entry, which is this parameter's comparison entry and so is
  where a reader of `default_cardiac_output_l_min` meets it. The Lowe and Ernst
  entry, which states the discrepancy, now points at it.

**The clarification that settled it** (project owner, 2026-09-08). The stated
goal was never "should the reference adult read 4.84" but "a child-sized
patient must not default to 5" - which is right, and is
`ROADMAP.md`'s planned-milestone item 30 rather than this item. Worked at 20 kg
against the shipped sevoflurane coefficients: scaling cardiac output alone
gives 2.64 times the adult's time constants, scaling volumes with it gives
0.76 times, and changing nothing gives 1.00. So the half-measure is further
from the paediatric truth than the status quo, which is why this item closes on
the recording and the scaling is milestone 30's to build as a package.

`PL-MMWX` carries recording that obligation in milestone 30's own entry, so a
session scoping it does not have to reach `docs/MODEL.md` to find the
constraint.
