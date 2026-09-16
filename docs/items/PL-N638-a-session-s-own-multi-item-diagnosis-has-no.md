---
id: PL-N638
title: A session's own multi-item diagnosis has no path that sets feature:, so the group it proposed exists only in the reply - PL-XD3C, PL-0J9K and PL-MMVF were each filed with none
priority: P2
effort: S
status: done
classes: defect, infra
feature: queue-hygiene
touches: CLAUDE.md, .claude/skills/docket/SKILL.md, .claude/rules/instruction-writing.md, docs/items/
added: 2026-09-16
closed: 2026-09-16
pr: 632
verify: grep -q 'group them as you file them' CLAUDE.md && grep -q 'A diagnosis that produces more than one item' .claude/skills/docket/SKILL.md && grep -q 'Where several lines are one problem' .claude/rules/instruction-writing.md
---

**Problem.** A session's own multi-item diagnosis has no path that sets feature:, so the group it proposed exists only in the reply - PL-XD3C, PL-0J9K and PL-MMVF were each filed with none

**Why it matters.** `feature:` is the only grouping the store has, and every
surface that answers "is this done?" reads it: `docket feature <name>` prints
`N/M done`, `docket status` lists a feature under Underway until it moves to
Finished, and `plan.recommend` prefers an underway feature *nearest finishing*
(`remaining = len(feature.open_items)`, fewest first). A group that carries no
feature gets none of that - its items are ranked independently, surface
independently in `docket next`, and the reader is left tracking three ids by
memory to know whether one problem has been dealt with. The project owner
raised exactly this on 2026-09-16: they think in "when do we fix the slow
digest", not "when do PL-XD3C, PL-0J9K and PL-MMVF land".

**Where the path is missing.** Two routes set `feature:` and neither covers a
finding:

- `.claude/skills/docket/SKILL.md` "Mode: turn an idea into work" creates items
  with `docket new --feature <name>`, but it is triggered by *the owner*
  describing something they want.
- The triage mode fills in `feature` "when it belongs with related work", which
  is after the fact and one item at a time - by then the session that knew the
  three were one problem is gone.

`CLAUDE.md`'s capture rule is the third route and deliberately takes no fields,
which is right for ideation and wrong for a diagnosis that has *just* named its
own group. `bin/docket new` already accepts `--feature` alongside several
titles (`cli.py` line 1844), so the capability exists and nothing tells a
session to reach for it.

**Evidence.** The three items above were created in one commit (`31d69a0`) from
one profiling pass, are still `status: untriaged` on
`origin/claude/confident-gauss-r3rg8i`, and carry no `feature:`. 145 of the
store's 1,089 items carry none.

**Open design question, not yet decided.** Whether `feature:` should also be
used at the finer grain this needs. It is currently a *theme* -
`dev-tooling` is 134/212 and never completes - so filing the digest items
under an existing feature would not answer "is it done?" either. See the
2026-09-16 design round.

**Done when.** A session that diagnoses one problem into two or more items
files them under one `feature:` in the same `docket new` call, and the reply
names the group rather than only the ids.

**Closed 2026-09-16.** Three edits, routed by where each fires. `CLAUDE.md`
gets one sentence only, because capture happens before a session would load
anything; the procedure, the naming rule and the two consequences are in
`.claude/skills/docket/SKILL.md`, which loads for queue work; and
`.claude/rules/instruction-writing.md` rule 14 now requires the closing block
to name the problem and its `feature:` rather than listing ids flat.

**The group turned out to be five, not three.** `bin/docket stranded` and the
creation commits (`9c9a3aa`, `fb73981`, `f753d38`, `31d69a0`, `7d533be`) put
`PL-JH3T`, `PL-XD3C`, `PL-0J9K`, `PL-MMVF` and `PL-RC86` on one problem, all
six items on `origin/claude/confident-gauss-r3rg8i` and none in any checkout.
The feature is named `session-start-cost` rather than `digest-cost` because
`PL-RC86` is the hook's network round trips and `PL-JH3T` is the whole hook's
wall clock - naming it for `digest` would have excluded two of its own members,
which is the failure mode this item is about. `PL-ZLS5` was recovered off the
same branch and deliberately left ungrouped; `PL-7XNX` is the same root cause
but its own brief calls it a nought-to-four-call ride-along, so it stays in
`parallel-sessions` rather than holding this group open.

**The backfill moved to `PL-MQH0`, and this item does not carry it.** The five
items were stranded on an idle branch when they were recovered here; the
project owner then started a session on that same branch
(`claude/confident-gauss-r3rg8i`), which now carries the implementations -
`vcs.py` +385 lines, a new `test_git_runner.py`, `docket digest --profile`.
Neither branch shares an ancestor holding those files, so `git merge-tree`
reports **add/add conflicts on all five**: git refuses the whole file rather
than merging a one-line front-matter addition against a body edit. That is the
resolution most likely to drop the `feature:` line silently, which would defeat
the change this item makes. So the files are dropped from this branch and the
one line is applied after that branch merges, cleanly, under `PL-MQH0`. The
convention - the three edits - is what this item is, and it lands here.
