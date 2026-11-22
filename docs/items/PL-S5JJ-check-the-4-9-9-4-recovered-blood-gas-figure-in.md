---
id: PL-S5JJ
title: Check the 4.9-9.4% recovered blood:gas figure in docs/PARAMETERS.md and the agent files against Yasuda 1989 Table 2: the brain column gives +4.1, +2.4 and -0.3%
status: untriaged
feature: model-claims-held-by-tests
touches: docs/PARAMETERS.md, src/anesthesia_sim/data/agents
added: 2026-11-22
---

**Problem.** `docs/PARAMETERS.md` § "v0.2.0: isoflurane and desflurane" says that dividing Yasuda, Targ and Eger's Table 1 by their Table 2 recovers the age-adjusted blood:gas coefficient of their 65.8-year-old cohort, and that these recovered values are 4.9–9.4% above the three stored blood:gas coefficients. The sevoflurane, isoflurane and desflurane agent files carry the same sentence. No test computes it, because neither table's full set of figures is in the repository.

The figures that can be read do not give that range. The paper's abstract (*Anesth Analg* 1989;69(3):370-3, PMID 2774233, read on PubMed on 2026-11-22) gives the brain:blood coefficients, which are Table 2's brain column: sevoflurane 1.70, isoflurane 1.57 and desflurane 1.29. The brain tissue:gas coefficients that `docs/PARAMETERS.md` quotes from Table 1 are 1.15, 2.09 and 0.54. Dividing gives 0.676, 1.331 and 0.419, which are 4.1% and 2.4% above, and 0.3% below, the stored 0.65, 1.3 and 0.42. The other tissues may give other ratios, because a table of per-subject ratios need not divide exactly, but that cannot be checked without the full tables.

**Why it matters.** The sentence is part of the case for why the stored blood:gas coefficients are not Yasuda's. A wrong range there misstates how far the stored values sit from what this cohort implies.

**Done when.** Someone with the full text of Yasuda et al. 1989 (the references corpus holds it, according to the agent files) has recomputed the range from both tables, the documents and agent files state the computed range, and a test computes it from the tables transcribed with their page.

Found 2026-11-22 by the `PL-5C1H` pass. That pass replaced the range in `docs/PARAMETERS.md` with the brain column's figures, which a test computes, and declared the other tissues as having no test yet against this item. The agent files' notes still carry the 4.9–9.4% sentence, and this item corrects them too.
