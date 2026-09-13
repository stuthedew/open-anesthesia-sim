---
id: PL-ZDWL
title: Run the published elimination comparison at Yasuda's own measured alveolar ventilation, which the methods text states and this project has not read out
priority: P1
effort: S
status: done
classes: science
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-13
closed: 2026-09-13
pr: 536
verify: python3 tools/doc_check.py check && grep -qF 'Both papers have since been read at full text, and the study publishes no' docs/MODEL.md
---

**Problem.** Run the published elimination comparison at Yasuda's own measured alveolar ventilation, which the methods text states and this project has not read out

**Where this came from.** `PL-RFLN` ran the apparatus-dead-space diagnostic
and found that a series dead space is exactly an alveolar-ventilation
decrement in this model. That made the operating point's ventilation the
load-bearing number, and it is the one thing the Route section of `PL-RFLN`
asked for that was never read out: its methods reading records *how* Yasuda
derived the alveolar fraction of ventilation - from
`F_M = f_A x F_A + f_D x F_I`, averaged over the 10-, 15- and 20-minute
samples, with minute ventilation measured rather than alveolar - but not the
**value**.

**Why it matters, and why it is the strongest remaining move.** The model runs
this comparison at 4.0 L/min, which `src/anesthesia_sim/data/patients/reference_adult.json`
records as a program default with no primary source behind it - a convention,
not a measurement, and not Yasuda's. So the second row of `docs/MODEL.md`'s
candidate table ("alveolar ventilation too high") is currently a free-parameter
sweep. Reading the study's own figure converts it into a sourced operating
point, and it is the only candidate left that could move the comparison
without being fitted to it.

It also settles a question `PL-RFLN` had to leave open. Yasuda's derived `f_A`
already nets out the apparatus dead space - the mixing chamber supplying `F_M`
sits beyond the nonrebreathing valve, so the 50 ml that is re-inspired never
reaches it - so a comparison run at their ventilation must **not** subtract the
dead space again. Whether any decrement is owed at all therefore depends
entirely on this value.

**Route.** Yasuda et al. *Anesthesiology* 1991;74:489-98 (PMID 2001028)
§ "Materials and Methods", and the parallel § in *Anesth Analg*
1991;72:316-24 (PMID 1994760). Both are in the private reference corpus
`stuthedew/open-anesthesia-sim-references`, which attaches to a session with
`add_repo` (`PL-5NR5`); neither is in PubMed Central and neither is held in
this repository. Read the minute ventilation and the derived alveolar
fraction, then re-run the four cohort rows in
`tests/reference/test_published_wash_in_and_elimination.py` at that
ventilation, both limbs.

**Done when.** The study's measured minute ventilation and derived alveolar
fraction are recorded in `docs/MODEL.md` with their page locators, the four
cohort rows are re-measured at that operating point, and the second row of the
candidate table either becomes a sourced result or is recorded as still
unreadable from the text.

## Read at the source 2026-09-13, and the premise in the title is wrong

The corpus was attached (`add_repo`, then `git clone --depth 1`) and
`yasuda-1991-comparison-of-kinetics-of-sevoflurane-and-isoflurane-in-humans.pdf`
read with `pdftotext -layout`. **PubMed route: not applicable - read from the
private reference corpus at full text.**

**The Anesth Analg paper states no numeric ventilation anywhere.** This item's
title says the methods text "states" the alveolar ventilation. It does not.
What the text says:

- § Methods: "Ventilation was controlled via a nonrebreathing system to produce
  normocapnea (end-tidal carbon dioxide [CO2] of 5.5%-6.5%)". So ventilation was
  **titrated to a CO2 target per subject**, not set to a figure - there is no
  single number to read out.
- § Methods: "Minute ventilation (VE) was measured, and mixed expired and
  inspired samples were collected at 5, 7.5, 10, 12.5, 15, 20, 25, and 29 min."
  Measured, used in the mass balance, and **its value is never reported**.
- The `fA` derivation is confirmed verbatim - `FM = fA x FA + fD x FI`, "where
  fA equals the fraction of ventilation coming from the alveoli and fD equals
  the fraction of ventilation coming from the dead space", averaged over the
  10-, 15- and 20-minute samples. **No numeric `fA` is printed either.**

Searched the whole extracted text for `L/min`: the only hits are gas-chromato-
graph carrier flows in mL/min and the two clearance figures below. There is no
ventilation table and no subject-characteristics ventilation row.

**What the paper does give, and it is not the same quantity.** Two fitted
clearances from the five-compartment mammillary model:

| Quantity | Sevoflurane | Isoflurane |
| --- | --- | --- |
| Pulmonary elimination clearance, `V_c x k_10` | 3.58 +/- 0.43 L/min | 3.62 +/- 0.41 L/min |
| Total body clearance | 3.6 +/- 0.6 L/min | 3.6 +/- 0.5 L/min |

For an agent that is essentially not metabolised, pulmonary clearance is the
rate alveolar gas is cleared, so ~3.6 L/min is the closest published analogue
of this model's alveolar ventilation - and it sits **0.4 L/min below the 4.0
this project runs at**.

**Do not treat that as the sourced operating point this item wanted.** Two
reasons, and the first is disqualifying on its own:

1. **It is fitted to the very curves the comparison is against.** `V_c` and
   `k_10` come from fitting the five-compartment model to these subjects'
   elimination data. Running this project's model at a ventilation derived from
   the data, then scoring this project's model against the same data, is
   circular. A measured ventilation would not be; this is not one.
2. It is a lumped clearance from a different model structure - `V_c` is a
   fitted 2.10 and 2.31 L "central compartment", not this model's alveolar gas
   volume.

