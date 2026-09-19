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

## Direct HTTP reaches an allowlist, and the list has a date on it

The environment's **Network access** setting decides this, and it is a property
of the cloud environment rather than of this project. It takes four levels —
`None`, `Trusted` (the default), `Full` (any domain) and `Custom` (an
allowlist, optionally including the `Trusted` defaults) — set from the
environment dialog at `claude.ai/code`. This environment is on `Custom`
(project owner, 2026-09-19, ratified, over `Full` — chosen because this
repository is public, its copyright exposure is not yet closed, and an
allowlist is a record of what a session could reach where `Full` is not).

So "can I fetch this?" has no standing answer, only a measured one.
**Re-measure rather than trusting the snapshot below**, substituting the hosts
you actually need:

```sh
for h in doi.org api.crossref.org pubmed.ncbi.nlm.nih.gov www.nejm.org; do
  printf '%-28s %s\n' "$h" \
    "$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "https://$h/" 2>&1 | tail -1)"
done
```

`000` is the gateway refusing the CONNECT; any HTTP status means the host
answered. `curl -sS "$HTTPS_PROXY/__agentproxy/status"` names the reason under
`recentRelayFailures`.

**Measured 2026-09-19: the indexes opened and the publishers did not.**

- **Reached** — `doi.org` 301, `api.crossref.org` 302, `api.openalex.org` 429,
  `link.springer.com` 303, `arxiv.org` 200, `pubmed.ncbi.nlm.nih.gov` 200,
  `eutils.ncbi.nlm.nih.gov` 301, `search.worldcat.org` 200, and
  `www.sciencedirect.com` 403 (which is the trap below, not a refusal).
- **Refused at the CONNECT** — `www.nejm.org`, `epubs.siam.org`,
  `journals.sagepub.com`, `www.w3.org`, `www.icrp.org`, `en.wikipedia.org`,
  `www.google.com`, `example.com`.

That split is the thing to carry, and it is more useful than either half on its
own: **an identifier can now be checked at the source, and a paywalled full
text still cannot be fetched from the publisher.** Resolving a DOI, confirming
a volume and page range, or pulling a Crossref or OpenAlex record is a direct
call now, so `CLAUDE.md`'s requirement to consult the source rather than memory
reaches those outright and there is no excuse left for an unverified
identifier. Reading the article is still the PubMed route and the private
corpus below.

It earned its keep immediately: the first session able to resolve a DOI from
here found that `core/matrix_exponential.py` had been citing one that does not
exist (`PL-5MT4`).

`pypi.org`, `files.pythonhosted.org`, `registry.npmjs.org` and
`api.anthropic.com` sit in the proxy's own `noProxy` list, so they bypass the
gateway entirely and prove nothing about the allowlist. Do not read one of them
answering as evidence that egress is open.

**A bare `403` now means two opposite things.** Before the change every host
failed identically, so `403` was unambiguous; now the same three digits appear
on both sides of the line:

| What you see | What happened |
| --- | --- |
| `curl: (56) CONNECT tunnel failed, response 403`, and `%{http_code}` is `000` | the gateway refused — the host was never contacted |
| `HTTP/1.1 200 Connection Established`, then `HTTP/2 403` | the tunnel opened and the **publisher** refused the client |

`www.sciencedirect.com` is the live instance of the second: it is reachable and
answers `403` to an unattended client, which is the publisher's bot block
rather than an egress refusal. Reading that as "still blocked" sends a
reachable source to memory; reading a real refusal as a bot block sends a
session hunting for a user agent that will never work.

**`WebFetch` tells them apart where `curl` does not**, and is the cheaper
check: it returns a structured `EGRESS_BLOCKED` naming the domain for a refused
host, and the page itself for an allowed one. Verified 2026-09-19 — it returned
`{"error_type":"EGRESS_BLOCKED","domain":"www.nejm.org", ...}` for NEJM and
resolved `api.crossref.org/works/10.1073/pnas.2400215121` to its title,
journal, volume and DOI.

**What has not changed is the inference a refusal licenses, which is none.** A
refused host is still not evidence that the literature is unreachable, and the
step taken from that conclusion is still memory, which both rules above forbid.
What has changed is the advice that used to follow it. *Do* check the host
before concluding anything about a source, because the answer is now per-host
and dated rather than uniform. Do **not** try to route around the gateway — no
alternate proxy, no disabling TLS verification, no unsetting `HTTPS_PROXY`. The
allowlist is a decision the project owner took about what a public repository's
sessions may reach, and evading it is not a workaround but a reversal of it.
Where a host is genuinely refused, there is still a route.

Read "there is a route" as "the block is not the end of it", never as "keep
hunting until something turns up" — the second reading is what produces a
search summary dressed as a reading. Whether that route carries what a given
citation needs is a separate question, and the fourth limit below is the case
where the honest answer is no.

**The 2026-09-04 measurement, kept because it is why the routes below exist.**
On that date the environment was on `Trusted` and every literature host failed
alike: `curl` returned `CONNECT tunnel failed, response 403` for `doi.org`,
`api.crossref.org`, `api.openalex.org`, `www.sciencedirect.com`,
`link.springer.com`, `arxiv.org`, `pubmed.ncbi.nlm.nih.gov` and
`eutils.ncbi.nlm.nih.gov` — all eight — and `WebFetch` returned
`EGRESS_BLOCKED` for each. The PubMed MCP server and the private reference
corpus were adopted under those conditions. They are **not** obsolete now:
PubMed remains the route to a structured record and an abstract, and the corpus
the route to a full text the publishers still will not serve. What has gone is
the reason they were the *only* routes.

**No check in this repository can replace the dated sentence above, and that is
structural rather than a gap in the tooling.** The allowlist is enforced at the
gateway, outside the sandbox; nothing in the tree can read it, set it, or scope
it per repository. Only `remote.defaultEnvironmentId` is settable from
`.claude/settings.json`, and it binds `claude --cloud` alone rather than the
Desktop and web surfaces this project is worked from — so a committed setting
would be a guarantee that silently does not hold (project owner, 2026-09-19,
ratified, over a second environment selected per session). `CLAUDE.md` §
"Prefer deterministic tooling over repeated model work" does not reach this
one, because the decidable part sits outside the tree. What is owed instead is
the date, the command that re-measures, and no claim that outlives the next
environment edit.

## The PubMed MCP server is that route

Verified 2026-09-04, the day of the historical measurement above: search
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
  than from memory or from a search. Both remain tier 3 — a textbook chapter is
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
