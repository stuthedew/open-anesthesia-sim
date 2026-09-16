---
id: PL-GN8C
title: docs/references/README.md records no reading of Lowe and Ernst 1981, and the interlibrary-loan route that reached it is the answer PL-XJ5P is looking for
priority: P2
effort: S
status: done
classes: docs
feature: provenance
touches: docs/references/README.md
added: 2026-09-08
closed: 2026-09-16
pr: 612
verify: python3 tools/doc_check.py check && grep -q '^### Lowe' docs/references/README.md
---

**Problem.** docs/references/README.md records no reading of Lowe and Ernst 1981, and the interlibrary-loan route that reached it is the answer PL-XJ5P is looking for (`PL-7HDS`, 2026-09-08).

`docs/references/README.md` is where this project records "the citations for
sources this repository may not carry" - its own words - and it carries entries
for Baker & Farmery and Schuttler & Schwilden on exactly that basis, both
removed as publisher-copyright material and both recorded so that a reader can
reach them by DOI. Lowe and Ernst 1981 is now in the same class and has no
entry: it was read at the source on 2026-09-08 from an interlibrary-loan scan,
it cannot be held here, and the only record of the reading is inside
`reference_adult.json`'s `sources`, where a reader looking for "what has been
read and how" will not think to look.

**The route is the more valuable half.** `PL-XJ5P` (citing-sources says there
is always a route, but a pre-abstract subscription paper has none) is open on
exactly the gap this filled: `.claude/rules/citing-sources.md` names the PubMed
MCP server as the route and it does not index monographs, while
`docs/references/` can no longer hold an in-copyright full text. What actually
worked was a third route neither document describes - an interlibrary loan
placed by the project owner through a university library (RapidILL; lender
University of Sydney Main Library, borrower University of Wisconsin-Madison
Memorial Library), returning a page range narrowed in advance by two
second-hand readings, delivered as a scan the session reads and the repository
never holds.

**Why it matters.** That is a repeatable procedure with a demonstrated success,
and it is currently recorded nowhere a session would find it. The next session
that meets an unreachable monograph will re-derive "ask the owner" without
knowing that narrowing the request to two page numbers is what made it cheap
enough to place.

**Approach.** One entry in `docs/references/README.md` under "The documents",
in the shape the two removed full texts already use: the citation, "Not held
here" with the reason, and what the document establishes. Plus a sentence in
the same file's "Redistribution" section, or wherever `PL-XJ5P` decides such
routes belong, recording interlibrary loan as a route and what makes a request
placeable.



**Done when.** `docs/references/README.md` carries an entry for Lowe and Ernst
1981 under "The documents", in the shape the two removed full texts use - the
citation, "Not held here" with the reason, and what the document establishes -
and the interlibrary-loan route is recorded as a route, with the detail that
makes it repeatable: that narrowing the request to a page range identified in
advance is what made it cheap enough to place.

**`PL-XJ5P` answered first, and took the larger half with it (2026-09-16,
found by `PL-3SQT`).** Both sequencing paragraphs here said to wait on it as
`needs-decision`; it closed `done` in v0.4.19. Its answer is where the
interlibrary-loan route now lives - `.claude/rules/citing-sources.md` tells a
session to "put the reading to the project owner, who has institutional access
and has turned interlibrary loans around inside a day **when the request named
the pages it needed**", which is exactly the detail this brief asked to have
preserved. So the route half is done and is not this item's any more.

**What is left is the entry**, and only that: one `### Lowe & Ernst 1981`
section under "The documents", in the shape `### Baker & Farmery 2011` and
`### Schüttler & Schwilden 2008` already use. The reading itself is not in
question - `reference_adult.json`'s `sources[1]` carries the citation with
chapters, page ranges, ISBN and OCLC, both RapidILL instalments, and the tier-2
cited-but-not-adopted verdict. What is missing is that none of it is in the
file whose job is to list the sources this repository may not carry, so a
reader asking "what has been read, and how" does not find it.

**`verify:` rewritten 2026-09-16, and the old one is why `main` was red.** It
read `grep -q 'Lowe and Ernst' docs/references/README.md`, and that file
already matches at line 236 - inside the Gas Man Workbook entry, in a sentence
about *that* document's bibliography being internally inconsistent ("Its
reference 23 is Lowe and Ernst 1981, printed with the initial 'HF' there and
'HJ' at references 22 and 24"). So the command passed before any work was
done, which is the second of the two causes `docket check --verify` names, and
`bin/docket check --verify` on `main` failed on it. It now greps for the
heading only this item's work creates. Run on the pre-work tree: exit 1.

**Closed 2026-09-16.** `docs/references/README.md` carries
`### Lowe & Ernst 1981 — *The Quantitative Practice of Anesthesia*` under "The
documents", between the Jugel and Philip entries, in the shape
`### Baker & Farmery 2011` uses: **Not held here** with the reason, the
citation with ISBN and OCLC rather than a DOI it does not have, and what the
document establishes.

**The route half was not written here**, because `PL-XJ5P` had already written
it — the rider above records that. What this entry does carry is the one thing
only it can: that the route *used for this document* was interlibrary loan,
with both instalments' page ranges, dates, lenders and item ids, so the record
of the reading sits in the file whose job is to hold it rather than only
inside a JSON data file.

**Four findings are summarised rather than reproduced**, with the data file
named as the record: the model patient is 100 kg and not 70, which is why the
material arrives as fractions; the book cites its values onward and measures
nothing, so the tier is 2 and cannot become 1; the vessel-rich pair reproduces
exactly and uniquely while muscle and fat reproduce under no grouping of the
book's ten compartments at all; and `0.2 x M^(3/4)` is Brody's interspecies
metabolic allometry over an assumed constant arteriovenous oxygen difference,
so 4.84 L/min at 70 kg is not a measured human cardiac output. An entry that
restated the whole `sources[1]` note would be a second copy to keep true.

**Landed in two changes on purpose.** The `verify:` rewrite went first and
alone, because the old command was holding `main` red and this prose wanted
the project owner's eye; this is the second.
