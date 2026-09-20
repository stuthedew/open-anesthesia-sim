---
id: PL-80X7
title: docs/MODEL.md sizes the fixed-alveolar-volume assumption against agent uptake alone, omitting the respiratory-quotient volume change of comparable size
status: untriaged
added: 2026-09-20
---

**Problem.** docs/MODEL.md sizes the fixed-alveolar-volume assumption against agent uptake alone, omitting the respiratory-quotient volume change of comparable size

 — found while closing `PL-WJNS`.

`docs/MODEL.md` § "Alveolar gas" justifies holding $`V_A`$ constant by
comparing the pulmonary uptake rate against alveolar ventilation: sevoflurane
at 2% removes 1.6% of each inspired alveolar volume, "which a fixed volume can
ignore and does", against nitrous oxide's 29%. The conclusion is almost
certainly right. The comparison is incomplete: the patient's respiratory gas
exchange also changes alveolar volume, at oxygen consumed minus carbon dioxide
produced — about 50 ml/min at a respiratory quotient of 0.8 for a 70 kg adult,
which is roughly 1.25% of the reference adult's 4 L/min alveolar ventilation
and therefore of the same order as the 1.6% the argument does weigh.

**Why it matters.** The section says the fixed volume is "correct rather than
merely convenient" for the agents this model ships, and that claim rests on a
one-term comparison against a two-term quantity. Adding the missing term does
not change the verdict — 1.6% and 1.25% together are still nothing beside 29% —
so this is a completeness defect in a published argument rather than a wrong
number, and no stored value or displayed output moves. It is worth correcting
because the section is the one a milestone scoping nitrous oxide is told to
read, and it is where the two standard formulations that lift the constraint
are written.

**Where.** `docs/MODEL.md` § "Alveolar gas", the paragraph beginning "The
alveolar volume is held constant" and the two-row comparison table under it.
Note the circuit-side statement in § "Breathing circuit" is *not* affected and
should not be changed to match: carbon dioxide nets to nothing at the circuit
boundary, because the absorbent removes what the blood returned.

**Done when.** The comparison names the respiratory-gas term, sizes it, and
says why the verdict is unchanged.
