# Source documents held on hand

The sources this project reads from, with the full text kept in the repository
where its licence permits, so a session can read the source rather than recall
it. **Being here promotes nothing.** `docs/MODEL.md` § "Source
hierarchy: what may be cited as the authority for a value" decides what may be
cited as the authority for a stored number, and a PDF sitting in this directory
is evidence a session can open, not a tier in that hierarchy. Cite the work,
never the file path.

## Redistribution

**The files here are not under one licence, and the difference decided what
had to happen before this repository went public.**

The two physiology sources were publisher-copyright works held under the
personal access of the project owner, which was ordinary personal use only
while this repository was private.

It is now public, and **both were removed on 2026-09-06** — by a
`git filter-repo` pass and a force-push rather than a delete commit, because
both blobs were in the history from the commit that added them. Their entries
below keep the full citation and no longer name a file: **citing a work is not
redistributing it**, and the citations were recorded in full here precisely so
that they would survive the removal. Cite either freely; neither full text is
held.

The M4 paper is different and does **not** join that set: VLDB publishes it
under Creative Commons Attribution-NonCommercial-NoDerivs 3.0, stated on the
paper's own first page, so keeping it here is redistribution the licence
already permits. Check a new file's own licence before adding it rather than
assuming this directory has one policy.

## The documents

### Baker & Farmery 2011 — inert gas transport in blood and tissues

*Full text not held here* — publisher copyright, removed 2026-09-06. Cite the
work below.

> Baker AB, Farmery AD. Inert gas transport in blood and tissues.
> *Comprehensive Physiology*. 2011 Apr;1(2):569–92.
> DOI [10.1002/cphy.c100011](https://doi.org/10.1002/cphy.c100011).
> PMID [23737195](https://pubmed.ncbi.nlm.nih.gov/23737195/).

Metadata confirmed against PubMed while the file was held. Its XMP packet
carried Wiley's legacy identifier for the same article,
`10.1002/j.2040-4603.2011.tb00337.x`; both resolve, and the DOI above is the
one to cite.

This is the closest published statement of what `docs/MODEL.md` specifies. It
derives single-compartment and multicompartment models of inert gas transfer,
develops transport between lungs, blood and other tissues from them, and
compares the result against experimental studies in animals and humans — then
treats the anesthetic gases specifically, deriving how transfer depends on
solubility in blood and in each tissue. Read it when a compartment structure,
a governing equation, or a solubility-driven assumption in `docs/MODEL.md` is
being questioned or extended.

### Schüttler & Schwilden 2008 — *Modern Anesthetics*

*Full text not held here* — publisher copyright, removed 2026-09-06. Cite the
chapter, per the note below.

> Schüttler J, Schwilden H, editors. *Modern Anesthetics*. Handbook of
> Experimental Pharmacology, vol. 182. Berlin, Heidelberg: Springer; 2008.
> DOI [10.1007/978-3-540-74806-9](https://doi.org/10.1007/978-3-540-74806-9).

The whole volume, 497 pages. It reaches well beyond what the simulator models
today, and the project owner's note on the branch this arrived from
(`556d454`, 2026-08-25) is why it was kept: *"lots of relevant stuff in article
on anesthesia considerations for down the road plans like implementing IV and
anesthetic depth"*.

Those are already on the map rather than being new scope — `ROADMAP.md`'s
"Planned milestones" items 13 (IV pharmacokinetic and effect-site models) and
14 (a modular hypnosis/eBIS effect model). This is a starting point for
sourcing when either is promoted into a scoped milestone, and not a source that
has been read and checked yet. A chapter in an edited volume is cited as that
chapter with its own authors, never as the volume.

### Jugel et al. 2014 — M4 time series aggregation

`jugel-2014-m4-visualization-oriented-time-series-aggregation.pdf`

> Jugel U, Jerzak Z, Hackenbroich G, Markl V. M4: A Visualization-Oriented
> Time Series Data Aggregation. *Proceedings of the VLDB Endowment*.
> 2014;7(10):797–808. ISSN 2150-8097.

Every field above is taken from the paper's own title page and running
footer, which is all this entry asserts. **No DOI is recorded, deliberately.**
Unlike the Baker & Farmery entry, whose metadata was confirmed against PubMed,
nothing here could be checked against a registry: `www.vldb.org` and `doi.org`
are both blocked by the session egress proxy, and the PDF prints no DOI of its
own — only the ISSN and the copyright line. A remembered DOI written down
becomes a fact by tomorrow, so it was left out. A session that can reach a
registry should confirm the record and add one.

Licensed by the publisher under
[CC BY-NC-ND 3.0](http://creativecommons.org/licenses/by-nc-nd/3.0/), per the
statement on its first page — the one file here that may stay if this
repository is ever made public.

Supplied by the project owner, 2026-09-04, after `www.vldb.org` proved
unreachable from a session. It is the authority for what the chart may claim
when it cannot draw every recorded sample, and `PL-D9WD` (build an M4
aggregate cache on a fixed dyadic grid) is written against it rather than
against a summary of it.

Three parts carry that weight. Definition 2 fixes what M4 selects per group —
the tuples at `min(v)`, `max(v)`, `min(t)` and `max(t)`. Theorem 1 proves
`vis_wh(G_M4(T)) = vis_wh(T)`, that a two-colour line visualization of the
reduced series equals that of the full one. And §6 states the condition that
guarantee depends on: exactness holds at `nh = k·w` for integer `k`, so the
bucket count must be an integer multiple of the pixel-column count and not
merely finer than it — which is the sentence to reread before anyone claims
this simulator's chart is provably exact, because its grid is anchored to
absolute sample index instead and therefore is not.

§4.3's error taxonomy for min/max-only aggregation matters for the same
reason: E1 and E2 are driven by gaps in the time distribution, and this
simulator samples at a fixed step with no gaps, so only E3 can occur here.
