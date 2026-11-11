---
id: PL-BLN0
title: Sentences in docs/MODEL.md, docs/ARCHITECTURE.md and docs/interface-provenance.md that restate how the code or the interface behaves go stale when the code changes, because nothing ties a free-prose sentence to the code it describes
priority: P1
effort: L
status: done
classes: defect, docs
touches: tools/doc_check.py, tests/unit/test_doc_check.py, .claude/rules/ui-calculations.md, docs/MODEL.md, docs/ARCHITECTURE.md, docs/interface-provenance.md, docs/items/PL-LJY8-docs-maintainer-md-has-the-headless-worker-take.md, docs/items/PL-HR4T-docs-model-md-intended-use-lists-extreme.md, docs/items/PL-N3SK-docs-model-md-known-limitations-says-nothing-on.md, docs/items/PL-LKX7-docs-interface-md-displayed-precision-says-a.md, docs/items/PL-97S1-two-citations-name-docs-model-md-s-known.md, docs/items/PL-LNFG-tools-doc-check-py-checks-no-citation-inside-a.md
added: 2026-11-09
closed: 2026-11-09
pr: 2072
payoff: A sentence in docs/MODEL.md, docs/ARCHITECTURE.md or docs/interface-provenance.md that describes the code names what it describes, so the change that alters that code lists the sentence for review instead of leaving it to be found stale one item at a time
verify: grep -qF 'docs/interface-provenance.md' tools/doc_check.py
root-cause-of: PL-LNFG, PL-D1LR, PL-PTDZ, PL-KSLX, PL-LKX7, PL-4CZW, PL-6G7N, PL-G1J9, PL-GSPR, PL-HLTR, PL-HR4T, PL-N3SK, PL-Y9F0, PL-GPTN, PL-97S1
generator: spent - since this item, every paragraph of docs/ARCHITECTURE.md and of docs/interface-provenance.md's last chapter names the code it describes or declares no code yet against an open item, so make check fails a paragraph that names nothing, and the review list prints the whole paragraph when code it names changes; docs/MODEL.md's free prose stays outside by this brief's decision, HR4T, N3SK, LKX7, 97S1 and LNFG stay ordinary items, and a member later found in a bound document reopens the head
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

## Step 1: what made each sentence wrong (checked 2026-11-09)

A subagent traced each sentence to the commit that wrote it and the commit
that made it false. For each stale sentence it ran that commit's own
`python3 tools/doc_check.py candidates --base <sha>^` in a worktree. PL-HLTR
was reasoned instead, because its commit predates `tools/`. For PL-PTDZ it ran
the fix's test against the tree of 2026-10-26.

