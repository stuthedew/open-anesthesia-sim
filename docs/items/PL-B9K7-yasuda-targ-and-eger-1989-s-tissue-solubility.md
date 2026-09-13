---
id: PL-B9K7
title: Yasuda, Targ and Eger 1989's tissue-solubility full text is the one document that could confirm or refute the Workbook's attribution of the twelve coefficients, and neither PubMed Central nor the reference corpus holds it
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md
added: 2026-09-13
closed: 2026-09-13
verify: python3 tools/doc_check.py check && grep -q 'Table 1' src/anesthesia_sim/data/agents/sevoflurane.json
---

**Problem, as filed.** `PL-ZP7Z` established that the Gas Man Workbook claims
its volatile partition coefficients are Yasuda, Targ and Eger's, and could not
check the claim: the stored coefficients are tissue:**gas**, the only reachable
form of the paper was its abstract, and an abstract reports tissue:**blood**
only. The full text was in neither PubMed Central nor the reference corpus.

**Closed 2026-09-13. The project owner supplied the full text and the claim
holds.** Yasuda N, Targ AG, Eger EI II. *Solubility of I-653, sevoflurane,
isoflurane, and halothane in human tissues.* Anesth Analg 1989 Sep;69(3):370-3,
PMID 2774233. Now in the private reference corpus, with the whole of Table 1 in
its README entry so a later session need not reopen the PDF. Read at full text
the same day. (The circuit companion had arrived first by mistake; what that one
opened is `PL-LS3H`, `PL-QBKQ`, `PL-XWCY` and `PL-8GJ6`.)

**The comparison.** Table 1 is tissue:gas, from 14 autopsy specimens, 6-10 per
tissue, mean age 65.8 +/- 14.4 yr, 1.5-2 h equilibration at 37 C, duplicates
discarded above 10 percent deviation. Against the nine stored values:

| agent | vessel-rich (Yasuda brain) | muscle | fat |
| --- | ---: | ---: | ---: |
| sevoflurane | 1.1 vs 1.15 +/- 0.07 (-0.71 SD) | 2.4 vs 2.38 +/- 1.03 (+0.02 SD) | 34.0 vs 34.0 +/- 6.0 (exact) |
| isoflurane | 2.1 vs 2.09 +/- 0.10 (+0.10 SD) | 4.5 vs 4.40 +/- 1.97 (+0.05 SD) | 70.0 vs 64.2 +/- 12.3 (+0.47 SD) |
| desflurane | 0.54 vs 0.54 +/- 0.02 (exact) | 0.97 vs 0.94 +/- 0.35 (+0.09 SD) | 13.0 vs 12.0 +/- 2.0 (+0.50 SD) |

All nine within 0.71 SD; three reproduce the measurement to the stored
precision. A parameter set assembled from anywhere else does not do that. The
Workbook's self-contradiction for sevoflurane - Yasuda in one sentence, "the
package insert and Abbott data" in the next - resolves in Yasuda's favour on the
same arithmetic.

**Two findings that are not about provenance, and are recorded in the files.**
The vessel-rich coefficient is Yasuda's **brain** value rather than a weighted
vessel-rich group: Table 1 measures brain, heart, liver and kidney separately
(sevoflurane 1.15, 1.21, 1.25, 0.78) and no weighting of the four lands where
the stored figures land, so a learner reading the vessel-rich trace is reading a
brain trace. And this paper is **not** a source for the stored blood:gas values
- it measured none, and its Table 2 tissue:blood figures are calculated by
dividing Table 1 by published age-adjusted blood:gas, which recovers 4.9 to 9.4
percent above the three round figures stored here.

**What is recorded and what is not.** The three agent files' Yasuda entries and
`docs/MODEL.md` now carry the comparison, the brain finding and the blood:gas
exclusion. **No tier, no `adopted` flag and no stored value was changed**, and
`PL-FN5F` carries the decision that would change them.

**Done when.** The three agent files and `docs/MODEL.md` record what the full
text says about the stored coefficients, with the per-agent deviations; the
tier decision is put to the project owner rather than taken. Both done.
