---
id: PL-33FM
title: ROADMAP.md gives Gate 0's size as nine items, as twenty items deep and as 21 frozen entries
priority: P2
effort: S
status: done
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-10
pr: 2082
payoff: The case for the one versioning exception rests on Gate 0's whole content, stated once and matching its frozen list.
verify: ! grep -qF 'Gate 0 held two safety fixes, four refactors, two tooling defects' ROADMAP.md
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

**Why it matters.** § "Versioning decision" rests its one versioning exception on what Gate 0 held. A reader cannot tell whether the nine items it lists are the whole gate, so the case for the exception reads as resting on a sample.

**Done when.** § "Versioning decision" gives Gate 0's size once, as a count
that matches the frozen list recorded under v0.4.0, and the list of kinds says
which entries it covers.

**Generator check.** One query from one structure read. Nothing produces it,
so nothing is recorded as a generator. `docket new` matched this filing to
`PL-TW3Q`, which is v0.2.8's own count (38 entries against a size of 37), a
different list in a different release; that match is withdrawn.

**Checked 2026-11-09:** § "Versioning decision" still lists "two safety fixes, four refactors, two tooling defects and a performance fix" and says Gate 0 "was twenty items deep". v0.4.0's Gate 0 list says twenty debt items at the freeze (six inside v0.4.0's scope and fourteen outside), and 21 entries cleared before v0.4.0 began, which matches the timeline's 4 M and 17 S. Counting that list by class answers the question, so the fix is a session's and does not need the author.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. `ROADMAP.md` there already said Gate 0 held "two safety fixes, four refactors, two tooling defects and a perf fix" and "was twenty items deep", beside the timeline's 4 M and 17 S.

**Done 2026-11-10.** § "Versioning decision" now gives Gate 0's size once, as the 21 entries that v0.3.0 released, matching the frozen list under v0.4.0 and timeline row 2 (4 M, 17 S). Its list of kinds now covers all 21 by count, from the entries' titles: seven safety and science fixes (`PL-026`, `PL-042`, `PL-VP7N`, `PL-SLHS`, `PL-9Y42`, `PL-0MLQ`, `PL-NV9W`), four refactors (`PL-006`, `PL-004`, `PL-007`, `PL-019`), eight workflow and tooling fixes (`PL-G049`, `PL-674D`, `PL-0RFH`, `PL-R0SR`, `PL-4F6P`, `PL-N2N1`, `PL-K79K`, the `PL-Z4GF`/`PL-SWFM` entry), a performance fix (`PL-010`) and the choice of a licence (`PL-Y2GG`). The next paragraph's "twenty items deep" is gone. Twenty was the count at the freeze, 14 to clear first and 6 inside v0.4.0's scope, and it is a different number from the gate that v0.3.0 released.
