---
id: PL-5DN3
title: The literature-route rule lands in docs/worker.md, which only delegated workers read, while the model-spec-accuracy items that need it are not delegable
priority: P2
effort: S
status: done
classes: docs, infra
feature: worker-instructions
milestone: v0.3.8
touches: .claude/rules/citing-sources.md, docs/worker.md
added: 2026-09-04
closed: 2026-09-04
pr: 307
verify: python3 tools/doc_check.py check && test -f .claude/rules/citing-sources.md && grep -q 'PubMed MCP' .claude/rules/citing-sources.md && ! grep -q 'api.crossref.org' docs/worker.md
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

**Worked.** Built as the `.claude/rules/` disposition rather than the resident
`CLAUDE.md` one the brief weighed alongside it: `paths:` frontmatter defers the
file, so it costs zero resident lines, which the alternative could not match.
Scoped to `docs/references/**` as well as the two paths the brief named - that
directory is where a citation is written down, and it is where `PL-P5NB` found
the same wrong lesson already in the tree.

The recording obligation is phrased as the convention the data files already
carry ("Retrieved from PubMed (PMID 2001020) and verified against the abstract
2026-09-04") rather than as a new form of words. Thirteen of the twenty-six
`sources` entries under `src/anesthesia_sim/data/` named a route or a depth
when this landed, so the rule makes an existing half-followed practice
compulsory instead of introducing one.

`docs/worker.md` keeps only what a worker uniquely needs - that a refused
`CONNECT` is expected and is not a block, which no other document tells them -
and points at the rule for the rest. Its section went from 36 lines to 15.
