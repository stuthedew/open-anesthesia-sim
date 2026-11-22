---
id: PL-LP96
title: docs/MODEL.md § "Known limitations" states three sets of figures that no test computes and no source gives: the lung store's share of the fast pool (20.1%, 19.7%, 23.4%) and its thirty-minute equilibration, the intertissue-diffusion fat fractions (13 to 20% against the trace's 2.3 to 3.9%), and the ambient pressures in Denver and Mexico City
priority: P1
effort: M
status: ready
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/reference
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: the figures are docs/MODEL.md prose in Known limitations, and no displayed string carries them, so no learner can see a wrong value through this item
added: 2026-11-14
payoff: Each size that docs/MODEL.md gives for an omission in the model is computed by a test or cited to a source, so a clinician judging a trace by it is not misled by an unchecked figure.
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
