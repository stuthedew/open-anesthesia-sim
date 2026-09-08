---
id: PL-RFLN
title: Settle what causes desflurane's five-minute washout residual, which PL-73G7 narrowed to end-tidal sampling or the published datum
status: untriaged
added: 2026-09-08
---

**Problem.** Settle what causes desflurane's five-minute washout residual, which PL-73G7 narrowed to end-tidal sampling or the published datum

**Where PL-73G7 left it.** With the rebreathing circuit removed as a
diagnostic, this model reproduces sevoflurane's and both isoflurane cohorts'
published five-minute `F_A/F_A0` and washes desflurane out 2.33 published SD
too fast. `docs/MODEL.md` § "Desflurane's residual, and why the parameter file
was not changed" is the authority and carries the whole account; it is not
restated here. What it rules out: desflurane's blood:gas and tissue:gas
coefficients, alveolar ventilation, cardiac output, the fast capacity this
model omits, a non-ideal lung, and residual rebreathing in the published
apparatus. Each fails the same way - it moves sevoflurane and isoflurane as
much as desflurane or more, and the published rows have no room for that, or
it moves desflurane the wrong way.

**The two candidates left, and what would separate them.** Either end-tidal
sampling in a lung with ventilation-perfusion dispersion, whose bias inflates
`F_A/F_A0` at both ends and grows as solubility falls, or the published value
itself. The first needs a weighting neither abstract gives: the flow-weighted
alveolar reading of the same calculation moves every agent the wrong way, so
the hypothesis stands entirely on which units the end-tidal sample came from.

**Route.** The methods sections of Yasuda et al. Anesthesiology
1991;74:489-98 (PMID 2001028) and Anesth Analg 1991;72:316-24 (PMID 1994760):
the breathing system, how end-tidal gas was sampled, and the alveolar
ventilation measured through the elimination. Neither is in PubMed Central and
neither is held in `docs/references/`, so this needs a copy the project owner
can supply, and it is worth deciding whether that is worth doing at all before
any work is scheduled. Failing that, a test-only multi-alveolar-compartment
diagnostic could bound the end-tidal weighting's size, which would say how
much of the residual it could possibly carry without settling that it does.

**Done when.** Either the cause is named against the methods sections, or the
question is recorded as unanswerable from what this project can reach and
`docs/MODEL.md` says so in place of the two open candidates.
