---
id: PL-6ZQY
title: Consolidate the workflow lane: verify each open item still reproduces, merge duplicates, drop what no longer applies
priority: P2
effort: M
status: ready
classes: docs, infra
feature: queue-hygiene
touches: docs/items
added: 2026-09-12
not-delegable: The work is a per-item judgment against the tree for 134 items - does this defect still reproduce, does this brief still describe the code. No command can prove that pass was made, and each drop or merge it produces is proven by the item it closes. What can be checked afterwards is make docket and that every dropped item carries a reason.
---

**Problem.** Consolidate the workflow lane: verify each open item still reproduces, merge duplicates, drop what no longer applies

**Observed 2026-09-12.** A 17-agent fan-out read all 134 open workflow-lane and
crossing items in full and checked each against the tree. The map phase completed;
the adversarial verification phase did not - the session hit its usage limit, so 53
of 72 agents failed. **Nothing below has been verified. No item may be dropped or
merged on the strength of this note alone.**

## What the map found

| | |
| --- | --- |
| items mapped | 134 (105 workflow, 29 crossing) |
| defect no longer reproduces | 12 |
| partly overtaken by later work | 31 |
| still fully real | 90 |
| needs an owner decision before anyone can start | 27 |
| mechanical (brief already determines the diff) | 33 |
| estimated total effort | 121 h, about 20 working days |

## The root cause under 47% of it

Six of the fifteen clusters share one mistake: **the apparatus infers a fact it
could have recorded.** 63 items, 56 of them workflow-lane, about 50 h:

- **What a branch's commits prove** (15) - Nothing is recorded when a session claims work, so `stranded`, `flight` and the digest reconstruct the claim afterwards by comparing file content against the base — and content is unchanged by a squash, by a history rewrite, and by two sessions running `docket record`, which is exactly when the answer is wrong.
- **The item store is hand-edited YAML** (10) - `docket` has exactly one write command (`new`); everything else prints questions and rules and then accepts nothing, so the store is maintained by a model editing YAML and validated by a checker that runs one step later.
- **The roadmap is prose the tooling parses** (8) - Scope membership is inferred by scraping item ids out of prose under a fixed heading vocabulary, with no representation of exclusion, so the roadmap's own decisions about what is *not* in a milestone cannot reach the ranking.
- **What a verify: command proves** (10) - `verify:` was specified as "a command that fails before the work and passes after" and nothing else about it was written down, so each consumer — the landed check, the replay, the delegated audit, the close-out — reads a different meaning out of the same exit code, and a non-zero exit means both "not started" and "prerequisite broken".
- **Prose that asserts facts about the tree** (10) - The project's authoritative documents were written as prose for a human reader and only later became the specification the code is judged against, so the link from a sentence to the identifier, test, constant or count it names exists only in the reader's head.
- **The checkout is a cache nobody validates** (10) - The ephemeral clone is treated as a faithful copy of the remote — it is not, because `git fetch` moves neither an existing tag nor a diverged branch ref — and separately nobody wrote down which ref operations a session is actually permitted, so procedures end in steps that report success and do nothing.

Each inference fails in a new way, each failure is found one at a time, and each
becomes its own item. That is the mechanism behind the lane's measured
self-generation rate of 0.69 new workflow items per workflow item worked (traced
2026-09-12 from the commit that created each item file back to the id its subject
leads with). Patching an inference closes one item and leaves the generator intact;
replacing one with a recorded fact closes a cluster.

## Candidates, all unverified

Defect no longer reproduces - drop candidates:

- `PL-RZPX` - Asks docket check to report open items that declare no touches — which it has done since the day docket landed, one day before this item was filed.
- `PL-V4LS` - Asks whether a checker may write the merged pull request number it recovered, or what command should — a command that now exists and is wired into make fix.
- `PL-2QMK` - Claims no session in this container can screenshot the running app because Flet fetches Flutter assets from a blocked host; the assets ship locally and one flag makes Flet use them.
- `PL-7RTN` - Claims pull request #395 opened with zero check runs, so a branch could merge with nothing having gated it.
- `PL-LM8P` - A rule file justifies itself with a census of source notes in the data files, and the item says the census no longer matches the tree.
- `PL-S5YM` - The covered-directory branch in doc_check is said to be untested and unused; both halves are now false.
- `PL-CPLD` - Recover a WORKING_NOTES commit stranded on a merged branch and delete that branch's remote ref.
- `PL-YMY7` - A record that simulation_view.py's uncovered lines are Flet-construction paths rather than guards, so nobody files them as routine coverage backfill.
- `PL-21GS` - The v0.3.0 loop-trial close-out should say that readout 4's early zeros were taken in a shallow clone, where `stranded` could only read the refs the checkout held.
- `PL-C8MV` - The product-vs-apparatus churn readout files tests of apparatus under tests/ on the product side, biasing the one readout meant to catch apparatus becoming the work.
- `PL-K2YF` - ROADMAP.md's release narrative skipped v0.2.6, and the convention that each release adds a paragraph is enforced by habit rather than a check.
- `PL-01CK` - The in-flight landedness test used to walk the whole default-branch history once per blob a candidate branch adds; that per-blob walk no longer exists.

Partly overtaken, so the brief overstates what is left (31): `PL-0M32`, `PL-4C41`, `PL-CW14`, `PL-KBD0`, `PL-LWMS`, `PL-TFWR`, `PL-WGXJ`, `PL-XQRK`, `PL-YKXQ`, `PL-J7C5`, `PL-JQVB`, `PL-KFWL`, `PL-2GQW`, `PL-38PN`, `PL-C92D`, `PL-SVRW`, `PL-XH1D`, `PL-ZG5J`, `PL-LPWK`, `PL-NBCS`, `PL-40PL`, `PL-GLBF`, `PL-PGZK`, `PL-HKTB`, `PL-MHQK`, `PL-QS9H`, `PL-6BDX`, `PL-B73C`, `PL-F48B`, `PL-XLQ5`, `PL-W6NY`.

## What this item still owes

Re-run the verification phase before acting: each drop must be refuted or confirmed
against the tree, and each merge must be checked for a brief that genuinely covers
what it absorbs. The workflow script is saved and resumable; the map phase replays
from cache, so only the verification agents re-run.

**Why it matters.** 43 of 134 items - 32% - are dead or overstated, and nothing
in the project noticed or can. `PL-LKGL` carries the measurement of why: a
`verify:` command tests for the presence of the fix, never for the presence of
the fault, so an item whose problem was solved another way fails forever and
reads as outstanding work. Six of the twelve dead items carry a `verify:` and
all six still fail. A churn advisory was tested against the sweep's verdicts and
does not separate the classes, so there is no cheap mechanical substitute for
this pass.

The cost of leaving it is paid by every session that opens the queue. A third of
the workflow lane is work nobody should do, and it is not marked, so it is
ranked, offered by `bin/docket next`, counted into the debt gate, and read past
by each session in turn. It also corrupts the one measurement the project uses
to judge the lane: the 0.69 self-generation rate is computed over items a third
of which are not real.

**Done when.** The adversarial verification phase has run over all 134 mapped
items; every drop candidate above is confirmed against the tree or refuted, and
the confirmed ones are `status: dropped` with a `reason`; each proposed merge is
checked for a brief that genuinely covers what it absorbs before either item
closes; the 31 partly-overtaken briefs say what is actually left; and the map's
counts are restated against what the pass found, so the self-generation figure is
computed over the surviving set.
