---
paths:
  - "/src/anesthesia_sim/data/**"
  - "/docs/MODEL.md"
  - "/docs/references/**"
---

# Reaching a source, and recording which route you took

`CLAUDE.md` requires a recommendation depending on current evidence to consult
the source rather than memory, and the safety-critical standard requires a
stored constant to be traceable to what actually measured it. This file is how
that is done from this environment. It loads on the files where a constant and
its provenance live, which is the moment the question arises.

What may be cited as the **authority** for a stored value is a different
question, decided by `docs/MODEL.md` § "Source hierarchy: what may be cited as
the authority for a value". That one is about whether a document counts; this
one is about how you reached it. Both have to be answered.

## Direct HTTP to publishers and indexes is refused

The egress proxy rejects the tunnel itself, so every route that opens a socket
to a journal fails the same way. Measured 2026-09-04 against `doi.org`,
`api.crossref.org`, `api.openalex.org`, `www.sciencedirect.com`,
`link.springer.com`, `arxiv.org`, and NCBI's own `pubmed.ncbi.nlm.nih.gov` and
`eutils.ncbi.nlm.nih.gov`: `curl` returned `CONNECT tunnel failed, response
403` for all eight, and `WebFetch` returned `EGRESS_BLOCKED`.

**A refusal is not evidence that the literature is unreachable**, and the next
step from that conclusion is memory, which both rules above forbid. Do not
retry, do not look for a proxy around it, and do not treat it as the
environment misbehaving. There is a route *around the network refusal*.

Whether that route carries what a given citation needs is a separate question,
and the fourth limit below is the case where the honest answer is no. Read
"there is a route" as "the block is not the end of it", never as "keep hunting
until something turns up" — the second reading is what produces a search
summary dressed as a reading.

## The PubMed MCP server is that route

Verified the same day: search returned 23 hits for `"MAC-awake" AND
sevoflurane`; metadata returned PMID, PMCID, DOI, journal, volume, pages,
authors and abstract; and full text came back for an open-access article given
its PMC id.

Four limits decide what a citation may claim:

- **Full text is PubMed Central only.** A paywalled article yields the abstract
  and no more, so an assertion that needs the methods section cannot be made
  from it.
- **Its reach is biomedical.** A venue PubMed does not index cannot be
  confirmed this way. The worked example was `docs/references/`' M4 paper, a
  database-systems paper whose entry recorded the absence of a DOI rather than
  filling it from memory; the entry went with the code that cited it
  (`PL-8LXM`), but the practice is the point — record what could not be
  confirmed, and never supply it from memory.
- **It requires attribution.** A reply citing what it returned names PubMed and
  gives the DOI as a link.
