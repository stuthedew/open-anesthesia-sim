---
id: PL-XJ5P
title: Citing-sources says there is always a route, but a pre-abstract subscription paper has none and docs/references can no longer hold one
priority: P1
effort: M
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.19
touches: .claude/rules/citing-sources.md, docs/references/README.md
added: 2026-09-06
closed: 2026-09-13
pr: 531
verify: python3 tools/doc_check.py check && grep -qF 'open-anesthesia-sim-references' .claude/rules/citing-sources.md && grep -qF 'Where owner-supplied full texts live now' docs/references/README.md
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

**Decision needed.** What does a session do on reaching a pre-abstract,
subscription-held source with no route? Three candidates, and the middle one
needs the project owner's judgment on redistribution rather than a session's:
record the gap in the item and put the reading to the owner, who has
institutional access; carry an owner-supplied *extract* - a table and its
caption, quoted - which the redistribution rule may permit where a full PDF
does not; or re-aim the item at a reachable primary measurement of the same
quantity, recorded alongside and explicitly not adopted. Stating the
metadata-only case as terminal is wanted whichever is chosen.

## More evidence, 2026-09-10 (`PL-8SDL`)

Four more sources met the terminal case this item describes, which brings the
measured instances to seven and makes the class harder to call exceptional.

Lowe and Ernst's chapter 4 reference list was supplied by interlibrary loan and
names four upstream sources for the reference patient's organ volumes and blood
flows. Checked the same day:

- **PMID 13932730** (Mapleson, *J Appl Physiol* 1963) - metadata only, no
  abstract, no PubMed Central record.
- **PMID 5050101** (Smith, Zwart and Beneken, *Anesthesiology* 1972) - the
  same.
- **PMID 5031801** (Zwart, Smith and Beneken, *Comput Biomed Res* 1972) - the
  same.
- **ICRP Committee II's 1960 permissible-dose report** - a monograph, so PubMed
  does not index it at all. `www.icrp.org`, `journals.sagepub.com` and
  `doi.org` each returned nothing through the egress proxy.

So the pre-abstract, subscription-held case is not a tail this project meets
occasionally on its oldest citations. It is what the *whole* remaining
provenance chain is made of: every source that would decide whether the
reference patient's eleven parameters rest on a measurement is in it.

**One thing this adds to the shape of an answer.** The middle candidate this
item lists - an owner-supplied extract rather than a full text - has now been
exercised twice, on 2026-09-08 and 2026-09-10, both times as a narrowed page
range placed as an interlibrary loan and read without the repository holding
the scan. `PL-GN8C` carries recording that route in
`docs/references/README.md`. Whatever this item decides, it is deciding about
a procedure that already works rather than about a hypothetical one.

## Half landed 2026-09-13: the terminal case is stated, the disposition is not

`.claude/rules/citing-sources.md` now carries a **fourth limit** saying that a
metadata-only record is a terminal answer rather than a cue to keep looking,
and the "there is a route" paragraph is qualified to mean *around the network
refusal* rather than *for every citation*. That is the half of **Done when**
that no decision gates - this item's own brief says "stating the metadata-only
case as terminal is wanted whichever is chosen" - so it was done rather than
held behind the question below.

**One correction to this item's framing, and it makes the rule checkable.**
"Pre-abstract" is the cause; it is not the test, and a session cannot apply it
without knowing publication conventions by era. The observable marker is what
the rule now names: the metadata call returns the literal string
`[Abstract not available]` in the abstract field - a placeholder, not an absent
key - together with no `pmc` entry under `identifiers`.

Re-measured 2026-09-13 through the PubMed MCP server rather than carried from
this item's 2026-09-06 and 2026-09-10 readings, since the whole point is to
check rather than recall. All five are still terminal: PMIDs 13932730, 14164256
and 4705482 (Mapleson, 1963-1973), 5050101 and 5031801 (Smith, Zwart and
Beneken, 1972). Against them, PMIDs 2001028 and 1994760 (Yasuda et al., 1991,
which `PL-RFLN` turns on) return **full abstracts** and still carry no `pmc`
entry - so they are the *third* limit, not this one. That pair is why the rule
keys on the field instead of the date: a 1991 paper has an abstract and no
methods section, a 1963 paper has neither, and only one of those two states is
terminal.

