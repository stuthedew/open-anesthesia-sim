---
id: PL-QPN8
title: src/anesthesia_sim/data/patients/reference_adult.json's Meybohm et al. 2021 note says its Tables 1-3 could not be read, but pmc.ncbi.nlm.nih.gov answered through the egress proxy on 2026-10-06, so read PMC7943506's tables and settle whether they list a blood or venous volume
priority: P1
effort: S
status: done
classes: science, docs
touches: src/anesthesia_sim/data/patients/reference_adult.json
added: 2026-10-06
closed: 2026-10-11
pr: 1424
payoff: the stored venous pool's provenance note says what its source's tables actually list, instead of recording a gap that no longer has to exist
verify: ! grep -qF 'Tables 1-3 could not be retrieved' src/anesthesia_sim/data/patients/reference_adult.json
---

**Problem.** src/anesthesia_sim/data/patients/reference_adult.json's Meybohm et al. 2021 note says its Tables 1-3 could not be read, but pmc.ncbi.nlm.nih.gov answered through the egress proxy on 2026-10-06, so read PMC7943506's tables and settle whether they list a blood or venous volume

**Found 2026-10-06** while closing `PL-CLW5`, whose probe that day had
`pmc.ncbi.nlm.nih.gov` answer 200 at the CONNECT and 200 from the host. The
note's sentence about the refusal now carries its 2026-09-07 date and a line
saying the tables can be read at the source; what it still cannot say is
whether they list a venous or blood volume, which is the question the note
was written to answer (`PL-0NQ1`, `PL-XJ5P`). Reading the tables either closes
that gap or names a value, and the second would be a provenance finding for
the stored venous pool.

**Re-confirmed 2026-10-11:** `https://pmc.ncbi.nlm.nih.gov/articles/PMC7943506/`
answered 200 from this container, so the tables can be read at the source.

**Why it matters.** The stored venous pool's provenance rests partly on what this
paper's model description does or does not list. If its tables name a blood or
venous volume, the stored value has a source the note does not cite, or a
disagreement it does not record; if they do not, the note can say so instead of
saying the tables were never read. Either way the note stops recording a gap that
no longer has to exist.

**Done when.** Tables 1-3 of PMC7943506 have been read, and the note in
`reference_adult.json` says, dated, whether they list a blood or venous volume
and what it is; a value that disagrees with the stored one is filed as its own
item rather than changed here.