| Item | Document | Class | Writing commit | Commit that made it false | `candidates` listed the sentence? | Names its code? |
| --- | --- | --- | --- | --- | --- | --- |
| PL-D1LR | MODEL | stale (second sentence wrong when written, `104e2543a`) | `9c6ebd298` | `ae8fc7bc2` (`PL-TG60`) | no | no |
| PL-KSLX | MODEL | stale | `4f6d6390b`, `fd0d9aaba` | `0fd277138` (`PL-NJPB`) | first sentence yes, second no | first yes, second no |
| PL-PTDZ | MODEL | wrong when written (7.31 min; the model gave 7.304) | `5a8dc0368` | none | n/a | no |
| PL-4CZW | ARCHITECTURE | stale | `ffe30d4c1` | `2713d097b` (`PL-VHQX`) | no; line 384 of the same paragraph yes | yes, `SimulationController.advance()` |
| PL-6G7N | ARCHITECTURE | stale | `96d308863` | `1f0e8b1ec` (`PL-M85T`) | no; line 49 of the same paragraph yes | yes, `core/`, `for_agent()` |
| PL-G1J9 | ARCHITECTURE | wrong when written | `434b67c89` | none | n/a | only `app/` and `core/` |
| PL-GPTN | interface-provenance | stale (a recommendation that shipped) | `c8f806854` | `4081f8766` (`PL-TH35`) | no | only the item id |
| PL-GSPR | ARCHITECTURE | misleading when written | `b9b3c8120` | none | n/a | in a code-fenced tree |
| PL-HLTR | ARCHITECTURE | stale | `434b67c89` | `4148a9ce6` | no (the same diagram's `controller` line would have matched) | in a code-fenced diagram |
| PL-HR4T | MODEL | wrong when written (decimation deleted five days earlier, `cf6f71f83`) | `a0c34f0b6` | none | n/a | no |
| PL-LKX7 | MODEL | stale (a dated measurement of the whole layout) | `0fcd1dddb` | `960c3b656` (`PL-NWTM`) | no | names `src/anesthesia_sim/app/main.py`, not the split |
| PL-N3SK | MODEL | stale (a claim that nothing reads `src/anesthesia_sim/core/liquid_agent.py`) | `c95177a6e` | `26eb4e39e` (`PL-B396`) | no | yes, but the change added a reader elsewhere |
| PL-Y9F0 | interface-provenance | stale (an implied recommendation the code went against) | `c8f806854` | `7b9efe01a` (`PL-50PZ`) | no | no |
| PL-97S1 | `src/anesthesia_sim/core/liquid_agent.py`, ROADMAP | a citation without its section mark | `d18c626dc`, `c95177a6e` | none | n/a | n/a |
| PL-LNFG | `src/anesthesia_sim/data/agents/desflurane.json` | stale (a renamed test file) | `2a4c76ab3` | `bc21c3208` | no; the review reads Markdown only | a bare path in JSON |

**Totals.** 10 stale, 3 wrong when written (PL-PTDZ, PL-G1J9, PL-HR4T, and
PL-D1LR's second sentence), 2 other (PL-GSPR, PL-97S1). Of the 10 stale
sentences, `candidates` listed the sentence itself once (PL-KSLX's first),
and that sentence stayed stale. In 7 of the 10, the commit that made the
sentence false also edited the same document and fixed a neighbouring
sentence. In 6, a later rewrite restated the sentence after it had gone
stale, so `git log -S` finds the rewrite first.

**How long the review list is.** Over the eight most recent merges that
touched `src/anesthesia_sim/`, `candidates` printed 17, 23, 27, 50, 160, 182,
211 and 389 lines. Most lines are a file name mentioned in `ROADMAP.md`, a
rule or an item, one line each.

**What the brief's mechanism would have caught.** Step 2 binds only
`docs/ARCHITECTURE.md` and `docs/interface-provenance.md`, where five of the
stale sentences sit:

- PL-GPTN: caught. Its paragraph names only `PL-TH35`, so it would carry the
  fixed form against `PL-TH35`, and the check fails on the branch that closes
  `PL-TH35`.
- PL-Y9F0: caught if read. Its paragraph would have to name the Area header's
  module, and `PL-50PZ` changed that module.
- PL-4CZW and PL-6G7N: caught if `candidates` lists the paragraph rather
  than the line, as step 2 says. Each already named code, and the list already
  showed a line three to seven lines from the stale sentence.
- PL-HLTR: not caught. The stale line is in a fenced diagram, which is not a
  paragraph. The diagram's `app/controller.SimulationController` line would
  have matched the change, and the stale line is seven lines above it.

So the design holds as written, and two parts carry it: the fixed form,
resolved against the queue, and listing the whole paragraph. Requiring a
paragraph to name code adds little in `docs/ARCHITECTURE.md`, where the stale
paragraphs already did. Its value is in forcing the fixed form onto a
recommendation or a "not yet" claim that names nothing.

**What it leaves.** The wrong-when-written sentences need a reader at the
time of writing, and the copy editor's structure read is what found all
three. The four `docs/MODEL.md` free-prose members (PL-D1LR, PL-KSLX,
PL-LKX7, PL-N3SK) are outside step 2, because the ratified scope of
`PL-4FBP` leaves `docs/MODEL.md`'s free prose to the close-out review, and
this audit is evidence that the review did not hold for them.


## Next steps (written 2026-11-09, at `edf349ade`)

The session that recorded step 1 stopped at its spend budget before the build.
The build follows the brief as written, because step 1 found no better route.

1. **The paragraph shape and the entity.** In `tools/doc_check.py`, add a
   member shape that yields each paragraph under the family's heading, as
   `read_blocks` reads them, up to the next heading at the family's depth or
   shallower. `_numeric_paragraph_members` is the model to follow. Add a
   `CODE_ENTITY` built with `_entity_kind("code", ...)`. A member names code
   when it holds a code span other than a bare item id, read with
   `_code_spans`, because an item id alone is what let PL-GPTN's paragraph go
   stale. Its fixed form is then "no code yet (`PL-XXXX`)", which
   `check_bound_families` already resolves against the queue.
2. **The families.** Bind every level-2 section of `docs/ARCHITECTURE.md`
   and `docs/interface-provenance.md` § "What this project adopts, diverges
   from, and refuses". On 2026-11-09, 16 of the 150 paragraphs in
   `docs/ARCHITECTURE.md` named no code. They were in § "Data files", § "Data
   flow", § "What a branch is" and § "User state: the saved Workspaces". In
   the interface-provenance section, 12 of 31 named no code. The new check
   lists them by line once it is built.
3. **The annotation pass, in the same commit as the families.** Make each
   listed paragraph name the module, symbol or test it describes, or carry
   the fixed form against the open item that owes the code. PL-GPTN's Prune
   entry and PL-Y9F0's paragraph on a view's chrome are among them, so claim
   both alongside and repair their sentences in this pass.
4. **The review list.** Where `candidates` finds a hit inside a member of a
   bound family, print the member's first and last line, so the reviewer
   reads the whole paragraph. The hit lines are built where `candidates`
   formats `f"    {doc}:{number}  ({token})"`.
5. **Tests** in `tests/unit/test_doc_check.py`: a paragraph that names no
   code fails, and so does one whose only code span is an item id. The fixed
   form against a closed item fails. `candidates` prints a member's range.
6. **Step 3**: `docs/MODEL.md` § "How this document is held to the tree"
   says that the convention binds `docs/MODEL.md`'s families,
   `docs/ARCHITECTURE.md` and the interface-provenance section, and its note
   for developers names the two new families.

**Each open member's disposition**, decided by this head:

- **Repaired on this head's branch, each claimed alongside with its own
  commit:**
  - PL-4CZW: the branch chapter is current (a fork onto the supported run
    length is refused), and § "Data flow" is stale.
  - PL-6G7N: § "Where new code belongs" is current, and § "Layering"'s
    "defaults are still written in `core/`" is stale.
  - PL-G1J9: § "Layering"'s claim that `app/` performs no unit calculation
    was wrong when written. Read `chart_frame.py`, `formatting.py` and
    `agent_cost.py` first, then say what `app/` converts or computes.
  - PL-GSPR: say in the package map that `AgentUptakeSystem.advance`
    advances the coupled system.
  - PL-HLTR: the startup diagram shows
    `AgentUptakeSystem.for_agent(agent_id)`.
  - PL-GPTN and PL-Y9F0: repaired by the annotation pass.
- **Left as their own items, outside this head's mechanism:**
  - PL-HR4T and PL-N3SK are `docs/MODEL.md` free prose.
  - PL-LKX7 also needs a new measurement in the running app.
  - PL-97S1 is a citation's form.
  - PL-LNFG needs a check of a data file's sources note, which is a
    citation check, not paragraph binding.

**`docs/MODEL.md`'s free prose stays outside the binding.** Of its four stale
members, the brief's mechanism would have caught at most two:

- PL-D1LR, if its paragraph had named the litre format function.
- PL-N3SK, had its writer cited an item rather than a planned milestone.

PL-KSLX already named its code, was listed, and still went stale. PL-LKX7 is
a measurement. Annotating every behaviour paragraph of a 12,500-line document
would not repay that, so this head keeps `PL-4FBP`'s ratified scope rather
than putting it back to the owner.

**Built 2026-11-09.** Steps 2 to 6 above are done as written. The check binds
`docs/ARCHITECTURE.md` at its title, so a chapter added later is bound too,
rather than listing its thirteen chapters. The annotation pass named code in 17
paragraphs of that document and 12 of the interface-provenance chapter. Naming
the code exposed two more stale sentences in § "User state: the saved
Workspaces", which were repaired in the same pass: a launch with no saved file
first tries `workspaces.json.previous`, and a file that is not UTF-8 text is set
aside like an invalid one rather than refused like a newer one. The repair of
§ "Layering" for PL-G1J9 also left `.claude/rules/ui-calculations.md`
paraphrasing the old sentence, so that rule now says the same as the document.

**Corrected 2026-11-10, after the blind review.** Step 1's table says PL-GPTN's
paragraph named only `PL-TH35`. It also named Blender's `SpaceType`, so the
first build, which counted any code span that was not an item id, would have
passed it. Both review passes found this. A paragraph now names code only with
a Python, JSON, TOML or YAML path, a directory outside `docs/`, or a name that
the simulator's source or tests define (`_defined_code`). A "no code yet" form
is resolved against the queue even where its paragraph also names code. The
tighter rule failed 21 more paragraphs, which name their code now. One
describes code nobody has written, and declares it against PL-PKLR. The review
also found that `app/wash_in.py` and `app/compartment_schematic.py` derive
displayed values, so § "Layering" names them, and PL-HL9P records that the
schematic's module loads the toolkit.