**What it is still worth, and it strengthens `PL-RFLN` rather than reopening
it.** 3.6 L/min is the operating point `PL-RFLN` already measured at f = 8
breaths/min, so the answer needs no new run
(`tests/reference/test_published_wash_in_and_elimination.py`, measured
2026-09-13): desflurane moves from -2.33 to **-1.73 SD** while isoflurane goes
to **+1.39 SD (n=7)** and **+1.82 SD (n=8)**, both outside their published
spreads, and sevoflurane to +0.62 SD. The same common-mode failure, now at the
nearest thing the study publishes to its own ventilation. Nothing about
`PL-RFLN`'s conclusion changes.

**The Anesthesiology paper is not in the corpus, which is the real gap.**
Holdings are Mapleson 1963, Smith/Zwart/Beneken 1972, this one, and
Nickalls/Mapleson 2003. **Yasuda et al. Anesthesiology 1991;74:489-98 (PMID
2001028) is absent** - and that is the desflurane cohort, the one the residual
is actually about, and the only one of the two whose methods section sites the
end-tidal port and names the ~50 ml dead space. Per
`.claude/rules/citing-sources.md`, a miss is an answer: recorded here and put to
the project owner rather than narrowed around.

**Done when** (replacing the version above, which assumed the value was
printed). Either the *Anesthesiology* paper is supplied and its ventilation
read, or this item closes as answered: the ventilation is not published in
either abstract or in the one full text held, the nearest published analogue is
a fitted clearance that cannot be used without circularity, and `docs/MODEL.md`
says so beside the second candidate row.

## The Anesthesiology paper supplied and read 2026-09-13, and this item is answered

The project owner supplied Yasuda et al. *Anesthesiology* 1991;74:489-98 (PMID
2001028) the same day and it is now corpus holding
`yasuda-1991-kinetics-of-desflurane-isoflurane-and-halothane-in-humans.pdf`.
**Read as page images at full text** - `pdftotext` returns an empty file, it
being a scan with no text layer, and it exits zero while doing so.

**The ventilation is not published in this one either, and for the same
reason.** Page 490: "Ventilation was controlled via a nonrebreathing system to
produce normocapnea (end-tidal carbon dioxide of 5.5-6.5%)". Titrated per
subject to a CO2 target, so there is no single figure to read out. "Minute
ventilation (V_E) was measured and mixed expired and inspired samples were
collected at 5, 7.5, 10, 12.5, 15, 20, 25, and 29 min" - measured, used in the
mass balance, **never reported**. Tables 1-6 carry A_i coefficients, hybrid and
mammillary time constants, transit times, blood flows, tissue volumes and
recovery. **There is no ventilation row anywhere in the paper.**

So both papers are now read at full text and neither prints V_E or f_A. The
premise in this item's title is wrong for the study as a whole, not just for one
of the pair.

**What page 492 does settle, and it is what `PL-RFLN`'s derivation needed.**
The paper defines the quantity explicitly, in the total-body-clearance method:
doses "delivered to the alveoli (calculated as `F_I x V_A x 30 min`, where
`V_A = f_A x V_E`)". So `f_A` is the alveolar fraction of **total minute
ventilation**, and `V_A` is `f_A x V_E` - which is the assumption `PL-RFLN`'s
series-dead-space derivation rests on, now confirmed at the source rather than
inferred from the `F_M` formula alone.

**The nearest published analogue, and it changes the desflurane picture.**
Page 494, pulmonary elimination clearances (`V_1 x k_10`) for the n=8 cohort:

| Agent | Pulmonary elimination clearance | Total body clearance |
| --- | --- | --- |
| Desflurane | 4.11 +/- 0.45 L/min | 4.6 +/- 0.9 L/min |
| Isoflurane | 3.94 +/- 0.34 L/min | 4.0 +/- 0.5 L/min |
| Halothane  | 3.94 +/- 0.33 L/min | 4.8 +/- 0.5 L/min |

Against the n=7 cohort's 3.58 and 3.62 L/min recorded above. **The model runs
at 4.0 L/min, so for the cohort desflurane's residual belongs to it is already
at the study's own effective pulmonary clearance** - if anything a shade below
desflurane's 4.11.

**That is a second and independent argument against the apparatus dead space,
and it is stronger than the common-mode one.** A dead-space decrement *lowers*
the model's alveolar ventilation. For the n=8 cohort that moves it **away** from
4.11, not toward it. So the mechanism `PL-RFLN` rejected for being common-mode
is also pointed the wrong way for the one cohort it would need to help.

**How much weight these clearances bear, measured from the paper itself.** The
same eight subjects breathed all three agents **simultaneously** from one
cylinder, so their ventilation was physically identical across the three rows.
The fitted clearances still come out 4.11, 3.94 and 3.94 - about 4% spread on a
quantity that cannot differ. That is the method's own precision, and it is why
these figures are worth quoting as a consistency check on the operating point
and **not** worth adopting as one: they are fitted to the same elimination
curves the comparison scores against, which would be circular. The paper says as
much itself at page 497 - "the opposite change in `V_1` resulted in the absence
of a difference" in clearance despite a threefold solubility range.

**Verified in passing, since the section cites them.** Table 6 recovery:
desflurane 105 +/- 25%, isoflurane 102 +/- 13%, halothane 64 +/- 9%, matching
`docs/MODEL.md` exactly. Subjects: eight healthy males, age 25 +/- 5 yr, weight
**76 +/- 7 kg**, height 182 +/- 4 cm - the source of the "76 kg" the section
uses, against this model's 70 kg reference adult.

**Done.** The ventilation is not published in either paper; the nearest
analogue is a fitted clearance that cannot be adopted without circularity but
does place the n=8 cohort at ~4.1 L/min against the model's 4.0; and
`docs/MODEL.md` now records that beside the candidate table.
