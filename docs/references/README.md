# Source documents held on hand

Full texts kept in the repository so a session can read the source rather than
recall it. **Being here promotes nothing.** `docs/MODEL.md` § "Source
hierarchy: what may be cited as the authority for a value" decides what may be
cited as the authority for a stored number, and a PDF sitting in this directory
is evidence a session can open, not a tier in that hierarchy. Cite the work,
never the file path.

## Redistribution

Both files are publisher-copyright works held under the personal access of the
project owner. This repository is **private**, which is what makes that
ordinary personal use rather than redistribution.

**They must come out before this repository is ever made public**, and taking
them out means rewriting history — a `git filter-repo` pass and a force-push,
not a delete commit — because both blobs are in the history from the commit
that adds them. Anyone weighing a change to repository visibility should treat
this as a prerequisite rather than a follow-up. The citations below are the
part that survives such a removal, which is why they are recorded in full here
and not left implicit in the filenames.

## The documents

### Baker & Farmery 2011 — inert gas transport in blood and tissues

`baker-farmery-2011-inert-gas-transport-in-blood-and-tissues.pdf`

> Baker AB, Farmery AD. Inert gas transport in blood and tissues.
> *Comprehensive Physiology*. 2011 Apr;1(2):569–92.
> DOI [10.1002/cphy.c100011](https://doi.org/10.1002/cphy.c100011).
> PMID [23737195](https://pubmed.ncbi.nlm.nih.gov/23737195/).

Metadata confirmed against PubMed. The file's own XMP packet carries Wiley's
legacy identifier for the same article, `10.1002/j.2040-4603.2011.tb00337.x`;
both resolve, and the DOI above is the one to cite.

This is the closest published statement of what `docs/MODEL.md` specifies. It
derives single-compartment and multicompartment models of inert gas transfer,
develops transport between lungs, blood and other tissues from them, and
compares the result against experimental studies in animals and humans — then
treats the anesthetic gases specifically, deriving how transfer depends on
solubility in blood and in each tissue. Read it when a compartment structure,
a governing equation, or a solubility-driven assumption in `docs/MODEL.md` is
being questioned or extended.

### Schüttler & Schwilden 2008 — *Modern Anesthetics*

`schuttler-schwilden-2008-modern-anesthetics-hep-182.pdf`

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
