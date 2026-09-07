---
id: PL-S3Q0
title: Two paraphrases of the tier-2 absolute survived PL-FJGY's sweep, in docs/MODEL.md's Kharasch note and reference_adult.json's Frayn and Karpe note
status: untriaged
added: 2026-09-07
---

**Problem.** Two paraphrases of the tier-2 absolute survived PL-FJGY's sweep, in docs/MODEL.md's Kharasch note and reference_adult.json's Frayn and Karpe note

**Where.** Both say a tier-2 source may never be the authority for a stored
value, which `PL-FJGY` replaced everywhere it found it on 2026-09-07:

- `docs/MODEL.md`, the Kharasch note under the 24-hour boundary (around line
  2786): "It is a review, so under \"Source hierarchy\" it may not be the
  authority for a stored value - and it is not one".
- `src/anesthesia_sim/data/patients/reference_adult.json`, the Frayn and Karpe
  entry: "A review measures nothing and cannot be the authority for a stored
  value".

**Why they survived.** The sweep matched two exact phrases - "does not admit
tier 2 as the authority" and "admits only tier 1 as the authority" - and these
two are paraphrases. That is the general shape of the defect rather than an
oversight: a rule restated in N places is repaired by searching for the words
it was last written in, and every paraphrase is invisible to that search.

**Smaller than the tier-3 case, and worth saying why.** Neither is
load-bearing. Both continue into a correct statement that the source is not
adopted and nothing is stored from it, so no provenance claim in the tree is
wrong because of them; what is wrong is the rule they assert on the way past.
Davis and Mapleson 1981 is a tier-2 source this project has adopted, so the
assertion is now false as written and a session copying either phrasing into a
new note would propagate it.

**Found.** `PL-X19T` (align the tier-3 absolute in the instruction files with
the practice), 2026-09-07, sweeping for restatements of both absolutes rather
than only the tier-3 one. Not fixed there: both files are outside that item's
`touches`, and the data file is `science`-classed.
