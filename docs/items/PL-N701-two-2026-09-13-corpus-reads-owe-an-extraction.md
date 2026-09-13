---
id: PL-N701
title: Two 2026-09-13 corpus reads owe an extraction note under docs/references/README.md, once PL-Z3V5 settles what one contains
status: untriaged
added: 2026-09-13
---

**Problem.** `docs/references/README.md` states the obligation: "Reading a
source from the corpus therefore owes an extraction note in this directory.
Without one the corpus is consulted once per *session* instead of once per
*source*, and each later session re-reads the same PDF at full context." Two
corpus reads on 2026-09-13 owe one, and neither has been written.

- **Yasuda et al. 1991**, *Comparison of kinetics of sevoflurane and isoflurane
  in humans*, Anesth Analg 1991;72:316-24, PMID 1994760. Read for `PL-ZP7Z`.
  What was taken: its Methods cite the 1989 tissue paper as the source of both
  "the tissue/blood partition coefficient (which we determined previously)" and
  "the tissue/gas partition coefficient", which is what establishes that the
  1989 full text carries the quantity this project stores. Also Table 5's
  estimated blood flows and tissue volumes, unused so far.
- **Targ, Yasuda & Eger 1989**, the circuit-solubility companion paper, Anesth
  Analg 1989;69(2):218-25, PMID 2764290. Supplied by the project owner
  2026-09-13 and read the same day. What was taken is in `PL-LS3H`, `PL-QBKQ`,
  `PL-XWCY` and `PL-8GJ6`; the corpus's own README entry carries the summary.

**Why this is not already done.** `PL-Z3V5` owns what an extraction note
contains and has not run, and writing four notes in an invented shape would
settle that question by default rather than by decision. The facts themselves
are not at risk - they are in the four items above, in the agent data files,
and in the corpus README - so what is missing is discoverability from the public
repository, not the readings.

**Done when.** `PL-Z3V5` has fixed the note's shape and both reads have one; or
this item records that the corpus README entry is sufficient and the public-side
note is dropped, with the reasoning.
