---
id: PL-7KDC
title: docs/MODEL.md's 'Where this project stands' paragraph still says all eleven reference-patient parameters are the Gas Man default patient and 26 of 29 rows are tier 3, though PL-8ZJQ moved venous_pool_volume_l to a tier-2 source
status: untriaged
added: 2026-09-07
---

**Problem.** docs/MODEL.md's 'Where this project stands' paragraph still says all eleven reference-patient parameters are the Gas Man default patient and 26 of 29 rows are tier 3, though PL-8ZJQ moved venous_pool_volume_l to a tier-2 source

**Where.** `docs/MODEL.md` § "Source hierarchy", the paragraph headed "Where
this project stands, stated rather than implied" (around line 1261). Two
claims in it:

- "all eleven physiologic parameters in
  `src/anesthesia_sim/data/patients/reference_adult.json` are the Gas Man
  default patient". The file's own `provenance_gap` says ten are, and that
  "the eleventh, `venous_pool_volume_l`, is Davis and Mapleson 1981, adopted
  2026-09-07 on the project owner's decision (`PL-8ZJQ`) and tier 2".
- "Of the 29 rows in the provenance table below, 26 are tier 3." By the same
  adoption one of those 26 is now tier 2, so the count wants recomputing
  against the table rather than adjusting by one on this note's arithmetic.

**Why it survived.** `PL-8ZJQ` changed the parameter's source and `PL-FJGY`
rewrote the section's rules, and neither pass reached the paragraph that
counts what the rules apply to. The sentence immediately below it - the file
"still adopts no primary source for any of its eleven parameters" - is correct,
which is what makes the stale one easy to read past.

**Consequence.** It is the paragraph a reader consults for what the shipped
parameter set rests on, so it is the one place a wrong tier claim reaches
somebody deciding whether to trust a displayed value. Nothing computed reads
it; `check_provenance` decides that a documented key holds the stated value,
never what tier its source carries. `PL-9LXK` is the mechanized answer to that
class.

**Found.** `PL-X19T` (align the tier-3 absolute in the instruction files with
the practice), 2026-09-07, while verifying the counts before restating them.
Not fixed there: `docs/MODEL.md` is outside that item's `touches` and this is
`science`-classed work in the authoritative specification.
