---
id: PL-S5JJ
title: Check the 4.9-9.4% recovered blood:gas figure in docs/PARAMETERS.md and the agent files against Yasuda 1989 Table 2: the brain column gives +4.1, +2.4 and -0.3%
priority: P1
effort: S
status: done
classes: defect, science
feature: model-claims-held-by-tests
touches: docs/PARAMETERS.md, docs/MODEL.md, docs/references, src/anesthesia_sim/data/agents, tests/reference/test_parameter_source_figures.py
added: 2026-11-22
closed: 2026-11-23
pr: 2279
payoff: a reader weighing why the stored blood:gas coefficients are not Yasuda's sees the gap each tissue column actually gives
tests: tests/reference/test_parameter_source_figures.py::test_yasudas_full_tables_recover_the_blood_gas_ranges_printed
---

**Problem.** `docs/PARAMETERS.md` § "v0.2.0: isoflurane and desflurane" says that dividing Yasuda, Targ and Eger's Table 1 by their Table 2 recovers the age-adjusted blood:gas coefficient of their 65.8-year-old cohort, and that these recovered values are 4.9–9.4% above the three stored blood:gas coefficients. The sevoflurane, isoflurane and desflurane agent files carry the same sentence. No test computes it, because neither table's full set of figures is in the repository.

The figures that can be read do not give that range. The paper's abstract (*Anesth Analg* 1989;69(3):370-3, PMID 2774233, read on PubMed on 2026-11-22) gives the brain:blood coefficients, which are Table 2's brain column: sevoflurane 1.70, isoflurane 1.57 and desflurane 1.29. The brain tissue:gas coefficients that `docs/PARAMETERS.md` quotes from Table 1 are 1.15, 2.09 and 0.54. Dividing gives 0.676, 1.331 and 0.419, which are 4.1% and 2.4% above, and 0.3% below, the stored 0.65, 1.3 and 0.42. The other tissues may give other ratios, because a table of per-subject ratios need not divide exactly, but that cannot be checked without the full tables.

**Why it matters.** The sentence is part of the case for why the stored blood:gas coefficients are not Yasuda's. A wrong range there misstates how far the stored values sit from what this cohort implies.

**Done when.** Someone with the full text of Yasuda et al. 1989 (the references corpus holds it, according to the agent files) has recomputed the range from both tables, the documents and agent files state the computed range, and a test computes it from the tables transcribed with their page.

Found 2026-11-22 by the `PL-5C1H` pass. That pass replaced the range in `docs/PARAMETERS.md` with the brain column's figures, which a test computes, and declared the other tissues as having no test yet against this item. The agent files' notes still carry the 4.9–9.4% sentence, and this item corrects them too.

**Generator check.** One-off. The 4.9-9.4% range was written before anyone
had the full tables, and no record says how it was computed. No head's
`misread:` line states the fact: `bin/docket generators --misread` was
searched on 2026-11-23 for "figure", "copy", "stored value" and "prose".

**Done 2026-11-23.** The full text is in the private reference corpus, as
`text/papers/yasuda-targ-eger-1989-solubility-of-i-653-sevoflurane-isoflurane-and-halothane-in-human-tissues.txt`,
and both tables are on printed page 371. Dividing Table 1 by Table 2, column
by column, against the stored 0.65, 1.3 and 0.42:

| Tissue | Sevoflurane | Isoflurane | Desflurane |
| --- | --- | --- | --- |
| Brain | +4.1% | +2.4% | −0.3% |
| Heart | +4.6% | +4.2% | −0.3% |
| Liver | +4.0% | +2.9% | −0.0% |
| Kidney | +4.3% | +1.8% | +1.3% |
| Muscle | +17.0% | +15.9% | +10.8% |
| Fat | +10.1% | +10.0% | +5.0% |

No column gives the old 4.9-9.4% range for all three agents. The four organ
columns agree within 2.4 percentage points for each agent, and the muscle and
fat columns lie above all of them. The paper's discussion gives no reason;
it notes only that muscle solubility rose with age (its Figure 2).
Each printed mean is rounded to two decimals, which can move a quotient by
up to 1.8% (desflurane kidney, 0.40 / 0.94). So the differences among the four
organ columns, and the sign of desflurane's gap, are within rounding, and the
document gives whole percents and states the 1.8%. Both blind review passes
found the 0.1% figures falsely precise. The muscle and fat columns lie above
every organ column by more than both roundings together, which the test
checks.
`docs/PARAMETERS.md` § "v0.2.0: isoflurane and desflurane" now states the
organ ranges and the muscle and fat figures, and
`test_yasudas_full_tables_recover_the_blood_gas_ranges_printed` computes them
from the tables transcribed with their page. The three agent files' notes and
`docs/MODEL.md` § "The agents" now point at that section
rather than restating a range. `docs/references/yasuda-1989-tissue-solubility.md`
is the paper's extraction note. No stored value changed.
Files checked: `docs/PARAMETERS.md`, `docs/MODEL.md`, `docs/INTERFACE.md`,
`docs/VERIFICATION.md` and the three agent files (`grep -rn "9.4 percent\|4.9"`
finds no other copy of the old range once `docs/MODEL.md`'s was replaced).
