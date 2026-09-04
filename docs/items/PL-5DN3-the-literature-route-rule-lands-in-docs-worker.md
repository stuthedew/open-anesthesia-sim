---
id: PL-5DN3
title: The literature-route rule lands in docs/worker.md, which only delegated workers read, while the model-spec-accuracy items that need it are not delegable
status: untriaged
added: 2026-09-04
---

**Problem.** `PL-0XMD` put the literature-route rule - direct HTTP to
publishers is refused, the PubMed MCP server works, say which route a citation
came from - into `docs/worker.md` § "Reaching a source". `AGENTS.md` sends only
a **worker** there: "If you have been asked to work this repository's queue as
a worker ... read `docs/worker.md` as well." A main session driven by
`CLAUDE.md` never opens it.

**Why it matters.** The sessions that need the rule are the ones `docs/worker.md`
cannot reach. `bin/docket delegable` does not list `PL-6Q8N` (the reference
adult's eleven physiologic parameters have no primary source at all), and it
cannot: `docs/worker.md` forbids a worker from editing
`src/anesthesia_sim/core/`, `src/anesthesia_sim/data/` or `docs/MODEL.md`,
which is exactly where a cited constant and its provenance live. So every item
in `model-spec-accuracy` - the whole body of work `PL-0XMD` was written to
protect - is worked by a main session that will not have read the rule.

The failure this leaves open is the one `PL-0XMD` describes: a session tries
`doi.org`, is refused, concludes the literature is unreachable, and falls back
to memory or to a search snippet. Neither is distinguishable from a reading
once it is written into a data file.

**Where.** A new path-scoped rule under `.claude/rules/`, with `paths:` matching
`src/anesthesia_sim/data/**` and `docs/MODEL.md` - the files a session reads
when it is about to record where a number came from. `.claude/rules/core-domain.md`
and `.claude/rules/ui-color.md` are the pattern.

`CLAUDE.md`'s routing rule warns that a path-scoped rule is "wrong for one that
must fire before a first write, which no read precedes". That objection does
not bite here: provenance is added to a file that already exists, so the read
always precedes.

**Approach.** Move the rule rather than copy it, or the two statements drift.
The natural split is that `.claude/rules/` carries the routes and the recording
obligation, and `docs/worker.md` keeps one sentence pointing at it, since a
worker still needs to know a refused `CONNECT` is not a block.

Weigh a second disposition before building: `CLAUDE.md` already says a
recommendation depending on current evidence must "consult the source rather
than memory", and two sentences naming the working route would make that rule
executable where it already lives. The cost is resident context in every
session - `make check` reports the total, currently 530 lines.

**Done when.** A session that opens `docs/MODEL.md` or a file under
`src/anesthesia_sim/data/` is told, before it tries, that direct HTTP to
publishers is refused and the PubMed MCP server is the route, and is asked to
record which route and what depth a citation came from - and `docs/worker.md`
does not state the same thing twice.
