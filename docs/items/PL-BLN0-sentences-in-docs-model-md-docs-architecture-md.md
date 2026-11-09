---
id: PL-BLN0
title: Sentences in docs/MODEL.md, docs/ARCHITECTURE.md and docs/interface-provenance.md that restate how the code or the interface behaves go stale when the code changes, because nothing ties a free-prose sentence to the code it describes
priority: P1
effort: L
status: ready
classes: defect, docs
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, docs/ARCHITECTURE.md, docs/interface-provenance.md
added: 2026-11-09
payoff: A sentence in docs/MODEL.md, docs/ARCHITECTURE.md or docs/interface-provenance.md that describes the code names what it describes, so the change that alters that code lists the sentence for review instead of leaving it to be found stale one item at a time
verify: grep -qF 'docs/interface-provenance.md' tools/doc_check.py
root-cause-of: PL-LNFG, PL-D1LR, PL-PTDZ, PL-KSLX, PL-LKX7, PL-4CZW, PL-6G7N, PL-G1J9, PL-GSPR, PL-HLTR, PL-HR4T, PL-N3SK, PL-Y9F0, PL-GPTN, PL-97S1
generator: live - fifteen filings re-entered PL-4FBP after it closed on 2026-09-19, twelve of them since PL-FM15 found no successor owed on 2026-10-31, and each structure read of a document still finds more
misread: The link between a document sentence and the tree fact it restates
reenters: PL-4FBP
---

**Problem.** Sentences in docs/MODEL.md, docs/ARCHITECTURE.md and docs/interface-provenance.md that restate how the code or the interface behaves go stale when the code changes, because nothing ties a free-prose sentence to the code it describes

**What `PL-4FBP` fixed, and what it left.** `PL-4FBP` (closed 2026-09-19)
recorded the fact this head shares with it: the link between a document
sentence and the tree fact it restates. Its convention made a live assertion
name what it asserts, and `tools/doc_check.py` now holds the enumerated lists
and the numeric paragraphs of `docs/MODEL.md` to that (`BOUND_FAMILIES`). Free
prose outside those lists was left, by decision, to the documentation review
before an item closes (`docs/MODEL.md` § "How this document is held to the
tree"). `docs/ARCHITECTURE.md` and `docs/interface-provenance.md` were never
bound at all. That review has not held. `python3 tools/doc_check.py candidates`
lists only the lines that name a changed file or definition in code type, and a
sentence saying "app/ never performs a unit calculation" or "Shift moves a
border alone" names nothing it would match.

**The filings that re-enter `PL-4FBP`.** Fifteen items record the re-entry, in
`reenters:` or in their generator check, and twelve of them were filed after
`PL-FM15` decided on 2026-10-31 that no successor head was owed:

- In `docs/ARCHITECTURE.md`: `PL-4CZW`, `PL-6G7N`, `PL-G1J9`, `PL-GSPR` and
  `PL-HLTR`, all filed 2026-11-05 by one structure read.
- In `docs/interface-provenance.md`: `PL-Y9F0` and `PL-GPTN`.
- In `docs/MODEL.md`'s free prose: `PL-HR4T`, `PL-N3SK`, `PL-KSLX`,
  `PL-LKX7`, `PL-D1LR` and `PL-PTDZ`.
- A pointer the check cannot read: `PL-97S1`.
- A source note in a data file that no check reads: `PL-LNFG`, which
  `PL-FM15` counted as the unfinished part of `PL-4FBP`'s own fix.

**Problem.** These documents restate how the code and the interface behave,
in sentences that name no module, symbol or test. When the code changes,
nothing lists the sentence, so it goes stale until somebody happens to read
it. `bin/docket inflow --lane product` lists `PL-4FBP` as a generator whose fix
did not hold.

**Why it matters.** `docs/MODEL.md` is what a clinician reads to decide whether
to trust a displayed value, and `docs/ARCHITECTURE.md` is what a contributor
reads to find where a change belongs and what it must keep. A stale sentence in
either sends the reader to a wrong conclusion. Each structure read of a
document still finds a batch of them, and each becomes its own item, so the
queue pays for the same mechanism once per sentence.

**Done when.**

1. The brief records, for each member above, whether the sentence went stale
   when the code changed or was wrong when written, and whether `python3
   tools/doc_check.py candidates --base <parent>` on the change that made it
   stale would have listed it. This sizes the two halves of the fix before
   either is built.
2. `docs/ARCHITECTURE.md` and `docs/interface-provenance.md` are held as
   `docs/MODEL.md` is. Each paragraph in a section that states how the code or
   the interface behaves names, in code type, the module, symbol or test it
   describes, or carries the fixed form for having none. `tools/doc_check.py`
   holds those sections as bound families, so a paragraph that names nothing
   fails `make check`, and `candidates` then lists the paragraph on the branch
   that changes what it names. This extends `PL-4FBP`'s own convention to two
   more documents, which is a session's call and not a reopening of the
   ratified scope.
3. `docs/MODEL.md` § "How this document is held to the tree" says which
   documents the convention binds, and the note for developers names the two
   added here.
4. Every open member is worked under this head or carries the disposition
   this head gives it.

**Lane.** The work touches `tools/doc_check.py` and its tests, which are
workflow apparatus, and three product documents, so the head is in the
crossing lane. The generator pause in `CLAUDE.md` binds only a workflow-lane
head, so this head does not pause unrelated workflow mechanisms.

**Generator check.** A generator whose fix did not hold: `PL-4FBP`'s fact,
"The link between a document sentence and the tree fact it restates", with
fifteen instances filed after it closed. `PL-G424` (the apparatus half, done
2026-10-18) and `PL-B6YV` (the computed claims in `docs/MODEL.md`, done
2026-11-02) are narrower heads on the same fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present.
At `817a4d88` the convention already bound only `docs/MODEL.md`'s lists, and
the sentences that `PL-G1J9`, `PL-HLTR`, `PL-Y9F0` and `PL-HR4T` repair were
already in their documents. The head completes entries already on
v0.7.0's frozen list, so it joins that list.

**Found by** the 2026-11-09 triage pass, from `bin/docket inflow --lane
product` and the `reenters:` fields.

