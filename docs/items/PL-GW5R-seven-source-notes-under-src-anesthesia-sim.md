---
id: PL-GW5R
title: Seven source notes under src/anesthesia_sim/data/ still state what docs/MODEL.md corrected on 2026-11-21: four in reference_adult.json and the Mapleson note in each agent file
priority: P2
effort: S
status: done
classes: defect
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-21
pr: 2190
payoff: the source notes in the parameter files say what docs/MODEL.md says about which sources were read, the 3.30% figure and the roadmap item that moves the MAC
verify: grep -qF 'No planned milestone moves the MAC to a primary measurement' src/anesthesia_sim/data/agents/sevoflurane.json src/anesthesia_sim/data/agents/isoflurane.json src/anesthesia_sim/data/agents/desflurane.json
---

**Problem.** Seven source notes under src/anesthesia_sim/data/ still state what docs/MODEL.md corrected on 2026-11-21: four in reference_adult.json and the Mapleson note in each agent file

**Why it matters.** A `sources` note is the record that a reviewer reads to check a stored value. These seven say that sources are unread which were read, give a figure that the note's own numbers do not give, and name the wrong roadmap item. So the parameter files disagree with `docs/MODEL.md` about what the project has read and plans.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. `PL-RMNP` corrected the sentences in `docs/MODEL.md`. The `sources` notes in the data files state the same things, and a data file under `src/anesthesia_sim/data/` is outside what a session may fix in place.

**The notes, and what each should say.**

1. `patients/reference_adult.json`, the Zwart 1972 note: "the last of the four still unread". All four sources of Lowe and Ernst's compilation were read on 2026-09-10 (`docs/MODEL.md` § "Parameter provenance" records each reading).
2. The same file, the Lowe and Ernst note: "whose own four sources are unread". The same reading makes this false.
3. The same file, the Cattermole note: a weight-scaled cardiac output "3.32%" below the stored 5 L/min. The note's own figures give 5/4.84009 − 1 = 3.30%.
4. The same file, the De Wolf 2012 note: "the only reachable published statement" of the vessel-rich flow fraction. Weber et al. 2021, Table 2, prints 76.00%, and the same file's Weber note records that it was read on 2026-10-11.
5. `agents/sevoflurane.json`, `agents/isoflurane.json` and `agents/desflurane.json`, the Mapleson 1996 note: `ROADMAP.md` planned-milestone item 31 is "the route to primary values". Item 31 plans a primary-literature set of partition coefficients. Item 30 moves the MAC to Mapleson's age-40 values, which are tier 2, and no milestone plans a primary MAC. `PL-LBVN` (the default MAC moves to Mapleson's age-40 values) rewrites these three notes anyway, so correct them there if it comes first.

**Done when.** Each note agrees with `docs/MODEL.md`, and each touched note names its route and how deeply the source was read, as `.claude/rules/citing-sources.md` requires.

**What was done, 2026-11-21.** Each note keeps its route and its depth of reading, and none of the stored values changes.

1. The Zwart note now says that Lowe and Ernst's reference 9 was read in full text on 2026-09-10, and points to the Mapleson 1963 entry below it.
2. The Lowe and Ernst note now says "a compilation, not a measurement", as `docs/MODEL.md` § "Where each stored value comes from" does, and that the four sources were read on 2026-09-10 and are each entered as tier 2.
3. The Cattermole note now gives 3.30%. `5 / (0.2 × 70^0.75) − 1` is 0.03304.
4. The De Wolf note now says that it was the only reachable published statement until Weber et al. 2021's tables were read on 2026-10-11, and that Weber's Table 2 prints 76.00%.
5. The Mapleson 1996 note in each agent file now says that no planned milestone moves the MAC to a primary measurement, that `ROADMAP.md` planned-milestone item 30 moves it to Mapleson's age-40 values, and that item 31 plans a primary-literature set of partition coefficients. `ROADMAP.md` §§ "30. Patient factors" and "31. Primary-literature partition coefficients, selectable beside the Gas Man set" were read for this. These three notes named no route and no depth of reading. The PubMed record of the paper (PMID 8777094, doi:10.1093/bja/76.2.179) was retrieved on 2026-11-21, and its abstract gives the figures the notes state: MAC at age 40 of 1.17% for isoflurane, 1.80% for sevoflurane and 6.6% for desflurane, 95% confidence limits of about ±7% (±10% for desflurane), and about 6% per decade of age. Each note now ends "Retrieved from PubMed (PMID 8777094) and verified against the abstract 2026-11-21."
6. The second review pass found one more stale sentence in the De Wolf note. It said that "the Workbook entry above records that the product states no numeric default" for alveolar ventilation. The Workbook entry in the same file records `VA=4` from the Workbook's Appendix C, read on 2026-09-15, and `docs/MODEL.md` § "Parameter provenance" says that "alveolar ventilation is stated as a number". The note now says that Gas Man's defaults file, printed in the Workbook's Appendix C, states it as VA=4.

**Documents checked.** `docs/MODEL.md` §§ "Where each stored value comes from", "Delivery-limit and MAC parameters" and "Known limitations"; the `provenance_gap` of each agent file, which names item 31 for the coefficient set and is right; and a search of `docs/`, `README.md`, `src/` and `tests/` for each corrected phrase.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.
