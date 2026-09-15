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
2026-09-05). It is founded again since 2026-09-14 - the chart's drawing
guarantee cites its result (`PL-GS3R`) - and lives in the private corpus below
rather than here, by the project owner's decision, with its entry and reading
note under "The documents".

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

**Two of its holdings are whole books**, added 2026-09-15 and split into
section PDFs so none exceeds 100 pages: this volume and the Gas Man Workbook,
both with entries below. Each lives in a folder of its own carrying a catalogue
of its chapters, page ranges and identifiers, and that catalogue is what to read
before opening a section — it will usually name the one file worth opening. A
science question with no obvious paper behind it starts there rather than from
memory.

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

### Jugel et al. 2014 — M4 time series aggregation

**Not held here.** Held in the private corpus,
`stuthedew/open-anesthesia-sim-references`, which "Where owner-supplied full
texts live now" above says how to attach. Its licence, CC BY-NC-ND 3.0 per the
statement on its first page, would let this public repository carry it, and it
did from 2026-09-04 until `PL-8LXM` removed it with the M4 decimation module
on 2026-09-08 as a paper nothing then founded. Supplied again by the project
owner on 2026-09-14 - the same bytes, by checksum - and placed in the private
corpus by their decision, with every other owner-supplied full text.

> Jugel U, Jerzak Z, Hackenbroich G, Markl V. M4: A Visualization-Oriented
> Time Series Data Aggregation. *Proceedings of the VLDB Endowment*.
> 2014;7(10):797–808. ISSN 2150-8097.

Every field above is taken from the paper's own title page and running
footer, read with `pdftotext` on 2026-09-14, which is all this entry asserts.
**No DOI is recorded, deliberately.** The PDF prints none — only the ISSN and
the copyright line — `doi.org` and `www.vldb.org` are both blocked by the
session egress proxy, and PubMed does not index the venue, so nothing could be
checked against a registry. A remembered DOI written down becomes a fact by
tomorrow. A session that can reach a registry should confirm the record and
add one.

**What the chart takes from it, and what it does not.** `docs/MODEL.md`
§ "What the chart draws" holds the chord between two drawn instants to one
pixel of time. This paper is the published form of the argument behind that,
seen from the other side. For recorded data grouped into pixel columns,
Theorem 1 proves `vis_wh(G_M4(T)) = vis_wh(T)`: the two-colour line
visualization of the four tuples Definition 2 selects per column — the
`min(v)`, `max(v)`, first and last tuples — equals that of the whole series,
and the proof (Lemmas 1 and 2) is that every inner-column pixel follows from
the column's top and bottom, and every inter-column line from the last tuple
of one column and the first of the next. The chart selects nothing: it
evaluates the run at one instant per pixel boundary, so on a stretch monotone
within the pixel the two boundary values are that column's top and bottom and
the segment between them is its inter-column line. Two things the paper's
guarantee has that the chart's does not, both stated in `docs/MODEL.md`. It
holds only with groups aligned to pixel columns — §6: "the engineers have to
make sure that nh = w", or any integer factor of w — and the chart's grid is
anchored to the case's zero rather than to the viewport, so the chart's claim
is "within one pixel of time", not pixel identity. And it needs the min and
max tuples for a stretch that turns inside a column, which the chart does not
evaluate, so an extremum between two dial changes is the one measured
residual, 0.0028 pp at worst over the supported envelope.

Read in full text on 2026-09-14 for the sections named above. §4.3's error
taxonomy and §5's query rewriting were not read for this entry.

### Philip — *Workbook for Gas Man*

**Not held here. Held in the private corpus**,
`stuthedew/open-anesthesia-sim-references`, which "Where owner-supplied full
texts live now" above says how to attach. Supplied by the project owner
2026-09-15, split into five section PDFs. It is the manual distributed with the
Gas Man program and carries no licence permitting redistribution, so it may not
sit in this directory.

> Philip JH. *Workbook for Gas Man®: a simulation and teaching tool*.
> Chestnut Hill, MA: Med Man Simulations, Inc.; title page dated 2012-05-16,
> preface dated October 2010. 199 pages.

**No DOI, ISBN or PubMed record**, deliberately: the document prints none, and
PubMed does not index software manuals, so there is nothing to check the
citation against. Every field above is read off the title page and the
preface's sign-off, 2026-09-15, which is all this entry asserts.

**The title this repository cited until 2026-09-15 is not the one on the title
page.** Every `sources` entry under `src/anesthesia_sim/data/` naming this
document called it "Gas Man(R) Workbook and Laboratory Manual", which `PL-XTMB`
took from the cover and from the original PDF's `/Title` and `/Author` fields.
That string occurs zero times in the document's 209 pages of text, and the
title page reads as quoted above. The corpus's section PDFs were rewritten by
`pypdf` and carry no `/Title`, so the two cannot be reconciled from anything
this project holds; a citation follows the title page, and `PL-9GP1` changed
the data files to match.

**Why this one is load-bearing.** Gas Man is this project's reference
implementation, and the `sources` notes trace the reference patient's eleven
parameters and all twelve stored partition coefficients to it. Until now the
project had read only "a copy of the front matter and appendices supplied by
the project owner"
(`src/anesthesia_sim/data/patients/reference_adult.json`, 2026-09-06) — a
route neither of the two in `.claude/rules/citing-sources.md`, recorded as a
gap by `PL-XJ5P`. The whole document is now readable, which closes that gap.
Three things found on reading it (`PL-9GP1`), none of which changes a stored
value:

- **Appendix B, "The Gas Man Approach", Model Parameters table, p. 168** — the
  table `src/anesthesia_sim/data/patients/reference_adult.json` already
  cites — reads exactly as that file records it.
- **Appendix C, "Gas Man System Defaults", pp. 171–72** is a verbatim listing
  of `GASMAN.INI`, and a second statement of the same parameter set: `Lambda`
  (blood/gas) and `VRG`, `MUS`, `FAT` (tissue/gas) per agent, matching all
  twelve stored coefficients, for nine agents. **It carries three values
  Appendix B's table does not**: `[Volumes] VEN=1.0`, and `[Defaults] VA=4` and
  `CO=5`. Two provenance notes in
  `src/anesthesia_sim/data/patients/reference_adult.json` were written without
  this page — one saying the venous pool value carried until 2026-09-07 appears
  nowhere, the other that the workbook states no numeric default for alveolar
  ventilation. Both are scoped to Appendix B's table and are true of it;
  Appendix C is a different page and does carry the numbers. That makes neither
  value a measurement — they are the same program's defaults, tier 3 — but it
  is where they are written down. `PL-9GP1` brought it into those notes and
  into `docs/MODEL.md`, which had recorded the venous pool's 1.0 L as a value
  no source contained; no stored value changed.
- **Appendix B's second table is mis-captioned.** Under "Tissue/Gas partition
  coefficients (calculated)" it lists Blood/Gas, Brain/Blood, Muscle/Blood and
  Fat/Blood rows, which are tissue/**blood** ratios. Every column reproduces as
  the first table's tissue/gas divided by that agent's blood/gas **except
  isoflurane's**, which is divided by 1.90 — enflurane's blood/gas, not
  isoflurane's 1.30. Appendix C's listing agrees with the first table, and so
  does this repository. Take a Gas Man tissue/gas coefficient from the first
  table or from Appendix C, and no isoflurane tissue/blood ratio from the
  second.

Its bibliography's reference 45 is "Yasuda, N, Targ, AG and Eger, EI II.
Solubility of I-653, Sevoflurane, Isoflurane and Halothane in human tissues.
Anesthesiology. Vol. A615 (Abstract), 69" — the 1988 abstract, not the 1989
*Anesth Analg* paper of the same title. Its reference 23 is Lowe and Ernst
1981, printed with the initial "HF" there and "HJ" at references 22 and 24, so
that bibliography is internally inconsistent.

Route and depth: the corpus's section PDFs, read with `pdftotext -layout` on
2026-09-15 — the front matter, the table of contents, Appendices A–E and the
bibliography in full, and every section's boundary pages. Chapters 1–19 were
not read beyond those.

### Schüttler & Schwilden 2008 — *Modern Anesthetics*

**Not held here. Held in the private corpus**,
`stuthedew/open-anesthesia-sim-references`, which "Where owner-supplied full
texts live now" above says how to attach. Removed from this public repository
2026-09-06 as publisher-copyright material it may not redistribute; see
"Redistribution" above. Supplied again by the project owner 2026-09-15, split
into eight section PDFs, and placed in the corpus by their decision, with every
other owner-supplied full text. Reachable from outside this project through the
DOI.

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
has been read and checked yet.

**A chapter in an edited volume is cited as that chapter with its own authors,
never as the volume**, and every field needed to do so is now recorded.
PubMed indexes all 22 chapters as *Handb Exp Pharmacol.* 2008;(182):pages —
the volume number sits in the issue field, so a search restricted to volume 182
returns nothing — each with its own DOI, `10.1007/978-3-540-74806-9_N` for
chapter *N*, and a PMID; they run consecutively from 18175084 for chapter 1 to
18175105 for chapter 22. Verified against PubMed 2026-09-15. The corpus folder
holds the whole table; four chapters are the ones this project would reach for
first:

- **Hendrickx JFA, De Wolf A. Special aspects of pharmacokinetics of inhalation
  anesthesia.** pp. 159–86. PMID
  [18175091](https://pubmed.ncbi.nlm.nih.gov/18175091/). The circle system, why
  inhaled and intravenous kinetics are modelled differently, the F_A/F_I curve,
  the general anesthetic equation, and the delivered-to-inspired discrepancy
  under low fresh gas flow. **Same two authors as the De Wolf et al. 2012 *BMC
  Anesthesiology* Gas Man simulation** that every file under
  `src/anesthesia_sim/data/agents/` cites at tier 3 for its coefficients — a
  different work, four years earlier, and easy to conflate with it.
- **Bischoff P, Schneider G, Kochs E. Anesthetics drug pharmacodynamics.**
  pp. 379–408. PMID [18175101](https://pubmed.ncbi.nlm.nih.gov/18175101/).
- **Shafer SL, Stanski DR. Defining depth of anesthesia.** pp. 409–23. PMID
  [18175102](https://pubmed.ncbi.nlm.nih.gov/18175102/). Depth as the
  probability of non-response calibrated against stimulus strength.
- **Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. Advanced technologies and
  devices for inhalational anesthetic drug dosing.** pp. 451–70. PMID
  [18175104](https://pubmed.ncbi.nlm.nih.gov/18175104/). Vaporizers,
  desflurane's differential-pressure delivery, gas sensing, and closed-circuit
  feedback control.

Route and depth, as `.claude/rules/citing-sources.md` requires: the corpus's
section PDFs, read with `pdftotext -layout` on 2026-09-15 for the front matter,
the full table of contents and every section's boundary pages, plus PubMed
metadata and abstracts for all 22 chapters. **No chapter has been read at full
text**, so nothing here may yet be cited for a value.
