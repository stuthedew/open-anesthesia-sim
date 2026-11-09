---
id: PL-33FM
title: ROADMAP.md gives Gate 0's size as nine items, as twenty items deep and as 21 frozen entries
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
recurrences: 2026-11-07 PL-PNH2 withdrawn 2026-11-07 PL-PNH2
---

**Problem.** `ROADMAP.md` gives Gate 0's size three ways. § "Versioning
decision" lists what Gate 0 held as "two safety fixes, four refactors, two
tooling defects and a performance fix", which is nine items, and then says it
"was twenty items deep". The timeline's v0.3.0 row gives its size as 4 M and
17 S, which is 21, and the v0.4.0 section's Gate 0 list and the v0.4.x
timeline cell's moved text speak of "Gate 0's 21". A reader cannot tell
whether the nine are the whole gate, the part released as v0.3.0, or a sample
of it.

Chapter read 2 of the structure read (`PL-DWGC`, rows 21, 29, 50, 55 and 66 at
`aff76df1`) raised it as a query. The tree does not settle which count the
nine-item list means, so it needs the author's answer, or a count of v0.4.0's
Gate 0 list by kind.

**Done when.** § "Versioning decision" gives Gate 0's size once, as a count
that matches the frozen list recorded under v0.4.0, and the list of kinds says
which entries it covers.

**Generator check.** One query from one structure read. Nothing produces it,
so nothing is recorded as a generator. `docket new` matched this filing to
`PL-TW3Q`, which is v0.2.8's own count (38 entries against a size of 37), a
different list in a different release; that match is withdrawn.
