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

## Direct HTTP reaches any host, and a publisher can still refuse

The environment's **Network access** setting decides which hosts a session can
reach. It belongs to the cloud environment and not to this repository. The
owner sets it in the environment dialog at `claude.ai/code`, and a session
reads it with the `get_environment` tool. Since 2026-11-10 it is `Full`, which
allows any domain (project owner, 2026-11-10, ratified, over keeping the
`Custom` allowlist chosen on 2026-09-19). `PL-6VZF` holds the evidence and the
list of hosts that the change discarded.

The allowlist did not control what it was chosen to control. A commit to this
public repository is what creates copyright exposure, and the list never
limited commits. A reviewer of a stored value needs a record of what was read,
and the list recorded only what a session could reach. In the design round of
2026-11-10 the list refused ten hosts that held primary sources, and five
claims reached the owner from memory.

Two rules do the work the list was chosen for:

1. **Read a source in the session before citing it.** `CLAUDE.md` § "Proactive
   expert review and domain best practices" states the rule: no citation comes
   from memory. A source that cannot be read is not cited.
2. **Commit nothing fetched from a third party**: no full text, no figure and
   no screenshot of another party's page. `docs/references/README.md` §
   "Redistribution" says which files this public repository may hold, and the
   same file says what an extraction note may quote.

**Measure whether a host answers before saying that it does not.** Substitute
the hosts you need:

```sh
for h in doi.org api.crossref.org pubmed.ncbi.nlm.nih.gov www.nejm.org; do
  printf '%-28s %s\n' "$h" \
    "$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "https://$h/" 2>&1 | tail -1)"
done
```

Any HTTP status means the host answered. `000` means the gateway refused the
CONNECT, which `Full` should never produce. Read the setting with
`get_environment` before concluding anything, and
`curl -sS "$HTTPS_PROXY/__agentproxy/status"` names the reason under
`recentRelayFailures`. Do **not** route around the gateway: no alternate proxy,
no disabling TLS verification, no unsetting `HTTPS_PROXY`. A host the gateway
refuses means the owner changed the setting, and that decision is the owner's.

**A `403` can come from the gateway or from the publisher.** The table tells
them apart:

| What you see | What happened |
| --- | --- |
| `curl: (56) CONNECT tunnel failed, response 403`, and `%{http_code}` is `000` | the gateway refused, and the host was never contacted |
| `HTTP/1.1 200 Connection Established`, then `HTTP/2 403` | the tunnel opened and the **publisher** refused the client |

`www.sciencedirect.com` answered `403` to an unattended client on 2026-09-19
and again on 2026-10-06. That is the publisher's bot block, and no user agent
gets past it. `WebFetch` returns a structured `EGRESS_BLOCKED` naming the
domain for a host the gateway refuses. For a host that answers, it returns a
small model's summary of the page and not the page itself. That settles
whether the host is reachable, and nothing it quotes: read a quotation or a
value from the page with `curl` (`PL-B1BW`).

**A publisher's refusal, or a paywall, ends the direct route and not the
search for the source.** The PubMed MCP server returns a structured record and
an abstract. The private reference corpus holds full texts that publishers do
not serve to a session. Where neither holds the passage a citation needs, the
last limit below says what to do. Never narrow the claim until something
reachable supports it, and never take a search summary for a reading.

**A sentence that says a host was refused carries its date.** The setting sits
outside the tree, so a file here can only record what a probe showed on one
day. `tools/doc_check.py` refuses a sentence that names a host beside a refusal
and gives no date (`PL-CLW5`).

## The PubMed MCP server is that route

Verified 2026-09-04: search
returned 23 hits for `"MAC-awake" AND sevoflurane`; metadata returned PMID,
PMCID, DOI, journal, volume, pages, authors and abstract; and full text came
back for an open-access article given its PMC id.

**Still the route even though `pubmed.ncbi.nlm.nih.gov` is now reachable
directly.** The MCP server returns a structured record — identifiers, the
bibliographic fields and the abstract as data — where the host returns a page
to be parsed, and a field read out of scraped HTML is the kind of provenance
this file exists to prevent. Use the direct call to *check* an identifier;
use the server to *read* a record.

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
  `open-anesthesia-sim-references`, access `read`). Then clone it outside the
  working tree, into the scratchpad directory your system prompt names:
  `git clone --depth 1 https://github.com/stuthedew/open-anesthesia-sim-references
  "$SCRATCHPAD/open-anesthesia-sim-references"`, with `SCRATCHPAD` set to that
  path. A session with no scratchpad clones beside the checkout, into
  `../open-anesthesia-sim-references`. A clone without a destination lands in
  the repository root as a nested git repository, and `git add -A` then records
  it as a gitlink this repository cannot resolve (`PL-548V`). `.gitignore`
  ignores that directory name at the root as a backstop. The GitHub
  proxy authenticates the clone, so no token enters the sandbox and the
  environment's Network access setting does not need to change. Reading a PDF
  needs `pdftotext`, from `poppler-utils`. The base image carried it on
  2026-10-18. Where `command -v pdftotext` finds nothing, install it with
  `apt-get update -qq && apt-get install -y -qq poppler-utils`. Use
  `pdftotext -layout FILE -` in preference to rendering page images, which
  costs far more and is needed only for a scan with no text layer. Its
  `README.md` indexes the holdings with
  citations verified against PubMed; read that before opening a PDF. Verified
  end to end from this environment on 2026-09-13.

  **Two of its holdings are whole textbooks**, added 2026-09-15 and split into
  section PDFs in a folder each: *Modern Anesthetics* (Schüttler & Schwilden
  2008, 22 chapters, each with its own DOI and PMID) and the *Workbook for Gas
  Man*, this project's reference implementation described by its own author.
  Together they cover inhalational and intravenous agents, uptake and
  distribution, depth of anesthesia and the parameter set the simulator runs
  on, so a science question with no obvious paper behind it starts there rather
  than from memory or from a search. Neither is a measurement. *Modern
  Anesthetics* is tier 2, a textbook, which `docs/MODEL.md` § "Source
  hierarchy" calls a secondary synthesis. The Workbook is tier 3, because it
  documents a reference implementation's parameter set. A textbook chapter is
  a route to a measurement, not the measurement.

  **Answer "is it in there, and where" without opening a PDF.** The corpus root
  carries an index file, INDEX.md, which states what the corpus does and does
  not cover and routes a topic to a book, chapter and printed page; beside it a
  text directory holds every text-layer holding extracted once and marked with
  the page number printed on each page — so `grep -rn -i "<phrase>" text/` in
  the clone costs nothing and returns something citable. Render a page only for a figure, a flattened table,
  or an exact quotation. Two cautions carried there: a printed page number is
  not a PDF page number in either book, and three of the papers are scans with
  no text layer, so a grep that finds nothing has not searched them.

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
  `docs/references/README.md` says where the note lives, what may lawfully go
  in it, and the fields it gives, with a worked example.

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

Many of the `sources` entries under `src/anesthesia_sim/data/` already named
a route or a depth when this rule was written. So this is the existing
convention made compulsory, not an addition. Every note you write or touch
names **which route** (PubMed metadata, PubMed full text, the
source's own page, the private corpus, or a document already held in
`docs/references/`) and **how deeply you read**
(full text, or the abstract only).

That sentence is the whole mechanism. Once written down, a citation taken from
a search snippet, one recalled from memory, and one read at the source are
indistinguishable in a data file — and only the first of the three is even
visibly wrong later. The note is what tells them apart.
