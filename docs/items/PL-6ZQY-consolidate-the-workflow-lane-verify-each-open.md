---
id: PL-6ZQY
title: Consolidate the workflow lane: verify each open item still reproduces, merge duplicates, drop what no longer applies
priority: P2
effort: M
status: done
classes: docs, infra
feature: queue-hygiene
milestone: v0.4.30
touches: docs/items
added: 2026-09-12
closed: 2026-09-19
pr: 719
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

## The verification phase, run 2026-09-19

**It ran, over all 166 open workflow-lane items** — a superset of the 105
workflow items in the 2026-09-12 map, and every one checked against the tree
rather than against this note. Twelve were dropped. The 29 crossing items in the
original map were **not** swept and are still owed.

| | 2026-09-12 map (unverified) | 2026-09-19 sweep (verified) |
| --- | --- | --- |
| items read | 134 | 166 |
| defect no longer reproduces | 12 | **7** (overtaken) |
| never was an issue | not a category | **5** |
| partly overtaken | 31 | **10** |
| still fully real | 90 | **144** |
| dead or overstated | 43 of 134 (32%) | **22 of 166 (13%)** |

**The map was 4-for-6 on the candidates still open when the sweep began.** Six of
its twelve had already closed under `#499`. Of the remaining six, `PL-RZPX` and
`PL-YMY7` were confirmed dead and dropped; `PL-7RTN` and `PL-LM8P` were
**refuted and kept** — `PL-7RTN` still names no cause, which its own `Done when` asks for.
`PL-LM8P`'s census sentence is still at `.claude/rules/citing-sources.md:160`. `PL-S5YM` and `PL-C8MV` are crossing-lane
and were out of this sweep's scope. That two of four went the other way is why
the warning at the top of this item was right.

**Dropped (12).** Overtaken: `PL-0BSC`, `PL-TTMF`, `PL-7XNX`, `PL-YMY7`,
`PL-PQQ2`, `PL-SCB4`, `PL-3DXV`. Never an issue: `PL-77SV`, `PL-3GSZ`,
`PL-YNYK`, `PL-RZPX`, `PL-T86P`. Each carries its `reason` and the tree fact
that settled it.

**Partly overtaken, briefs not yet corrected (10).** `PL-6YYR`, `PL-WXX8`,
`PL-LF2C`, `PL-SY1J`, `PL-38PN`, `PL-LBW5`, `PL-SYG4`, `PL-KFWL`, `PL-3DN1`,
and this item. Each has a one-clause note of what landed and what is left in the
sweep's record; none of the briefs has been rewritten.

**The self-generation figure is not restated here.** It was computed over a set
a third of which was believed dead; that set is now 13% dead rather than 32%, so
the figure moves — but recomputing it is `PL-WXKD`'s work (no shipped command
reports filed-per-closed), not this item's, and doing it by hand would be the
same unrepeatable measurement this project keeps paying for.

## What this item still owes

Nothing. The crossing lane was swept 2026-09-19 and the ten partly-overtaken
briefs were corrected in the same pass; both are recorded below.

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

**Done when.** ~~The adversarial verification phase has run over all 134 mapped
items~~ (done 2026-09-19, over 166); ~~every drop candidate above is confirmed
against the tree or refuted~~ (done for the workflow lane 2026-09-19, and for
the crossing lane later the same day - `PL-C8MV` confirmed and dropped,
`PL-S5YM` refuted and kept); ~~the **29 crossing items** in the original map are
swept the same way~~ (done, over today's 32, which is a proven superset - see
below); and ~~the **10 partly-overtaken briefs listed above say what is actually
left**~~ (done). No merges were proposed by the map, but the crossing sweep
found one pair and recorded it on both items rather than merging them.

## The crossing lane, swept 2026-09-19

**The map's 29 crossing items are covered, and that is provable rather than
asserted.** At `355b604c`, the commit that created this item, the store held
245 open items of which **26** were crossing (the brief says 29; the difference
is `workflow_paths` drift since, `docs/maintainer.md` having been added under
`PL-GVNS`). Of those 26, **12 are still open and still crossing** and the other
**14 are all closed** - 13 `done`, `PL-7J96` `dropped`. Not one left the
crossing lane by having its `touches` edited. So today's crossing set is a
strict superset of the historical backlog, and sweeping it sweeps the map's.
Re-runnable: reconstruct the store at that commit and call
`Item.lane(config.workflow_paths)` on each open item.

