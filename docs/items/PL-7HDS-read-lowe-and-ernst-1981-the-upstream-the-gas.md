---
id: PL-7HDS
title: Read Lowe and Ernst 1981, the upstream the Gas Man Workbook names for its volume and flow values
priority: P1
effort: M
status: blocked
classes: science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
blocked-by: PL-XJ5P
added: 2026-09-06
---

**Problem.** The Gas Man Workbook's Model Parameters table (Appendix B, page
168), read at the source 2026-09-06, carries this note under it:

> Values for volume, flow and relative flow are taken from Lowe and Ernst, 1981

Its reference 23 is *Lowe HJ, Ernst EA. The Quantitative Practice of
Anesthesia: Use of Closed Circuit. Baltimore: Williams & Wilkins; 1981* - the
bibliography prints the first initial as `HF` there and as `HJ` at references
22 and 24, so the entry is internally inconsistent and `HJ` is the reading
taken.

That is the upstream for seven of this file's eleven stored values, and it has
not been read. Whether the book reports those volumes and flows as
measurements, derives them, or reproduces them from somewhere else again is
unknown.

**Why it matters.** This is the second link in the only provenance chain the
reference patient has, and it is the one that decides whether the chain ends in
a measurement or in another compilation. Until it is read, `docs/MODEL.md`'s
source hierarchy cannot place it: a monograph on closed-circuit practice could
be tier 1 for a value it measured, tier 2 for one it collected, and the file
must not guess which.

**This replaces a wrong guess, which is the reason to be careful with it.**
Until 2026-09-06 this file named Mapleson's 1963, 1964 and 1973 papers as "the
primary lineage" - on the strength of their titles, never having been opened.
`PL-6Q8N` removed that framing, and the Workbook turns out to attribute nothing
to Mapleson. Recording Lowe and Ernst as read, or as tier 1, before anybody has
opened it would be the identical error one citation later.

**Reachability, and why this is likely not delegable to a session.** A 1981
Williams & Wilkins monograph is outside every route
`.claude/rules/citing-sources.md` describes: not in PubMed Central, not a
journal article with a DOI, and the publisher domains are refused by the egress
proxy. Expect this to need the project owner's institutional or library access,
as the Workbook itself did. `PL-XJ5P` carries the general gap.

**Where.** `src/anesthesia_sim/data/patients/reference_adult.json` - the Lowe
and Ernst `sources` entry, which currently records the book as located and
unread; and `docs/MODEL.md` § "Parameter provenance".

**Done when.** The tier of Lowe and Ernst 1981 is established by someone who
has opened it, and for each of the seven values the book is credited with, the
file records whether the book measured it, collected it, or cites it onward -
or the file records that the book could not be reached and by whom it was
tried.

**Blocked on `PL-XJ5P`** (citing-sources says there is always a route, but a
pre-abstract subscription paper has none). Every route
`.claude/rules/citing-sources.md` describes has already been tried and refused
for this book, so the next step is not another attempt: it is the disposition
`PL-XJ5P` decides - whether an unreachable in-copyright source is put to the
project owner for their institutional access, carried as an owner-supplied
extract, or recorded as terminal. Which of those is chosen decides what closing
this item even looks like.

**A live session was working this item when the block was written, and the
block is a triage disposition rather than a claim on it.** `list_sessions`
2026-09-06: session `PL-7HDS`, branch `claude/pl-7hds-e170bx`, running and
searching for the book. Nothing was pushed, so no ref could show it and
`bin/docket show` reported the item startable. Whoever reaches the book first
should close this and take the block off `PL-3YZW` with it; the sequencing
above is what to do if nobody does.
