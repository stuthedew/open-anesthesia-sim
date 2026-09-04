---
id: PL-0XMD
title: Primary literature is unreachable by direct HTTP from a remote session, and the finding is currently buried in a dropped item
priority: P2
effort: S
status: done
classes: docs, infra
feature: worker-instructions
milestone: v0.3.8
touches: docs/worker.md
added: 2026-09-04
closed: 2026-09-04
pr: 305
verify: python3 tools/doc_check.py check && grep -q 'PubMed MCP' docs/worker.md
---

**Problem.** This environment's egress policy refuses direct HTTP to publisher
and indexing domains. Measured 2026-09-04 while chasing citations for `PL-5WFS`:
`CONNECT` was rejected for ScienceDirect, Springer, `doi.org`, Crossref,
OpenAlex, Semantic Scholar and arXiv, and `curl` is blocked on the same policy.
Search engines answer; the sources themselves do not.

**The PubMed MCP server is the working route**, verified end-to-end in the same
session: `"MAC-awake" AND sevoflurane` returned 23 hits, and metadata retrieval
returned abstract, journal, volume/issue/pages and DOI. So the environment is
not cut off from the literature - it reaches it by a different door.

**Why it matters.** `CLAUDE.md` requires a recommendation that depends on
current standards or evidence to consult the source rather than memory, and the
safety-critical standard requires a stored constant to be traceable to what
actually measured it. A session that tries `doi.org`, is refused, and does not
know about the PubMed route concludes the literature is unreachable - and the
next step from there is memory, which is the one thing both rules forbid. The
failure is silent: a citation recorded from a search-result snippet is
indistinguishable, in a data file, from one read at the source.

This is not hypothetical for the queue ahead. `PL-6Q8N` (the reference adult's
eleven physiologic parameters have no primary source at all) and the rest of
`model-spec-accuracy` are exactly this work, and `PL-F52R` required MAC-awake
values sourced from primary literature with the explicit instruction that they
"must not be taken from memory".

**Where it is now, and why that is the bug.** The finding was written into
`PL-0PSX`, which was dropped the same day - correctly, its own premise about
rendering was disproved. But dropping an item takes its appended content out of
circulation, and this half was never part of that premise: rendering the app and
reaching a journal are different questions that happened to share an egress
policy. `PL-0PSX`'s `reason` routes what survives to `PL-CQRL` and `PL-7J96`,
and both are about driving the interface. Neither carries this.

**Where.** `docs/worker.md`, beside whatever `PL-CQRL` lands about driving the
app.

**Approach.** State both halves - what is refused, and that the PubMed MCP
server is the route - and ask a reply citing a source to say which route it came
from and whether full text or only the abstract was read. Stating only the
restriction is what produces the fallback-to-memory failure above.

**Done when.** `docs/worker.md` tells a session, before it tries, that direct
HTTP to publishers is refused and that the PubMed MCP server works, and asks it
to record which route a citation came from.