Today's lane split: **32 crossing, 155 workflow, 117 product, 12 unplaced** -
11 of the 12 unplaced being untriaged captures, which is expected, leaving only
`PL-V9L3`, which `bin/docket check` already reports.

| | workflow lane (166) | crossing lane (32) |
| --- | --- | --- |
| still fully real | 144 | **24** |
| partly overtaken | 10 | **7** |
| defect no longer reproduces | 7 | **1** |
| never was an issue | 5 | **0** |
| dead or overstated | 22 of 166 (13%) | **8 of 32 (25%)** |

**The crossing lane is healthier where it counts and staler where it does
not.** One item of 32 is dead against the workflow lane's 12 of 166 - but seven
of 32 overstate what is left, against ten of 166. The reason is visible in the
verdicts: a crossing item declares a path in `src/` or `docs/MODEL.md`, and the
simulator moves under it. The Qt port alone falsified premises in `PL-XJ37`,
`PL-QS9H` and `PL-38PN` without closing any of them.

**Dropped (1).** `PL-C8MV` - overtaken seven hours after filing by the v0.3.0
close-out, which scores readout 1 both ways and names `PL-C8MV` as the
disposition it follows. Its `reason` carries the command.

**Refuted and kept (1).** `PL-S5YM`, which the 2026-09-12 map listed as a drop
candidate on the claim that both halves of it were false. Replaying
`doc_check`'s own parser and suppression loop over the live tree: the covered
set is non-empty, one direction is tested and the other is not, and the prose
at `docs/ARCHITECTURE.md:523` is untouched. **That makes the map 5-for-8 across
both lanes** - `PL-RZPX` and `PL-YMY7` confirmed dead, `PL-7RTN`, `PL-LM8P` and
`PL-S5YM` refuted and kept, `PL-C8MV` confirmed - which is why the warning at
the top of this item was right and why no drop here was taken on the map's
word.

**The most expensive single find was not a dead item.** `PL-KFWL` recorded the
v0.4.8 resolution backwards - "`v0.4.8` was deleted from the remote, not cut" -
and told a later session to run `git tag -d v0.4.8` to repair a clone. The tag
is live on the remote at `b340e7f`, `docs/releases/v0.4.8.md` exists, and
`ROADMAP.md:71` marks it Completed, so following that paragraph would have
removed a tag `check_tags` expects and turned a correct tree into a reported
error. `python3 tools/doc_check.py check` exits clean over that file, because
every path and identifier it cites exists; what had gone false was the tense
and the outcome, which no check reads.

**One merge candidate, recorded rather than merged.** `PL-KFWL` and `PL-6YYR`
describe the same missing guard - a release tag that has no cut behind it -
from the instance and from the rule. Both are open, neither has any of its work
done, and each carries a note naming the other. Merging them is a judgment for
whoever starts either, and it is cheaper made with the code open than in a
sweep.

**Four items were wrong on the day they were filed**, which is the pattern
`PL-JB3Z` closed for the future by making triage reproduce the fault: `PL-3DN1`
(its illustration was already caught by `already_released`, landed nine days
earlier), `PL-6YYR` ("nothing in `make check` reads tags", false since
2026-08-31), `PL-316G` (the simulator scope it recommends held 4 occurrences at
filing and 5 today, with `docs/MODEL.md`, `docs/ARCHITECTURE.md` and
`README.md` at zero), and `PL-SY1J` (both disjuncts of its second `Done when`
clause were satisfied twelve days before the observation). None of the four is
dead; each has a real remainder, and each now says which half was never true.

**The ten partly-overtaken briefs are corrected**, and two of the ten were
misclassified: `PL-KFWL` and `PL-3DN1` are **still real** rather than partly
overtaken - nothing either asks for has landed - while what was stale in them
was the account of how a neighbouring thing resolved. `PL-6YYR` went the same
way. The rest hold: `PL-WXX8`, `PL-LF2C`, `PL-SY1J`, `PL-38PN`, `PL-LBW5`,
`PL-SYG4` and this item.

## What the sweep cost, and the one thing worth changing

Eleven read-only agents over 41 items, about 1.09 million subagent tokens, with
every drop and every number re-checked in the main session before it was
written. The verdicts are in the items rather than in this reply, which is the
correction: the 2026-09-19 workflow sweep left its "what landed, what is left"
notes for ten items in its reply alone, that session was archived, and this
session had to re-derive all ten from the tree. A sweep verdict that is not
written into the item it judges has not been recorded.