- **Metadata only is a terminal answer, not a cue to keep looking.** A record
  old enough to predate abstracts returns title, journal, volume, pages, DOI
  and MeSH terms, and nothing else. There is no abstract to fall back to and no
  full text behind it; the route ends there, and the next step is the item's,
  not another search.

  **Check the marker rather than the year**, because the year does not decide
  it. Measured 2026-09-13 against this project's own provenance chain: the
  metadata call returns the literal string `[Abstract not available]` in the
  abstract field — a placeholder, not an absent key — and no `pmc` entry under
  `identifiers`. That pair is the terminal state. Five of the sources deciding
  whether the reference patient's parameters rest on a measurement are in it:
  PMIDs 13932730, 14164256 and 4705482 (Mapleson, 1963 to 1973), and 5050101
  and 5031801 (Smith, Zwart and Beneken, 1972). Against them, PMIDs 2001028 and
  1994760 (Yasuda et al., 1991) return full abstracts and still carry no `pmc`
  entry — which is the *third* limit, not this one: their abstracts are
  readable and their methods sections are not. Telling the two apart is the
  point of checking the field instead of the date.

  **What to do on reaching it: attach the private reference corpus** (decided
  by the project owner 2026-09-13, `PL-XJ5P`).
  `stuthedew/open-anesthesia-sim-references` holds owner-supplied full texts
  for exactly this case. It is *private*, which is what makes holding them
  ordinary personal use rather than redistribution — the premise this project
  lost when the public repository stopped being able to carry them
  (`PL-SHG5`), restored without reopening it.

  Attach it with `add_repo` (owner `stuthedew`, repo
  `open-anesthesia-sim-references`, access `read`), then `git clone --depth 1
  https://github.com/stuthedew/open-anesthesia-sim-references`. The GitHub
  proxy authenticates the clone, so no token enters the sandbox and the
  environment's network level stays Trusted. Reading a PDF needs
  `poppler-utils`, which the base image does **not** carry: `apt-get update -qq
  && apt-get install -y -qq poppler-utils`, then `pdftotext -layout FILE -` in
  preference to rendering page images, which costs far more and is needed only
  for a scan with no text layer. Its `README.md` indexes the holdings with
  citations verified against PubMed; read that before opening a PDF. Verified
  end to end from this environment on 2026-09-13.

  **Two of its holdings are whole textbooks**, added 2026-09-15 and split into
  section PDFs in a folder each: *Modern Anesthetics* (Schüttler & Schwilden
  2008, 22 chapters, each with its own DOI and PMID) and the *Workbook for Gas
  Man*, this project's reference implementation described by its own author.
  Together they cover inhalational and intravenous agents, uptake and
  distribution, depth of anesthesia and the parameter set the simulator runs
  on, so a science question with no obvious paper behind it starts there rather
  than from memory or from a search. Each folder carries its own catalogue
  indexing chapters, page ranges and identifiers; read it before opening a
  section, and mind that a printed page number is not a PDF page number in
  either book. Both remain tier 3 — a textbook chapter is a route to a
  measurement, not the measurement.

  **A miss is an answer too, because the corpus is not the literature.** It
  holds what the project owner has supplied, and nothing else. Where a terminal
  source is not among its holdings the route really has ended: record the gap in
  the item and put the reading to the project owner, who has institutional
  access and has turned interlibrary loans around inside a day when the request
  named the pages it needed. What must not happen is the other two exits —
  narrowing the claim until something reachable supports it, or taking a search
  summary for a reading. Both produce a `sources` note that looks sourced, and
  `docs/MODEL.md` § "Source hierarchy" exists to stop exactly that.

  **Reading a source from the corpus owes an extraction note back here.**
  Otherwise the corpus is consulted once per *session* rather than once per
  *source*, and every later session re-reads the same PDF at full context.
  Where that note lives and what may lawfully go in it is
  `docs/references/README.md`; `PL-Z3V5` carries the note's fields and the
  first worked example.

## A search result is not a source

Search answers when the publishers do not, which is what makes its summaries
the likeliest thing to be mistaken for a reading. In the same measurement a
search summary produced the citation `Anesthesiology 1994; 84:1484-1492`, which
PubMed's citation matcher does not resolve. Search for an identifier; read the
record through PubMed.

## Full text arrives with its subscripts flattened

The body comes back as plain prose, so `MAC_awake` reads as `MAC` and `ETCO2`
as `ETCO`. Take a number from that text; do not take the symbol the number
belongs to from it — check the symbol against the abstract, the metadata, or
`docs/MODEL.md` § "Symbols", which is where getting it wrong reaches a reader.

## Record the route and the depth, in the note itself

The data files already do this, and the phrasing is theirs rather than a new
one to invent:

> Retrieved from PubMed (PMID 2001020) and verified against the abstract
> 2026-09-04.

Thirteen of the twenty-six `sources` entries under `src/anesthesia_sim/data/`
named a route or a depth when this rule was written; the rest name neither. So
this is the existing convention made compulsory, not an addition — every note
you write or touch names **which route** (PubMed metadata, PubMed full text, or
a document already held in `docs/references/`) and **how deeply you read**
(full text, or the abstract only).

That sentence is the whole mechanism. Once written down, a citation taken from
a search snippet, one recalled from memory, and one read at the source are
indistinguishable in a data file — and only the first of the three is even
visibly wrong later. The note is what tells them apart.
