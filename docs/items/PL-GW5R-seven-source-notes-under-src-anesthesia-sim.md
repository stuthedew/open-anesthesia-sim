---
id: PL-GW5R
title: Seven source notes under src/anesthesia_sim/data/ still state what docs/MODEL.md corrected on 2026-11-21: four in reference_adult.json and the Mapleson note in each agent file
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** Seven source notes under src/anesthesia_sim/data/ still state what docs/MODEL.md corrected on 2026-11-21: four in reference_adult.json and the Mapleson note in each agent file

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. `PL-RMNP` corrected the sentences in `docs/MODEL.md`. The `sources` notes in the data files state the same things, and a data file under `src/anesthesia_sim/data/` is outside what a session may fix in place.

**The notes, and what each should say.**

1. `patients/reference_adult.json`, the Zwart 1972 note: "the last of the four still unread". All four sources of Lowe and Ernst's compilation were read on 2026-09-10 (`docs/MODEL.md` § "Parameter provenance" records each reading).
2. The same file, the Lowe and Ernst note: "whose own four sources are unread". The same reading makes this false.
3. The same file, the Cattermole note: a weight-scaled cardiac output "3.32%" below the stored 5 L/min. The note's own figures give 5/4.84009 − 1 = 3.30%.
4. The same file, the De Wolf 2012 note: "the only reachable published statement" of the vessel-rich flow fraction. Weber et al. 2021, Table 2, prints 76.00%, and the same file's Weber note records that it was read on 2026-10-11.
5. `agents/sevoflurane.json`, `agents/isoflurane.json` and `agents/desflurane.json`, the Mapleson 1996 note: `ROADMAP.md` planned-milestone item 31 is "the route to primary values". Item 31 plans a primary-literature set of partition coefficients. Item 30 moves the MAC to Mapleson's age-40 values, which are tier 2, and no milestone plans a primary MAC. `PL-LBVN` (the default MAC moves to Mapleson's age-40 values) rewrites these three notes anyway, so correct them there if it comes first.

**Done when.** Each note agrees with `docs/MODEL.md`, and each touched note names its route and how deeply the source was read, as `.claude/rules/citing-sources.md` requires.
