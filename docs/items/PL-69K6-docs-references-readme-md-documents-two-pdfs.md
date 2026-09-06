---
id: PL-69K6
status: untriaged
added: 2026-09-06
title: docs/references/README.md documents two PDFs the copyright purge removed, and doc_check does not verify that a documented reference file exists
touches: docs/references, tools/doc_check.py
---

**Problem.** The 2026-09-06 history rewrite removed
`baker-farmery-2011-inert-gas-transport-in-blood-and-tissues.pdf` and
`schuttler-schwilden-2008-modern-anesthetics-hep-182.pdf` from the repository.
`docs/references/README.md` still carries a full entry for each - filename,
citation block and provenance note - at lines 35-39 and 57-61 on `origin/main`,
and a later paragraph still contrasts a third entry against "the Baker &
Farmery entry, whose metadata was confirmed against PubMed". A reader is told
the repository holds two files it does not.

**Why it matters.** `CLAUDE.md` treats stale documentation as a safety issue
rather than tidiness, and this is the sharper form of it: the README is the
provenance record for the model's own sources. A reader following it to check
where a coefficient came from finds nothing, and cannot tell whether the file
was removed deliberately, was never there, or is missing by accident. That is
exactly the question a provenance record exists to answer.

It also leaves the purge half-finished. Removing the files was the copyright
remedy `PL-SHG5` asked for; leaving entries that name them keeps the
repository asserting, in prose, that it distributes them.

**The check gap, which is the more durable half.** `make check` passes on this
state. `tools/doc_check.py` decides the package map, the provenance table,
dangling citations, marked prose values, math rendering and the release train,
and it verifies that a cited *path* exists elsewhere in the tree - but nothing
verifies that a file named in `docs/references/README.md` is present in
`docs/references/`. That is squarely the decidable half `CLAUDE.md` asks to be
put in code: whether a named file exists is answerable by reading the tree, and
the judgment half - whether the entry should be deleted or the file restored -
stays with a person.

**Also unresolved, and deliberately not assumed here.** One PDF remains:
`jugel-2014-m4-visualization-oriented-time-series-aggregation.pdf`, a
*Proceedings of the VLDB Endowment* paper. `PL-SHG5` named only the two
physiology texts, and the README's entry for this one records no licence or
redistribution basis - it asserts only that its metadata came from the paper's
own title page. Whether PVLDB's terms for volume 7 permit redistribution is a
question for the primary source, not for memory, and it is not answered here.

**Where.** `docs/references/README.md` - the Baker & Farmery entry, the
Schüttler & Schwilden entry, and the sentence under the Jugel entry that
refers back to Baker & Farmery. `tools/doc_check.py`, for the new check.

**Done when.** The README describes only files the repository actually holds,
and `doc_check` fails when it names one that is absent - so the next removal
cannot leave the provenance record asserting something untrue.
