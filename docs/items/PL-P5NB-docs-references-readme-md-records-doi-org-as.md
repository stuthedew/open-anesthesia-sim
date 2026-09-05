---
id: PL-P5NB
title: docs/references/README.md records doi.org as blocked without naming the PubMed route that works
priority: P2
effort: S
status: ready
classes: docs
feature: provenance
touches: docs/references/README.md
added: 2026-09-04
verify: python3 tools/doc_check.py check && grep -q 'PubMed MCP' docs/references/README.md
---

**Problem.** `docs/references/README.md`'s Jugel et al. entry explains why it
records no DOI: "nothing here could be checked against a registry:
`www.vldb.org` and `doi.org` are both blocked by the session egress proxy", and
closes with "A session that can reach a registry should confirm the record and
add one."

For that paper the conclusion is right and should stand - M4 is a VLDB database
paper, so PubMed does not index it and there was no route to check. What is
wrong is the sentence's reach. It states the blockage as a property of the
environment with no route out of it, in the one file a session reads while
recording a citation, and two entries above it the Baker & Farmery entry says
"Metadata confirmed against PubMed" without saying how that was done.

**Why it matters.** This is `PL-0XMD`'s failure mode already present in the
tree: a reader takes "registries are blocked" as general, when
`docs/worker.md` § "Reaching a source" now records that the PubMed MCP server
reaches PubMed and PubMed Central and was verified doing so on 2026-09-04. The
next session recording a *biomedical* citation reads this file, believes no
registry is reachable, and writes down what it remembers.

**Where.** `docs/references/README.md`, the Jugel et al. entry's
no-DOI-recorded paragraph, and the Baker & Farmery entry's "Metadata confirmed
against PubMed" line.

**Approach.** Two clauses, no restructuring. Qualify the Jugel paragraph so it
says the registries reachable from a session do not index this venue, rather
than that no registry is reachable. Say on the Baker & Farmery entry which
route confirmed it, which is what that entry is asking every later entry to do.

**Done when.** `docs/references/README.md` cannot be read as saying the
literature is unreachable, and each entry that claims confirmation names the
route that confirmed it.

**Note, 2026-09-04.** `PL-5DN3` scoped `.claude/rules/citing-sources.md` to
`docs/references/**` as well as the two paths it was written for, so a session
opening this file now loads the correct account of the routes alongside the
wrong one. That lowers the severity and does not close the item: the sentence
in the file still says what it says, and a rule loaded beside a contradicting
paragraph is a worse state than either alone.
