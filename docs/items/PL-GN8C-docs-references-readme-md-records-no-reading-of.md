---
id: PL-GN8C
title: docs/references/README.md records no reading of Lowe and Ernst 1981, and the interlibrary-loan route that reached it is the answer PL-XJ5P is looking for
status: untriaged
added: 2026-09-08
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

**Sequencing.** `PL-XJ5P` is `needs-decision` and touches the same file; if it
is answered first, this becomes part of its answer rather than a separate edit.

