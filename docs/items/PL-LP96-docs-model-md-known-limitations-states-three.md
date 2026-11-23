---
id: PL-LP96
title: docs/MODEL.md § "Known limitations" states three sets of figures that no test computes and no source gives: the lung store's share of the fast pool (20.1%, 19.7%, 23.4%) and its thirty-minute equilibration, the intertissue-diffusion fat fractions (13 to 20% against the trace's 2.3 to 3.9%), and the ambient pressures in Denver and Mexico City
priority: P1
effort: M
status: done
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/reference
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: the figures are docs/MODEL.md prose in Known limitations, and no displayed string carries them, so no learner can see a wrong value through this item
added: 2026-11-14
closed: 2026-11-22
pr: 2255
payoff: Each size that docs/MODEL.md gives for an omission in the model is computed by a test or cited to a source, so a clinician judging a trace by it is not misled by an unchecked figure.
tests: tests/reference/test_known_limitations_figures.py::test_the_omitted_lung_store_is_the_share_of_the_fast_pool_printed, tests/reference/test_known_limitations_figures.py::test_the_omitted_lung_store_lowers_the_wash_in_by_the_amounts_printed, tests/reference/test_known_limitations_figures.py::test_the_fourth_compartment_and_the_fat_group_fill_as_printed
---

**Problem.** `PL-19W8` held each numeric paragraph of `docs/MODEL.md` § "Known limitations" to a test, a source or a date. Three sets of figures had none of those, so their paragraphs say they have no test yet and name this item:

1. The lung store. "Lung tissue and pulmonary blood are an omitted store worth about a fifth of the fast pool" gives 20.1%, 19.7% and 23.4% from round physiologic figures (1 kg of lung at a tissue:blood ratio of 1.2, and 1.8 L of blood). The next paragraph says the store equilibrates within about thirty minutes. Neither the "fast pool" these are shares of nor the round figures' source is stated beside them.
2. The intertissue-diffusion bias. "The fat trace shows only the slowly filling fat" gives fat beside lean tissue at 13 to 20% of arterial after an hour, against the trace's 2.3 to 3.9%. The section says these were worked out from the compartment structure, not from running the simulator.
3. The ambient pressures in Denver (about 630 mmHg) and Mexico City (about 585 mmHg), which no source in the section gives.

**Why it matters.** These figures tell a clinician how large each omission in
the model is, and so how far to trust a trace. A size that no test computes and
no source gives can be wrong without anyone noticing, and a reader would then
misjudge the limitation it describes.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n 'PL-LP96' docs/MODEL.md`
printed lines 5751, 5760, 6074 and 6490, each a sentence saying the figures
beside it have no test yet. The same three sets of figures were in
`docs/MODEL.md` at the Gate 3 freeze (`0947408`). `grep -rn 'Denver\|Mexico City'`
over `src/anesthesia_sim` outside the data files found nothing, so no
displayed string carries them.

**Done when.** Each figure is computed by a test, or cited to a source read in the session, and the `no test yet (`PL-LP96`)` sentences name the test or carry the citation. A figure the test shows wrong is corrected.

**Generator check.** The fact is whether a `docs/MODEL.md` sentence about what
the model computes matches what it computes, which `PL-B6YV` states. That head
is spent, and its verdict names the remaining stock as the
`model-claims-held-by-tests` passes, of which this item is one. So it is
planned stock, not a re-entry.

**Closed 2026-11-22.** Each of the three sets of figures is now computed by a test or cited to a source read in the session, and no paragraph says it has no test yet.

1. The lung store. `docs/MODEL.md` § "Lung tissue and pulmonary blood" now says what the fast pool is and that the round figures are not measurements. `test_the_omitted_lung_store_is_the_share_of_the_fast_pool_printed` computes the three shares from the stored volumes and coefficients. The sentence that the store "equilibrates within about thirty minutes" was wrong: the store sits at the alveolar partial pressure, so it fills only while $`F_A`$ rises. It is replaced by the computed drop in $`F_A/F_I`$ when the store is added as alveolar capacity, which `test_the_omitted_lung_store_lowers_the_wash_in_by_the_amounts_printed` checks: 0.08 to 0.10 at one minute and 0.001 to 0.005 at 30 minutes at the default settings, and 0.005 to 0.010 at 30 minutes with 0.5 L/min of fresh gas. A sweep over the supported ranges found the 30-minute drop as large as 0.037 at a ventilation of 0.5 L/min and a cardiac output of 1 L/min, and 0.15 at a cardiac output of 0.1 L/min. So the text gives the figure at stated settings and claims no bound.
2. The intertissue-diffusion figures. The two fat bullets had lost their condition that the compartments fill from a steady arterial partial pressure, and it is restored. `test_the_fourth_compartment_and_the_fat_group_fill_as_printed` computes their figures over every case length from 30 minutes to 4 hours. "As large as or larger" became "about as large as, or larger", because the ratio falls to 0.9.
3. The ambient pressures. Denver is cited to Banchero et al. 1976 (doi:10.1016/0034-5687(76)90060-8), whose abstract gives 635 mmHg, so the text now says about 635 rather than 630. Mexico City's 585 mmHg is cited to Hernández-Zenteno et al. 2002 (doi:10.1016/s0188-4409(02)00398-3). Both abstracts were read on PubMed on 2026-11-22. Julian et al. 2014 was read and not cited, because its abstract does not name the city.

Computed claims found wrong or missing a condition: three in the text before this pass (the thirty-minute equilibration, the fat bullets' lost condition, and Denver's unsourced 630 mmHg). The blind review found two more in this pass's own new text (the drops stated without their default settings, and "as large as" against a ratio of 0.9), and both were fixed before merge.

Files checked in the sweep: `docs/MODEL.md`, `docs/PARAMETERS.md`, `docs/VERIFICATION.md`, `docs/INTERFACE.md` and `README.md`, for "thirty minutes", "630 mmHg" and any other copy of the changed figures. None remained.
