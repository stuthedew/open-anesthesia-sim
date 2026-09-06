---
id: PL-XJ5P
title: Citing-sources says there is always a route, but a pre-abstract subscription paper has none and docs/references can no longer hold one
status: untriaged
added: 2026-09-06
---

**Problem.** `.claude/rules/citing-sources.md` tells a session, in those
words, that "a refusal is not evidence that the literature is unreachable"
and "there is a route", then names the PubMed MCP server as it. For a large
and predictable class of source there is no route at all, and the rule as
written sends a session looking for one that does not exist.

The rule does state two of its limits — full text is PubMed Central only, and
a paywalled article yields the abstract and no more. It does not state the
third, which is the one that bites on this project's oldest citations: **a
paper published before structured abstracts yields neither.** Measured
2026-09-06 while starting `PL-6Q8N` (the reference adult's eleven physiologic
parameters have no primary source at all), against all three Mapleson papers
that item names as its primary lineage — PMIDs 13932730, 14164256 and 4705482,
1963 to 1973 — PubMed returns title, journal, volume, pages, DOI and MeSH
terms, no abstract for any of the three, and no PMC record. `WebFetch` is
refused for `doi.org`, `pubmed.ncbi.nlm.nih.gov`, `pmc.ncbi.nlm.nih.gov`,
`europepmc.org`, `journals.physiology.org`, `www.sciencedirect.com` and
`www.bjanaesthesia.org.uk`. There is nothing left to try.

**The escape hatch existed and was closed on 2026-09-06, without replacing
it.** `docs/references/` is where a source a session cannot reach used to
land: the project owner supplied the M4 paper on 2026-09-04 after
`www.vldb.org` proved unreachable, and `docs/references/README.md` records
that as the reason. The same README's "Redistribution" section now forbids
publisher-copyright material in this public repository and records two full
texts removed under it. Both facts are correct and the combination leaves a
hole: an unreachable, in-copyright primary source has no home, and neither
`docs/references/README.md` nor `.claude/rules/citing-sources.md` says what to
do instead.

**Why it matters.** The failure is silent, which is the property that makes it
worth fixing rather than tolerating. A session told "there is a route" that
cannot find one has three exits, and the rule's own text rules out only the
worst: memory. The other two are a search summary — which
`.claude/rules/citing-sources.md` says is indistinguishable from a reading
once written into a data file — and quietly narrowing the claim until
something reachable supports it. Both produce a `sources` note that looks
sourced. `docs/MODEL.md` § "Source hierarchy" exists to stop exactly that, and
this rule is the thing standing upstream of it.

It is not one item's problem. `model-spec-accuracy` is largely provenance work
against mid-century anesthesia literature, and that literature is
pre-abstract, subscription-held and outside PMC almost without exception.
Every such item is startable-looking, will be offered by `bin/docket next`,
and will spend a session's opening on the same discovery.

**Where.**

- `.claude/rules/citing-sources.md` — the "there is a route" paragraph and the
  three limits under the PubMed section.
- `docs/references/README.md` — "Redistribution", which closed the hatch and
  should say what now takes its place.

**The shape of an answer, not yet a decision.** State the third limit
alongside the other two: a pre-abstract paper returns metadata only, and that
is a terminal answer rather than a cue to keep hunting. Then say what a
session does when it reaches one — the candidates are recording the gap in the
item and putting the reading to the project owner, who has institutional
access; carrying an owner-supplied *extract* (a table and its caption, quoted
under fair dealing) rather than a full text, which the redistribution rule may
permit where a whole PDF does not; and re-aiming the item at a reachable
primary measurement of the same quantity, recorded alongside and explicitly
not adopted. Which of those is right is the decision this item carries, and
the middle one needs the project owner's judgment on redistribution rather
than a session's.

**Done when.** `.claude/rules/citing-sources.md` names the metadata-only case
as terminal and tells a session what to do on reaching it, and
`docs/references/README.md` says what now stands where owner-supplied full
texts used to.