**What remains, and it is the open decision.** What a session *does* on
reaching the terminal state, and what `docs/references/README.md` says now
stands where owner-supplied full texts used to. Both wait on the redistribution
question in **Decision needed** above, which is the project owner's. Nothing
was written into either on a session's guess.

## A third exercise of the extract route, 2026-09-13

The project owner supplied both Yasuda 1991 papers (PMIDs 2001028 and 1994760)
for `PL-RFLN`. Neither is in PubMed Central; both were read for their methods
sections and the findings recorded in `PL-RFLN` and `docs/MODEL.md`, with the
repository holding no copy. That is the middle candidate in **Decision needed**
above, exercised a third time after 2026-09-08 and 2026-09-10 - and this time
it settled a question `docs/MODEL.md` had recorded as unanswerable from what
the project could reach.

It strengthens the case for that candidate without deciding it: what the route
still lacks is a written rule saying it *is* the route, and what
`docs/references/README.md` says now stands where owner-supplied full texts
used to. Both remain the owner's call on redistribution.

## Decided 2026-09-13 by the project owner: the private corpus is the route

**The answer is the fourth candidate, which this item's own Decision needed
does not list.** `PL-5NR5` found it while this item sat open: a private
companion repository, `stuthedew/open-anesthesia-sim-references`, attached per
session with `add_repo` and cloned through the GitHub proxy. It is better than
all three candidates here, and for a reason none of them could reach - it is
*storage*. The middle candidate, an owner-supplied extract read without the
repository holding the scan, had been exercised three times by the day this
closed, and every time the reading survived only as prose in an item. So that
route scales with **sessions**; this one scales with **sources**.

**Why it is lawful, which is the half that was the owner's to settle.** The
corpus is private, which restores the premise this project lost when the public
repository stopped being able to carry a publisher-copyright full text
(`PL-SHG5`). What crosses back into the public repository is the citation and
the facts - a value, its units, its locator, what was measured and in whom -
which are not copyrightable (*Feist Publications, Inc. v. Rural Telephone
Service Co.*, 499 U.S. 340, 344-45 (1991)), with short quotation for commentary
separately supported by 17 U.S.C. 107. Reproducing a table in its published
arrangement is a different act and is not needed. `PL-Z3V5` carries that
reasoning in full; this item adopted it rather than re-deriving it.

**Verified end to end from this environment before the rule was written**,
rather than written from the documentation. `add_repo`, then `git clone
--depth 1`, then `rev-parse` - the clone authenticates through the GitHub proxy
with no token in the sandbox, and the corpus holds four sources including
Mapleson 1963 (PMID 13932730) and Smith, Zwart and Beneken 1972 (PMID 5050101),
two of the seven terminal cases this item measured. Writing a rule that points
at a repository nobody had opened would have been the same defect this item is
about.

**What landed.**

- `.claude/rules/citing-sources.md`, under the fourth limit: what a session
  does on reaching the terminal state - attach the corpus, with the exact
  commands and the `poppler-utils` / `pdftotext -layout` note - and, as
  importantly, **what a miss means**. The corpus holds what the owner has
  supplied, not the literature, so a source that is not in it has genuinely run
  out of route: record the gap and put the reading to the owner. The two exits
  this item was filed on - narrowing the claim, or taking a search summary for
  a reading - are named and refused there.
- `docs/references/README.md`, a new section beside Redistribution saying what
  now stands where owner-supplied full texts used to, what may lawfully cross
  back, and that reading one owes an extraction note in that directory.

**Deliberately not decided here.** What an extraction note *contains* and the
first worked example are `PL-Z3V5`'s, which is live on another branch; this
item settled only that the obligation exists and where it lives, both of which
are in this item's `touches` and neither of which `PL-Z3V5` could settle
without them. `PL-5NR5` is `blocked-by` this item and is now unblocked.

