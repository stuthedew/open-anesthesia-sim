---
paths:
  - "src/anesthesia_sim/data/**"
  - "docs/MODEL.md"
  - "docs/references/**"
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
environment misbehaving. There is a route.

## The PubMed MCP server is that route

Verified the same day: search returned 23 hits for `"MAC-awake" AND
sevoflurane`; metadata returned PMID, PMCID, DOI, journal, volume, pages,
authors and abstract; and full text came back for an open-access article given
its PMC id.

Three limits decide what a citation may claim:

- **Full text is PubMed Central only.** A paywalled article yields the abstract
  and no more, so an assertion that needs the methods section cannot be made
  from it.
- **Its reach is biomedical.** A venue PubMed does not index cannot be
  confirmed this way — the M4 paper in `docs/references/` is a database-systems
  paper, and its entry records the absence rather than filling it from memory.
  Copy that.
- **It requires attribution.** A reply citing what it returned names PubMed and
  gives the DOI as a link.

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
