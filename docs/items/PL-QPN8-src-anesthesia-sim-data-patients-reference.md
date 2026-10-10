---
id: PL-QPN8
title: src/anesthesia_sim/data/patients/reference_adult.json's Meybohm et al. 2021 note says its Tables 1-3 could not be read, but pmc.ncbi.nlm.nih.gov answered through the egress proxy on 2026-10-06, so read PMC7943506's tables and settle whether they list a blood or venous volume
status: untriaged
added: 2026-10-06
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
