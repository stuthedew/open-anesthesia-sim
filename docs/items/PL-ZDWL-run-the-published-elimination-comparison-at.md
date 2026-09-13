---
id: PL-ZDWL
title: Run the published elimination comparison at Yasuda's own measured alveolar ventilation, which the methods text states and this project has not read out
status: untriaged
feature: model-spec-accuracy
added: 2026-09-13
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
