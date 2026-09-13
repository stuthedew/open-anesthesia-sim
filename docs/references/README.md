# Source documents held on hand

Full texts kept in the repository so a session can read the source rather than
recall it, and the citations for sources this repository may not carry.
**Being here promotes nothing.** `docs/MODEL.md` § "Source
hierarchy: what may be cited as the authority for a value" decides what may be
cited as the authority for a stored number, and a PDF sitting in this directory
is evidence a session can open, not a tier in that hierarchy. Cite the work,
never the file path.

## Redistribution

**This repository is public.** A file here is therefore redistributed to
anyone, and the only files that may sit in this directory are ones whose own
licence permits that. Check a new file's licence before adding it; there is no
directory-wide policy to inherit, and "the repository is private" is no longer
available as the thing that makes personal use lawful.

**This directory currently holds no full texts**, only the records below.
The one it did hold - VLDB's M4 aggregation paper, redistributable under
CC BY-NC-ND 3.0 - was removed with the code that cited it (`PL-8LXM`,
2026-09-08): this directory holds papers the code is founded on, and a paper
nothing founds is a question a reader has to answer (project owner,
2026-09-05).

**Two publisher-copyright full texts were removed on 2026-09-06**, by the
`git filter-repo` pass and force-push this section used to name as a
prerequisite. They were kept here under the project owner's personal access
while the repository was private; that stopped being the situation when
`PL-XYRN` opened the go-public gate, and the removal did not happen with it.
`PL-SHG5` carries what went wrong, what was rewritten, and what remains.

Their entries stay below, without the files. The citations were always the
part designed to survive such a removal, which is why they are recorded here
in full rather than left implicit in the filenames — a reader who needs one of
those sources can now reach it the way any other reader would, through the DOI.

## Where owner-supplied full texts live now

**A private companion repository: `stuthedew/open-anesthesia-sim-references`**
(`PL-XJ5P`, decided by the project owner 2026-09-13). The rule above closed the
only home this directory had for a source the project cannot otherwise reach,
and put nothing in its place; this is what now stands there.

It is *private*, which restores the premise the removed entries used to rest on
— holding a publisher-copyright full text for personal use is not
redistribution — without reopening it for this public repository. **Nothing
about the rule above changes.** No publisher-copyright file may sit in this
directory, and nothing is to be copied from the corpus into this repository.

**What may cross back, and why it is a different act.** The citation, and the
*facts* taken from the source: a value, its units, the table or page it sits on,
what was measured and in what population. Facts are not copyrightable in the
United States — *Feist Publications, Inc. v. Rural Telephone Service Co.*,
499 U.S. 340, 344–45 (1991), holding that "facts are not copyrightable" and
that copyright in a factual compilation is "thin", protecting only original
selection and arrangement. Short quotation for scholarly commentary is
separately supported by 17 U.S.C. § 107. Reproducing a table wholesale in its
published arrangement is neither of those things, and is not needed.

This is what the section above already says about citations — "the citations
were always the part designed to survive such a removal" — extended from the
citation to the numbers taken under it.

**Reading a source from the corpus therefore owes an extraction note in this
directory.** Without one the corpus is consulted once per *session* instead of
once per *source*, and each later session re-reads the same PDF at full
context; `CLAUDE.md` § "Prefer deterministic tooling over repeated model work"
is that argument applied to literature. The obligation and its home are settled
here. What a note contains, and the first worked example, are `PL-Z3V5`'s and
are deliberately not fixed here.

How a session attaches and reads the corpus — `add_repo`, the shallow clone,
`poppler-utils` and `pdftotext -layout` — is in
`.claude/rules/citing-sources.md`, which loads on this directory, so it is not
repeated here. That file also says what to do when a terminal source is *not*
among the holdings: the corpus is what the project owner has supplied, not the
literature, and a miss means recording the gap and putting the reading to them.

## The documents

### Baker & Farmery 2011 — inert gas transport in blood and tissues

**Not held here.** Removed 2026-09-06 as publisher-copyright material this
public repository may not redistribute; see "Redistribution" above. Reach it
through the DOI.

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

**Not held here.** Removed 2026-09-06 as publisher-copyright material this
public repository may not redistribute; see "Redistribution" above. Reach it
through the DOI.

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

